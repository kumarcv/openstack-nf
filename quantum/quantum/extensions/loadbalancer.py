# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

import abc

from quantum.extensions import extensions
from quantum.api.v2 import attributes as attr
from quantum.api.v2 import base
from quantum.common import exceptions as qexception
from quantum import manager
from quantum.plugins.common import constants
from quantum.plugins.services.service_base import ServicePluginBase

import logging
LOG = logging.getLogger(__name__)

RESOURCE_ATTRIBUTE_MAP = {
    'pools': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'description': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'subnet_id': {'allow_post': True, 'allow_put': True,
                       'required_by_policy': True,
                       'validate': {'type:string': None},
                       'is_visible': True},
        'protocol': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'lb_method': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'status': {'allow_post': False, 'allow_put': False,
                   'is_visible': True},
        'admin_status': {'allow_post': False, 'allow_put': False,
                   'is_visible': True},
        'subnet': {'allow_post': False, 'allow_put': False,
                             'default': attr.ATTR_NOT_SPECIFIED,
                             'validate': {'type:string': None},
                             'is_visible': True},
    },
    'members': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'ip_address': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:ip_address': None},
                 'is_visible': True},
        'port_no': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'weight': {'allow_post': True, 'allow_put': True,
                   'default': 1,
                   'validate': {'type:string': None},
                   'is_visible': True},
        'pool_id': {'allow_post': True, 'allow_put': True,
                    'validate': {'type:string': None},
                    'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'admin_status': {'allow_post': False, 'allow_put': False,
                   'is_visible': True},
        'status': {'allow_post': False, 'allow_put': False,
                   'is_visible': True},
    },
    'monitors': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'type': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'delay': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'timeout': {'allow_post': True, 'allow_put': True,
                   'validate': {'type:string': None},
                   'is_visible': True},
        'max_retries': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'http_method': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'url_path': {'allow_post': True, 'allow_put': True,
                   'validate': {'type:string': None},
                   'is_visible': True},
        'expected_codes': {'allow_post': True, 'allow_put': True,
                   'validate': {'type:string': None},
                   'is_visible': True},
        'pool_id': {'allow_post': True, 'allow_put': True,
                    'validate': {'type:string': None},
                    'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'admin_status': {'allow_post': False, 'allow_put': False,
                   'is_visible': True},
        'status': {'allow_post': False, 'allow_put': False,
                   'is_visible': True},
    },
    'vips': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'description': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'port_no': {'allow_post': True, 'allow_put': True,
                   'validate': {'type:string': None},
                   'is_visible': True},
        'protocol': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'connection_limit': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'config_handle_id': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'session_persistance_id': {'allow_post': True, 'allow_put': True,
                   'validate': {'type:string': None},
                   'is_visible': True},
        'pool_id': {'allow_post': True, 'allow_put': True,
                    'validate': {'type:string': None},
                    'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'admin_status': {'allow_post': False, 'allow_put': False,
                   'is_visible': True},
        'status': {'allow_post': False, 'allow_put': False,
                   'is_visible': True},
        'session_persistance_type': {'allow_post': False, 'allow_put': False,
                             'default': attr.ATTR_NOT_SPECIFIED,
                             'validate': {'type:string': None},
                             'is_visible': True},
        'session_persistance_cookie': {'allow_post': False, 'allow_put': False,
                             'default': attr.ATTR_NOT_SPECIFIED,
                             'validate': {'type:string': None},
                             'is_visible': True},
    },
    'sessions': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'type': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
        'cookie_name': {'allow_post': True, 'allow_put': True, 'default': '',
                 'validate': {'type:string': None},
                 'is_visible': True},
    },
    'configs': {
        'config_handle_id': {'allow_post': True, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'data': {'allow_post': False, 'allow_put': False,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'slug': {'allow_post': True, 'allow_put': False,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'version': {'allow_post': True, 'allow_put': False,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'header': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
     },
}


#SUB_RESOURCE_ATTRIBUTE_MAP = {
#    'monitors': {
#        'parent': {'collection_name': 'pools',
#                   'member_name': 'pool'},
#        'parameters': {'id': {'allow_post': True, 'allow_put': False,
#                              'validate': {'type:uuid': None},
#                              'is_visible': True},
#                       'tenant_id': {'allow_post': True, 'allow_put': False,
#                                     'validate': {'type:string': None},
#                                     'required_by_policy': True,
#                                     'is_visible': True},
#                       }
#    }
#}


class Loadbalancer(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "LoadBalancing service"

    @classmethod
    def get_alias(cls):
        return "lbaas"

    @classmethod
    def get_description(cls):
        return "Extension for LoadBalancing service"

    @classmethod
    def get_namespace(cls):
        return "http://wiki.openstack.org/Quantum/LBaaS/API_1.0"

    @classmethod
    def get_updated(cls):
        return "2012-10-07T10:00:00-00:00"

    @classmethod
    def get_resources(cls):
        my_plurals = [(key, key[:-1]) for key in RESOURCE_ATTRIBUTE_MAP.keys()]
        attr.PLURALS.update(dict(my_plurals))
        resources = []
        plugin = manager.QuantumManager.get_service_plugins()[
            constants.LOADBALANCER]
        for collection_name in RESOURCE_ATTRIBUTE_MAP:
            # Special handling needed for resources with 'y' ending
            # (e.g. proxies -> proxy)
            resource_name = collection_name[:-1]
            params = RESOURCE_ATTRIBUTE_MAP[collection_name]

            member_actions = {}
            if resource_name == 'pool':
                member_actions = {'stats': 'GET'}

            controller = base.create_resource(collection_name,
                                              resource_name,
                                              plugin, params,
                                              member_actions=member_actions)

            resource = extensions.ResourceExtension(
                collection_name,
                controller,
                path_prefix=constants.COMMON_PREFIXES[constants.LOADBALANCER],
                member_actions=member_actions,
                attr_map=params)
            resources.append(resource)

        #for collection_name in SUB_RESOURCE_ATTRIBUTE_MAP:
        #    # Special handling needed for sub-resources with 'y' ending
        #    # (e.g. proxies -> proxy)
        #    resource_name = collection_name[:-1]
        #    parent = SUB_RESOURCE_ATTRIBUTE_MAP[collection_name].get('parent')
        #    params = SUB_RESOURCE_ATTRIBUTE_MAP[collection_name].get(
        #        'parameters')
        #
        #    controller = base.create_resource(collection_name, resource_name,
        #                                      plugin, params,
        #                                      allow_bulk=True,
        #                                      parent=parent)
        #
        #    resource = extensions.ResourceExtension(
        #        collection_name,
        #        controller, parent,
        #        path_prefix=constants.COMMON_PREFIXES[constants.LOADBALANCER],
        #        attr_map=params)
        #    resources.append(resource)

        return resources

    @classmethod
    def get_plugin_interface(cls):
        return LoadbalancerPluginBase


class LoadbalancerPluginBase(ServicePluginBase):
    __metaclass__ = abc.ABCMeta

    def get_plugin_name(self):
        return constants.LOADBALANCER

    def get_plugin_type(self):
        return constants.LOADBALANCER

    def get_plugin_description(self):
        return 'LoadBalancer service plugin'

    @abc.abstractmethod
    def get_vips(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_vip(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_vip(self, context, vip):
        pass

    @abc.abstractmethod
    def update_vip(self, context, id, vip):
        pass

    @abc.abstractmethod
    def delete_vip(self, context, id):
        pass

    @abc.abstractmethod
    def get_pools(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_pool(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_pool(self, context, pool):
        pass

    @abc.abstractmethod
    def update_pool(self, context, id, pool):
        pass

    @abc.abstractmethod
    def delete_pool(self, context, id):
        pass

    @abc.abstractmethod
    def get_members(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_member(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_member(self, context, member):
        pass

    @abc.abstractmethod
    def update_member(self, context, id, member):
        pass

    @abc.abstractmethod
    def delete_member(self, context, id):
        pass

    @abc.abstractmethod
    def get_monitors(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_monitor(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_monitor(self, context, health_monitor):
        pass

    @abc.abstractmethod
    def update_monitor(self, context, id, health_monitor):
        pass

    @abc.abstractmethod
    def delete_monitor(self, context, id):
        pass
    
    @abc.abstractmethod
    def create_config(self, context, config):
        pass
