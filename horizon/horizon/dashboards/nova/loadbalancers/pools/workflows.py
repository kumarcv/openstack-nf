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
import netaddr
import re

from django.utils.text import normalize_newlines
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from horizon import api
from horizon import exceptions
from horizon import forms
from horizon import workflows
from horizon.utils import fields
from horizon.openstack.common import jsonutils


LOG = logging.getLogger(__name__)


class CreatePoolInfoAction(workflows.Action):
    PROTOCOL_CHOICES = (
        ("", _("Select Protocol")),
        ("HTTP", _("HTTP")),
        ("HTTPS", _("HTTPS")),
        ("TCP", _("TCP")),
    )
    
    ALGORITHM_CHOICES = (
        ("", _("Select Algorithm")),
        ("ROUNDROBIN", _("Round Robin")),
        ("LEASTCONN", _("Least Connections")),
        ("STATIC-RR", _("Static Round Robin")),
        ("SOURCE", _("Source")),
    )
    pool_name = forms.CharField(label=_("Pool Name"),
                                  required=True,
                                  initial="",
                                  help_text=_("Name of the Pool"))
    description = forms.CharField(label=_("Description"),
                                  required=False,
                                  initial="")
    subnet_id = forms.ChoiceField(label=_("Subnet"), required=True)
    protocol = forms.ChoiceField(label=_("Protocol"),
                                    required=True,
                                    choices=PROTOCOL_CHOICES)
    lb_method = forms.ChoiceField(label=_("LB Method"),
                                    required=True,
                                    choices=ALGORITHM_CHOICES)
    
    class Meta:
        name = ("Pool")
        help_text = _("From here you can create a new Pool.\n"
                      ""
                      "")
        
    def populate_subnet_id_choices(self, request, context):
	tenant_id = self.request.user.tenant_id
        subnets = api.quantum.subnet_list(request, tenant_id=tenant_id)
        #subnets = []
        choices = [(subnet.id, subnet.cidr)
                   for subnet in subnets]
        if choices:
            choices.insert(0, ("", _("Select Subnet")))
        else:
            choices.insert(0, ("", _("No subnets available.")))
            ###Need to Remove once code merged###
            #choices.insert(1, ("1b5bf493-be0c-43e8-9755-4c43e8e65862", _("Load Balancer")))
        return choices


class CreatePoolInfo(workflows.Step):
    action_class = CreatePoolInfoAction
    contributes = ("pool_name", "description", "subnet_id", "protocol", "lb_method", )

class CreatePool(workflows.Workflow):
    slug = "create_pool"
    name = _("Create Pool")
    finalize_button_name = _("Create")
    success_message = _('Created pool "%s".')
    failure_message = _('Unable to create Pool "%s".')
    success_url = "horizon:nova:loadbalancers:pools"
    default_steps = (CreatePoolInfo,
                    )

    def format_status_message(self, message):
        name = self.context.get('pool_name') or self.context.get('pool_id', '')
        return message % name

    def handle(self, request, data):
        try:
	    ###Check if a service is available with the name
	    tenant_id = self.request.user.tenant_id
	    is_pool = api.quantum.pool_list_for_tenant(request, tenant_id, 
                                                 name=data['pool_name'],
						 description=data['description'],
						 subnet_id=data['subnet_id'],
						 protocol=data['protocol'],
						 lb_method=data['lb_method'])
	    #####
	    if is_pool:
		return False
	    else:
		pool = api.quantum.pool_create(request,
						     name=data['pool_name'],
						     description=data['description'],
						     subnet_id=data['subnet_id'],
						     protocol=data['protocol'],
						     lb_method=data['lb_method'])
		pool.set_id_as_name_if_empty()
		self.context['pool_id'] = pool.id
		msg = _('Pool "%s" was successfully created.') % pool.id
		LOG.debug(msg)
        except:
            msg = _('Failed to create Pool "%s".') % data['pool_name']
            LOG.info(msg)
            redirect = reverse('horizon:nova:loadbalancers:pools')
            exceptions.handle(request, msg, redirect=redirect)
            return False

        return True
