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

class CreateVIPInfoAction(workflows.Action):
    PROTOCOL_CHOICES = (
        ("", _("Select Protocol")),
        ("HTTP", _("HTTP")),
        ("HTTPS", _("HTTPS")),
        ("TCP", _("TCP")),
    )

    config_handle_id = forms.CharField(label=_("Configuration ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    name = forms.CharField(max_length=50, label=_("Name"),
                          required=True,
                          initial="")
    description = forms.CharField(max_length=15, label=_("Description"),
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

    class Meta:
        name = ("Standard Info")
        help_text = _("From here you can create a new Virtual IP.\n"
                      ""
                      "")
	
    def populate_pool_id_choices(self, request, context):
	tenant_id = self.request.user.tenant_id
        pools = api.quantum.pool_list(request, tenant_id=tenant_id)
        choices = []
        for pool in pools:
            choices.append([pool.id, pool.name])
        if choices:
            choices.insert(0, ("", _("Select Pool")))
            pass
        else:
            choices.insert(0, ("", _("No images available.")))
        return choices

class CreateVIPInfo(workflows.Step):
    action_class = CreateVIPInfoAction
    contributes = ("name", "description", "port_no", "protocol", "connection_limit",
       "config_handle_id", "pool_id",)

class SessionPersistanceInfoAction(workflows.Action):
    TYPE_CHOICES = (
        ("", _("Select Type")),
        #("SOURCE_IP", _("SOURCE IP")),
        ("HTTP_COOKIE", _("HTTP COOKIE")),
        #("APP_COOKIE", _("APP COOKIE")),
    )

    type = forms.ChoiceField(label=_("Type"),
                                    choices=TYPE_CHOICES,
                                    required=False)
    cookie_name = forms.CharField(max_length=1024, label=_("Cookie Name"),
                          required=False,
                          initial="")
    
    class Meta:
        name = ("Session Persistance")
        help_text = _("From here you can create a new Virtual IP.\n"
                      ""
                      "")
	
    def populate_pool_id_choices(self, request, context):
	tenant_id = self.request.user.tenant_id
        pools = api.quantum.pool_list(request, tenant_id=tenant_id)
        choices = []
        for pool in pools:
            choices.append([pool.id, pool.name])
        if choices:
            choices.insert(0, ("", _("Select Pool")))
            pass
        else:
            choices.insert(0, ("", _("No Pools available.")))
        return choices

class SessionPersistanceInfo(workflows.Step):
    action_class = SessionPersistanceInfoAction
    contributes = ("type", "cookie_name",)
    
class CreateVirtualIP(workflows.Workflow):
    slug = "create_vip"
    name = _("Create Virtual IP")
    finalize_button_name = _("Create")
    success_message = _('Created Virtual IP "%s".')
    failure_message = _('Unable to create Virtual IP "%s".')
    success_url = "horizon:nova:loadbalancers:listvips"
    default_steps = (CreateVIPInfo,
		     SessionPersistanceInfo,
                    )
    failure_url = 'horizon:nova:loadbalancers:listvips'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.context.get('config_handle_id'),))

    def format_status_message(self, message):
        name = self.context.get('name') or self.context.get('config_handle_id', '')
        return message % name

    def handle(self, request, data):
        # create the Virtual IP
        try:
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
		vip = api.quantum.vip_create(request, **data_params)
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
		    vip = api.quantum.vip_create(request, **data_params)
		    return True
		else:
		    return False
        except:
	    exceptions.handle(request)
            return False