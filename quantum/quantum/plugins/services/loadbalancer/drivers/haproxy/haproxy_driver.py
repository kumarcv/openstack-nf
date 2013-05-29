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
# @author: Oleg Bondarev (obondarev@mirantis.com)
#

from quantum.openstack.common import cfg
from quantum.plugins.services.loadbalancer.drivers import base_driver
from quantum.plugins.services.loadbalancer.drivers import exceptions
from quantum.plugins.services.loadbalancer.drivers import vm_utils
from quantum.plugins.services.loadbalancer.drivers.haproxy import (
    config_models as models)
from quantum.plugins.services.loadbalancer.drivers.haproxy import (
    config_manager)
from quantum.plugins.services.loadbalancer.drivers.haproxy import constants
from quantum.plugins.services.loadbalancer.drivers.haproxy import (
    remote_control)
from quantum.openstack.common import log as logging

LOG = logging.getLogger(__name__)

HAPROXY_OPTS = [
    cfg.StrOpt("haproxy_flavor_name", default="m1.tiny",
               help=_("Flavor name to run a haproxy VM")),
    cfg.StrOpt("haproxy_image_id", default="",
               help=_("Glance image id for a haproxy VM")),
    cfg.StrOpt("haproxy_keypair", default="haproxy-keypair",
               help=_("Keypair name for a haproxy VM")),
    cfg.StrOpt("haproxy_key_path",
               default="/root/.ssh/haproxy-keypair.pem",
               help=_("Path to the private key for ssh to a haproxy VM")),
]

cfg.CONF.register_opts(HAPROXY_OPTS, 'HAPROXY')


def validate_device(method):
    """
    Validates that given device dictionary contains
    all info needed to config HAProxy loadbalancer
    """
    def wrapper(*args, **kwargs):
        if 'device' in kwargs:
            device = kwargs['device']
        else:
            device = args[1]
        if 'management' not in device:
            msg = _('"management" not found in device: %s') % (device,)
            LOG.error(msg)
            raise HAProxyError(msg=msg)
        for field in ['address']:
            if field not in device['management']:
                msg = _('"%s" not found in device management info') % (field,)
                LOG.error(msg)
                raise HAProxyError(msg=msg)
        return method(*args, **kwargs)
    return wrapper


class HAProxyError(exceptions.LoadbalancerDriverException):
    message = _('Haproxy error: %(msg)s')


class HAProxyDriver(base_driver.BaseLoadbalancerDriver):
    """Driver for HAProxy loadbalancer (http://haproxy.1wt.eu/)"""

    driver_type = 'HAPROXY'
    driver_version = 'v1.0'

    def get_type(self):
        return self.driver_type

    def get_version(self):
        return self.driver_version

    def create_device(self, device):
        return vm_utils.create_vm('haproxy',
                                  cfg.CONF.HAPROXY.haproxy_image_id,
                                  cfg.CONF.HAPROXY.haproxy_flavor_name,
                                  cfg.CONF.HAPROXY.haproxy_keypair,
                                  device['subnet_id'],
                                  device['tenant_id'])

    def delete_device(self, device):
        return vm_utils.shutdown_vm(device['tenant_id'],
                                    device['management']['instance_id'])

    @validate_device
    def create_vip(self, device, vip):
        LOG.debug(_('Create VIP: device=%(device)s, vip=%(vip)s'),
                  {'device': device, 'vip': vip})
        with config_manager.ConfigManager(device) as config:
            frontend = models.HaproxyFrontend(vip)
            config.add_frontend(frontend)
            if 'session_persistence' in vip:
                backend = models.HaproxyConfigBlock(vip['pool_id'], 'backend')
                config.add_persistence(backend, vip['session_persistence'])
        LOG.debug(_('Create VIP succeed'))

    @validate_device
    def update_vip(self, device, new_vip, old_vip):
        LOG.debug(_('Update VIP: device=%(device)s, old vip=%(vip1)s, '
                    'new vip=%(vip2)s'),
                  {'device': device, 'vip1': old_vip, 'vip2': new_vip})
        with config_manager.ConfigManager(device) as config:
            frontend = models.HaproxyFrontend(new_vip)
            config.delete_block(frontend)
            config.add_frontend(frontend)

            if 'session_persistence' in new_vip:
                backend = models.HaproxyConfigBlock(new_vip['pool_id'],
                                                    'backend')
                config.delete_persistence(backend)
                # empty session_persistence dict means just delete existing
                # session persistence
                if new_vip['session_persistence']:
                    config.add_persistence(backend,
                                           new_vip['session_persistence'])
        LOG.debug(_('Update VIP succeed'))

    @validate_device
    def delete_vip(self, device, vip):
        LOG.debug(_('Delete VIP: device=%(device)s, vip=%(vip)s'),
                  {'device': device, 'vip': vip})
        with config_manager.ConfigManager(device) as config:
            # delete frontend first
            config.delete_block(models.HaproxyFrontend(vip))
            # then delete session persistence from backend
            # associated with the vip
            backend = models.HaproxyConfigBlock(vip['pool_id'],
                                                'backend')
            config.delete_persistence(backend)
        LOG.debug(_('Delete VIP succeed'))

    @validate_device
    def create_pool(self, device, pool):
        LOG.debug(_('Create pool: device=%(device)s, pool=%(pool)s'),
                  {'device': device, 'pool': pool})
        with config_manager.ConfigManager(device) as config:
            backend = models.HaproxyBackend(pool)
            config.add_backend(backend)
        LOG.debug(_('Create pool succeed'))

    @validate_device
    def update_pool(self, device, new_pool, old_pool):
        LOG.debug(_('Update pool: device=%(device)s, old pool=%(pool1)s, '
                    'new pool=%(pool2)s'),
                  {'device': device, 'pool1': old_pool, 'pool2': new_pool})
        with config_manager.ConfigManager(device) as config:
            old_backend = models.HaproxyBackend(old_pool)
            new_backend = models.HaproxyBackend(new_pool)
            config.update_backend(old_backend, new_backend)
        LOG.debug(_('Update pool succeed'))

    @validate_device
    def delete_pool(self, device, pool):
        LOG.debug(_('Delete pool: device=%(device)s, pool=%(pool)s'),
                  {'device': device, 'pool': pool})
        with config_manager.ConfigManager(device) as config:
            config.delete_block(models.HaproxyBackend(pool))
        LOG.debug(_('Delete pool succeed'))

    @validate_device
    def create_member(self, device, member):
        LOG.debug(_('Create member: device=%(device)s, member=%(member)s'),
                  {'device': device, 'member': member})
        with config_manager.ConfigManager(device) as config:
            backend = models.HaproxyConfigBlock(member['pool_id'], 'backend')
            server = models.HaproxyServer(member)
            config.add_server(backend, server)
        LOG.debug(_('Create member succeed'))

    @validate_device
    def update_member(self, device, new_member, old_member):
        LOG.debug(_('Update member: device=%(device)s, old member=%(member1)s,'
                    ' new member=%(member2)s'),
                  {'device': device, 'member1': old_member,
                   'member2': new_member})
        with config_manager.ConfigManager(device) as config:
            backend = models.HaproxyConfigBlock(new_member['pool_id'],
                                                'backend')
            server = models.HaproxyServer(new_member)
            config.delete_server(backend, server)
            config.add_server(backend, server)
        LOG.debug(_('Update member succeed'))

    @validate_device
    def delete_member(self, device, member):
        LOG.debug(_('Delete member: device=%(device)s, member=%(member)s'),
                  {'device': device, 'member': member})
        with config_manager.ConfigManager(device) as config:
            backend = models.HaproxyConfigBlock(member['pool_id'], 'backend')
            server = models.HaproxyServer(member)
            config.delete_server(backend, server)
        LOG.debug(_('Member deleted successfully'))

    @validate_device
    def create_health_monitor(self, device, health_monitor, pool_id):
        LOG.debug(_('Add health monitor to pool %(pool)s: device=%(device)s, '
                    'monitor=%(monitor)s'),
                  {'pool': pool_id, 'device': device,
                   'monitor': health_monitor})
        with config_manager.ConfigManager(device) as config:
            backend = models.HaproxyConfigBlock(pool_id, 'backend')
            if config.has_health_monitors(backend):
                msg = _('Can associate only one health monitor '
                        'with a HAProxy pool')
                LOG.error(msg)
                raise exceptions.ConfigError(msg=msg)
            probe = models.HaproxyProbe(health_monitor)
            config.add_probe(backend, probe)
        LOG.debug(_('Add health monitor succeed'))

    @validate_device
    def delete_health_monitor(self, device, health_monitor, pool_id):
        LOG.debug(_('Delete health monitor from pool %(pool)s: '
                    'device=%(device)s, monitor=%(monitor)s'),
                  {'pool': pool_id, 'device': device,
                   'monitor': health_monitor})
        with config_manager.ConfigManager(device) as config:
            backend = models.HaproxyConfigBlock(pool_id, 'backend')
            config.delete_probe(backend)
        LOG.debug(_('Delete health monitor succeed'))

    @validate_device
    def get_pool_stats(self, device, pool_id):
        LOG.debug(_('Get pool stats: device=%(device)s, pool=%(pool)s'),
                  {'device': device, 'pool': pool_id})
        remote_ctrl = remote_control.RemoteControl(device['management'])
        status, raw_stats, errors = remote_ctrl.get_backend_stats(pool_id)
        if status != 0:
            msg = _('Error while getting stats for pool %(pool_id)s: '
                    '%(errors)s') % {'pool_id': pool_id, 'errors': errors}
            LOG.error(msg)
            raise HAProxyError(msg=msg)
        if len(raw_stats.splitlines()) < 2 or not raw_stats.splitlines()[1]:
            msg = _('No stats found for pool %s') % (pool_id,)
            LOG.error(msg)
            raise HAProxyError(msg=msg)

        LOG.debug(_('Get pool stats succeed'))
        return self._parse_stats(raw_stats)

    @validate_device
    def get_member_stats(self, device, pool_id, member_id):
        LOG.debug(_('Get member stats: device=%(device)s, pool=%(pool)s, '
                    'member=%(member)s'),
                  {'device': device, 'pool': pool_id, 'member': member_id})
        remote_ctrl = remote_control.RemoteControl(device['management'])
        status, raw_stats, errors = remote_ctrl.get_server_stats(
            pool_id, member_id)
        if status != 0:
            msg = _('Error while getting stats for member %(member_id)s: '
                    '%(errors)s') % {'member_id': member_id,
                                     'errors': errors}
            LOG.error(msg)
            raise HAProxyError(msg=msg)
        if len(raw_stats.splitlines()) < 2 or not raw_stats.splitlines()[1]:
            msg = _('No stats found for member %s') % (member_id,)
            LOG.error(msg)
            raise HAProxyError(msg=msg)

        LOG.debug(_('Get member stats succeed'))
        return self._parse_stats(raw_stats)

    def _parse_stats(self, raw_stats):
        stat_lines = raw_stats.splitlines()
        if len(stat_lines) < 2:
            return {}
        stat_names = [line.strip('# ') for line in stat_lines[0].split(',')]
        stat_values = [line.strip() for line in stat_lines[1].split(',')]
        stats = dict(zip(stat_names, stat_values))
        stats['check_status'] = self._map_health(stats['check_status'])
        result_stats = {}
        for stat in constants.STATS_MAPPING:
            result_stats[stat] = stats.get(constants.STATS_MAPPING[stat], '')

        return result_stats

    def _map_health(self, raw_health):
        return constants.HEALTH_MAPPING.get(raw_health, 'UNKNOWN')
