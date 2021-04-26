# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c) 2017-2021, NetApp Ansible Team <ng-ansibleteam@netapp.com>
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

"""
netapp.py: wrapper around send_requests and other utilities
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import time
from ansible.module_utils.basic import missing_required_lib

try:
    from ansible.module_utils.ansible_release import __version__ as ansible_version
except ImportError:
    ansible_version = 'unknown'

COLLECTION_VERSION = "21.5.1"
AUTH0_DOMAIN = 'netapp-cloud-account.auth0.com'
AUTH0_CLIENT = 'Mu0V1ywgYteI6w1MbD15fKfVIUrNXGWC'

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


POW2_BYTE_MAP = dict(
    # Here, 1 kb = 1024
    bytes=1,
    b=1,
    kb=1024,
    mb=1024 ** 2,
    gb=1024 ** 3,
    tb=1024 ** 4,
    pb=1024 ** 5,
    eb=1024 ** 6,
    zb=1024 ** 7,
    yb=1024 ** 8
)


def cloudmanager_host_argument_spec():

    return dict(
        refresh_token=dict(required=True, type='str', no_log=True)
    )


class CloudManagerRestAPI(object):
    """ wrapper around send_request """
    def __init__(self, module, timeout=60):
        self.module = module
        self.timeout = timeout
        self.refresh_token = self.module.params['refresh_token']
        self.token_type, self.token = self.get_token()
        self.url = 'https://'
        self.api_root_path = None
        self.check_required_library()

    def check_required_library(self):
        if not HAS_REQUESTS:
            self.module.fail_json(msg=missing_required_lib('requests'))

    def send_request(self, method, api, params, json=None, data=None, header=None):
        ''' send http request and process response, including error conditions '''
        if params is not None:
            self.module.fail_json(msg='params is not implemented.  api=%s, params=%s' % (api, repr(params)))
        url = self.url + api
        json_dict = None
        json_error = None
        error_details = None
        on_cloud_request_id = None
        response = None
        headers = {
            'Content-type': "application/json",
            'Referer': "Ansible_NetApp",
            'Authorization': self.token_type + " " + self.token,
        }
        if header is not None:
            headers.update(header)

        def get_json(response):
            ''' extract json, and error message if present '''
            error = None
            try:
                json = response.json()
            except ValueError:
                return None, None
            success_code = [200, 201, 202]
            if response.status_code not in success_code:
                error = json.get('message')
            return json, error

        try:
            response = requests.request(method, url, headers=headers, timeout=self.timeout, json=json, data=data)
            status_code = response.status_code
            if status_code >= 300 or status_code < 200:
                return response.content, str(status_code), on_cloud_request_id
            # If the response was successful, no Exception will be raised
            json_dict, json_error = get_json(response)
            if response.headers.get('OnCloud-Request-Id', '') != '':
                on_cloud_request_id = response.headers.get('OnCloud-Request-Id')
        except requests.exceptions.HTTPError as err:
            __, json_error = get_json(response)
            if json_error is None:
                error_details = str(err)
            # If an error was reported in the json payload, it is handled below
        except requests.exceptions.ConnectionError as err:
            error_details = str(err)
        except Exception as err:
            error_details = str(err)
        if json_error is not None:
            error_details = json_error
        return json_dict, error_details, on_cloud_request_id

    # If an error was reported in the json payload, it is handled below
    def get(self, api, params=None, header=None):
        method = 'GET'
        return self.send_request(method=method, api=api, params=params, json=None, header=header)

    def post(self, api, data, params=None, header=None, gcp_type=False):
        method = 'POST'
        if gcp_type:
            return self.send_request(method=method, api=api, params=params, data=data, header=header)
        else:
            return self.send_request(method=method, api=api, params=params, json=data, header=header)

    def patch(self, api, data, params=None, header=None):
        method = 'PATCH'
        return self.send_request(method=method, api=api, params=params, json=data, header=header)

    def put(self, api, data, params=None, header=None):
        method = 'PUT'
        return self.send_request(method=method, api=api, params=params, json=data, header=header)

    def delete(self, api, data, params=None, header=None):
        method = 'DELETE'
        return self.send_request(method=method, api=api, params=params, json=data, header=header)

    def get_token(self):
        token_res = requests.post('https://' + AUTH0_DOMAIN + '/oauth/token',
                                  json={"grant_type": "refresh_token", "refresh_token": self.refresh_token,
                                        "client_id": AUTH0_CLIENT, "audience": "https://api.cloud.netapp.com"})
        token_dict = token_res.json()
        token = token_dict['access_token']
        token_type = token_dict['token_type']

        return token_type, token

    def wait_on_completion(self, api_url, action_name, task, retries, wait_interval):
        while True:
            cvo_status, failure_error_message, error = self.check_task_status(api_url)
            if error is not None:
                return error
            # status value 1 means success
            if cvo_status == 1:
                return None
            # status value -1 means failed
            elif cvo_status == -1:
                return 'Failed to %s %s, error: %s' % (task, action_name, failure_error_message)
            # status value 0 means pending
            if retries == 0:
                return 'Taking too long for %s to %s or not properly setup' % (action_name, task)
            time.sleep(wait_interval)
            retries = retries - 1

    def check_task_status(self, api_url):

        headers = {
            'X-Agent-Id': self.module.params['client_id'] + "clients"
        }

        network_retries = 3
        while True:
            result, error, dummy = self.get(api_url, None, header=headers)
            if error is not None:
                if network_retries > 0:
                    time.sleep(1)
                    network_retries = network_retries - 1
                else:
                    return 0, '', error
            else:
                response = result
                break
        return response['status'], response['error'], None
