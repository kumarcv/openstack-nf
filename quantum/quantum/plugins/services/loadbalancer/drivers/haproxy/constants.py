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

from quantum.plugins.services.loadbalancer.drivers import constants


STATS_SOCKET_PATH = '/var/run/haproxy.sock'

STATS_MAPPING = {
    constants.STATS_CURRENT_CONNECTIONS: 'qcur',
    constants.STATS_MAX_CONNECTIONS: 'qmax',
    constants.STATS_CURRENT_SESSIONS: 'scur',
    constants.STATS_MAX_SESSIONS: 'smax',
    constants.STATS_TOTAL_SESSIONS: 'stot',
    constants.STATS_IN_BYTES: 'bin',
    constants.STATS_OUT_BYTES: 'bout',
    constants.STATS_REQUEST_ERRORS: 'ereq',
    constants.STATS_CONNECTION_ERRORS: 'econ',
    constants.STATS_RESPONSE_ERRORS: 'eresp',
    constants.STATS_RETRIES: 'wretr',
    constants.STATS_FAILED_CHECKS: 'chkfail',
    constants.STATS_HEALTH: 'check_status',
    constants.STATS_CURRENT_REQUESTS: 'req_rate',
    constants.STATS_MAX_REQUESTS: 'req_rate_max',
    constants.STATS_TOTAL_REQUESTS: 'req_tot',
}

HEALTH_MAPPING = {
    'UNK': constants.HEALTH_UNKNOWN,
    'SOCKERR': constants.HEALTH_SOCKET_ERROR,
    'L4OK': constants.HEALTH_TCP_OK,
    'L4TMOUT': constants.HEALTH_TCP_TIMEOUT,
    'L4CON': constants.HEALTH_TCP_ERROR,
    'L6OK': constants.HEALTH_SSL_OK,
    'L6TOUT': constants.HEALTH_SSL_TIMEOUT,
    'L6RSP': constants.HEALTH_SSL_ERROR,
    'L7OK': constants.HEALTH_L7_OK,
    'L7OKC': constants.HEALTH_L7_OK,
    'L7TOUT': constants.HEALTH_L7_TIMEOUT,
    'L7RSP': constants.HEALTH_L7_ERROR,
    'L7STS': constants.HEALTH_L7_ERROR
}


ALGORITHMS_MAPPING = {
    constants.LB_METHOD_ROUND_ROBIN: 'roundrobin',
    constants.LB_METHOD_LEAST_CONNECTION: 'leastconn',
    constants.LB_METHOD_HASH_SOURCE: 'source',
    constants.LB_METHOD_HASH_URI: 'uri',
}

PROTOCOL_MAPPING = {
    constants.PROTOCOL_TCP: 'tcp',
    constants.PROTOCOL_HTTP: 'http',
    constants.PROTOCOL_HTTPS: 'tcp',
}
