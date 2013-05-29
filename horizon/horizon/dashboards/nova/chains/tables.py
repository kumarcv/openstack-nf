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


class DeleteChain(tables.DeleteAction):
    data_type_singular = _("Chain")
    data_type_plural = _("Chains")

    def delete(self, request, chain_id):
        try:
            api.quantum.chain_delete(request, chain_id)
            LOG.debug('Deleted chain %s successfully' % chain_id)
        except:
            msg = _('Failed to delete chain %s') % chain_id
            LOG.info(msg)
            redirect = reverse("horizon:nova:chains:index")
            exceptions.handle(request, msg, redirect=redirect)


class CreateChain(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Chain")
    url = "horizon:nova:chains:create"
    classes = ("ajax-modal", "btn-create")


class EditChain(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Chain")
    url = "horizon:nova:chains:update"
    classes = ("ajax-modal", "btn-edit")

class AssociateImage(tables.LinkAction):
    name = "mapimg"
    verbose_name = _("Associate Image To Chain")
    url = "horizon:nova:chains:mapimg"
    classes = ("ajax-modal", "btn-create")

class LaunchChain(tables.LinkAction):
    name = "launch"
    verbose_name = _("Launch Chain")
    url = "horizon:nova:chains:launch"
    classes = ("ajax-modal", "btn-edit")   
    

class ChainsTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link='horizon:nova:chains:detail')
    type = tables.Column("type", verbose_name=_("Type"))
    auto_boot = tables.Column("auto_boot", verbose_name=_("Auto Boot"))
    
    class Meta:
        name = "chains"
        verbose_name = _("Chain List")
        table_actions = (CreateChain, DeleteChain)
        row_actions = (EditChain, DeleteChain, AssociateImage, LaunchChain)
        

        
      
