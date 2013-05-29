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

from .views import IndexView, CreateView, UpdateView, DetailView
from .members.views import CreateView as CreatePoolMemberView
from .monitors.views import CreateView as CreateMonitorView
from .members.views import UpdateView as EditPoolMemberView
from .monitors.views import UpdateView as EditMonitorView

VIEWS_MOD = 'horizon.dashboards.nova.pools.views'
POOLS = r'^(?P<pool_id>[^/]+)/%s$'

urlpatterns = patterns(VIEWS_MOD,
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^create$', CreateView.as_view(), name='create'),
    url(POOLS % 'update', UpdateView.as_view(), name='update'),
    url(POOLS % 'detail', DetailView.as_view(),
        name='detail'),
    url(POOLS % 'members/createmember', CreatePoolMemberView.as_view(),
        name='createmember'),
    url(POOLS % 'monitors/addmonitor', CreateMonitorView.as_view(),
        name='addmonitor'),
    url(r'^(?P<pool_id>[^/]+)/members/(?P<member_id>[^/]+)/update$',
        EditPoolMemberView.as_view(), name='editmember'),
    url(r'^(?P<pool_id>[^/]+)/monitors/(?P<monitor_id>[^/]+)/update$',
        EditMonitorView.as_view(), name='editmonitor'))
    