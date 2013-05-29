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

class EditMember(tables.LinkAction):
    name = "editmember"
    verbose_name = _("Edit Pool Member")
    url = "horizon:nova:loadbalancers:editmember"
    classes = ("ajax-modal", "btn-edit")

    def get_link_url(self, member):
        pool_id = self.table.kwargs['pool_id']
        return reverse(self.url, args=(pool_id, member.id))


class DeleteMember(tables.DeleteAction):
    data_type_singular = _("Pool Member")
    data_type_plural = _("Pool Members")

    def delete(self, request, member_id):
        try:
            api.quantum.member_delete(request, member_id)
        except:
            msg = _('Failed to delete pool member %s') % member_id
            LOG.info(msg)
            pool_id = self.table.kwargs['pool_id']
            redirect = reverse('horizon:nova:loadbalancers:detail',
                               args=[pool_id])
            exceptions.handle(request, msg, redirect=redirect)

class AddPoolMember(tables.LinkAction):
    name = "createmember"
    verbose_name = _("Add Pool Member")
    url = "horizon:nova:loadbalancers:createmember"
    classes = ("ajax-modal", "btn-create")

    def get_link_url(self, datum=None):
        pool_id = self.table.kwargs['pool_id']
        return reverse(self.url, args=(pool_id,))

class PoolMembersTable(tables.DataTable):
    ip_address = tables.Column("ip_address", verbose_name=_("IP Address"))
    port_no = tables.Column("port_no", verbose_name=_("Port Number"))
    weight = tables.Column("weight", verbose_name=_("Weight"))
    failure_url = reverse_lazy('horizon:nova:loadbalancers:pools')

    def _get_pool(self):
        if not hasattr(self, "_pool"):
            try:
                pool_id = self.kwargs['pool_id']
                pool = api.quantum.pool_get(self.request, pool_id)
                pool.set_id_as_name_if_empty(length=0)
            except:
                msg = _('Unable to retrieve details for Pool "%s".') \
                      % (pool_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)
            self._pool = pool
        return self._pool
    
    class Meta:
        name = "members"
        verbose_name = _("Pool Members")
        table_actions = (AddPoolMember, DeleteMember)
        row_actions = (EditMember, DeleteMember, )
