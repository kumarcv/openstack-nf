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

from quantum.common import topics
from quantum.db.nwservices import nwservices_db
from quantum.extensions import nwservices
from quantum.extensions.nwservices import NwservicesPluginBase
from quantum.openstack.common import log as logging
from quantum.plugins.common import constants
from quantum.plugins.services.nwservices import plugin_rpc
from quantum.plugins.services.nwservices.scheduler import scheduler
from quantum.plugins.services.nwservices.drivers.fsl_driver import NwservicesDriver

LOG = logging.getLogger(__name__)


class NwservicesPlugin(NwservicesPluginBase):
    """
    Implementation of the Quantum Network Service Plugin.
    DB related work is implemented in class NwservicesPluginDb
    """
    supported_extension_aliases = ["fns"]

    def __init__(self):
        self.scheduler = scheduler.BalancerScheduler()
        self.db = nwservices_db.NwservicePluginDb()
        self.agent_api = plugin_rpc.LoadbalancerAgentCaller(topics.SVC_AGENT)
        self.callbacks = plugin_rpc.LoadbalancerPluginCallbacks(self.db,
                                                                self.scheduler)
        self.driver = NwservicesDriver.get_instance()

    def get_plugin_type(self):
        return constants.NWSERVICES

    def get_plugin_description(self):
        return "Quantum Network Service Plugin"

    def _fetch_device(self, context, pool_id):
        pool = self.db.get_pool(context, pool_id)
        device = self.scheduler.get_device_by_resource(context, pool)
        return device

    def _is_pending(self, obj):
        return obj['status'] in [constants.PENDING_CREATE,
                                 constants.PENDING_UPDATE,
                                 constants.PENDING_DELETE]

    def create_networkfunction(self, context, networkfunction):
        v = self.db.create_networkfunction(context, networkfunction)
        ###TODO::Network Service DRVIER TO HANDLE
        return v

    def update_networkfunction(self, context, networkfunction_id, networkfunction):
        LOG.debug(_('Update networkfunction %s'), networkfunction_id)
        v_new = self.db.update_networkfunction(context, networkfunction_id, networkfunction)
        return v_new

    def delete_networkfunction(self, context, networkfunction_id):
        LOG.debug(_('Delete networkfunction %s'), networkfunction_id)
        self.db.delete_networkfunction(context, networkfunction_id)

    def get_networkfunction(self, context, networkfunction_id, fields=None):
        LOG.debug(_('Get networkfunction %s'), networkfunction_id)
        return self.db.get_networkfunction(context, networkfunction_id, fields)

    def get_networkfunctions(self, context, filters=None, fields=None):
        LOG.debug(_('Get networkfunctions'))
        return self.db.get_networkfunctions(context, filters, fields)
        
    def create_category(self, context, category):
        v = self.db.create_category(context, category)
        ###TODO::Network Service DRVIER TO HANDLE
        return v

    def update_category(self, context, category_id, category):
        LOG.debug(_('Update category %s'), category_id)
        v_new = self.db.update_category(context, category_id, category)
        return v_new

    def delete_category(self, context, category_id):
        LOG.debug(_('Delete category %s'), category_id)
        self.db.delete_category(context, category_id)

    def get_category(self, context, category_id, fields=None):
        LOG.debug(_('Get category %s'), category_id)
        return self.db.get_category(context, category_id, fields)

    def get_categories(self, context, filters=None, fields=None):
        LOG.debug(_('Get categories'))
        return self.db.get_categories(context, filters, fields)
    
    def create_category_networkfunction(self, context, category_networkfunction):
        v = self.db.create_category_networkfunction(context, category_networkfunction)
        ###TODO::Network Service DRVIER TO HANDLE
        return v

    def update_category_networkfunction(self, context, category_networkfunction_id, category_networkfunction):
        LOG.debug(_('Update category_networkfunction %s'), category_networkfunction_id)
        v_new = self.db.update_category_networkfunction(context, category_networkfunction_id, category_networkfunction)
        return v_new

    def delete_category_networkfunction(self, context, category_networkfunction_id):
        LOG.debug(_('Delete category_networkfunction %s'), category_networkfunction_id)
        self.db.delete_category_networkfunction(context, category_networkfunction_id)

    def get_category_networkfunction(self, context, category_networkfunction_id, fields=None):
        LOG.debug(_('Get category_networkfunction %s'), category_networkfunction_id)
        return self.db.get_category_networkfunction(context, category_networkfunction_id, fields)

    def get_category_networkfunctions(self, context, filters=None, fields=None):
        LOG.debug(_('Get category_networkfunctions'))
        return self.db.get_category_networkfunctions(context, filters, fields)
        
        
    def create_vendor(self, context, vendor):
        v = self.db.create_vendor(context, vendor)
        ###TODO::Network Service DRVIER TO HANDLE
        return v

    def update_vendor(self, context, vendor_id, vendor):
        LOG.debug(_('Update vendor %s'), vendor_id)
        v_new = self.db.update_vendor(context, vendor_id, vendor)
        return v_new

    def delete_vendor(self, context, vendor_id):
        LOG.debug(_('Delete vendor %s'), vendor_id)
        self.db.delete_vendor(context, vendor_id)

    def get_vendor(self, context, vendor_id, fields=None):
        LOG.debug(_('Get vendor %s'), vendor_id)
        return self.db.get_vendor(context, vendor_id, fields)

    def get_vendors(self, context, filters=None, fields=None):
        LOG.debug(_('Get vendors'))
        return self.db.get_vendors(context, filters, fields)
        
    def create_image(self, context, image):
        v = self.db.create_image(context, image)
        ###TODO::Network Service DRVIER TO HANDLE
        return v

    def update_image(self, context, image_id, image):
        LOG.debug(_('Update image %s'), image_id)
        v_new = self.db.update_image(context, image_id, image)
        return v_new

    def delete_image(self, context, image_id):
        LOG.debug(_('Delete image %s'), image_id)
        self.db.delete_image(context, image_id)

    def get_image(self, context, image_id, fields=None):
        LOG.debug(_('Get image %s'), image_id)
        return self.db.get_image(context, image_id, fields)

    def get_images(self, context, filters=None, fields=None):
        LOG.debug(_('Get images'))
        return self.db.get_images(context, filters, fields)
        
    def create_metadata(self, context, metadata):
        v = self.db.create_metadata(context, metadata)
        ###TODO::Network Service DRVIER TO HANDLE
        return v

    def update_metadata(self, context, metadata_id, metadata):
        LOG.debug(_('Update metadata %s'), metadata_id)
        v_new = self.db.update_metadata(context, metadata_id, metadata)
        return v_new

    def delete_metadata(self, context, metadata_id):
        LOG.debug(_('Delete metadata %s'), metadata_id)
        self.db.delete_metadata(context, metadata_id)

    def get_metadata(self, context, metadata_id, fields=None):
        LOG.debug(_('Get metadata %s'), metadata_id)
        return self.db.get_metadata(context, metadata_id, fields)

    def get_metadatas(self, context, filters=None, fields=None):
        LOG.debug(_('Get metadatas'))
        return self.db.get_metadatas(context, filters, fields)
        
    def create_personality(self, context, personality):
        v = self.db.create_personality(context, personality)
        ###TODO::Network Service DRVIER TO HANDLE
        return v

    def update_personality(self, context, personality_id, personality):
        LOG.debug(_('Update personality %s'), personality_id)
        v_new = self.db.update_personality(context, personality_id, personality)
        return v_new

    def delete_personality(self, context, personality_id):
        LOG.debug(_('Delete personality %s'), personality_id)
        self.db.delete_personality(context, personality_id)

    def get_personality(self, context, personality_id, fields=None):
        LOG.debug(_('Get personality %s'), personality_id)
        return self.db.get_personality(context, personality_id, fields)

    def get_personalities(self, context, filters=None, fields=None):
        LOG.debug(_('Get personalities'))
        return self.db.get_personalities(context, filters, fields)
        
    def create_chain(self, context, chain):
        v = self.db.create_chain(context, chain)
        ###TODO::Network Service DRVIER TO HANDLE
        return v

    def update_chain(self, context, chain_id, chain):
        LOG.debug(_('Update chain %s'), chain_id)
        v_new = self.db.update_chain(context, chain_id, chain)
        return v_new

    def delete_chain(self, context, chain_id):
        LOG.debug(_('Delete chain %s'), chain_id)
        self.db.delete_chain(context, chain_id)

    def get_chain(self, context, chain_id, fields=None):
        LOG.debug(_('Get chain %s'), chain_id)
        return self.db.get_chain(context, chain_id, fields)

    def get_chains(self, context, filters=None, fields=None):
        LOG.debug(_('Get chains'))
        return self.db.get_chains(context, filters, fields)
        
    def create_chain_image(self, context, chain_image):
        v = self.db.create_chain_image(context, chain_image)
        ###TODO::Network Service DRVIER TO HANDLE
        return v

    def update_chain_image(self, context, chain_image_id, chain_image):
        LOG.debug(_('Update chain_image %s'), chain_image_id)
        v_new = self.db.update_chain_image(context, chain_image_id, chain_image)
        return v_new

    def delete_chain_image(self, context, chain_image_id):
        LOG.debug(_('Delete chain_image %s'), chain_image_id)
        self.db.delete_chain_image(context, chain_image_id)

    def get_chain_image(self, context, chain_image_id, fields=None):
        LOG.debug(_('Get chain_image %s'), chain_image_id)
        return self.db.get_chain_image(context, chain_image_id, fields)

    def get_chain_images(self, context, filters=None, fields=None):
        LOG.debug(_('Get chain_images'))
        return self.db.get_chain_images(context, filters, fields)
        
    def create_chain_image_network(self, context, chain_image_network):
        v = self.db.create_chain_image_network(context, chain_image_network)
        ###TODO::Network Service DRVIER TO HANDLE
        return v

    def update_chain_image_network(self, context, chain_image_network_id, chain_image_network):
        LOG.debug(_('Update chain_image_network %s'), chain_image_network_id)
        v_new = self.db.update_chain_image_network(context, chain_image_network_id, chain_image_network)
        return v_new

    def delete_chain_image_network(self, context, chain_image_network_id):
        LOG.debug(_('Delete chain_image_network %s'), chain_image_network_id)
        self.db.delete_chain_image_network(context, chain_image_network_id)

    def get_chain_image_network(self, context, chain_image_network_id, fields=None):
        LOG.debug(_('Get chain_image_network %s'), chain_image_network_id)
        return self.db.get_chain_image_network(context, chain_image_network_id, fields)

    def get_chain_image_networks(self, context, filters=None, fields=None):
        LOG.debug(_('Get chain_image_networks'))
        return self.db.get_chain_image_networks(context, filters, fields)
        
    def create_chain_image_conf(self, context, chain_image_conf):
        v = self.db.create_chain_image_conf(context, chain_image_conf)
        ###TODO::Network Service DRVIER TO HANDLE
        return v

    def update_chain_image_conf(self, context, chain_image_conf_id, chain_image_conf):
        LOG.debug(_('Update chain_image_conf %s'), chain_image_conf_id)
        v_new = self.db.update_chain_image_conf(context, chain_image_conf_id, chain_image_conf)
        return v_new

    def delete_chain_image_conf(self, context, chain_image_conf_id):
        LOG.debug(_('Delete chain_image_conf %s'), chain_image_conf_id)
        self.db.delete_chain_image_conf(context, chain_image_conf_id)

    def get_chain_image_conf(self, context, chain_image_conf_id, fields=None):
        LOG.debug(_('Get chain_image_conf %s'), chain_image_conf_id)
        return self.db.get_chain_image_conf(context, chain_image_conf_id, fields)

    def get_chain_image_confs(self, context, filters=None, fields=None):
        LOG.debug(_('Get chain_image_confs'))
        return self.db.get_chain_image_confs(context, filters, fields)
        
    def create_config_handle(self, context, config_handle):
        v = self.db.create_config_handle(context, config_handle)
        ###TODO::Network Service DRVIER TO HANDLE
        return v

    def update_config_handle(self, context, config_handle_id, config_handle):
        LOG.debug(_('Update config_handle %s'), config_handle_id)
        v_new = self.db.update_config_handle(context, config_handle_id, config_handle)
        return v_new

    def delete_config_handle(self, context, config_handle_id):
        LOG.debug(_('Delete config_handle %s'), config_handle_id)
        self.db.delete_config_handle(context, config_handle_id)

    def get_config_handle(self, context, config_handle_id, fields=None):
        LOG.debug(_('Get config_handle %s'), config_handle_id)
        return self.db.get_config_handle(context, config_handle_id, fields)

    def get_config_handles(self, context, filters=None, fields=None):
        LOG.debug(_('Get config_handles'))
        return self.db.get_config_handles(context, filters, fields)
        
    def get_launch(self, context, config_handle_id, fields=None):
        LOG.debug(_('Launch Configuration'))
        conf = self.db.get_config_handle(context, config_handle_id, fields)
        slug = conf['slug']
       
        res = {'header': 'request',
               'config_handle_id': config_handle_id,
               'slug': slug,
               'version':'1.0'}
        self.driver.send_cast(config_handle_id,{'config':res})
        return res
        
    
