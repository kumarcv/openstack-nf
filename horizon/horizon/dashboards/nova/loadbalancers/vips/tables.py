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

from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import tables


LOG = logging.getLogger(__name__)

class CreateVirtualIP(tables.LinkAction):
    name = "addvip"
    verbose_name = _("Add Virtual IP")
    url = "horizon:nova:loadbalancers:addvip"
    classes = ("ajax-modal", "btn-create")

    def get_link_url(self, datum=None):
        config_id = self.table.kwargs['config_id']
        return reverse(self.url, args=(config_id,))
        
class DeleteVirtualIP(tables.DeleteAction):
    data_type_singular = _("Virtual IP")
    data_type_plural = _("Virtual IPs")

    def delete(self, request, obj_id):
        try:
            api.quantum.vip_delete(request, obj_id)
        except:
            msg = _('Failed to delete Virtual IP %s') % obj_id
            LOG.info(msg)
            config_id = self.table.kwargs['config_id']
            redirect = reverse('horizon:nova:loadbalancers:listvips',
                               args=[config_id])
            exceptions.handle(request, msg, redirect=redirect)
            
class UpdateVirtualIP(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Virtual IP")
    url = "horizon:nova:loadbalancers:editvip"
    classes = ("ajax-modal", "btn-edit")

    def get_link_url(self, vip):
        config_id = self.table.kwargs['config_id']
        return reverse(self.url, args=(config_id, vip.id))
        
class ListPoolDetails(tables.LinkAction):
    name = "detail"
    verbose_name = _("List Pool Details")
    url = "horizon:nova:loadbalancers:detail"
    
    def get_link_url(self, vip):
        #config_id = self.table.kwargs['config_id']
        return reverse(self.url, args=(vip.pool_id,))

class VIPsTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"))
    description = tables.Column("description", verbose_name=_("Description"))
    port_no = tables.Column("port_no", verbose_name=_("Port Number"))
    protocol = tables.Column("protocol", verbose_name=_("Protocol"))
    connection_limit = tables.Column("connection_limit", verbose_name=_("Connection Limit"))
    session_persistance_type = tables.Column("session_persistance_type", verbose_name=_("Session Type"))
    session_persistance_cookie = tables.Column("session_persistance_cookie", verbose_name=_("Cookie Name"))
    failure_url = reverse_lazy('horizon:nova:loadbalancers:index')

    def _get_configuration(self):
        try:
            config_id = self.kwargs['config_id']
            configuration = api.quantum.config_handle_get(self.request, config_id)
            configuration.set_id_as_name_if_empty(length=0)
        except:
            msg = _('Unable to retrieve details for Configuration "%s".') \
                  % (config_id)
            exceptions.handle(self.request, msg, redirect=self.failure_url)
            
        self._configuration = configuration
        return self._configuration
    
    class Meta:
        name = "vips"
        verbose_name = _("Virtual IPs")
        table_actions = (CreateVirtualIP, DeleteVirtualIP, )
        row_actions = (ListPoolDetails, UpdateVirtualIP, DeleteVirtualIP, )
