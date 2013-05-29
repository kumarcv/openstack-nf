# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2012, Nachi Ueno, NTT MCL, Inc.
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

import socket
import sys
import uuid

import mock
import unittest2 as unittest

from quantum.agent.common import config
from quantum.agent.linux import interface
from quantum.agent.linux import utils
from quantum.common import exceptions
from quantum.debug import commands
from quantum.debug.debug_agent import DEVICE_OWNER_PROBE, QuantumDebugAgent
from quantum.openstack.common import cfg


class MyApp(object):
    def __init__(self, _stdout):
        self.stdout = _stdout


class TestDebugCommands(unittest.TestCase):
    def setUp(self):
        cfg.CONF.register_opts(interface.OPTS)
        cfg.CONF.register_opts(QuantumDebugAgent.OPTS)
        cfg.CONF(args=sys.argv, project='quantum')
        cfg.CONF.set_override('use_namespaces', True)
        cfg.CONF.root_helper = 'sudo'

        self.addCleanup(mock.patch.stopall)
        device_exists_p = mock.patch(
            'quantum.agent.linux.ip_lib.device_exists')
        device_exists_p.start()
        namespace_p = mock.patch(
            'quantum.agent.linux.ip_lib.IpNetnsCommand')
        namespace_p.start()
        ensure_namespace_p = mock.patch(
            'quantum.agent.linux.ip_lib.IPWrapper.ensure_namespace')
        ensure_namespace_p.start()
        dvr_cls_p = mock.patch('quantum.agent.linux.interface.NullDriver')
        driver_cls = dvr_cls_p.start()
        mock_driver = mock.MagicMock()
        mock_driver.DEV_NAME_LEN = (
            interface.LinuxInterfaceDriver.DEV_NAME_LEN)
        mock_driver.get_device_name.return_value = 'tap12345678-12'
        driver_cls.return_value = mock_driver
        self.driver = mock_driver

        client_cls_p = mock.patch('quantumclient.v2_0.client.Client')
        client_cls = client_cls_p.start()
        client_inst = mock.Mock()
        client_cls.return_value = client_inst

        fake_network = {'network': {'id': 'fake_net',
                                    'tenant_id': 'fake_tenant',
                                    'subnets': ['fake_subnet']}}
        fake_port = {'port':
                    {'id': 'fake_port',
                     'device_owner': 'fake_device',
                     'mac_address': 'aa:bb:cc:dd:ee:ffa',
                     'network_id': 'fake_net',
                     'fixed_ips':
                     [{'subnet_id': 'fake_subnet', 'ip_address':'10.0.0.3'}]
                     }}
        fake_ports = {'ports': [fake_port['port']]}
        self.fake_ports = fake_ports
        allocation_pools = [{'start': '10.0.0.2',
                             'end': '10.0.0.254'}]
        fake_subnet_v4 = {'subnet': {'name': 'fake_subnet_v4',
                          'id': 'fake_subnet',
                          'network_id': 'fake_net',
                          'gateway_ip': '10.0.0.1',
                          'dns_nameservers': ['10.0.0.2'],
                          'host_routes': [],
                          'cidr': '10.0.0.0/24',
                          'allocation_pools': allocation_pools,
                          'enable_dhcp': True,
                          'ip_version': 4}}

        client_inst.list_ports.return_value = fake_ports
        client_inst.create_port.return_value = fake_port
        client_inst.show_port.return_value = fake_port
        client_inst.show_network.return_value = fake_network
        client_inst.show_subnet.return_value = fake_subnet_v4
        self.client = client_inst
        mock_std = mock.Mock()
        self.app = MyApp(mock_std)
        self.app.debug_agent = QuantumDebugAgent(cfg.CONF,
                                                 client_inst,
                                                 mock_driver)

    def test_create_probe(self):
        cmd = commands.CreateProbe(self.app, None)
        cmd_parser = cmd.get_parser('create_probe')
        args = ['fake_net']
        parsed_args = cmd_parser.parse_args(args)
        cmd.run(parsed_args)
        fake_port = {'port':
                    {'device_owner': DEVICE_OWNER_PROBE,
                     'admin_state_up': True,
                     'network_id': 'fake_net',
                     'tenant_id': 'fake_tenant',
                     'fixed_ips': [{'subnet_id': 'fake_subnet'}],
                     'device_id': socket.gethostname()}}
        namespace = 'qprobe-fake_port'
        self.client.assert_has_calls([mock.call.show_network('fake_net'),
                                      mock.call.show_subnet('fake_subnet'),
                                      mock.call.create_port(fake_port),
                                      mock.call.show_subnet('fake_subnet')])
        self.driver.assert_has_calls([mock.call.init_l3('tap12345678-12',
                                                        ['10.0.0.3/24'],
                                                        namespace=namespace
                                                        )])

    def test_delete_probe(self):
        cmd = commands.DeleteProbe(self.app, None)
        cmd_parser = cmd.get_parser('delete_probe')
        args = ['fake_port']
        parsed_args = cmd_parser.parse_args(args)
        cmd.run(parsed_args)
        namespace = 'qprobe-fake_port'
        self.client.assert_has_calls([mock.call.show_port('fake_port'),
                                      mock.call.delete_port('fake_port')])
        self.driver.assert_has_calls([mock.call.get_device_name(mock.ANY),
                                      mock.call.unplug('tap12345678-12',
                                      namespace=namespace)])

    def test_delete_probe_without_namespace(self):
        cfg.CONF.set_override('use_namespaces', False)
        cmd = commands.DeleteProbe(self.app, None)
        cmd_parser = cmd.get_parser('delete_probe')
        args = ['fake_port']
        parsed_args = cmd_parser.parse_args(args)
        cmd.run(parsed_args)
        self.client.assert_has_calls([mock.call.show_port('fake_port'),
                                      mock.call.delete_port('fake_port')])
        self.driver.assert_has_calls([mock.call.get_device_name(mock.ANY),
                                      mock.call.unplug('tap12345678-12')])

    def test_list_probe(self):
        cmd = commands.ListProbe(self.app, None)
        cmd_parser = cmd.get_parser('list_probe')
        args = []
        parsed_args = cmd_parser.parse_args(args)
        cmd.run(parsed_args)
        self.client.assert_has_calls(
            [mock.call.list_ports(device_owner=DEVICE_OWNER_PROBE)])

    def test_exec_command(self):
        cmd = commands.ExecProbe(self.app, None)
        cmd_parser = cmd.get_parser('exec_command')
        args = ['fake_port', 'fake_command']
        parsed_args = cmd_parser.parse_args(args)
        with mock.patch('quantum.agent.linux.ip_lib.IpNetnsCommand') as ns:
            cmd.run(parsed_args)
            ns.assert_has_calls([mock.call.execute(mock.ANY)])
        self.client.assert_has_calls([mock.call.show_port('fake_port')])

    def test_exec_command_without_namespace(self):
        cfg.CONF.set_override('use_namespaces', False)
        cmd = commands.ExecProbe(self.app, None)
        cmd_parser = cmd.get_parser('exec_command')
        args = ['fake_port', 'fake_command']
        parsed_args = cmd_parser.parse_args(args)
        with mock.patch('quantum.agent.linux.utils.execute') as exe:
            cmd.run(parsed_args)
            exe.assert_has_calls([mock.call.execute(mock.ANY)])
        self.client.assert_has_calls([mock.call.show_port('fake_port')])

    def test_clear_probe(self):
        cmd = commands.ClearProbe(self.app, None)
        cmd_parser = cmd.get_parser('clear_probe')
        args = []
        parsed_args = cmd_parser.parse_args(args)
        cmd.run(parsed_args)
        namespace = 'qprobe-fake_port'
        self.client.assert_has_calls([mock.call.list_ports(
                                      device_id=socket.gethostname(),
                                      device_owner=DEVICE_OWNER_PROBE),
                                      mock.call.show_port('fake_port'),
                                      mock.call.delete_port('fake_port')])
        self.driver.assert_has_calls([mock.call.get_device_name(mock.ANY),
                                      mock.call.unplug('tap12345678-12',
                                                       namespace=namespace)])

    def test_ping_all_with_ensure_port(self):
        fake_ports = self.fake_ports

        def fake_port_list(network_id=None, device_owner=None, device_id=None):
            if network_id:
                # In order to test ensure_port, return []
                return {'ports': []}
            return fake_ports
        self.client.list_ports.side_effect = fake_port_list
        cmd = commands.PingAll(self.app, None)
        cmd_parser = cmd.get_parser('ping_all')
        args = []
        parsed_args = cmd_parser.parse_args(args)
        namespace = 'qprobe-fake_port'
        with mock.patch('quantum.agent.linux.ip_lib.IpNetnsCommand') as ns:
            cmd.run(parsed_args)
            ns.assert_has_calls([mock.call.execute(mock.ANY)])
        fake_port = {'port':
                    {'device_owner': DEVICE_OWNER_PROBE,
                     'admin_state_up': True,
                     'network_id': 'fake_net',
                     'tenant_id': 'fake_tenant',
                     'fixed_ips': [{'subnet_id': 'fake_subnet'}],
                     'device_id': socket.gethostname()}}
        expected = [mock.call.show_network('fake_net'),
                    mock.call.show_subnet('fake_subnet'),
                    mock.call.create_port(fake_port),
                    mock.call.show_subnet('fake_subnet')]
        self.client.assert_has_calls(expected)
        self.driver.assert_has_calls([mock.call.init_l3('tap12345678-12',
                                                        ['10.0.0.3/24'],
                                                        namespace=namespace
                                                        )])

    def test_ping_all(self):
        cmd = commands.PingAll(self.app, None)
        cmd_parser = cmd.get_parser('ping_all')
        args = []
        parsed_args = cmd_parser.parse_args(args)
        with mock.patch('quantum.agent.linux.ip_lib.IpNetnsCommand') as ns:
            cmd.run(parsed_args)
            ns.assert_has_calls([mock.call.execute(mock.ANY)])
        fake_port = {'port':
                    {'device_owner': DEVICE_OWNER_PROBE,
                     'admin_state_up': True,
                     'network_id': 'fake_net',
                     'tenant_id': 'fake_tenant',
                     'fixed_ips': [{'subnet_id': 'fake_subnet'}],
                     'device_id': socket.gethostname()}}
        expected = [mock.call.list_ports(),
                    mock.call.list_ports(network_id='fake_net',
                                         device_owner=DEVICE_OWNER_PROBE,
                                         device_id=socket.gethostname()),
                    mock.call.show_subnet('fake_subnet'),
                    mock.call.show_port('fake_port')]
        self.client.assert_has_calls(expected)

    def test_ping_all_v6(self):
        fake_subnet_v6 = {'subnet': {'name': 'fake_v6',
                          'ip_version': 6}}
        self.client.show_subnet.return_value = fake_subnet_v6
        cmd = commands.PingAll(self.app, None)
        cmd_parser = cmd.get_parser('ping_all')
        args = []
        parsed_args = cmd_parser.parse_args(args)
        with mock.patch('quantum.agent.linux.ip_lib.IpNetnsCommand') as ns:
            cmd.run(parsed_args)
            ns.assert_has_calls([mock.call.execute(mock.ANY)])
        self.client.assert_has_calls([mock.call.list_ports()])
