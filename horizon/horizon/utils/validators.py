# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Nebula, Inc.
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

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

horizon_config = getattr(settings, "HORIZON_CONFIG", {})
password_config = horizon_config.get("password_validator", {})


def validate_port_range(port):
    if port not in range(-1, 65536):
        raise ValidationError("Not a valid port number")


def password_validator():
    return password_config.get("regex", ".*")


def password_validator_msg():
    return password_config.get("help_text", _("Password is not accepted"))
