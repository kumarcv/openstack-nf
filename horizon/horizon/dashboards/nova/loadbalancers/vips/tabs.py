# vim: tabstop=4 shiftwidth=4 softtabstop=4

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
    template_name = "nova/loadbalancers/vips/_detail_overview.html"

    def get_context_data(self, request):
        config_id = self.tab_group.kwargs['config_id']
        try:
            config = api.quantum.config_get(self.request, config_id)
        except:
            redirect = reverse('horizon:nova:loadbalancers:index')
            msg = _('Unable to retrieve config details.')
            exceptions.handle(request, msg, redirect=redirect)
        return {'config': config}


class ConfigDetailTabs(tabs.TabGroup):
    slug = "config_details"
    tabs = (OverviewTab,)
