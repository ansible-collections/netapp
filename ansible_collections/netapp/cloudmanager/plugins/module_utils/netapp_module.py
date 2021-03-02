# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c) 2021, Laurent Nicolas <laurentn@netapp.com>
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

''' Support class for NetApp ansible modules '''

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from copy import deepcopy
from ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp import CloudManagerRestAPI
import json
import re


def cmp(a, b):
    '''
    Python 3 does not have a cmp function, this will do the cmp.
    :param a: first object to check
    :param b: second object to check
    :return:
    '''
    # convert to lower case for string comparison.
    if a is None:
        return -1
    if isinstance(a, str) and isinstance(b, str):
        a = a.lower()
        b = b.lower()
    # if list has string element, convert string to lower case.
    if isinstance(a, list) and isinstance(b, list):
        a = [x.lower() if isinstance(x, str) else x for x in a]
        b = [x.lower() if isinstance(x, str) else x for x in b]
        a.sort()
        b.sort()
    return (a > b) - (a < b)


class NetAppModule(object):
    '''
    Common class for NetApp modules
    set of support functions to derive actions based
    on the current state of the system, and a desired state
    '''

    def __init__(self):
        self.log = list()
        self.changed = False
        self.parameters = {'name': 'not intialized'}

    def set_parameters(self, ansible_params):
        self.parameters = dict()
        for param in ansible_params:
            if ansible_params[param] is not None:
                self.parameters[param] = ansible_params[param]
        return self.parameters

    def get_cd_action(self, current, desired):
        ''' takes a desired state and a current state, and return an action:
            create, delete, None
            eg:
            is_present = 'absent'
            some_object = self.get_object(source)
            if some_object is not None:
                is_present = 'present'
            action = cd_action(current=is_present, desired = self.desired.state())
        '''
        if 'state' in desired:
            desired_state = desired['state']
        else:
            desired_state = 'present'

        if current is None and desired_state == 'absent':
            return None
        if current is not None and desired_state == 'present':
            return None
        # change in state
        self.changed = True
        if current is not None:
            return 'delete'
        return 'create'

    def compare_and_update_values(self, current, desired, keys_to_compare):
        updated_values = dict()
        is_changed = False
        for key in keys_to_compare:
            if key in current:
                if key in desired and desired[key] is not None:
                    if current[key] != desired[key]:
                        updated_values[key] = desired[key]
                        is_changed = True
                    else:
                        updated_values[key] = current[key]
                else:
                    updated_values[key] = current[key]

        return updated_values, is_changed

    def look_up_working_environment_by_name_in_list(self, we_list):
        '''
        Look up working environment by the name in working environment list
        '''
        for we in we_list:
            if we['name'] == self.parameters['working_environment_name']:
                return we, None
        return None, "Not found"

    def get_working_environment_details_by_name(self, rest_api):
        '''
        Use working environment name to get working environment details including:
        name: working environment name,
        publicID: working environment ID
        cloudProviderName,
        isHA,
        svmName
        '''
        if rest_api.token is None:
            rest_api.token_type, rest_api.token = rest_api.get_token()

        # check the working environment exist or not
        api = "/occm/api/working-environments/exists/" + self.parameters['working_environment_name']
        headers = {
            'X-Agent-Id': self.parameters['client_id'] + "clients"
        }
        response, error, dummy = rest_api.get(api, None, header=headers)
        if error is not None:
            return None, error

        # get working environment lists
        api = "/occm/api/working-environments"
        response, error, dummy = rest_api.get(api, None, header=headers)
        if error is not None:
            return None, error
        # look up the working environment in the working environment lists
        working_environment_details, error = self.look_up_working_environment_by_name_in_list(response['onPremWorkingEnvironments'])
        if error is None:
            return working_environment_details, None
        working_environment_details, error = self.look_up_working_environment_by_name_in_list(response['gcpVsaWorkingEnvironments'])
        if error is None:
            return working_environment_details, None
        working_environment_details, error = self.look_up_working_environment_by_name_in_list(response['azureVsaWorkingEnvironments'])
        if error is None:
            return working_environment_details, None
        working_environment_details, error = self.look_up_working_environment_by_name_in_list(response['vsaWorkingEnvironments'])
        if error is None:
            return working_environment_details, None
        return None, "Not found"

    def get_working_environment_details(self, rest_api):
        '''
        Use working environment id to get working environment details including:
        name: working environment name,
        publicID: working environment ID
        cloudProviderName,
        isHA,
        svmName
        '''
        if rest_api.token is None:
            rest_api.token_type, rest_api.token = rest_api.get_token()

        api = "/occm/api/working-environments/"
        api += self.parameters['working_environment_id']
        headers = {
            'X-Agent-Id': self.parameters['client_id'] + "clients"
        }
        response, error, dummy = rest_api.get(api, None, header=headers)
        if error:
            return None, error
        return response, None

    def set_api_root_path(self, working_environment_details, rest_api):
        provider = working_environment_details['cloudProviderName']
        is_ha = working_environment_details['isHA']
        api_root_path = None
        if provider != "Amazon":
            if is_ha:
                api_root_path = "/occm/api/" + provider.lower() + "/ha"
            else:
                api_root_path = "/occm/api/" + provider.lower() + "/vsa"
        else:
            if is_ha:
                api_root_path = "/occm/api/aws/ha"
            else:
                api_root_path = "/occm/api/vsa"
        rest_api.api_root_path = api_root_path

    def have_required_parameters(self, action):
        '''
        Check if all the required parameters in self.params are available or not besides the mandatory parameters
        '''
        actions = {'create_aggregate': ['number_of_disks', 'disk_size_size', 'disk_size_unit', 'working_environment_id'],
                   'update_aggregate': ['number_of_disks', 'disk_size_size', 'disk_size_unit', 'working_environment_id'],
                   'delete_aggregate': ['working_environment_id'],
                   }
        missed_params = []
        for parameter in actions[action]:
            if parameter not in self.parameters:
                missed_params.append(parameter)

        if not missed_params:
            return True, None
        else:
            return False, missed_params

    def get_modified_attributes(self, current, desired, get_list_diff=False):
        ''' takes two dicts of attributes and return a dict of attributes that are
            not in the current state
            It is expected that all attributes of interest are listed in current and
            desired.
            :param: current: current attributes in ONTAP
            :param: desired: attributes from playbook
            :param: get_list_diff: specifies whether to have a diff of desired list w.r.t current list for an attribute
            :return: dict of attributes to be modified
            :rtype: dict

            NOTE: depending on the attribute, the caller may need to do a modify or a
            different operation (eg move volume if the modified attribute is an
            aggregate name)
        '''
        # if the object does not exist,  we can't modify it
        modified = dict()
        if current is None:
            return modified

        # error out if keys do not match
        # self.check_keys(current, desired)

        # collect changed attributes
        for key, value in current.items():
            if key in desired and desired[key] is not None:
                if isinstance(value, list):
                    modified_list = self.compare_lists(value, desired[key], get_list_diff)  # get modified list from current and desired
                    if modified_list is not None:
                        modified[key] = modified_list
                elif isinstance(value, dict):
                    modified_dict = self.get_modified_attributes(value, desired[key])
                    if modified_dict:
                        modified[key] = modified_dict
                else:
                    try:
                        result = cmp(value, desired[key])
                    except TypeError as exc:
                        raise TypeError("%s, key: %s, value: %s, desired: %s" % (repr(exc), key, repr(value), repr(desired[key])))
                    else:
                        if result != 0:
                            modified[key] = desired[key]
        if modified:
            self.changed = True
        return modified

    @staticmethod
    def compare_lists(current, desired, get_list_diff):
        ''' compares two lists and return a list of elements that are either the desired elements or elements that are
            modified from the current state depending on the get_list_diff flag
            :param: current: current item attribute in ONTAP
            :param: desired: attributes from playbook
            :param: get_list_diff: specifies whether to have a diff of desired list w.r.t current list for an attribute
            :return: list of attributes to be modified
            :rtype: list
        '''
        current_copy = deepcopy(current)
        desired_copy = deepcopy(desired)

        # get what in desired and not in current
        desired_diff_list = list()
        for item in desired:
            if item in current_copy:
                current_copy.remove(item)
            else:
                desired_diff_list.append(item)

        # get what in current but not in desired
        current_diff_list = list()
        for item in current:
            if item in desired_copy:
                desired_copy.remove(item)
            else:
                current_diff_list.append(item)

        if desired_diff_list or current_diff_list:
            # there are changes
            if get_list_diff:
                return desired_diff_list
            else:
                return desired
        else:
            return None

    @staticmethod
    def convert_module_args_to_api(parameters, exclusion=None):
        '''
        Convert a list of string module args to API option format.
        For example, convert test_option to testOption.
        :param parameters: dict of parameters to be converted.
        :param exclusion: list of parameters to be ignored.
        :return: dict of key value pairs.
        '''
        exclude_list = ['api_url', 'token_type', 'refresh_token']
        if exclusion is not None:
            exclude_list += exclusion
        api_keys = dict()
        for k, v in parameters.items():
            if k not in exclude_list:
                words = k.split("_")
                api_key = ""
                for word in words:
                    if len(api_key) > 0:
                        word = word.title()
                    api_key = api_key + word
                api_keys[api_key] = v
        return api_keys

    @staticmethod
    def convert_data_to_tabbed_jsonstring(data):
        '''
        Convert a dictionary data to json format string
        '''
        dump = json.dumps(data, indent=2, separators=(',', ': '))
        tabbed = re.sub('\n +', lambda match: '\n' + '\t' * int(len(match.group().strip('\n')) / 2), dump)
        return tabbed
