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
from .forms import MapNet, MapConf





LOG = logging.getLogger(__name__)

    
class MapnetView(forms.ModalFormView):
    form_class = MapNet
    template_name = 'nova/chains/chain_images/chain_image_networks/mapnet.html'
    success_url = 'horizon:nova:chains:chain_images:detail'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['chain_image_id'],))

    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                chain_image_id = self.kwargs["chain_image_id"]
                self._object = api.quantum.chain_image_get(self.request,
                                                       chain_image_id)
            except:
                redirect = reverse('horizon:nova:chains:index')
                msg = _("Unable to retrieve data.")
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(MapnetView, self).get_context_data(**kwargs)
        context['chain_image'] = self.get_object()
        return context

    def get_initial(self):
        chain_image = self.get_object()
        return {"chain_image_id": self.kwargs['chain_image_id'],
                "chain_image_name": chain_image.name}
    
class MapconfView(forms.ModalFormView):
    form_class = MapConf
    template_name = 'nova/chains/chain_images/chain_image_networks/mapconf.html'
    success_url = 'horizon:nova:chains:chain_images:detail'

    def get_success_url(self):
        chain_image_id = self.kwargs["chain_image_id"]
        data = api.quantum.chain_image_conf_get(self.request,
                                                       chain_image_id)
        return reverse(self.success_url,
                       args=(data.chain_map_id,))

    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                chain_image_id = self.kwargs["chain_image_id"]
                chain_confs = api.quantum.chain_image_conf_get(self.request,
                                                       chain_image_id)
                
                 
                
            except:
                redirect = reverse('horizon:nova:chains:index')
                msg = _("Unable to retrieve data.")
                exceptions.handle(self.request, msg, redirect=redirect)
        return chain_confs

    def get_context_data(self, **kwargs):
        context = super(MapconfView, self).get_context_data(**kwargs)
        context['chain_image'] = self.get_object()
        return context

    def get_initial(self):
        chain_image = self.get_object()
        return {"chain_image_id": chain_image.chain_map_id,
                "chain_image_conf_id": chain_image.id,
                "config_handle_id" : chain_image.config_handle_id,
                "chain_image_name": chain_image.name,
                "networkfunction_id" : chain_image.networkfunction_id}
        
        




