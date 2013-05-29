# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 Nicira Networks, Inc
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

"""
Quantum base exception handling.
"""

from quantum.openstack.common.exception import Error
from quantum.openstack.common.exception import OpenstackException


class QuantumException(OpenstackException):
    """Base Quantum Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    """
    message = _("An unknown exception occurred.")


class BadRequest(QuantumException):
    message = _('Bad %(resource)s request: %(msg)s')


class NotFound(QuantumException):
    pass


class NotAuthorized(QuantumException):
    message = _("Not authorized.")


class AdminRequired(NotAuthorized):
    message = _("User does not have admin privileges: %(reason)s")


class PolicyNotAuthorized(NotAuthorized):
    message = _("Policy doesn't allow %(action)s to be performed.")


class ClassNotFound(NotFound):
    message = _("Class %(class_name)s could not be found")


class NetworkNotFound(NotFound):
    message = _("Network %(net_id)s could not be found")


class SubnetNotFound(NotFound):
    message = _("Subnet %(subnet_id)s could not be found")


class PortNotFound(NotFound):
    message = _("Port %(port_id)s could not be found "
                "on network %(net_id)s")


class PolicyNotFound(NotFound):
    message = _("Policy configuration policy.json could not be found")


class StateInvalid(QuantumException):
    message = _("Unsupported port state: %(port_state)s")


class InUse(QuantumException):
    message = _("The resource is inuse")


class NetworkInUse(InUse):
    message = _("Unable to complete operation on network %(net_id)s. "
                "There is one or more ports still in use on the network.")


class SubnetInUse(InUse):
    message = _("Unable to complete operation on subnet %(subnet_id)s. "
                "One or more ports have an IP allocation from this subnet.")


class PortInUse(InUse):
    message = _("Unable to complete operation on port %(port_id)s "
                "for network %(net_id)s. Port already has an attached"
                "device %(device_id)s.")


class MacAddressInUse(InUse):
    message = _("Unable to complete operation for network %(net_id)s. "
                "The mac address %(mac)s is in use.")


class HostRoutesExhausted(QuantumException):
    # NOTE(xchenum): probably make sense to use quota exceeded exception?
    message = _("Unable to complete operation for %(subnet_id)s. "
                "The number of host routes exceeds the limit %(quota)s.")


class DNSNameServersExhausted(QuantumException):
    # NOTE(xchenum): probably make sense to use quota exceeded exception?
    message = _("Unable to complete operation for %(subnet_id)s. "
                "The number of DNS nameservers exceeds the limit %(quota)s.")


class IpAddressInUse(InUse):
    message = _("Unable to complete operation for network %(net_id)s. "
                "The IP address %(ip_address)s is in use.")


class VlanIdInUse(InUse):
    message = _("Unable to create the network. "
                "The VLAN %(vlan_id)s on physical network "
                "%(physical_network)s is in use.")


class FlatNetworkInUse(InUse):
    message = _("Unable to create the flat network. "
                "Physical network %(physical_network)s is in use.")


class TunnelIdInUse(InUse):
    message = _("Unable to create the network. "
                "The tunnel ID %(tunnel_id)s is in use.")


class TenantNetworksDisabled(QuantumException):
    message = _("Tenant network creation is not enabled.")


class ResourceExhausted(QuantumException):
    pass


class NoNetworkAvailable(ResourceExhausted):
    message = _("Unable to create the network. "
                "No virtual network is available.")


class AlreadyAttached(QuantumException):
    message = _("Unable to plug the attachment %(att_id)s into port "
                "%(port_id)s for network %(net_id)s. The attachment is "
                "already plugged into port %(att_port_id)s")


class MalformedRequestBody(QuantumException):
    message = _("Malformed request body: %(reason)s")


class Invalid(Error):
    pass


class InvalidInput(QuantumException):
    message = _("Invalid input for operation: %(error_message)s.")


class InvalidContentType(Invalid):
    message = _("Invalid content type %(content_type)s.")


class InvalidAllocationPool(QuantumException):
    message = _("The allocation pool %(pool)s is not valid.")


class OverlappingAllocationPools(QuantumException):
    message = _("Found overlapping allocation pools:"
                "%(pool_1)s %(pool_2)s for subnet %(subnet_cidr)s.")


class OutOfBoundsAllocationPool(QuantumException):
    message = _("The allocation pool %(pool)s spans "
                "beyond the subnet cidr %(subnet_cidr)s.")


class NotImplementedError(Error):
    pass


class FixedIPNotAvailable(QuantumException):
    message = _("Fixed IP (%(ip)s) unavailable for network "
                "%(network_uuid)s")


class MacAddressGenerationFailure(QuantumException):
    message = _("Unable to generate unique mac on network %(net_id)s.")


class IpAddressGenerationFailure(QuantumException):
    message = _("No more IP addresses available on network %(net_id)s.")


class BridgeDoesNotExist(QuantumException):
    message = _("Bridge %(bridge)s does not exist.")


class PreexistingDeviceFailure(QuantumException):
    message = _("Creation failed. %(dev_name)s already exists.")


class SudoRequired(QuantumException):
    message = _("Sudo priviledge is required to run this command.")


class QuotaResourceUnknown(QuantumException):
    message = _("Unknown quota resources %(unknown)s.")


class OverQuota(QuantumException):
    message = _("Quota exceeded for resources: %(overs)s")


class InvalidQuotaValue(QuantumException):
    message = _("Change would make usage less than 0 for the following "
                "resources: %(unders)s")


class InvalidSharedSetting(QuantumException):
    message = _("Unable to reconfigure sharing settings for network "
                "%(network)s. Multiple tenants are using it")


class InvalidExtenstionEnv(QuantumException):
    message = _("Invalid extension environment: %(reason)s")
    
###Modifications by Srikanth
class ConfigurationNotFound(NotFound):
    message = _("Configuration %(config_id)s could not be found")
    
class PoolNotFound(NotFound):
    message = _("Pool %(pool_id)s could not be found")
    
class PoolMemberNotFound(NotFound):
    message = _("Pool Member %(member_id)s could not be found")

class HealthMonitorNotFound(NotFound):
    message = _("Health Monitor %(monitor_id)s could not be found")
    
class VIPNotFound(NotFound):
    message = _("Virtual IP %(vip_id)s could not be found")
    
class SessionPersistanceNotFound(NotFound):
    message = _("Sesssion Persistance %(session_id)s could not be found")
    
###Modifications done by Veera
class CategoryNotFound(NotFound):
    message = _("Category %(category_id)s could not be found ")
    
class VendorNotFound(NotFound):
    message = _("Vendor %(vendor_id)s could not be found ")
    
class ImageNotFound(NotFound):
    message = _("Image Map %(image_id)s could not be found ")
    
class MetadataNotFound(NotFound):
    message = _("Metadata %(metadata_id)s could not be found ")

class PersonalityNotFound(NotFound):
    message = _("Personality %(personality_id)s could not be found ")
    
class ChainNotFound(NotFound):
    message = _("Chain %(chain_id)s could not be found ")
    
class Chain_imageNotFound(NotFound):
    message = _("Image Chain %(chain_image_id)s could not be found ")
    
class Chain_image_networkNotFound(NotFound):
    message = _("Image Chain  network%(chain_image_network_id)s could not be found ")
    
class Chain_image_confNotFound(NotFound):
    message = _("Image Chain  configuration%(chain_image_conf_id)s could not be found ")
    
class NetworkfunctionNotFound(NotFound):
    message = _("Networkfunction %(networkfunction_id)s could not be found ")
    
class Category_networkfunctionNotFound(NotFound):
    message = _("Networkfunction %(networkfunction_id)s could not be found ")

class Config_handleNotFound(NotFound):
    message = _("Config_handle %(config_handle_id)s could not be found ")

class InstanceNotFound(NotFound):
    message = _("No Instance exists for Configuration Handle Id %(config_handle_id)")

class InstanceErrorState(QuantumException):
    message = _("Instance with id '%(instance_uuid)' is unable to start")
