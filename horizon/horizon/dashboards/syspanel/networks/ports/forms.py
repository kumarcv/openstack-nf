# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 NEC Corporation
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


class CreatePort(forms.SelfHandlingForm):
    network_name = forms.CharField(label=_("Network Name"),
                                   widget=forms.TextInput(
                                       attrs={'readonly': 'readonly'}))
    network_id = forms.CharField(label=_("Network ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    name = forms.CharField(max_length=255,
                           label=_("Name"),
                           required=False)
    device_id = forms.CharField(max_length=100, label=_("Device ID"),
                                help_text='Device ID attached to the port',
                                required=False)

    def handle(self, request, data):
        try:
            # We must specify tenant_id of the network which a subnet is
            # created for if admin user does not belong to the tenant.
            network = api.quantum.network_get(request, data['network_id'])
            data['tenant_id'] = network.tenant_id

            port = api.quantum.port_create(request, **data)
            msg = _('Port %s was successfully created.') % port['id']
            LOG.debug(msg)
            messages.success(request, msg)
            return port
        except:
            msg = _('Failed to create a port for network %s') \
                  % data['network_id']
            LOG.info(msg)
            redirect = reverse('horizon:syspanel:networks:detail',
                               args=(data['network_id'],))
            exceptions.handle(request, msg, redirect=redirect)


class UpdatePort(forms.SelfHandlingForm):
    network_id = forms.CharField(widget=forms.HiddenInput())
    tenant_id = forms.CharField(widget=forms.HiddenInput())
    port_id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(max_length=255,
                           label=_("Name"),
                           required=False)
    device_id = forms.CharField(max_length=100, label=_("Device ID"),
                                help_text='Device ID attached to the port',
                                required=False)

    def handle(self, request, data):
        try:
            LOG.debug('params = %s' % data)
            port = api.quantum.port_modify(request, data['port_id'],
                                           name=data['name'],
                                           device_id=data['device_id'])
            msg = _('Port %s was successfully updated.') % data['port_id']
            LOG.debug(msg)
            messages.success(request, msg)
            return port
        except Exception:
            msg = _('Failed to update port %s') % data['port_id']
            LOG.info(msg)
            redirect = reverse('horizon:syspanel:networks:detail',
                               args=[data['network_id']])
            exceptions.handle(request, msg, redirect=redirect)
