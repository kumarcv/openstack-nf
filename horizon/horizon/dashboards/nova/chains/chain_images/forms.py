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

class BaseImageForm(forms.SelfHandlingForm):
    def __init__(self, request, *args, **kwargs):
        super(BaseImageForm, self).__init__(request, *args, **kwargs)
        # Populate image choices
        image_choices = [('', _("Select a Image Map"))]
        tenant_id = self.request.user.tenant_id
        for image in api.quantum.image_list_for_tenant(request, tenant_id):
            image_choices.append((image.id, image.name))
        self.fields['image_id'].choices = image_choices


class MapImage(BaseImageForm):
    chain_id = forms.CharField(label=_("Chain ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    name = forms.CharField(label=_("Name"))
    image_id = forms.ChoiceField(label=_("Image Map"), required=True)
    sequence_number = forms.IntegerField(label=_("Boot order"),
                               min_value=1,
                               initial=1)
    
    
    
    def handle(self, request, data):
        try:
            sg = api.quantum.chain_image_create(request,
                                           chain_id=data['chain_id'],
                                           name=data['name'],
                                           image_map_id=data['image_id'],
                                           sequence_number=data['sequence_number'])
            chain_map_id = sg.id
            
            imgdata = api.quantum.image_get(self.request,
                                                       data['image_id'])
            category_id = imgdata.category_id
            networkfunctions = api.quantum.category_networkfunction_list_for_category(request, category_id)
            for networkfunction in networkfunctions:
                networkfunction_id = networkfunction.networkfunction_id
                
                chain_conf_map = api.quantum.chain_image_conf_create(request,
                                            networkfunction_id=networkfunction_id,                        
                                           chain_map_id=chain_map_id)
            
            
            messages.success(request,
                             _('Successfully created Chain  Image Map: %s')
                               % data['name'])
            return sg
        except:
            redirect = reverse("horizon:nova:chains:detail")
            exceptions.handle(request,
                              _('Unable to Map Chain to image.'),
                              redirect=redirect)
    
            
            
class UpdateChain_image(forms.SelfHandlingForm):
    chain_id = forms.CharField(widget=forms.HiddenInput())
    chain_image_id = forms.CharField(label=_("ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    name = forms.CharField(max_length=255,
                           label=_("Name"),
                           required=False)
    sequence_number = forms.IntegerField(label=_("Boot order"),
                               min_value=1,
                               initial=1)
    
    failure_url = 'horizon:nova:chains:detail'

    def handle(self, request, data):
        try:
            LOG.debug('params = %s' % data)
            params = {'name': data['name']}
            params['sequence_number'] = data['sequence_number']
            
            chain_image = api.quantum.chain_image_modify(request, data['chain_image_id'],
                                                        name=data['name'],
                                                        sequence_number=data['sequence_number'])
            msg = _('Chain Image Map %s was successfully updated.') % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return chain_image
        except Exception:
            msg = _('Failed to update chain image map %s') % data['cidr']
            LOG.info(msg)
            redirect = reverse(self.failure_url, args=[data['chain_id']])
            exceptions.handle(request, msg, redirect=redirect)
            

