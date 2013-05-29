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

STATUS_OK = 'OK'
STATUS_ERROR = 'ERROR'


class LoadbalancerPluginAPI(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def confirm_device(self, context, device, status, message):
        pass

    @abc.abstractmethod
    def confirm(self, context, model, obj_id, status, message):
        pass

    @abc.abstractmethod
    def store_pool_stats(self, context, obj_id, data, status, message):
        pass
