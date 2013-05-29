#!/usr/bin/env python
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

import logging
import sys
import socket
import time

import eventlet

from quantum.agent.linux import ovs_lib
from quantum.common import config as logging_config
from quantum.common import topics
from quantum.openstack.common import cfg
from quantum.openstack.common import context
from quantum.openstack.common import rpc
from quantum.openstack.common.rpc import dispatcher
from quantum.plugins.services.nwservices.agent import remote_control

logging.basicConfig()
LOG = logging.getLogger(__name__)



agent_opts = [
    cfg.IntOpt('polling_interval', default=2),
    cfg.IntOpt('reconnect_interval', default=2),
    cfg.StrOpt('root_helper', default='sudo'),
    cfg.BoolOpt('rpc', default=True),
    cfg.StrOpt('integration_bridge', default='br-int'),
]

relay_opts = [
    cfg.StrOpt('admin_user',default="quantum"),
    cfg.StrOpt('admin_password',default="password"),
    cfg.StrOpt('admin_tenant',default="service"),
    cfg.StrOpt('auth_url',default='http://10.232.90.53:5000/v2.0/'),
    cfg.StrOpt('endpoint_url',default='http://10.232.90.53:9696/'),
]

cfg.CONF.register_opts(relay_opts, "RELAY")
cfg.CONF.register_opts(agent_opts, "RAGENT")


class QuantumRelayAgent(object):
    '''
    '''

    # Set RPC API version to 1.0 by default.
    RPC_API_VERSION = '1.0'

    def __init__(self, integ_br, root_helper,
                 polling_interval, reconnect_interval, rpc):
        '''Constructor.

        :param root_helper: utility to use when running shell cmds.
        :param rpc: if True use RPC interface to interface with plugin.
        '''
        self.root_helper = root_helper
        self.polling_interval = polling_interval
        self.reconnect_interval = reconnect_interval
        self.setup_integration_br(integ_br)
        self.com = remote_control.RemoteControl()

        self.rpc = rpc
        if rpc:
            self.setup_rpc()

    def setup_rpc(self):
        self.host = get_hostname()
        self.topic = '%s.%s' % (topics.RELAY_AGENT,self.host)

        # RPC network init
        self.context = context.RequestContext('quantum', 'quantum',
                                              is_admin=False)
        # Handle updates from service
        self.dispatcher = self.create_rpc_dispatcher()
        # Define the listening consumers for the agent
        self.conn = rpc.create_connection(new=True)
        LOG.debug(_('connection is created......creating consumer with topic %s....\n'),self.topic)
        self.conn.create_consumer(self.topic,
                                   self.dispatcher,fanout=False)
        self.conn.consume_in_thread()

    def config_update(self,context,**kwargs):
        LOG.debug(_('Config Update Message received\n'))
        LOG.debug(_('msg received is %s\n'),str(kwargs))
        LOG.debug(_('context token id= %s*******************\n\n'),str(context.to_dict()))
        self.com.send_data_to_vm(kwargs.get('instance_id'),str(kwargs.get('config_request')))

    def create_rpc_dispatcher(self):
        '''Get the rpc dispatcher for this manager.

        If a manager would like to set an rpc API version, or support more than
        one class as the target of rpc messages, override this method.
        '''
        return dispatcher.RpcDispatcher([self])

    def setup_integration_br(self, integ_br):
        '''Setup the integration bridge.

        Create patch ports and remove all existing flows.

        :param integ_br: the name of the integration bridge.'''
        self.int_br = ovs_lib.OVSBridge(integ_br, self.root_helper)

    def update_ports(self, registered_ports):
        ports = self.int_br.get_vif_port_set()
        if ports == registered_ports:
            return
        added = ports - registered_ports
        removed = registered_ports - ports
        return {'current': ports,
                'added': added,
                'removed': removed}

    def rpc_loop(self):
        sync = True
        ports = set()
        tunnel_sync = True

        while True:
            try:
                start = time.time()
                if sync:
                    LOG.info("Agent out of sync with plugin!")
                    ports.clear()
                    sync = False

                port_info = self.update_ports(ports)

                # notify plugin about port deltas
                if port_info:
                    LOG.debug("Agent loop has new devices!")
                    # If treat devices fails - must resync with plugin
                    ports = port_info['current']

            except:
                LOG.exception("Error in agent event loop")
                sync = True

            # sleep till end of polling interval
            elapsed = (time.time() - start)
            if (elapsed < self.polling_interval):
                time.sleep(self.polling_interval - elapsed)
            else:
                LOG.debug("Loop iteration exceeded interval (%s vs. %s)!",
                          self.polling_interval, elapsed)

    def daemon_loop(self):
        if self.rpc:
            self.rpc_loop()

def get_hostname():
        return '%s' % socket.gethostname()

def main():
    eventlet.monkey_patch()
    cfg.CONF(args=sys.argv, project='quantum')

    # (TODO) gary - swap with common logging
    logging_config.setup_logging(cfg.CONF)

    LOG.debug("")
    root_helper = cfg.CONF.RAGENT.root_helper
    polling_interval = cfg.CONF.RAGENT.polling_interval
    reconnect_interval = cfg.CONF.RAGENT.reconnect_interval
    rpc = cfg.CONF.RAGENT.rpc
    integ_br = cfg.CONF.RAGENT.integration_bridge
    LOG.debug(_("username= %s,password=%s,auth_url=%s"),cfg.CONF.RELAY.admin_user,cfg.CONF.RELAY.admin_password,cfg.CONF.RELAY.auth_url)

    plugin = QuantumRelayAgent(integ_br,root_helper, polling_interval,
                             reconnect_interval, rpc)

    # Start everything.
    LOG.info("Agent initialized successfully, now running... ")
    plugin.daemon_loop()

    sys.exit(0)

if __name__ == "__main__":
    main()
