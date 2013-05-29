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

 
class AssociateNetwork(tables.LinkAction):
    name = "mapnet"
    verbose_name = _("Associate Network To Chain")
    url = "horizon:nova:chains:chain_images:mapnet"
    classes = ("ajax-modal", "btn-create")
    
    def get_link_url(self, datum=None):
        chain_image_id = self.table.kwargs['chain_image_id']
        return reverse(self.url, args=(chain_image_id,))
        
class DeleteNetwork(tables.DeleteAction):
    data_type_singular = _("Chain Network")
    data_type_plural = _("Chain Networks")
    
    def delete(self, request, chain_image_network_id):
        try:
            api.quantum.chain_image_network_delete(request, chain_image_network_id)
            LOG.debug('Dissociated network %s successfully' % chain_image_network_id)
        except:
            msg = _('Failed to Dissociated network %s') % chain_image_network_id
            LOG.info(msg)
            chain_image_id = self.table.kwargs['chain_image_id']
            redirect = reverse('horizon:nova:chains:chain_images:detail',
                               args=[chain_image_id])
            exceptions.handle(request, msg, redirect=redirect)
            
class DissociateNetwork(tables.DeleteAction):
    data_type_singular = _("Chain Network")
    data_type_plural = _("Chain Networks")
    
    def delete(self, request, network_id):
        try:
            api.quantum.chain_image_network_delete_map(request, network_id)
            LOG.debug('Dissociated network %s successfully' % network_id)
        except:
            msg = _('Failed to Dissociated network %s') % network_id
            LOG.info(msg)
            chain_image_id = self.table.kwargs['chain_image_id']
            redirect = reverse('horizon:nova:chains:chain_images:detail',
                               args=[chain_image_id])
            exceptions.handle(request, msg, redirect=redirect)

def get_chain_network(chain_image_network):
    context = chain_image_network.image_map_networks
    return context

def get_network_link(datum):
    view = "horizon:nova:networks:detail"
    if datum.network_id:
        return reverse(view, args=(datum.network_id,))
    else:
        return None
    
def get_subnets(network):
    template_name = 'nova/networks/_network_ips.html'
    context = {"subnets": network.subnets}
    return template.loader.render_to_string(template_name, context)
    
class ChainNetworksTable(tables.DataTable):
    
    #network = tables.Column(get_chain_network,
    #                     verbose_name=_("Associated Network"),
    #                     link=get_network_link)
    
    
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link='horizon:nova:networks:detail')
    subnets = tables.Column(get_subnets,
                            verbose_name=_("Subnets Associated"),)
    shared = tables.Column("shared", verbose_name=_("Shared"),
                           filters=(filters.yesno, filters.capfirst))
    network_status = tables.Column("status", verbose_name=_("Status"))
    admin_state = tables.Column("admin_state",
                                verbose_name=_("Admin State"))
    class Meta:
        name = "chain_image_networks"
        verbose_name = _("Chain Images Network Map List")
        table_actions = (AssociateNetwork, DissociateNetwork, )
        row_actions = (DissociateNetwork, )
        
class AssociateConf(tables.LinkAction):
    name = "mapconf"
    verbose_name = _("Map Configuration")
    url = "horizon:nova:chains:chain_images:mapconf"
    classes = ("ajax-modal", "btn-edit")
    
    def get_link_url(self, chain_image_conf):
        chain_image_id = self.table.kwargs['chain_image_id']
        chain_image_conf_id = chain_image_conf.id
        return reverse(self.url, args=(chain_image_conf_id,))
        
        

        
class DissociateConf(tables.DeleteAction):
    data_type_singular = _("Chain Configuration")
    data_type_plural = _("Chain Configuration")
    
    def delete(self, request, chain_image_conf_id):
        try:
            #api.quantum.chain_image_conf_delete(request, chain_image_conf_id)
            api.quantum.chain_image_conf_modify(request, chain_image_conf_id,
                                                        config_handle_id='')
            LOG.debug('Dissociated Configuration %s successfully' % chain_image_conf_id)
        except:
            msg = _('Failed to Dissociated configuration %s') % chain_image_conf_id
            LOG.info(msg)
            chain_image_id = self.table.kwargs['chain_image_id']
            redirect = reverse('horizon:nova:chains:chain_images:detail',
                               args=[chain_image_id])
            exceptions.handle(request, msg, redirect=redirect) 

       
class ChainConfsTable(tables.DataTable):
    network_function_name = tables.Column("network_function_name",
                         verbose_name=_("Network Function"))
    config_handle_name = tables.Column("config_handle_name",
                         verbose_name=_("Configuration"))
        
    class Meta:
        name = "chain_image_confs"
        verbose_name = _("Chain Images Configuration Map List")
        table_actions = (DissociateConf, )
        row_actions = (AssociateConf, DissociateConf, )
        

