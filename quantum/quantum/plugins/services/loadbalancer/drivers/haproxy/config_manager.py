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

import re
import tempfile

from quantum.plugins.services.loadbalancer.drivers import constants
from quantum.plugins.services.loadbalancer.drivers import exceptions
from quantum.plugins.services.loadbalancer.drivers.haproxy import (
    remote_control)
from quantum.plugins.services.loadbalancer.drivers.haproxy.constants import (
    STATS_SOCKET_PATH)
from quantum.openstack.common import log as logging

LOG = logging.getLogger(__name__)


def validate_backend(method):
    """Validates that given backend exists in the config"""
    def wrapper(*args, **kwargs):
        if 'backend' in kwargs:
            backend = kwargs['backend']
        else:
            backend = args[1]
        if not backend.name in args[0].config['backends']:
            msg = _('No such pool: %s') % (backend.name,)
            LOG.error(msg)
            raise exceptions.ConfigError(msg=msg)
        return method(*args, **kwargs)
    return wrapper


class ConfigManager(object):
    """HAProxy configuration manager

    This class understands HAProxy config file format.
    It's able to get and parse it, append/delete/update config blocks,
    deploy config on the device.

    It operates with HAProxy config objects defined in ./config_models.py
    """

    remote_config_path = '/etc/haproxy/haproxy.cfg'

    def __init__(self, device):
        self.config = {}
        self.remote_control = remote_control.RemoteControl(
            device['management'])
        self.local_config_path = tempfile.mktemp()

    def __enter__(self):
        self._parse(self._fetch_config())
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            self._deploy_config(self._get_raw_config())

    def _fetch_config(self):
        LOG.debug(_('Fetching configuration from %s'),
                  self.remote_config_path)

        if not self.remote_control.get_file(self.remote_config_path,
                                            self.local_config_path):
            msg = _('Could not fetch configuration from the device')
            LOG.error(msg)
            raise exceptions.ConfigError(msg=msg)

        with open(self.local_config_path, 'r') as f:
            return [line.rstrip() for line in f]

    def _deploy_config(self, raw_config):
        LOG.debug(_('writing configuration to %s'), self.local_config_path)
        with open(self.local_config_path, 'w') as f:
            f.writelines([line + '\n' for line in raw_config])

        LOG.debug(_('Deploying configuration'))
        tmp_path = '/tmp/haproxy.cfg.remote'
        if not self.remote_control.put_file(self.local_config_path, tmp_path):
            msg = _('Could not put configuration on the device')
            LOG.error(msg)
            raise exceptions.ConfigError(msg=msg)

        if self.remote_control.validate_config(tmp_path):
            self.remote_control.perform('sudo mv %s %s' %
                                        (tmp_path, self.remote_config_path))
            if not self.remote_control.restart_haproxy():
                msg = _('Failed to restart HAProxy')
                LOG.error(msg)
        else:
            msg = _('HAProxy config file is invalid')
            LOG.error(msg)
            raise exceptions.ConfigError(msg=msg)

    def _parse(self, raw_config):
        self.config = {}
        cur_block = None
        for line in raw_config:
            line = line.strip()

            if line == '':
                continue

            for block_name in ['global', 'defaults', 'listen', 'frontend',
                               'backend']:
                if line.startswith(block_name):
                    cur_block = self.config[line] = []
                    break
            else:
                if cur_block is None:
                    cur_block = self.config['comments'] = [line]
                else:
                    cur_block.append('\t' + line)

        self._structure_backends()
        self._ensure_stats_socket()

    def _structure_backends(self):
        """Improves backends structure to simplify further configuring"""
        self.config['backends'] = {}
        for block in self.config.keys():
            if block.startswith('backend '):
                block_name = block.split()[1]

                backend = {'servers': [],
                           'default-server': '',
                           'options': []}
                for line in self.config[block]:
                    if line.startswith('\tserver'):
                        backend['servers'].append(line)
                    elif line.startswith('\tdefault-server'):
                        backend['default-server'] = line
                    else:
                        backend['options'].append(line)
                del self.config[block]
                self.config['backends'][block_name] = backend

    def _ensure_stats_socket(self):
        """Ensures that stats socket is created under certain path"""
        stats_socket = ('\tstats socket %s user root level admin'
                        % STATS_SOCKET_PATH)
        for line in self.config['global']:
            if line.startswith('\tstats socket'):
                index = self.config['global'].index(line)
                self.config['global'].remove(line)
                self.config['global'].insert(index, stats_socket)
                break
        else:
            self.config['global'].append(stats_socket)

    def _get_raw_config(self):
        result = []

        for line in self.config.get('comments', []):
            result.append(line)

        for block in ['global', 'defaults']:
            result.append(block)
            for line in (self.config.get(block, [])):
                result.append(line)

        for block in sorted(self.config):
            if block.startswith('frontend') or block.startswith('listen'):
                result.append(block)
                for line in sorted(self.config[block]):
                    result.append(line)

        for backend_name in self.config['backends']:
            result.append('backend %s' % backend_name)
            backend = self.config['backends'][backend_name]
            for option in backend['options']:
                result.append(option)
            # if there is any info in default-server section
            if backend['default-server'].strip() != 'default-server':
                result.append(backend['default-server'])
            for server in backend['servers']:
                result.append(server)

        return result

    def add_frontend(self, frontend):
        LOG.debug(_('Adding frontend %s'), frontend.name)
        frontend_lines = ['\tid %s' % frontend.id,
                          '\tbind %s:%s' % (frontend.bind_address,
                                            frontend.bind_port),
                          '\tmode %s' % frontend.mode,
                          '\tdefault_backend %s' % frontend.default_backend,
                          '\t%s' % ('enabled' if frontend.enabled
                          else 'disabled')]
        self.config['frontend %s' % frontend.name] = frontend_lines

    def add_backend(self, backend):
        LOG.debug(_('Adding backend %s'), backend.name)
        if backend.name in self.config['backends']:
            msg = _('Pool %s already exists') % (backend.name,)
            LOG.error(msg)
            raise exceptions.ConfigError(msg=msg)
        self.config['backends'][backend.name] = {}

        options = self._get_backend_common_options(backend)
        self.config['backends'][backend.name]['options'] = options
        self.config['backends'][backend.name]['servers'] = []
        self.config['backends'][backend.name]['default-server'] = ''

    @validate_backend
    def _get_backend_common_options(self, backend):
        return ['\tid %s' % backend.id,
                '\tbalance %s' % backend.balance,
                '\tmode %s' % backend.mode,
                '\t%s' % ('enabled' if backend.enabled else 'disabled')]

    @validate_backend
    def update_backend(self, backend, new_backend):
        old_options = self.config['backends'][backend.name]['options']
        new_options = self._get_backend_common_options(new_backend)
        for option in old_options:
            if not self._is_common_backend_option(option):
                new_options.append(option)
        self.config['backends'][backend.name]['options'] = new_options

    def _is_common_backend_option(self, option):
        if (re.match(r'\s+id\s+\w+', option) or
            re.match(r'\s+balance\s+\w+', option) or
            re.match(r'\s+mode\s+\w+', option) or
            re.match(r'\s+enabled', option) or
            re.match(r'\s+disabled', option)):
            return True

    @validate_backend
    def add_server(self, backend, server):
        LOG.debug(_('Adding server %(server)s to backend %(backend)s'),
                  {'server': server.name, 'backend': backend.name})
        server_line = ('\tserver {0} {1}:{2} id {3} weight {4}'
                       .format(server.name, server.address,
                               server.port, server.id,
                               server.weight))
        if self.has_health_monitors(backend):
            server_line += ' check'
        if self._has_http_cookie_persistence(backend):
            server_line += ' cookie %s' % server.id
        if not server.enabled:
            server_line += ' disabled'
        self.config['backends'][backend.name]['servers'].append(server_line)

    @validate_backend
    def delete_server(self, backend, server):
        LOG.debug(_('Deleting server %(server)s from backend %(backend)s'),
                  {'server': server.name, 'backend': backend.name})
        servers = self.config['backends'][backend.name]['servers']
        for srv in servers:
            if re.match(r'\s*server\s+%s' % server.name, srv):
                servers.remove(srv)
                break
        else:
            msg = (_('Member %(member)s not found in pool %(pool)s') %
                   {'member': server.name, 'pool': backend.name})
            LOG.error(msg)
            raise exceptions.ConfigError(msg=msg)

    def delete_block(self, block):
        LOG.debug(_('Deleting block %s'), block.name)
        if block.type == 'backend' and block.name in self.config['backends']:
            del self.config['backends'][block.name]
        else:
            for key in self.config.keys():
                if re.match(r'%s\s+%s' % (block.type, block.name), key):
                    del self.config[key]
                    break
            else:
                msg = (_('No such %(type)s: %(name)s') %
                       {'type': block.type, 'name': block.name})
                LOG.error(msg)
                raise exceptions.ConfigError(msg=msg)

    @validate_backend
    def add_probe(self, backend, probe):
        if not probe.enabled:
            return

        LOG.debug(_('Adding %(probe)s probe to backend %(backend)s'),
                  {'probe': probe.type, 'backend': backend.name})
        if self.has_health_monitors(backend):
            msg = _('Can associate only one health monitor '
                    'with a HAProxy pool')
            LOG.error(msg)
            raise exceptions.ConfigError(msg=msg)
        # needed for any health_monitor
        self._add_server_checks(backend.name, probe.inter, probe.fall)

        options = self.config['backends'][backend.name]['options']
        options.append('\ttimeout connect %d' % probe.timeout)

        if (probe.probe_type == constants.HEALTH_MONITOR_HTTP or
            probe.probe_type == constants.HEALTH_MONITOR_HTTPS):
            http_check = '\toption httpchk %(method)s %(uri)s' % (
                {'method': probe.method, 'uri': probe.uri})
            options.append(http_check)
            http_expect = ('\thttp-check expect rstatus %s'
                           % self._expected_codes_to_regexp(probe.expect))
            options.append(http_expect)

        # adding HTTPS check as a combination of http (above) and ssl checks
        if probe.probe_type == constants.HEALTH_MONITOR_HTTPS:
            options.append('\toption ssl-hello-chk')

    @validate_backend
    def delete_probe(self, backend):
        """ Deletes all checks from servers and backend
            since HAProxy allows only one health monitor per pool
        """
        LOG.debug(_('Deleting health probe from backend %s'), backend.name)
        self._delete_server_checks(backend.name)

        no_checks_options = []
        for option in self.config['backends'][backend.name]['options']:
            if not ('timeout connect' in option or
                    'httpchk' in option or
                    'ssl-hello-chk' in option or
                    'http-check' in option):
                no_checks_options.append(option)
        self.config['backends'][backend.name]['options'] = no_checks_options

    @validate_backend
    def has_health_monitors(self, backend):
        for server in self.config['backends'][backend.name]['servers']:
            if re.search(r'\scheck\b', server):
                return True
        for option in self.config['backends'][backend.name]['options']:
            if ('httpchk' in option or
                'ssl-hello-chk' in option or
                'http-check' in option):
                return True

    @validate_backend
    def add_persistence(self, backend, persistence):
        LOG.debug(_('Adding %(persist)s session persistence'
                    ' to backend %(backend)s'),
                  {'persist': persistence, 'backend': backend.name})
        persist_type = persistence.get('type')
        if persist_type:
            options = self.config['backends'][backend.name]['options']
            if persist_type == constants.SESSION_PERSISTENCE_SOURCE_IP:
                options.append('\tstick-table type ip size 200k expire 30m')
                options.append('\tstick on src')
            elif persist_type == constants.SESSION_PERSISTENCE_HTTP_COOKIE:
                options.append('\tcookie SRV insert indirect nocache')
                self._add_server_cookies(backend.name)
            elif persist_type == constants.SESSION_PERSISTENCE_APP_COOKIE:
                options.append('\tappsession %s len 56 timeout 3h'
                               % persistence['cookie_name'])

    @validate_backend
    def delete_persistence(self, backend):
        LOG.debug(_('Deleting session persistence from backend %s'),
                  backend.name)
        self._delete_server_cookies(backend.name)

        no_stick_options = []
        for option in self.config['backends'][backend.name]['options']:
            if not ('stick' in option or
                    'cookie' in option or
                    'appsession' in option):
                no_stick_options.append(option)
        self.config['backends'][backend.name]['options'] = no_stick_options

    @validate_backend
    def _has_http_cookie_persistence(self, backend):
        for option in self.config['backends'][backend.name]['options']:
            if re.match(r'\s+cookie\s+\w+', option):
                return True

    def _add_server_checks(self, backend_name, inter, fall):
        if backend_name in self.config['backends']:
            backend_cfg = self.config['backends'][backend_name]

            if re.search(r'\s+inter\s+\d+', backend_cfg['default-server']):
                backend_cfg['default-server'] = re.sub(
                    r'\s+inter\s+\d+',
                    ' inter %d' % inter,
                    backend_cfg['default-server'])
            else:
                backend_cfg['default-server'] += ' inter %d' % inter
            if re.search(r'\s+fall\s+\d+', backend_cfg['default-server']):
                backend_cfg['default-server'] = re.sub(
                    r'\s+fall\s+\d+',
                    ' fall %d' % fall,
                    backend_cfg['default-server'])
            else:
                backend_cfg['default-server'] += ' fall %d' % fall

            for server in backend_cfg['servers']:
                if not re.search(r'\scheck\b', server):
                    index = backend_cfg['servers'].index(server)
                    backend_cfg['servers'].remove(server)
                    server += ' check'
                    backend_cfg['servers'].insert(index, server)

    def _delete_server_checks(self, backend_name):
        if backend_name in self.config['backends']:
            backend_cfg = self.config['backends'][backend_name]
            backend_cfg['default-server'] = re.sub(
                r'\s+inter\s+\d+', '', backend_cfg['default-server'])
            backend_cfg['default-server'] = re.sub(
                r'\s+fall\s+\d+', '', backend_cfg['default-server'])

            for server in backend_cfg['servers']:
                index = backend_cfg['servers'].index(server)
                backend_cfg['servers'].remove(server)
                server = re.sub(r'\scheck\b', '', server)
                backend_cfg['servers'].insert(index, server)

    def _add_server_cookies(self, backend_name):
        if backend_name in self.config['backends']:
            backend_cfg = self.config['backends'][backend_name]
            for server in backend_cfg['servers']:
                if not re.search(r'\scookie\s+\w+', server):
                    index = backend_cfg['servers'].index(server)
                    backend_cfg['servers'].remove(server)
                    server_id = re.search(r'\s+id\s+(\d+)',
                                          server).groups()[0]
                    server += ' cookie %s' % server_id
                    backend_cfg['servers'].insert(index, server)

    def _delete_server_cookies(self, backend_name):
        if backend_name in self.config['backends']:
            backend_cfg = self.config['backends'][backend_name]
            for server in backend_cfg['servers']:
                index = backend_cfg['servers'].index(server)
                backend_cfg['servers'].remove(server)
                server = re.sub(r'\scookie\s+\w+', '', server)
                backend_cfg['servers'].insert(index, server)

    def _expected_codes_to_regexp(self, exp_codes):
        """ Translates expected codes of the form '200, 202-210, 300...'
            to a simple regexp like: '200|202|203|204...'
        """
        # TODO: improve to make result regexp shorter
        regexp = ''
        for part in [part.strip() for part in exp_codes.split(',')]:
            rng = part.split('-')
            if len(rng) == 1:
                # part is just one expected code
                regexp += '%s|' % part
            else:
                lower, upper = part.split('-')
                regexp += '%s|' % lower
                if int(lower) > int(upper):
                    msg = _('Invalid range of expected codes: %s') % (part,)
                    LOG.error(msg)
                    raise exceptions.ConfigError(msg=msg)

                while lower != upper:
                    lower = str(int(lower) + 1)
                    regexp += '%s|' % lower

        return regexp[:-1]
