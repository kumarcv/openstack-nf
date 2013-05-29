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
from horizon import exceptions
from horizon import forms
from horizon import messages


LOG = logging.getLogger(__name__)

class BaseCategoryfunctionForm(forms.SelfHandlingForm):
    def __init__(self, request, *args, **kwargs):
        super(BaseCategoryfunctionForm, self).__init__(request, *args, **kwargs)
        # Populate Categoryfunctions choices
        networkfunction_choices = []
        tenant_id = self.request.user.tenant_id
        for networkfunction in api.quantum.networkfunction_list_for_tenant(request, tenant_id):
            networkfunction_choices.append((networkfunction.id, networkfunction.name))
        self.fields['networkfunction_id'].choices = networkfunction_choices

class CreateCategory(BaseCategoryfunctionForm):
    name = forms.CharField(label=_("Name"))
    description = forms.CharField(label=_("Description"))
    #shared = forms.BooleanField(label=_("Shared"),
    #                            initial=False, required=False)
    
    networkfunction_id = forms.MultipleChoiceField(label=_("Network Functions"),
                                        required=True,
                                        widget=forms.CheckboxSelectMultiple(),
                                        help_text=_("Launch instance with"
                                                    "these networks"))
    
    
        
    def handle(self, request, data):
        try:
            sg = api.quantum.category_create(request,
                                           name=data['name'],
                                           description=data['description'],
                                           shared=0)
            
            networkfunctions = data['networkfunction_id']
            for networkfunction in networkfunctions:
                cn = api.quantum.category_networkfunction_create(request,
                                           category_id=sg.id,
                                           networkfunction_id=networkfunction)
                
                
                
            
            messages.success(request,
                             _('Successfully created Category: %s')
                               % data['name'])
            return sg
        except:
            redirect = reverse("horizon:nova:categories:index")
            exceptions.handle(request,
                              _('Unable to create Category.'),
                              redirect=redirect)
            
            
class UpdateCategory(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    description = forms.CharField(label=_("Description"))
    tenant_id = forms.CharField(widget=forms.HiddenInput)
    category_id = forms.CharField(label=_("ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    failure_url = 'horizon:nova:categories:index'

    def handle(self, request, data):
        try:
            category = api.quantum.category_modify(request, data['category_id'],
                                                 name=data['name'], description=data['description'])
            msg = _('Category %s was successfully updated.') % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return category
        except:
            msg = _('Failed to update category %s') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
