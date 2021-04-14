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

from ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_gcp \
    import NetAppCloudManagerConnectorGCP as my_module

IMPORT_ERRORS = list()
HAS_GCP_COLLECTION = False

try:
    from google.auth.transport import requests
    from google.oauth2 import service_account
    import yaml
    HAS_GCP_COLLECTION = True
except ImportError as exc:
    IMPORT_ERRORS.append(str(exc))

if not HAS_GCP_COLLECTION and sys.version_info < (3, 5):
    pytestmark = pytest.mark.skip('skipping as missing required google packages on 2.6 and 2.7')


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


# using pytest natively, without unittest.TestCase
@pytest.fixture(name='patch_ansible')
def fixture_patch_ansible():
    with patch.multiple(basic.AnsibleModule,
                        exit_json=exit_json,
                        fail_json=fail_json) as mocks:
        yield mocks


def set_default_args_pass_check():
    return dict({
        'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
        'refresh_token': 'my_refresh_token',
        'state': 'present',
        'name': 'TestG',
        'project_id': 'tlv-support',
        'zone': 'us-west-1',
        'account_id': 'account-test',
        'company': 'NetApp',
        'service_account_email': 'terraform-user@tlv-support.iam.gserviceaccount.com',
        'service_account_path': 'test.json',
    })


def set_args_create_cloudmanager_connector_gcp():
    return dict({
        'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
        'refresh_token': 'my_refresh_token',
        'state': 'present',
        'name': 'TestG',
        'project_id': 'tlv-support',
        'zone': 'us-west-1',
        'account_id': 'account-test',
        'company': 'NetApp',
        'service_account_email': 'terraform-user@tlv-support.iam.gserviceaccount.com',
        'service_account_path': 'test.json',
    })


def set_args_delete_cloudmanager_connector_gcp():
    return dict({
        'client_id': 'test',
        'refresh_token': 'my_refresh_token',
        'state': 'absent',
        'name': 'Dummyname',
        'project_id': 'tlv-support',
        'zone': 'us-west-1',
        'account_id': 'account-test',
        'company': 'NetApp',
        'service_account_email': 'terraform-user@tlv-support.iam.gserviceaccount.com',
        'service_account_path': 'test.json',
    })


def test_module_fail_when_required_args_missing(patch_ansible):
    ''' required arguments are reported as errors '''
    with pytest.raises(AnsibleFailJson) as exc:
        set_module_args({})
        my_module()
    print('Info: %s' % exc.value.args[0]['msg'])


@patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_gcp.NetAppCloudManagerConnectorGCP.get_gcp_token')
@patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
def test_module_fail_when_required_args_present(get_token, get_gcp_token, patch_ansible):
    ''' required arguments are reported as errors '''
    with pytest.raises(AnsibleExitJson) as exc:
        set_module_args(set_default_args_pass_check())
        get_token.return_value = 'test', 'test'
        get_gcp_token.return_value = 'token', None
        my_module()
        exit_json(changed=True, msg="TestCase Fail when required args are present")
    assert exc.value.args[0]['changed']


@patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
@patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_gcp.NetAppCloudManagerConnectorGCP.get_gcp_token')
@patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_gcp.NetAppCloudManagerConnectorGCP.deploy_gcp_vm')
@patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_gcp.NetAppCloudManagerConnectorGCP.get_custom_data_for_gcp')
@patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_gcp.NetAppCloudManagerConnectorGCP.create_occm_gcp')
@patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.post')
def test_create_cloudmanager_connector_gcp_pass(get_post_api, create_occm_gcp, get_custom_data_for_gcp, deploy_gcp_vm, get_gcp_token, get_token, patch_ansible):
    set_module_args(set_args_create_cloudmanager_connector_gcp())
    get_token.return_value = 'test', 'test'
    get_gcp_token.return_value = 'test', None
    my_obj = my_module()

    deploy_gcp_vm.return_value = None, 'test', None
    get_custom_data_for_gcp.return_value = 'test', 'test', None
    create_occm_gcp.return_value = 'test'
    get_post_api.return_value = None, None, None

    with pytest.raises(AnsibleExitJson) as exc:
        my_obj.apply()
    print('Info: test_create_cloudmanager_connector_gcp: %s' % repr(exc.value))
    assert exc.value.args[0]['changed'], create_occm_gcp.return_value[1]


@patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
@patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_gcp.NetAppCloudManagerConnectorGCP.get_gcp_token')
@patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_gcp.NetAppCloudManagerConnectorGCP.delete_occm_gcp')
@patch('ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_connector_gcp.NetAppCloudManagerConnectorGCP.get_deploy_vm')
@patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.delete')
def test_delete_cloudmanager_connector_gcp_pass(get_delete_api, get_deploy_vm, delete_occm_gcp, get_gcp_token, get_token, patch_ansible):
    set_module_args(set_args_delete_cloudmanager_connector_gcp())
    get_token.return_value = 'test', 'test'
    get_gcp_token.return_value = 'test', None
    my_obj = my_module()

    my_connector_gcp = {
        'name': 'Dummyname-vm-boot-deployment',
        'client_id': 'test',
        'refresh_token': 'my_refresh_token',
    }
    get_deploy_vm.return_value = my_connector_gcp
    get_delete_api.return_value = None, None, None
    delete_occm_gcp.return_value = 'terminated'

    with pytest.raises(AnsibleExitJson) as exc:
        my_obj.apply()
    print('Info: test_delete_cloudmanager_connector_gcp: %s' % repr(exc.value))

    assert exc.value.args[0]['changed']
