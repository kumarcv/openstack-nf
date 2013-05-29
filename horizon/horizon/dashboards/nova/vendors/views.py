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
Views for managing Quantum Vendors.
"""
import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import forms
from horizon import tables
from .forms import CreateVendor, UpdateVendor
from .tables import VendorsTable


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = VendorsTable
    template_name = 'nova/vendors/index.html'

    def get_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            vendors = api.quantum.vendor_list_for_tenant(self.request,
                                                           tenant_id)
        except:
            vendors = []
            msg = _('Vendor list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in vendors:
            n.set_id_as_name_if_empty()
        return vendors

class CreateVendorView(forms.ModalFormView):
    form_class = CreateVendor
    template_name = 'nova/vendors/create.html'
    success_url = reverse_lazy('horizon:nova:vendors:index')
    
class UpdateVendorView(forms.ModalFormView):
    form_class = UpdateVendor
    template_name = 'nova/vendors/update.html'
    context_object_name = 'vendor'
    success_url = reverse_lazy("horizon:nova:vendors:index")

    def get_context_data(self, **kwargs):
        context = super(UpdateVendorView, self).get_context_data(**kwargs)
        context["vendor_id"] = self.kwargs['vendor_id']
        return context

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            vendor_id = self.kwargs['vendor_id']
            try:
                self._object = api.quantum.vendor_get(self.request,
                                                       vendor_id)
            except:
                redirect = self.success_url
                msg = _('Unable to retrieve vendor details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object
    
    def get_initial(self):
        vendor = self._get_object()
        return {'vendor_id': vendor['id'],
                'tenant_id': vendor['tenant_id'],
                'name': vendor['name'],
                'description': vendor['description']}


