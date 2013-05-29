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
from django.template import defaultfilters as filters
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import tables


LOG = logging.getLogger(__name__)


class CheckVendorEditable(object):
    """Mixin class to determine the specified vendor is editable."""

    def allowed(self, request, datum=None):
        # Only administrator is allowed to create and manage shared vendors.
        if datum and datum.shared:
            return False
        return True


class DeleteVendor(CheckVendorEditable, tables.DeleteAction):
    data_type_singular = _("Vendor")
    data_type_plural = _("Vendors")

    def delete(self, request, vendor_id):
        try:
            
            api.quantum.vendor_delete(request, vendor_id)
            LOG.debug('Deleted vendor %s successfully' % vendor_id)
        except:
            msg = _('Failed to delete vendor %s') % vendor_id
            LOG.info(msg)
            redirect = reverse("horizon:nova:vendors:index")
            exceptions.handle(request, msg, redirect=redirect)


class CreateVendor(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Vendor")
    url = "horizon:nova:vendors:create"
    classes = ("ajax-modal", "btn-create")


class EditVendor(CheckVendorEditable, tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Vendor")
    url = "horizon:nova:vendors:update"
    classes = ("ajax-modal", "btn-edit")


class VendorsTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"))
    description = tables.Column("description", verbose_name=_("Description"))
    shared = tables.Column("shared", verbose_name=_("Shared"),
                           filters=(filters.yesno, filters.capfirst))
    
    class Meta:
        name = "vendors"
        verbose_name = _("Vendors")
        table_actions = (CreateVendor, DeleteVendor)
        row_actions = (EditVendor, DeleteVendor)
