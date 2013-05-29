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


class CreateVendor(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    description = forms.CharField(label=_("Description"))
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False, required=False)
    def handle(self, request, data):
        try:
            sg = api.quantum.vendor_create(request,
                                           name=data['name'],
                                           description=data['description'],
                                           shared=data['shared'])
            
            messages.success(request,
                             _('Successfully created Vendor: %s')
                               % data['name'])
            return sg
        except:
            redirect = reverse("horizon:syspanel:vendors:index")
            exceptions.handle(request,
                              _('Unable to create Vendor.'),
                              redirect=redirect)
            
            
class UpdateVendor(forms.SelfHandlingForm):
    vendor_id = forms.CharField(label=_("ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    name = forms.CharField(label=_("Name"))
    description = forms.CharField(label=_("Description"))
    tenant_id = forms.CharField(widget=forms.HiddenInput)
    shared = forms.BooleanField(label=_("Shared"), required=False)
    
    failure_url = 'horizon:syspanel:vendors:index'

    def handle(self, request, data):
        try:
            vendor = api.quantum.vendor_modify(request, data['vendor_id'],
                                                 name=data['name'], description=data['description'], shared=data['shared'])
            msg = _('Vendor %s was successfully updated.') % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return vendor
        except:
            msg = _('Failed to update vendor %s') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
