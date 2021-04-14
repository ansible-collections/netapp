# (c) 2021, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

''' unit tests Cloudmanager Ansible module: '''

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json
import sys
import pytest

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.netapp.cloudmanager.tests.unit.compat import unittest
from ansible_collections.netapp.cloudmanager.tests.unit.compat.mock import patch

from ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_aws \
    import NetAppCloudManagerConnectorAWS as my_module, IMPORT_EXCEPTION

if IMPORT_EXCEPTION is not None and sys.version_info < (3, 5):
    pytestmark = pytest.mark.skip('skipping as missing required imports on 2.6 and 2.7: %s' % IMPORT_EXCEPTION)


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
            'region': 'us-west-1',
            'key_name': 'dev_automation',
            'subnet_id': 'subnet-test',
            'ami': 'ami-test',
            'security_group_ids': ['sg-test'],
            'refresh_token': 'myrefresh_token',
            'iam_instance_profile_name': 'OCCM_AUTOMATION',
            'account_id': 'account-test',
            'company': 'NetApp'
        })

    def set_args_create_cloudmanager_connector_aws(self):
        return dict({
            'state': 'present',
            'name': 'Dummyname',
            'region': 'us-west-1',
            'key_name': 'dev_automation',
            'subnet_id': 'subnet-test',
            'ami': 'ami-test',
            'security_group_ids': ['sg-test'],
            'refresh_token': 'myrefresh_token',
            'iam_instance_profile_name': 'OCCM_AUTOMATION',
            'account_id': 'account-test',
            'company': 'NetApp'
        })

    def set_args_delete_cloudmanager_connector_aws(self):
        return dict({
            'state': 'absent',
            'name': 'Dummyname',
            'client_id': 'test',
            'instance_id': 'test',
            'region': 'us-west-1',
            'account_id': 'account-test',
            'refresh_token': 'myrefresh_token',
            'company': 'NetApp'
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
            exit_json(changed=True, msg="TestCase Fail when required args are present")
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_aws.NetAppCloudManagerConnectorAWS.create_instance')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_aws.NetAppCloudManagerConnectorAWS.get_vpc')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_aws.NetAppCloudManagerConnectorAWS.register_agent_to_service')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_aws.NetAppCloudManagerConnectorAWS.get_ami')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.post')
    def test_create_cloudmanager_connector_aws_pass(self, get_post_api, get_ami, register_agent_to_service, get_vpc, create_instance, get_token):
        set_module_args(self.set_args_create_cloudmanager_connector_aws())
        get_token.return_value = 'test', 'test'
        my_obj = my_module()

        get_post_api.return_value = None, None, None
        get_ami.return_value = 'ami-test'
        register_agent_to_service.return_value = 'test', 'test'
        get_vpc.return_value = 'test'
        create_instance.return_value = 'test', 'test'

        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print('Info: test_create_cloudmanager_connector_aws: %s' % repr(exc.value))
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_aws.NetAppCloudManagerConnectorAWS.delete_instance')
    @patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_aws.NetAppCloudManagerConnectorAWS.get_instance')
    @patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.delete')
    def test_delete_cloudmanager_connector_aws_pass(self, get_delete_api, get_connector_aws, delete_instance, get_token):
        set_module_args(self.set_args_delete_cloudmanager_connector_aws())
        get_token.return_value = 'test', 'test'
        my_obj = my_module()

        my_connector_aws = {
            'name': 'Dummyname',
            'client_id': 'test',
            'refresh_token': 'myrefresh_token',
        }
        get_connector_aws.return_value = my_connector_aws
        get_delete_api.return_value = None, None, None
        delete_instance.return_value = 'terminated'

        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print('Info: test_delete_cloudmanager_connector_aws: %s' % repr(exc.value))
        assert exc.value.args[0]['changed']
