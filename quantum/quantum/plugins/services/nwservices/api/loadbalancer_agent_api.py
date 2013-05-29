# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Mirantis Inc.
# All Rights Reserved
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
# @author: Ilya Shakhat, Mirantis Inc.

import abc


class LoadbalancerAgentAPI(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def create_vip(self, context, device, vip):
        pass

    @abc.abstractmethod
    def update_vip(self, context, device, new_vip, old_vip):
        pass

    @abc.abstractmethod
    def delete_vip(self, context, device, vip):
        pass

    @abc.abstractmethod
    def create_pool(self, context, device, pool):
        pass

    @abc.abstractmethod
    def update_pool(self, context, device, new_pool, old_pool):
        pass

    @abc.abstractmethod
    def delete_pool(self, context, device, pool):
        pass

    @abc.abstractmethod
    def create_member(self, context, device, member):
        pass

    @abc.abstractmethod
    def update_member(self, context, device, new_member, old_member):
        pass

    @abc.abstractmethod
    def delete_member(self, context, device, member):
        pass

    @abc.abstractmethod
    def create_health_monitor(self, context, device, healthmonitor, pool_id):
        pass

    @abc.abstractmethod
    def delete_health_monitor(self, context, device, healthmonitor, pool_id):
        pass

    @abc.abstractmethod
    def get_pool_stats(self, context, device, pool_id):
        pass
