# (c) 2021, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

''' unit tests Cloudmanager Ansible module: '''

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import json
import pytest

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.netapp.cloudmanager.tests.unit.compat import unittest
from ansible_collections.netapp.cloudmanager.tests.unit.compat.mock import patch, Mock

from ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_cifs_server \
    import NetAppCloudmanagerCifsServer as my_module


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
            'working_environment_id': 'VsaWorkingEnvironment-abcdefg12345',
            'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
            'refresh_token': 'refreshToken',
            'domain': 'test.com',
            'username': 'admin',
            'password': 'abcde',
            'dns_domain': 'test.com',
            'ip_addresses': '["1.0.0.1"]',
            'netbios': 'cvoname',
            'organizational_unit': 'CN=Computers',
        })

    def set_using_workgroup_args_pass_check(self):
        return dict({
            'state': 'present',
            'working_environment_id': 'VsaWorkingEnvironment-abcdefg12345',
            'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
            'refresh_token': 'refreshToken',
            'is_workgroup': True,
            'server_name': 'abc',
            'workgroup_name': 'wk',
        })

    def test_module_fail_when_required_args_missing(self):
        ''' required arguments are reported as errors '''
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({})
            my_module()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_cifs_server.NetAppCloudmanagerCifsServer.get_cifs_server')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_cifs_server.NetAppCloudmanagerCifsServer.create_cifs_server')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.send_request')
    def test_create_cifs_server_successfully(self, send_request, create, get, get_token):
        set_module_args(self.set_default_args_pass_check())
        get.return_value = None
        create.return_value = None
        send_request.side_effect = [({'publicId': 'id', 'svmName': 'svm_name', 'cloudProviderName': "aws", 'isHA': False}, None, 'dummy')]
        get_token.return_value = ("type", "token")
        obj = my_module()
        obj.rest_api.api_root_path = "test_root_path"

        with pytest.raises(AnsibleExitJson) as exc:
            obj.apply()
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_cifs_server.NetAppCloudmanagerCifsServer.get_cifs_server')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.send_request')
    def test_create_cifs_server_idempotency(self, send_request, get, get_token):
        set_module_args(self.set_default_args_pass_check())
        get.return_value = {
            'domain': 'test.com',
            'dns_domain': 'test.com',
            'ip_addresses': ['1.0.0.1'],
            'netbios': 'cvoname',
            'organizational_unit': 'CN=Computers',
        }
        send_request.side_effect = [({'publicId': 'id', 'svmName': 'svm_name', 'cloudProviderName': "aws", 'isHA': False}, None, 'dummy')]
        get_token.return_value = ("type", "token")
        obj = my_module()
        obj.rest_api.api_root_path = "test_root_path"

        with pytest.raises(AnsibleExitJson) as exc:
            obj.apply()
        assert not exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_cifs_server.NetAppCloudmanagerCifsServer.get_cifs_server')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_cifs_server.NetAppCloudmanagerCifsServer.create_cifs_server')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.send_request')
    def test_create_cifs_server_using_workgroup_successfully(self, send_request, create, get, get_token):
        set_module_args(self.set_using_workgroup_args_pass_check())
        get.return_value = None
        create.return_value = None
        send_request.side_effect = [({'publicId': 'id', 'svmName': 'svm_name', 'cloudProviderName': "aws", 'isHA': False}, None, 'dummy')]
        get_token.return_value = ("type", "token")
        obj = my_module()
        obj.rest_api.api_root_path = "test_root_path"

        with pytest.raises(AnsibleExitJson) as exc:
            obj.apply()
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_cifs_server.NetAppCloudmanagerCifsServer.get_cifs_server')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_cifs_server.NetAppCloudmanagerCifsServer.delete_cifs_server')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.send_request')
    def test_delete_cifs_server_successfully(self, send_request, delete, get, get_token):
        args = self.set_default_args_pass_check()
        args['state'] = 'absent'
        set_module_args(args)
        get.return_value = {
            'domain': 'test.com',
            'dns_domain': 'test.com',
            'ip_addresses': ['1.0.0.1'],
            'netbios': 'cvoname',
            'organizational_unit': 'CN=Computers',
        }
        delete.return_value = None
        send_request.side_effect = [({'publicId': 'id', 'svmName': 'svm_name', 'cloudProviderName': "aws", 'isHA': False}, None, 'dummy')]
        get_token.return_value = ("type", "token")
        obj = my_module()
        obj.rest_api.api_root_path = "test_root_path"

        with pytest.raises(AnsibleExitJson) as exc:
            obj.apply()
        assert exc.value.args[0]['changed']
