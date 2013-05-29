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

class CreateLBInfoAction(workflows.Action):
    ALGORITHM_CHOICES = (
        ("", _("None")),
        ("roundrobin", _("Round Robin")),
        ("source", _("Source Hash")),
        ("static-rr", _("Static-rr")),
    )
    
    BALANCE_MODE_CHOICES = (
        ("", _("Default")),
        ("http", _("HTTP")),
        ("tcp", _("TCP")),
    )
    
    HTTP_METHODS = (
        ("", _("Default")),
        ("GET", _("GET")),
        ("POST", _("POST")),
    )
    service_id = forms.CharField(label=_("Service ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    name = forms.CharField(max_length=50, label=_("Name"),
                          required=True,
                          initial="")
    server_ip = forms.CharField(max_length=15, label=_("Server IP"),
                          required=True,
                          initial="")
    port_num = forms.IntegerField(label=_("Port Number"),
                               min_value=1,
                               required=True,
                               help_text=_("Port Number."))
    algorithm = forms.ChoiceField(label=_("Algorithm"),
                                    choices=ALGORITHM_CHOICES,
                                    required=True)
    mode = forms.ChoiceField(label=_("Balance Mode"),
                                    choices=BALANCE_MODE_CHOICES,
                                    required=False)
    max_conn = forms.IntegerField(label=_("Max. Connections"),
                               min_value=1,
                               required=False,
                               help_text=_("Maximum Connections."))
    
    class Meta:
        name = ("Standard Info")
        help_text = _("From here you can create a new SLB Configuration.\n"
                      ""
                      "")


class CreateLBInfo(workflows.Step):
    action_class = CreateLBInfoAction
    contributes = ("name", "service_id", "server_ip", "port_num", "algorithm",
		   "mode", "max_conn",)

class ProtoTestsInfoAction(workflows.Action):
    HTTP_METHODS = (
        ("", _("Default")),
        ("GET", _("GET")),
        ("POST", _("POST")),
    )
    
    http_check = forms.BooleanField(label=_("HTTP Check"),
                                     initial=False, required=False)
    http_method = forms.ChoiceField(label=_("HTTP Method"),
                        choices=HTTP_METHODS,
                        required=False)
    http_url = forms.CharField(max_length=50, label=_("HTTP URL"),
                          required=False,
                          initial="")
    ssl_check = forms.BooleanField(label=_("SSL Check"),
                                     initial=False, required=False)

    class Meta:
        name = ("Protocol Tests")
        help_text = _("From here you can create a new SLB Configuration.\n"
                      ""
                      "")


class ProtoTestsInfo(workflows.Step):
    action_class = ProtoTestsInfoAction
    contributes = ("http_check", "http_method", "http_url",
		   "ssl_check",)

class HTTPOptionsInfoAction(workflows.Action):
    insert_cookie = forms.BooleanField(label=_("Insert Cookie"),
                                     initial=False, required=False)
    cookie_name = forms.CharField(max_length=255, label=_("Cookie Name"),
                          required=False,
                          initial="")
    cookie_option_indirect = forms.BooleanField(label=_("Cookie Option Indirect"),
                                     initial=False, required=False)
    cookie_option_rewrite = forms.BooleanField(label=_("Cookie Option Rewrite"),
                                     initial=False, required=False)
    cookie_option_insert = forms.BooleanField(label=_("Cookie Option Insert"),
                                     initial=False, required=False)
    cookie_option_nocache = forms.BooleanField(label=_("Cookie Option Nocache"),
                                     initial=False, required=False)
    cookie_option_prefix = forms.BooleanField(label=_("Cookie Option Prefix"),
                                     initial=False, required=False)
    cookie_option_postonly = forms.BooleanField(label=_("Cookie Option Postonly"),
                                     initial=False, required=False)

    class Meta:
        name = ("HTTP Options")
        help_text = _("From here you can create a new SLB Configuration.\n"
                      ""
                      "")


class HTTPOptionsInfo(workflows.Step):
    action_class = HTTPOptionsInfoAction
    contributes = ("insert_cookie", "cookie_name", "cookie_option_indirect",
		   "cookie_option_rewrite", "cookie_option_insert", "cookie_option_nocache",
		   "cookie_option_prefix", "cookie_option_postonly",)

class CreateLBConfig(workflows.Workflow):
    slug = "create_lb"
    name = _("Create SLB Configuration")
    finalize_button_name = _("Create")
    success_message = _('Created SLB Configuration "%s".')
    failure_message = _('Unable to create SLB Configuration "%s".')
    success_url = "horizon:nova:pools:detail"
    default_steps = (CreateLBInfo,
		     ProtoTestsInfo,
		     HTTPOptionsInfo,
                    )
    failure_url = 'horizon:nova:pools:detail'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.context.get('service_id'),))
	
    def format_status_message(self, message):
        name = self.context.get('name') or self.context.get('service_id', '')
        return message % name

    def handle(self, request, data):
        # create the SLB Configuration
        try:
	    lb_config = api.quantum.lb_config_create(request, **data)
	    return True
        except:
	    exceptions.handle(request)
            return False

class StandardInfoServerAction(workflows.Action):
    SERVER_TYPES = (
        ("primary", _("Primary")),
        ("backup", _("Backup")),
    )
    
    config_id = forms.CharField(label=_("Config ID"),
                                   required=False,
                                   widget=forms.TextInput(
                                       attrs={'readonly': 'readonly'}))
    name = forms.CharField(max_length=50, label=_("Server Name"),
                          required=True,
                          initial="")
    server_ip = forms.CharField(max_length=15, label=_("Server IP"),
                          required=True,
                          initial="")
    port_num = forms.IntegerField(label=_("Port Number"),
                               min_value=1,
                               required=True,
                               help_text=_("Port Number."))
    server_type = forms.ChoiceField(label=_("Server Type"),
                                    choices=SERVER_TYPES,
                                    required=False)
    cookie_str = forms.CharField(max_length=50, label=_("Cookie String"),
                          required=False,
                          initial="")

    class Meta:
        name = ("Standard Options")
        help_text = _("From here you can add standard\n"
                      "options to create a new Server."
                      "")


class StandardInfoServer(workflows.Step):
    action_class = StandardInfoServerAction
    contributes = ("config_id", "name", "server_ip",
		   "port_num", "server_type", "cookie_str")

class HealthChecksInfoAction(workflows.Action):
    HEALTH_CHECKS = (
        (1, _("On")),
        (0, _("Off")),
    )
    
    http_redirect = forms.CharField(max_length=255, label=_("HTTP Redirect"),
                          required=False,
                          initial="")
    health_check = forms.BooleanField(label=_("Health Check"),
                                     initial=False, required=False)
    fall_count = forms.IntegerField(label=_("Fall Count"),
                               min_value=0,
                               required=False)
    rise_count = forms.IntegerField(label=_("Rise Count"),
                               min_value=0,
                               required=False)
    interval = forms.IntegerField(label=_("Interval"),
                               min_value=0,
                               required=False)

    class Meta:
        name = ("Health Checks")
        help_text = _("From here you can add some \n"
                      "Health Check options of a Server."
                      "")


class HealthChecksInfo(workflows.Step):
    action_class = HealthChecksInfoAction
    contributes = ("http_redirect", "health_check", "fall_count",
		   "rise_count", "interval")

class CreateLBServer(workflows.Workflow):
    slug = "create_lb_server"
    name = _("Create Server")
    finalize_button_name = _("Create")
    success_message = _('Created Server "%s".')
    failure_message = _('Unable to create Server "%s".')
    success_url = "horizon:nova:pools:monitors:detail"
    default_steps = (StandardInfoServer,
		     HealthChecksInfo,
                    )
    failure_url = 'horizon:nova:pools:monitors:detail'

    def get_success_url(self):
        return reverse(self.success_url,
                       args=(self.context.get('config_id'),))
	
    def format_status_message(self, message):
        name = self.context.get('name') or self.context.get('config_id', '')
        return message % name

    def handle(self, request, data):
        # create the SLB Server
        try:
	    lb_server = api.quantum.lb_server_create(request, **data)
	    return True
        except:
	    exceptions.handle(request)
            return False