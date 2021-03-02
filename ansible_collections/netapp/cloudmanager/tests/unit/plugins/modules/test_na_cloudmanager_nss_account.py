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

from ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_nss_account \
    import NetAppCloudmanagerNssAccount as my_module


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
            'name': 'test_nss_account',
            'username': 'username',
            'password': 'password',
            'client_id': 'client_id',
            'refresh_token': 'refrsh_token'
        })

    def test_module_fail_when_required_args_missing(self):
        ''' required arguments are reported as errors '''
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({})
            my_module()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_nss_account.NetAppCloudmanagerNssAccount.get_nss_account')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_nss_account.NetAppCloudmanagerNssAccount.create_nss_account')
    def test_create_nss_account_successfully(self, create, get, get_token):
        set_module_args(self.set_default_args_pass_check())
        get.return_value = None
        create.return_value = None
        get_token.return_value = ("type", "token")
        obj = my_module()
        obj.rest_api.api_root_path = "test_root_path"

        with pytest.raises(AnsibleExitJson) as exc:
            obj.apply()
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_nss_account.NetAppCloudmanagerNssAccount.get_nss_account')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_nss_account.NetAppCloudmanagerNssAccount.create_nss_account')
    def test_create_nss_account_idempotency(self, create, get, get_token):
        set_module_args(self.set_default_args_pass_check())
        get.return_value = {
            'name': 'test_nss_account',
            'username': 'TESTCLOUD1',
            'password': 'test_test',
            'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
            'refresh_token': 'CvMJXRhz5V4dmxZqVg5LDRDlZyE - kbqRKT9YMcAsjmwFs'
        }
        create.return_value = None
        get_token.return_value = ("type", "token")
        obj = my_module()
        obj.rest_api.api_root_path = "test_root_path"

        with pytest.raises(AnsibleExitJson) as exc:
            obj.apply()
        assert not exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_nss_account.NetAppCloudmanagerNssAccount.get_nss_account')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_nss_account.NetAppCloudmanagerNssAccount.delete_nss_account')
    def test_create_nss_account_successfully(self, delete, get, get_token):
        args = self.set_default_args_pass_check()
        args['state'] = 'absent'
        set_module_args(args)
        get.return_value = {
            'name': 'test_nss_account',
            'username': 'TESTCLOUD1',
            'password': 'test_test',
            'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
            'refresh_token': 'CvMJXRhz5V4dmxZqVg5LDRDlZyE - kbqRKT9YMcAsjmwFs'
        }
        delete.return_value = None
        get_token.return_value = ("type", "token")
        obj = my_module()
        obj.rest_api.api_root_path = "test_root_path"

        with pytest.raises(AnsibleExitJson) as exc:
            obj.apply()
        assert exc.value.args[0]['changed']
