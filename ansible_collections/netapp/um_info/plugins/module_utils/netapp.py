# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c) 2017, Sumit Kumar <sumit4@netapp.com>
# Copyright (c) 2017, Michael Price <michael.price@netapp.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''
common routines for um_info
'''

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import missing_required_lib

try:
    from ansible.module_utils.ansible_release import __version__ as ansible_version
except ImportError:
    ansible_version = 'unknown'

COLLECTION_VERSION = "21.6.0"

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

ERROR_MSG = dict(
    no_cserver='This module is expected to run as cluster admin'
)


def na_um_host_argument_spec():

    return dict(
        hostname=dict(required=True, type='str'),
        username=dict(required=True, type='str'),
        password=dict(required=True, type='str', no_log=True),
        validate_certs=dict(required=False, type='bool', default=True),
        http_port=dict(required=False, type='int'),
    )


class UMRestAPI(object):
    ''' send REST request and process response '''
    def __init__(self, module, timeout=60):
        self.module = module
        self.username = self.module.params['username']
        self.password = self.module.params['password']
        self.hostname = self.module.params['hostname']
        self.verify = self.module.params['validate_certs']
        self.timeout = timeout
        if self.module.params.get('http_port') is not None:
            self.url = 'https://%s:%d/api/' % (self.hostname, self.module.params['http_port'])
        else:
            self.url = 'https://%s/api/' % self.hostname
        self.errors = list()
        self.debug_logs = list()
        self.check_required_library()

    def check_required_library(self):
        if not HAS_REQUESTS:
            self.module.fail_json(msg=missing_required_lib('requests'))

    def send_request(self, method, api, params, json=None, accept=None):
        ''' send http request and process response, including error conditions '''
        url = self.url + api
        status_code = None
        content = None
        json_dict = None
        json_error = None
        error_details = None
        headers = None
        if accept is not None:
            headers = dict()
            # accept is used to turn on/off HAL linking
            if accept is not None:
                headers['accept'] = accept

        def get_json(response):
            ''' extract json, and error message if present '''
            try:
                json = response.json()
            except ValueError:
                return None, None
            error = json.get('error')
            return json, error

        try:
            response = requests.request(method, url, verify=self.verify, auth=(self.username, self.password),
                                        params=params, timeout=self.timeout, json=json, headers=headers)
            content = response.content  # for debug purposes
            status_code = response.status_code
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
            json_dict, json_error = get_json(response)
        except requests.exceptions.HTTPError as err:
            __, json_error = get_json(response)
            if json_error is None:
                self.log_error(status_code, 'HTTP error: %s' % err)
                error_details = str(err)
            # If an error was reported in the json payload, it is handled below
        except requests.exceptions.ConnectionError as err:
            self.log_error(status_code, 'Connection error: %s' % err)
            error_details = str(err)
        except Exception as err:
            self.log_error(status_code, 'Other error: %s' % err)
            error_details = str(err)
        if json_error is not None:
            self.log_error(status_code, 'Endpoint error: %d: %s' % (status_code, json_error))
            error_details = json_error
        self.log_debug(status_code, content)
        return json_dict, error_details

    def get(self, api, params):
        method = 'GET'
        return self.send_request(method, api, params)

    def log_error(self, status_code, message):
        self.errors.append(message)
        self.debug_logs.append((status_code, message))

    def log_debug(self, status_code, content):
        self.debug_logs.append((status_code, content))
