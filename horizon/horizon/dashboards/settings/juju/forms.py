# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Openstack, LLC
# Copyright 2012 Canonical Ltd.
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
import tempfile
import zipfile
from contextlib import closing

from django import http, shortcuts
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import forms
from horizon import messages

import boto
import uuid

LOG = logging.getLogger(__name__)


class DownloadJujuEnvironment(forms.SelfHandlingForm):
    # This is heavily based off the ec2 credentials form
    tenant = forms.ChoiceField(label=_("Select a Project"))
    @classmethod
    def _instantiate(cls, request, *args, **kwargs):
        return cls(request, *args, **kwargs)

    def __init__(self, request, *args, **kwargs):
        super(DownloadJujuEnvironment, self).__init__(request, *args, **kwargs)
        tenant_choices = []
        try:
            tenant_list = api.keystone.tenant_list(request)
        except:
            tenant_list = []
            exceptions.handle(request, _("Unable to retrieve tenant list."))

        for tenant in tenant_list:
            if tenant.enabled:
                tenant_choices.append((tenant.id, tenant.name))
        if not tenant_choices:
            self.fields['tenant'].choices = ('', 'No Available Tenants')
        else:
            self.fields['tenant'].choices = tenant_choices

    def handle(self, request, data):
        def find_or_create_access_keys(request, tenant_id):
            keys = api.keystone.list_ec2_credentials(request, request.user.id)
            if keys:
                return keys[0]
            else:
                return api.keystone.create_ec2_credentials(request,
                                                           request.user.id,
                                                           tenant_id)
        try:
            api.keystone.token_create_scoped(request,
                                             data.get('tenant'),
                                             request.user.token.id)
            keys = find_or_create_access_keys(request, data.get('tenant'))
            tenant_id = data['tenant']
            tenant_name = dict(self.fields['tenant'].choices)[tenant_id]
            control_bucket = "juju-openstack-%s-%s" % (tenant_name, str(uuid.uuid4())[19:])
            context = {'ec2_access_key': keys.access,
                       'ec2_secret_key': keys.secret,
                       'ec2_url': api.url_for(request, 'ec2'),
                       's3_url': api.url_for(request, 's3'),
                       'juju_admin_secret': uuid.uuid4().hex,
                       'control_bucket': control_bucket
                      }
        except Exception, e:
            # This will fail if there is not an S3 endpoint configured in the
            # service catalog.
            msg = "Could not generate Juju environment config: %s" % e
            messages.error(request, msg)
            redirect = request.build_absolute_uri()
            raise exceptions.Http302(redirect)

        response = shortcuts.render(request,
                                    'settings/juju/environments.yaml.template',
                                    context,
                                    content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=environments.yaml'
        response['Content-Length'] = str(len(response.content))
        return response
