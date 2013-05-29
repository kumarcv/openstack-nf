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

from django import template
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from django.template import defaultfilters as filters
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import tables


LOG = logging.getLogger(__name__)

class DeletePool(tables.DeleteAction):
    data_type_singular = _("Pool")
    data_type_plural = _("Pools")

    def delete(self, request, pool_id):
        try:
            api.quantum.pool_delete(request, pool_id)
            LOG.debug('Deleted pool %s successfully' % pool_id)
        except:
            msg = _('Failed to delete pool %s') % pool_id
            LOG.info(msg)
            redirect = reverse("horizon:nova:loadbalancers:pools")
            exceptions.handle(request, msg, redirect=redirect)


class CreatePool(tables.LinkAction):
    name = "createpool"
    verbose_name = _("Add Pool")
    url = "horizon:nova:loadbalancers:createpool"
    classes = ("ajax-modal", "btn-create")


class EditPool(tables.LinkAction):
    name = "updatepool"
    verbose_name = _("Edit Pool")
    url = "horizon:nova:loadbalancers:updatepool"
    classes = ("ajax-modal", "btn-edit")
    
class ListPoolMembers(tables.LinkAction):
    name = "detail"
    verbose_name = _("List Details")
    url = "horizon:nova:loadbalancers:detail"
    
class AddPoolMember(tables.LinkAction):
    name = "createmember"
    verbose_name = _("Add Pool Member")
    url = "horizon:nova:loadbalancers:createmember"
    classes = ("ajax-modal", "btn-create")

    def get_link_url(self, datum=None):
        pool_id = datum.id
        return reverse(self.url, args=(pool_id,))

class AddMonitor(tables.LinkAction):
    name = "addmonitor"
    verbose_name = _("Add Health Monitor")
    url = "horizon:nova:loadbalancers:addmonitor"
    classes = ("ajax-modal", "btn-create")

    def get_link_url(self, datum=None):
        pool_id = datum.id
        return reverse(self.url, args=(pool_id,))
        
class PoolsTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"))
    description = tables.Column("description", verbose_name=_("Description"))
    subnet = tables.Column("subnet", verbose_name=_("Subnet"))
    protocol = tables.Column("protocol", verbose_name=_("Protocol"))
    lb_method = tables.Column("lb_method", verbose_name=_("LB Method"))

    class Meta:
        name = "pools"
        verbose_name = _("Pools")
        table_actions = (CreatePool, DeletePool)
        row_actions = (ListPoolMembers, EditPool, DeletePool, AddPoolMember, AddMonitor)
