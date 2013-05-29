# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from quantum.openstack.common import cfg
from quantum.common import topics
from quantum.db.loadbalancer import loadbalancer_db
from quantum.extensions.loadbalancer import LoadbalancerPluginBase
from quantum.openstack.common import log as logging
from quantum.plugins.common import constants
from quantum.plugins.services.loadbalancer import plugin_rpc
from quantum.openstack.common import importutils


LOG = logging.getLogger(__name__)


class LoadbalancerPlugin(LoadbalancerPluginBase):
    """
    Implementation of the Quantum Loadbalancer Service Plugin.

    This class manages the workflow of LBaaS request/response,
    DB related work is implemented in class LoadBalancerPluginDb
    """
    supported_extension_aliases = ["lbaas"]

    def __init__(self):
        self.db = loadbalancer_db.LoadbalancerPluginDb()
        self.driver = importutils.import_object(cfg.CONF.DRIVER.loadbalancer_driver)
        LOG.debug(_("Using SLB Scheduler Driver: %s"),str(self.driver))

    def get_plugin_type(self):
        return constants.LOADBALANCER

    def get_plugin_description(self):
        return "Quantum LoadBalancer Service Plugin"


    def _is_pending(self, obj):
        return obj['status'] in [constants.PENDING_CREATE,
                                 constants.PENDING_UPDATE,
                                 constants.PENDING_DELETE]

    def create_configuration(self, context, configuration):
        v = self.db.create_configuration(context, configuration)
        return v

    def update_configuration(self, context, configuration_id, configuration):
        LOG.debug(_('Update configuration %s'), configuration_id)
        v_new = self.db.update_configuration(context, configuration_id, configuration)
        return v_new

    def delete_configuration(self, context, configuration_id):
        LOG.debug(_('Delete configuration %s'), configuration_id)
        self.db.delete_configuration(context, configuration_id)

    def get_configuration(self, context, configuration_id, fields=None):
        LOG.debug(_('Get configuration %s'), configuration_id)
        return self.db.get_configuration(context, configuration_id, fields)

    def get_configurations(self, context, filters=None, fields=None):
        LOG.debug(_('Get configurations'))
        return self.db.get_configurations(context, filters, fields)
    
    """
    Handling Virtual IPs 
    """


    def create_vip(self, context, vip):
        vip_record = self.db.create_vip(context, vip)
        self.driver.vip_config_update(context,vip_record)
        return vip_record

    def update_vip(self, context, vip_id, vip):
        LOG.debug(_('Update vip %s'), vip_id)
        vip_update_record = self.db.update_vip(context, vip_id, vip)
        self.driver.vip_config_update(context,vip_update_record)
        return vip_update_record

    def delete_vip(self, context, vip_id):
        LOG.debug(_('Delete vip %s'), vip_id)
        vip_record = self.get_vip(context,vip_id)     # (trinath) added to support SLB driver
        self.db.delete_vip(context, vip_id)
        self.driver.vip_config_update(context,vip_record) # (trinath) added to support SLB driver

    def get_vip(self, context, vip_id, fields=None):
        LOG.debug(_('Get vip %s'), vip_id)
        return self.db.get_vip(context, vip_id, fields)

    def get_vips(self, context, filters=None, fields=None):
        LOG.debug(_('Get vips'))
        return self.db.get_vips(context, filters, fields)

    """
    Handling Pools
    """

    def create_pool(self, context, pool):
        pool_record = self.db.create_pool(context, pool)
        #self.driver.lb_pool_update(context,pool_record)
        return pool_record

    def update_pool(self, context, pool_id, pool):
        LOG.debug(_('Update pool %s'), pool_id)
        pool_new = self.db.update_pool(context, pool_id, pool)
        self.driver.lb_pool_update(context,pool_new)
        return pool_new

    def delete_pool(self, context, pool_id):
        LOG.debug(_('Delete pool %s'), pool_id)
        pool_record = self.get_pool(context,pool_id)
        self.db.delete_pool(context, pool_id)
        self.driver.lb_pool_update(context,pool_record) # Notify HAProxy Driver
        
    def get_pool(self, context, pool_id, fields=None):
        LOG.debug(_('Get pool %s'), pool_id)
        return self.db.get_pool(context, pool_id, fields)

    def get_pools(self, context, filters=None, fields=None):
        LOG.debug(_('Get Pools'))
        return self.db.get_pools(context, filters, fields)

    """
    Handling Pool Members
    """

    def get_member(self, context, member_id, fields=None):
        LOG.debug(_('Get member: %s'), member_id)
        return self.db.get_member(context, member_id, fields)

    def get_members(self, context, filters=None, fields=None):
        LOG.debug(_('Get members'))
        return self.db.get_members(context, filters, fields)

    def create_member(self, context, member):
        member_record = self.db.create_member(context, member)
        LOG.debug(_("Create new PoolMember: PoolMemberRecord: %s" % str(member_record)))
        self.driver.lb_config_update(context,member_record)
        LOG.debug(_('Create member: %s'), member_record['id'])
        return member_record

    def update_member(self, context, member_id, member):
        LOG.debug(_('Going to update member: %s'), member_id)
        member_update_record = self.db.update_member(context, member_id, member)
        self.driver.lb_config_update(context,member_update_record)
        return member_update_record

    def delete_member(self, context, member_id):
        LOG.debug(_('Delete member: %s'), member_id)
        member_record = self.get_member(context,member_id)
        self.db.delete_member(context, member_id)
        self.driver.lb_config_update(context,member_record)

    """
    Handling Health Monitors
    """

    def get_monitor(self, context, monitor_id, fields=None):
        LOG.debug(_('Get health monitor: %s'), monitor_id)
        res = self.db.get_monitor(context, monitor_id, fields)
        return res

    def get_monitors(self, context, filters=None, fields=None):
        LOG.debug(_('Get health monitors'))
        res = self.db.get_monitors(context, filters, fields)
        return res

    def create_monitor(self, context, monitor):
        monitor_record = self.db.create_monitor(context, monitor)
        self.driver.lb_config_update(context,monitor_record)
        return self.db.get_monitor(context, monitor_record['id'])

    def update_monitor(self, context, monitor_id, monitor):
        # It's allowed to update health monitor only if it is not
        # associated with any pool
        LOG.debug(_('Update health monitor: %s'), monitor_id)
        monitor_record = self.db.update_monitor(context,monitor_id,
                                                  monitor)
        self.driver.lb_config_update(context,monitor_record)
        return monitor_record

    def delete_monitor(self, context, monitor_id):
        # It's allowed to delete health monitor only if it is not
        # associated with any pool
        LOG.debug(_('Delete health monitor: %s'), monitor_id)
        monitor_record = self.get_monitor(context,monitor_id)
        self.db.delete_monitor(context, monitor_id)
        self.driver.lb_config_update(context,monitor_record)
    
    """
    Handling Session Persistance
    """

    def get_session(self, context, session_id, fields=None):
        LOG.debug(_('Get health session: %s'), session_id)
        res = self.db.get_session(context, session_id, fields)
        return res

    def get_sessions(self, context, filters=None, fields=None):
        LOG.debug(_('Get health sessions'))
        res = self.db.get_sessions(context, filters, fields)
        return res

    def create_session(self, context, session):
        sp_record = self.db.create_session(
            context, session)
        self.driver.lb_session_vips_update(context,sp_record)
        return self.db.get_session(context, sp_record['id'])

    def update_session(self, context, session_id, session):
        # It's allowed to update health session only if it is not
        # associated with any pool
        LOG.debug(_('Update health session: %s'), session_id)
        session_record = self.db.update_session(context, session_id,
                                                             session)
        self.drvier.lb_session_vips_update(context,session_record)
        return session_record

    def delete_session(self, context, session_id):
        # It's allowed to delete health session only if it is not
        # associated with any pool
        LOG.debug(_('Delete health session: %s'), session_id)
        sp_record = self.get_session(context,session_id)
        self.db.delete_session(context, session_id)
        self.driver.lb_session_vips_update(context,sp_record)
        
    """
    Generating Configuration File from Configuration Feilds
    """
    
    def create_config(self, context, config):
        res = self.db.create_config(context, config)
        #with open('/tmp/srik.out', 'w+') as f:
        #    f.write(str(res))
        #    f.close()
        return res

