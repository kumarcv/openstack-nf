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

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import workflows

from .tables import PoolsTable
from .forms import UpdatePool
from .members.tables import PoolMembersTable
from .monitors.tables import PoolMonitorsTable
from .workflows import CreatePool

LOG = logging.getLogger(__name__)

class IndexView(tables.DataTableView):
    table_class = PoolsTable
    template_name = 'nova/loadbalancers/pools/index.html'

    def get_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            pools = api.quantum.pool_list_for_tenant(self.request,
                                                           tenant_id)
        except:
            pools = []
            msg = _('Pool list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in pools:
            n.set_id_as_name_if_empty()
        return pools


class CreateView(workflows.WorkflowView):
    workflow_class = CreatePool
    template_name = 'nova/loadbalancers/pools/create.html'

    def get_initial(self):
        pass

class UpdateView(forms.ModalFormView):
    form_class = UpdatePool
    template_name = 'nova/loadbalancers/pools/update.html'
    context_object_name = 'pool'
    success_url = reverse_lazy('horizon:nova:loadbalancers:pools')

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context["pool_id"] = self.kwargs['pool_id']
        return context
    
    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            pool_id = self.kwargs['pool_id']
            try:
                self._object = api.quantum.pool_get(self.request, pool_id)
            except:
                redirect = self.success_url
                msg = _('Unable to retrieve Pool details')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_initial(self):
        pool = self._get_object()
        return {'pool_id': pool['id'],
                'tenant_id': pool['tenant_id'],
                'name': pool['name'],
		'description': pool['description'],
                'subnet_id': pool['subnet_id'],
		'protocol': pool['protocol'],
                'lb_method': pool['lb_method']}
    
class DetailView(tables.MultiTableView):
    table_classes = (PoolMembersTable, PoolMonitorsTable)
    template_name = 'nova/loadbalancers/pools/detail.html'
    failure_url = reverse_lazy('horizon:nova:loadbalancers:pools')

    def get_members_data(self):
        try:
	    ##FSL - Get the Pool Details first.
	    tenant_id = self.request.user.tenant_id
            pool = self._get_data()
            members = api.quantum.member_list(self.request,
							tenant_id,
							pool_id=pool.id)
        except:
            members = []
            msg = _('Pool Member list can not be retrieved.')
            exceptions.handle(self.request, msg)
	for dc in members:
            dc.set_id_as_name_if_empty()
        return members

    def get_monitors_data(self):
        try:
	    pool_id = self.kwargs['pool_id']
	    tenant_id = self.request.user.tenant_id
            monitors = api.quantum.monitor_list(self.request,
							tenant_id,
							pool_id=pool_id)
        except:
            monitors = []
            msg = _('Health Monitors list can not be retrieved.')
            exceptions.handle(self.request, msg)
	for mn in monitors:
            mn.set_id_as_name_if_empty()
	    
        return monitors

    def _get_data(self):
	if not hasattr(self, "_pool"):
	    try:
		pool_id = self.kwargs['pool_id']
		pool = api.quantum.pool_get(self.request, pool_id)
		pool.set_id_as_name_if_empty(length=0)
	    except:
		msg = _('Unable to retrieve details for Pool "%s".') \
		       % (pool_id)
		exceptions.handle(self.request, msg)
	    
	    self._pool = pool
        return self._pool

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["pool"] = self._get_data()
        return context