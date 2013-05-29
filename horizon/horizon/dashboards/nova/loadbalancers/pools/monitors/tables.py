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

class AddMonitor(tables.LinkAction):
    name = "addmonitor"
    verbose_name = _("Add Health Monitor")
    url = "horizon:nova:loadbalancers:addmonitor"
    classes = ("ajax-modal", "btn-create")

    def get_link_url(self, datum=None):
        pool_id = self.table.kwargs['pool_id']
        return reverse(self.url, args=(pool_id,))
        
class DeleteMonitor(tables.DeleteAction):
    data_type_singular = _("Monitor")
    data_type_plural = _("Monitors")

    def delete(self, request, monitor_id):
        try:
            api.quantum.monitor_delete(request, monitor_id)
        except:
            msg = _('Failed to delete monitor %s') % monitor_id
            LOG.info(msg)
            pool_id = self.table.kwargs['pool_id']
            redirect = reverse('horizon:nova:loadbalancers:detail',
                               args=[pool_id])
            exceptions.handle(request, msg, redirect=redirect)
            
class EditMonitor(tables.LinkAction):
    name = "editmonitor"
    verbose_name = _("Edit Health Monitor")
    url = "horizon:nova:loadbalancers:editmonitor"
    classes = ("ajax-modal", "btn-edit")

    def get_link_url(self, pool):
        pool_id = self.table.kwargs['pool_id']
        return reverse(self.url, args=(pool_id, pool.id))

class PoolMonitorsTable(tables.DataTable):
    type = tables.Column("type", verbose_name=_("Type"))
    delay = tables.Column("delay", verbose_name=_("Delay"))
    timeout = tables.Column("timeout", verbose_name=_("Timeout"))
    max_retries = tables.Column("max_retries", verbose_name=_("Max. Retries"))
    http_method = tables.Column("http_method", verbose_name=_("HTTP Method"))
    url_path = tables.Column("url_path", verbose_name=_("URL Path"))
    expected_codes = tables.Column("expected_codes", verbose_name=_("Expected Codes"))
    
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
        name = "monitors"
        verbose_name = _("Health Monitors")
        table_actions = (AddMonitor, DeleteMonitor, )
        row_actions = (EditMonitor, DeleteMonitor, )