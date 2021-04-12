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
from ansible_collections.netapp.cloudmanager.tests.unit.compat.mock import patch

from ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_azure \
    import NetAppCloudManagerConnectorAzure as my_module, IMPORT_EXCEPTION

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


class MockCMConnection:
    ''' Mock response of http connections '''

    def __init__(self, kind=None, parm1=None):
        self.type = kind
        self.parm1 = parm1


# using pytest natively, without unittest.TestCase
@pytest.fixture
def patch_ansible():
    with patch.multiple(basic.AnsibleModule,
                        exit_json=exit_json,
                        fail_json=fail_json) as mocks:
        yield mocks


def set_default_args_pass_check():
    return dict({
        'state': 'present',
        'name': 'TestA',
        'location': 'westus',
        'resource_group': 'occm_group_westus',
        'subnet_id': 'Subnet1',
        'vnet_id': 'Vnet1',
        'subscription_id': 'subscriptionId-test',
        'refresh_token': 'myrefresh_token',
        'account_id': 'account-test',
        'company': 'NetApp',
        'admin_username': 'test',
        'admin_password': 'test',
        'network_security_group_name': 'test'
    })


def set_args_create_cloudmanager_connector_azure():
    return dict({
        'state': 'present',
        'name': 'TestA',
        'location': 'westus',
        'resource_group': 'occm_group_westus',
        'subnet_id': 'Subnet1',
        'vnet_id': 'Vnet1',
        'subscription_id': 'subscriptionId-test',
        'refresh_token': 'myrefresh_token',
        'account_id': 'account-test',
        'company': 'NetApp',
        'admin_username': 'test',
        'admin_password': 'test',
        'network_security_group_name': 'test'
    })


def set_args_delete_cloudmanager_connector_azure():
    return dict({
        'state': 'absent',
        'name': 'Dummyname',
        'client_id': 'test',
        'location': 'westus',
        'resource_group': 'occm_group_westus',
        'subnet_id': 'Subnet1',
        'vnet_id': 'Vnet1',
        'subscription_id': 'subscriptionId-test',
        'refresh_token': 'myrefresh_token',
        'account_id': 'account-test',
        'company': 'NetApp',
        'admin_username': 'test',
        'admin_password': 'test',
        'network_security_group_name': 'test'
    })


def test_module_fail_when_required_args_missing(patch_ansible):
    ''' required arguments are reported as errors '''
    with pytest.raises(AnsibleFailJson) as exc:
        set_module_args({})
        my_module()
    print('Info: %s' % exc.value.args[0]['msg'])


@patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
def test_module_fail_when_required_args_present(get_token, patch_ansible):
    ''' required arguments are reported as errors '''
    with pytest.raises(AnsibleExitJson) as exc:
        set_module_args(set_default_args_pass_check())
        get_token.return_value = 'test', 'test'
        my_module()
        exit_json(changed=True, msg="TestCase Fail when required args are present")
    assert exc.value.args[0]['changed']


@patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
@patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_azure.NetAppCloudManagerConnectorAzure.deploy_azure')
@patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_azure.NetAppCloudManagerConnectorAzure.register_agent_to_service')
@patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.post')
def test_create_cloudmanager_connector_azure_pass(get_post_api, register_agent_to_service, deploy_azure, get_token, patch_ansible):
    set_module_args(set_args_create_cloudmanager_connector_azure())
    get_token.return_value = 'test', 'test'
    my_obj = my_module()

    get_post_api.return_value = None, None, None
    register_agent_to_service.return_value = 'test', 'test'
    deploy_azure.return_value = None

    with pytest.raises(AnsibleExitJson) as exc:
        my_obj.apply()
    print('Info: test_create_cloudmanager_connector_azure: %s' % repr(exc.value))
    assert exc.value.args[0]['changed']


@patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
@patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_azure.NetAppCloudManagerConnectorAzure.get_deploy_azure_vm')
@patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_azure.NetAppCloudManagerConnectorAzure.delete_azure_occm')
@patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.delete')
def test_delete_cloudmanager_connector_azure_pass(get_delete_api, delete_azure_occm, get_deploy_azure_vm, get_token, patch_ansible):
    set_module_args(set_args_delete_cloudmanager_connector_azure())
    get_token.return_value = 'test', 'test'
    my_obj = my_module()

    get_deploy_azure_vm.return_value = True
    delete_azure_occm.return_value = None
    get_delete_api.return_value = None, None, None

    with pytest.raises(AnsibleExitJson) as exc:
        my_obj.apply()
    print('Info: test_delete_cloudmanager_connector_azure: %s' % repr(exc.value))
    assert exc.value.args[0]['changed']
