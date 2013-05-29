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


class CheckImageEditable(object):
    """Mixin class to determine the specified image is editable."""

    def allowed(self, request, datum=None):
        # Only administrator is allowed to create and manage shared images.
        if datum and datum.shared:
            return False
        return True


class DeleteImage(CheckImageEditable, tables.DeleteAction):
    data_type_singular = _("Image")
    data_type_plural = _("Images")

    def delete(self, request, image_id):
        try:
            api.quantum.image_delete(request, image_id)
            LOG.debug('Deleted image %s successfully' % image_id)
        except:
            msg = _('Failed to delete image %s') % image_id
            LOG.info(msg)
            redirect = reverse("horizon:nova:images:index")
            exceptions.handle(request, msg, redirect=redirect)


class CreateImage(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Image Map")
    url = "horizon:nova:images:create"
    classes = ("ajax-modal", "btn-create")


class EditImage(CheckImageEditable, tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Image")
    url = "horizon:nova:images:update"
    classes = ("ajax-modal", "btn-edit")

def get_category(image):
    context = image.image_map_categories
    return context

def get_vendor(image):
    context = image.image_map_vendors
    return context

def get_image_link(datum):
    view = "horizon:nova:images_and_snapshots:images:detail"
    if datum.image_id:
        return reverse(view, args=(datum.image_id,))
    else:
        return None


class ImagesTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link='horizon:nova:images:detail')
    glanceimage = tables.Column("glanceimage",
                         verbose_name=_("Glance Image"),
                         link=get_image_link)
    category = tables.Column(get_category,
                         verbose_name=_("Category"))
    vendor = tables.Column(get_vendor,
                         verbose_name=_("Vendor"))
    shared = tables.Column("shared", verbose_name=_("Shared"),
                           filters=(filters.yesno, filters.capfirst))
    
    class Meta:
        name = "images"
        verbose_name = _("Service Images")
        table_actions = (CreateImage, DeleteImage)
        row_actions = (EditImage, DeleteImage, )
