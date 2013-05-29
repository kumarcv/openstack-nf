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

import shlex

from quantum.openstack.common import cfg
from quantum.agent.common import config
from quantum.agent.linux import utils
from quantum.plugins.services.loadbalancer.drivers.haproxy.constants import (
    STATS_SOCKET_PATH)
from quantum.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class RemoteControl(object):
    """HAProxy remote control class

    This class is capable of managing HAProxy service
    on a haproxy VM and retrieving its config and stats.
    """

    def __init__(self, device_mgmt_info):
        LOG.debug(_('Instantiating RemoteControl for device %s'),
                  device_mgmt_info)
        self.address = device_mgmt_info['address']
        self.namespace = device_mgmt_info.get('namespace')
        self.ssh_options = ('-i %s -o StrictHostKeyChecking=no '
                            '-o UserKnownHostsFile=/dev/null'
                            % cfg.CONF.HAPROXY.haproxy_key_path)

    def perform(self, command, use_ssh=True, use_namespace=True):
        if use_ssh:
            command = ('ssh %(ssh_options)s root@%(address)s "%(cmd)s"'
                       % {'ssh_options': self.ssh_options,
                          'address': self.address,
                          'cmd': command})
        root_helper = None
        if use_namespace and self.namespace:
            command = 'ip netns exec %(ns)s %(cmd)s' % {'ns': self.namespace,
                                                        'cmd': command}
            root_helper = config.get_root_helper(cfg.CONF)

        try:
            stdout, stderr = utils.execute(shlex.split(command),
                                           root_helper=root_helper,
                                           return_stderr=True)
        except RuntimeError as e:
            LOG.error(_('Error while performing command: %s'), e)
            return False

        return True

    def get_file(self, remote_path, local_path):
        LOG.debug(_('Copying remote file %(remote)s to local %(local)s'),
                  {'remote': remote_path, 'local': local_path})
        cmd = ('scp %(ssh_options)s root@%(address)s:%(remote)s %(local)s'
               % {'ssh_options': self.ssh_options,
                  'address': self.address,
                  'remote': remote_path,
                  'local': local_path})
        if self.perform(cmd, use_ssh=False):
            return self.perform('sudo chmod 666 %s' % local_path,
                                use_ssh=False, use_namespace=False)
        else:
            return False

    def put_file(self, local_path, remote_path):
        LOG.debug(_('Copying local file %(local)s to remote %(remote)s'),
                  {'remote': remote_path, 'local': local_path})
        cmd = ('scp %(ssh_options)s %(local)s root@%(address)s:%(remote)s'
               % {'ssh_options': self.ssh_options,
                  'address': self.address,
                  'remote': remote_path,
                  'local': local_path})
        return self.perform(cmd, use_ssh=False)

    def validate_config(self, remote_path):
        command = 'haproxy -c -f {0}'.format(remote_path)
        if self.perform(command):
            LOG.debug(_('Remote configuration is valid: %s'), remote_path)
            return True
        else:
            LOG.error(_('Invalid configuration in %s'),
                      remote_path)
            return False

    def start_haproxy(self):
        LOG.debug(_('Starting service haproxy'))
        return self.perform('service haproxy start')

    def stop_haproxy(self):
        LOG.debug(_('Stopping service haproxy'))
        return self.perform('service haproxy stop')

    def restart_haproxy(self):
        LOG.debug(_('Restarting haproxy'))
        return self.perform('haproxy'
                            ' -f /etc/haproxy/haproxy.cfg'
                            ' -p /var/run/haproxy.pid'
                            ' -sf $(cat /var/run/haproxy.pid)')

    def _perform_unix_socket_command(self, command):
        return self.perform(
            'echo "%s" | socat stdio unix-connect:%s'
            % (command, STATS_SOCKET_PATH))

    def disable_server(self, backend, server):
        return self._perform_unix_socket_command('disable server %s/%s'
                                                 % (backend, server))

    def enable_server(self, backend, server):
        return self._perform_unix_socket_command('enable server %s/%s'
                                                 % (backend, server))

    def get_backend_stats(self, backend_id):
        cmd = 'show stat %s 2 -1' % backend_id
        return self._perform_unix_socket_command(cmd)

    def get_server_stats(self, backend_id, server_id):
        cmd = 'show stat %s 4 %s' % (backend_id, server_id)
        return self._perform_unix_socket_command(cmd)
