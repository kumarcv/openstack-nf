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
#
# @author: B39208 (b39208@freescale.com)
#

from quantum.openstack.common import cfg
from quantum.openstack.common import importutils
from quantum.openstack.common import log as logging
#from quantum.plugins.services.nwservices.nwservices_driver import NwservicesDriver
from quantum.db.loadbalancer import loadbalancer_db
from quantum.plugins.common import constants
LOG = logging.getLogger(__name__)

class HAProxyDriver():
    """
    The HAProxy Driver class
    The following tasks are done in this calss
    [1] Check for the changes in the SLB configuration and intimates the 
        Network Services driver with the logical UUID, API and other info.
    """
    def __init__(self):
        self.db = loadbalancer_db.LoadbalancerPluginDb()
        self.client_api = "dummpy.api" # TODO (trinath) yet to get the API details
        self.driver = importutils.import_object(cfg.CONF.NWSDRIVER.nwservice_driver)
        LOG.debug(_("Trinath :: Using SLB Scheduler Driver: %s"),str(self.driver))

    def vip_config_update(self,context,vip):
        LOG.debug(_("Trinath::Prepare Virtual_IP update msg."))
        if vip != '':
            self.prepare_update([vip],constants.LB_UPDATE)
        return

    def lb_pool_update(self,context,lb_rec):
        pool_id = lb_rec['id']
        tenant_id = lb_rec['tenant_id']
        vips_record = self.db.check_vip_update(context,pool_id,tenant_id)
        if (vips_record != False):
            self.prepare_update(vips_record,constants.LB_UPDATE)        
            LOG.debug(_("Trinath :: Prepare LB_Config_Update."))
        return

    def lb_config_update(self,context,lb_rec):
        pool_id = lb_rec['pool_id']
        tenant_id = lb_rec['tenant_id']
        vips_record = self.db.check_vip_update(context,pool_id,tenant_id)
        if (vips_record != False):
            self.prepare_update(vips_record,constants.LB_UPDATE)        
            LOG.debug(_("Trinath :: Prepare LB_Config_Update."))
        return

    def lb_session_vips_update(self,context,session_record):
        session_id = session_record['id']
        vips_record = self.db.check_session_vips_update(context,session_id)
        if (vips_record != False):
            LOG.debug(_("Trinath :: Prepare Session Persistance based Update"))
            self.prepare_update(vips_record,constants.LB_UPDATE)
        return 

    def prepare_update(self,vip,method):
        LOG.debug(_("Trinath:: VIP data => %s"),(str(vip)))
        if vip:
            for vip_record in vip:
                update_dict = { "header":"request",
                            "config_handle_id":vip_record['config_handle_id'],
                            "slug":"loadbalancer",
                            "version":"0.0",
                          }
                LOG.debug(_("Trinath :: Notification Data : %s" % str(update_dict)))
                self.send_modified_notification(vip_record['config_handle_id'],{'config':update_dict})
        return

    def send_modified_notification(self,config_handle_id,notify_data):
        LOG.debug(_('Trinath :: Send modified notification to NS Driver: Data: %s' % str(notify_data)))
        self.driver.send_rpc_msg(config_handle_id,notify_data)

