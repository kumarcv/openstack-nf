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

"""
Views for managing Quantum Chains.
"""
import logging

from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import forms
from horizon import tables
from .forms import MapImage, UpdateChain_image
from .chain_image_networks.tables import ChainNetworksTable, ChainConfsTable




LOG = logging.getLogger(__name__)

    
class MapimgView(forms.ModalFormView):
    form_class = MapImage
    template_name = 'nova/chains/chain_images/mapimg.html'
    success_url = 'horizon:nova:chains:detail'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['chain_id'],))

    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                chain_id = self.kwargs["chain_id"]
                self._object = api.quantum.chain_get(self.request,
                                                       chain_id)
            except:
                redirect = reverse('horizon:nova:chains:index')
                msg = _("Unable to retrieve Chain.")
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(MapimgView, self).get_context_data(**kwargs)
        context['chain'] = self.get_object()
        return context

    def get_initial(self):
        chain = self.get_object()
        return {"chain_id": self.kwargs['chain_id'],
                "chain_name": chain.name}
        

class EditChain_imageView(forms.ModalFormView):
    form_class = UpdateChain_image
    template_name = 'nova/chains/chain_images/update.html'
    context_object_name = 'chain_image'
    success_url = reverse_lazy('horizon:nova:chains:detail')
    
    def get_success_url(self):
        return reverse('horizon:nova:chains:detail',
                       args=(self.kwargs['chain_id'],))

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            chain_image_id = self.kwargs['chain_image_id']
            try:
                self._object = api.quantum.chain_image_get(self.request, chain_image_id)
            except:
                redirect = reverse("horizon:nova:chains:index")
                msg = _('Unable to retrieve chain image details')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(EditChain_imageView, self).get_context_data(**kwargs)
        chain_image = self._get_object()
        context['chain_image_id'] = chain_image.id
        context['chain_id'] = chain_image.chain_id
        context['image_map_id'] = chain_image.image_map_id
        context['name'] = chain_image.name
        context['sequence_number'] = chain_image.sequence_number
        return context

    def get_initial(self):
        chain_image = self._get_object()
        return {'chain_id': self.kwargs['chain_id'],
                'chain_image_id': chain_image['id'],
                'name': chain_image['name'],
                'image_map_id': chain_image['image_map_id'],
                'sequence_number': chain_image['sequence_number']}
        
        
class DetailChainImageView(tables.MultiTableView):
    table_classes = (ChainNetworksTable, ChainConfsTable,  )
    template_name = 'nova/chains/chain_images/detail.html'
    failure_url = reverse_lazy('horizon:nova:chains:index')
    
    def get_chain_image_networks_data(self):
        try:
            chain_image = self._get_data()
            chain_image_networks = api.quantum.chain_image_network_list_for_chain_networks(self.request,
                                              chain_map_id=chain_image.id)
        except:
            chain_image_networks = []
            msg = _('Network list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for s in chain_image_networks:
            s.set_id_as_name_if_empty()
        
        return chain_image_networks
    
    def get_chain_image_confs_data(self):
        try:
            chain_image = self._get_data()
            chain_image_confs = api.quantum.chain_image_conf_list_for_chain(self.request,
                                              chain_map_id=chain_image.id)
            for chain_image_conf in chain_image_confs:
                    networkfunction_id = chain_image_conf.networkfunction_id
                    config_handle_id = chain_image_conf.config_handle_id
                    config_handle_name = ''
                    network_function_name = ''
                    if networkfunction_id != '' :
                        network_function = api.quantum.networkfunction_get(self.request, networkfunction_id)
                        network_function_name = network_function.name
                    if config_handle_id != '' :
                        config_handle = api.quantum.config_handle_get(self.request, config_handle_id)
                        config_handle_name = config_handle.name
                    
                    setattr(chain_image_conf, 'config_handle_name', config_handle_name)
                    setattr(chain_image_conf, 'network_function_name', network_function_name)
            
        except:
            chain_image_confs = []
            msg = _('Configuration list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for s in chain_image_confs:
            s.set_id_as_name_if_empty()
        
        return chain_image_confs

    def _get_data(self):
        if not hasattr(self, "_chain_image"):
            try:
                chain_image_id = self.kwargs['chain_image_id']
                
                chain_image = api.quantum.chain_image_get(self.request, chain_image_id)
                chain_image.set_id_as_name_if_empty(length=0)
            except:
                msg = _('Unable to retrieve details for chain image "%s".') \
                      % (chain_image_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)
            self._chain_image = chain_image
        return self._chain_image

    def get_context_data(self, **kwargs):
        context = super(DetailChainImageView, self).get_context_data(**kwargs)
        context["chain_image"] = self._get_data()
        return context
    





