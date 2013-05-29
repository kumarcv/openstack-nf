# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Mirantis Inc.
# All Rights Reserved
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
# @author: Ilya Shakhat, Mirantis Inc.

from quantum.agent.services.driver_manager import ServiceDriverManager
from quantum.common import topics
from quantum.openstack.common import log as logging
from quantum.openstack.common.rpc import proxy as rpc_proxy
from quantum.plugins.common import constants
from quantum.plugins.services.loadbalancer.api import loadbalancer_agent_api
from quantum.plugins.services.loadbalancer.api import loadbalancer_plugin_api

LOG = logging.getLogger(__name__)


class LoadbalancerAgentCallbacks(loadbalancer_agent_api.LoadbalancerAgentAPI):
    def create_vip(self, context, device, vip):
        LOG.debug(_('Got request to create vip %(v)s on device %(d)s'),
                  {'d': device['id'], 'v': vip['id']})
        proxy.create_vip(device, vip).confirm(context, 'vip', vip['id'])

    def update_vip(self, context, device, new_vip, old_vip):
        LOG.debug(_('Got request to update vip %(v)s on device %(d)s'),
                  {'d': device['id'], 'v': new_vip['id']})
        proxy.update_vip(device, new_vip, old_vip).confirm(context, 'vip',
                                                           new_vip['id'])

    def delete_vip(self, context, device, vip):
        LOG.debug(_('Got request to delete vip %(v)s on device %(d)s'),
                  {'d': device['id'], 'v': vip['id']})
        proxy.delete_vip(device, vip).confirm(context, 'vip', vip['id'])

    def _create_device(self, device):
        LOG.debug(_('Device %s is pending create, going to create it'),
                  device['id'])
        res = proxy.create_device(device)
        if res.status == loadbalancer_plugin_api.STATUS_OK:
            LOG.debug(_('Device %(dev)s is created, its management '
                        'is %(mgmt)s'),
                      {'dev': device['id'], 'mgmt': res.data})
            device['management'] = res.data
        else:
            LOG.warn(_('Device %s is not created'), device['id'])
        return res

    def create_pool(self, context, device, pool):
        LOG.debug(_('Got request to create pool %(p)s on device %(d)s'),
                  {'d': device['id'], 'p': pool['id']})
        ok = True
        need_create_device = device['status'] == constants.PENDING_CREATE

        if need_create_device:
            res_dev = self._create_device(device)
            ok = res_dev.status == loadbalancer_plugin_api.STATUS_OK

        if ok:
            res_pool = proxy.create_pool(device, pool)
            status = res_pool.status
            msg = res_pool.message

            if (status == loadbalancer_plugin_api.STATUS_ERROR and
                    need_create_device):
                LOG.warn(_('Failed to create pool %(p)s on fresh device %(d)s.'
                           ' The device will be deleted.'),
                         {'p': pool['id'], 'd': device['id']})
                device['status'] = constants.PENDING_DELETE
                res_dev = proxy.delete_device(device)
        else:
            LOG.debug(_('Failed to create device %s. Pool will not be '
                        'created'), device['id'])
            status = loadbalancer_plugin_api.STATUS_ERROR
            msg = _('Pool is not created due to failure of device creation')

        if need_create_device:
            plugin_caller.confirm_device(context, device, res_dev.status,
                                         res_dev.message)
        plugin_caller.confirm(context, 'pool', pool['id'], status, msg)

    def update_pool(self, context, device, new_pool, old_pool):
        LOG.debug(_('Got request to update pool %(p)s on device %(d)s'),
                  {'d': device['id'], 'p': new_pool['id']})
        proxy.update_pool(device, new_pool, old_pool).confirm(context, 'pool',
                                                              new_pool['id'])

    def _delete_device(self, context, device):
        LOG.debug(_('Device %s is pending delete, going to delete it'),
                  device['id'])
        res = proxy.delete_device(device)
        LOG.debug(_('Device %s is deleted'), device['id'])
        plugin_caller.confirm_device(context, device, res.status, res.message)

    def delete_pool(self, context, device, pool):
        LOG.debug(_('Got request to delete pool %(p)s on device %(d)s'),
                  {'d': device['id'], 'p': pool['id']})
        res = proxy.delete_pool(device, pool)
        plugin_caller.confirm(context, 'pool', pool['id'], res.status,
                              res.message)
        if device['status'] == constants.PENDING_DELETE:
            self._delete_device(context, device)

    def create_member(self, context, device, member):
        LOG.debug(_('Got request to create member %(m)s on device %(d)s'),
                  {'d': device['id'], 'm': member['id']})
        proxy.create_member(device, member).confirm(context, 'member',
                                                    member['id'])

    def update_member(self, context, device, new_member, old_member):
        LOG.debug(_('Got request to update member %(m)s on device %(d)s'),
                  {'d': device['id'], 'm': new_member['id']})
        proxy.update_member(device, new_member, old_member).confirm(
            context, 'member', new_member['id'])

    def delete_member(self, context, device, member):
        LOG.debug(_('Got request to delete member %(m)s on device %(d)s'),
                  {'d': device['id'], 'm': member['id']})
        proxy.delete_member(device, member).confirm(
            context, 'member', member['id'])

    def create_health_monitor(self, context, device, health_monitor, pool_id):
        LOG.debug(_('Got request to create health monitor %(hm)s for '
                    'pool %(p)s on device %(d)s'),
                  {'d': device['id'], 'hm': health_monitor['id'],
                   'p': pool_id})
        proxy.create_health_monitor(device, health_monitor, pool_id).confirm(
            context, 'pool', pool_id)

    def delete_health_monitor(self, context, device, health_monitor, pool_id):
        LOG.debug(_('Got request to delete health monitor %(hm)s '
                    'for pool %(p)s on device %(d)s'),
                  {'d': device['id'], 'hm': health_monitor['id'],
                   'p': pool_id})
        proxy.delete_health_monitor(device, health_monitor, pool_id).confirm(
            context, 'pool', pool_id)

    def get_pool_stats(self, context, device, pool_id):
        LOG.debug(_('Got request to get stats for pool %(p)s on device %(d)s'),
                  {'d': device['id'], 'p': pool_id})
        result = proxy.get_pool_stats(device, pool_id)
        plugin_caller.store_pool_stats(context, pool_id, result.data,
                                       result.status, result.message)


class Dispatcher(object):
    def __init__(self, data, device, status, message):
        self.data = data
        self.device = device
        self.status = status
        self.message = message

    def confirm(self, context, model, obj_id):
        plugin_caller.confirm(context, model, obj_id, self.status,
                              self.message)


class DriverProxy(object):
    def __getattr__(self, item):
        def dispatch(*params):
            status = loadbalancer_plugin_api.STATUS_OK
            message = loadbalancer_plugin_api.STATUS_OK
            device = params[0]
            data = None
            try:
                driver = ServiceDriverManager.get_driver(
                    constants.LOADBALANCER,
                    device['type'], device['version'])
                data = getattr(driver, item)(*params)
            except Exception as e:
                LOG.error(_('Exception "%s" occurred in the driver'), e)
                status = loadbalancer_plugin_api.STATUS_ERROR
                message = str(e)
            return Dispatcher(data, device, status, message)

        return dispatch


proxy = DriverProxy()


class LoadbalancerPluginCaller(rpc_proxy.RpcProxy,
                               loadbalancer_plugin_api.LoadbalancerPluginAPI):
    """Agent side of the loadbalancer rpc API.

    API version history:
        1.0 - Initial version.

    """
    BASE_RPC_API_VERSION = '1.0'

    def __init__(self, topic, host=None):
        super(LoadbalancerPluginCaller, self).__init__(
            topic=topic, default_version=self.BASE_RPC_API_VERSION)

    def confirm_device(self, context, device, status, message):
        LOG.debug(_('Going to confirm device %(id)s with '
                    'status %(status)s: "%(message)s"'),
                  {'id': device['id'], 'status': status, 'message': message})
        rpc_msg = self.make_msg('confirm_device', device=device, status=status,
                                message=message)
        self.cast(context, rpc_msg, topic=self.topic)
        LOG.debug(_('Confirmation for device %s is sent'), device['id'])

    def confirm(self, context, model, obj_id, status, message):
        LOG.debug(_('Going to confirm %(model)s:%(id)s with '
                    'status %(status)s: "%(message)s"'),
                  {'model': model, 'id': obj_id, 'status': status,
                   'message': message})
        rpc_msg = self.make_msg('confirm', model=model, obj_id=obj_id,
                                status=status, message=message)
        self.cast(context, rpc_msg, topic=self.topic)
        LOG.debug(_('Confirmation for object %s is sent'), obj_id)

    def store_pool_stats(self, context, obj_id, data, status, message):
        rpc_msg = self.make_msg('store_pool_stats', obj_id=obj_id, data=data,
                                status=status, message=message)
        self.cast(context, rpc_msg, topic=self.topic)
        LOG.debug(_('Pool statistics for object %s is sent'), obj_id)


plugin_caller = LoadbalancerPluginCaller(topics.LOADBALANCER_PLUGIN)
