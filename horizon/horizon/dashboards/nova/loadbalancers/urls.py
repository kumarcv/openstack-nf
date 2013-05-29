# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from .views import IndexView, CreateView, UpdateView, VirtualIPListView, GenerateConfigView
from .vips.views import CreateView as CreateVirtualIPView
from .vips.views import UpdateView as EditVirtualIPView
from .pools.views import IndexView as PoolsListView
from .pools.views import CreateView as PoolCreateView
from .pools.views import UpdateView as PoolUpdateView
from .pools.views import DetailView as PoolDetailView
from .pools.members.views import CreateView as CreatePoolMemberView
from .pools.monitors.views import CreateView as CreateMonitorView
from .pools.members.views import UpdateView as EditPoolMemberView
from .pools.monitors.views import UpdateView as EditMonitorView

#from .views import IndexView, CreateView, UpdateView, DetailView


VIEWS_MOD = 'horizon.dashboards.nova.loadbalancers.views'
CONFIGS = r'^(?P<config_id>[^/]+)/%s$'

urlpatterns = patterns(VIEWS_MOD,
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^create$', CreateView.as_view(), name='create'),
    url(CONFIGS % 'update', UpdateView.as_view(), name='update'),
    url(CONFIGS % 'listvips', VirtualIPListView.as_view(),
        name='listvips'),
    url(CONFIGS % 'vips/addvip', CreateVirtualIPView.as_view(),
        name='addvip'),
    url(r'^(?P<config_id>[^/]+)/vips/(?P<vip_id>[^/]+)/update$',
        EditVirtualIPView.as_view(), name='editvip'),
    url(r'^pools$', PoolsListView.as_view(), name='pools'),
    url(r'^createpool$', PoolCreateView.as_view(), name='createpool'),
    url(r'^pools/(?P<pool_id>[^/]+)/updatepool$', PoolUpdateView.as_view(), name='updatepool'),
    url(r'^pools/(?P<pool_id>[^/]+)/detail$', PoolDetailView.as_view(), name='detail'),
    url(r'^pools/(?P<pool_id>[^/]+)/members/createmember$', CreatePoolMemberView.as_view(), name='createmember'),
    url(r'^pools/(?P<pool_id>[^/]+)/members/(?P<member_id>[^/]+)/editmember$', EditPoolMemberView.as_view(), name='editmember'),
    url(r'^pools/(?P<pool_id>[^/]+)/monitors/addmonitor$', CreateMonitorView.as_view(), name='addmonitor'),
    url(r'^pools/(?P<pool_id>[^/]+)/monitors/(?P<monitor_id>[^/]+)/editmonitor$', EditMonitorView.as_view(), name='editmonitor'),
    url(CONFIGS % 'genconfig', GenerateConfigView.as_view(), name='genconfig'))
    