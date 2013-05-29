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
from horizon import workflows
from horizon import exceptions
from horizon import api
from horizon import tabs
from horizon import tables
from .forms import CreateMonitor, EditMonitor

LOG = logging.getLogger(__name__)

class CreateView(forms.ModalFormView):
    form_class = CreateMonitor
    template_name = 'nova/loadbalancers/pools/monitors/create.html'
    success_url = 'horizon:nova:loadbalancers:detail'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['pool_id'],))

    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                pool_id = self.kwargs["pool_id"]
                self._object = api.quantum.pool_get(self.request,
                                                       pool_id)
            except:
                redirect = reverse('horizon:nova:loadbalancers:pools')
                msg = _("Unable to retrieve Pool.")
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['pool'] = self.get_object()
        return context

    def get_initial(self):
        pool = self.get_object()
        return {"pool_id": self.kwargs['pool_id'],
                "pool_name": pool.name}
        
class UpdateView(forms.ModalFormView):
    form_class = EditMonitor
    template_name = 'nova/loadbalancers/pools/monitors/update.html'
    context_object_name = 'monitor'
    success_url = reverse_lazy('horizon:nova:loadbalancers:detail')

    def get_success_url(self):
        return reverse('horizon:nova:loadbalancers:detail',
                       args=(self.kwargs['pool_id'],))

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            monitor_id = self.kwargs['monitor_id']
            try:
                self._object = api.quantum.monitor_get(self.request, monitor_id)
            except:
                redirect = reverse("horizon:nova:loadbalancers:pools")
                msg = _('Unable to retrieve Health Monitor details')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        monitor = self._get_object()
        context['monitor_id'] = monitor.id
        context['pool_id'] = monitor.pool_id
        context['type'] = monitor.type
        context['delay'] = monitor.delay
        context['timeout'] = monitor.timeout
        context['max_retries'] = monitor.max_retries
        context['http_method'] = monitor.http_method
        context['url_path'] = monitor.url_path
        context['expected_codes'] = monitor.expected_codes
        return context

    def get_initial(self):
        monitor = self._get_object()
        return {'pool_id': self.kwargs['pool_id'],
                'monitor_id': monitor['id'],
                'type': monitor['type'],
                'delay': monitor['delay'],
                'timeout': monitor['timeout'],
                'max_retries': monitor['max_retries'],
                'http_method': monitor['http_method'],
                'url_path': monitor['url_path'],
                'expected_codes': monitor['expected_codes']}