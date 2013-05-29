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
from horizon import tabs


LOG = logging.getLogger(__name__)


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = "syspanel/imagemaps/_detail_overview.html"

    def get_context_data(self, request):
        image_id = self.tab_group.kwargs['image_id']
        try:
            image = api.quantum.image_get(self.request, image_id)
            image.category = api.quantum.category_get(self.request,
                                                      image.category_id)
            image.vendor = api.quantum.vendor_get(self.request,
                                                      image.vendor_id)
            image.full_flavor = api.flavor_get(self.request,
                                                      image.flavor_id)
            image.security_group = api.security_group_get(
                                           self.request, image.security_group_id)
            image.glance_image = api.glance.image_get(self.request,
                                                      image.image_id)
            metadata = api.quantum.metadata_list_for_image(self.request,
                                                      image_id)
            image.metadata = api.quantum.metadata_get(self.request,
                                                      metadata[0].id)
            personality = api.quantum.personality_list_for_image(self.request,
                                                      image_id)
            image.personality = api.quantum.personality_get(self.request,
                                                      personality[0].id)
            
        except:
            redirect = reverse('horizon:syspanel:imagemaps:index')
            msg = _('Unable to retrieve image map details.')
            exceptions.handle(request, msg, redirect=redirect)
        return {'image': image}


class ImageDetailTabs(tabs.TabGroup):
    slug = "image_details"
    tabs = (OverviewTab,)
