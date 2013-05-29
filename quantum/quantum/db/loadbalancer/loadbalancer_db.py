# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
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
from sqlalchemy import orm
from sqlalchemy.orm import exc

from quantum.api.v2 import attributes
from quantum.common import exceptions as q_exc
from quantum.db import api as qdbapi
from quantum.db import model_base
from quantum.db import models_v2
from quantum.db.nwservices import nwservices_db
from quantum.extensions import loadbalancer
from quantum.openstack.common import log as logging
from quantum.openstack.common import uuidutils
from quantum.plugins.common import constants
from quantum.common import utils
from quantum.openstack.common import timeutils
from quantum.db import db_base_plugin_v2
from quantum.db.nwservices import nwservices_db

LOG = logging.getLogger(__name__)

############    
#SLB Tables added by Srikanth
############
class HasTenant(object):
    """Tenant mixin, add to subclasses that have a tenant."""
    # NOTE(jkoelker) tenant_id is just a free form string ;(
    tenant_id = sa.Column(sa.String(255))


class HasId(object):
    """id mixin, add to subclasses that have an id."""
    id = sa.Column(sa.String(36), primary_key=True, default=utils.str_uuid)

class LB_Pool_Member(model_base.BASEV2, HasId, HasTenant):
    pool_id = sa.Column(sa.String(36), sa.ForeignKey('lb_pools.id'),
                           nullable=False)
    name = sa.Column(sa.String(255))
    ip_address = sa.Column(sa.String(15))
    port_no = sa.Column(sa.Integer)
    weight = sa.Column(sa.Integer)
    admin_status = sa.Column(sa.Boolean)
    status = sa.Column(sa.String(50))
    
class LB_Health_Monitor(model_base.BASEV2, HasId, HasTenant):
    pool_id = sa.Column(sa.String(36), sa.ForeignKey('lb_pools.id'),
                           nullable=False)
    name = sa.Column(sa.String(255))
    type = sa.Column(sa.String(50))
    delay = sa.Column(sa.Integer)
    timeout = sa.Column(sa.Integer)
    max_retries = sa.Column(sa.Integer)
    http_method = sa.Column(sa.String(50))
    url_path = sa.Column(sa.String(255))
    expected_codes = sa.Column(sa.String(255))
    admin_status = sa.Column(sa.Boolean)
    status = sa.Column(sa.String(50))
    
class LB_Pool(model_base.BASEV2, HasId, HasTenant):
    name = sa.Column(sa.String(255))
    description = sa.Column(sa.String(255))
    subnet_id = sa.Column(sa.String(36), sa.ForeignKey('subnets.id'),
                           nullable=False)
    protocol = sa.Column(sa.String(50))
    lb_method = sa.Column(sa.String(50))
    admin_status = sa.Column(sa.Boolean)
    status = sa.Column(sa.String(50))
    subnet = orm.relationship(models_v2.Subnet, backref="lb_pools",
                                        lazy="dynamic")
    
class LB_Session_Persistance(model_base.BASEV2, HasId):
    type = sa.Column(sa.String(255))
    cookie_name = sa.Column(sa.String(1024))
    
class LB_Virtual_IP(model_base.BASEV2, HasId, HasTenant):
    pool_id = sa.Column(sa.String(36), sa.ForeignKey('lb_pools.id'),
                           nullable=False)
    session_persistance_id = sa.Column(sa.String(36), sa.ForeignKey('lb_session_persistances.id'),
                           nullable=False)
    name = sa.Column(sa.String(255))
    description = sa.Column(sa.String(255))
    #port_id = sa.Column(sa.String(36), sa.ForeignKey('ports.id'),
    #                       nullable=False)
    port_no = sa.Column(sa.Integer)
    protocol = sa.Column(sa.String(50))
    connection_limit = sa.Column(sa.Integer)
    config_handle_id = sa.Column(sa.String(36), sa.ForeignKey('ns_config_handles.id'),
                           nullable=False)
    admin_status = sa.Column(sa.Boolean)
    status = sa.Column(sa.String(50))
    session_persistance = orm.relationship(LB_Session_Persistance, backref="lb_virtual_ips",
                                        lazy="dynamic")
    
class LB_Version(model_base.BASEV2):
    id = sa.Column(sa.Integer(), primary_key=True, autoincrement=True)
    runtime_version = sa.Column(sa.String(50),
                                nullable=False)
    
class LB_Delta(model_base.BASEV2, HasId):
    main_table_name = sa.Column(sa.String(50),
                                nullable=False)
    link_id = sa.Column(sa.Integer)
    old_value = sa.Column(sa.String(50))
    new_value = sa.Column(sa.String(50))
    operation = sa.Column(sa.String(50))
    version_id = sa.Column(sa.Integer(), sa.ForeignKey('lb_versions.id'),
                           nullable=False)
    updated_at = sa.Column(sa.DateTime(), default=timeutils.utcnow)
    user_id = sa.Column(sa.String(50), nullable=False)
    

class LoadbalancerPluginDb(db_base_plugin_v2.QuantumDbPluginV2):
    """
    A class that wraps the implementation of the Quantum
    loadbalancer plugin database access interface using SQLAlchemy models.

    As opposed to all other DB plugins LoadBalancerPluginDb does not
    implement plugin interface. LoadBalancerPlugin follows "has-a" instead of
    "is-a" relation with db-plugin. The main reason is that Db plugin is
    called not only by plugin, but also by notify handler and direct calls
    are a logical way.
    """

    def __init__(self):
        qdbapi.register_models(base=model_base.BASEV2)

    # TODO(lcui):
    # A set of internal facility methods are borrowed from QuantumDbPluginV2
    # class and hence this is duplicate. We need to pull out those methods
    # into a seperate class which can be used by both QuantumDbPluginV2 and
    # this class (and others).
    def _get_tenant_id_for_create(self, context, resource):
        if context.is_admin and 'tenant_id' in resource:
            tenant_id = resource['tenant_id']
        elif ('tenant_id' in resource and
              resource['tenant_id'] != context.tenant_id):
            reason = _('Cannot create resource for another tenant')
            raise q_exc.AdminRequired(reason=reason)
        else:
            tenant_id = context.tenant_id
        return tenant_id

    def _fields(self, resource, fields):
        if fields:
            return dict((key, item) for key, item in resource.iteritems()
                        if key in fields)
        return resource

    def _apply_filters_to_query(self, query, model, filters):
        if filters:
            for key, value in filters.iteritems():
                column = getattr(model, key, None)
                if column:
                    query = query.filter(column.in_(value))
        return query

    def _get_collection_query(self, context, model, filters=None):
        collection = self._model_query(context, model)
        collection = self._apply_filters_to_query(collection, model, filters)
        return collection

    def _get_collection(self, context, model, dict_func, filters=None,
                        fields=None):
        query = self._get_collection_query(context, model, filters)
        return [dict_func(c, fields) for c in query.all()]

    def _get_collection_count(self, context, model, filters=None):
        return self._get_collection_query(context, model, filters).count()

    def _model_query(self, context, model):
        query = context.session.query(model)
        query_filter = None
        if not context.is_admin and hasattr(model, 'tenant_id'):
            if hasattr(model, 'shared'):
                query_filter = ((model.tenant_id == context.tenant_id) |
                                (model.shared))
            else:
                query_filter = (model.tenant_id == context.tenant_id)

        if query_filter is not None:
            query = query.filter(query_filter)
        return query

    def _query_resource(self, context, model, obj_id):
        query = self._model_query(context, model)
        return query.filter(model.id == obj_id).one()
    ########################################################
    # SRIKANTH MODIFICATIONS
    def _get_configuration(self, context, id):
        try:
            config_handle = self._get_by_id(context, nwservices_db.ns_config_handle, id)
        except exc.NoResultFound:
            # NOTE(jkoelker) The PortNotFound exceptions requires net_id
            #                kwarg in order to set the message correctly
            raise q_exc.Config_handleNotFound(config_handle_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Config_handles match for %s' % id)
            raise q_exc.Config_handleNotFound(config_handle_id=id)
        return config_handle
    
    def _make_configuration_dict(self, configuration, fields=None):
        res = {'id': configuration['id'],
               'name': configuration['name'],
               'tenant_id': configuration['tenant_id'],
               'status': configuration['status']}

        return self._fields(res, fields)

    def get_configuration(self, context, id, fields=None):
        configuration = self._get_configuration(context, id)
        return self._make_configuration_dict(configuration, fields)

    def get_configurations(self, context, filters=None, fields=None):
        return self._get_collection(context, LB_Logical_app,
                                    self._make_configuration_dict,
                                    filters=filters, fields=fields)
        
    def create_configuration(self, context, configuration):
        """ handle creation of a single configuration """
        # single request processing
        s = configuration['configuration']
        # NOTE(jkoelker) Get the tenant_id outside of the session to avoid
        #                unneeded db action if the operation raises
        tenant_id = self._get_tenant_id_for_create(context, s)
        with context.session.begin(subtransactions=True):
            configuration = LB_Logical_app(tenant_id=tenant_id,
                                        id=s.get('id') or utils.str_uuid(),
                                        name=s['name'],
                                        status='In-Active',
                                        category_id=s['category_id'])
            context.session.add(configuration)
        return self._make_configuration_dict(configuration)
        
    def delete_configuration(self, context, id):
        with context.session.begin(subtransactions=True):
            configuration = self._get_configuration(context, id)
            context.session.delete(configuration)
            
    def update_configuration(self, context, id, configuration):
        """Update the configuration with new info."""

        s = configuration['configuration']
	with context.session.begin(subtransactions=True):
	    configuration = self._get_configuration(context, id)
	    configuration.update(s)
        return self._make_configuration_dict(configuration)
        
    ###Pools
    def _get_pool(self, context, id):
        try:
            pool = self._get_by_id(context, LB_Pool, id)
        except exc.NoResultFound:
            raise q_exc.PoolNotFound(pool_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple pools match for %s' % id)
            raise q_exc.PoolNotFound(pool_id=id)
        return pool
    
    def _make_pool_dict(self, pool, fields=None):
        for pl in pool['subnet']:
            subnet_name = str(pl['cidr'])
            
        res = {'id': pool['id'],
               'name': pool['name'],
               'description': pool['description'],
               'subnet_id': pool['subnet_id'],
               'tenant_id': pool['tenant_id'],
               'status': pool['status'],
               'admin_status': pool['admin_status'],
               'protocol': pool['protocol'],
               'lb_method': pool['lb_method'],
               'subnet': subnet_name}

        return self._fields(res, fields)

    def get_pool(self, context, id, fields=None):
        pool = self._get_pool(context, id)
        return self._make_pool_dict(pool, fields)

    def get_pools(self, context, filters=None, fields=None):
        return self._get_collection(context, LB_Pool,
                                    self._make_pool_dict,
                                    filters=filters, fields=fields)
        
    def create_pool(self, context, pool):
        """ handle creation of a single pool """
        # single request processing
        s = pool['pool']
        # NOTE(jkoelker) Get the tenant_id outside of the session to avoid
        #                unneeded db action if the operation raises
        tenant_id = self._get_tenant_id_for_create(context, s)
        with context.session.begin(subtransactions=True):
            pool = LB_Pool(tenant_id=tenant_id,
                                        id=s.get('id') or utils.str_uuid(),
                                        name=s['name'],
                                        description=s['description'],
                                        protocol=s['protocol'],
                                        lb_method=s['lb_method'],
                                        status=1,
                                        admin_status=1,
                                        subnet_id=s['subnet_id'])
            context.session.add(pool)
        return self._make_pool_dict(pool)
        
    def delete_pool(self, context, id):
        with context.session.begin(subtransactions=True):
            pool = self._get_pool(context, id)
            context.session.delete(pool)
            
    def update_pool(self, context, id, pool):
        """Update the pool with new info."""

        s = pool['pool']
	with context.session.begin(subtransactions=True):
	    pool = self._get_pool(context, id)
	    pool.update(s)
        return self._make_pool_dict(pool)
    
    ###Pool Members
    def _get_member(self, context, id):
        try:
            member = self._get_by_id(context, LB_Pool_Member, id)
        except exc.NoResultFound:
            raise q_exc.PoolMemberNotFound(member_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple members match for %s' % id)
            raise q_exc.PoolMemberNotFound(member_id=id)
        return member
    
    def _make_member_dict(self, member, fields=None):
        res = {'id': member['id'],
               'name': member['name'],
               'pool_id': member['pool_id'],
               'ip_address': member['ip_address'],
               'port_no': member['port_no'],
               'weight': member['weight'],
               'tenant_id': member['tenant_id'],
               'status': member['status'],
               'admin_status': member['admin_status']}

        return self._fields(res, fields)

    def get_member(self, context, id, fields=None):
        member = self._get_member(context, id)
        return self._make_member_dict(member, fields)

    def get_members(self, context, filters=None, fields=None):
        return self._get_collection(context, LB_Pool_Member,
                                    self._make_member_dict,
                                    filters=filters, fields=fields)
        
    def create_member(self, context, member):
        """ handle creation of a single member """
        # single request processing
        s = member['member']
        # NOTE(jkoelker) Get the tenant_id outside of the session to avoid
        #                unneeded db action if the operation raises
        tenant_id = self._get_tenant_id_for_create(context, s)
        with context.session.begin(subtransactions=True):
            member = LB_Pool_Member(tenant_id=tenant_id,
                                        id=s.get('id') or utils.str_uuid(),
                                        name=s['name'],
                                        ip_address=s['ip_address'],
                                        pool_id=s['pool_id'],
                                        port_no=s['port_no'],
                                        weight=s['weight'],
                                        status=1,
                                        admin_status=1)
            context.session.add(member)
        return self._make_member_dict(member)
        
    def delete_member(self, context, id):
        with context.session.begin(subtransactions=True):
            member = self._get_member(context, id)
            context.session.delete(member)
            
    def update_member(self, context, id, member):
        """Update the member with new info."""

        s = member['member']
	with context.session.begin(subtransactions=True):
	    member = self._get_member(context, id)
	    member.update(s)
        return self._make_member_dict(member)
        
    ###Health Monitors
    def _get_monitor(self, context, id):
        try:
            monitor = self._get_by_id(context, LB_Health_Monitor, id)
        except exc.NoResultFound:
            raise q_exc.HealthMonitorNotFound(monitor_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple monitors match for %s' % id)
            raise q_exc.HealthMonitorNotFound(monitor_id=id)
        return monitor
    
    def _make_monitor_dict(self, monitor, fields=None):
        res = {'id': monitor['id'],
               'name': monitor['name'],
               'pool_id': monitor['pool_id'],
               'type': monitor['type'],
               'delay': monitor['delay'],
               'timeout': monitor['timeout'],
               'max_retries': monitor['max_retries'],
               'http_method': monitor['http_method'],
               'url_path': monitor['url_path'],
               'expected_codes': monitor['expected_codes'],
               'tenant_id': monitor['tenant_id'],
               'status': monitor['status'],
               'admin_status': monitor['admin_status']}

        return self._fields(res, fields)

    def check_vip_update(self,context,pool_id,tenant_id,fields=None):
        """
        (trinath) Check for the logical_device_uuid for
        the given pool id and tenant id. (generic def)
        """
        """
        vip_qry = context.session.query(LB_Virtual_IP)
        try:
            vips_record = vip_qry.filter_by(pool_id=pool_id,
                                            tenant_id=tenant_id).all()
        except exc.NoResultFound:
            LOG.debug(_('Virtual_IP record not found.'))
            return False
        LOG.debug(_("Trinath ::(check_vip_update) Virtual_IP record found. Record: %s" % str(vips_record)))
        return vips_record
        """
        return self._get_collection(context, LB_Virtual_IP,
                                    self._make_vip_dict,
                                    filters={"pool_id":[pool_id],"tenant_id":[tenant_id]}, fields=fields)

    def check_session_vips_update(self,context,id,filters=None,fields=None):
        """
        (trinath) Check for the session Per.Id in the Virtual IPs tbl.
        """
        """
        vip_qry = context.session.query(LB_Virtual_IP)
        try:
            vips_record = vip_qry.filter_by(session_persistance_id=id).all()

        except exc.NoResultFound:
            LOG.debug(_("Virtual_IP record for Session Persistance not found."))
            return False
        LOG.debug(_("Trinath::(check_session_vips_update)Virtual_IP record found. Record: %s" % str(vips_record)))
        return vips_record
        """
        return self._get_collection(context, LB_Virtual_IP,
                                    self._make_vip_dict,
                                    filters={"session_persistance_id":[id]}, fields=fields)

    def get_monitor(self, context, id, fields=None):
        monitor = self._get_monitor(context, id)
        return self._make_monitor_dict(monitor, fields)

    def get_monitors(self, context, filters=None, fields=None):
        return self._get_collection(context, LB_Health_Monitor,
                                    self._make_monitor_dict,
                                    filters=filters, fields=fields)
        
    def create_monitor(self, context, monitor):
        """ handle creation of a single monitor """
        # single request processing
        s = monitor['monitor']
        # NOTE(jkoelker) Get the tenant_id outside of the session to avoid
        #                unneeded db action if the operation raises
        tenant_id = self._get_tenant_id_for_create(context, s)
        with context.session.begin(subtransactions=True):
            monitor = LB_Health_Monitor(tenant_id=tenant_id,
                                        id=s.get('id') or utils.str_uuid(),
                                        name=s['name'],
                                        pool_id=s['pool_id'],
                                        type=s['type'],
                                        delay=s['delay'],
                                        timeout=s['timeout'],
                                        max_retries=s['max_retries'],
                                        http_method=s['http_method'],
                                        url_path=s['url_path'],
                                        expected_codes=s['expected_codes'],
                                        status=1,
                                        admin_status=1)
            context.session.add(monitor)
        return self._make_monitor_dict(monitor)
        
    def delete_monitor(self, context, id):
        with context.session.begin(subtransactions=True):
            monitor = self._get_monitor(context, id)
            context.session.delete(monitor)
            
    def update_monitor(self, context, id, monitor):
        """Update the monitor with new info."""

        s = monitor['monitor']
	with context.session.begin(subtransactions=True):
	    monitor = self._get_monitor(context, id)
	    monitor.update(s)
        return self._make_monitor_dict(monitor)
        
    ###Virtual IP's
    def _get_vip(self, context, id):
        try:
            vip = self._get_by_id(context, LB_Virtual_IP, id)
        except exc.NoResultFound:
            raise q_exc.VIPNotFound(vip_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple vips match for %s' % id)
            raise q_exc.VIPNotFound(vip_id=id)
        return vip
    
    def _make_vip_dict(self, vip, fields=None):
        for pl in vip['session_persistance']:
            session_persistance_type = str(pl['type'])
            session_persistance_cookie = str(pl['cookie_name'])
            
        res = {'id': vip['id'],
               'name': vip['name'],
               'description': vip['description'],
               'port_no': vip['port_no'],
               'protocol': vip['protocol'],
               'connection_limit': vip['connection_limit'],
               'pool_id': vip['pool_id'],
               'config_handle_id': vip['config_handle_id'],
               'session_persistance_id': vip['session_persistance_id'],
               'tenant_id': vip['tenant_id'],
               'status': vip['status'],
               'admin_status': vip['admin_status'],
               'session_persistance_type': session_persistance_type,
               'session_persistance_cookie': session_persistance_cookie}

        return self._fields(res, fields)


    def get_vip(self, context, id, fields=None):
        vip = self._get_vip(context, id)
        return self._make_vip_dict(vip, fields)

    def get_vips(self, context, filters=None, fields=None):
        return self._get_collection(context, LB_Virtual_IP,
                                    self._make_vip_dict,
                                    filters=filters, fields=fields)
        
    def create_vip(self, context, vip):
        """ handle creation of a single vip """
        # single request processing
        s = vip['vip']
        # NOTE(jkoelker) Get the tenant_id outside of the session to avoid
        #                unneeded db action if the operation raises
        tenant_id = self._get_tenant_id_for_create(context, s)
        with context.session.begin(subtransactions=True):
            vip = LB_Virtual_IP(tenant_id=tenant_id,
                                        id=s.get('id') or utils.str_uuid(),
                                        name=s['name'],
                                        description=s['description'],
                                        port_no=s['port_no'],
                                        protocol=s['protocol'],
                                        connection_limit=s['connection_limit'],
                                        status=1,
                                        admin_status=1,
                                        session_persistance_id=s['session_persistance_id'],
                                        config_handle_id=s['config_handle_id'],
                                        pool_id=s['pool_id'])
            context.session.add(vip)
        return self._make_vip_dict(vip)
        
    def delete_vip(self, context, id):
        with context.session.begin(subtransactions=True):
            vip = self._get_vip(context, id)
            context.session.delete(vip)
            
    def update_vip(self, context, id, vip):
        """Update the vip with new info."""

        s = vip['vip']
	with context.session.begin(subtransactions=True):
	    vip = self._get_vip(context, id)
	    vip.update(s)
        return self._make_vip_dict(vip)
        
    ###Session Persistance
    def _get_session(self, context, id):
        try:
            session = self._get_by_id(context, LB_Session_Persistance, id)
        except exc.NoResultFound:
            raise q_exc.SessionPersistanceNotFound(session_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple sessions match for %s' % id)
            raise q_exc.SessionPersistanceNotFound(session_id=id)
        return session
    
    def _make_session_dict(self, session, fields=None):
        res = {'id': session['id'],
               'type': session['type'],
               'cookie_name': session['cookie_name']}

        return self._fields(res, fields)

    def get_session(self, context, id, fields=None):
        session = self._get_session(context, id)
        return self._make_session_dict(session, fields)

    def get_sessions(self, context, filters=None, fields=None):
        return self._get_collection(context, LB_Session_Persistance,
                                    self._make_session_dict,
                                    filters=filters, fields=fields)
        
    def create_session(self, context, session):
        """ handle creation of a single session """
        # single request processing
        s = session['session']
        # NOTE(jkoelker) Get the tenant_id outside of the session to avoid
        #                unneeded db action if the operation raises
        tenant_id = self._get_tenant_id_for_create(context, s)
        with context.session.begin(subtransactions=True):
            session = LB_Session_Persistance(id=s.get('id') or utils.str_uuid(),
                                        type=s['type'],
                                        cookie_name=s['cookie_name'])
            context.session.add(session)
        return self._make_session_dict(session)
        
    def delete_session(self, context, id):
        with context.session.begin(subtransactions=True):
            session = self._get_session(context, id)
            context.session.delete(session)
            
    def update_session(self, context, id, session):
        """Update the session with new info."""

        s = session['session']
	with context.session.begin(subtransactions=True):
	    session = self._get_session(context, id)
	    session.update(s)
        return self._make_session_dict(session)
        
    def create_config(self, context, config):
        c = config['config']
        id = c['config_handle_id']
        slug = c['slug']
        version = c['version']
        vip_qry = context.session.query(LB_Virtual_IP)
        vips = vip_qry.filter_by(config_handle_id=id).all()
        lb_str = "global\n\
    daemon\n\
    maxconn 256\n\
    stats socket /tmp/haproxy\n\
\n\
defaults\n\
    mode http\n\
    timeout connect 5000ms\n\
    timeout client 50000ms\n\
    timeout server 50000ms\n\
    stats enable\n\
    log global\n\
    stats scope .\n\
    stats realm Haproxy\ Statistics\n\
    stats uri /haproxy?stats\n\
    option contstats\n\n"
        for vip in vips:
            pool_id = vip.pool_id
            pool_qry = context.session.query(LB_Pool)
            pool = pool_qry.filter_by(id=pool_id).one()
            
            pool_member_qry = context.session.query(LB_Pool_Member)
            pool_members = pool_member_qry.filter_by(pool_id=pool_id).all()
            
            health_monitor_qry = context.session.query(LB_Health_Monitor)
            try:
                health_monitors = health_monitor_qry.filter_by(pool_id=pool_id).one()
            except:
                LOG.debug(_("No Health Monitors Mapped for the Virtual IP"))
                health_monitors = []
                
            
            session_pers_qry = context.session.query(LB_Session_Persistance)
            session_pers = session_pers_qry.filter_by(id=vip.session_persistance_id).one()
            
            ##VIP Details
            vip_name = vip.name
            vip_protocol = str(vip.protocol)
            vip_port = vip.port_no
            vip_conn_limit = vip.connection_limit
            
            ##Pool Details
            pool_name = pool.name
            pool_protocol = pool.protocol
            pool_lb_method = str(pool.lb_method)
            
            ##Health Monitors Details
            if health_monitors:
                hm_type = health_monitors.type
                hm_timeout = health_monitors.type
                hm_delay = health_monitors.delay
                hm_max_retries = health_monitors.max_retries
                hm_http_method = health_monitors.http_method
                hm_url_path = health_monitors.url_path
                hm_expected_codes = health_monitors.expected_codes
            else:
                hm_type = ''
                hm_timeout = ''
                hm_delay = ''
                hm_max_retries = ''
                hm_http_method = ''
                hm_url_path = ''
                hm_expected_codes = ''
            
            ###Session Persistance
            session_type = session_pers.type
            cookie_name = session_pers.cookie_name
            
            #lb_str += "listen\t %s" % (vip_name) + " %s" % (server_ip) + ":%s" % (port_num) + "\n"
            lb_str += "listen %s" % (vip_name) + "\n"
            lb_str += "\t mode %s" % (vip_protocol.lower()) + "\n"
            lb_str += "\t bind :%s" % (vip_port) + "\n"
            lb_str += "\t maxconn %s" % (vip_conn_limit) + "\n"
            lb_str += "\t balance %s" % (pool_lb_method.lower()) + "\n"
            
            if hm_type == 'HTTP':
                lb_str += "\t option httpchk"
                
                if len(hm_http_method) > 0:
                    lb_str += " %s" % (hm_http_method)
                else:
                    lb_str += " OPTIONS"
                
                if len(hm_url_path) > 0:
                    lb_str += " %s" % (hm_url_path)
                else:
                    lb_str += " /"
                    
                lb_str += " HTTP/1.0\n"
                
            if len(hm_expected_codes) > 0 and hm_expected_codes:
                lb_str += "\t http-check expect"
                
                try:
                    hm_expected_codes = int(hm_expected_codes)
                    lb_str += " status %s" % (hm_expected_codes)
                except:
                    lb_str += " %s" % (hm_expected_codes)
                
                lb_str += "\n"
                
            if len(session_type) > 0 and session_type:
                lb_str += "\t option persist\n"
                if session_type == 'HTTP_COOKIE' and len(cookie_name) > 0:
                    lb_str += "\t cookie %s" % (cookie_name) + " insert\n"
                
                if session_type == 'APP_COOKIE' and len(cookie_name) > 0:
                    lb_str += "\t appsession %s" % (cookie_name) + " len 64 timeout 1h\n"
                
            for pm in pool_members:
                pm_name = str(pm.ip_address)
                pm_port_no = pm.port_no
                pm_weight = pm.weight
                
                lb_str += "\t server %s" % (pm_name) + " %s" % (pm_name) + ":%s" % (pm_port_no)
		if session_type == 'HTTP_COOKIE':
		    ck_name = pm_name.replace('.','')
		    lb_str += " cookie %s" % (ck_name)
		    
                if pm_weight:
                    lb_str += " weight %s" % (pm_weight)
                
                if hm_delay or hm_max_retries:
                    lb_str += " check"
                    if hm_delay:
                        lb_str += " inter %s" % (hm_delay)
                    if hm_max_retries:
                        lb_str += " fall %s" % (hm_max_retries)
                    
                    lb_str += " rise 1"
                
                lb_str += "\n"
                
                
                
            #with open('/tmp/haproxy.cfg', 'w+') as f:
            #    f.write(lb_str)
            #    f.close()
                
        res = {'config_handle_id': id,
               'data': lb_str,
               'slug': slug,
               'version': version,
               'header': 'data'}
        return res
        #return True
