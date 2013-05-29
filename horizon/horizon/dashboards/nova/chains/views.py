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

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict

from horizon import api
from horizon import exceptions
from horizon import forms
from horizon import tables
from .forms import CreateChain, UpdateChain, LaunchChain
from .tables import ChainsTable
from .chain_images.tables import ChainImagesTable




LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = ChainsTable
    template_name = 'nova/chains/index.html'

    def get_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            chains = api.quantum.chain_list_for_tenant(self.request,
                                                           tenant_id)
        except:
            chains = []
            msg = _('Chain list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in chains:
            n.set_id_as_name_if_empty()
        return chains

class CreateChainView(forms.ModalFormView):
    form_class = CreateChain
    template_name = 'nova/chains/create.html'
    success_url = reverse_lazy('horizon:nova:chains:index')
    
class UpdateChainView(forms.ModalFormView):
    form_class = UpdateChain
    template_name = 'nova/chains/update.html'
    context_object_name = 'chain'
    success_url = reverse_lazy("horizon:nova:chains:index")

    def get_context_data(self, **kwargs):
        context = super(UpdateChainView, self).get_context_data(**kwargs)
        context["chain_id"] = self.kwargs['chain_id']
        return context

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            chain_id = self.kwargs['chain_id']
            try:
                self._object = api.quantum.chain_get(self.request,
                                                       chain_id)
            except:
                redirect = self.success_url
                msg = _('Unable to retrieve chain details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object
    
    def get_initial(self):
        chain = self._get_object()
        return {'chain_id': chain['id'],
                'tenant_id': chain['tenant_id'],
                'name': chain['name']}
        
class DetailChainView(tables.MultiTableView):
    table_classes = (ChainImagesTable, )
    template_name = 'nova/chains/detail.html'
    failure_url = reverse_lazy('horizon:nova:chains:index')
    
    def get_chain_images_data(self):
        try:
            chain = self._get_data()
            chain_images = api.quantum.chain_image_list_for_chain(self.request,
                                              chain_id=chain.id)
            for chain_image in chain_images:
                instance_id = chain_image.instance_id
                try:
                    instance = api.nova.server_get(self.request, instance_id)
                    setattr(chain_image, 'instance_uuid', instance.id)
                    #xx = getattr(instance,'OS-EXT-SRV-ATTR:instance_name','')
                    #setattr(chain_image, 'instance_uuid', xx)
                except:
                    msg = _('Unable to retrieve details for instance "%s".') \
                      % (instance_id)
                    setattr(chain_image, 'instance_uuid', '')
                    #api.quantum.chain_image_modify(self.request, chain.id,
                    #                            instance_uuid='NULL')
                    
                                                  
            
        except:
            chain_images = []
            msg = _('Image list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for s in chain_images:
            s.set_id_as_name_if_empty()
        return chain_images

    def _get_data(self):
        if not hasattr(self, "_chain"):
            try:
                chain_id = self.kwargs['chain_id']
                chain = api.quantum.chain_get(self.request, chain_id)
                chain.set_id_as_name_if_empty(length=0)
            except:
                msg = _('Unable to retrieve details for chain "%s".') \
                      % (chain_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)
            self._chain = chain
        return self._chain

    def get_context_data(self, **kwargs):
        context = super(DetailChainView, self).get_context_data(**kwargs)
        context["chain"] = self._get_data()
        return context
    
    
class LaunchChainView(forms.ModalFormView):
    form_class = LaunchChain
    template_name = 'nova/chains/launch.html'
    success_url = reverse_lazy('horizon:nova:instances:index')
    failure_url = reverse_lazy('horizon:nova:chains:index')
    
    def get_context_data(self, **kwargs):
        context = super(LaunchChainView, self).get_context_data(**kwargs)
        context["chain_id"] = self.kwargs['chain_id']
        return context

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            chain_id = self.kwargs['chain_id']
            try:
                self._object = api.quantum.chain_get(self.request,
                                                       chain_id)
            except:
                redirect = self.success_url
                msg = _('Unable to retrieve chain details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object
    
    def get_initial(self):
        chain = self._get_object()
        return {'chain_id': chain['id'],
                'tenant_id': chain['tenant_id'],
                'name': chain['name']}


