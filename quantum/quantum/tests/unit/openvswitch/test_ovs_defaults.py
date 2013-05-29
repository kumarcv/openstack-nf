# Copyright (c) 2012 OpenStack, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from quantum.openstack.common import cfg
from quantum.plugins.openvswitch.common import config


class ConfigurationTest(unittest.TestCase):

    def test_defaults(self):
        self.assertEqual('br-int', cfg.CONF.OVS.integration_bridge)
        self.assertFalse(cfg.CONF.OVS.enable_tunneling)
        self.assertEqual('br-tun', cfg.CONF.OVS.tunnel_bridge)
        self.assertEqual('sqlite://', cfg.CONF.DATABASE.sql_connection)
        self.assertEqual(-1, cfg.CONF.DATABASE.sql_max_retries)
        self.assertEqual(2, cfg.CONF.DATABASE.reconnect_interval)
        self.assertEqual(2, cfg.CONF.AGENT.polling_interval)
        self.assertEqual('sudo', cfg.CONF.AGENT.root_helper)
        self.assertTrue(cfg.CONF.AGENT.rpc)
        self.assertEqual('local', cfg.CONF.OVS.tenant_network_type)
        self.assertEqual(0, len(cfg.CONF.OVS.bridge_mappings))
        self.assertEqual(0, len(cfg.CONF.OVS.network_vlan_ranges))
        self.assertEqual(0, len(cfg.CONF.OVS.tunnel_id_ranges))
