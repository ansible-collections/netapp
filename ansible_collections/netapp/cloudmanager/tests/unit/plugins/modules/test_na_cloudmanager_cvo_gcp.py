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

from ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_cvo_gcp \
    import NetAppCloudManagerCVOGCP as my_module


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
        # self.token_type, self.token = self.get_token()


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
            'client_id': 'test',
            'zone': 'us-west-1b',
            'vpc_id': 'vpc-test',
            'subnet_id': 'subnet-test',
            'svm_password': 'password',
            'refresh_token': 'myrefresh_token',
            'is_ha': False,
            'gcp_service_account': 'test_account',
            'data_encryption_type': 'GCP',
            'gcp_volume_type': 'pd-ssd',
            'gcp_volume_size': 500,
            'gcp_volume_size_unit': 'GB',
            'project_id': 'project-test'
        })

    def set_args_create_cloudmanager_cvo_gcp(self):
        return dict({
            'state': 'present',
            'name': 'Dummyname',
            'client_id': 'test',
            'zone': 'us-west-1',
            'vpc_id': 'vpc-test',
            'subnet_id': 'subnet-test',
            'svm_password': 'password',
            'refresh_token': 'myrefresh_token',
            'is_ha': False,
            'gcp_service_account': 'test_account',
            'data_encryption_type': 'GCP',
            'gcp_volume_type': 'pd-ssd',
            'gcp_volume_size': 500,
            'gcp_volume_size_unit': 'GB',
            'project_id': 'project-test'
        })

    def test_module_fail_when_required_args_missing(self):
        ''' required arguments are reported as errors '''
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({})
            my_module()
            self.rest_api = MockCMConnection()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    def test_module_fail_when_required_args_present(self, get_token):
        ''' required arguments are reported as errors '''
        with pytest.raises(AnsibleExitJson) as exc:
            set_module_args(self.set_default_args_pass_check())
            get_token.return_value = 'test', 'test'
            my_module()
            exit_json(changed=True, msg="TestCase Fail when required args are present")
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.wait_on_completion')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_cvo_gcp.NetAppCloudManagerCVOGCP.get_tenant')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_cvo_gcp.NetAppCloudManagerCVOGCP.get_nss')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_cvo_gcp.NetAppCloudManagerCVOGCP.get_working_environment')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.post')
    def test_create_cloudmanager_cvo_gcp_pass(self, get_post_api, get_working_environment, get_nss, get_tenant, wait_on_completion, get_token):
        set_module_args(self.set_args_create_cloudmanager_cvo_gcp())
        get_token.return_value = 'test', 'test'
        my_obj = my_module()

        response = {'publicId': 'abcdefg12345'}
        get_post_api.return_value = response, None, None
        get_working_environment.return_value = None
        get_nss.return_value = 'nss-test'
        get_tenant.return_value = 'test'
        wait_on_completion.return_value = None

        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print('Info: test_create_cloudmanager_cvo_gcp_pass: %s' % repr(exc.value))
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.wait_on_completion')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_cvo_gcp.NetAppCloudManagerCVOGCP.get_tenant')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_cvo_gcp.NetAppCloudManagerCVOGCP.get_nss')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_cvo_gcp.NetAppCloudManagerCVOGCP.get_working_environment')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.post')
    def test_create_cloudmanager_cvo_gcp_ha_pass(self, get_post_api, get_working_environment, get_nss, get_tenant, wait_on_completion, get_token):
        data = self.set_args_create_cloudmanager_cvo_gcp()
        data['is_ha'] = True
        data['subnet0_node_and_data_connectivity'] = 'default'
        data['subnet1_cluster_connectivity'] = 'subnet2'
        data['subnet2_ha_connectivity'] = 'subnet3'
        data['subnet3_data_replication'] = 'subnet1'
        data['vpc0_node_and_data_connectivity'] = 'default'
        data['vpc1_cluster_connectivity'] = 'vpc2'
        data['vpc2_ha_connectivity'] = 'vpc3'
        data['vpc3_data_replication'] = 'vpc1'
        set_module_args(data)
        get_token.return_value = 'test', 'test'
        my_obj = my_module()

        response = {'publicId': 'abcdefg12345'}
        get_post_api.return_value = response, None, None
        get_working_environment.return_value = None
        get_nss.return_value = 'nss-test'
        get_tenant.return_value = 'test'
        wait_on_completion.return_value = None

        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print('Info: test_create_cloudmanager_cvo_gcp_ha_pass: %s' % repr(exc.value))
        assert exc.value.args[0]['changed']
