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

from django.conf.urls.defaults import patterns, url, include

from .chain_image_networks import urls as chain_network_urls

from .views import DetailChainImageView
from .chain_image_networks.views import MapnetView, MapconfView


CHAINSIMAGES = r'^(?P<chain_image_id>[^/]+)/%s$'

urlpatterns = patterns('horizon.dashboards.nova.chains.chain_images.views',
    url(CHAINSIMAGES % 'detail', DetailChainImageView.as_view(), name='detail'),
    url(CHAINSIMAGES % 'chain_image_networks/mapnet', MapnetView.as_view(), name='mapnet'),
    url(CHAINSIMAGES % 'chain_image_networks/mapconf', MapconfView.as_view(), name='mapconf'),
    url(r'^chain_image_networks/', include(chain_network_urls, namespace='chain_image_networks')))
