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

from quantum.openstack.common  import cfg

from quantum.common import exceptions as q_exc
from quantum.openstack.common import importutils
from quantum.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class DriverNotFound(q_exc.NotFound):
    message = _('Driver %(driver_name)s could not be found')


class DuplicateDriver(q_exc.NotFound):
    message = _('Multiple drivers are configured for '
                '%(service_type)s:%(driver_type)s:%(version)s')


class ServiceDriverManager(object):
    _instance = None

    def __init__(self):
        self._load_drivers()

    def _load_drivers(self):
        self.drivers = {}
        drivers = cfg.CONF.service_drivers
        LOG.debug(_('Configured service drivers: "%s"'), drivers)

        for driver in drivers:
            try:
                LOG.debug(_('Loading service driver "%s"'), driver)
                driver_inst = importutils.import_object(driver)
            except ImportError:
                LOG.error(_('Error loading driver "%s"'), driver)
                raise DriverNotFound(driver_name=driver)

            service_type = driver_inst.get_service_type()
            driver_type = driver_inst.get_type()
            version = driver_inst.get_version()
            identity = (service_type, driver_type, version)

            # restrict multiple implementations of the same type and version
            if identity in self.drivers:
                raise DuplicateDriver(service_type=service_type,
                                      driver_type=driver_type, version=version)

            self.drivers[identity] = driver_inst
            LOG.info(_('Service driver "%(driver)s" loaded successfully. '
                       'Driver identity is "%(identity)s"'),
                     {'driver': driver, 'identity': ':'.join(identity)})

    def _get_driver(self, service_type, driver_type, version):
        identity = (service_type, driver_type, version)
        if identity in self.drivers:
            return self.drivers[identity]
        else:
            driver_name = ':'.join(identity)
            LOG.error(_('Driver %s is not found'), driver_name)
            raise DriverNotFound(driver_name=driver_name)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def get_driver(cls, service_type, driver_type, version):
        return cls.get_instance()._get_driver(service_type, driver_type,
                                              version)
