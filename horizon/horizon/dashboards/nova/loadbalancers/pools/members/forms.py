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
import netaddr

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import forms
from horizon import messages
from horizon import exceptions
from horizon.utils import fields


LOG = logging.getLogger(__name__)


class CreateMember(forms.SelfHandlingForm):
    pool_name = forms.CharField(label=_("Pool Name"),
                                   required=False,
                                   widget=forms.TextInput(
                                       attrs={'readonly': 'readonly'}))
    pool_id = forms.CharField(label=_("Pool ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    ip_address = forms.CharField(max_length=80, label=_("IP Address"),
                          required=True,
                          initial="",
                          help_text=_("IP Address "
                                      "(e.g. 192.168.0.0)"))
    port_no = forms.CharField(max_length=80,
                              label=_("Port Number"), required=True)
    weight = forms.CharField(max_length=80, label=_("Weight"),
                                  required=True,
                                  help_text=_("Weight should be between 1-256"))
    failure_url = 'horizon:nova:pools:detail'

    def handle(self, request, data):
        try:
            LOG.debug('params = %s' % data)
            member = api.quantum.member_create(request, **data)
            msg = _('Pool Member %s was successfully created.') % data['ip_address']
            LOG.debug(msg)
            messages.success(request, msg)
            return member
        except Exception:
            msg = _('Failed to create Pool Member %s') % data['ip_address']
            LOG.info(msg)
            redirect = reverse(self.failure_url, args=[data['pool_id']])
            exceptions.handle(request, msg, redirect=redirect)


class EditMember(forms.SelfHandlingForm):
    pool_id = forms.CharField(label=_("Pool ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    member_id = forms.CharField(label=_("Pool Member ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    ip_address = forms.CharField(max_length=80, label=_("IP Address"),
                          required=True,
                          initial="",
                          help_text=_("IP Address "
                                      "(e.g. 192.168.0.0)"))
    port_no = forms.CharField(max_length=80,
                              label=_("Port Number"), required=True)
    weight = forms.CharField(max_length=80, label=_("Weight"),
                                  required=True,
                                  help_text=_("Weight should be between 1-256"))
    failure_url = 'horizon:nova:pools:detail'

    def clean(self):
        cleaned_data = super(EditMember, self).clean()
        #ip_version = int(cleaned_data.get('ip_version'))
        #gateway_ip = cleaned_data.get('gateway_ip')
        #if gateway_ip:
        #    if netaddr.IPAddress(gateway_ip).version is not ip_version:
        #        msg = _('Gateway IP and IP version are inconsistent.')
        #        raise forms.ValidationError(msg)
        return cleaned_data

    def handle(self, request, data):
        try:
            LOG.debug('params = %s' % data)
            member = api.quantum.member_modify(request, data['member_id'],
                                               ip_address=data['ip_address'],
                                               port_no=data['port_no'],
                                               weight=data['weight'])
            msg = _('Pool Member %s was successfully updated.') % data['member_id']
            LOG.debug(msg)
            messages.success(request, msg)
            return member
        except Exception:
            msg = _('Failed to update Pool Member %s') % data['member_id']
            LOG.info(msg)
            redirect = reverse(self.failure_url, args=[data['pool_id']])
            exceptions.handle(request, msg, redirect=redirect)
            
class DeleteConfig(forms.SelfHandlingForm):
    service_id = forms.CharField(widget=forms.HiddenInput())
    config_id = forms.CharField(widget=forms.HiddenInput())
    
    failure_url = 'horizon:nova:pools:detail'

    def clean(self):
        cleaned_data = super(DeleteConfig, self).clean()
        #ip_version = int(cleaned_data.get('ip_version'))
        #gateway_ip = cleaned_data.get('gateway_ip')
        #if gateway_ip:
        #    if netaddr.IPAddress(gateway_ip).version is not ip_version:
        #        msg = _('Gateway IP and IP version are inconsistent.')
        #        raise forms.ValidationError(msg)
        return cleaned_data
    
    def handle(self, request, data):
        try:
            LOG.debug('params = %s' % data)
            #params = {'name': data['name']}
            #params['gateway_ip'] = data['gateway_ip']
            config = api.quantum.dhcp_config_delete(request, data['config_id'])
            msg = _('IP Pool %s was successfully deleted.') % data['config_id']
            LOG.debug(msg)
            config = True
            messages.success(request, msg)
            return config
        except Exception:
            msg = _('Failed to delete IP Pool %s') % data['config_id']
            LOG.info(msg)
            redirect = reverse(self.failure_url, args=[data['service_id']])
            exceptions.handle(request, msg, redirect=redirect)
            

class CreateNetwork(forms.SelfHandlingForm):
    service_id = forms.CharField(label=_("Service ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    net_name = forms.CharField(label=_("Network Name"),
                                   required=True)
    name = forms.CharField(max_length=255,
                           label=_("Subnet Name"),
                           required=False)
    cidr = fields.IPField(label=_("Network Address"),
                          required=True,
                          initial="",
                          help_text=_("Network address in CIDR format "
                                      "(e.g. 192.168.0.0/24)"),
                          version=fields.IPv4 | fields.IPv6,
                          mask=True)
    ip_version = forms.ChoiceField(choices=[(4, 'IPv4'), (6, 'IPv6')],
                                   label=_("IP Version"))
    gateway_ip = fields.IPField(label=_("Gateway IP"),
                                required=False,
                                initial="",
                                help_text=_("IP address of Gateway "
                                            "(e.g. 192.168.0.1)"),
                                version=fields.IPv4 | fields.IPv6,
                                mask=False)
    failure_url = 'horizon:nova:pools:detail'

    def clean(self):
        cleaned_data = super(CreateNetwork, self).clean()
        cidr = cleaned_data.get('cidr')
        ip_version = int(cleaned_data.get('ip_version'))
        gateway_ip = cleaned_data.get('gateway_ip')
        if cidr:
            if netaddr.IPNetwork(cidr).version is not ip_version:
                msg = _('Network Address and IP version are inconsistent.')
                raise forms.ValidationError(msg)
        if gateway_ip:
            if netaddr.IPAddress(gateway_ip).version is not ip_version:
                msg = _('Gateway IP and IP version are inconsistent.')
                raise forms.ValidationError(msg)
        return cleaned_data

    def handle(self, request, data):
        try:
            network = api.quantum.network_create(request,
                                                 name=data['net_name'])
            network.set_id_as_name_if_empty()
            msg = _('Network "%s" was successfully created.') % network.name
            LOG.debug(msg)
        except:
            msg = _('Failed to create network "%s".') % data['net_name']
            LOG.info(msg)
            redirect = reverse('horizon:nova:pools:index')
            exceptions.handle(request, msg, redirect=redirect)
            return False
        
        try:
            params = {'network_id': network.id,
                      'name': data['name'],
                      'cidr': data['cidr'],
                      'ip_version': int(data['ip_version']),
		      'enable_dhcp': 0}
            if data['gateway_ip']:
                params['gateway_ip'] = data['gateway_ip']
            subnet = api.quantum.subnet_create(request, **params)
	    ##This is to insert into dhcp_server_pools table in quantum
	    service_id = data['service_id']
	    service_name = 'DHCP'
	    net = netaddr.IPNetwork(data['cidr'])
	    net1 = netaddr.ip.IPNetwork(data['cidr'])
	    first_ip = net.first + 2
	    last_ip = net.last - 1
	    
	    pools = []
	    
	    subnet = str(net1.ip)
	    netmask = str(net1.netmask)
	    start_ip = str(netaddr.IPAddress(first_ip))
	    end_ip = str(netaddr.IPAddress(last_ip))
	    primary_name_server = ''
	    secondary_name_server = ''
	    domain_name = ''
	    routers = ''
	    pools = {'subnet': subnet,
			  'service_id': service_id,
			  'service_name': service_name,
			  'netmask': netmask,
			  'start_ip': start_ip,
			  'end_ip': end_ip,
			  'lease_time': None,
			  'primary_name_server': primary_name_server,
			  'secondary_name_server': secondary_name_server,
			  'domain_name': domain_name,
			  'routers': routers}
	    try:
		dhcp_config = api.quantum.dhcp_config_create(request, **pools)
	    except Exception:
		msg = _('Failed to add ippool "%(ippool)s" for service "%(serv)s".')
		redirect = reverse('horizon:nova:networks:index')
		exceptions.handle(request,
				  msg % {"ippool": pools['subnet'], "serv": service_id},
				  redirect=redirect)
		return False
	    
            msg = _('Subnet "%s" was successfully created.') % data['cidr']
            LOG.debug(msg)
            messages.success(request, msg)
            return subnet
        except Exception:
            msg = _('Failed to create subnet "%(sub)s" for network "%(net)s".')
            redirect = reverse('horizon:nova:networks:index')
            exceptions.handle(request,
                              msg % {"sub": data['cidr'], "net": network.id},
                              redirect=redirect)
            return False
