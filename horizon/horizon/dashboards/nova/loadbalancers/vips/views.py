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

from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import exceptions
from horizon import api
from horizon import tabs
from horizon import workflows
from .workflows import CreateVirtualIP
from .forms import UpdateVirtualIP

LOG = logging.getLogger(__name__)


class CreateView(workflows.WorkflowView):
    workflow_class = CreateVirtualIP
    template_name = 'nova/loadbalancers/vips/create.html'
    success_url = 'horizon:nova:loadbalancers:listvips'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['config_id'],))

    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                config_id = self.kwargs["config_id"]
                self._object = api.quantum.config_handle_get(self.request,
                                                       config_id)
            except:
                redirect = reverse('horizon:nova:loadbalancers:index')
                msg = _("Unable to retrieve Configuration.")
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['configuration'] = self.get_object()
        return context

    def get_initial(self):
        configuration = self.get_object()
        return {"config_handle_id": self.kwargs['config_id'],
                "config_name": configuration.name}
        
class UpdateView(forms.ModalFormView):
    form_class = UpdateVirtualIP
    template_name = 'nova/loadbalancers/vips/update.html'
    context_object_name = 'vip'
    success_url = reverse_lazy('horizon:nova:loadbalancers:listvips')

    def get_success_url(self):
        return reverse('horizon:nova:loadbalancers:listvips',
                       args=(self.kwargs['config_id'],))

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            vip_id = self.kwargs['vip_id']
            try:
                self._object = api.quantum.vip_get(self.request, vip_id)
            except:
                redirect = reverse("horizon:nova:loadbalancers:index")
                msg = _('Unable to retrieve Virtual IP details')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        vip = self._get_object()
        context['vip_id'] = vip.id
        context['config_handle_id'] = vip.config_handle_id
        context['name'] = vip.name
        context['description'] = vip.description
        context['protocol'] = vip.protocol
        context['port_no'] = vip.port_no
        context['connection_limit'] = vip.connection_limit
        context['pool_id'] = vip.pool_id
        context['session_persistance_id'] = vip.session_persistance_id
        context['type'] = vip.session_persistance_type
        context['cookie_name'] = vip.session_persistance_cookie
        return context

    def get_initial(self):
        vip = self._get_object()
        return {'config_handle_id': self.kwargs['config_id'],
                'vip_id': vip['id'],
                'name': vip['name'],
                'description': vip['description'],
                'protocol': vip['protocol'],
                'port_no': vip['port_no'],
                'connection_limit': vip['connection_limit'],
                'pool_id': vip['pool_id'],
                'session_persistance_id': vip['session_persistance_id'],
                'type': vip['session_persistance_type'],
                'cookie_name': vip['session_persistance_cookie']
                }