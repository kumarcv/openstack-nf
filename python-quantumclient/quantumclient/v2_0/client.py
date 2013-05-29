# Copyright 2012 OpenStack LLC.
# Copyright 2013 Freescale Semiconductor, Inc.
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
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import httplib
import logging
import time
import urllib

from quantumclient.client import HTTPClient
from quantumclient.common import exceptions
from quantumclient.common.serializer import Serializer

_logger = logging.getLogger(__name__)


def exception_handler_v20(status_code, error_content):
    """ Exception handler for API v2.0 client

        This routine generates the appropriate
        Quantum exception according to the contents of the
        response body

        :param status_code: HTTP error status code
        :param error_content: deserialized body of error response
    """

    quantum_errors = {
        'NetworkNotFound': exceptions.NetworkNotFoundClient,
        'NetworkInUse': exceptions.NetworkInUseClient,
        'PortNotFound': exceptions.PortNotFoundClient,
        'RequestedStateInvalid': exceptions.StateInvalidClient,
        'PortInUse': exceptions.PortInUseClient,
        'AlreadyAttached': exceptions.AlreadyAttachedClient, }

    error_dict = None
    if isinstance(error_content, dict):
        error_dict = error_content.get('QuantumError')
    # Find real error type
    bad_quantum_error_flag = False
    if error_dict:
        # If QuantumError key is found, it will definitely contain
        # a 'message' and 'type' keys?
        try:
            error_type = error_dict['type']
            error_message = (error_dict['message'] + "\n" +
                             error_dict['detail'])
        except Exception:
            bad_quantum_error_flag = True
        if not bad_quantum_error_flag:
            ex = None
            try:
                # raise the appropriate error!
                ex = quantum_errors[error_type](message=error_message)
                ex.args = ([dict(status_code=status_code,
                                 message=error_message)], )
            except Exception:
                pass
            if ex:
                raise ex
        else:
            raise exceptions.QuantumClientException(message=error_dict)
    else:
        message = None
        if isinstance(error_content, dict):
            message = error_content.get('message', None)
        if message:
            raise exceptions.QuantumClientException(status_code=status_code,
                                                    message=message)

    # If we end up here the exception was not a quantum error
    msg = "%s-%s" % (status_code, error_content)
    raise exceptions.QuantumClientException(status_code=status_code,
                                            message=msg)


class APIParamsCall(object):
    """A Decorator to add support for format and tenant overriding
       and filters
    """
    def __init__(self, function):
        self.function = function

    def __get__(self, instance, owner):
        def with_params(*args, **kwargs):
            _format = instance.format
            if 'format' in kwargs:
                instance.format = kwargs['format']
            ret = self.function(instance, *args, **kwargs)
            instance.format = _format
            return ret
        return with_params


class Client(object):
    """Client for the OpenStack Quantum v2.0 API.

    :param string username: Username for authentication. (optional)
    :param string password: Password for authentication. (optional)
    :param string token: Token for authentication. (optional)
    :param string tenant_name: Tenant name. (optional)
    :param string auth_url: Keystone service endpoint for authorization.
    :param string region_name: Name of a region to select when choosing an
                               endpoint from the service catalog.
    :param string endpoint_url: A user-supplied endpoint URL for the quantum
                            service.  Lazy-authentication is possible for API
                            service calls if endpoint is set at
                            instantiation.(optional)
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    :param insecure: ssl certificate validation. (optional)

    Example::

        >>> from quantumclient.v2_0 import client
        >>> quantum = client.Client(username=USER,
                                     password=PASS,
                                     tenant_name=TENANT_NAME,
                                     auth_url=KEYSTONE_URL)

        >>> nets = quantum.list_nets()
        ...

    """

    #Metadata for deserializing xml
    _serialization_metadata = {
        "application/xml": {
            "attributes": {
                "network": ["id", "name"],
                "port": ["id", "mac_address"],
                "subnet": ["id", "prefix"],
                "configuration": ["id", "name"],
                "pool": ["id", "name"],
                "member": ["id", "name"],
                "monitor": ["id", "name"],
                "vip": ["id", "name"],
                "session": ["id", "type"]},
            "plurals": {
                "networks": "network",
                "ports": "port",
                "subnets": "subnet",
                "configurations": "configuration",
                "pools": "pool",
                "members": "member",
                "vips": "vip",
                "sessions": "session",}, }, }

    networks_path = "/networks"
    network_path = "/networks/%s"
    ports_path = "/ports"
    port_path = "/ports/%s"
    subnets_path = "/subnets"
    subnet_path = "/subnets/%s"
    quotas_path = "/quotas"
    quota_path = "/quotas/%s"
    exts_path = "/extensions"
    ext_path = "/extensions/%s"
    routers_path = "/routers"
    router_path = "/routers/%s"
    floatingips_path = "/floatingips"
    floatingip_path = "/floatingips/%s"
    #loadbalancer_path = "/loadbalancer/vip/%s"
    
    configurations_path = "/lb/configurations"
    configuration_path = "/lb/configurations/%s"
    pools_path = "/lb/pools"
    pool_path = "/lb/pools/%s"
    members_path = "/lb/members"
    member_path = "/lb/members/%s"
    monitors_path = "/lb/monitors"
    monitor_path = "/lb/monitors/%s"
    vips_path = "/lb/vips"
    vip_path = "/lb/vips/%s"
    sessions_path = "/lb/sessions"
    session_path = "/lb/sessions/%s"
    slb_configs_path = "/lb/configs"
    slb_config_path = "/lb/configs/%s"
    
    networkfunctions_path = "/fns/networkfunctions"
    networkfunction_path = "/fns/networkfunctions/%s"
    categories_path = "/fns/categories"
    category_path = "/fns/categories/%s"
    category_networkfunctions_path = "/fns/category_networkfunctions"
    category_networkfunction_path = "/fns/category_networkfunctions/%s"
    vendors_path = "/fns/vendors"
    vendor_path = "/fns/vendors/%s"
    images_path = "/fns/images"
    image_path = "/fns/images/%s"
    metadatas_path = "/fns/metadatas"
    metadata_path = "/fns/metadatas/%s"
    personalities_path = "/fns/personalities"
    personality_path = "/fns/personalities/%s"
    chains_path = "/fns/chains"
    chain_path = "/fns/chains/%s"
    chain_images_path = "/fns/chain_images"
    chain_image_path = "/fns/chain_images/%s"
    chain_image_networks_path = "/fns/chain_image_networks"
    chain_image_network_path = "/fns/chain_image_networks/%s"
    chain_image_confs_path = "/fns/chain_image_confs"
    chain_image_conf_path = "/fns/chain_image_confs/%s"
    config_handles_path = "/fns/config_handles"
    config_handle_path = "/fns/config_handles/%s"
    
    launchs_path = "/fns/launchs"
    launch_path = "/fns/launchs/%s"

    @APIParamsCall
    def get_vip_list(self,**_params):
        """(trinath) get VIP list .. FAKE  """
        return self.get(self.loadbalancer_path % 'tenant', params=_params)

    @APIParamsCall
    def get_quotas_tenant(self, **_params):
        """Fetch tenant info in server's context for
        following quota operation."""
        return self.get(self.quota_path % 'tenant', params=_params)

    @APIParamsCall
    def list_quotas(self, **_params):
        """Fetch all tenants' quotas."""
        return self.get(self.quotas_path, params=_params)

    @APIParamsCall
    def show_quota(self, tenant_id, **_params):
        """Fetch information of a certain tenant's quotas."""
        return self.get(self.quota_path % (tenant_id), params=_params)

    @APIParamsCall
    def update_quota(self, tenant_id, body=None):
        """Update a tenant's quotas."""
        return self.put(self.quota_path % (tenant_id), body=body)

    @APIParamsCall
    def delete_quota(self, tenant_id):
        """Delete the specified tenant's quota values."""
        return self.delete(self.quota_path % (tenant_id))

    @APIParamsCall
    def list_extensions(self, **_params):
        """Fetch a list of all exts on server side."""
        return self.get(self.exts_path, params=_params)

    @APIParamsCall
    def show_extension(self, ext_alias, **_params):
        """Fetch a list of all exts on server side."""
        return self.get(self.ext_path % ext_alias, params=_params)

    @APIParamsCall
    def list_ports(self, **_params):
        """
        Fetches a list of all networks for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.ports_path, params=_params)

    @APIParamsCall
    def show_port(self, port, **_params):
        """
        Fetches information of a certain network
        """
        return self.get(self.port_path % (port), params=_params)

    @APIParamsCall
    def create_port(self, body=None):
        """
        Creates a new port
        """
        return self.post(self.ports_path, body=body)

    @APIParamsCall
    def update_port(self, port, body=None):
        """
        Updates a port
        """
        return self.put(self.port_path % (port), body=body)

    @APIParamsCall
    def delete_port(self, port):
        """
        Deletes the specified port
        """
        return self.delete(self.port_path % (port))

    @APIParamsCall
    def list_networks(self, **_params):
        """
        Fetches a list of all networks for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.networks_path, params=_params)

    @APIParamsCall
    def show_network(self, network, **_params):
        """
        Fetches information of a certain network
        """
        return self.get(self.network_path % (network), params=_params)

    @APIParamsCall
    def create_network(self, body=None):
        """
        Creates a new network
        """
        return self.post(self.networks_path, body=body)

    @APIParamsCall
    def update_network(self, network, body=None):
        """
        Updates a network
        """
        return self.put(self.network_path % (network), body=body)

    @APIParamsCall
    def delete_network(self, network):
        """
        Deletes the specified network
        """
        return self.delete(self.network_path % (network))

    @APIParamsCall
    def list_subnets(self, **_params):
        """
        Fetches a list of all networks for a tenant
        """
        return self.get(self.subnets_path, params=_params)

    @APIParamsCall
    def show_subnet(self, subnet, **_params):
        """
        Fetches information of a certain subnet
        """
        return self.get(self.subnet_path % (subnet), params=_params)

    @APIParamsCall
    def create_subnet(self, body=None):
        """
        Creates a new subnet
        """
        return self.post(self.subnets_path, body=body)

    @APIParamsCall
    def update_subnet(self, subnet, body=None):
        """
        Updates a subnet
        """
        return self.put(self.subnet_path % (subnet), body=body)

    @APIParamsCall
    def delete_subnet(self, subnet):
        """
        Deletes the specified subnet
        """
        return self.delete(self.subnet_path % (subnet))

    @APIParamsCall
    def list_routers(self, **_params):
        """
        Fetches a list of all routers for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.routers_path, params=_params)

    @APIParamsCall
    def show_router(self, router, **_params):
        """
        Fetches information of a certain router
        """
        return self.get(self.router_path % (router), params=_params)

    @APIParamsCall
    def create_router(self, body=None):
        """
        Creates a new router
        """
        return self.post(self.routers_path, body=body)

    @APIParamsCall
    def update_router(self, router, body=None):
        """
        Updates a router
        """
        return self.put(self.router_path % (router), body=body)

    @APIParamsCall
    def delete_router(self, router):
        """
        Deletes the specified router
        """
        return self.delete(self.router_path % (router))

    @APIParamsCall
    def add_interface_router(self, router, body=None):
        """
        Adds an internal network interface to the specified router
        """
        return self.put((self.router_path % router) + "/add_router_interface",
                        body=body)

    @APIParamsCall
    def remove_interface_router(self, router, body=None):
        """
        Removes an internal network interface from the specified router
        """
        return self.put((self.router_path % router) +
                        "/remove_router_interface", body=body)

    @APIParamsCall
    def add_gateway_router(self, router, body=None):
        """
        Adds an external network gateway to the specified router
        """
        return self.put((self.router_path % router),
                        body={'router': {'external_gateway_info': body}})

    @APIParamsCall
    def remove_gateway_router(self, router):
        """
        Removes an external network gateway from the specified router
        """
        return self.put((self.router_path % router),
                        body={'router': {'external_gateway_info': {}}})

    @APIParamsCall
    def list_floatingips(self, **_params):
        """
        Fetches a list of all floatingips for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.floatingips_path, params=_params)

    @APIParamsCall
    def show_floatingip(self, floatingip, **_params):
        """
        Fetches information of a certain floatingip
        """
        return self.get(self.floatingip_path % (floatingip), params=_params)

    @APIParamsCall
    def create_floatingip(self, body=None):
        """
        Creates a new floatingip
        """
        return self.post(self.floatingips_path, body=body)

    @APIParamsCall
    def update_floatingip(self, floatingip, body=None):
        """
        Updates a floatingip
        """
        return self.put(self.floatingip_path % (floatingip), body=body)

    @APIParamsCall
    def delete_floatingip(self, floatingip):
        """
        Deletes the specified floatingip
        """
        return self.delete(self.floatingip_path % (floatingip))
        
    ###Modifications by Srikanth
    @APIParamsCall
    def list_configurations(self, **_params):
        """
        Fetches a list of all configurations for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.configurations_path, params=_params)
        
    @APIParamsCall
    def create_configuration(self, body=None):
        """
        Creates a new configuration
        """
        return self.post(self.configurations_path, body=body)
        
    @APIParamsCall
    def delete_configuration(self, configuration):
        """
        Deletes the specified configuration
        """
        return self.delete(self.configuration_path % (configuration))
        
    @APIParamsCall
    def show_configuration(self, configuration, **_params):
        """
        Fetches information of a certain configuration
        """
        return self.get(self.configuration_path % (configuration), params=_params)
        
    @APIParamsCall
    def update_configuration(self, configuration, body=None):
        """
        Updates a configuration
        """
        return self.put(self.configuration_path % (configuration), body=body)

    @APIParamsCall
    def list_pools(self, **_params):
        """
        Fetches a list of all pools for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.pools_path, params=_params)
        
    @APIParamsCall
    def create_pool(self, body=None):
        """
        Creates a new pool
        """
        return self.post(self.pools_path, body=body)
        
    @APIParamsCall
    def delete_pool(self, pool):
        """
        Deletes the specified pool
        """
        return self.delete(self.pool_path % (pool))
        
    @APIParamsCall
    def show_pool(self, pool, **_params):
        """
        Fetches information of a certain pool
        """
        return self.get(self.pool_path % (pool), params=_params)
        
    @APIParamsCall
    def update_pool(self, pool, body=None):
        """
        Updates a pool
        """
        return self.put(self.pool_path % (pool), body=body)
        
    @APIParamsCall
    def list_members(self, **_params):
        """
        Fetches a list of all pool members for a pool/tenant
        """
        return self.get(self.members_path, params=_params)
        
    @APIParamsCall
    def create_member(self, body=None):
        """
        Creates a new member
        """
        return self.post(self.members_path, body=body)
        
    @APIParamsCall
    def delete_member(self, member):
        """
        Deletes the specified member
        """
        return self.delete(self.member_path % (member))
        
    @APIParamsCall
    def show_member(self, member, **_params):
        """
        Fetches information of a certain member
        """
        return self.get(self.member_path % (member), params=_params)
        
    @APIParamsCall
    def update_member(self, member, body=None):
        """
        Updates a member
        """
        return self.put(self.member_path % (member), body=body)
        
    ###Helath Monitors
    @APIParamsCall
    def list_monitors(self, **_params):
        """
        Fetches a list of all pool monitors for a pool/tenant
        """
        return self.get(self.monitors_path, params=_params)
        
    @APIParamsCall
    def create_monitor(self, body=None):
        """
        Creates a new monitor
        """
        return self.post(self.monitors_path, body=body)
        
    @APIParamsCall
    def delete_monitor(self, monitor):
        """
        Deletes the specified monitor
        """
        return self.delete(self.monitor_path % (monitor))
        
    @APIParamsCall
    def show_monitor(self, monitor, **_params):
        """
        Fetches information of a certain monitor
        """
        return self.get(self.monitor_path % (monitor), params=_params)
        
    @APIParamsCall
    def update_monitor(self, monitor, body=None):
        """
        Updates a monitor
        """
        return self.put(self.monitor_path % (monitor), body=body)
        
    ###Virtual IP's
    @APIParamsCall
    def list_vips(self, **_params):
        """
        Fetches a list of all pool vips for a pool/tenant
        """
        return self.get(self.vips_path, params=_params)
        
    @APIParamsCall
    def create_vip(self, body=None):
        """
        Creates a new vip
        """
        return self.post(self.vips_path, body=body)
        
    @APIParamsCall
    def delete_vip(self, vip):
        """
        Deletes the specified vip
        """
        return self.delete(self.vip_path % (vip))
        
    @APIParamsCall
    def show_vip(self, vip, **_params):
        """
        Fetches information of a certain vip
        """
        return self.get(self.vip_path % (vip), params=_params)
        
    @APIParamsCall
    def update_vip(self, vip, body=None):
        """
        Updates a vip
        """
        return self.put(self.vip_path % (vip), body=body)
        
    ###Session Persistance
    @APIParamsCall
    def list_sessions(self, **_params):
        """
        Fetches a list of all pool sessions for a pool/tenant
        """
        return self.get(self.sessions_path, params=_params)
        
    @APIParamsCall
    def create_session(self, body=None):
        """
        Creates a new session
        """
        return self.post(self.sessions_path, body=body)
        
    @APIParamsCall
    def delete_session(self, session):
        """
        Deletes the specified session
        """
        return self.delete(self.session_path % (session))
        
    @APIParamsCall
    def show_session(self, session, **_params):
        """
        Fetches information of a certain session
        """
        return self.get(self.session_path % (session), params=_params)
        
    @APIParamsCall
    def update_session(self, session, body=None):
        """
        Updates a session
        """
        return self.put(self.session_path % (session), body=body)
        
    @APIParamsCall
    def list_networkfunctions(self, **_params):
        """
        Fetches a list of all networkfunctions for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.networkfunctions_path, params=_params)
        
    @APIParamsCall
    def create_networkfunction(self, body=None):
        """
        Creates a new Networkfunction
        """
        return self.post(self.networkfunctions_path, body=body)
        
    @APIParamsCall
    def delete_networkfunction(self, networkfunction):
        """
        Deletes the specified networkfunction
        """
        return self.delete(self.networkfunction_path % (networkfunction))
    
    @APIParamsCall
    def show_networkfunction(self, networkfunction, **_params):
        """
        Fetches information of a certain networkfunction
        """
        return self.get(self.networkfunction_path % (networkfunction), params=_params)
        
    @APIParamsCall
    def update_networkfunction(self, networkfunction, body=None):
        """
        Updates a networkfunction
        """
        return self.put(self.networkfunction_path % (networkfunction), body=body)
    
    @APIParamsCall
    def list_categories(self, **_params):
        """
        Fetches a list of all categories for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.categories_path, params=_params)
        
    @APIParamsCall
    def create_category(self, body=None):
        """
        Creates a new Category
        """
        return self.post(self.categories_path, body=body)
        
    @APIParamsCall
    def delete_category(self, category):
        """
        Deletes the specified category
        """
        return self.delete(self.category_path % (category))
    
    @APIParamsCall
    def show_category(self, category, **_params):
        """
        Fetches information of a certain category
        """
        return self.get(self.category_path % (category), params=_params)
        
    @APIParamsCall
    def update_category(self, category, body=None):
        """
        Updates a category
        """
        return self.put(self.category_path % (category), body=body)
        
    @APIParamsCall
    def list_category_networkfunctions(self, **_params):
        """
        Fetches a list of all category_networkfunctions for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.category_networkfunctions_path, params=_params)
        
    @APIParamsCall
    def create_category_networkfunction(self, body=None):
        """
        Creates a new Category_networkfunction
        """
        return self.post(self.category_networkfunctions_path, body=body)
        
    @APIParamsCall
    def delete_category_networkfunction(self, category_networkfunction):
        """
        Deletes the specified category_networkfunction
        """
        return self.delete(self.category_networkfunction_path % (category_networkfunction))
    
    @APIParamsCall
    def show_category_networkfunction(self, category_networkfunction, **_params):
        """
        Fetches information of a certain category_networkfunction
        """
        return self.get(self.category_networkfunction_path % (category_networkfunction), params=_params)
        
    @APIParamsCall
    def update_category_networkfunction(self, category_networkfunction, body=None):
        """
        Updates a category_networkfunction
        """
        return self.put(self.category_networkfunction_path % (category_networkfunction), body=body)
        
    @APIParamsCall
    def list_vendors(self, **_params):
        """
        Fetches a list of all vendors for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.vendors_path, params=_params)
        
    @APIParamsCall
    def create_vendor(self, body=None):
        """
        Creates a new Vendor
        """
        return self.post(self.vendors_path, body=body)
        
    @APIParamsCall
    def delete_vendor(self, vendor):
        """
        Deletes the specified vendor
        """
        return self.delete(self.vendor_path % (vendor))
    
    @APIParamsCall
    def show_vendor(self, vendor, **_params):
        """
        Fetches information of a certain vendor
        """
        return self.get(self.vendor_path % (vendor), params=_params)
        
    @APIParamsCall
    def update_vendor(self, vendor, body=None):
        """
        Updates a vendor
        """
        return self.put(self.vendor_path % (vendor), body=body)
        
    @APIParamsCall
    def list_images(self, **_params):
        """
        Fetches a list of all images for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.images_path, params=_params)
        
    @APIParamsCall
    def create_image(self, body=None):
        """
        Creates a new Images
        """
        return self.post(self.images_path, body=body)
        
    @APIParamsCall
    def delete_image(self, image):
        """
        Deletes the specified image
        """
        return self.delete(self.image_path % (image))
    
    @APIParamsCall
    def show_image(self, image, **_params):
        """
        Fetches information of a certain image
        """
        return self.get(self.image_path % (image), params=_params)
        
    @APIParamsCall
    def update_image(self, image, body=None):
        """
        Updates a image
        """
        return self.put(self.image_path % (image), body=body)
        
    @APIParamsCall
    def list_metadatas(self, **_params):
        """
        Fetches a list of all metadatas for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.metadatas_path, params=_params)
        
    @APIParamsCall
    def create_metadata(self, body=None):
        """
        Creates a new Metadata
        """
        return self.post(self.metadatas_path, body=body)
        
    @APIParamsCall
    def delete_metadata(self, metadata):
        """
        Deletes the specified metadata
        """
        return self.delete(self.metadata_path % (metadata))
    
    @APIParamsCall
    def show_metadata(self, metadata, **_params):
        """
        Fetches information of a certain metadata
        """
        return self.get(self.metadata_path % (metadata), params=_params)
        
    @APIParamsCall
    def update_metadata(self, metadata, body=None):
        """
        Updates a metadata
        """
        return self.put(self.metadata_path % (metadata), body=body)
    @APIParamsCall
    def list_personalities(self, **_params):
        """
        Fetches a list of all personalities for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.personalities_path, params=_params)
        
    @APIParamsCall
    def create_personality(self, body=None):
        """
        Creates a new Personality
        """
        return self.post(self.personalities_path, body=body)
        
    @APIParamsCall
    def delete_personality(self, personality):
        """
        Deletes the specified personality
        """
        return self.delete(self.personality_path % (personality))
    
    @APIParamsCall
    def show_personality(self, personality, **_params):
        """
        Fetches information of a certain personality
        """
        return self.get(self.personality_path % (personality), params=_params)
        
    @APIParamsCall
    def update_personality(self, personality, body=None):
        """
        Updates a personality
        """
        return self.put(self.personality_path % (personality), body=body)
        
    @APIParamsCall
    def list_chains(self, **_params):
        """
        Fetches a list of all chains for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.chains_path, params=_params)
        
    @APIParamsCall
    def create_chain(self, body=None):
        """
        Creates a new chain
        """
        return self.post(self.chains_path, body=body)
        
    @APIParamsCall
    def delete_chain(self, chain):
        """
        Deletes the specified chain
        """
        return self.delete(self.chain_path % (chain))
    
    @APIParamsCall
    def show_chain(self, chain, **_params):
        """
        Fetches information of a certain chain
        """
        return self.get(self.chain_path % (chain), params=_params)
        
    @APIParamsCall
    def update_chain(self, chain, body=None):
        """
        Updates a chain
        """
        return self.put(self.chain_path % (chain), body=body)
        
    @APIParamsCall
    def list_chain_images(self, **_params):
        """
        Fetches a list of all chain_images for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.chain_images_path, params=_params)
        
    @APIParamsCall
    def create_chain_image(self, body=None):
        """
        Creates a new Chain_image
        """
        return self.post(self.chain_images_path, body=body)
        
    @APIParamsCall
    def delete_chain_image(self, chain_image):
        """
        Deletes the specified chain_image
        """
        return self.delete(self.chain_image_path % (chain_image))
    
    @APIParamsCall
    def show_chain_image(self, chain_image, **_params):
        """
        Fetches information of a certain chain_image
        """
        return self.get(self.chain_image_path % (chain_image), params=_params)
        
    @APIParamsCall
    def update_chain_image(self, chain_image, body=None):
        """
        Updates a chain_image
        """
        return self.put(self.chain_image_path % (chain_image), body=body)
        
    @APIParamsCall
    def list_chain_image_networks(self, **_params):
        """
        Fetches a list of all chain_image_networks for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.chain_image_networks_path, params=_params)
        
    @APIParamsCall
    def create_chain_image_network(self, body=None):
        """
        Creates a new Chain_image_network
        """
        return self.post(self.chain_image_networks_path, body=body)
        
    @APIParamsCall
    def delete_chain_image_network(self, chain_image_network):
        """
        Deletes the specified chain_image_network
        """
        return self.delete(self.chain_image_network_path % (chain_image_network))
    
    @APIParamsCall
    def show_chain_image_network(self, chain_image_network, **_params):
        """
        Fetches information of a certain chain_image_network
        """
        return self.get(self.chain_image_network_path % (chain_image_network), params=_params)
        
    @APIParamsCall
    def update_chain_image_network(self, chain_image_network, body=None):
        """
        Updates a chain_image_network
        """
        return self.put(self.chain_image_network_path % (chain_image_network), body=body)
        
    @APIParamsCall
    def list_chain_image_confs(self, **_params):
        """
        Fetches a list of all chain_image_confs for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.chain_image_confs_path, params=_params)
        
    @APIParamsCall
    def create_chain_image_conf(self, body=None):
        """
        Creates a new Chain_image_conf
        """
        return self.post(self.chain_image_confs_path, body=body)
        
    @APIParamsCall
    def delete_chain_image_conf(self, chain_image_conf):
        """
        Deletes the specified chain_image_conf
        """
        return self.delete(self.chain_image_conf_path % (chain_image_conf))
    
    @APIParamsCall
    def show_chain_image_conf(self, chain_image_conf, **_params):
        """
        Fetches information of a certain chain_image_conf
        """
        return self.get(self.chain_image_conf_path % (chain_image_conf), params=_params)
        
    @APIParamsCall
    def update_chain_image_conf(self, chain_image_conf, body=None):
        """
        Updates a chain_image_conf
        """
        return self.put(self.chain_image_conf_path % (chain_image_conf), body=body)
        
    @APIParamsCall
    def list_config_handles(self, **_params):
        """
        Fetches a list of all config_handles for a tenant
        """
        # Pass filters in "params" argument to do_request
        return self.get(self.config_handles_path, params=_params)
        
    @APIParamsCall
    def create_config_handle(self, body=None):
        """
        Creates a new Config_handle
        """
        return self.post(self.config_handles_path, body=body)
        
    @APIParamsCall
    def delete_config_handle(self, config_handle):
        """
        Deletes the specified config_handle
        """
        return self.delete(self.config_handle_path % (config_handle))
    
    @APIParamsCall
    def show_config_handle(self, config_handle, **_params):
        """
        Fetches information of a certain config_handle
        """
        return self.get(self.config_handle_path % (config_handle), params=_params)
        
    @APIParamsCall
    def update_config_handle(self, config_handle, body=None):
        """
        Updates a config_handle
        """
        return self.put(self.config_handle_path % (config_handle), body=body)
        
    @APIParamsCall
    def generate_slb_config(self, body=None):
        """
        Generate the specified configuration
        """
        return self.post(self.slb_configs_path, body=body)
        
    @APIParamsCall
    def launch_chain(self, launch, **_params):
        """
        Generate the specified configuration
        """       
        return self.get(self.launch_path % (launch), params=_params)

    def __init__(self, **kwargs):
        """ Initialize a new client for the Quantum v2.0 API. """
        super(Client, self).__init__()
        self.httpclient = HTTPClient(**kwargs)
        self.version = '2.0'
        self.format = 'json'
        self.action_prefix = "/v%s" % (self.version)
        self.retries = 0
        self.retry_interval = 1

    def _handle_fault_response(self, status_code, response_body):
        # Create exception with HTTP status code and message
        error_message = response_body
        _logger.debug("Error message: %s", error_message)
        # Add deserialized error message to exception arguments
        try:
            des_error_body = Serializer().deserialize(error_message,
                                                      self.content_type())
        except:
            # If unable to deserialized body it is probably not a
            # Quantum error
            des_error_body = {'message': error_message}
        # Raise the appropriate exception
        exception_handler_v20(status_code, des_error_body)

    def do_request(self, method, action, body=None, headers=None, params=None):
        # Add format and tenant_id
        action += ".%s" % self.format
        action = self.action_prefix + action
        if type(params) is dict and params:
            action += '?' + urllib.urlencode(params, doseq=1)
        if body:
            body = self.serialize(body)
        self.httpclient.content_type = self.content_type()
        resp, replybody = self.httpclient.do_request(action, method, body=body)
        status_code = self.get_status_code(resp)
        if status_code in (httplib.OK,
                           httplib.CREATED,
                           httplib.ACCEPTED,
                           httplib.NO_CONTENT):
            return self.deserialize(replybody, status_code)
        else:
            self._handle_fault_response(status_code, replybody)

    def get_status_code(self, response):
        """
        Returns the integer status code from the response, which
        can be either a Webob.Response (used in testing) or httplib.Response
        """
        if hasattr(response, 'status_int'):
            return response.status_int
        else:
            return response.status

    def serialize(self, data):
        """
        Serializes a dictionary with a single key (which can contain any
        structure) into either xml or json
        """
        if data is None:
            return None
        elif type(data) is dict:
            return Serializer().serialize(data, self.content_type())
        else:
            raise Exception("unable to serialize object of type = '%s'" %
                            type(data))

    def deserialize(self, data, status_code):
        """
        Deserializes an xml or json string into a dictionary
        """
        if status_code == 204:
            return data
        return Serializer(self._serialization_metadata).deserialize(
            data, self.content_type())

    def content_type(self, format=None):
        """
        Returns the mime-type for either 'xml' or 'json'.  Defaults to the
        currently set format
        """
        if not format:
            format = self.format
        return "application/%s" % (format)

    def retry_request(self, method, action, body=None,
                      headers=None, params=None):
        """
        Call do_request with the default retry configuration. Only
        idempotent requests should retry failed connection attempts.

        :raises: ConnectionFailed if the maximum # of retries is exceeded
        """
        max_attempts = self.retries + 1
        for i in xrange(max_attempts):
            try:
                return self.do_request(method, action, body=body,
                                       headers=headers, params=params)
            except exceptions.ConnectionFailed:
                # Exception has already been logged by do_request()
                if i < self.retries:
                    _logger.debug(_('Retrying connection to quantum service'))
                    time.sleep(self.retry_interval)

        raise exceptions.ConnectionFailed(reason=_("Maximum attempts reached"))

    def delete(self, action, body=None, headers=None, params=None):
        return self.retry_request("DELETE", action, body=body,
                                  headers=headers, params=params)

    def get(self, action, body=None, headers=None, params=None):
        return self.retry_request("GET", action, body=body,
                                  headers=headers, params=params)

    def post(self, action, body=None, headers=None, params=None):
        # Do not retry POST requests to avoid the orphan objects problem.
        return self.do_request("POST", action, body=body,
                               headers=headers, params=params)

    def put(self, action, body=None, headers=None, params=None):
        return self.retry_request("PUT", action, body=body,
                                  headers=headers, params=params)

#if __name__ == '__main__':
#
#    client20 = Client(username='admin',
#                      password='password',
#                      auth_url='http://localhost:5000/v2.0',
#                      tenant_name='admin')
#    client20 = Client(token='ec796583fcad4aa690b723bc0b25270e',
#                      endpoint_url='http://localhost:9696')
#
#    client20.tenant = 'default'
#    client20.format = 'json'
#    nets = client20.list_networks()
#    print nets
