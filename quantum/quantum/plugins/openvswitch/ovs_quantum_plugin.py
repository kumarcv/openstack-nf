# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2011 Nicira Networks, Inc.
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
# @author: Somik Behera, Nicira Networks, Inc.
# @author: Brad Hall, Nicira Networks, Inc.
# @author: Dan Wendlandt, Nicira Networks, Inc.
# @author: Dave Lapsley, Nicira Networks, Inc.
# @author: Aaron Rosen, Nicira Networks, Inc.
# @author: Bob Kukura, Red Hat, Inc.

import logging
import os
import sys

from quantum.api.v2 import attributes
from quantum.common import constants as q_const
from quantum.common import exceptions as q_exc
from quantum.common import topics
from quantum.db import db_base_plugin_v2
from quantum.db import dhcp_rpc_base
from quantum.db import l3_db
from quantum.extensions import providernet as provider
from quantum.openstack.common import context
from quantum.openstack.common import cfg
from quantum.openstack.common import rpc
from quantum.openstack.common.rpc import dispatcher
from quantum.openstack.common.rpc import proxy
from quantum.plugins.openvswitch.common import config
from quantum.plugins.openvswitch.common import constants
from quantum.plugins.openvswitch import ovs_db_v2
from quantum import policy


LOG = logging.getLogger(__name__)


class OVSRpcCallbacks(dhcp_rpc_base.DhcpRpcCallbackMixin):

    # Set RPC API version to 1.0 by default.
    RPC_API_VERSION = '1.0'

    def __init__(self, rpc_context, notifier):
        self.rpc_context = rpc_context
        self.notifier = notifier

    def create_rpc_dispatcher(self):
        '''Get the rpc dispatcher for this manager.

        If a manager would like to set an rpc API version, or support more than
        one class as the target of rpc messages, override this method.
        '''
        return dispatcher.RpcDispatcher([self])

    def get_device_details(self, rpc_context, **kwargs):
        """Agent requests device details"""
        agent_id = kwargs.get('agent_id')
        device = kwargs.get('device')
        LOG.debug("Device %s details requested from %s", device, agent_id)
        port = ovs_db_v2.get_port(device)
        if port:
            binding = ovs_db_v2.get_network_binding(None, port['network_id'])
            entry = {'device': device,
                     'network_id': port['network_id'],
                     'port_id': port['id'],
                     'admin_state_up': port['admin_state_up'],
                     'network_type': binding.network_type,
                     'segmentation_id': binding.segmentation_id,
                     'physical_network': binding.physical_network}
            # Set the port status to UP
            ovs_db_v2.set_port_status(port['id'], q_const.PORT_STATUS_ACTIVE)
        else:
            entry = {'device': device}
            LOG.debug("%s can not be found in database", device)
        return entry

    def update_device_down(self, rpc_context, **kwargs):
        """Device no longer exists on agent"""
        # (TODO) garyk - live migration and port status
        agent_id = kwargs.get('agent_id')
        device = kwargs.get('device')
        LOG.debug("Device %s no longer exists on %s", device, agent_id)
        port = ovs_db_v2.get_port(device)
        if port:
            entry = {'device': device,
                     'exists': True}
            # Set port status to DOWN
            ovs_db_v2.set_port_status(port['id'], q_const.PORT_STATUS_DOWN)
        else:
            entry = {'device': device,
                     'exists': False}
            LOG.debug("%s can not be found in database", device)
        return entry

    def tunnel_sync(self, rpc_context, **kwargs):
        """Update new tunnel.

        Updates the datbase with the tunnel IP. All listening agents will also
        be notified about the new tunnel IP.
        """
        tunnel_ip = kwargs.get('tunnel_ip')
        # Update the database with the IP
        tunnel = ovs_db_v2.add_tunnel_endpoint(tunnel_ip)
        tunnels = ovs_db_v2.get_tunnel_endpoints()
        entry = dict()
        entry['tunnels'] = tunnels
        # Notify all other listening agents
        self.notifier.tunnel_update(self.rpc_context, tunnel.ip_address,
                                    tunnel.id)
        # Return the list of tunnels IP's to the agent
        return entry


class AgentNotifierApi(proxy.RpcProxy):
    '''Agent side of the linux bridge rpc API.

    API version history:
        1.0 - Initial version.

    '''

    BASE_RPC_API_VERSION = '1.0'

    def __init__(self, topic):
        super(AgentNotifierApi, self).__init__(
            topic=topic, default_version=self.BASE_RPC_API_VERSION)
        self.topic_network_delete = topics.get_topic_name(topic,
                                                          topics.NETWORK,
                                                          topics.DELETE)
        self.topic_port_update = topics.get_topic_name(topic,
                                                       topics.PORT,
                                                       topics.UPDATE)
        self.topic_tunnel_update = topics.get_topic_name(topic,
                                                         constants.TUNNEL,
                                                         topics.UPDATE)

    def network_delete(self, context, network_id):
        self.fanout_cast(context,
                         self.make_msg('network_delete',
                                       network_id=network_id),
                         topic=self.topic_network_delete)

    def port_update(self, context, port, network_type, segmentation_id,
                    physical_network):
        self.fanout_cast(context,
                         self.make_msg('port_update',
                                       port=port,
                                       network_type=network_type,
                                       segmentation_id=segmentation_id,
                                       physical_network=physical_network),
                         topic=self.topic_port_update)

    def tunnel_update(self, context, tunnel_ip, tunnel_id):
        self.fanout_cast(context,
                         self.make_msg('tunnel_update',
                                       tunnel_ip=tunnel_ip,
                                       tunnel_id=tunnel_id),
                         topic=self.topic_tunnel_update)


class OVSQuantumPluginV2(db_base_plugin_v2.QuantumDbPluginV2,
                         l3_db.L3_NAT_db_mixin):
    """Implement the Quantum abstractions using Open vSwitch.

    Depending on whether tunneling is enabled, either a GRE tunnel or
    a new VLAN is created for each network. An agent is relied upon to
    perform the actual OVS configuration on each host.

    The provider extension is also supported. As discussed in
    https://bugs.launchpad.net/quantum/+bug/1023156, this class could
    be simplified, and filtering on extended attributes could be
    handled, by adding support for extended attributes to the
    QuantumDbPluginV2 base class. When that occurs, this class should
    be updated to take advantage of it.
    """

    # This attribute specifies whether the plugin supports or not
    # bulk operations. Name mangling is used in order to ensure it
    # is qualified by class
    __native_bulk_support = True
    supported_extension_aliases = ["provider", "router"]

    def __init__(self, configfile=None):
        ovs_db_v2.initialize()
        self._parse_network_vlan_ranges()
        ovs_db_v2.sync_vlan_allocations(self.network_vlan_ranges)
        self.tenant_network_type = cfg.CONF.OVS.tenant_network_type
        if self.tenant_network_type not in [constants.TYPE_LOCAL,
                                            constants.TYPE_VLAN,
                                            constants.TYPE_GRE,
                                            constants.TYPE_NONE]:
            LOG.error("Invalid tenant_network_type: %s. "
                      "Agent terminated!",
                      self.tenant_network_type)
            sys.exit(1)
        self.enable_tunneling = cfg.CONF.OVS.enable_tunneling
        self.tunnel_id_ranges = []
        if self.enable_tunneling:
            self._parse_tunnel_id_ranges()
            ovs_db_v2.sync_tunnel_allocations(self.tunnel_id_ranges)
        elif self.tenant_network_type == constants.TYPE_GRE:
            LOG.error("Tunneling disabled but tenant_network_type is 'gre'. "
                      "Agent terminated!")
            sys.exit(1)
        self.agent_rpc = cfg.CONF.AGENT.rpc
        self.setup_rpc()

    def setup_rpc(self):
        # RPC support
        self.topic = topics.PLUGIN
        self.rpc_context = context.RequestContext('quantum', 'quantum',
                                                  is_admin=False)
        self.conn = rpc.create_connection(new=True)
        self.notifier = AgentNotifierApi(topics.AGENT)
        self.callbacks = OVSRpcCallbacks(self.rpc_context, self.notifier)
        self.dispatcher = self.callbacks.create_rpc_dispatcher()
        self.conn.create_consumer(self.topic, self.dispatcher,
                                  fanout=False)
        # Consume from all consumers in a thread
        self.conn.consume_in_thread()

    def _parse_network_vlan_ranges(self):
        self.network_vlan_ranges = {}
        for entry in cfg.CONF.OVS.network_vlan_ranges:
            entry = entry.strip()
            if ':' in entry:
                try:
                    physical_network, vlan_min, vlan_max = entry.split(':')
                    self._add_network_vlan_range(physical_network.strip(),
                                                 int(vlan_min),
                                                 int(vlan_max))
                except ValueError as ex:
                    LOG.error("Invalid network VLAN range: '%s' - %s. "
                              "Agent terminated!",
                              entry, ex)
                    sys.exit(1)
            else:
                self._add_network(entry)
        LOG.info("Network VLAN ranges: %s", self.network_vlan_ranges)

    def _add_network_vlan_range(self, physical_network, vlan_min, vlan_max):
        self._add_network(physical_network)
        self.network_vlan_ranges[physical_network].append((vlan_min, vlan_max))

    def _add_network(self, physical_network):
        if physical_network not in self.network_vlan_ranges:
            self.network_vlan_ranges[physical_network] = []

    def _parse_tunnel_id_ranges(self):
        for entry in cfg.CONF.OVS.tunnel_id_ranges:
            entry = entry.strip()
            try:
                tun_min, tun_max = entry.split(':')
                self.tunnel_id_ranges.append((int(tun_min), int(tun_max)))
            except ValueError as ex:
                LOG.error("Invalid tunnel ID range: '%s' - %s. "
                          "Agent terminated!", entry, ex)
                sys.exit(1)
        LOG.info("Tunnel ID ranges: %s", self.tunnel_id_ranges)

    # TODO(rkukura) Use core mechanism for attribute authorization
    # when available.

    def _check_provider_view_auth(self, context, network):
        return policy.check(context,
                            "extension:provider_network:view",
                            network)

    def _enforce_provider_set_auth(self, context, network):
        return policy.enforce(context,
                              "extension:provider_network:set",
                              network)

    def _extend_network_dict_provider(self, context, network):
        if self._check_provider_view_auth(context, network):
            binding = ovs_db_v2.get_network_binding(context.session,
                                                    network['id'])
            network[provider.NETWORK_TYPE] = binding.network_type
            if binding.network_type == constants.TYPE_GRE:
                network[provider.PHYSICAL_NETWORK] = None
                network[provider.SEGMENTATION_ID] = binding.segmentation_id
            elif binding.network_type == constants.TYPE_FLAT:
                network[provider.PHYSICAL_NETWORK] = binding.physical_network
                network[provider.SEGMENTATION_ID] = None
            elif binding.network_type == constants.TYPE_VLAN:
                network[provider.PHYSICAL_NETWORK] = binding.physical_network
                network[provider.SEGMENTATION_ID] = binding.segmentation_id
            elif binding.network_type == constants.TYPE_LOCAL:
                network[provider.PHYSICAL_NETWORK] = None
                network[provider.SEGMENTATION_ID] = None

    def _process_provider_create(self, context, attrs):
        network_type = attrs.get(provider.NETWORK_TYPE)
        physical_network = attrs.get(provider.PHYSICAL_NETWORK)
        segmentation_id = attrs.get(provider.SEGMENTATION_ID)

        network_type_set = attributes.is_attr_set(network_type)
        physical_network_set = attributes.is_attr_set(physical_network)
        segmentation_id_set = attributes.is_attr_set(segmentation_id)

        if not (network_type_set or physical_network_set or
                segmentation_id_set):
            return (None, None, None)

        # Authorize before exposing plugin details to client
        self._enforce_provider_set_auth(context, attrs)

        if not network_type_set:
            msg = _("provider:network_type required")
            raise q_exc.InvalidInput(error_message=msg)
        elif network_type == constants.TYPE_FLAT:
            if segmentation_id_set:
                msg = _("provider:segmentation_id specified for flat network")
                raise q_exc.InvalidInput(error_message=msg)
            else:
                segmentation_id = constants.FLAT_VLAN_ID
        elif network_type == constants.TYPE_VLAN:
            if not segmentation_id_set:
                msg = _("provider:segmentation_id required")
                raise q_exc.InvalidInput(error_message=msg)
            if segmentation_id < 1 or segmentation_id > 4094:
                msg = _("provider:segmentation_id out of range "
                        "(1 through 4094)")
                raise q_exc.InvalidInput(error_message=msg)
        elif network_type == constants.TYPE_GRE:
            if not self.enable_tunneling:
                msg = _("GRE networks are not enabled")
                raise q_exc.InvalidInput(error_message=msg)
            if physical_network_set:
                msg = _("provider:physical_network specified for GRE "
                        "network")
                raise q_exc.InvalidInput(error_message=msg)
            else:
                physical_network = None
            if not segmentation_id_set:
                msg = _("provider:segmentation_id required")
                raise q_exc.InvalidInput(error_message=msg)
        elif network_type == constants.TYPE_LOCAL:
            if physical_network_set:
                msg = _("provider:physical_network specified for local "
                        "network")
                raise q_exc.InvalidInput(error_message=msg)
            else:
                physical_network = None
            if segmentation_id_set:
                msg = _("provider:segmentation_id specified for local "
                        "network")
                raise q_exc.InvalidInput(error_message=msg)
            else:
                segmentation_id = None
        else:
            msg = _("provider:network_type %s not supported" % network_type)
            raise q_exc.InvalidInput(error_message=msg)

        if network_type in [constants.TYPE_VLAN, constants.TYPE_FLAT]:
            if physical_network_set:
                if physical_network not in self.network_vlan_ranges:
                    msg = _("unknown provider:physical_network %s" %
                            physical_network)
                    raise q_exc.InvalidInput(error_message=msg)
            elif 'default' in self.network_vlan_ranges:
                physical_network = 'default'
            else:
                msg = _("provider:physical_network required")
                raise q_exc.InvalidInput(error_message=msg)

        return (network_type, physical_network, segmentation_id)

    def _check_provider_update(self, context, attrs):
        network_type = attrs.get(provider.NETWORK_TYPE)
        physical_network = attrs.get(provider.PHYSICAL_NETWORK)
        segmentation_id = attrs.get(provider.SEGMENTATION_ID)

        network_type_set = attributes.is_attr_set(network_type)
        physical_network_set = attributes.is_attr_set(physical_network)
        segmentation_id_set = attributes.is_attr_set(segmentation_id)

        if not (network_type_set or physical_network_set or
                segmentation_id_set):
            return

        # Authorize before exposing plugin details to client
        self._enforce_provider_set_auth(context, attrs)

        msg = _("plugin does not support updating provider attributes")
        raise q_exc.InvalidInput(error_message=msg)

    def create_network(self, context, network):
        (network_type, physical_network,
         segmentation_id) = self._process_provider_create(context,
                                                          network['network'])

        session = context.session
        with session.begin(subtransactions=True):
            if not network_type:
                # tenant network
                network_type = self.tenant_network_type
                if network_type == constants.TYPE_NONE:
                    raise q_exc.TenantNetworksDisabled()
                elif network_type == constants.TYPE_VLAN:
                    (physical_network,
                     segmentation_id) = ovs_db_v2.reserve_vlan(session)
                elif network_type == constants.TYPE_GRE:
                    segmentation_id = ovs_db_v2.reserve_tunnel(session)
                # no reservation needed for TYPE_LOCAL
            else:
                # provider network
                if network_type in [constants.TYPE_VLAN, constants.TYPE_FLAT]:
                    ovs_db_v2.reserve_specific_vlan(session, physical_network,
                                                    segmentation_id)
                elif network_type == constants.TYPE_GRE:
                    ovs_db_v2.reserve_specific_tunnel(session, segmentation_id)
                # no reservation needed for TYPE_LOCAL
            net = super(OVSQuantumPluginV2, self).create_network(context,
                                                                 network)
            ovs_db_v2.add_network_binding(session, net['id'], network_type,
                                          physical_network, segmentation_id)

            self._process_l3_create(context, network['network'], net['id'])
            self._extend_network_dict_provider(context, net)
            self._extend_network_dict_l3(context, net)
            # note - exception will rollback entire transaction
        LOG.debug("Created network: %s", net['id'])
        return net

    def update_network(self, context, id, network):
        self._check_provider_update(context, network['network'])

        session = context.session
        with session.begin(subtransactions=True):
            net = super(OVSQuantumPluginV2, self).update_network(context, id,
                                                                 network)
            self._process_l3_update(context, network['network'], id)
            self._extend_network_dict_provider(context, net)
            self._extend_network_dict_l3(context, net)
        return net

    def delete_network(self, context, id):
        session = context.session
        with session.begin(subtransactions=True):
            binding = ovs_db_v2.get_network_binding(session, id)
            super(OVSQuantumPluginV2, self).delete_network(context, id)
            if binding.network_type == constants.TYPE_GRE:
                ovs_db_v2.release_tunnel(session, binding.segmentation_id,
                                         self.tunnel_id_ranges)
            elif binding.network_type in [constants.TYPE_VLAN,
                                          constants.TYPE_FLAT]:
                ovs_db_v2.release_vlan(session, binding.physical_network,
                                       binding.segmentation_id,
                                       self.network_vlan_ranges)
            # the network_binding record is deleted via cascade from
            # the network record, so explicit removal is not necessary
        if self.agent_rpc:
            self.notifier.network_delete(self.rpc_context, id)

    def get_network(self, context, id, fields=None):
        session = context.session
        with session.begin(subtransactions=True):
            net = super(OVSQuantumPluginV2, self).get_network(context,
                                                              id, None)
            self._extend_network_dict_provider(context, net)
            self._extend_network_dict_l3(context, net)
        return self._fields(net, fields)

    def get_networks(self, context, filters=None, fields=None):
        session = context.session
        with session.begin(subtransactions=True):
            nets = super(OVSQuantumPluginV2, self).get_networks(context,
                                                                filters,
                                                                None)
            for net in nets:
                self._extend_network_dict_provider(context, net)
                self._extend_network_dict_l3(context, net)

            # TODO(rkukura): Filter on extended provider attributes.
            nets = self._filter_nets_l3(context, nets, filters)

        return [self._fields(net, fields) for net in nets]

    def update_port(self, context, id, port):
        if self.agent_rpc:
            original_port = super(OVSQuantumPluginV2, self).get_port(context,
                                                                     id)
        port = super(OVSQuantumPluginV2, self).update_port(context, id, port)
        if self.agent_rpc:
            if original_port['admin_state_up'] != port['admin_state_up']:
                binding = ovs_db_v2.get_network_binding(None,
                                                        port['network_id'])
                self.notifier.port_update(self.rpc_context, port,
                                          binding.network_type,
                                          binding.segmentation_id,
                                          binding.physical_network)
        return port

    def delete_port(self, context, id, l3_port_check=True):

        # if needed, check to see if this is a port owned by
        # and l3-router.  If so, we should prevent deletion.
        if l3_port_check:
            self.prevent_l3_port_deletion(context, id)
        self.disassociate_floatingips(context, id)
        return super(OVSQuantumPluginV2, self).delete_port(context, id)
