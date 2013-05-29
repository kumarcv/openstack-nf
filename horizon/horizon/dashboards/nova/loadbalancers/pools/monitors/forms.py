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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import forms
from horizon import messages
from horizon import exceptions
from horizon.utils import fields


LOG = logging.getLogger(__name__)

class CreateMonitor(forms.SelfHandlingForm):
    TYPE_CHOICES = (
        #("", _("Select Type")),
        #("PING", _("PING")),
        ("HTTP", _("HTTP")),
        #("HTTPS", _("HTTPS")),
        #("TCP", _("TCP")),
    )
    
    HTTP_METHODS = (
        ("", _("Default")),
        ("GET", _("GET")),
        ("POST", _("POST")),
    )
    pool_name = forms.CharField(label=_("Pool Name"),
                                   required=False,
                                   widget=forms.TextInput(
                                       attrs={'readonly': 'readonly'}))
    pool_id = forms.CharField(label=_("Pool ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    type = forms.ChoiceField(label=_("Type"),
                                    choices=TYPE_CHOICES, required=True)
    delay = forms.CharField(max_length=80,
                              label=_("Delay"), required=True)
    timeout = forms.CharField(max_length=80, label=_("Timeout"),
                                  required=True)
    max_retries = forms.CharField(max_length=80, label=_("Max. Retries"),
                          required=True,
                          initial="")
    http_method = forms.ChoiceField(label=_("HTTP Method"),
                        choices=HTTP_METHODS,
                        required=False)
    url_path = forms.CharField(max_length=255, label=_("URL Path"),
                                  required=False)
    expected_codes = forms.CharField(max_length=64, label=_("Expected Codes"),
                                  required=False)
    failure_url = 'horizon:nova:pools:detail'

    def handle(self, request, data):
        try:
            LOG.debug('params = %s' % data)
            monitor = api.quantum.monitor_create(request, **data)
            msg = _('Health Monitor %s was successfully created.') % data['type']
            LOG.debug(msg)
            messages.success(request, msg)
            return monitor
        except Exception:
            msg = _('Failed to create Pool Member %s') % data['type']
            LOG.info(msg)
            redirect = reverse(self.failure_url, args=[data['pool_id']])
            exceptions.handle(request, msg, redirect=redirect)
            
class EditMonitor(forms.SelfHandlingForm):
    TYPE_CHOICES = (
        #("", _("Select Type")),
        #("PING", _("PING")),
        ("HTTP", _("HTTP")),
        #("HTTPS", _("HTTPS")),
        #("TCP", _("TCP")),
    )
    
    HTTP_METHODS = (
        ("", _("Default")),
        ("GET", _("GET")),
        ("POST", _("POST")),
    )
    pool_id = forms.CharField(label=_("Pool ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    monitor_id = forms.CharField(label=_("Health Monitor ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    type = forms.ChoiceField(label=_("Type"),
                                    choices=TYPE_CHOICES, required=True)
    delay = forms.CharField(max_length=80,
                              label=_("Delay"), required=True)
    timeout = forms.CharField(max_length=80, label=_("Timeout"),
                                  required=True)
    max_retries = forms.CharField(max_length=80, label=_("Max. Retries"),
                          required=True,
                          initial="")
    http_method = forms.ChoiceField(label=_("HTTP Method"),
                        choices=HTTP_METHODS,
                        required=False)
    url_path = forms.CharField(max_length=255, label=_("URL Path"),
                                  required=False)
    expected_codes = forms.CharField(max_length=64, label=_("Expected Codes"),
                                  required=False)
    failure_url = 'horizon:nova:pools:detail'

    def clean(self):
        cleaned_data = super(EditMonitor, self).clean()
        #ip_version = int(cleaned_data.get('ip_version'))
        #gateway_ip = cleaned_data.get('gateway_ip')
        #if gateway_ip:
        #    if netaddr.IPAddress(gateway_ip).version is not ip_version:
        #        msg = _('Gateway IP and IP version are inconsistent.')
        #        raise forms.ValidationError(msg)
        return cleaned_data

    def handle(self, request, data):
        try:
            LOG.debug('params = %s' % data)
            monitor = api.quantum.monitor_modify(request, data['monitor_id'],
                                               type=data['type'],
                                               delay=data['delay'],
                                               timeout=data['timeout'],
                                               max_retries=data['max_retries'],
                                               http_method=data['http_method'],
                                               url_path=data['url_path'],
                                               expected_codes=data['expected_codes'])
            msg = _('Health Monitor %s was successfully updated.') % data['monitor_id']
            LOG.debug(msg)
            messages.success(request, msg)
            return monitor
        except Exception:
            msg = _('Failed to update Health Monitor %s') % data['monitor_id']
            LOG.info(msg)
            redirect = reverse(self.failure_url, args=[data['pool_id']])
            exceptions.handle(request, msg, redirect=redirect)
