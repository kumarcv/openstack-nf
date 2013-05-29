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

from quantum.common import topics
from quantum.openstack.common import log as logging
from quantum.plugins.common import constants
from quantum.openstack.common import context
from quantum import context as q_context
from quantum.openstack.common.rpc import proxy
from quantum.openstack.common import rpc
from quantum.openstack.common.rpc import dispatcher
from quantum.db.nwservices import nwservices_db
from quantum.db import models_v2
from novaclient.v1_1 import client as nova_client
from keystoneclient.v2_0 import client as keystone_client
from quantum.common import exceptions as q_exc
from quantum.openstack.common import cfg
import time


LOG = logging.getLogger(__name__)

class NwservicesDriver(proxy.RpcProxy):
    """
        Network Services Driver is used for following tasks:
            1. Application VM Monitoring. To dynamically start service VMs when one or more applications are brought up
            2. Service VM Load Monitoring. To dynamically check for service VM load, dynamically spawn new service VMs if require
            and share the load to new service VM
            3. Inform corresponding relay agent when there is any configuration change.
    """
    # default RPC API version
    BASE_RPC_API_VERSION = '1.0'

    _instance = None

    def __init__(self,topic=topics.NWSERVICES_PLUGIN):
        super(NwservicesDriver,self).__init__(topic=topic,default_version=self.BASE_RPC_API_VERSION)
        self.context = q_context.Context('quantum', 'quantum',
                                                   is_admin=False)
        self.setup_rpc()


    def setup_rpc(self):
        # RPC support
        self.rpc_context = context.RequestContext('quantum', 'quantum',
                                                   is_admin=False)
        self.conn = rpc.create_connection(new=True)
        self.dispatcher = dispatcher.RpcDispatcher([self])
        self.conn.create_consumer(self.topic, self.dispatcher,fanout=False)
        # Consume from all consumers in a thread
        self.conn.consume_in_thread()
        
    def get_instance_details(self,config_handle_id,timeout=300):
        LOG.debug('In get_instance_details config_id = %s****************** sairam ************\n\n' % config_handle_id)
        self.db = nwservices_db.NwservicePluginDb()
        
        try:
            chain_image_confs = self.db.get_chain_image_confs(self.context, filters = dict(config_handle_id=[config_handle_id]))[0]
        except IndexError:
            raise q_exc.InstanceNotFound(config_handle_id=config_handle_id)
        LOG.debug("chain image confs %s" % (str(chain_image_confs)))
        chain_map_id=chain_image_confs['chain_map_id']
        
        chain_image = self.db.get_chain_image(self.context, chain_map_id)
        instance_uuid=chain_image['instance_uuid']
        if instance_uuid == '':
            raise q_exc.InstanceNotFound(config_handle_id=config_handle_id)
        LOG.debug('instance uuid = %s' % chain_image['instance_uuid'])

        try:
            LOG.debug(_("waiting for instance to be active..."))
            instance_id, tenant_id, hostname = self.wait_for_instance_active(instance_uuid)
        except q_exc.InstanceErrorState,msg:
            LOG.error(_(msg))
            raise q_exc.InstanceNotFound(config_handle_id=config_handle_id)
        LOG.debug(_('tenant id = %s, instance id = %s hostname=%s'),tenant_id,str(instance_id),hostname)
        return tenant_id,instance_id,hostname

    def wait_for_instance_active(self,instance_uuid,timeout=300):
        LOG.debug('Looping for 300 secs')
        for i in range(0,timeout):
            time.sleep(1)
            LOG.debug('After Sleep.')
            nt = novaclient()
            LOG.debug('novaclient = %s' % str(nt))
            try:
                instance_details = nt.servers.get(instance_uuid)
            except Exception,msg:
                LOG.error(msg)
                raise q_exc.InstanceErrorState(instance_uuid=instance_uuid)
            LOG.debug(_('VM state = %s'),instance_details.__getattribute__('OS-EXT-STS:vm_state'))
            LOG.debug('tenant id = %s' % instance_details.__getattribute__('tenant_id'))
            if instance_details.__getattribute__('OS-EXT-STS:vm_state') == 'active':
                LOG.debug('vm state is active')
                instance_id = int(instance_details.__getattribute__('OS-EXT-SRV-ATTR:instance_name').split('instance-')[1],16)
                tenant_id = instance_details.__getattribute__('tenant_id') 
                hostname = instance_details.__getattribute__('OS-EXT-SRV-ATTR:host') 
                return instance_id,tenant_id,hostname
            elif instance_details.__getattribute__('OS-EXT-STS:vm_state') == 'error':
                raise q_exc.InstanceErrorState(instance_id=instance_uuid)
        
    def prepare_msg(self,instance_id,tenant_id,msg):
        m = self.make_msg('config_update',
                      instance_id=instance_id,
                      tenant_id=tenant_id,
                      config_request=msg)
        LOG.debug(_('msg framed in NwServicesDriver = %s\n\n'),str(m))
        return m
    
    def _get_relay_topic_name(self,hostname):
        return '%s.%s' % (topics.RELAY_AGENT,hostname)

    def send_cast(self,logical_id,msg):
        LOG.debug('In send_cast ****************** sairam ************\n\n')
        try:
            tenant_id,instance_id,hostname = self.get_instance_details(logical_id)
            LOG.debug(_('sending cast to machine %s\n\n'),self._get_relay_topic_name(hostname))
            self.cast(self.rpc_context,self.prepare_msg(instance_id,tenant_id,msg),topic=self._get_relay_topic_name(hostname))
        except q_exc.InstanceNotFound,msg:
            LOG.error(msg)

    @classmethod
    def send_rpc_msg(cls,logical_id,msg):
        LOG.debug('In send_rpc_msg ****************** sairam ************')
        driver = cls.get_instance()
        driver.send_cast(logical_id,msg)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
def novaclient():
    LOG.debug(cfg.CONF.NWSDRIVER.admin_user)
    LOG.debug(cfg.CONF.NWSDRIVER.admin_password)
    LOG.debug(cfg.CONF.NWSDRIVER.admin_tenant_name)
    LOG.debug(cfg.CONF.NWSDRIVER.auth_url)
    return  nova_client.Client(cfg.CONF.NWSDRIVER.admin_user,
                               cfg.CONF.NWSDRIVER.admin_password,
                               cfg.CONF.NWSDRIVER.admin_tenant_name,
                               auth_url=cfg.CONF.NWSDRIVER.auth_url,
                               service_type="compute")

