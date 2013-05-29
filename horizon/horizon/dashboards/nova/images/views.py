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
Views for managing Quantum Images.
"""
import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from horizon import workflows
from .forms import UpdateImage
from .tables import ImagesTable
from .workflows import CreateImage
from .tabs import ImageDetailTabs


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = ImagesTable
    template_name = 'nova/images/index.html'

    def get_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            images = api.quantum.image_list_for_tenant(self.request,
                                                           tenant_id)
            for image in images:
                glanceimage = ''
                image_id = image.image_id
                glanceimg = api.glance.image_get(self.request, str(image_id))
                glanceimage = glanceimg.name
                setattr(image, 'glanceimage', glanceimage)
                
        except:
            images = []
            msg = _('Image list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in images:
            n.set_id_as_name_if_empty()
        return images

class CreateImageView(workflows.WorkflowView):
    workflow_class = CreateImage
    template_name = 'nova/images/create.html'

    def get_initial(self):
        pass
    
class UpdateImageView(forms.ModalFormView):
    form_class = UpdateImage
    template_name = 'nova/images/update.html'
    context_object_name = 'image'
    success_url = reverse_lazy("horizon:nova:images:index")

    def get_context_data(self, **kwargs):
        context = super(UpdateImageView, self).get_context_data(**kwargs)
        context["image_id"] = self.kwargs['image_id']
        return context

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            image_id = self.kwargs['image_id']
            try:
                self._object = api.quantum.image_get(self.request,
                                                       image_id)
            except:
                redirect = self.success_url
                msg = _('Unable to retrieve image details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object
    
    def get_initial(self):
        image = self._get_object()
        return {'image_id': image['id'],
                'tenant_id': image['tenant_id'],
                'name': image['name']}

class DetailImageView(tabs.TabView):
    tab_group_class = ImageDetailTabs
    template_name = 'nova/images/detail.html'
