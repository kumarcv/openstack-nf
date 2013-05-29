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

from quantum.common import rpc as q_rpc
from quantum.common import topics
from quantum.openstack.common import log as logging
from quantum.openstack.common import rpc
from quantum.openstack.common.rpc import proxy
from quantum.plugins.common import constants
from quantum.plugins.services.loadbalancer.api import (
    loadbalancer_agent_api as agent_api)
from quantum.plugins.services.loadbalancer.api import (
    loadbalancer_plugin_api as plugin_api)

LOG = logging.getLogger(__name__)

STATUSES = {
    plugin_api.STATUS_OK: constants.ACTIVE,
    plugin_api.STATUS_ERROR: constants.ERROR,
}


class LoadbalancerPluginCallbacks(plugin_api.LoadbalancerPluginAPI):
    def __init__(self, db_plugin, scheduler):
        self._setup_rpc()
        self.db_plugin = db_plugin
        self.scheduler = scheduler

    def _setup_rpc(self):
        topic = topics.LOADBALANCER_PLUGIN
        self.conn = rpc.create_connection(new=True)
        self.dispatcher = q_rpc.PluginRpcDispatcher([self])
        self.conn.create_consumer(topic, self.dispatcher, fanout=False)
        self.conn.consume_in_thread()

    def confirm_device(self, context, device, status, message):
        LOG.debug(_('Confirm status %(status)s for device %(id)s '),
                  {'status': status, 'id': device['id']})
        if (device['status'] == constants.PENDING_DELETE and
                status == plugin_api.STATUS_OK):
            self.scheduler.delete_device(context, device)
        else:
            device['status'] = STATUSES[status]
            self.scheduler.update_device(context, device)

    def confirm(self, context, model, obj_id, status, message):
        LOG.debug(_('Confirm status %(status)s for %(model)s:%(id)s '),
                  {'status': status, 'model': model, 'id': obj_id})
        obj = self.db_plugin.get_by_id(context, model, obj_id)
        if (obj.status == constants.PENDING_DELETE and
                status == plugin_api.STATUS_OK):
            self.db_plugin.delete_by_id(context, model, obj_id)
        else:
            self.db_plugin.update_status_str(context, model, obj_id,
                                             STATUSES[status])

    def store_pool_stats(self, context, obj_id, data, status, message):
        if status == plugin_api.STATUS_ERROR:
            LOG.warn(_('Stats retrieval failed with error "%s"'), message)
            return

        self.db_plugin.store_pool_stats(context, obj_id, data)


class LoadbalancerAgentCaller(proxy.RpcProxy, agent_api.LoadbalancerAgentAPI):
    """Plugin side of the loadbalancer rpc API.

    API version history:
        1.0 - Initial version.

    """
    BASE_RPC_API_VERSION = '1.0'

    def __init__(self, topic, host=None):
        super(LoadbalancerAgentCaller, self).__init__(
            topic=topic, default_version=self.BASE_RPC_API_VERSION)

    def _api_call(self, context, method, device, **kwargs):
        msg = self.make_msg(method, device=device, **kwargs)
        LOG.debug(_('Going to cast RPC message %s'), msg)
        self.cast(context, msg, topic=self.topic)
        LOG.debug(_('RPC cast succeed'))

    def create_vip(self, context, device, vip):
        self._api_call(context, 'create_vip', device, vip=vip)

    def update_vip(self, context, device, new_vip, old_vip):
        self._api_call(context, 'update_vip', device, new_vip=new_vip,
                       old_vip=old_vip)

    def delete_vip(self, context, device, vip):
        self._api_call(context, 'delete_vip', device, vip=vip)

    def create_pool(self, context, device, pool):
        self._api_call(context, 'create_pool', device, pool=pool)

    def update_pool(self, context, device, new_pool, old_pool):
        self._api_call(context, 'update_pool', device, new_pool=new_pool,
                       old_pool=old_pool)

    def delete_pool(self, context, device, pool):
        self._api_call(context, 'delete_pool', device, pool=pool)

    def create_member(self, context, device, member):
        self._api_call(context, 'create_member', device, member=member)

    def update_member(self, context, device, new_member, old_member):
        self._api_call(context, 'update_member', device, new_member=new_member,
                       old_member=old_member)

    def delete_member(self, context, device, member):
        self._api_call(context, 'delete_member', device, member=member)

    def create_health_monitor(self, context, device, health_monitor, pool_id):
        self._api_call(context, 'create_health_monitor', device,
                       health_monitor=health_monitor, pool_id=pool_id)

    def update_health_monitor(self, context, device, new_health_monitor,
                              old_health_monitor, pool_id):
        self._api_call(context, 'update_health_monitor', device,
                       new_health_monitor=new_health_monitor,
                       old_health_monitor=old_health_monitor,
                       pool_id=pool_id)

    def delete_health_monitor(self, context, device, health_monitor, pool_id):
        self._api_call(context, 'delete_health_monitor', device,
                       health_monitor=health_monitor, pool_id=pool_id)

    def get_pool_stats(self, context, device, pool_id):
        self._api_call(context, 'get_pool_stats', device, pool_id=pool_id)
