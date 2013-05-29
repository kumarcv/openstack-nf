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


class UpdateImage(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    tenant_id = forms.CharField(widget=forms.HiddenInput)
    image_id = forms.CharField(label=_("ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    failure_url = 'horizon:nova:images:index'

    def handle(self, request, data):
        try:
            image = api.quantum.image_modify(request, data['image_id'],
                                                name=data['name'])
            msg = _('Image %s was successfully updated.') % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return image
        except:
            msg = _('Failed to update image %s') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
