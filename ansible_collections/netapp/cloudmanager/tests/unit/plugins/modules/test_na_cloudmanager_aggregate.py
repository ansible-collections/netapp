# (c) 2021, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

''' unit tests ONTAP Ansible module: '''

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json
import pytest

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.netapp.cloudmanager.tests.unit.compat import unittest
from ansible_collections.netapp.cloudmanager.tests.unit.compat.mock import patch, Mock

from ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_aggregate \
    import NetAppCloudmanagerAggregate as my_module


def set_module_args(args):
    '''prepare arguments so that they will be picked up during module creation'''
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)  # pylint: disable=protected-access


class AnsibleExitJson(Exception):
    '''Exception class to be raised by module.exit_json and caught by the test case'''


class AnsibleFailJson(Exception):
    '''Exception class to be raised by module.fail_json and caught by the test case'''


def exit_json(*args, **kwargs):  # pylint: disable=unused-argument
    '''function to patch over exit_json; package return data into an exception'''
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):  # pylint: disable=unused-argument
    '''function to patch over fail_json; package return data into an exception'''
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class MockCMConnection():
    ''' Mock response of http connections '''

    def __init__(self, kind=None, parm1=None):
        self.type = kind
        self.parm1 = parm1
        self.xml_in = None
        self.xml_out = None


class TestMyModule(unittest.TestCase):
    ''' a group of related Unit Tests '''

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def set_default_args_pass_check(self):
        return dict({
            'state': 'present',
            'name': 'TestA',
            'working_environment_id': 'VsaWorkingEnvironment-abcdefg12345',
            'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
            'number_of_disks': 2,
            'disk_size_size': 100,
            'disk_size_unit': 'GB',
            'refresh_token': 'myrefresh_token',
        })

    def set_args_create_cloudmanager_aggregate(self):
        return dict({
            'state': 'present',
            'name': 'Dummyname',
            'working_environment_id': 'VsaWorkingEnvironment-abcdefg12345',
            'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
            'number_of_disks': 2,
            'disk_size_size': 100,
            'disk_size_unit': 'GB',
            'refresh_token': 'myrefresh_token',
        })

    def set_args_delete_cloudmanager_aggregate(self):
        return dict({
            'state': 'absent',
            'name': 'Dummyname',
            'working_environment_id': 'VsaWorkingEnvironment-abcdefg12345',
            'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
            'number_of_disks': 2,
            'disk_size_size': 100,
            'disk_size_unit': 'GB',
            'refresh_token': 'myrefresh_token',
        })

    def set_args_update_cloudmanager_aggregate(self):
        return dict({
            'state': 'present',
            'name': 'TestCMAggregate',
            'working_environment_id': 'VsaWorkingEnvironment-abcdefg12345',
            'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
            'number_of_disks': 3,
            'disk_size_size': 100,
            'disk_size_unit': 'GB',
            'refresh_token': 'myrefresh_token',
        })

    def test_module_fail_when_required_args_missing(self):
        ''' required arguments are reported as errors '''
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({})
            my_module()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    def test_module_fail_when_required_args_present(self, get_token):
        ''' required arguments are reported as errors '''
        with pytest.raises(AnsibleExitJson) as exc:
            set_module_args(self.set_default_args_pass_check())
            get_token.return_value = 'test', 'test'
            my_module()
            exit_json(changed=True, msg="TestCase Fail when required ars are present")
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch(
        'ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_aggregate.NetAppCloudmanagerAggregate.get_aggregate')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.post')
    def test_create_cloudmanager_aggregate_pass(self, get_post_api, get_aggregate_api, get_token):
        set_module_args(self.set_args_create_cloudmanager_aggregate())
        get_token.return_value = 'test', 'test'
        my_obj = my_module()
        my_obj.rest_api.api_root_path = "my_root_path"

        get_aggregate_api.return_value = None
        get_post_api.return_value = None, None, None

        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print('Info: test_create_cloudmanager_aggregate: %s' % repr(exc.value))
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch(
        'ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_aggregate.NetAppCloudmanagerAggregate.get_aggregate')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.delete')
    def test_delete_cloudmanager_aggregate_pass(self, get_delete_api, get_aggregate_api, get_token):
        set_module_args(self.set_args_delete_cloudmanager_aggregate())
        get_token.return_value = 'test', 'test'
        my_obj = my_module()
        my_obj.rest_api.api_root_path = "my_root_path"

        my_aggregate = {
            'name': 'Dummyname',
            'state': 'online',
            'working_environment_id': 'VsaWorkingEnvironment-abcdefg12345',
            'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
            'refresh_token': 'myrefresh_token',
            'disks': [{'device': 'xvdh vol-313', 'position': 'data', 'vmDiskProperties': None,
                       'ownerNode': 'testAWSa-01', 'name': 'testAWSa-01-i-12h'},
                      {'device': 'xvdi vol-314', 'position': 'data', 'vmDiskProperties': None,
                       'ownerNode': 'testAWSa-01', 'name': 'testAWSa-01-i-12i'}],
            'homeNode': 'testAWSa-01',
        }
        get_aggregate_api.return_value = my_aggregate
        get_delete_api.return_value = 'Aggregated Deleted', None, None

        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print('Info: test_delete_cloudmanager_aggregate: %s' % repr(exc.value))
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_aggregate.NetAppCloudmanagerAggregate.get_aggregate')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.post')
    def test_update_cloudmanager_aggregate_pass(self, get_post_api, get_aggregate_api, get_token):
        set_module_args(self.set_args_update_cloudmanager_aggregate())
        get_token.return_value = 'test', 'test'
        my_obj = my_module()
        my_obj.rest_api.api_root_path = "my_root_path"

        my_aggregate = {
            'name': 'Dummyname',
            'state': 'online',
            'working_environment_id': 'VsaWorkingEnvironment-abcdefg12345',
            'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
            'refresh_token': 'myrefresh_token',
            'disks': [{'device': 'xvdh vol-313', 'position': 'data', 'vmDiskProperties': None,
                       'ownerNode': 'testAWSa-01', 'name': 'testAWSa-01-i-12h'},
                      {'device': 'xvdi vol-314', 'position': 'data', 'vmDiskProperties': None,
                       'ownerNode': 'testAWSa-01', 'name': 'testAWSa-01-i-12i'}],
            'homeNode': 'testAWSa-01',
        }
        get_aggregate_api.return_value = my_aggregate
        get_post_api.return_value = None, None, None

        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print('Info: test_update_cloudmanager_aggregate: %s' % repr(exc.value))
        assert exc.value.args[0]['changed']
