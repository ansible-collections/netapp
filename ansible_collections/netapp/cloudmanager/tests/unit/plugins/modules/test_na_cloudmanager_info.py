# (c) 2021, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

''' unit tests ONTAP Ansible module: '''

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json
import pytest

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.netapp.cloudmanager.tests.unit.compat.mock import patch, Mock

from ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_info \
    import NetAppCloudmanagerInfo as my_module


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
@pytest.fixture
def patch_ansible():
    with patch.multiple(basic.AnsibleModule,
                        exit_json=exit_json,
                        fail_json=fail_json) as mocks:
        yield mocks


def set_default_args_pass_check(patch_ansible):
    return dict({
        'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
        'refresh_token': 'myrefresh_token',
    })


def set_args_get_cloudmanager_working_environments_info():
    args = {
        'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
        'refresh_token': 'myrefresh_token',
        'gather_subsets': ['working_environments_info']
    }
    return args


def set_args_get_cloudmanager_aggregates_info():
    args = {
        'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
        'refresh_token': 'myrefresh_token',
        'gather_subsets': ['working_environments_info']
    }
    return args


def set_args_get_accounts_info():
    args = {
        'client_id': 'Nw4Q2O1kdnLtvhwegGalFnodEHUfPJWh',
        'refresh_token': 'myrefresh_token',
        'gather_subsets': ['accounts_info']
    }
    return args


def test_module_fail_when_required_args_missing(patch_ansible):
    ''' required arguments are reported as errors '''
    with pytest.raises(AnsibleFailJson) as exc:
        set_module_args({})
        my_module()
    print('Info: %s' % exc.value.args[0]['msg'])


@patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
@patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp_module.NetAppModule.get_working_environments_info')
def test_get_working_environments_info(working_environments_info, get_token, patch_ansible):
    args = dict(set_args_get_cloudmanager_working_environments_info())
    set_module_args(args)
    get_token.return_value = 'token_type', 'token'
    working_environments_info.return_value = {
        "azureVsaWorkingEnvironments": [
            {
                "name": "testazure",
                "cloudProviderName": "Azure",
                "creatorUserEmail": "samlp|NetAppSAML|testuser",
                "isHA": False,
                "publicId": "VsaWorkingEnvironment-az123456",
                "tenantId": "Tenant-2345",
                "workingEnvironmentType": "VSA",
            }
        ],
        "gcpVsaWorkingEnvironments": [],
        "onPremWorkingEnvironments": [],
        "vsaWorkingEnvironments": [
            {
                "name": "testAWS",
                "cloudProviderName": "Amazon",
                "creatorUserEmail": "samlp|NetAppSAML|testuser",
                "isHA": False,
                "publicId": "VsaWorkingEnvironment-aws12345",
                "tenantId": "Tenant-2345",
                "workingEnvironmentType": "VSA",
            },
            {
                "name": "testAWSHA",
                "cloudProviderName": "Amazon",
                "creatorUserEmail": "samlp|NetAppSAML|testuser",
                "isHA": True,
                "publicId": "VsaWorkingEnvironment-awsha345",
                "tenantId": "Tenant-2345",
                "workingEnvironmentType": "VSA",
            }
        ]
    }, None
    my_obj = my_module()
    my_obj.rest_api.api_root_path = "my_root_path"

    with pytest.raises(AnsibleExitJson) as exc:
        my_obj.apply()
    print('Info: test_create_cloudmanager_info: %s' % repr(exc.value))
    assert not exc.value.args[0]['changed']


@patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
@patch(
    'ansible_collections.netapp.cloudmanager.plugins.modules.na_cloudmanager_info.NetAppCloudmanagerInfo.get_aggregates_info')
def test_get_aggregates_info(aggregates_info, get_token, patch_ansible):
    args = dict(set_args_get_cloudmanager_aggregates_info())
    set_module_args(args)
    get_token.return_value = 'token_type', 'token'
    aggregates_info.return_value = {
        "azureVsaWorkingEnvironments": {
            "VsaWorkingEnvironment-az123456": [
                {
                    "availableCapacity": {
                        "size": 430.0,
                        "unit": "GB"
                    },
                    "disks": [
                        {
                            "device": "LUN 3.1",
                            "name": "testazure-01-1",
                            "ownerNode": "testazure-01",
                            "position": "data",
                        }
                    ],
                    "encryptionType": "notEncrypted",
                    "homeNode": "testazure-01",
                    "isRoot": False,
                    "name": "aggr1",
                    "ownerNode": "testazure-01",
                    "providerVolumes": [
                        {
                            "device": "1",
                            "diskType": "Premium_LRS",
                            "encrypted": False,
                            "instanceId": "testazureid",
                            "name": "testazuredatadisk1",
                            "size": {
                                "size": 500.0,
                                "unit": "GB"
                            },
                            "state": "available"
                        }
                    ],
                    "sidlEnabled": False,
                    "snaplockType": "non_snaplock",
                    "state": "online",
                    "totalCapacity": {
                        "size": 500.0,
                        "unit": "GB"
                    },
                    "usedCapacity": {
                        "size": 70.0,
                        "unit": "GB"
                    },
                    "volumes": [
                        {
                            "isClone": False,
                            "name": "svm_testazure_root",
                            "rootVolume": True,
                            "thinProvisioned": True,
                            "totalSize": {
                                "size": 1.0,
                                "unit": "GB"
                            },
                            "usedSize": {
                                "size": 0.000339508056640625,
                                "unit": "GB"
                            }
                        },
                        {
                            "isClone": False,
                            "name": "azv1",
                            "rootVolume": False,
                            "thinProvisioned": True,
                            "totalSize": {
                                "size": 500.0,
                                "unit": "GB"
                            },
                            "usedSize": {
                                "size": 0.0,
                                "unit": "GB"
                            }
                        }
                    ]
                },
            ]
        },
        "gcpVsaWorkingEnvironments": {},
        "onPremWorkingEnvironments": {},
        "vsaWorkingEnvironments": {
            "VsaWorkingEnvironment-aws12345": [
                {
                    "availableCapacity": {
                        "size": 430.0,
                        "unit": "GB"
                    },
                    "disks": [
                        {
                            "device": "xvdh vol-381",
                            "name": "testAWSHA-01-i-196h",
                            "ownerNode": "testAWSHA-01",
                            "position": "data",
                        },
                        {
                            "device": "xvdh vol-382",
                            "name": "testAWSHA-01-i-195h",
                            "ownerNode": "testAWSHA-01",
                            "position": "data",
                        }
                    ],
                    "encryptionType": "cloudEncrypted",
                    "homeNode": "testAWSHA-01",
                    "isRoot": False,
                    "name": "aggr1",
                    "ownerNode": "testAWSHA-01",
                    "providerVolumes": [
                        {
                            "device": "/dev/xvdh",
                            "diskType": "gp2",
                            "encrypted": True,
                            "id": "vol-381",
                            "instanceId": "i-196",
                            "name": "vol-381",
                            "size": {
                                "size": 500.0,
                                "unit": "GB"
                            },
                            "state": "in-use"
                        },
                        {
                            "device": "/dev/xvdh",
                            "diskType": "gp2",
                            "encrypted": True,
                            "id": "vol-382",
                            "instanceId": "i-195",
                            "name": "vol-382",
                            "size": {
                                "size": 500.0,
                                "unit": "GB"
                            },
                            "state": "in-use"
                        }
                    ],
                    "sidlEnabled": True,
                    "snaplockType": "non_snaplock",
                    "state": "online",
                    "totalCapacity": {
                        "size": 500.0,
                        "unit": "GB"
                    },
                    "usedCapacity": {
                        "size": 70.0,
                        "unit": "GB"
                    },
                    "volumes": [
                        {
                            "isClone": False,
                            "name": "svm_testAWSHA_root",
                            "rootVolume": True,
                            "thinProvisioned": True,
                            "totalSize": {
                                "size": 1.0,
                                "unit": "GB"
                            },
                            "usedSize": {
                                "size": 0.000339508056640625,
                                "unit": "GB"
                            }
                        },
                        {
                            "isClone": False,
                            "name": "vha",
                            "rootVolume": False,
                            "thinProvisioned": True,
                            "totalSize": {
                                "size": 100.0,
                                "unit": "GB"
                            },
                            "usedSize": {
                                "size": 0.0,
                                "unit": "GB"
                            }
                        }
                    ]
                }
            ],
            "VsaWorkingEnvironment-awsha345": [
                {
                    "availableCapacity": {
                        "size": 430.0,
                        "unit": "GB"
                    },
                    "disks": [
                        {
                            "device": "xvdg vol-369",
                            "name": "testAWS-01-i-190g",
                            "ownerNode": "testAWS-01",
                            "position": "data",
                        }
                    ],
                    "encryptionType": "cloudEncrypted",
                    "homeNode": "testAWS-01",
                    "isRoot": False,
                    "name": "aggr1",
                    "ownerNode": "testAWS-01",
                    "providerVolumes": [
                        {
                            "device": "/dev/xvdg",
                            "diskType": "gp2",
                            "encrypted": True,
                            "id": "vol-369",
                            "instanceId": "i-190",
                            "name": "vol-369",
                            "size": {
                                "size": 500.0,
                                "unit": "GB"
                            },
                            "state": "in-use"
                        }
                    ],
                    "sidlEnabled": True,
                    "snaplockType": "non_snaplock",
                    "state": "online",
                    "totalCapacity": {
                        "size": 500.0,
                        "unit": "GB"
                    },
                    "usedCapacity": {
                        "size": 70.0,
                        "unit": "GB"
                    },
                    "volumes": [
                        {
                            "isClone": False,
                            "name": "svm_testAWS_root",
                            "rootVolume": True,
                            "thinProvisioned": True,
                            "totalSize": {
                                "size": 1.0,
                                "unit": "GB"
                            },
                            "usedSize": {
                                "size": 0.000339508056640625,
                                "unit": "GB"
                            }
                        },
                        {
                            "isClone": False,
                            "name": "v1",
                            "rootVolume": False,
                            "thinProvisioned": True,
                            "totalSize": {
                                "size": 100.0,
                                "unit": "GB"
                            },
                            "usedSize": {
                                "size": 0.0,
                                "unit": "GB"
                            }
                        }
                    ]
                },
                {
                    "availableCapacity": {
                        "size": 86.0,
                        "unit": "GB"
                    },
                    "disks": [
                        {
                            "device": "xvdh vol-371",
                            "name": "testAWS-01-i-190h",
                            "ownerNode": "testAWS-01",
                            "position": "data",
                        }
                    ],
                    "encryptionType": "cloudEncrypted",
                    "homeNode": "testAWS-01",
                    "isRoot": False,
                    "name": "aggr2",
                    "ownerNode": "testAWS-01",
                    "providerVolumes": [
                        {
                            "device": "/dev/xvdh",
                            "diskType": "gp2",
                            "encrypted": True,
                            "id": "vol-371",
                            "instanceId": "i-190",
                            "name": "vol-371",
                            "size": {
                                "size": 100.0,
                                "unit": "GB"
                            },
                            "state": "in-use"
                        }
                    ],
                    "sidlEnabled": True,
                    "snaplockType": "non_snaplock",
                    "state": "online",
                    "totalCapacity": {
                        "size": 100.0,
                        "unit": "GB"
                    },
                    "usedCapacity": {
                        "size": 0.0,
                        "unit": "GB"
                    },
                    "volumes": []
                }
            ]
        }
    }
    my_obj = my_module()
    my_obj.rest_api.api_root_path = "my_root_path"

    with pytest.raises(AnsibleExitJson) as exc:
        my_obj.apply()
    print('Info: test_create_cloudmanager_info: %s' % repr(exc.value))
    assert not exc.value.args[0]['changed']


@patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp.CloudManagerRestAPI.get_token')
@patch('ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp_module.NetAppModule.get_accounts_info')
def test_get_accounts_info(accounts_info, get_token, patch_ansible):
    args = dict(set_args_get_accounts_info())
    set_module_args(args)
    get_token.return_value = 'token_type', 'token'
    accounts_info.return_value = {
        "awsAccounts": [
            {
                "accessKey": "1",
                "accountId": "123456789011",
                "accountName": "tami",
                "accountType": "AWS_KEYS",
                "publicId": "CloudProviderAccount-Ekj6L9QX",
                "subscriptionId": "hackExp10Days",
                "vsaList": []
            },
            {
                "accessKey": "",
                "accountId": "123456789011",
                "accountName": "Instance Profile",
                "accountType": "INSTANCE_PROFILE",
                "occmRole": "occmRole",
                "publicId": "InstanceProfile",
                "subscriptionId": "hackExp10Days",
                "vsaList": [
                    {
                        "name": "CVO_AWSCluster",
                        "publicId": "VsaWorkingEnvironment-9m3I6i3I",
                        "workingEnvironmentType": "AWS"
                    },
                    {
                        "name": "testAWS1",
                        "publicId": "VsaWorkingEnvironment-JCzkA9OX",
                        "workingEnvironmentType": "AWS"
                    },
                ]
            }
        ],
        "azureAccounts": [
            {
                "accountName": "AzureKeys",
                "accountType": "AZURE_KEYS",
                "applicationId": "1",
                "publicId": "CloudProviderAccount-T84ceMYu",
                "tenantId": "1",
                "vsaList": [
                    {
                        "name": "testAZURE",
                        "publicId": "VsaWorkingEnvironment-jI0tbceH",
                        "workingEnvironmentType": "AZURE"
                    },
                    {
                        "name": "test",
                        "publicId": "VsaWorkingEnvironment-00EnDcfB",
                        "workingEnvironmentType": "AZURE"
                    },
                ]
            },
            {
                "accountName": "s",
                "accountType": "AZURE_KEYS",
                "applicationId": "1",
                "publicId": "CloudProviderAccount-XxbN95dj",
                "tenantId": "1",
                "vsaList": []
            }
        ],
        "gcpStorageAccounts": [],
        "nssAccounts": [
            {
                "accountName": "TESTCLOUD2",
                "accountType": "NSS_KEYS",
                "nssUserName": "TESTCLOUD2",
                "publicId": "be2f3cac-352a-46b9-a341-a446c35b61c9",
                "vsaList": [
                    {
                        "name": "testAWS",
                        "publicId": "VsaWorkingEnvironment-3txYJOsX",
                        "workingEnvironmentType": "AWS"
                    },
                    {
                        "name": "testAZURE",
                        "publicId": "VsaWorkingEnvironment-jI0tbceH",
                        "workingEnvironmentType": "AZURE"
                    },
                ]
            },
            {
                "accountName": "ntapitdemo",
                "accountType": "NSS_KEYS",
                "nssUserName": "ntapitdemo",
                "publicId": "01e43a7d-cfc9-4682-aa12-15374ce81638",
                "vsaList": [
                    {
                        "name": "test",
                        "publicId": "VsaWorkingEnvironment-00EnDcfB",
                        "workingEnvironmentType": "AZURE"
                    }
                ]
            }
        ]
    }, None
    my_obj = my_module()
    my_obj.rest_api.api_root_path = "my_root_path"

    with pytest.raises(AnsibleExitJson) as exc:
        my_obj.apply()
    print('Info: test_create_cloudmanager_info: %s' % repr(exc.value))
    assert not exc.value.args[0]['changed']
