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

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import exc
import netaddr

from quantum.api.v2 import attributes
from quantum.common import exceptions as q_exc
from quantum.db import api as qdbapi
from quantum.db import model_base
from quantum.db import models_v2
from quantum.extensions import nwservices
from quantum.openstack.common import log as logging
from quantum.openstack.common import uuidutils
from quantum.plugins.common import constants
from quantum.common import utils
from quantum.openstack.common import timeutils
from quantum.db import db_base_plugin_v2

LOG = logging.getLogger(__name__)

############    
#Network Service  Tables added by Veera
############
class HasTenant(object):
    """Tenant mixin, add to subclasses that have a tenant."""
    # NOTE(jkoelker) tenant_id is just a free form string ;(
    tenant_id = sa.Column(sa.String(255))


class HasId(object):
    """id mixin, add to subclasses that have an id."""
    id = sa.Column(sa.String(36), primary_key=True, default=utils.str_uuid)
    
class ns_categorie(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 quantum FSL service."""
    name = sa.Column(sa.String(50), nullable=False)
    description = sa.Column(sa.String(255))
    shared = sa.Column(sa.Boolean)

class ns_networkfunction(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 quantum FSL service."""
    name = sa.Column(sa.String(50), nullable=False)
    description = sa.Column(sa.String(255))
    shared = sa.Column(sa.Boolean)
    
class ns_category_networkfunction(model_base.BASEV2, HasId):
    """Represents a v2 quantum FSL service."""
    category_id = sa.Column(sa.String(36), sa.ForeignKey('ns_categories.id', ondelete="CASCADE"), nullable=False)
    networkfunction_id = sa.Column(sa.String(36), sa.ForeignKey('ns_networkfunctions.id'), nullable=False)

class ns_vendor(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 quantum FSL service."""
    name = sa.Column(sa.String(50), nullable=False)
    description = sa.Column(sa.String(255))
    shared = sa.Column(sa.Boolean)
    
class ns_image_map(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 quantum FSL service."""
    name = sa.Column(sa.String(50), nullable=False)
    category_id = sa.Column(sa.String(36), sa.ForeignKey('ns_categories.id'), nullable=False)
    vendor_id = sa.Column(sa.String(36), sa.ForeignKey('ns_vendors.id'), nullable=False)
    image_id = sa.Column(sa.String(36), nullable=False)
    flavor_id = sa.Column(sa.Integer, nullable=False)
    security_group_id = sa.Column(sa.Integer, nullable=False)
    shared = sa.Column(sa.Boolean)
    image_map_categories = orm.relationship(ns_categorie,
                                        backref='ns_image_map',
                                        lazy="dynamic")
    image_map_vendors = orm.relationship(ns_vendor,
                                        backref='ns_image_map',
                                        lazy="dynamic")
    
class ns_metadata(model_base.BASEV2, HasId):
    """Represents a v2 quantum FSL service."""
    name = sa.Column(sa.String(50), nullable=False)
    value = sa.Column(sa.String(255), nullable=False)
    image_map_id = sa.Column(sa.String(36), sa.ForeignKey('ns_image_maps.id', ondelete="CASCADE"), nullable=False)
   
   
class ns_personalitie(model_base.BASEV2, HasId):
    """Represents a v2 quantum FSL service."""
    file_path = sa.Column(sa.String(255), nullable=False)
    file_content = sa.Column(sa.String(255), nullable=False)
    image_map_id = sa.Column(sa.String(36), sa.ForeignKey('ns_image_maps.id', ondelete="CASCADE"), nullable=False)
    
    
    
class ns_chain(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 quantum FSL service."""
    name = sa.Column(sa.String(50), nullable=False)
    type = sa.Column(sa.String(50), nullable=False)
    auto_boot = sa.Column(sa.Boolean)

class ns_chain_network_associate(model_base.BASEV2, HasId):
    """Represents a v2 quantum FSL service."""
    name = sa.Column(sa.String(50))
    chain_map_id = sa.Column(sa.String(36), sa.ForeignKey('ns_chain_image_maps.id'), nullable=False)
    network_id = sa.Column(sa.String(36), sa.ForeignKey('networks.id'), nullable=False)
    image_map_networks = orm.relationship(models_v2.Network,
                                        backref='ns_chain_network_associate',
                                        lazy="dynamic")
    

class ns_chain_configuration_associate(model_base.BASEV2, HasId):
    """Represents a v2 quantum FSL service."""
    name = sa.Column(sa.String(50))
    networkfunction_id = sa.Column(sa.String(36), sa.ForeignKey('ns_networkfunctions.id'), nullable=False)
    chain_map_id = sa.Column(sa.String(36), sa.ForeignKey('ns_chain_image_maps.id'), nullable=False)
    config_handle_id = sa.Column(sa.String(36))
   
    

class ns_chain_image_map(model_base.BASEV2, HasId):
    """Represents a v2 quantum FSL service."""
    name = sa.Column(sa.String(50), nullable=False)
    chain_id = sa.Column(sa.String(36), sa.ForeignKey('ns_chains.id'), nullable=False)
    image_map_id = sa.Column(sa.String(36), sa.ForeignKey('ns_image_maps.id'), nullable=False)
    sequence_number = sa.Column(sa.Integer)
    instance_uuid = sa.Column(sa.String(36))
    instance_id = sa.Column(sa.Integer)
    chain_image_map = orm.relationship(ns_image_map,
                                        backref='ns_chain_image_map',
                                        lazy="dynamic")
    chain_image_networks = orm.relationship(ns_chain_network_associate, backref='ns_chain_image_maps')
    chain_image_confs = orm.relationship(ns_chain_configuration_associate, backref='ns_chain_image_maps')
        

class ns_config_handle(model_base.BASEV2, HasId, HasTenant):
    """Represents a v2 quantum FSL service."""
    name = sa.Column(sa.String(50))
    networkfunction_id = sa.Column(sa.String(36), sa.ForeignKey('ns_networkfunctions.id'), nullable=False) 
    status = sa.Column(sa.Boolean)
    slug = sa.Column(sa.String(255))
    

    
class ns_version(model_base.BASEV2):
    id = sa.Column(sa.Integer(), primary_key=True, autoincrement=True)
    runtime_version = sa.Column(sa.String(50),
                                nullable=False)
    
class ns_delta(model_base.BASEV2, HasId):
    main_table_name = sa.Column(sa.String(50),
                                nullable=False)
    link_id = sa.Column(sa.Integer())
    old_value = sa.Column(sa.String(50))
    new_value = sa.Column(sa.String(50))
    version_id = sa.Column(sa.Integer(), sa.ForeignKey('ns_versions.id'),
                           nullable=False)
    date_time = sa.Column(sa.DateTime(), default=timeutils.utcnow)    
    user_id = sa.Column(sa.String(50), nullable=False)
    operation = sa.Column(sa.String(50), nullable=False)
    
   

class NwservicePluginDb(db_base_plugin_v2.QuantumDbPluginV2):
    """
    A class that wraps the implementation of the Quantum
    nwservices plugin database access interface using SQLAlchemy models.

    As opposed to all other DB plugins NwServicePluginDb does not
    implement plugin interface. nwservicesPlugin follows "has-a" instead of
    "is-a" relation with db-plugin. The main reason is that Db plugin is
    called not only by plugin, but also by notify handler and direct calls
    are a logical way.
    """

    

    
    
    ########################################################
    # MWS MODIFICATIONS
    
    def _make_networkfunction_dict(self, networkfunction, fields=None):
        res = {'id': networkfunction['id'],
               'name': networkfunction['name'],
               'tenant_id': networkfunction['tenant_id'],
               'description': networkfunction['description'],
               'shared': networkfunction['shared']}

        return self._fields(res, fields)
    
    def get_networkfunction(self, context, id, fields=None):
        networkfunction = self._get_networkfunction(context, id)
        return self._make_networkfunction_dict(networkfunction, fields)
        
    def get_networkfunctions(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_networkfunction,
                                    self._make_networkfunction_dict,
                                    filters=filters, fields=fields)
        
        
    def create_networkfunction(self, context, networkfunction):
        n = networkfunction['networkfunction']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            networkfunction = ns_networkfunction(tenant_id=tenant_id,
                                        id=n.get('id') or utils.str_uuid(),
                                        name=n['name'],
                                        description=n['description'],
                                        shared=n['shared'])
            context.session.add(networkfunction)
        return self._make_networkfunction_dict(networkfunction)
    
    def _get_networkfunction(self, context, id):
        try:
            networkfunction = self._get_by_id(context, ns_networkfunction, id)
        except exc.NoResultFound:
            # NOTE(jkoelker) The PortNotFound exceptions requires net_id
            #                kwarg in order to set the message correctly
            raise q_exc.NetworkfunctionNotFound(networkfunction_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Networkfunctions match for %s' % id)
            raise q_exc.NetworkfunctionNotFound(networkfunction_id=id)
        return networkfunction
    
    def delete_networkfunction(self, context, id):
        networkfunction = self._get_networkfunction(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(networkfunction)
            
    def update_networkfunction(self, context, id, networkfunction):
        n = networkfunction['networkfunction']
        with context.session.begin(subtransactions=True):
            networkfunction = self._get_networkfunction(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, networkfunction, n)
            networkfunction.update(n)
          
        return self._make_networkfunction_dict(networkfunction)    
        
    def _make_category_dict(self, category, fields=None):
        res = {'id': category['id'],
               'name': category['name'],
               'tenant_id': category['tenant_id'],
               'description': category['description'],
               'shared': category['shared']}

        return self._fields(res, fields)
    
    def get_category(self, context, id, fields=None):
        category = self._get_category(context, id)
        return self._make_category_dict(category, fields)
        
    def get_categories(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_categorie,
                                    self._make_category_dict,
                                    filters=filters, fields=fields)
        
        
    def create_category(self, context, category):
        n = category['category']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            category = ns_categorie(tenant_id=tenant_id,
                                        id=n.get('id') or utils.str_uuid(),
                                        name=n['name'],
                                        description=n['description'],
                                        shared=n['shared'])
            context.session.add(category)
        return self._make_category_dict(category)
    
    def _get_category(self, context, id):
        try:
            category = self._get_by_id(context, ns_categorie, id)
        except exc.NoResultFound:
            # NOTE(jkoelker) The PortNotFound exceptions requires net_id
            #                kwarg in order to set the message correctly
            raise q_exc.CategoryNotFound(category_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Categories match for %s' % id)
            raise q_exc.CategoryNotFound(category_id=id)
        return category
    
    def delete_category(self, context, id):
        category = self._get_category(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(category)
            
    def update_category(self, context, id, category):
        n = category['category']
        with context.session.begin(subtransactions=True):
            category = self._get_category(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, category, n)
            category.update(n)
          
        return self._make_category_dict(category)
        
        
    def _make_category_networkfunction_dict(self, category_networkfunction, fields=None):
        res = {'id': category_networkfunction['id'],
               'category_id': category_networkfunction['category_id'],
               'networkfunction_id': category_networkfunction['networkfunction_id']}

        return self._fields(res, fields)
    
    def get_category_networkfunction(self, context, id, fields=None):
        category_networkfunction = self._get_category_networkfunction(context, id)
        return self._make_category_networkfunction_dict(category_networkfunction, fields)
        
    def get_category_networkfunctions(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_category_networkfunction,
                                    self._make_category_networkfunction_dict,
                                    filters=filters, fields=fields)
        
        
    def create_category_networkfunction(self, context, category_networkfunction):
        n = category_networkfunction['category_networkfunction']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            category_networkfunction = ns_category_networkfunction(id=n.get('id') or utils.str_uuid(),
                                            category_id=n['category_id'],
                                            networkfunction_id=n['networkfunction_id'])
            context.session.add(category_networkfunction)
        return self._make_category_networkfunction_dict(category_networkfunction)
    
    def _get_category_networkfunction(self, context, id):
        try:
            category_networkfunction = self._get_by_id(context, ns_category_networkfunction, id)
        except exc.NoResultFound:
            # NOTE(jkoelker) The PortNotFound exceptions requires net_id
            #                kwarg in order to set the message correctly
            raise q_exc.Category_networkfunctionNotFound(category_networkfunction_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Category_networkfunctions match for %s' % id)
            raise q_exc.Category_networkfunctionNotFound(category_networkfunction_id=id)
        return category_networkfunction
    
    def delete_category_networkfunction(self, context, id):
        category_networkfunction = self._get_category_networkfunction(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(category_networkfunction)
            
    def update_category_networkfunction(self, context, id, category_networkfunction):
        n = category_networkfunction['category_networkfunction']
        with context.session.begin(subtransactions=True):
            category_networkfunction = self._get_category_networkfunction(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, category_networkfunction, n)
            category_networkfunction.update(n)
          
        return self._make_category_networkfunction_dict(category_networkfunction)
        
    def _make_vendor_dict(self, vendor, fields=None):
        res = {'id': vendor['id'],
               'name': vendor['name'],
               'tenant_id': vendor['tenant_id'],
               'description': vendor['description'],
               'shared': vendor['shared']}

        return self._fields(res, fields)
    
    def get_vendor(self, context, id, fields=None):
        vendor = self._get_vendor(context, id)
        return self._make_vendor_dict(vendor, fields)
        
    def get_vendors(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_vendor,
                                    self._make_vendor_dict,
                                    filters=filters, fields=fields)
        
        
    def create_vendor(self, context, vendor):
        n = vendor['vendor']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            vendor = ns_vendor(tenant_id=tenant_id,
                                        id=n.get('id') or utils.str_uuid(),
                                        name=n['name'],
                                        description=n['description'],
                                        shared=n['shared'])
            context.session.add(vendor)
        return self._make_vendor_dict(vendor)
    
    def _get_vendor(self, context, id):
        try:
            vendor = self._get_by_id(context, ns_vendor, id)
        except exc.NoResultFound:
            # NOTE(jkoelker) The PortNotFound exceptions requires net_id
            #                kwarg in order to set the message correctly
            raise q_exc.VendorNotFound(vendor_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Vendors match for %s' % id)
            raise q_exc.VendorNotFound(vendor_id=id)
        return vendor
    
    def delete_vendor(self, context, id):
        vendor = self._get_vendor(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(vendor)
            
    def update_vendor(self, context, id, vendor):
        n = vendor['vendor']
        with context.session.begin(subtransactions=True):
            vendor = self._get_vendor(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, vendor, n)
            vendor.update(n)
          
        return self._make_vendor_dict(vendor)
        
    def _make_image_dict(self, image, fields=None):
        for ven in image['image_map_vendors']:
            vendor_name = str(ven['name'])
        for cat in image['image_map_categories']:
            cat_name = str(cat['name'])
        res = {'id': image['id'],
               'name': image['name'],
               'tenant_id': image['tenant_id'],
               'category_id': image['category_id'],
               'vendor_id': image['vendor_id'],
               'image_id': image['image_id'],
               'flavor_id': image['flavor_id'],
               'security_group_id': image['security_group_id'],
               'shared': image['shared'],
               'image_map_categories': cat_name,
               'image_map_vendors': vendor_name}

        return self._fields(res, fields)
    
    def get_image(self, context, id, fields=None):
        image = self._get_image(context, id)
        return self._make_image_dict(image, fields)
        
    def get_images(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_image_map,
                                    self._make_image_dict,
                                    filters=filters, fields=fields)
        
        
    def create_image(self, context, image):
        n = image['image']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            image = ns_image_map(tenant_id=tenant_id,
                                        id=n.get('id') or utils.str_uuid(),
                                        name=n['name'],
                                        category_id=n['category_id'],
                                        vendor_id=n['vendor_id'],
                                        flavor_id=n['flavor_id'],
                                        security_group_id=n['security_group_id'],
                                        image_id=n['image_id'],
                                        shared=n['shared'])
            context.session.add(image)
        return self._make_image_dict(image)
    
    def _get_image(self, context, id):
        try:
            image = self._get_by_id(context, ns_image_map, id)
        except exc.NoResultFound:
            # NOTE(jkoelker) The PortNotFound exceptions requires net_id
            #                kwarg in order to set the message correctly
            raise q_exc.ImageNotFound(image_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Images match for %s' % id)
            raise q_exc.ImageNotFound(image_id=id)
        return image
    
    def delete_image(self, context, id):
        image = self._get_image(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(image)
            
    def update_image(self, context, id, image):
        n = image['image']
        with context.session.begin(subtransactions=True):
            image = self._get_image(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, image, n)
            image.update(n)
          
        return self._make_image_dict(image)
        
    def _make_metadata_dict(self, metadata, fields=None):
        res = {'id': metadata['id'],
               'name': metadata['name'],
               'value': metadata['value'],
               'image_map_id': metadata['image_map_id']}

        return self._fields(res, fields)
    
    def get_metadata(self, context, id, fields=None):
        metadata = self._get_metadata(context, id)
        return self._make_metadata_dict(metadata, fields)
        
    def get_metadatas(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_metadata,
                                    self._make_metadata_dict,
                                    filters=filters, fields=fields)
        
        
    def create_metadata(self, context, metadata):
        n = metadata['metadata']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            metadata = ns_metadata(id=n.get('id') or utils.str_uuid(),
                                            name=n['name'],
                                            value=n['value'],
                                            image_map_id=n['image_map_id'])
            context.session.add(metadata)
        return self._make_metadata_dict(metadata)
    
    def _get_metadata(self, context, id):
        try:
            metadata = self._get_by_id(context, ns_metadata, id)
        except exc.NoResultFound:
            # NOTE(jkoelker) The PortNotFound exceptions requires net_id
            #                kwarg in order to set the message correctly
            raise q_exc.MetadataNotFound(metadata_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Metadatas match for %s' % id)
            raise q_exc.MetadataNotFound(metadata_id=id)
        return metadata
    
    def delete_metadata(self, context, id):
        metadata = self._get_metadata(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(metadata)
            
    def update_metadata(self, context, id, metadata):
        n = metadata['metadata']
        with context.session.begin(subtransactions=True):
            metadata = self._get_metadata(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, metadata, n)
            metadata.update(n)
          
        return self._make_metadata_dict(metadata)
        
    def _make_personality_dict(self, personality, fields=None):
        res = {'id': personality['id'],
               'file_path': personality['file_path'],
               'file_content': personality['file_content'],
               'image_map_id': personality['image_map_id']}

        return self._fields(res, fields)
    
    def get_personality(self, context, id, fields=None):
        personality = self._get_personality(context, id)
        return self._make_personality_dict(personality, fields)
        
    def get_personalities(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_personalitie,
                                    self._make_personality_dict,
                                    filters=filters, fields=fields)
        
        
    def create_personality(self, context, personality):
        n = personality['personality']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            personality = ns_personalitie(id=n.get('id') or utils.str_uuid(),
                                                    file_path=n['file_path'],
                                                    file_content=n['file_content'],
                                                    image_map_id=n['image_map_id'])
            context.session.add(personality)
        return self._make_personality_dict(personality)
    
    def _get_personality(self, context, id):
        try:
            personality = self._get_by_id(context, ns_personalitie, id)
        except exc.NoResultFound:
            # NOTE(jkoelker) The PortNotFound exceptions requires net_id
            #                kwarg in order to set the message correctly
            raise q_exc.PersonalityNotFound(personality_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Personalities match for %s' % id)
            raise q_exc.PersonalityNotFound(personality_id=id)
        return personality
    
    def delete_personality(self, context, id):
        personality = self._get_personality(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(personality)
            
    def update_personality(self, context, id, personality):
        n = personality['personality']
        with context.session.begin(subtransactions=True):
            personality = self._get_personality(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, personality, n)
            personality.update(n)
          
        return self._make_personality_dict(personality)
        
    def _make_chain_dict(self, chain, fields=None):
        res = {'id': chain['id'],
               'name': chain['name'],
               'tenant_id': chain['tenant_id'],
               'type': chain['type'],
               'auto_boot': chain['auto_boot']}

        return self._fields(res, fields)
    
    def get_chain(self, context, id, fields=None):
        chain = self._get_chain(context, id)
        return self._make_chain_dict(chain, fields)
        
    def get_chains(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_chain,
                                    self._make_chain_dict,
                                    filters=filters, fields=fields)
        
        
    def create_chain(self, context, chain):
        n = chain['chain']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            chain = ns_chain(tenant_id=tenant_id,
                                        id=n.get('id') or utils.str_uuid(),
                                        name=n['name'],
                                        type=n['type'],
                                        auto_boot=n['auto_boot'])
            context.session.add(chain)
        return self._make_chain_dict(chain)
    
    def _get_chain(self, context, id):
        try:
            chain = self._get_by_id(context, ns_chain, id)
        except exc.NoResultFound:
            # NOTE(jkoelker) The PortNotFound exceptions requires net_id
            #                kwarg in order to set the message correctly
            raise q_exc.ChainNotFound(chain_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Chains match for %s' % id)
            raise q_exc.ChainNotFound(chain_id=id)
        return chain
    
    def delete_chain(self, context, id):
        chain = self._get_chain(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(chain)
            
    def update_chain(self, context, id, chain):
        n = chain['chain']
        with context.session.begin(subtransactions=True):
            chain = self._get_chain(context, id)
            # validate 'shared' parameter
            #if 'shared' in n:
                #self._validate_shared_update(context, id, chain, n)
            chain.update(n)
          
        return self._make_chain_dict(chain)
        
       
        
    def _make_chain_image_dict(self, chain_image, fields=None):
        for img in chain_image['chain_image_map']:
            img_name = str(img['name'])
        res = {'id': chain_image['id'],
               'name': chain_image['name'],
               'chain_id': chain_image['chain_id'],
               'image_map_id': chain_image['image_map_id'],
               'sequence_number': chain_image['sequence_number'],
	       'instance_id': chain_image['instance_id'],
	       'instance_uuid': chain_image['instance_uuid'],
               'chain_image_map': img_name}

        return self._fields(res, fields)
    
    def get_chain_image(self, context, id, fields=None):
        chain_image = self._get_chain_image(context, id)
        return self._make_chain_image_dict(chain_image, fields)
        
    def get_chain_images(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_chain_image_map,
                                    self._make_chain_image_dict,
                                    filters=filters, fields=fields)
        
        
    def create_chain_image(self, context, chain_image):
        n = chain_image['chain_image']
        with context.session.begin(subtransactions=True):
            chain_image = ns_chain_image_map(id=n.get('id') or utils.str_uuid(),
                                        name=n['name'],
                                        chain_id=n['chain_id'],
                                        image_map_id=n['image_map_id'],
                                        sequence_number=n['sequence_number'],
					instance_id =n['instance_id'],
					instance_uuid =n['instance_uuid'])
            context.session.add(chain_image)
        return self._make_chain_image_dict(chain_image)
    
    def _get_chain_image(self, context, id):
        try:
            chain_image = self._get_by_id(context, ns_chain_image_map, id)
        except exc.NoResultFound:
            # NOTE(jkoelker) The PortNotFound exceptions requires net_id
            #                kwarg in order to set the message correctly
            raise q_exc.Chain_imageNotFound(chain_image_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Chain_images match for %s' % id)
            raise q_exc.Chain_imageNotFound(chain_image_id=id)
        return chain_image
    
    def delete_chain_image(self, context, id):
        chain_image = self._get_chain_image(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(chain_image)
            
    def update_chain_image(self, context, id, chain_image):
        n = chain_image['chain_image']
        with context.session.begin(subtransactions=True):
            chain_image = self._get_chain_image(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, chain_image, n)
            chain_image.update(n)
          
        return self._make_chain_image_dict(chain_image)

    def _make_chain_image_network_dict(self, chain_image_network, fields=None):
        for net in chain_image_network['image_map_networks']:
            net_name = str(net['name'])
        res = {'id': chain_image_network['id'],
               'name': chain_image_network['name'],
               'chain_map_id': chain_image_network['chain_map_id'],
               'network_id': chain_image_network['network_id'],
               'image_map_networks': net_name}

        return self._fields(res, fields)
    
    def get_chain_image_network(self, context, id, fields=None):
        chain_image_network = self._get_chain_image_network(context, id)
        return self._make_chain_image_network_dict(chain_image_network, fields)
        
    def get_chain_image_networks(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_chain_network_associate,
                                    self._make_chain_image_network_dict,
                                    filters=filters, fields=fields)
        
        
    def create_chain_image_network(self, context, chain_image_network):
        n = chain_image_network['chain_image_network']
        
        with context.session.begin(subtransactions=True):
            chain_image = self._get_chain_image(context, n["chain_map_id"])
            self._validate_chain_image_network_id(context, chain_image, n['network_id'])
            
            chain_image_network = ns_chain_network_associate(id=n.get('id') or utils.str_uuid(),
                                        chain_map_id=n['chain_map_id'],
                                        network_id=n['network_id'])
            context.session.add(chain_image_network)
        return self._make_chain_image_network_dict(chain_image_network)
        
    def _validate_chain_image_network_id(self, context, chain_image, new_chain_image_network_id):
        chain_image_network_list = chain_image.chain_image_networks
        
        for chain_image_network in chain_image_network_list:
            if (chain_image_network.network_id == new_chain_image_network_id):
                err_msg = _("Already  %s  network is mapped " %
                            (new_chain_image_network_id))
                LOG.error("Already  %s  network is mapped " %
                            (new_chain_image_network_id))
                raise q_exc.Invalid(error_message=err_msg)
    
    def _get_chain_image_network(self, context, id):
        try:
            chain_image_network = self._get_by_id(context, ns_chain_network_associate, id)
        except exc.NoResultFound:
            # NOTE(jkoelker) The PortNotFound exceptions requires net_id
            #                kwarg in order to set the message correctly
            raise q_exc.Chain_image_networkNotFound(chain_image_network_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Chain_image_networks match for %s' % id)
            raise q_exc.Chain_image_networkNotFound(chain_image_network_id=id)
        return chain_image_network
    
    def delete_chain_image_network(self, context, id):
        chain_image_network = self._get_chain_image_network(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(chain_image_network)
            
    def update_chain_image_network(self, context, id, chain_image_network):
        n = chain_image_network['chain_image_network']
        with context.session.begin(subtransactions=True):
            chain_image_network = self._get_chain_image_network(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, chain_image_network, n)
            chain_image_network.update(n)
          
        return self._make_chain_image_network_dict(chain_image_network)
        
    def _make_chain_image_conf_dict(self, chain_image_conf, fields=None):
        res = {'id': chain_image_conf['id'],
               'name': chain_image_conf['name'],
               'chain_map_id': chain_image_conf['chain_map_id'],
               'config_handle_id': chain_image_conf['config_handle_id'],
               'networkfunction_id': chain_image_conf['networkfunction_id']}

        return self._fields(res, fields)
    
    def get_chain_image_conf(self, context, id, fields=None):
        chain_image_conf = self._get_chain_image_conf(context, id)
        return self._make_chain_image_conf_dict(chain_image_conf, fields)
        
    def get_chain_image_confs(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_chain_configuration_associate,
                                    self._make_chain_image_conf_dict,
                                    filters=filters, fields=fields)
        
        
    def create_chain_image_conf(self, context, chain_image_conf):
        n = chain_image_conf['chain_image_conf']
        
        with context.session.begin(subtransactions=True):
            chain_image = self._get_chain_image(context, n["chain_map_id"])
            #self._validate_chain_image_conf_id(context, chain_image, n['networkfunction_id'])
            
            chain_image_conf = ns_chain_configuration_associate(id=n.get('id') or utils.str_uuid(),
                                        chain_map_id=n['chain_map_id'],
                                        networkfunction_id=n['networkfunction_id'],
                                        config_handle_id=n['config_handle_id'])
            context.session.add(chain_image_conf)
        return self._make_chain_image_conf_dict(chain_image_conf)
        
    
            
    def _validate_chain_image_conf_id(self, context, chain_image, new_networkfunction_id):
        chain_image_conf_list = chain_image.chain_image_confs
        
        for chain_image_conf in chain_image_conf_list:
            if (chain_image_conf.networkfunction_id == new_networkfunction_id):
                err_msg = _("Already  %s  Config handle is mapped " %
                            (new_networkfunction_id))
                LOG.error("Already  %s  Config handle is mapped " %
                            (new_networkfunction_id))
                raise q_exc.Invalid(error_message=err_msg)
    
    def _get_chain_image_conf(self, context, id):
        try:
            chain_image_conf = self._get_by_id(context, ns_chain_configuration_associate, id)
        except exc.NoResultFound:
            # NOTE(jkoelker) The PortNotFound exceptions requires net_id
            #                kwarg in order to set the message correctly
            raise q_exc.Chain_image_confNotFound(chain_image_conf_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Chain_image_confs match for %s' % id)
            raise q_exc.Chain_image_confNotFound(chain_image_conf_id=id)
        return chain_image_conf
    
    def delete_chain_image_conf(self, context, id):
        chain_image_conf = self._get_chain_image_conf(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(chain_image_conf)
            
    def update_chain_image_conf(self, context, id, chain_image_conf):
        n = chain_image_conf['chain_image_conf']
        with context.session.begin(subtransactions=True):
            chain_image_conf = self._get_chain_image_conf(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, chain_image_conf, n)
            chain_image_conf.update(n)
          
        return self._make_chain_image_conf_dict(chain_image_conf)
        
                

    def _make_config_handle_dict(self, config_handle, fields=None):
        res = {'id': config_handle['id'],
               'name': config_handle['name'],
               'tenant_id': config_handle['tenant_id'],
               'networkfunction_id': config_handle['networkfunction_id'],
               'status': config_handle['status'],
               'slug': config_handle['slug']}

        return self._fields(res, fields)
    
    def get_config_handle(self, context, id, fields=None):
        config_handle = self._get_config_handle(context, id)
        return self._make_config_handle_dict(config_handle, fields)
        
    def get_config_handles(self, context, filters=None, fields=None):
        return self._get_collection(context, ns_config_handle,
                                    self._make_config_handle_dict,
                                    filters=filters, fields=fields)
        
        
    def create_config_handle(self, context, config_handle):
        n = config_handle['config_handle']
        tenant_id = self._get_tenant_id_for_create(context, n)
        with context.session.begin(subtransactions=True):
            config_handle = ns_config_handle(tenant_id=tenant_id,
                                        id=n.get('id') or utils.str_uuid(),
                                        name=n['name'],
                                        networkfunction_id=n['networkfunction_id'],
                                        status=n['status'],
                                        slug=n['slug'])
            context.session.add(config_handle)
        return self._make_config_handle_dict(config_handle)
    
    def _get_config_handle(self, context, id):
        try:
            config_handle = self._get_by_id(context, ns_config_handle, id)
        except exc.NoResultFound:
            # NOTE(jkoelker) The PortNotFound exceptions requires net_id
            #                kwarg in order to set the message correctly
            raise q_exc.Config_handleNotFound(config_handle_id=id)
        except exc.MultipleResultsFound:
            LOG.error('Multiple Config_handles match for %s' % id)
            raise q_exc.Config_handleNotFound(config_handle_id=id)
        return config_handle
    
    def delete_config_handle(self, context, id):
        config_handle = self._get_config_handle(context, id)
        with context.session.begin(subtransactions=True):
            context.session.delete(config_handle)
            
    def update_config_handle(self, context, id, config_handle):
        n = config_handle['config_handle']
        with context.session.begin(subtransactions=True):
            config_handle = self._get_config_handle(context, id)
            # validate 'shared' parameter
            if 'shared' in n:
                self._validate_shared_update(context, id, config_handle, n)
            config_handle.update(n)
          
        return self._make_config_handle_dict(config_handle)
