#!/usr/bin/env python
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
import ast
import socket
import select
import time

import eventlet

from quantumclient.v2_0 import client as qclient
from quantum.openstack.common import cfg
from quantum.openstack.common import log as logging

LOG = logging.getLogger(__name__)
INSTANCES_PATH='/var/lib/nova/instances'

class RemoteControl(object):
    """Relay config class

    This class is capable of mananging configurations in service VMs
    and retrieving its config and stats.
    """

    def __init__(self):
        LOG.debug(_('Instantiating RelayConfig'))
        self.port_fds = {}
        self.user = cfg.CONF.RELAY.admin_user
        self.password = cfg.CONF.RELAY.admin_password
        self.tenant=cfg.CONF.RELAY.admin_tenant
        self.auth_url=cfg.CONF.RELAY.auth_url
        self.endpoint_url=cfg.CONF.RELAY.endpoint_url
        self.epoll = select.epoll()
        self.poll_fn = eventlet.spawn_n(self.poller)


    
    def poller(self):
        while True:
            time.sleep(0.25)
            events = self.epoll.poll(0.25)
            LOG.debug(_('Polling %d events'),len(events))
            LOG.debug('port_fds = %s' % str(self.port_fds))
            for fileno, event in events:
                if event & select.EPOLLIN:
                    self.process_config_request(fileno)

    
    def process_config_request(self,fileno):
        data = self.port_fds[fileno]['tmp_data'] + self.port_fds[fileno]['fd'].recv(65535)
        LOG.debug("data received from VM ...... ************sairam*************\n\n%s\n\n" % data)
        
        try:
            req = ast.literal_eval(data)
            self.port_fds[fileno]['tmp_data'] = ''
            LOG.debug("data received from VM ...... ************sairam*************\n\n%s\n\n" % data)
            if req['method'] == 'hello':
                self.port_fds[fileno]['status_up'] = True
                if self.port_fds[fileno]['conf_up_req'] != '':
		    LOG.debug('sending data to VM............\n\n%s\n\n' % self.port_fds[fileno]['conf_up_req'])
                    self.send_data_to_vm(self.port_fds[fileno]['instance_id'],self.port_fds[fileno]['conf_up_req'])
                    self.port_fds[fileno]['conf_up_req'] = ''
                return
            else:
                try:
                    qc = quantumclient(self.user,self.password,self.tenant,self.auth_url,self.endpoint_url)
                    LOG.debug("quantum client created ......%s *****************sairam****************\n\n" % str(qc))
                    q_data_recv=str(getattr(qc,req['method'])(**req['kwargs']))
                    LOG.debug('data received from quantum client = %s*************************sairam**************\n\n' % q_data_recv)
                    self.port_fds[fileno]['fd'].send(q_data_recv)
                    return
                except Exception,msg:
                    LOG.error(_('Quantumclient Exception...\n\t%s'),msg)
        except SyntaxError,msg:
            LOG.debug(_('Incomplete data received from VM.'))
            self.port_fds[fileno]['tmp_data'] += data
            return


    def connect_vm(self,instance_id):
        fd = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        try:
            fd.connect(INSTANCES_PATH + '/instance-%08x/port' % instance_id)
        except socket.error,msg:
            LOG.debug(_('unable to connect to virtio-serial port. Error: %s'),msg)
            return False
        self.port_fds[fd.fileno()] = {'fd':fd,
                                      'instance_id':instance_id,
                                      'status_up':False,
                                      'tmp_data':'',
                                      'conf_up_req' : '',
                                     }
        LOG.debug("Successfully created virtio-serial socket.")
        self.epoll.register(fd.fileno(),select.EPOLLIN)
        return self.port_fds[fd.fileno()]
    
    def _get_fd_details(self,instance_id):
        for val in self.port_fds.values():
            if val['instance_id'] == instance_id:
                return val
        return False

    def send_data_to_vm(self,instance_id,data=''):
        fd = self._get_fd_details(instance_id)
        if not fd:
            LOG.debug("no socket fd exists.creating.")
            fd = self.connect_vm(instance_id)
            if not fd:
                LOG.debug(_('No VM virtio-serial port exists for instance instance-%08x'),instance_id)
                return False
        LOG.debug('fd details  %s' % str(fd))
        LOG.debug('data = %s' % data)
        if data != '' and fd['status_up']:
            if not fd['fd'].send(data) == len(data):
                LOG.debug(_('Could not Send complete data. Data length = %d'),len(data))
	elif (data != '') and (not fd['status_up']):
            fd['conf_up_req'] = data
	    LOG.debug("VM is not up.......Storing data\n\n%s\n\n" % (fd['conf_up_req']))

    def update_config(self):
        """
        TODO: Configuration Update available event generated at plugin. Need to send this to VM.
        """
def quantumclient(username,password,tenant,auth_url,endpoint_url):
    cl = qclient.Client(username=username,tenant_name=tenant,password=password,auth_url=auth_url,endpoint_url=endpoint_url)
    cl.httpclient.authenticate()
    return cl
