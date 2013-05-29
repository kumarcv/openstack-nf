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

from .tables import ConfigurationsTable
from .forms import UpdateConfig, GenerateConfig
from .vips.tables import VIPsTable
from .workflows import CreateConfiguration

LOG = logging.getLogger(__name__)

class IndexView(tables.DataTableView):
    table_class = ConfigurationsTable
    template_name = 'nova/loadbalancers/index.html'

    def get_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            configurations = api.quantum.config_handle_list_for_tenant(self.request,
                                                           tenant_id)
	    for config in configurations:
		nwfname = ''
                nwf_id = config.networkfunction_id
                nwfunction = api.quantum.networkfunction_get(self.request, str(nwf_id))
                nwfname = nwfunction.name
                setattr(config, 'nwfname', nwfname)
        except:
            configurations = []
            msg = _('Configuration list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in configurations:
            n.set_id_as_name_if_empty()
        return configurations


class CreateView(workflows.WorkflowView):
    workflow_class = CreateConfiguration
    template_name = 'nova/loadbalancers/create.html'

    def get_initial(self):
        pass

class UpdateView(forms.ModalFormView):
    form_class = UpdateConfig
    template_name = 'nova/loadbalancers/update.html'
    context_object_name = 'configuration'
    success_url = reverse_lazy('horizon:nova:loadbalancers:index')

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context["config_id"] = self.kwargs['config_id']
        return context
    
    def _get_object(self, *args, **kwargs):
        if not hasattr(self, "_object"):
            config_id = self.kwargs['config_id']
            try:
                self._object = api.quantum.config_handle_get(self.request, config_id)
            except:
                redirect = self.success_url
                msg = _('Unable to retrieve Configuration details')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self._object

    def get_initial(self):
        configuration = self._get_object()
        return {'config_id': configuration['id'],
                'tenant_id': configuration['tenant_id'],
                'name': configuration['name']}

class VirtualIPListView(tables.DataTableView):
    table_class= VIPsTable
    template_name = 'nova/loadbalancers/vip_index.html'
    failure_url = reverse_lazy('horizon:nova:loadbalancers:index')

    ##FSL - Get Virtual IP List
    def get_data(self):
        try:
	    tenant_id = self.request.user.tenant_id
            configuration = self._get_data()
            vips = api.quantum.vip_list(self.request,
							tenant_id,
							config_handle_id=configuration.id)
        except:
            vips = []
            msg = _('Virtual IP list can not be retrieved.')
            exceptions.handle(self.request, msg)
	for dc in vips:
            dc.set_id_as_name_if_empty()
	    
        return vips

    #FSL - Get Service details
    def _get_data(self):
	if not hasattr(self, "_configuration"):
	    try:
		config_id = self.kwargs['config_id']
		configuration = api.quantum.config_handle_get(self.request, config_id)
		configuration.set_id_as_name_if_empty(length=0)
	    except:
		msg = _('Unable to retrieve details for configuration "%s".') \
		       % (config_id)
		exceptions.handle(self.request, msg)
	    
	    self._configuration = configuration
        return self._configuration

    def get_context_data(self, **kwargs):
        context = super(VirtualIPListView, self).get_context_data(**kwargs)
        context["configuration"] = self._get_data()
        return context
    
class GenerateConfigView(forms.ModalFormView):
    form_class = GenerateConfig
    template_name = 'nova/loadbalancers/delete.html'
    context_object_name = 'genconfig'
    failure_url = reverse_lazy('horizon:nova:loadbalancers:index')

    def _get_object(self, *args, **kwargs):
        config_id = self.kwargs['config_id']
	self._object = api.quantum.config_handle_get(self.request, config_id)
	return self._object

    def get_context_data(self, **kwargs):
        context = super(GenerateConfigView, self).get_context_data(**kwargs)
        config = self._get_object()
        context['config_id'] = config.id
	context['slug'] = config.slug
        return context

    def get_initial(self):
        config = self._get_object()
	return {'config_id': config.id,
		'slug': config.slug,}