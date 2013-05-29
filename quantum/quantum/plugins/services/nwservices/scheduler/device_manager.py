# Copyright 2013 Freescale Semiconductor, Inc.
# All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sqlalchemy as sa
from sqlalchemy import types
from sqlalchemy.orm import exc as orm_exc
from sqlalchemy.types import TypeDecorator

from quantum.common import exceptions as q_exc
from quantum.db import api as db
from quantum.db import model_base
from quantum.db import models_v2
from quantum.openstack.common import log as logging
from quantum.openstack.common import jsonutils
from quantum.openstack.common import uuidutils
from quantum.plugins.common import constants
from quantum.openstack.common import cfg

LOG = logging.getLogger(__name__)

# No of resources per balancer device
# hardcoded for now
RESOURCE_LIMIT = 10


class BalancerDeviceNotFound(q_exc.QuantumException):
    message = _("Loadbalancer Device was not found")


class AssociationNotFound(q_exc.QuantumException):
    message = _("Association was not found")


class AssociationError(q_exc.QuantumException):
    message = _("Error adding association")


class NoValidDevice(q_exc.NotFound):
    message = _("No valid device found")


class ResourceAssociation(model_base.BASEV2):
    """ Represents association between foreign resource and device
        Resource is unknown to device manager - hence no FK constraint
        on resource_id
    """
    resource_id = sa.Column(sa.String(36), nullable=False,
                            primary_key=True)
    device_id = sa.Column(sa.String(36),
                          sa.ForeignKey('balancerdevices.id',
                                        ondelete='CASCADE'),
                          nullable=False)


class JsonType(TypeDecorator):
    impl = types.String

    def process_bind_param(self, value, engine):
        if value is not None:
            return jsonutils.dumps(value)
        return jsonutils.dumps({})

    def process_result_value(self, value, engine):
        if value is not None:
            return jsonutils.loads(value)
        return {}


class BalancerDevice(model_base.BASEV2, models_v2.HasId,
                     models_v2.HasTenant):
    """ Represents loadbalancing device
    """
    name = sa.Column(sa.String(36), nullable=False)
    type = sa.Column(sa.String(36), nullable=False)
    version = sa.Column(sa.String(36), nullable=False)
    management = sa.Column(JsonType(255), nullable=False)
    ref_counter = sa.Column(sa.Integer, default=0)
    subnet_id = sa.Column(sa.String(36), default="")
    status = sa.Column(sa.String(36), nullable=False,
                       default=constants.PENDING_CREATE)


class SchedulingAlgorithm():
    """ Algorithm which chooses appropriate device for the tenant/network
        which has less associated resources with it
    """
    def __call__(self, resource, devices, device_type=None):
        # assuming resource and devices has tenant_id in it
        if len(devices) == 0:
            raise NoValidDevice()

        # find running device of needed type
        filtered = [device for device in devices
                    if device["status"] == constants.ACTIVE and
                    (device_type is None or device_type == device["type"])]
        # filter by tenant_id and subnet_id
        # if they're present in resource
        # also find only those devices which doesn't exceed
        # the limit of already associatied resources
        filtered = [device for device in filtered if
                    ((device["tenant_id"] == resource["tenant_id"] and
                      (device["subnet_id"] ==
                       resource.get('subnet_id', device['subnet_id'])))) and
                    device["ref_counter"] < RESOURCE_LIMIT]
        if not filtered:
            raise NoValidDevice()
        # select device with minimum associated resources
        device = min(filtered, key=lambda x: x["ref_counter"])
        LOG.debug(_("Found device %(dev)s for resource %(res)s"),
                  {"dev": device, "res": resource})
        return device


class BalancerDeviceManager(object):
    """ Simplistic device manager provided for PoC purpose.
        Supports only private virtual devices provisioned on demand
    """
    def __init__(self):
        self._initialize_db()

    def _apply_add_policy(self, context, device, resource):
        # perform common steps
        device.ref_counter = device.ref_counter + 1
        device.tenant_id = resource["tenant_id"]
        device.subnet_id = resource["subnet_id"]

    def _apply_del_policy(self, context, device):
        # perform common steps
        device.ref_counter = device.ref_counter - 1
        if device.ref_counter == 0:
            device.status = constants.PENDING_DELETE

    def _initialize_db(self):
        options={'sql_connection: %s' % cfg.CONF.DATABASE.sql_connection}
        options.update({"sql_max_retries": cfg.CONF.DATABASE.sql_max_retries})
        options.update({"reconnect_interval": cfg.CONF.DATABASE.reconnect_interval})
        options.update({"base": models_v2.model_base.BASEV2})
        db.configure_db(options)
#        db.configure_db()

    def create_device(self, context, dev_info):
        # caller must provide full device description
        LOG.debug(_("Creating device: %s"), dev_info)
        # as this method may be used to provision unexisting devices
        with context.session.begin(subtransactions=True):
            dev = BalancerDevice(id=uuidutils.generate_uuid(),
                                 name=dev_info["name"],
                                 type=dev_info["type"],
                                 version=dev_info["version"],
                                 management=dev_info["management"],
                                 tenant_id=dev_info["tenant_id"],
                                 subnet_id=dev_info["subnet_id"],
                                 status=dev_info["status"])
            context.session.add(dev)
            return dev

    def update_device(self, context, device):
        if device["status"] == constants.ERROR:
            LOG.debug(_("Deleting device in ERROR state: %s"), device)
            self.delete_device(context, device)
            return

        LOG.debug(_("Updating device: %s"), device)

        with context.session.begin(subtransactions=True):
            dev = (context.session.query(BalancerDevice).
                   filter_by(id=device["id"]).one())
            dev.update({"management": device["management"],
                        "status": device["status"]})

    def delete_device(self, context, device):
        LOG.debug(_("Deleting device: %s"), device)
        with context.session.begin(subtransactions=True):
            dev = (context.session.query(BalancerDevice).
                   filter_by(id=device["id"]))
            dev.delete()

    def get_device_list(self, context):
        # Not checking for device ownership
        with context.session.begin(subtransactions=True):
            return context.session.query(BalancerDevice).all()

    def _get_resource_association(self, context, resource):
        with context.session.begin(subtransactions=True):
            try:
                return (context.session.query(ResourceAssociation).
                        filter_by(resource_id=resource["id"]).one())
            except orm_exc.NoResultFound:
                raise AssociationNotFound()

    def get_device_by_resource(self, context, resource):
        with context.session.begin(subtransactions=True):
            assoc = self._get_resource_association(context, resource)
            device = (context.session.query(BalancerDevice).
                      filter_by(id=assoc["device_id"]).one())
            return device

    def add_association(self, context, device, resource):
        if (device["tenant_id"] != resource["tenant_id"] or
            device["subnet_id"] != resource["subnet_id"]):
            raise NoValidDevice()

        """ Adds association and returns it """
        LOG.debug(_("Adding resource %(res)s to device %(id)s"),
                  {"res": resource, "id": device["id"]})
        association = ResourceAssociation(resource_id=resource["id"],
                                          device_id=device["id"])
        try:
            with context.session.begin(subtransactions=True):
                dev = (context.session.query(BalancerDevice).
                       filter_by(id=device["id"]).one())
                context.session.add(association)
                self._apply_add_policy(context, dev, resource)
                return association
        except:
            # due to sqlalchemy bug(?) specific exception
            # can't be catched here
            raise AssociationError()

    def delete_association(self, context, resource):
        """ Deletes association
            This may leave device in 'PENDING DELETE' if it was the last
            association with this device
            TO BE CALLED BEFORE update_device/delete_device
        """
        with context.session.begin(subtransactions=True):
            try:
                assoc = (context.session.query(ResourceAssociation).
                         filter_by(resource_id=resource["id"]))
                dev = (context.session.query(BalancerDevice).
                       filter_by(id=assoc.one().device_id).one())
                self._apply_del_policy(context, dev)
                assoc.delete()
                return dev
            except orm_exc.NoResultFound:
                raise AssociationNotFound()
