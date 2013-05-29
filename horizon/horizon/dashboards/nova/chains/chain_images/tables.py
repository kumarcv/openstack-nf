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
import logging

from django import template
from django.core.urlresolvers import reverse, reverse_lazy
from django.template import defaultfilters as filters
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import tables


LOG = logging.getLogger(__name__)



class AssociateImage(tables.LinkAction):
    name = "mapimg"
    verbose_name = _("Associate Image To Chain")
    url = "horizon:nova:chains:mapimg"
    classes = ("ajax-modal", "btn-create")
    
    def get_link_url(self, datum=None):
        chain_id = self.table.kwargs['chain_id']
        return reverse(self.url, args=(chain_id,))
        
class DissociateImage(tables.DeleteAction):
    data_type_singular = _("Chain Image")
    data_type_plural = _("Chain Images")

    def delete(self, request, chain_image_id):
        try:
            chain_networks = api.quantum.chain_image_network_list(request,
                                                       chain_map_id=chain_image_id)
            
            for chain_network in chain_networks:
                network_id = chain_network.id
                api.quantum.chain_image_network_delete(request, network_id)
                
              
            chain_confs = api.quantum.chain_image_conf_list(request,
                                                       chain_map_id=chain_image_id)
            for chain_conf in chain_confs:
                conf_id = chain_conf.id
                api.quantum.chain_image_conf_delete(request, conf_id)    
            
            api.quantum.chain_image_delete(request, chain_image_id)
            LOG.debug('Dissociated chain %s successfully' % chain_image_id)
        except:
            msg = _('Failed to Dissociated chain %s') % chain_image_id
            LOG.info(msg)
            chain_id = self.table.kwargs['chain_id']
            redirect = reverse('horizon:nova:chains:detail',
                               args=[chain_id])
            exceptions.handle(request, msg, redirect=redirect)
            
class EditChainMap(tables.LinkAction):
    name = "editchainimg"
    verbose_name = _("Edit Chain Image Map")
    url = "horizon:nova:chains:editchainimg"
    classes = ("ajax-modal", "btn-edit")
    
    def get_link_url(self, chain_image):
        chain_id = self.table.kwargs['chain_id']
        return reverse(self.url, args=(chain_id, chain_image.id))
        
def get_chain_image(chain_image):
    context = chain_image.chain_image_map
    return context

class AssociateNetwork(tables.LinkAction):
    name = "mapnet"
    verbose_name = _("Associate Network To Chain")
    url = "horizon:nova:chains:chain_images:mapnet"
    classes = ("ajax-modal", "btn-create")

def get_image_map_link(datum):
    view = "horizon:nova:images:detail"
    if datum.image_map_id:
        return reverse(view, args=(datum.image_map_id,))
    else:
        return None
    
def get_instance_link(datum):
    view = "horizon:nova:instances:detail"
    if datum.instance_uuid:
        return reverse(view, args=(datum.instance_uuid,))
    else:
        return None 
    
    
class ChainImagesTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link='horizon:nova:chains:chain_images:detail')
    image = tables.Column(get_chain_image,
                         verbose_name=_("Associated Image"),
                         link=get_image_map_link)
    sequence_number = tables.Column("sequence_number", verbose_name=_("Sequence Number"))
    instance_uuid = tables.Column("instance_uuid", verbose_name=_("Instance"),
                                link=get_instance_link)
    
    class Meta:
        name = "chain_images"
        verbose_name = _("Chain Images Map List")
        table_actions = (AssociateImage, DissociateImage, )
        row_actions = (EditChainMap, DissociateImage, AssociateNetwork   )
        
   
