# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
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

import abc

from quantum.extensions import extensions


class ServicePluginBase(extensions.PluginInterface):
    """ defines base interface for any Advanced Service plugin """
    __metaclass__ = abc.ABCMeta
    supported_extension_aliases = []

    @abc.abstractmethod
    def get_plugin_type(self):
        """ returns one of predefine service types. see
            quantum/plugins/common/constants.py """
        pass

    @abc.abstractmethod
    def get_plugin_name(self):
        """ return a symbolic name for the plugin.

        Each service plugin should have a symbolic name. This name
        will be used, for instance, by service definitions in service types
        """
        pass

    @abc.abstractmethod
    def get_plugin_description(self):
        """ returns string description of the plugin """
        pass
