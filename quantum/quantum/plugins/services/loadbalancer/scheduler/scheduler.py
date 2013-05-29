# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Mirantis, Inc.
# All Rights Reserved.
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
#
# @author: Eugene Nikanorov
#

from quantum.openstack.common import log as logging
from quantum.openstack.common import uuidutils
from quantum.plugins.common import constants
from quantum.plugins.services.loadbalancer.\
    scheduler.device_manager import BalancerDeviceManager
from quantum.plugins.services.loadbalancer.\
    scheduler.device_manager import NoValidDevice
from quantum.plugins.services.loadbalancer.\
    scheduler.device_manager import SchedulingAlgorithm


LOG = logging.getLogger(__name__)

# device types
HAPROXY = "HAPROXY"

HAPROXY_VERSION = "v1.0"


class BalancerScheduler(object):

    def __init__(self):
        self.dev_manager = BalancerDeviceManager()
        self.algorithm = SchedulingAlgorithm()

    def _get_default_device(self, resource):
        # no management since it's unknown at the moment
        device = {
            "name": uuidutils.generate_uuid(),
            "type": HAPROXY,
            "version": HAPROXY_VERSION,
            "management": "",
            "tenant_id": resource["tenant_id"],
            "subnet_id": resource["subnet_id"],
            "status": constants.PENDING_CREATE,
        }
        return device

    def _create_default(self, context, resource):
        dev_info = self._get_default_device(resource)
        return self.dev_manager.create_device(context, dev_info)

    def add_resource_association(self, context, resource):
        LOG.debug(_("Going to schedule resource %s"), resource)
        devices = self.dev_manager.get_device_list(context)
        try:
            device = self.algorithm(resource, devices)
        except NoValidDevice, e:
            LOG.info(_("No valid device was found, "
                       "creating haproxy vm device"))
            # create device object in DB
            device = self._create_default(context, resource)

        self.dev_manager.add_association(context, device, resource)
        return device

    def delete_resource_association(self, context, resource):
        return self.dev_manager.delete_association(context, resource)

    def get_device_by_resource(self, context, resource):
        return self.dev_manager.get_device_by_resource(context, resource)

    def update_device(self, context, device):
        return self.dev_manager.update_device(context, device)

    def delete_device(self, context, device):
        self.dev_manager.delete_device(context, device)
