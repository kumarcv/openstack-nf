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

class BaseVIPForm(forms.SelfHandlingForm):
    def __init__(self, request, *args, **kwargs):
        super(BaseVIPForm, self).__init__(request, *args, **kwargs)
        # Populate pool choices
        pool_choices = [('', _("Select a Pool"))]
        tenant_id = self.request.user.tenant_id

        for pool in api.quantum.pool_list(request, tenant_id=tenant_id):
	    pool_choices.append((pool.id, pool.name))
        self.fields['pool_id'].choices = pool_choices


class UpdateVirtualIP(BaseVIPForm):
    PROTOCOL_CHOICES = (
        ("", _("Select Protocol")),
        ("HTTP", _("HTTP")),
        ("HTTPS", _("HTTPS")),
        ("TCP", _("TCP")),
    )
    
    TYPE_CHOICES = (
        ("", _("Select Type")),
        #("SOURCE_IP", _("SOURCE IP")),
        ("HTTP_COOKIE", _("HTTP COOKIE")),
        #("APP_COOKIE", _("APP COOKIE")),
    )
    
    config_handle_id = forms.CharField(label=_("Configuration ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    vip_id = forms.CharField(label=_("Virtual IP ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    name = forms.CharField(max_length=50, label=_("Name"),
                          required=True,
                          initial="")
    description = forms.CharField(max_length=255, label=_("Description"),
                          required=False,
                          initial="")
    port_no = forms.CharField(label=_("Port Number"),
                               required=True,
                               help_text=_("Port Number."))
    protocol = forms.ChoiceField(label=_("Protocol"),
                                    choices=PROTOCOL_CHOICES,
                                    required=True)
    connection_limit = forms.CharField(label=_("Connection Limit"),
                               required=False,
                               help_text=_("Connection Limit."))
    pool_id = forms.ChoiceField(label=_("Pool"), required=True)

    type = forms.ChoiceField(label=_("Session Persistance Type"),
                                    choices=TYPE_CHOICES,
                                    required=False)
    cookie_name = forms.CharField(max_length=1024, label=_("Cookie Name"),
                          required=False,
                          initial="")
    failure_url = 'horizon:nova:loadbalancers:listvips'
	
    def clean(self):
	cleaned_data = super(UpdateVirtualIP, self).clean()
	return cleaned_data

    def handle(self, request, data):
        try:
            LOG.debug('params = %s' % data)
	    #Get Session Persistance ID
	    session_type = data['type']
	    session_cookie = data['cookie_name']
	    session_data = {'type': session_type,
			    'cookie_name': session_cookie,
			    }
	    sessions = api.quantum.session_list(request)
	    session_id = False
	    if sessions:
		for session in sessions:
		    if session.type == session_type and session.cookie_name == session_cookie:
			session_id = session.id
			break
		    
	    if session_id:
		data_params = {'pool_id': data['pool_id'],
                      'session_persistance_id': session_id,
                      'name': data['name'],
                      'description': data['description'],
		      'port_no': data['port_no'],
		      'protocol': data['protocol'],
                      'connection_limit': data['connection_limit'],
		      'config_handle_id': data['config_handle_id']}
		vip = api.quantum.vip_modify(request, data['vip_id'], **data_params)
		return True
	    else:
		sess = api.quantum.session_create(request, **session_data)
		sessions = api.quantum.session_list(request)
		for session in sessions:
		    if session.type == session_type and session.cookie_name == session_cookie:
			session_id = session.id
			break
		
		if session_id:
		    data_params = {'pool_id': data['pool_id'],
			'session_persistance_id': session_id,
			'name': data['name'],
			'description': data['description'],
			'port_no': data['port_no'],
			'protocol': data['protocol'],
			'connection_limit': data['connection_limit'],
			'config_handle_id': data['config_handle_id']}
		    vip = api.quantum.vip_modify(request, data['vip_id'], **data_params)
		    msg = _('Virtual IP %s was successfully updated.') % data['vip_id']
		    LOG.debug(msg)
		    messages.success(request, msg)
		    return True
		else:
		    return False
        except Exception:
            msg = _('Failed to update Virtual IP %s') % data['vip_id']
            LOG.info(msg)
            redirect = reverse(self.failure_url, args=[data['config_handle_id']])
            exceptions.handle(request, msg, redirect=redirect)