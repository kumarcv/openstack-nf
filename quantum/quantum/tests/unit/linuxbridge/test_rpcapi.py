# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012, Red Hat, Inc.
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

"""
Unit Tests for linuxbridge rpc
"""

import stubout
import unittest2

from quantum.agent import rpc as agent_rpc
from quantum.common import topics
from quantum.openstack.common import context
from quantum.openstack.common import rpc
from quantum.plugins.linuxbridge import lb_quantum_plugin as plb


class rpcApiTestCase(unittest2.TestCase):

    def _test_lb_api(self, rpcapi, topic, method, rpc_method, **kwargs):
        ctxt = context.RequestContext('fake_user', 'fake_project')
        expected_retval = 'foo' if method == 'call' else None
        expected_msg = rpcapi.make_msg(method, **kwargs)
        expected_msg['version'] = rpcapi.BASE_RPC_API_VERSION
        if rpc_method == 'cast' and method == 'run_instance':
            kwargs['call'] = False

        self.fake_args = None
        self.fake_kwargs = None

        def _fake_rpc_method(*args, **kwargs):
            self.fake_args = args
            self.fake_kwargs = kwargs
            if expected_retval:
                return expected_retval

        self.stubs = stubout.StubOutForTesting()
        self.stubs.Set(rpc, rpc_method, _fake_rpc_method)

        retval = getattr(rpcapi, method)(ctxt, **kwargs)

        self.assertEqual(retval, expected_retval)
        expected_args = [ctxt, topic, expected_msg]

        for arg, expected_arg in zip(self.fake_args, expected_args):
            self.assertEqual(arg, expected_arg)

    def test_delete_network(self):
        rpcapi = plb.AgentNotifierApi(topics.AGENT)
        self._test_lb_api(rpcapi,
                          topics.get_topic_name(topics.AGENT,
                                                topics.NETWORK,
                                                topics.DELETE),
                          'network_delete', rpc_method='fanout_cast',
                          network_id='fake_request_spec')

    def test_port_update(self):
        rpcapi = plb.AgentNotifierApi(topics.AGENT)
        self._test_lb_api(rpcapi,
                          topics.get_topic_name(topics.AGENT,
                                                topics.PORT,
                                                topics.UPDATE),
                          'port_update', rpc_method='fanout_cast',
                          port='fake_port',
                          physical_network='fake_net',
                          vlan_id='fake_vlan_id')

    def test_device_details(self):
        rpcapi = agent_rpc.PluginApi(topics.PLUGIN)
        self._test_lb_api(rpcapi, topics.PLUGIN,
                          'get_device_details', rpc_method='call',
                          device='fake_device',
                          agent_id='fake_agent_id')

    def test_update_device_down(self):
        rpcapi = agent_rpc.PluginApi(topics.PLUGIN)
        self._test_lb_api(rpcapi, topics.PLUGIN,
                          'update_device_down', rpc_method='call',
                          device='fake_device',
                          agent_id='fake_agent_id')

    def test_update_device_up(self):
        rpcapi = agent_rpc.PluginApi(topics.PLUGIN)
        self._test_lb_api(rpcapi, topics.PLUGIN,
                          'update_device_up', rpc_method='call',
                          device='fake_device',
                          agent_id='fake_agent_id')
