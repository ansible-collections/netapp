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

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import missing_required_lib

try:
    from ansible.module_utils.ansible_release import __version__ as ansible_version
except ImportError:
    ansible_version = 'unknown'

COLLECTION_VERSION = "21.3.0"
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
        api_url=dict(required=True, type='str'),
        token=dict(required=True, type='str'),
        token_type=dict(required=True, type='str'),
        refresh_token=dict(required=True, type='str')
    )


class CloudManagerRestAPI(object):
    def __init__(self, module, timeout=60):
        self.module = module
        self.timeout = timeout
        self.api_url = self.module.params['api_url']
        self.token = self.module.params['token']
        self.token_type = self.module.params['token_type']
        self.refresh_token = self.module.params['refresh_token']
        self.url = 'https://' + self.api_url
        self.check_required_library()

    def check_required_library(self):
        if not HAS_REQUESTS:
            self.module.fail_json(msg=missing_required_lib('requests'))

    def send_request(self, method, api, params, json=None):
        ''' send http request and process response, including error conditions '''
        if params is not None:
            self.module.fail_json(msg='params is not implemented.  api=%s, params=%s' % (api, repr(params)))
        url = self.url + api
        json_dict = None
        json_error = None
        error_details = None
        headers = {
            'Content-type': "application/json",
            "Authorization": self.token_type + " " + self.token,
        }

        def get_json(response):
            ''' extract json, and error message if present '''
            try:
                json = response.json()

            except ValueError:
                return None, None
            success_code = [200, 201, 202]
            if response.status_code not in success_code:
                error = json.get('message')
            else:
                error = None
            return json, error
        try:
            response = requests.request(method, url, headers=headers, timeout=self.timeout, json=json)
            # If the response was successful, no Exception will be raised
            json_dict, json_error = get_json(response)
        except requests.exceptions.HTTPError as err:
            __, json_error = get_json(response)
            if json_error is None:
                error_details = str(err)
        except requests.exceptions.ConnectionError as err:
            error_details = str(err)
        except Exception as err:
            error_details = str(err)
        if json_error is not None:
            error_details = json_error

        return json_dict, error_details

    # If an error was reported in the json payload, it is handled below
    def get(self, api, params=None):
        method = 'GET'
        return self.send_request(method, api, params)

    def post(self, api, data, params=None):
        method = 'POST'
        return self.send_request(method, api, params, json=data)

    def patch(self, api, data, params=None):
        method = 'PATCH'
        return self.send_request(method, api, params, json=data)

    def put(self, api, data, params=None):
        method = 'PUT'
        return self.send_request(method, api, params, json=data)

    def delete(self, api, data, params=None):
        method = 'DELETE'
        return self.send_request(method, api, params, json=data)

    def get_token(self):
        token_res = requests.post('https://' + AUTH0_DOMAIN + '/oauth/token',
                                  json={"grant_type": "refresh_token", "refresh_token": self.refresh_token,
                                        "client_id": AUTH0_CLIENT, "audience": "https://api.cloud.netapp.com"})
        token_dict = token_res.json()
        token = token_dict['access_token']
        token_type = token_dict['token_type']

        return token_type, token

