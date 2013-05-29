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


import logging


from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from horizon import api
from horizon import exceptions
from horizon import forms
from horizon import workflows
from horizon.utils import fields


LOG = logging.getLogger(__name__)


class CreateImageInfoAction(workflows.Action):
    image_name = forms.CharField(max_length=255,
                               label=_("Image Map Name"))
    image_id = forms.ChoiceField(label=_("Image"))
    flavor = forms.ChoiceField(label=_("Flavor"),
                               help_text=_("Size of image to launch."))
    security_group = forms.ChoiceField(label=_("Security Group"))
    category = forms.ChoiceField(label=_("Category"),
                               help_text=_("To which Category it belongs."))
    vendor = forms.ChoiceField(label=_("Vendor"),
                               help_text=_("Who is the Vendor."))
    shared = forms.BooleanField(label=_("Shared"),
                                initial=False, required=False)

    class Meta:
        name = ("Details")
        help_text = _("From here you can map image to Category & Vendors.\n")
        
    def _get_available_images(self, request, context):
        project_id = context.get('project_id', None)
        if not hasattr(self, "_public_images"):
            public = {"is_public": True,
                      "status": "active"}
            try:
                public_images, _more = api.glance.image_list_detailed(request,
                                                           filters=public)
            except:
                public_images = []
                exceptions.handle(request,
                                  _("Unable to retrieve public images."))
            self._public_images = public_images

        # Preempt if we don't have a project_id yet.
        if project_id is None:
            setattr(self, "_images_for_%s" % project_id, [])

        if not hasattr(self, "_images_for_%s" % project_id):
            owner = {"property-owner_id": project_id,
                     "status": "active"}
            try:
                owned_images, _more = api.glance.image_list_detailed(request,
                                                          filters=owner)
            except:
                exceptions.handle(request,
                                  _("Unable to retrieve images for "
                                    "the current project."))
            setattr(self, "_images_for_%s" % project_id, owned_images)

        owned_images = getattr(self, "_images_for_%s" % project_id)
        images = owned_images + self._public_images

        # Remove duplicate images
        image_ids = []
        final_images = []
        for image in images:
            if image.id not in image_ids:
                image_ids.append(image.id)
                final_images.append(image)
        return [image for image in final_images
                if image.container_format not in ('aki', 'ari')]

    def populate_image_id_choices(self, request, context):
        images = self._get_available_images(request, context)
        choices = [(image.id, image.name)
                   for image in images
                   if image.properties.get("image_type", '') != "snapshot"]
        if choices:
            choices.insert(0, ("", _("Select Image")))
        else:
            choices.insert(0, ("", _("No images available.")))
        return choices
    
    def populate_flavor_choices(self, request, context):
        try:
            flavors = api.nova.flavor_list(request)
            flavor_list = [(flavor.id, "%s" % flavor.name)
                           for flavor in flavors]
        except:
            flavor_list = []
            exceptions.handle(request,
                              _('Unable to retrieve instance flavors.'))
        choices = sorted(flavor_list)
        if choices:
            choices.insert(0, ("", _("Select Flavour")))
        else:
            choices.insert(0, ("", _("No Flavours available.")))
        return choices
    
    def populate_security_group_choices(self, request, context):
        try:
            security_groups = api.nova.security_group_list(request)
            security_group_list = [(security_group.id, "%s" % security_group.name)
                           for security_group in security_groups]
        except:
            security_group_list = []
            exceptions.handle(request,
                              _('Unable to retrieve instance Security Groups.'))
        choices = sorted(security_group_list)
        if choices:
            choices.insert(0, ("", _("Select Security Group")))
        else:
            choices.insert(0, ("", _("No Security Group available.")))
        return choices
        
    def populate_category_choices(self, request, context):
        try:
            categories = api.quantum.category_list(request)
            category_list = [(category.id, "%s" % category.name)
                           for category in categories]
        except:
            category_list = []
            exceptions.handle(request,
                              _('Unable to retrieve categories.'))
        choices = sorted(category_list)
        if choices:
            choices.insert(0, ("", _("Select Category")))
        else:
            choices.insert(0, ("", _("No Categories available.")))
        return choices
        
    def populate_vendor_choices(self, request, context):
        try:
            vendors = api.quantum.vendor_list(request)
            vendor_list = [(vendor.id, "%s" % vendor.name)
                           for vendor in vendors]
        except:
            vendor_list = []
            exceptions.handle(request,
                              _('Unable to retrieve vendors.'))
        choices = sorted(vendor_list)
        if choices:
            choices.insert(0, ("", _("Select Vendor")))
        else:
            choices.insert(0, ("", _("No Vendors available.")))
        return choices


class CreateImageInfo(workflows.Step):
    action_class = CreateImageInfoAction
    contributes = ("image_name", "image_id", "flavor", "category", "vendor", "security_group" ,"shared")


class CreateMetadataInfoAction(workflows.Action):
    metadata_name = forms.CharField(max_length=255,
                                  label=_("Name"),
                                  required=False)
    metadata_value = forms.CharField(widget=forms.Textarea,
                                           label=_("Value"),
                                           required=False)
    

    class Meta:
        name = ("Metadata")
        help_text = _('Mapped Image metadata')

    def clean(self):
        cleaned_data = super(CreateMetadataInfoAction, self).clean()
        metadata_name = cleaned_data.get('metadata_name')
        metadata_value = cleaned_data.get('metadata_value')
       
        return cleaned_data


class CreateMetadataInfo(workflows.Step):
    action_class = CreateMetadataInfoAction
    contributes = ("metadata_name", "metadata_value")
    
class CreatePersonalityInfoAction(workflows.Action):
    personality_path = forms.CharField(max_length=255,
                                  label=_("File Path"),
                                  required=False)
    personality_content = forms.CharField(widget=forms.Textarea,
                                           label=_("File Content"),
                                           required=False)
    

    class Meta:
        name = ("Personality")
        help_text = _('Mapped Image Personality')

    def clean(self):
        cleaned_data = super(CreatePersonalityInfoAction, self).clean()
        personality_path = cleaned_data.get('personality_path')
        personality_content = cleaned_data.get('personality_content')
       
        return cleaned_data

class CreatePersonalityInfo(workflows.Step):
    action_class = CreatePersonalityInfoAction
    contributes = ("personality_path", "personality_content")


class CreateImage(workflows.Workflow):
    slug = "create_image"
    name = _("Create Image Map")
    finalize_button_name = _("Create")
    success_message = _('Created image map "%s".')
    failure_message = _('Unable to create image map "%s".')
    success_url = "horizon:syspanel:imagemaps:index"
    default_steps = (CreateImageInfo,
                     CreateMetadataInfo,
                     CreatePersonalityInfo,)

    def format_status_message(self, message):
        name = self.context.get('name') or self.context.get('id', '')
        return message % name

    def handle(self, request, data):
        # create the image map
        try:
            image = api.quantum.image_create(request,
                                                 name=data['image_name'],
                                                 image_id=data['image_id'],
                                                 flavor_id=data['flavor'],
                                                 category_id=data['category'],
                                                 vendor_id=data['vendor'],
                                                 security_group_id=data['security_group'],
                                                 shared=data['shared'])
            image.set_id_as_name_if_empty()
            self.context['id'] = image.id
            msg = _('Mapped Image "%s" was successfully created.') % image.name
            LOG.debug(msg)
        except:
            msg = _('Failed to map image "%s".') % data['name']
            LOG.info(msg)
            redirect = reverse('horizon:syspanel:imagemaps:index')
            exceptions.handle(request, msg, redirect=redirect)
            return False

        # If we do not need to create a metadata, return here.
        #if not data['with_metadata']:
        #    return True

        # Create the metadata.
        try:
            params = {'image_map_id': image.id,
                      'name': data['metadata_name'],
                      'value': data['metadata_value']}
            api.quantum.metadata_create(request, **params)
            msg = _('Metadata "%s" was successfully created.') % data['metadata_name']
            LOG.debug(msg)
        except Exception:
            msg = _('Failed to create Metadata "%(sub)s" for Image "%(image)s".')
            redirect = reverse('horizon:syspanel:imagemaps:index')
            exceptions.handle(request,
                              msg % {"Metadata": data['metadata_name'], "Image": image.id},
                              redirect=redirect)
            return False
        
        
        # If we do not need to create a personality, return here.
        #if not data['with_personality']:
        #    return True

        # Create the metadata.
        try:
            params = {'image_map_id': image.id,
                      'file_path': data['personality_path'],
                      'file_content': data['personality_content']}
            
            api.quantum.personality_create(request, **params)
            msg = _('Personality "%s" was successfully created.') % data['personality_path']
            LOG.debug(msg)
        except Exception:
            msg = _('Failed to create Personality "%(sub)s" for Image "%(image)s".')
            redirect = reverse('horizon:syspanel:imagemaps:index')
            exceptions.handle(request,
                              msg % {"Personality": data['personality_path'], "Image": image.id},
                              redirect=redirect)
            return False

        return True
