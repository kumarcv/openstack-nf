# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Cisco Systems, Inc.
# Copyright 2012 NEC Corporation
# Copyright 2013 Freescale Semiconductor, Inc.s
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

from __future__ import absolute_import

import logging

from quantumclient.v2_0 import client as quantum_client
from django.utils.datastructures import SortedDict

from horizon.api.base import APIDictWrapper, url_for


LOG = logging.getLogger(__name__)


class QuantumAPIDictWrapper(APIDictWrapper):

    def set_id_as_name_if_empty(self, length=8):
        try:
            if not self._apidict['name']:
                id = self._apidict['id']
                if length:
                    id = id[:length]
                self._apidict['name'] = '(%s)' % id
        except KeyError:
            pass

    def items(self):
        return self._apidict.items()


class Network(QuantumAPIDictWrapper):
    """Wrapper for quantum Networks"""
    _attrs = ['name', 'id', 'subnets', 'tenant_id', 'status',
              'admin_state_up', 'shared']

    def __init__(self, apiresource):
        apiresource['admin_state'] = \
            'UP' if apiresource['admin_state_up'] else 'DOWN'
        super(Network, self).__init__(apiresource)


class Subnet(QuantumAPIDictWrapper):
    """Wrapper for quantum subnets"""
    _attrs = ['name', 'id', 'cidr', 'network_id', 'tenant_id',
              'ip_version', 'ipver_str']

    def __init__(self, apiresource):
        apiresource['ipver_str'] = get_ipver_str(apiresource['ip_version'])
        super(Subnet, self).__init__(apiresource)


class Port(QuantumAPIDictWrapper):
    """Wrapper for quantum ports"""
    _attrs = ['name', 'id', 'network_id', 'tenant_id',
              'admin_state_up', 'status', 'mac_address',
              'fixed_ips', 'host_routes', 'device_id']

    def __init__(self, apiresource):
        apiresource['admin_state'] = \
            'UP' if apiresource['admin_state_up'] else 'DOWN'
        super(Port, self).__init__(apiresource)


IP_VERSION_DICT = {4: 'IPv4', 6: 'IPv6'}


def get_ipver_str(ip_version):
    """Convert an ip version number to a human-friendly string"""
    return IP_VERSION_DICT.get(ip_version, '')


def quantumclient(request):
    LOG.debug('quantumclient connection created using token "%s" and url "%s"'
              % (request.user.token.id, url_for(request, 'network')))
    LOG.debug('user_id=%(user)s, tenant_id=%(tenant)s' %
              {'user': request.user.id, 'tenant': request.user.tenant_id})
    c = quantum_client.Client(token=request.user.token.id,
                              endpoint_url=url_for(request, 'network'))
    return c


def network_list(request, **params):
    LOG.debug("network_list(): params=%s" % (params))
    networks = quantumclient(request).list_networks(**params).get('networks')
    # Get subnet list to expand subnet info in network list.
    subnets = subnet_list(request)
    subnet_dict = SortedDict([(s['id'], s) for s in subnets])
    # Expand subnet list from subnet_id to values.
    for n in networks:
        n['subnets'] = [subnet_dict[s] for s in n['subnets']]
    return [Network(n) for n in networks]


def network_list_for_tenant(request, tenant_id, **params):
    """Return a network list available for the tenant.
    The list contains networks owned by the tenant and public networks.
    If requested_networks specified, it searches requested_networks only.
    """
    LOG.debug("network_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    # If a user has admin role, network list returned by Quantum API
    # contains networks that do not belong to that tenant.
    # So we need to specify tenant_id when calling network_list().
    networks = network_list(request, tenant_id=tenant_id,
                            shared=False, **params)

    # In the current Quantum API, there is no way to retrieve
    # both owner networks and public networks in a single API call.
    networks += network_list(request, shared=True, **params)

    return networks


def network_get(request, network_id, **params):
    LOG.debug("network_get(): netid=%s, params=%s" % (network_id, params))
    network = quantumclient(request).show_network(network_id,
                                                  **params).get('network')
    # Since the number of subnets per network must be small,
    # call subnet_get() for each subnet instead of calling
    # subnet_list() once.
    network['subnets'] = [subnet_get(request, sid)
                          for sid in network['subnets']]
    return Network(network)


def network_create(request, **kwargs):
    """
    Create a subnet on a specified network.
    :param request: request context
    :param tenant_id: (optional) tenant id of the network created
    :param name: (optional) name of the network created
    :returns: Subnet object
    """
    LOG.debug("network_create(): kwargs = %s" % kwargs)
    body = {'network': kwargs}
    network = quantumclient(request).create_network(body=body).get('network')
    return Network(network)


def network_modify(request, network_id, **kwargs):
    LOG.debug("network_modify(): netid=%s, params=%s" % (network_id, kwargs))
    body = {'network': kwargs}
    network = quantumclient(request).update_network(network_id,
                                                    body=body).get('network')
    return Network(network)


def network_delete(request, network_id):
    LOG.debug("network_delete(): netid=%s" % network_id)
    quantumclient(request).delete_network(network_id)


def subnet_list(request, **params):
    LOG.debug("subnet_list(): params=%s" % (params))
    subnets = quantumclient(request).list_subnets(**params).get('subnets')
    return [Subnet(s) for s in subnets]


def subnet_get(request, subnet_id, **params):
    LOG.debug("subnet_get(): subnetid=%s, params=%s" % (subnet_id, params))
    subnet = quantumclient(request).show_subnet(subnet_id,
                                                **params).get('subnet')
    return Subnet(subnet)


def subnet_create(request, network_id, cidr, ip_version, **kwargs):
    """
    Create a subnet on a specified network.
    :param request: request context
    :param network_id: network id a subnet is created on
    :param cidr: subnet IP address range
    :param ip_version: IP version (4 or 6)
    :param gateway_ip: (optional) IP address of gateway
    :param tenant_id: (optional) tenant id of the subnet created
    :param name: (optional) name of the subnet created
    :returns: Subnet object
    """
    LOG.debug("subnet_create(): netid=%s, cidr=%s, ipver=%d, kwargs=%s"
              % (network_id, cidr, ip_version, kwargs))
    body = {'subnet':
                {'network_id': network_id,
                 'ip_version': ip_version,
                 'cidr': cidr}}
    body['subnet'].update(kwargs)
    subnet = quantumclient(request).create_subnet(body=body).get('subnet')
    return Subnet(subnet)


def subnet_modify(request, subnet_id, **kwargs):
    LOG.debug("subnet_modify(): subnetid=%s, kwargs=%s" % (subnet_id, kwargs))
    body = {'subnet': kwargs}
    subnet = quantumclient(request).update_subnet(subnet_id,
                                                  body=body).get('subnet')
    return Subnet(subnet)


def subnet_delete(request, subnet_id):
    LOG.debug("subnet_delete(): subnetid=%s" % subnet_id)
    quantumclient(request).delete_subnet(subnet_id)


def port_list(request, **params):
    LOG.debug("port_list(): params=%s" % (params))
    ports = quantumclient(request).list_ports(**params).get('ports')
    return [Port(p) for p in ports]


def port_get(request, port_id, **params):
    LOG.debug("port_get(): portid=%s, params=%s" % (port_id, params))
    port = quantumclient(request).show_port(port_id, **params).get('port')
    return Port(port)


def port_create(request, network_id, **kwargs):
    """
    Create a port on a specified network.
    :param request: request context
    :param network_id: network id a subnet is created on
    :param device_id: (optional) device id attached to the port
    :param tenant_id: (optional) tenant id of the port created
    :param name: (optional) name of the port created
    :returns: Port object
    """
    LOG.debug("port_create(): netid=%s, kwargs=%s" % (network_id, kwargs))
    body = {'port': {'network_id': network_id}}
    body['port'].update(kwargs)
    port = quantumclient(request).create_port(body=body).get('port')
    return Port(port)


def port_delete(request, port_id):
    LOG.debug("port_delete(): portid=%s" % port_id)
    quantumclient(request).delete_port(port_id)


def port_modify(request, port_id, **kwargs):
    LOG.debug("port_modify(): portid=%s, kwargs=%s" % (port_id, kwargs))
    body = {'port': kwargs}
    port = quantumclient(request).update_port(port_id, body=body).get('port')
    return Port(port)

####Modifications by Srikanth####################
class Configuration(QuantumAPIDictWrapper):
    """Wrapper for SLB configurations"""
    _attrs = ['name', 'id', 'tenant_id',
              'category_id', 'status', 'category']

    def __init__(self, apiresource):
        super(Configuration, self).__init__(apiresource)
        
def configuration_list(request, **params):
    LOG.debug("configuration_list(): params=%s" % (params))
    configurations = quantumclient(request).list_configurations(**params).get('configurations')
    return [Configuration(n) for n in configurations]


def configuration_list_for_tenant(request, tenant_id, **params):
    """Return a configuration list available for the tenant.
    The list contains configurations owned by the tenant.
    """
    LOG.debug("configuration_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    configurations = configuration_list(request, tenant_id=tenant_id,
                            shared=False, **params)

    # In the current Quantum API, there is no way to retrieve
    # both owner networks and public networks in a single API call.
    #configurations += configuration_list(request, shared=True, **params)

    return configurations

def configuration_create(request, **kwargs):
    """
    Create a configuration
    :param request: request context
    :param tenant_id: (optional) tenant id of the network created
    :param name: (optional) name of the service created
    
    """
    LOG.debug("configuration_create(): kwargs = %s" % kwargs)
    body = {'configuration': kwargs}
    configuration = quantumclient(request).create_configuration(body=body).get('configuration')
    return Configuration(configuration)
    
def configuration_delete(request, configuration_id):
    LOG.debug("configuration_delete(): configid=%s" % configuration_id)
    quantumclient(request).delete_configuration(configuration_id)
    
def configuration_get(request, configuration_id, **params):
    LOG.debug("configuration_get(): configid=%s, params=%s" % (configuration_id, params))
    configuration = quantumclient(request).show_configuration(configuration_id, **params).get('configuration')
    return Configuration(configuration)
    
def configuration_modify(request, configuration_id, **kwargs):
    LOG.debug("configuration_modify(): configid=%s, kwargs=%s" % (configuration_id, kwargs))
    body = {'configuration': kwargs}
    configuration = quantumclient(request).update_configuration(configuration_id,
                                                  body=body).get('configuration')
    return Configuration(configuration)

class Pool(QuantumAPIDictWrapper):
    """Wrapper for SLB pools"""
    _attrs = ['name', 'id', 'tenant_id',
              'subnet_id', 'status', 'description',
              'protocol', 'lb_method', 'admin_status',
              'subnet']

    def __init__(self, apiresource):
        super(Pool, self).__init__(apiresource)
        
class PoolMember(QuantumAPIDictWrapper):
    """Wrapper for SLB pool members"""
    _attrs = ['id', 'name', 'tenant_id', 'pool_id'
              'ip_address', 'port_no', 'weight',
              'admin_status','status']

    def __init__(self, apiresource):
        super(PoolMember, self).__init__(apiresource)
        
class Monitor(QuantumAPIDictWrapper):
    """Wrapper for SLB health monitors"""
    _attrs = ['id', 'name', 'tenant_id', 'pool_id'
              'type', 'delay', 'timeout',
              'max_retries', 'http_method', 'url_path',
              'expected_codes', 'admin_status','status']

    def __init__(self, apiresource):
        super(Monitor, self).__init__(apiresource)
        
class VIP(QuantumAPIDictWrapper):
    """Wrapper for SLB health monitors"""
    _attrs = ['id', 'tenant_id', 'pool_id'
              'session_persistance_id', 'name', 'description',
              'port_no', 'protocol', 'connection_limit', 'logical_device_uuid',
              'status', 'admin_status', 'session_persistance_type', 'session_persistance_cookie']

    def __init__(self, apiresource):
        super(VIP, self).__init__(apiresource)
        
class SessionPersistance(QuantumAPIDictWrapper):
    """Wrapper for SLB Session Persistance"""
    _attrs = ['id', 'type', 'cookie_name']

    def __init__(self, apiresource):
        super(SessionPersistance, self).__init__(apiresource)
        
###Pools
def pool_list(request, **params):
    LOG.debug("pool_list(): params=%s" % (params))
    pools = quantumclient(request).list_pools(**params).get('pools')
    return [Pool(n) for n in pools]


def pool_list_for_tenant(request, tenant_id, **params):
    """Return a pool list available for the tenant.
    The list contains pools owned by the tenant.
    """
    LOG.debug("pool_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    pools = pool_list(request, tenant_id=tenant_id,
                            shared=False, **params)

    # In the current Quantum API, there is no way to retrieve
    # both owner networks and public networks in a single API call.
    #pools += pool_list(request, shared=True, **params)

    return pools

def pool_create(request, **kwargs):
    """
    Create a pool
    :param request: request context
    :param tenant_id: (optional) tenant id of the network created
    :param name: (optional) name of the service created
    
    """
    LOG.debug("pool_create(): kwargs = %s" % kwargs)
    body = {'pool': kwargs}
    pool = quantumclient(request).create_pool(body=body).get('pool')
    return Pool(pool)
    
def pool_delete(request, pool_id):
    LOG.debug("pool_delete(): configid=%s" % pool_id)
    quantumclient(request).delete_pool(pool_id)
    
def pool_get(request, pool_id, **params):
    LOG.debug("pool_get(): poolid=%s, params=%s" % (pool_id, params))
    pool = quantumclient(request).show_pool(pool_id, **params).get('pool')
    return Pool(pool)
    
def pool_modify(request, pool_id, **kwargs):
    LOG.debug("pool_modify(): configid=%s, kwargs=%s" % (pool_id, kwargs))
    body = {'pool': kwargs}
    pool = quantumclient(request).update_pool(pool_id,
                                                  body=body).get('pool')
    return Pool(pool)

###Pool Members
def member_list(request, tenant_id, **params):
    LOG.debug("pool_member_list(): params=%s" % (params))
    pool_members = quantumclient(request).list_members(**params).get('members')
    return [PoolMember(s) for s in pool_members]
    
def member_list_for_tenant(request, tenant_id, **params):
    """Return a member list available for the tenant.
    The list contains members owned by the tenant.
    """
    LOG.debug("member_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    members = member_list(request, tenant_id=tenant_id,
                            shared=False, **params)

    # In the current Quantum API, there is no way to retrieve
    # both owner networks and public networks in a single API call.
    #members += member_list(request, shared=True, **params)

    return members

def member_create(request, **kwargs):
    """
    Create a member
    :param request: request context
    :param tenant_id: (optional) tenant id of the network created
    :param name: (optional) name of the service created
    
    """
    LOG.debug("member_create(): kwargs = %s" % kwargs)
    body = {'member': kwargs}
    member = quantumclient(request).create_member(body=body).get('member')
    return PoolMember(member)
    
def member_delete(request, member_id):
    LOG.debug("member_delete(): memberid=%s" % member_id)
    with open('/tmp/test.out', 'w+') as f:
        f.write("member - %s" % member_id)
        f.close()
    quantumclient(request).delete_member(member_id)
    
def member_get(request, member_id, **params):
    LOG.debug("member_get(): memberid=%s, params=%s" % (member_id, params))
    member = quantumclient(request).show_member(member_id, **params).get('member')
    return PoolMember(member)
    
def member_modify(request, member_id, **kwargs):
    LOG.debug("member_modify(): memberid=%s, kwargs=%s" % (member_id, kwargs))
    body = {'member': kwargs}
    member = quantumclient(request).update_member(member_id,
                                                  body=body).get('member')
    return PoolMember(member)
    
###Health Monitors
def monitor_list(request, tenant_id, **params):
    LOG.debug("pool_monitor_list(): params=%s" % (params))
    pool_monitors = quantumclient(request).list_monitors(**params).get('monitors')
    return [Monitor(s) for s in pool_monitors]
    
def monitor_list_for_tenant(request, tenant_id, **params):
    """Return a monitor list available for the tenant.
    The list contains monitors owned by the tenant.
    """
    LOG.debug("monitor_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    monitors = monitor_list(request, tenant_id=tenant_id,
                            shared=False, **params)

    # In the current Quantum API, there is no way to retrieve
    # both owner networks and public networks in a single API call.
    #monitors += monitor_list(request, shared=True, **params)

    return monitors

def monitor_create(request, **kwargs):
    """
    Create a monitor
    :param request: request context
    :param tenant_id: (optional) tenant id of the network created
    :param name: (optional) name of the service created
    
    """
    LOG.debug("monitor_create(): kwargs = %s" % kwargs)
    body = {'monitor': kwargs}
    monitor = quantumclient(request).create_monitor(body=body).get('monitor')
    return Monitor(monitor)
    
def monitor_delete(request, monitor_id):
    LOG.debug("monitor_delete(): monitorid=%s" % monitor_id)
    quantumclient(request).delete_monitor(monitor_id)
    
def monitor_get(request, monitor_id, **params):
    LOG.debug("monitor_get(): monitorid=%s, params=%s" % (monitor_id, params))
    monitor = quantumclient(request).show_monitor(monitor_id, **params).get('monitor')
    return Monitor(monitor)
    
def monitor_modify(request, monitor_id, **kwargs):
    LOG.debug("monitor_modify(): monitorid=%s, kwargs=%s" % (monitor_id, kwargs))
    body = {'monitor': kwargs}
    monitor = quantumclient(request).update_monitor(monitor_id,
                                                  body=body).get('monitor')
    return Monitor(monitor)
    
###Virtual IP's
def vip_list(request, tenant_id, **params):
    LOG.debug("vip_list(): params=%s" % (params))
    vips = quantumclient(request).list_vips(**params).get('vips')
    return [VIP(s) for s in vips]
    
def vip_list_for_tenant(request, tenant_id, **params):
    """Return a vip list available for the tenant.
    The list contains vips owned by the tenant.
    """
    LOG.debug("vip_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    vips = vip_list(request, tenant_id=tenant_id,
                            shared=False, **params)

    # In the current Quantum API, there is no way to retrieve
    # both owner networks and public networks in a single API call.
    #vips += vip_list(request, shared=True, **params)

    return vips

def vip_create(request, **kwargs):
    """
    Create a vip
    :param request: request context
    :param tenant_id: (optional) tenant id of the network created
    :param name: (optional) name of the service created
    
    """
    LOG.debug("vip_create(): kwargs = %s" % kwargs)
    body = {'vip': kwargs}
    vip = quantumclient(request).create_vip(body=body).get('vip')
    return VIP(vip)
    
def vip_delete(request, vip_id):
    LOG.debug("vip_delete(): vipid=%s" % vip_id)
    quantumclient(request).delete_vip(vip_id)
    
def vip_get(request, vip_id, **params):
    LOG.debug("vip_get(): vipid=%s, params=%s" % (vip_id, params))
    vip = quantumclient(request).show_vip(vip_id, **params).get('vip')
    return VIP(vip)
    
def vip_modify(request, vip_id, **kwargs):
    LOG.debug("vip_modify(): vipid=%s, kwargs=%s" % (vip_id, kwargs))
    body = {'vip': kwargs}
    vip = quantumclient(request).update_vip(vip_id,
                                                  body=body).get('vip')
    return VIP(vip)
    
###Session Persistance
def session_list(request, **params):
    LOG.debug("session_list(): params=%s" % (params))
    sessions = quantumclient(request).list_sessions(**params).get('sessions')
    return [SessionPersistance(s) for s in sessions]
    
def session_create(request, **kwargs):
    """
    Create a session
    :param request: request context
    :param tenant_id: (optional) tenant id of the network created
    :param name: (optional) name of the service created
    
    """
    LOG.debug("session_create(): kwargs = %s" % kwargs)
    body = {'session': kwargs}
    session = quantumclient(request).create_session(body=body).get('session')
    return SessionPersistance(session)
    
def session_delete(request, session_id):
    LOG.debug("session_delete(): sessionid=%s" % session_id)
    quantumclient(request).delete_session(session_id)
    
def session_get(request, session_id, **params):
    LOG.debug("session_get(): sessionid=%s, params=%s" % (session_id, params))
    session = quantumclient(request).show_session(session_id, **params).get('session')
    return SessionPersistance(session)
    
def session_modify(request, session_id, **kwargs):
    LOG.debug("session_modify(): sessionid=%s, kwargs=%s" % (session_id, kwargs))
    body = {'session': kwargs}
    session = quantumclient(request).update_session(session_id,
                                                  body=body).get('session')
    return SessionPersistance(session)
    
    
class Networkfunction(QuantumAPIDictWrapper):
    """Wrapper for quantum networkfunctions"""
    _attrs = ['name', 'id', 'description', 'tenant_id', 'shared']

    def __init__(self, apiresource):
        super(Networkfunction, self).__init__(apiresource)

def networkfunction_list(request, **params):
    LOG.debug("networkfunction_list(): params=%s" % (params))
    networkfunctions = quantumclient(request).list_networkfunctions(**params).get('networkfunctions')
    return [Networkfunction(n) for n in networkfunctions]

def networkfunction_list_for_tenant(request, tenant_id, **params):
    LOG.debug("networkfunction_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    networkfunctions = networkfunction_list(request, tenant_id=tenant_id,
                            shared=False, **params)

    networkfunctions += networkfunction_list(request, shared=True, **params)

    return networkfunctions

def networkfunction_create(request, **kwargs):
    LOG.debug("networkfunction_create(): kwargs = %s" % kwargs)
    body = {'networkfunction': kwargs}
    networkfunction = quantumclient(request).create_networkfunction(body=body).get('networkfunction')
    return Networkfunction(networkfunction)

def networkfunction_delete(request, networkfunction_id):
    LOG.debug("networkfunction_delete(): catid=%s" % networkfunction_id)
    quantumclient(request).delete_networkfunction(networkfunction_id)
    
def networkfunction_modify(request, networkfunction_id, **kwargs):
    LOG.debug("networkfunction_modify(): cateid=%s, params=%s" % (networkfunction_id, kwargs))
    body = {'networkfunction': kwargs}
    networkfunction = quantumclient(request).update_networkfunction(networkfunction_id,
                                                    body=body).get('networkfunction')
    return Networkfunction(networkfunction)    

def networkfunction_get(request, networkfunction_id, **params):
    LOG.debug("networkfunction_get(): catid=%s, params=%s" % (networkfunction_id, params))
    networkfunction = quantumclient(request).show_networkfunction(networkfunction_id,
                                                  **params).get('networkfunction')
    return Networkfunction(networkfunction)   

class Category(QuantumAPIDictWrapper):
    """Wrapper for quantum Categories"""
    _attrs = ['name', 'id', 'description', 'tenant_id', 'shared']

    def __init__(self, apiresource):
        super(Category, self).__init__(apiresource)

def category_list(request, **params):
    LOG.debug("category_list(): params=%s" % (params))
    categories = quantumclient(request).list_categories(**params).get('categories')
    return [Category(n) for n in categories]

def category_list_for_tenant(request, tenant_id, **params):
    LOG.debug("category_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    categories = category_list(request, tenant_id=tenant_id,
                            shared=False, **params)

    categories += category_list(request, shared=True, **params)

    return categories

def category_create(request, **kwargs):
    LOG.debug("category_create(): kwargs = %s" % kwargs)
    body = {'category': kwargs}
    category = quantumclient(request).create_category(body=body).get('category')
    return Category(category)

def category_delete(request, category_id):
    LOG.debug("category_delete(): catid=%s" % category_id)
    quantumclient(request).delete_category(category_id)
    
def category_modify(request, category_id, **kwargs):
    LOG.debug("category_modify(): cateid=%s, params=%s" % (category_id, kwargs))
    body = {'category': kwargs}
    category = quantumclient(request).update_category(category_id,
                                                    body=body).get('category')
    return Category(category)    

def category_get(request, category_id, **params):
    LOG.debug("category_get(): catid=%s, params=%s" % (category_id, params))
    category = quantumclient(request).show_category(category_id,
                                                  **params).get('category')
    return Category(category)
    
class Category_networkfunction(QuantumAPIDictWrapper):
    """Wrapper for quantum category_networkfunctions"""
    _attrs = ['id', 'category_id', 'networkfunction_id']

    def __init__(self, apiresource):
        super(Category_networkfunction, self).__init__(apiresource)

def category_networkfunction_list(request, **params):
    LOG.debug("category_networkfunction_list(): params=%s" % (params))
    category_networkfunctions = quantumclient(request).list_category_networkfunctions(**params).get('category_networkfunctions')
    return [Category_networkfunction(n) for n in category_networkfunctions]

def category_networkfunction_list_for_category(request, category_id, **params):
    LOG.debug("category_networkfunction_list_for_category(): category_id=%s, params=%s"
              % (category_id, params))

    category_networkfunctions = category_networkfunction_list(request, category_id=category_id,
                            shared=False, **params)

    #category_networkfunctions += category_networkfunction_list(request, shared=True, **params)

    return category_networkfunctions

def category_networkfunction_create(request, **kwargs):
    LOG.debug("category_networkfunction_create(): kwargs = %s" % kwargs)
    body = {'category_networkfunction': kwargs}
    category_networkfunction = quantumclient(request).create_category_networkfunction(body=body).get('category_networkfunction')
    return Category_networkfunction(category_networkfunction)

def category_networkfunction_delete(request, category_networkfunction_id):
    LOG.debug("category_networkfunction_delete(): catid=%s" % category_networkfunction_id)
    quantumclient(request).delete_category_networkfunction(category_networkfunction_id)
    
def category_networkfunction_modify(request, category_networkfunction_id, **kwargs):
    LOG.debug("category_networkfunction_modify(): cateid=%s, params=%s" % (category_networkfunction_id, kwargs))
    body = {'category_networkfunction': kwargs}
    category_networkfunction = quantumclient(request).update_category_networkfunction(category_networkfunction_id,
                                                    body=body).get('category_networkfunction')
    return Category_networkfunction(category_networkfunction)    

def category_networkfunction_get(request, category_networkfunction_id, **params):
    LOG.debug("category_networkfunction_get(): catid=%s, params=%s" % (category_networkfunction_id, params))
    category_networkfunction = quantumclient(request).show_category_networkfunction(category_networkfunction_id,
                                                  **params).get('category_networkfunction')
    return Category_networkfunction(category_networkfunction)
    
class Vendor(QuantumAPIDictWrapper):
    """Wrapper for quantum vendors"""
    _attrs = ['name', 'id', 'description', 'tenant_id', 'shared']

    def __init__(self, apiresource):
        super(Vendor, self).__init__(apiresource)

def vendor_list(request, **params):
    LOG.debug("vendor_list(): params=%s" % (params))
    vendors = quantumclient(request).list_vendors(**params).get('vendors')
    return [Vendor(n) for n in vendors]

def vendor_list_for_tenant(request, tenant_id, **params):
    LOG.debug("vendor_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    vendors = vendor_list(request, tenant_id=tenant_id,
                            shared=False, **params)

    vendors += vendor_list(request, shared=True, **params)

    return vendors

def vendor_create(request, **kwargs):
    LOG.debug("vendor_create(): kwargs = %s" % kwargs)
    body = {'vendor': kwargs}
    vendor = quantumclient(request).create_vendor(body=body).get('vendor')
    return Vendor(vendor)

def vendor_delete(request, vendor_id):
    LOG.debug("vendor_delete(): catid=%s" % vendor_id)
    quantumclient(request).delete_vendor(vendor_id)
    
def vendor_modify(request, vendor_id, **kwargs):
    LOG.debug("vendor_modify(): cateid=%s, params=%s" % (vendor_id, kwargs))
    body = {'vendor': kwargs}
    vendor = quantumclient(request).update_vendor(vendor_id,
                                                    body=body).get('vendor')
    return Vendor(vendor)    

def vendor_get(request, vendor_id, **params):
    LOG.debug("vendor_get(): catid=%s, params=%s" % (vendor_id, params))
    vendor = quantumclient(request).show_vendor(vendor_id,
                                                  **params).get('vendor')
    return Vendor(vendor)
    
class Image(QuantumAPIDictWrapper):
    """Wrapper for quantum images"""
    _attrs = ['name', 'id', 'tenant_id', 'category_id', 'vendor_id', 'image_id', 'flavor_id', 'security_group_id', 'shared']

    def __init__(self, apiresource):
        super(Image, self).__init__(apiresource)

def image_list(request, **params):
    LOG.debug("image_list(): params=%s" % (params))
    images = quantumclient(request).list_images(**params).get('images')
    return [Image(n) for n in images]

def image_list_for_tenant(request, tenant_id, **params):
    LOG.debug("image_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    images = image_list(request, tenant_id=tenant_id,
                            shared=False, **params)

    images += image_list(request, shared=True, **params)

    return images

def image_create(request, **kwargs):
    LOG.debug("image_create(): kwargs = %s" % kwargs)
    body = {'image': kwargs}
    image = quantumclient(request).create_image(body=body).get('image')
    return Image(image)

def image_delete(request, image_id):
    LOG.debug("image_delete(): catid=%s" % image_id)
    quantumclient(request).delete_image(image_id)
    
def image_modify(request, image_id, **kwargs):
    LOG.debug("image_modify(): cateid=%s, params=%s" % (image_id, kwargs))
    body = {'image': kwargs}
    image = quantumclient(request).update_image(image_id,
                                                    body=body).get('image')
    return Image(image)    

def image_get(request, image_id, **params):
    LOG.debug("image_get(): catid=%s, params=%s" % (image_id, params))
    image = quantumclient(request).show_image(image_id,
                                                  **params).get('image')
    return Image(image)
    
class Metadata(QuantumAPIDictWrapper):
    """Wrapper for quantum metadatas"""
    _attrs = ['name', 'id', 'value', 'image_map_id']

    def __init__(self, apiresource):
        super(Metadata, self).__init__(apiresource)

def metadata_list(request, **params):
    LOG.debug("metadata_list(): params=%s" % (params))
    metadatas = quantumclient(request).list_metadatas(**params).get('metadatas')
    return [Metadata(n) for n in metadatas]

def metadata_list_for_image(request, image_map_id, **params):
    LOG.debug("metadata_list_for_image(): image_map_id=%s, params=%s"
              % (image_map_id, params))

    metadatas = metadata_list(request, image_map_id=image_map_id,
                            shared=False, **params)

    metadatas += metadata_list(request, shared=True, **params)

    return metadatas

def metadata_create(request, **kwargs):
    LOG.debug("metadata_create(): kwargs = %s" % kwargs)
    body = {'metadata': kwargs}
    metadata = quantumclient(request).create_metadata(body=body).get('metadata')
    return Metadata(metadata)

def metadata_delete(request, metadata_id):
    LOG.debug("metadata_delete(): catid=%s" % metadata_id)
    quantumclient(request).delete_metadata(metadata_id)
    
def metadata_modify(request, metadata_id, **kwargs):
    LOG.debug("metadata_modify(): cateid=%s, params=%s" % (metadata_id, kwargs))
    body = {'metadata': kwargs}
    metadata = quantumclient(request).update_metadata(metadata_id,
                                                    body=body).get('metadata')
    return Metadata(metadata)    

def metadata_get(request, metadata_id, **params):
    LOG.debug("metadata_get(): catid=%s, params=%s" % (metadata_id, params))
    metadata = quantumclient(request).show_metadata(metadata_id,
                                                  **params).get('metadata')
    return Metadata(metadata)
    
class Personality(QuantumAPIDictWrapper):
    """Wrapper for quantum personalities"""
    _attrs = ['file_path', 'id', 'file_content', 'image_map_id']

    def __init__(self, apiresource):
        super(Personality, self).__init__(apiresource)

def personality_list(request, **params):
    LOG.debug("personality_list(): params=%s" % (params))
    personalities = quantumclient(request).list_personalities(**params).get('personalities')
    return [Personality(n) for n in personalities]

def personality_list_for_image(request, image_map_id, **params):
    LOG.debug("personality_list_for_image(): image_map_id=%s, params=%s"
              % (image_map_id, params))

    personalities = personality_list(request, image_map_id=image_map_id,
                            shared=False, **params)

    personalities += personality_list(request, shared=True, **params)

    return personalities

def personality_create(request, **kwargs):
    LOG.debug("personality_create(): kwargs = %s" % kwargs)
    body = {'personality': kwargs}
    personality = quantumclient(request).create_personality(body=body).get('personality')
    return Personality(personality)

def personality_delete(request, personality_id):
    LOG.debug("personality_delete(): catid=%s" % personality_id)
    quantumclient(request).delete_personality(personality_id)
    
def personality_modify(request, personality_id, **kwargs):
    LOG.debug("personality_modify(): cateid=%s, params=%s" % (personality_id, kwargs))
    body = {'personality': kwargs}
    personality = quantumclient(request).update_personality(personality_id,
                                                    body=body).get('personality')
    return Personality(personality)    

def personality_get(request, personality_id, **params):
    LOG.debug("personality_get(): catid=%s, params=%s" % (personality_id, params))
    personality = quantumclient(request).show_personality(personality_id,
                                                  **params).get('personality')
    return Personality(personality)
    
class Chain(QuantumAPIDictWrapper):
    """Wrapper for quantum chains"""
    _attrs = ['name', 'id', 'type', 'tenant_id', 'auto_boot']

    def __init__(self, apiresource):
        super(Chain, self).__init__(apiresource)

def chain_list(request, **params):
    LOG.debug("chain_list(): params=%s" % (params))
    chains = quantumclient(request).list_chains(**params).get('chains')
    return [Chain(n) for n in chains]

def chain_list_for_tenant(request, tenant_id, **params):
    LOG.debug("chain_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))

    chains = chain_list(request, tenant_id=tenant_id,
                            shared=True, **params)

    #chains += chain_list(request, shared=True, **params)

    return chains

def chain_create(request, **kwargs):
    LOG.debug("chain_create(): kwargs = %s" % kwargs)
    body = {'chain': kwargs}
    chain = quantumclient(request).create_chain(body=body).get('chain')
    return Chain(chain)

def chain_delete(request, chain_id):
    LOG.debug("chain_delete(): catid=%s" % chain_id)
    quantumclient(request).delete_chain(chain_id)
    
def chain_modify(request, chain_id, **kwargs):
    LOG.debug("chain_modify(): cateid=%s, params=%s" % (chain_id, kwargs))
    body = {'chain': kwargs}
    chain = quantumclient(request).update_chain(chain_id,
                                                    body=body).get('chain')
    return Chain(chain)    

def chain_get(request, chain_id, **params):
    LOG.debug("chain_get(): catid=%s, params=%s" % (chain_id, params))
    chain = quantumclient(request).show_chain(chain_id,
                                                  **params).get('chain')
    return Chain(chain)

class Chain_image(QuantumAPIDictWrapper):
    """Wrapper for quantum chain_images"""
    _attrs = ['name', 'id', 'chain_id', 'image_map_id', 'sequence_number', 'instance_id' , 'instance_uuid']

    def __init__(self, apiresource):
        super(Chain_image, self).__init__(apiresource)

def chain_image_list(request, **params):
    LOG.debug("chain_image_list(): params=%s" % (params))
    chain_images = quantumclient(request).list_chain_images(**params).get('chain_images')
    return [Chain_image(n) for n in chain_images]

def chain_image_list_for_chain(request, chain_id, **params):
    LOG.debug("chain_image_list_for_chain(): chain_id=%s, params=%s"
              % (chain_id, params))
    chain_images = chain_image_list(request, chain_id=chain_id,
                            shared=False, **params)

    #chain_images += chain_image_list(request, shared=True, **params)

    return chain_images

def chain_image_create(request, **kwargs):
    LOG.debug("chain_image_create(): kwargs = %s" % kwargs)
    body = {'chain_image': kwargs}
    chain_image = quantumclient(request).create_chain_image(body=body).get('chain_image')
    return Chain_image(chain_image)

def chain_image_delete(request, chain_image_id):
    LOG.debug("chain_image_delete(): catid=%s" % chain_image_id)
    quantumclient(request).delete_chain_image(chain_image_id)
    
def chain_image_modify(request, chain_image_id, **kwargs):
    LOG.debug("chain_image_modify(): cateid=%s, params=%s" % (chain_image_id, kwargs))
    body = {'chain_image': kwargs}
    chain_image = quantumclient(request).update_chain_image(chain_image_id,
                                                    body=body).get('chain_image')
    return Chain_image(chain_image)    

def chain_image_get(request, chain_image_id, **params):
    LOG.debug("chain_image_get(): catid=%s, params=%s" % (chain_image_id, params))
    chain_image = quantumclient(request).show_chain_image(chain_image_id,
                                                  **params).get('chain_image')
    return Chain_image(chain_image)
    
class Chain_image_network(QuantumAPIDictWrapper):
    """Wrapper for quantum chain_image_networks"""
    _attrs = ['id', 'name', 'chain_map_id', 'network_id']

    def __init__(self, apiresource):
        super(Chain_image_network, self).__init__(apiresource)

def chain_image_network_list(request, **params):
    LOG.debug("chain_image_network_list(): params=%s" % (params))
    chain_image_networks = quantumclient(request).list_chain_image_networks(**params).get('chain_image_networks')
    return [Chain_image_network(n) for n in chain_image_networks]

def chain_image_network_list_for_chain(request, chain_map_id, **params):
    LOG.debug("chain_image_network_list_for_chain(): chain_map_id=%s, params=%s"
              % (chain_map_id, params))

    chain_image_networks = chain_image_network_list(request, chain_map_id=chain_map_id,
                            shared=False, **params)

    #chain_image_networks += chain_image_network_list(request, shared=True, **params)

    return chain_image_networks



def chain_image_network_list_for_chain_networks(request, chain_map_id, **params):
    LOG.debug("chain_image_network_list_for_chain(): chain_map_id=%s, params=%s"
              % (chain_map_id, params))

    chain_image_networks = chain_image_network_list(request, chain_map_id=chain_map_id,
                            shared=False, **params)
    networks = []
    for chain_image_network in chain_image_networks:
        networks += network_list(request, id=chain_image_network.network_id,
                        shared=False, **params)
        
        
    
    #chain_image_networks += chain_image_network_list(request, shared=True, **params)

    return networks

def chain_image_network_create(request, **kwargs):
    LOG.debug("chain_image_network_create(): kwargs = %s" % kwargs)
    body = {'chain_image_network': kwargs}
    chain_image_network = quantumclient(request).create_chain_image_network(body=body).get('chain_image_network')
    return Chain_image_network(chain_image_network)

def chain_image_network_delete(request, chain_image_network_id):
    LOG.debug("chain_image_network_delete(): catid=%s" % chain_image_network_id)
    quantumclient(request).delete_chain_image_network(chain_image_network_id)
    
def chain_image_network_delete_map(request, network_id, **params):
    LOG.debug("chain_image_network_delete_map(): catid=%s" % network_id)
    
    chain_image_networks_arr = chain_image_network_list(request, network_id=network_id,
                            shared=False, **params)
    for chain_image_network_arr in chain_image_networks_arr:
        chain_image_network_delete(request, chain_image_network_arr.id)
    
    
    
    
def chain_image_network_modify(request, chain_image_network_id, **kwargs):
    LOG.debug("chain_image_network_modify(): cateid=%s, params=%s" % (chain_image_network_id, kwargs))
    body = {'chain_image_network': kwargs}
    chain_image_network = quantumclient(request).update_chain_image_network(chain_image_network_id,
                                                    body=body).get('chain_image_network')
    return Chain_image_network(chain_image_network)    

def chain_image_network_get(request, chain_image_network_id, **params):
    LOG.debug("chain_image_network_get(): catid=%s, params=%s" % (chain_image_network_id, params))
    chain_image_network = quantumclient(request).show_chain_image_network(chain_image_network_id,
                                                  **params).get('chain_image_network')
    return Chain_image_network(chain_image_network)
    
class Chain_image_conf(QuantumAPIDictWrapper):
    """Wrapper for quantum chain_image_confs"""
    _attrs = ['id', 'name', 'chain_map_id', 'config_handle_id', 'networkfunction_id']

    def __init__(self, apiresource):
        super(Chain_image_conf, self).__init__(apiresource)

def chain_image_conf_list(request, **params):
    LOG.debug("chain_image_conf_list(): params=%s" % (params))
    chain_image_confs = quantumclient(request).list_chain_image_confs(**params).get('chain_image_confs')
    return [Chain_image_conf(n) for n in chain_image_confs]

def chain_image_conf_list_for_chain(request, chain_map_id, **params):
    LOG.debug("chain_image_conf_list_for_chain(): chain_map_id=%s, params=%s"
              % (chain_map_id, params))

    chain_image_confs = chain_image_conf_list(request, chain_map_id=chain_map_id,
                            shared=False, **params)

    #chain_image_confs += chain_image_conf_list(request, shared=True, **params)

    return chain_image_confs

def chain_image_conf_create(request, **kwargs):
    LOG.debug("chain_image_conf_create(): kwargs = %s" % kwargs)
    body = {'chain_image_conf': kwargs}
    chain_image_conf = quantumclient(request).create_chain_image_conf(body=body).get('chain_image_conf')
    return Chain_image_conf(chain_image_conf)

def chain_image_conf_delete(request, chain_image_conf_id):
    LOG.debug("chain_image_conf_delete(): catid=%s" % chain_image_conf_id)
    quantumclient(request).delete_chain_image_conf(chain_image_conf_id)
    
def chain_image_conf_modify(request, chain_image_conf_id, **kwargs):
    LOG.debug("chain_image_conf_modify(): cateid=%s, params=%s" % (chain_image_conf_id, kwargs))
    body = {'chain_image_conf': kwargs}
    chain_image_conf = quantumclient(request).update_chain_image_conf(chain_image_conf_id,
                                                    body=body).get('chain_image_conf')
    return Chain_image_conf(chain_image_conf)    

def chain_image_conf_get(request, chain_image_conf_id, **params):
    LOG.debug("chain_image_conf_get(): catid=%s, params=%s" % (chain_image_conf_id, params))
    chain_image_conf = quantumclient(request).show_chain_image_conf(chain_image_conf_id,
                                                  **params).get('chain_image_conf')
    return Chain_image_conf(chain_image_conf)
    
    
class Config_handle(QuantumAPIDictWrapper):
    """Wrapper for quantum config_handles"""
    _attrs = ['name', 'id', 'description', 'tenant_id', 'shared']

    def __init__(self, apiresource):
        super(Config_handle, self).__init__(apiresource)

def config_handle_list(request, **params):
    LOG.debug("config_handle_list(): params=%s" % (params))
    config_handles = quantumclient(request).list_config_handles(**params).get('config_handles')
    return [Config_handle(n) for n in config_handles]

def config_handle_list_for_tenant(request, tenant_id, **params):
    LOG.debug("config_handle_list_for_tenant(): tenant_id=%s, params=%s"
              % (tenant_id, params))
    config_handles = config_handle_list(request, tenant_id=tenant_id,
                            shared=False, **params)

    #config_handles += config_handle_list(request, shared=True, **params)

    return config_handles

def config_handle_create(request, **kwargs):
    LOG.debug("config_handle_create(): kwargs = %s" % kwargs)
    body = {'config_handle': kwargs}
    config_handle = quantumclient(request).create_config_handle(body=body).get('config_handle')
    return Config_handle(config_handle)

def config_handle_delete(request, config_handle_id):
    LOG.debug("config_handle_delete(): catid=%s" % config_handle_id)
    quantumclient(request).delete_config_handle(config_handle_id)
    
def config_handle_modify(request, config_handle_id, **kwargs):
    LOG.debug("config_handle_modify(): cateid=%s, params=%s" % (config_handle_id, kwargs))
    body = {'config_handle': kwargs}
    config_handle = quantumclient(request).update_config_handle(config_handle_id,
                                                    body=body).get('config_handle')
    return Config_handle(config_handle)    

def config_handle_get(request, config_handle_id, **params):
    LOG.debug("config_handle_get(): catid=%s, params=%s" % (config_handle_id, params))
    config_handle = quantumclient(request).show_config_handle(config_handle_id,
                                                  **params).get('config_handle')
    return Config_handle(config_handle)
    
def generate_config(request, config_handle_id, **params):
    LOG.debug("generate_config(): config_handle_id=%s" % config_handle_id)
    config = quantumclient(request).generate_configuration(config_handle_id, **params).get('config')
    return config

def launch_chain(request, config_handle_id, **params):
    LOG.debug("launch_chain(): config_handle_id=%s" % config_handle_id)
    
    launch = quantumclient(request).launch_chain(config_handle_id, **params).get('launch')
    return launch