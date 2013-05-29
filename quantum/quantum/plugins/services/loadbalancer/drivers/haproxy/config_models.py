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

import uuid

from quantum.plugins.services.loadbalancer.drivers import exceptions
from quantum.plugins.services.loadbalancer.drivers.haproxy import constants
from quantum.openstack.common import log as logging

LOG = logging.getLogger(__name__)

'''
    The module provides objects that serve as a transitional layer between
    LBaaS API and HAProxy object models
'''


class HaproxyConfigBlock(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type


class HaproxyFrontend(HaproxyConfigBlock):
    def __init__(self, vip):
        super(HaproxyFrontend, self).__init__(vip['id'], 'frontend')
        self._validate_vip(vip)

        # a 16 bit integer needed as an id for retrieving stats
        self.id = uuid.UUID(vip['id']).time_mid
        self.bind_address = vip['address']
        self.bind_port = vip['port']
        self.default_backend = vip['pool_id']
        self.mode = constants.PROTOCOL_MAPPING[vip['protocol']]
        self.maxconn = vip['connection_limit']
        self.enabled = vip['admin_state_up']

    def _validate_vip(self, vip):
        protocol = vip.get('protocol')
        if not protocol in constants.PROTOCOL_MAPPING:
            msg = _('Unsupported protocol type %s') % (protocol,)
            LOG.error(msg)
            raise exceptions.ConfigError(msg=msg)


class HaproxyBackend(HaproxyConfigBlock):
    def __init__(self, pool):
        super(HaproxyBackend, self).__init__(pool['id'], 'backend')
        self._validate_pool(pool)

        # a 16 bit integer needed as an id for retrieving stats
        self.id = uuid.UUID(pool['id']).time_mid
        self.balance = constants.ALGORITHMS_MAPPING[pool['lb_method']]
        self.mode = constants.PROTOCOL_MAPPING[pool['protocol']]
        self.enabled = pool['admin_state_up']

    def _validate_pool(self, pool):
        protocol = pool.get('protocol')
        if not protocol in constants.PROTOCOL_MAPPING:
            msg = _('Unsupported protocol type %s') % (protocol,)
            LOG.error(msg)
            raise exceptions.ConfigError(msg=msg)

        lb_method = pool.get('lb_method')
        if not lb_method in constants.ALGORITHMS_MAPPING:
            msg = _('Unsupported lb_method %s') % (lb_method,)
            LOG.error(msg)
            raise exceptions.ConfigError(msg=msg)


class HaproxyServer(HaproxyConfigBlock):
    def __init__(self, member):
        super(HaproxyServer, self).__init__(member['id'], 'server')
        # a 16 bit integer needed as an id for retrieving stats
        self.id = uuid.UUID(member['id']).time_mid
        self.backend = member['pool_id']
        self.address = member['address']
        self.port = member['port']
        self.weight = member['weight']
        self.enabled = member['admin_state_up']


class HaproxyProbe(HaproxyConfigBlock):
    def __init__(self, health_monitor):
        super(HaproxyProbe, self).__init__(health_monitor['id'], 'probe')
        self._validate_health_monitor(health_monitor)

        self.probe_type = health_monitor['type']
        self.inter = health_monitor['delay'] * 1000
        self.timeout = health_monitor['timeout'] * 1000
        self.fall = health_monitor['max_retries']
        self.enabled = health_monitor['admin_state_up']
        if self.probe_type in ['HTTP', 'HTTPS']:
            self.method = health_monitor['http_method']
            self.uri = health_monitor['url_path']
            self.expect = health_monitor['expected_codes']

    def _validate_health_monitor(self, health_monitor):
        monitor_type = health_monitor['type']
        if monitor_type not in ('TCP', 'HTTP', 'HTTPS'):
            msg = _('Unsupported health_monitor type %s') % (monitor_type,)
            LOG.error(msg)
            raise exceptions.ConfigError(msg=msg)
