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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import forms
from horizon import messages
from horizon import exceptions
from horizon.utils import fields

LOG = logging.getLogger(__name__)

class BaseNetworkForm(forms.SelfHandlingForm):
    def __init__(self, request, *args, **kwargs):
        super(BaseNetworkForm, self).__init__(request, *args, **kwargs)
        # Populate image choices
        network_choices = [('', _("Select Network"))]
        tenant_id = self.request.user.tenant_id
        for network in api.quantum.network_list_for_tenant(request, tenant_id):
            network_choices.append((network.id, network.name))
        self.fields['network_id'].choices = network_choices


class MapNet(BaseNetworkForm):
    chain_image_id = forms.CharField(label=_("Chain Image ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    network_id = forms.ChoiceField(label=_("Network"), required=True)
    
    def handle(self, request, data):
        try:
            sg = api.quantum.chain_image_network_create(request,
                                           chain_map_id=data['chain_image_id'],
                                           network_id=data['network_id'])
                      
            messages.success(request,
                             _('Successfully created Chain  Network Map: %s')
                               % data['network_id'])
            return sg
        except Exception:
            redirect = reverse("horizon:nova:chains:chain_images:detail")
            exceptions.handle(request,
                              _('Unable to Map Chain to image.'),
                              redirect=redirect)

class BaseConfForm(forms.SelfHandlingForm):
    def __init__(self, request, *args, **kwargs):
        super(BaseConfForm, self).__init__(request, *args, **kwargs)
        config_handle_choices = [('', _("Select Config Handle"))]
        tenant_id = self.request.user.tenant_id
        for config_handle in api.quantum.config_handle_list_for_tenant(request, tenant_id):
            config_handle_choices.append((config_handle.id, config_handle.name))
        self.fields['config_handle_id'].choices = config_handle_choices
           
class MapConf(BaseConfForm):
    chain_image_conf_id = forms.CharField(label=_("Chain Image Configuration ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    config_handle_id = forms.ChoiceField(label=_("Configuration Handle"), required=True)
    
    def handle(self, request, data):
        try:
            
            sg = api.quantum.chain_image_conf_modify(request, data['chain_image_conf_id'],
                                                        config_handle_id=data['config_handle_id'])
            
            str1 = api.quantum.launch_chain(request,
                                             data['config_handle_id'])
            messages.success(request,
                             _('Successfully created Chain  Configuration Map: %s')
                               % data['config_handle_id'])
            return sg
        except:
            redirect = reverse("horizon:nova:chains:chain_images:detail")
            exceptions.handle(request,
                              _('Unable to Map Chain to image.'),
                              redirect=redirect)

