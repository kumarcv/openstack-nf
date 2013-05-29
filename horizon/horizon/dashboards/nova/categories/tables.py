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


class CheckCategoryEditable(object):
    """Mixin class to determine the specified category is editable."""

    def allowed(self, request, datum=None):
        # Only administrator is allowed to create and manage shared categories.
        if datum and datum.shared:
            return False
        return True


class DeleteCategory(CheckCategoryEditable, tables.DeleteAction):
    data_type_singular = _("Category")
    data_type_plural = _("Categories")

    def delete(self, request, category_id):
        try:
           
            api.quantum.category_delete(request, category_id)
            LOG.debug('Deleted category %s successfully' % category_id)
        except:
            msg = _('Failed to delete category %s') % category_id
            LOG.info(msg)
            redirect = reverse("horizon:nova:categories:index")
            exceptions.handle(request, msg, redirect=redirect)


class CreateCategory(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Category")
    url = "horizon:nova:categories:create"
    classes = ("ajax-modal", "btn-create")


class EditCategory(CheckCategoryEditable, tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Category")
    url = "horizon:nova:categories:update"
    classes = ("ajax-modal", "btn-edit")


class CategoriesTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"))
    description = tables.Column("description", verbose_name=_("Description"))
    shared = tables.Column("shared", verbose_name=_("Shared"),
                           filters=(filters.yesno, filters.capfirst))
    networkfunction = tables.Column("networkfunction", verbose_name=_("Network Functions"))
    
    class Meta:
        name = "categories"
        verbose_name = _("Categories")
        table_actions = (CreateCategory, DeleteCategory)
        row_actions = (EditCategory, DeleteCategory)
