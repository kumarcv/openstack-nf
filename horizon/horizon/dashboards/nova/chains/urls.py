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


from .views import IndexView, CreateChainView, UpdateChainView, DetailChainView, LaunchChainView
from .chain_images.views import MapimgView, EditChain_imageView
from .chain_images import urls as chain_image_urls
from .chain_images.chain_image_networks import urls as chain_image_network_urls



CHAINS = r'^(?P<chain_id>[^/]+)/%s$'


urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^create/$', CreateChainView.as_view(), name='create'),
    url(CHAINS % 'update', UpdateChainView.as_view(), name='update'),
    url(CHAINS % 'detail', DetailChainView.as_view(), name='detail'),
    url(CHAINS % 'launch', LaunchChainView.as_view(), name='launch'),
    url(CHAINS % 'chain_images/mapimg', MapimgView.as_view(), name='mapimg'),
    url(r'^(?P<chain_id>[^/]+)/chain_images/(?P<chain_image_id>[^/]+)/editchain_image$', EditChain_imageView.as_view(), name='editchainimg'),
    url(r'^chain_images/', include(chain_image_urls, namespace='chain_images')),
    url(r'^chain_images/chain_image_networks', include(chain_image_network_urls, namespace='chain_image_networks')))
