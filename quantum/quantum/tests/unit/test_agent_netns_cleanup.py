import mock
import unittest2 as unittest

from quantum.agent import netns_cleanup_util as util


class TestNetnsCleanup(unittest.TestCase):
    def test_setup_conf(self):
        conf = util.setup_conf()
        self.assertFalse(conf.force)

    def test_kill_dhcp(self, dhcp_active=True):
        conf = mock.Mock()
        conf.root_helper = 'sudo',
        conf.dhcp_driver = 'driver'

        method_to_patch = 'quantum.openstack.common.importutils.import_object'

        with mock.patch(method_to_patch) as import_object:
            driver = mock.Mock()
            driver.active = dhcp_active
            import_object.return_value = driver

            util.kill_dhcp(conf, 'ns')

            import_object.called_once_with('driver', conf, mock.ANY, 'sudo',
                                           mock.ANY)

            if dhcp_active:
                driver.assert_has_calls([mock.call.disable()])
            else:
                self.assertFalse(driver.called)

    def test_kill_dhcp_no_active(self):
        self.test_kill_dhcp(False)

    def test_eligible_for_deletion_ns_not_uuid(self):
        ns = 'not_a_uuid'
        self.assertFalse(util.eligible_for_deletion(mock.Mock(), ns))

    def _test_eligible_for_deletion_helper(self, prefix, force, is_empty,
                                           expected):
        ns = prefix + '6e322ac7-ab50-4f53-9cdc-d1d3c1164b6d'
        conf = mock.Mock()
        conf.root_helper = 'sudo'

        with mock.patch('quantum.agent.linux.ip_lib.IPWrapper') as ip_wrap:
            ip_wrap.return_value.namespace_is_empty.return_value = is_empty
            self.assertEqual(util.eligible_for_deletion(conf, ns, force),
                             expected)

            expected_calls = [mock.call('sudo', ns)]
            if not force:
                expected_calls.append(mock.call().namespace_is_empty())
            ip_wrap.assert_has_calls(expected_calls)

    def test_eligible_for_deletion_empty(self):
        self._test_eligible_for_deletion_helper('qrouter-', False, True, True)

    def test_eligible_for_deletion_not_empty(self):
        self._test_eligible_for_deletion_helper('qdhcp-', False, False, False)

    def test_eligible_for_deletion_not_empty_forced(self):
        self._test_eligible_for_deletion_helper('qdhcp-', True, False, True)

    def test_unplug_device_regular_device(self):
        conf = mock.Mock()
        device = mock.Mock()

        util.unplug_device(conf, device)
        device.assert_has_calls([mock.call.link.delete()])

    def test_unplug_device_ovs_port(self):
        conf = mock.Mock()
        conf.ovs_integration_bridge = 'br-int'
        conf.root_helper = 'sudo'

        device = mock.Mock()
        device.name = 'tap1'
        device.link.delete.side_effect = RuntimeError

        with mock.patch('quantum.agent.linux.ovs_lib.OVSBridge') as ovs_br_cls:
            br_patch = mock.patch(
                'quantum.agent.linux.ovs_lib.get_bridge_for_iface')
            with br_patch as mock_get_bridge_for_iface:
                mock_get_bridge_for_iface.return_value = 'br-int'
                ovs_bridge = mock.Mock()
                ovs_br_cls.return_value = ovs_bridge

                util.unplug_device(conf, device)

                mock_get_bridge_for_iface.assert_called_once_with(
                    conf.root_helper, 'tap1')
                ovs_br_cls.called_once_with('br-int', 'sudo')
                ovs_bridge.assert_has_calls(
                    [mock.call.delete_port(device.name)])

    def test_unplug_device_cannot_determine_bridge_port(self):
        conf = mock.Mock()
        conf.ovs_integration_bridge = 'br-int'
        conf.root_helper = 'sudo'

        device = mock.Mock()
        device.name = 'tap1'
        device.link.delete.side_effect = RuntimeError

        with mock.patch('quantum.agent.linux.ovs_lib.OVSBridge') as ovs_br_cls:
            br_patch = mock.patch(
                'quantum.agent.linux.ovs_lib.get_bridge_for_iface')
            with br_patch as mock_get_bridge_for_iface:
                with mock.patch.object(util.LOG, 'debug') as debug:
                    mock_get_bridge_for_iface.return_value = None
                    ovs_bridge = mock.Mock()
                    ovs_br_cls.return_value = ovs_bridge

                    util.unplug_device(conf, device)

                    mock_get_bridge_for_iface.assert_called_once_with(
                        conf.root_helper, 'tap1')
                    self.assertEquals(ovs_br_cls.mock_calls, [])
                    self.assertTrue(debug.called)

    def _test_destroy_namespace_helper(self, force, num_devices):
        ns = 'qrouter-6e322ac7-ab50-4f53-9cdc-d1d3c1164b6d'
        conf = mock.Mock()
        conf.root_helper = 'sudo'

        lo_device = mock.Mock()
        lo_device.name = 'lo'

        devices = [lo_device]

        while num_devices:
            dev = mock.Mock()
            dev.name = 'tap%d' % num_devices
            devices.append(dev)
            num_devices -= 1

        with mock.patch('quantum.agent.linux.ip_lib.IPWrapper') as ip_wrap:
            ip_wrap.return_value.get_devices.return_value = devices
            ip_wrap.return_value.netns.exists.return_value = True

            with mock.patch.object(util, 'unplug_device') as unplug:

                with mock.patch.object(util, 'kill_dhcp') as kill_dhcp:
                    util.destroy_namespace(conf, ns, force)
                    expected = [mock.call('sudo', ns)]

                    if force:
                        expected.extend([
                            mock.call().netns.exists(ns),
                            mock.call().get_devices(exclude_loopback=True)])
                        self.assertTrue(kill_dhcp.called)
                        unplug.assert_has_calls(
                            [mock.call(conf, d) for d in
                             devices[1:]])

                    expected.append(mock.call().garbage_collect_namespace())
                    ip_wrap.assert_has_calls(expected)

    def test_destory_namespace_empty(self):
        self._test_destroy_namespace_helper(False, 0)

    def test_destory_namespace_not_empty(self):
        self._test_destroy_namespace_helper(False, 1)

    def test_destory_namespace_not_empty_forced(self):
        self._test_destroy_namespace_helper(True, 2)

    def test_main(self):
        namespaces = ['ns1', 'ns2']
        with mock.patch('quantum.agent.linux.ip_lib.IPWrapper') as ip_wrap:
            ip_wrap.get_namespaces.return_value = namespaces

            with mock.patch('eventlet.sleep') as eventlet_sleep:
                conf = mock.Mock()
                conf.root_helper = 'sudo'
                conf.force = False
                methods_to_mock = dict(
                    eligible_for_deletion=mock.DEFAULT,
                    destroy_namespace=mock.DEFAULT,
                    setup_conf=mock.DEFAULT)

                with mock.patch.multiple(util, **methods_to_mock) as mocks:
                    mocks['eligible_for_deletion'].return_value = True
                    mocks['setup_conf'].return_value = conf
                    util.main()

                    mocks['eligible_for_deletion'].assert_has_calls(
                        [mock.call(conf, 'ns1', False),
                         mock.call(conf, 'ns2', False)])

                    mocks['destroy_namespace'].assert_has_calls(
                        [mock.call(conf, 'ns1', False),
                         mock.call(conf, 'ns2', False)])

                    ip_wrap.assert_has_calls(
                        [mock.call.get_namespaces('sudo')])

                    eventlet_sleep.assert_called_once_with(2)

    def test_main_no_candidates(self):
        namespaces = ['ns1', 'ns2']
        with mock.patch('quantum.agent.linux.ip_lib.IPWrapper') as ip_wrap:
            ip_wrap.get_namespaces.return_value = namespaces

            with mock.patch('eventlet.sleep') as eventlet_sleep:
                conf = mock.Mock()
                conf.root_helper = 'sudo'
                conf.force = False
                methods_to_mock = dict(
                    eligible_for_deletion=mock.DEFAULT,
                    destroy_namespace=mock.DEFAULT,
                    setup_conf=mock.DEFAULT)

                with mock.patch.multiple(util, **methods_to_mock) as mocks:
                    mocks['eligible_for_deletion'].return_value = False
                    mocks['setup_conf'].return_value = conf
                    util.main()

                    ip_wrap.assert_has_calls(
                        [mock.call.get_namespaces('sudo')])

                    mocks['eligible_for_deletion'].assert_has_calls(
                        [mock.call(conf, 'ns1', False),
                         mock.call(conf, 'ns2', False)])

                    self.assertFalse(mocks['destroy_namespace'].called)

                    self.assertFalse(eventlet_sleep.called)
