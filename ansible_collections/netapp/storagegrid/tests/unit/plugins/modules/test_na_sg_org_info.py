# (c) 2020, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

''' Unit Tests NetApp StorageGRID Org Ansible module: na_sg_org_info '''

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import json
import pytest

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.netapp.storagegrid.tests.unit.compat import unittest
from ansible_collections.netapp.storagegrid.tests.unit.compat.mock import patch

from ansible_collections.netapp.storagegrid.plugins.modules.na_sg_org_info \
    import NetAppSgGatherInfo as sg_org_info_module

# REST API canned responses when mocking send_request
SRR = {
    # common responses
    'empty_good': ({'data': []}, None),
    'end_of_sequence': (None, 'Unexpected call to send_request'),
    'generic_error': (None, 'Expected error'),
    'org_compliance_global': ({'data': {}}, None),
    'org_config': ({'data': {}}, None),
    'org_config_product_version': ({'data': {}}, None),
    'org_containers': ({'data': {}}, None),
    'org_deactivated_features': ({'data': {}}, None),
    'org_endpoints': ({'data': []}, None),
    'org_groups': ({'data': []}, None),
    'org_identity_source': ({'data': {}}, None),
    'org_regions': ({'data': []}, None),
    'org_users_current_user_s3_access_keys': ({'data': []}, None),
    'org_usage': ({'data': {}}, None),
    'org_users': (
        {
            'data': [
                {
                    'accountId': '99846664116007910793',
                    'disable': False,
                    'federated': False,
                    'fullName': 'Root',
                    'id': '00000000-0000-0000-0000-000000000000',
                    'memberOf': None,
                    'uniqueName': 'root',
                    'userURN': 'urn:sgws:identity::99846664116007910793:root'
                },
            ]
        },
        None
    ),
    'org_users_root': (
        {
            'data': {
                'accountId': '99846664116007910793',
                'disable': False,
                'federated': False,
                'fullName': 'Root',
                'id': '00000000-0000-0000-0000-000000000000',
                'memberOf': None,
                'uniqueName': 'root',
                'userURN': 'urn:sgws:identity::99846664116007910793:root'
            },
        },
        None
    ),
    'versions': ({'data': [2, 3]}, None),
}


def set_module_args(args):
    ''' Prepare arguments so that they will be picked up during module creation '''
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)  # pylint: disable=protected-access


class AnsibleExitJson(Exception):
    ''' Exception class to be raised by module.exit_json and caught by the test case '''
    pass


class AnsibleFailJson(Exception):
    ''' Exception class to be raised by module.fail_json and caught by the test case '''
    pass


def exit_json(*args, **kwargs):  # pylint: disable=unused-argument
    ''' Function to patch over exit_json; package return data into an exception '''
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):  # pylint: disable=unused-argument
    ''' Function to patch over fail_json; package return data into an exception '''
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class TestMyModule(unittest.TestCase):
    ''' A group of related Unit Tests '''

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def set_default_args_fail_check(self):
        return dict(
            {
                'api_url': 'sgmi.example.com',
            }
        )

    def set_default_args_pass_check(self):
        return dict(
            {
                'api_url': 'sgmi.example.com',
                'auth_token': '01234567-5678-9abc-78de-9fgabc123def',
            }
        )

    def set_default_optional_args_pass_check(self):
        return dict(
            {
                'api_url': 'sgmi.example.com',
                'auth_token': '01234567-5678-9abc-78de-9fgabc123def',
                'validate_certs': False,
                'gather_subset': ['all'],
                'parameters': {'limit': 5},
            }
        )

    def set_args_run_sg_gather_facts_for_all_info(self):
        return dict({
            'api_url': 'sgmi.example.com',
            'auth_token': '01234567-5678-9abc-78de-9fgabc123def',
            'validate_certs': False,
        })

    def set_args_run_sg_gather_facts_for_org_users_info(self):
        return dict({
            'api_url': 'sgmi.example.com',
            'auth_token': '01234567-5678-9abc-78de-9fgabc123def',
            'validate_certs': False,
            'gather_subset': ['org_users_info'],
        })

    def set_args_run_sg_gather_facts_for_org_users_and_org_users_root_info(self):
        return dict({
            'api_url': 'sgmi.example.com',
            'auth_token': '01234567-5678-9abc-78de-9fgabc123def',
            'validate_certs': False,
            'gather_subset': ['org_users_info', 'org/users/root'],
        })

    def test_module_fail_when_required_args_missing(self):
        ''' required arguments are reported as errors '''
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args(self.set_default_args_fail_check())
            sg_org_info_module()
        print(
            'Info: test_module_fail_when_required_args_missing: %s'
            % exc.value.args[0]['msg']
        )

    def test_module_pass_when_required_args_present(self):
        ''' required arguments are reported as errors '''
        with pytest.raises(AnsibleExitJson) as exc:
            set_module_args(self.set_default_args_pass_check())
            sg_org_info_module()
            exit_json(changed=True, msg='Induced arguments check')
        print(
            'Info: test_module_pass_when_required_args_present: %s'
            % exc.value.args[0]['msg']
        )
        assert exc.value.args[0]['changed']

    def test_module_pass_when_optional_args_present(self):
        ''' Optional arguments are reported as pass '''
        with pytest.raises(AnsibleExitJson) as exc:
            set_module_args(self.set_default_optional_args_pass_check())
            sg_org_info_module()
            exit_json(changed=True, msg='Induced arguments check')
        print(
            'Info: test_module_pass_when_optional_args_present: %s'
            % exc.value.args[0]['msg']
        )
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request')
    def test_run_sg_gather_facts_for_all_info_pass(self, mock_request):
        set_module_args(self.set_args_run_sg_gather_facts_for_all_info())
        my_obj = sg_org_info_module()
        gather_subset = [
            'org/compliance-global',
            'org/config',
            'org/config/product-version',
            'org/containers',
            'org/deactivated-features',
            'org/endpoints',
            'org/groups',
            'org/identity-source',
            'org/regions',
            'org/users/current-user/s3-access-keys',
            'org/usage',
            'org/users',
            'org/users/root',
            'versions',
        ]
        mock_request.side_effect = [
            SRR['org_compliance_global'],
            SRR['org_config'],
            SRR['org_config_product_version'],
            SRR['org_containers'],
            SRR['org_deactivated_features'],
            SRR['org_endpoints'],
            SRR['org_groups'],
            SRR['org_identity_source'],
            SRR['org_regions'],
            SRR['org_users_current_user_s3_access_keys'],
            SRR['org_usage'],
            SRR['org_users'],
            SRR['org_users_root'],
            SRR['versions'],
            SRR['end_of_sequence'],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print('Info: test_run_sg_gather_facts_for_all_info_pass: %s' % repr(exc.value.args))
        assert set(exc.value.args[0]['sg_info']) == set(gather_subset)

    @patch('ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request')
    def test_run_sg_gather_facts_for_org_users_info_pass(self, mock_request):
        set_module_args(self.set_args_run_sg_gather_facts_for_org_users_info())
        my_obj = sg_org_info_module()
        gather_subset = ['org/users']
        mock_request.side_effect = [
            SRR['org_users'],
            SRR['end_of_sequence'],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print('Info: test_run_sg_gather_facts_for_org_users_info_pass: %s' % repr(exc.value.args))
        assert set(exc.value.args[0]['sg_info']) == set(gather_subset)

    @patch('ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request')
    def test_run_sg_gather_facts_for_org_users_and_org_users_root_info_pass(self, mock_request):
        set_module_args(self.set_args_run_sg_gather_facts_for_org_users_and_org_users_root_info())
        my_obj = sg_org_info_module()
        gather_subset = ['org/users', 'org/users/root']
        mock_request.side_effect = [
            SRR['org_users'],
            SRR['org_users_root'],
            SRR['end_of_sequence'],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print('Info: test_run_sg_gather_facts_for_org_users_and_org_users_root_info_pass: %s' % repr(exc.value.args))
        assert set(exc.value.args[0]['sg_info']) == set(gather_subset)
