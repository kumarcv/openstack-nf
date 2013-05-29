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

from quantum.common.exceptions import QuantumException


class ServiceDriverException(QuantumException):
    message = 'An unknown error occurred in service driver.'


class BaseServiceDriver(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_service_type(self):
        """
        Return the service type handled by the driver, i.e. "LOADBALANCER".
        :return: service type: string
        """
        pass

    @abc.abstractmethod
    def get_type(self):
        """
        Return the type of the driver, that value used for driver
        identification.
        :return: driver type: string
        """
        pass

    @abc.abstractmethod
    def get_version(self):
        """
        Return the version of the driver, i.e. "1.0".
        :return: driver version
        """
        pass

    def __str__(self):
        return '%(st)s:%(t)s:%(v)s' % {'st': self.get_service_type(),
                                       't': self.get_type(),
                                       'v': self.get_version()}
