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
Views for managing Quantum Categories.
"""
import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import forms
from horizon import tables
from .forms import CreateCategory, UpdateCategory
from .tables import CategoriesTable


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = CategoriesTable
    template_name = 'syspanel/categories/index.html'

    def get_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            categories = api.quantum.category_list_for_tenant(self.request,
                                                           tenant_id)
        except:
            categories = []
            msg = _('Category list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in categories:
            n.set_id_as_name_if_empty()
        return categories

class CreateCategoryView(forms.ModalFormView):
    form_class = CreateCategory
    template_name = 'syspanel/categories/create.html'
    success_url = reverse_lazy('horizon:syspanel:categories:index')
    
class UpdateCategoryView(forms.ModalFormView):
    form_class = UpdateCategory
    template_name = 'syspanel/categories/update.html'
    context_object_name = 'category'
    success_url = reverse_lazy("horizon:syspanel:categories:index")

    def get_context_data(self, **kwargs):
        context = super(UpdateCategoryView, self).get_context_data(**kwargs)
        context["category_id"] = self.kwargs['category_id']
        return context

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            category_id = self.kwargs['category_id']
            try:
                self._object = api.quantum.category_get(self.request,
                                                       category_id)
            except:
                redirect = self.success_url
                msg = _('Unable to retrieve category details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object
    
    def get_initial(self):
        category = self._get_object()
        return {'category_id': category['id'],
                'tenant_id': category['tenant_id'],
                'name': category['name'],
                'description': category['description'],
                'shared': category['shared']}


