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


NWSERVICES_PLURALS = {
    'networkfunctions': 'networkfunction',
    'categories': 'category',
    'vendors': 'vendor',
    'images': 'image',
    'personalities': 'personality',
    'metadatas': 'metadata',
    'chains': 'chain',
    'chain_images': 'chain_image',
    'chain_image_confs': 'chain_image_conf',
    'chain_image_networks': 'chain_image_network',
    'category_networkfunctions': 'category_networkfunction',
    'config_handles': 'config_handle',
    'launchs': 'launch'
}

RESOURCE_ATTRIBUTE_MAP = {
    'networkfunctions': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'description': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        attr.SHARED: {'allow_post': True,
                 'allow_put': True,
                 'default': False,
                 'convert_to': attr.convert_to_boolean,
                 'is_visible': True,
                 'required_by_policy': True,
                 'enforce_policy': True},
    },
    'categories': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'description': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        attr.SHARED: {'allow_post': True,
                 'allow_put': True,
                 'default': False,
                 'convert_to': attr.convert_to_boolean,
                 'is_visible': True,
                 'required_by_policy': True,
                 'enforce_policy': True},
        
    },
    'category_networkfunctions': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'category_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'networkfunction_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
                
    },
    'vendors': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'description': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        attr.SHARED: {'allow_post': True,
                 'allow_put': True,
                 'default': False,
                 'convert_to': attr.convert_to_boolean,
                 'is_visible': True,
                 'required_by_policy': True,
                 'enforce_policy': True},
    },
    'images': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'category_id': {'allow_post': True, 'allow_put': False,
                       'required_by_policy': True,
                       'validate': {'type:regex': attr.UUID_PATTERN},
                       'is_visible': True},
        'image_map_categories': {'allow_post': False, 'allow_put': False,
                    'default': [],
                    'is_visible': True},
        'vendor_id': {'allow_post': True, 'allow_put': False,
                       'required_by_policy': True,
                       'validate': {'type:regex': attr.UUID_PATTERN},
                       'is_visible': True},
        'image_map_vendors': {'allow_post': False, 'allow_put': False,
                    'default': [],
                    'is_visible': True},
        'image_id': {'allow_post': True, 'allow_put': False,
                       'required_by_policy': True,
                       'validate': {'type:regex': attr.UUID_PATTERN},
                       'is_visible': True},
        'flavor_id': {'allow_post': True, 'allow_put': False,
                       'required_by_policy': True,
                       'is_visible': True},
        'security_group_id': {'allow_post': True, 'allow_put': False,
                       'required_by_policy': True,
                       'is_visible': True},
        attr.SHARED: {'allow_post': True,
                 'allow_put': True,
                 'default': False,
                 'convert_to': attr.convert_to_boolean,
                 'is_visible': True,
                 'required_by_policy': True,
                 'enforce_policy': True},
    },
    'metadatas': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'value': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'image_map_id': {'allow_post': True, 'allow_put': False,
                       'required_by_policy': True,
                       'validate': {'type:regex': attr.UUID_PATTERN},
                       'is_visible': True},
    },
    'personalities': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'file_path': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'file_content': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'image_map_id': {'allow_post': True, 'allow_put': False,
                       'required_by_policy': True,
                       'validate': {'type:regex': attr.UUID_PATTERN},
                       'is_visible': True},
    },
    'chains': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'type': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'auto_boot': {'allow_post': True, 'allow_put': True,
                       'required_by_policy': True,
                       'is_visible': True},
    },
    'chain_images': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'chain_id': {'allow_post': True, 'allow_put': True,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'image_map_id': {'allow_post': True, 'allow_put': True,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'chain_image_map': {'allow_post': False, 'allow_put': True,
                    'default': [],
                    'is_visible': True},
        'sequence_number': {'allow_post': True, 'allow_put': True,
                       'required_by_policy': True,
                       'is_visible': True},
        'instance_uuid': {'allow_post': True, 'allow_put': True,
                      'validate': {'type:string': None},
                      'default': '', 'is_visible': True},
        'instance_id': {'allow_post': True, 'allow_put': True,
                       'default': '', 'is_visible': True},
        'chain_image_networks': {'allow_post': False, 'allow_put': False,
                    'default': [],
                    'is_visible': True},
        'chain_image_confs': {'allow_post': False, 'allow_put': False,
                    'default': [],
                    'is_visible': True},
    },
    'chain_image_networks': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'image_map_networks': {'allow_post': False, 'allow_put': False,
                    'default': [],
                    'is_visible': True},
        'chain_map_id': {'allow_post': True, 'allow_put': True,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'network_id': {'allow_post': True, 'allow_put': True,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
    },
    'chain_image_confs': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'chain_map_id': {'allow_post': True, 'allow_put': True,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'config_handle_id': {'allow_post': True, 'allow_put': True,
                      'validate': {'type:string': None},
                      'default': '', 'is_visible': True},
        'networkfunction_id': {'allow_post': True, 'allow_put': True,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
    },
    'config_handles': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'tenant_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'networkfunction_id': {'allow_post': True, 'allow_put': False,
                      'validate': {'type:string': None},
                      'required_by_policy': True,
                      'is_visible': True},
        'status': {'allow_post': True, 'allow_put': True,
                   'default': '', 'is_visible': True},
        'slug': {'allow_post': True, 'allow_put': True,
                   'default': '', 'is_visible': True},
                
    },
    'launchs': {
        'config_handle_id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:regex': attr.UUID_PATTERN},
               'is_visible': True},
        'header': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'default': '', 'is_visible': True},
        'slug': {'allow_post': True, 'allow_put': True,
                'validate': {'type:string': None},
                'default': '', 'is_visible': True},
        'version': {'allow_post': True, 'allow_put': True,
                'validate': {'type:string': None},
                'default': '', 'is_visible': True},
            
    },
}


class Nwservices(extensions.ExtensionDescriptor):

    @classmethod
    def get_name(cls):
        return "Network service"

    @classmethod
    def get_alias(cls):
        return "fns"

    @classmethod
    def get_description(cls):
        return "Extension for Network services"

    @classmethod
    def get_namespace(cls):
        return "http://wiki.openstack.org/Quantum/LBaaS/API_1.0"

    @classmethod
    def get_updated(cls):
        return "2012-10-07T10:00:00-00:00"

    @classmethod
    def get_resources(cls):
        #my_plurals = [(key, key[:-1]) for key in RESOURCE_ATTRIBUTE_MAP.keys()]
        #attr.PLURALS.update(dict(my_plurals))
        attr.PLURALS.update(NWSERVICES_PLURALS)
        resources = []
        plugin = manager.QuantumManager.get_service_plugins()[
            constants.NWSERVICES]
        for collection_name in RESOURCE_ATTRIBUTE_MAP:
            # Special handling needed for resources with 'y' ending
            # (e.g. proxies -> proxy)
            resource_name = NWSERVICES_PLURALS[collection_name]
            params = RESOURCE_ATTRIBUTE_MAP[collection_name]

            member_actions = {}

            controller = base.create_resource(collection_name,
                                              resource_name,
                                              plugin, params,
                                              member_actions=member_actions)

            resource = extensions.ResourceExtension(
                collection_name,
                controller,
                path_prefix=constants.COMMON_PREFIXES[constants.NWSERVICES],
                member_actions=member_actions,
                attr_map=params)
            resources.append(resource)

        return resources

    @classmethod
    def get_plugin_interface(cls):
        return NwservicesPluginBase


class NwservicesPluginBase(ServicePluginBase):
    __metaclass__ = abc.ABCMeta

    def get_plugin_name(self):
        return constants.NWSERVICES

    def get_plugin_type(self):
        return constants.NWSERVICES

    def get_plugin_description(self):
        return 'Network service plugin'

    @abc.abstractmethod
    def get_networkfunctions(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_networkfunction(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_networkfunction(self, context, networkfunction):
        pass

    @abc.abstractmethod
    def update_networkfunction(self, context, id, networkfunction):
        pass

    @abc.abstractmethod
    def delete_networkfunction(self, context, id):
        pass
    
    @abc.abstractmethod
    def get_categories(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_category(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_category(self, context, category):
        pass

    @abc.abstractmethod
    def update_category(self, context, id, category):
        pass

    @abc.abstractmethod
    def delete_category(self, context, id):
        pass

    @abc.abstractmethod
    def get_category_networkfunctions(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_category_networkfunction(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_category_networkfunction(self, context, category_networkfunction):
        pass

    @abc.abstractmethod
    def update_category_networkfunction(self, context, id, category_networkfunction):
        pass

    @abc.abstractmethod
    def delete_category_networkfunction(self, context, id):
        pass
    
    @abc.abstractmethod
    def get_vendors(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_vendor(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_vendor(self, context, vendor):
        pass

    @abc.abstractmethod
    def update_vendor(self, context, id, vendor):
        pass

    @abc.abstractmethod
    def delete_vendor(self, context, id):
        pass
    
    @abc.abstractmethod
    def get_images(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_image(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_image(self, context, image):
        pass

    @abc.abstractmethod
    def update_image(self, context, id, image):
        pass

    @abc.abstractmethod
    def delete_image(self, context, id):
        pass
    
    @abc.abstractmethod
    def get_metadatas(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_metadata(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_metadata(self, context, metadata):
        pass

    @abc.abstractmethod
    def update_metadata(self, context, id, metadata):
        pass

    @abc.abstractmethod
    def delete_metadata(self, context, id):
        pass
    
    @abc.abstractmethod
    def get_personalities(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_personality(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_personality(self, context, personality):
        pass

    @abc.abstractmethod
    def update_personality(self, context, id, personality):
        pass

    @abc.abstractmethod
    def delete_personality(self, context, id):
        pass
    
    @abc.abstractmethod
    def get_chains(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_chain(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_chain(self, context, chain):
        pass

    @abc.abstractmethod
    def update_chain(self, context, id, chain):
        pass

    @abc.abstractmethod
    def delete_chain(self, context, id):
        pass
    
    @abc.abstractmethod
    def get_chain_images(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_chain_image(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_chain_image(self, context, chain_image):
        pass

    @abc.abstractmethod
    def update_chain_image(self, context, id, chain_image):
        pass

    @abc.abstractmethod
    def delete_chain_image(self, context, id):
        pass
    
    @abc.abstractmethod
    def get_chain_image_networks(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_chain_image_network(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_chain_image_network(self, context, chain_image_network):
        pass

    @abc.abstractmethod
    def update_chain_image_network(self, context, id, chain_image_network):
        pass

    @abc.abstractmethod
    def delete_chain_image_network(self, context, id):
        pass
    
    @abc.abstractmethod
    def get_chain_image_confs(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_chain_image_conf(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_chain_image_conf(self, context, chain_image_conf):
        pass

    @abc.abstractmethod
    def update_chain_image_conf(self, context, id, chain_image_conf):
        pass

    @abc.abstractmethod
    def delete_chain_image_conf(self, context, id):
        pass
    
    @abc.abstractmethod
    def get_config_handles(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def get_config_handle(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_config_handle(self, context, config_handle):
        pass

    @abc.abstractmethod
    def update_config_handle(self, context, id, config_handle):
        pass

    @abc.abstractmethod
    def delete_config_handle(self, context, id):
        pass
    
    @abc.abstractmethod
    def get_launch(self, context, id, fields=None):
        pass
    
    
    
    
    
