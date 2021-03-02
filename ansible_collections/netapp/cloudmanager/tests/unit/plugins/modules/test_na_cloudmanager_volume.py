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

from ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_volume \
    import NetAppCloudmanagerVolume as my_module


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
            'name': 'testvol',
            'working_environment_id': 'VsaWorkingEnvironment-abcdefg12345',
            'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
            'svm_name': 'svm_justinaws',
            'snapshot_policy_name': 'default',
            'export_policy_type': 'custom',
            'export_policy_ip': ["10.30.0.1/16"],
            'export_policy_nfs_version': ["nfs4"],
            'refresh_token': 'myrefresh_token',
            'size': 10,
        })

    def test_module_fail_when_required_args_missing(self):
        ''' required arguments are reported as errors '''
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({})
            my_module()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_volume.NetAppCloudmanagerVolume.get_volume')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_volume.NetAppCloudmanagerVolume.create_volume')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.send_request')
    def test_create_volume_successfully(self, send_request, create, get, get_token):
        set_module_args(self.set_default_args_pass_check())
        get.return_value = None
        create.return_value = None
        send_request.side_effect = [({'publicId': 'id', 'svmName': 'svm_name', 'cloudProviderName': "aws", 'isHA': False}, None, None)]
        get_token.return_value = ("type", "token")
        obj = my_module()
        obj.rest_api.api_root_path = "test_root_path"

        with pytest.raises(AnsibleExitJson) as exc:
            obj.apply()
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_volume.NetAppCloudmanagerVolume.get_volume')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.send_request')
    def test_create_volume_idempotency(self, send_request, get, get_token):
        set_module_args(self.set_default_args_pass_check())
        get.return_value = {
            'name': 'testvol',
            'snapshot_policy_name': 'default',
            'export_policy_type': 'custom',
            'export_policy_ip': ["10.30.0.1/16"],
            'export_policy_nfs_version': ["nfs4"],
        }
        send_request.side_effect = [({'publicId': 'id', 'svmName': 'svm_name', 'cloudProviderName': "aws", 'isHA': False}, None, None)]
        get_token.return_value = ("type", "token")
        obj = my_module()
        obj.rest_api.api_root_path = "test_root_path"

        with pytest.raises(AnsibleExitJson) as exc:
            obj.apply()
        assert not exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_volume.NetAppCloudmanagerVolume.modify_volume')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_volume.NetAppCloudmanagerVolume.get_volume')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.send_request')
    def test_update_volume_successfully(self, send_request, get, get_token, modify):
        set_module_args(self.set_default_args_pass_check())
        get.return_value = {
            'name': 'testvol',
            'snapshot_policy_name': 'default',
            'export_policy_type': 'custom',
            'export_policy_ip': ["10.30.0.1/16"],
            'export_policy_nfs_version': ["nfs3", "nfs4"],
        }
        send_request.side_effect = [({'publicId': 'id', 'svmName': 'svm_name', 'cloudProviderName': "aws", 'isHA': False}, None, None)]
        get_token.return_value = ("type", "token")
        modify.return_value = None
        obj = my_module()
        obj.rest_api.api_root_path = "test_root_path"

        with pytest.raises(AnsibleExitJson) as exc:
            obj.apply()
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_volume.NetAppCloudmanagerVolume.modify_volume')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_volume.NetAppCloudmanagerVolume.get_volume')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.send_request')
    def test_update_volume_idempotency(self, send_request, get, get_token, modify):
        set_module_args(self.set_default_args_pass_check())
        get.return_value = {
            'name': 'testvol',
            'snapshot_policy_name': 'default',
            'export_policy_type': 'custom',
            'export_policy_ip': ["10.30.0.1/16"],
            'export_policy_nfs_version': ["nfs4"],
        }
        send_request.side_effect = [({'publicId': 'id', 'svmName': 'svm_name', 'cloudProviderName': "aws", 'isHA': False}, None, None)]
        get_token.return_value = ("type", "token")
        modify.return_value = None
        obj = my_module()
        obj.rest_api.api_root_path = "test_root_path"

        with pytest.raises(AnsibleExitJson) as exc:
            obj.apply()
        assert not exc.value.args[0]['changed']
