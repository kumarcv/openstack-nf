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

import eventlet

from quantum.openstack.common import cfg

from quantum.agent.common import config
from quantum.agent.services.driver_manager import ServiceDriverManager
from quantum.common import topics
from quantum.openstack.common import log as logging
from quantum.openstack.common import service
from quantum import service as quantum_service, manager
from quantum.plugins.services.loadbalancer import agent_rpc

LOG = logging.getLogger(__name__)

# TODO(shakhat) Currently API extension is implemented via mixin,
# to weaken dependencies this may be considered to be changed to
# dynamic extensions


class ServiceAgent(manager.Manager,
                   agent_rpc.LoadbalancerAgentCallbacks):
    __metaclass__ = type("MSA", (manager.Manager.__metaclass__,
                                 agent_rpc.LoadbalancerAgentCallbacks
                                 .__metaclass__), {})

    OPTS = [
        cfg.ListOpt('service_drivers', default=[],
                    help=_("Drivers for advanced services")),
        cfg.StrOpt('admin_user', help=_("Admin username")),
        cfg.StrOpt('admin_password', help=_("Admin password")),
        cfg.StrOpt('admin_tenant_name', help=_("Admin tenant name")),
        cfg.StrOpt('auth_url', help=_("Authentication URL")),
    ]

    def __init__(self, host, conf=None):
        self.conf = conf or cfg.CONF
        self.driver_manager = ServiceDriverManager.get_instance()
        super(ServiceAgent, self).__init__(host=host)

    def after_start(self):
        LOG.info(_('Service agent started'))


def main():
    eventlet.monkey_patch()

    conf = cfg.CONF
    config.register_root_helper(conf)
    conf.register_opts(ServiceAgent.OPTS)
    conf()
    config.setup_logging(conf)

    manager = 'quantum.agent.services.service_agent.ServiceAgent'
    server = quantum_service.Service.create(binary='quantum-svc-agent',
                                            topic=topics.SVC_AGENT,
                                            manager=manager)
    service.launch(server).wait()
