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
Views for managing Quantum Networkfunctions.
"""
import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import forms
from horizon import tables
from .forms import CreateNetworkfunction, UpdateNetworkfunction
from .tables import NetworkfunctionsTable


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = NetworkfunctionsTable
    template_name = 'syspanel/networkfunctions/index.html'

    def get_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            networkfunctions = api.quantum.networkfunction_list_for_tenant(self.request,
                                                           tenant_id)
        except:
            networkfunctions = []
            msg = _('Networkfunction list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in networkfunctions:
            n.set_id_as_name_if_empty()
        return networkfunctions

class CreateNetworkfunctionView(forms.ModalFormView):
    form_class = CreateNetworkfunction
    template_name = 'syspanel/networkfunctions/create.html'
    success_url = reverse_lazy('horizon:syspanel:networkfunctions:index')
    
class UpdateNetworkfunctionView(forms.ModalFormView):
    form_class = UpdateNetworkfunction
    template_name = 'syspanel/networkfunctions/update.html'
    context_object_name = 'networkfunction'
    success_url = reverse_lazy("horizon:syspanel:networkfunctions:index")

    def get_context_data(self, **kwargs):
        context = super(UpdateNetworkfunctionView, self).get_context_data(**kwargs)
        context["networkfunction_id"] = self.kwargs['networkfunction_id']
        return context

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            networkfunction_id = self.kwargs['networkfunction_id']
            try:
                self._object = api.quantum.networkfunction_get(self.request,
                                                       networkfunction_id)
            except:
                redirect = self.success_url
                msg = _('Unable to retrieve networkfunction details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object
    
    def get_initial(self):
        networkfunction = self._get_object()
        return {'networkfunction_id': networkfunction['id'],
                'tenant_id': networkfunction['tenant_id'],
                'name': networkfunction['name'],
                'description': networkfunction['description'],
                'shared': networkfunction['shared']}


