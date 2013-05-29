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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import forms
from horizon import messages


LOG = logging.getLogger(__name__)


class CreateChain(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    type = forms.ChoiceField(label=_("Type"), widget = forms.Select(), 
                     choices = ([('L2-Mode','L2-Mode'), ('L3-Mode','L3-Mode'), ]), initial='L2-Mode', required = True,)
    auto_boot = forms.BooleanField(label=_("Auto Boot "),
                                     initial=False, required=False)
    def handle(self, request, data):
        try:
            sg = api.quantum.chain_create(request,
                                           name=data['name'],
                                           type=data['type'],
                                           auto_boot=data['auto_boot'])
            
            messages.success(request,
                             _('Successfully created Chain: %s')
                               % data['name'])
            return sg
        except:
            redirect = reverse("horizon:nova:chains:index")
            exceptions.handle(request,
                              _('Unable to create Chain.'),
                              redirect=redirect)
            
            
class UpdateChain(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    tenant_id = forms.CharField(widget=forms.HiddenInput)
    chain_id = forms.CharField(label=_("ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    failure_url = 'horizon:nova:chains:index'

    def handle(self, request, data):
        try:
            chain = api.quantum.chain_modify(request, data['chain_id'],
                                                 name=data['name'])
            msg = _('Chain %s was successfully updated.') % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return chain
        except:
            msg = _('Failed to update chain %s') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
            
class LaunchChain(forms.SelfHandlingForm):
    chain_id = forms.CharField(label=_("ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    name = forms.CharField(label=_("name"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    def handle(self, request, data):
        try:
            chain_id = data['chain_id']
            
            
            
            chain_images = api.quantum.chain_image_list_for_chain(self.request,
                                                       chain_id)
            for chain_image in chain_images:
                name = chain_image.name
                chian_image_id = chain_image.id
                image_map_id = chain_image.image_map_id
                image = api.quantum.image_get(self.request,
                                                   image_map_id)
                glance_image_id = image.image_id
                flavor_id = image.flavor_id
                security_group_id = image.security_group_id
                security_groups = []
                secgrp = api.nova.security_group_get(self.request, image.security_group_id)
                security_group_name = secgrp.name
                security_groups.append(security_group_name)
                chain_confs = api.quantum.chain_image_conf_list_for_chain(self.request,
                                                   chian_image_id)
                
                chain_networks = api.quantum.chain_image_network_list_for_chain(self.request,
                                                   chian_image_id)
                netids = []
                for chain_network in chain_networks:
                    network_id = chain_network.network_id
                    netids.append(network_id)
                if netids:
                    nics = [{"net-id": netid, "v4-fixed-ip": ""}
                            for netid in netids]
                else:
                    nics = None
                    msg = _('Failed to launch chain  %s, No Network associated') % data['chain_id']
                    LOG.info(msg)
                    redirect = reverse(self.failure_url)
                    exceptions.handle(request, msg, redirect=redirect)
                
                
                chain_confs = api.quantum.chain_image_conf_list_for_chain(self.request,
                                                   chian_image_id)
                for chain_conf in chain_confs:
                    config_handle_id = chain_conf.config_handle_id
                    if(config_handle_id == ''):
                        msg = _('Failed to launch chain  %s, No Cnfiguration associated') % data['chain_id']
                        LOG.info(msg)
                        redirect = reverse(self.failure_url)
                        exceptions.handle(request, msg, redirect=redirect)
                        
                    
                
                
                dev_mapping = None
                custom_script = None
                keypair_id = None
                instance_count = 1
                instance = api.nova.server_create(self.request,
                               name,
                               glance_image_id,
                               flavor_id,
                               keypair_id,
                               custom_script,
                               security_groups,
                               dev_mapping,
                               nics=nics,
                               instance_count=int(instance_count))
                msg = _('Instance %s was successfully launched.') % instance.id
                LOG.debug(msg)
                messages.success(request, msg)
                instance_uuid = instance.id
                instance = api.nova.server_get(self.request, instance_uuid)
                instance_name = getattr(instance,'OS-EXT-SRV-ATTR:instance_name','')
                instance_id = int(instance_name.split('instance-')[1],16)
                host = getattr(instance,'OS-EXT-SRV-ATTR:host','')
                
                api.quantum.chain_image_modify(request, chian_image_id,
                                                 instance_uuid=instance_uuid,
                                                 instance_id=instance_id)
                
                for chain_conf in chain_confs:
                    config_handle_id = chain_conf.config_handle_id
                    str1 = api.quantum.launch_chain(self.request,
                                             config_handle_id)                  
                
                
            
            return instance
        except:
            msg = _('Failed to launch chain %s') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
