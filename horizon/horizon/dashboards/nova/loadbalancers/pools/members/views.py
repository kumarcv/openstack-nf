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
from .forms import CreateMember
from .forms import EditMember
from .forms import DeleteConfig
from .tabs import ConfigDetailTabs
from .forms import CreateNetwork

LOG = logging.getLogger(__name__)


class CreateView(forms.ModalFormView):
    form_class = CreateMember
    template_name = 'nova/loadbalancers/pools/members/create.html'
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
                redirect = reverse('horizon:nova:pools:index')
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
    form_class = EditMember
    template_name = 'nova/loadbalancers/pools/members/update.html'
    context_object_name = 'member'
    success_url = reverse_lazy('horizon:nova:loadbalancers:detail')

    def get_success_url(self):
        return reverse('horizon:nova:loadbalancers:detail',
                       args=(self.kwargs['pool_id'],))

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            member_id = self.kwargs['member_id']
            try:
                self._object = api.quantum.member_get(self.request, member_id)
            except:
                redirect = reverse("horizon:nova:loadbalancers:pools")
                msg = _('Unable to retrieve Pool Member details')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        member = self._get_object()
        context['member_id'] = member.id
        context['pool_id'] = member.pool_id
        context['ip_address'] = member.ip_address
        context['port_no'] = member.port_no
        context['weight'] = member.weight
        return context

    def get_initial(self):
        pool = self._get_object()
        return {'pool_id': self.kwargs['pool_id'],
                'member_id': pool['id'],
                'ip_address': pool['ip_address'],
                'port_no': pool['port_no'],
                'weight': pool['weight']}
        
class DeleteView(forms.ModalFormView):
    form_class = DeleteConfig
    template_name = 'nova/pools/members/delete.html'
    context_object_name = 'config'
    success_url = reverse_lazy('horizon:nova:pools:detail')

    def get_success_url(self):
        return reverse('horizon:nova:pools:detail',
                       args=(self.kwargs['service_id'],))

    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            config_id = self.kwargs['config_id']
            try:
                self._object = api.quantum.config_get(self.request, config_id)
            except:
                redirect = reverse("horizon:nova:pools:detail")
                msg = _('Unable to retrieve IP Pool details')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        config = self._get_object()
        context['config_id'] = config.id
        context['service_id'] = config.service_id
        return context

    def get_initial(self):
        config = self._get_object()
        return {'service_id': self.kwargs['service_id'],
                'config_id': config['id'],}

class DetailView(tabs.TabView):
    tab_group_class = ConfigDetailTabs
    template_name = 'nova/pools/members/detail.html'
    
    
###
###BEGIN - Srikanth Modifications
###This is to Create Networks from Pools Page
###
"""
class CreateNetworkView(workflows.WorkflowView):
    workflow_class = CreateNetwork
    template_name = 'nova/pools/createnet.html'

    def get_initial(self):
        initial = super(CreateNetworkView, self).get_initial()
        initial['project_id'] = self.request.user.tenant_id
        initial['user_id'] = self.request.user.id
        return initial
""" 
class CreateNetworkView(forms.ModalFormView):
    form_class = CreateNetwork
    template_name = 'nova/pools/members/createnet.html'
    success_url = 'horizon:nova:pools:detail'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.kwargs['service_id'],))

    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                service_id = self.kwargs["service_id"]
                self._object = api.quantum.service_get(self.request,
                                                       service_id)
            except:
                redirect = reverse('horizon:nova:pools:index')
                msg = _("Unable to retrieve service.")
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(CreateNetworkView, self).get_context_data(**kwargs)
        context['service'] = self.get_object()
        return context

    def get_initial(self):
        service = self.get_object()
        return {"service_id": self.kwargs['service_id'],
                "service_name": service.name}
    
###
###END - Srikanth Modifications
###