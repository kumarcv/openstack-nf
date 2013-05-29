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
from horizon import forms
from horizon import messages


LOG = logging.getLogger(__name__)

class BasePoolForm(forms.SelfHandlingForm):
    def __init__(self, request, *args, **kwargs):
        super(BasePoolForm, self).__init__(request, *args, **kwargs)
        # Populate subnet choices
        subnet_choices = [('', _("Select a Subnet"))]
        tenant_id = self.request.user.tenant_id

        for subnet in api.quantum.subnet_list(request, tenant_id=tenant_id):
            subnet_choices.append((subnet.id, subnet.cidr))
        self.fields['subnet_id'].choices = subnet_choices

class UpdatePool(BasePoolForm):
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
    pool_id = forms.CharField(label=_("ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    name = forms.CharField(label=_("Pool Name"),
                                  required=True,
                                  initial="",
                                  help_text=_("Name of the Pool"))
    description = forms.CharField(label=_("Description"),
                                  required=False,
                                  initial="",
                                  help_text=_("Description"))
    subnet_id = forms.ChoiceField(label=_("Subnet"), required=True)
    protocol = forms.ChoiceField(label=_("Protocol"),
                                    required=True,
                                    choices=PROTOCOL_CHOICES)
    lb_method = forms.ChoiceField(label=_("LB Method"),
                                    required=True,
                                    choices=ALGORITHM_CHOICES)
    
    tenant_id = forms.CharField(widget=forms.HiddenInput)
        
    failure_url = 'horizon:nova:loadbalancers:pools'

    def handle(self, request, data):
        try:
            LOG.debug('params = %s' % data)
            #params = {'name': data['name']}
            #params['gateway_ip'] = data['gateway_ip']
            pool = api.quantum.pool_modify(request, data['pool_id'],
                                               name=data['name'],
                                               description=data['description'],
                                               subnet_id=data['subnet_id'],
                                               protocol=data['protocol'],
                                               lb_method=data['lb_method'])
            msg = _('Pool %s was successfully updated.') % data['pool_id']
            LOG.debug(msg)
            messages.success(request, msg)
            return pool
        except Exception:
            msg = _('Failed to update Pool %s') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
