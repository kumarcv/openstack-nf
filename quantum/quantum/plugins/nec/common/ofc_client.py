# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2012 NEC Corporation.  All rights reserved.
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
# @author: Ryota MIBU

import httplib
import json
import logging
import socket

from quantum.plugins.nec.common import exceptions as nexc


LOG = logging.getLogger(__name__)


class OFCClient(object):
    """A HTTP/HTTPS client for OFC Drivers"""

    def __init__(self, host="127.0.0.1", port=8888, use_ssl=False,
                 key_file=None, cert_file=None):
        """Creates a new client to some OFC.

        :param host: The host where service resides
        :param port: The port where service resides
        :param use_ssl: True to use SSL, False to use HTTP
        :param key_file: The SSL key file to use if use_ssl is true
        :param cert_file: The SSL cert file to use if use_ssl is true
        """
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.key_file = key_file
        self.cert_file = cert_file
        self.connection = None

    def get_connection_type(self):
        """Returns the proper connection type"""
        if self.use_ssl:
            return httplib.HTTPSConnection
        else:
            return httplib.HTTPConnection

    def do_request(self, method, action, body=None):
        LOG.debug("Client request: %s %s [%s]" % (method, action, str(body)))

        if type(body) is dict:
            body = json.dumps(body)
        try:
            connection_type = self.get_connection_type()
            headers = {"Content-Type": "application/json"}
            # Open connection and send request, handling SSL certs
            certs = {'key_file': self.key_file, 'cert_file': self.cert_file}
            certs = dict((x, certs[x]) for x in certs if certs[x] is not None)
            if self.use_ssl and len(certs):
                conn = connection_type(self.host, self.port, **certs)
            else:
                conn = connection_type(self.host, self.port)
            conn.request(method, action, body, headers)
            res = conn.getresponse()
            data = res.read()
            LOG.debug("OFC returns [%s:%s]" % (str(res.status), data))
            if res.status in (httplib.OK,
                              httplib.CREATED,
                              httplib.ACCEPTED,
                              httplib.NO_CONTENT):
                if data and len(data) > 1:
                    return json.loads(data)
            else:
                reason = _("An operation on OFC is failed.")
                raise nexc.OFCException(reason=reason)
        except (socket.error, IOError), e:
            reason = _("Failed to connect OFC : %s" % str(e))
            LOG.error(reason)
            raise nexc.OFCException(reason=reason)

    def get(self, action):
        return self.do_request("GET", action)

    def post(self, action, body=None):
        return self.do_request("POST", action, body=body)

    def put(self, action, body=None):
        return self.do_request("PUT", action, body=body)

    def delete(self, action):
        return self.do_request("DELETE", action)
