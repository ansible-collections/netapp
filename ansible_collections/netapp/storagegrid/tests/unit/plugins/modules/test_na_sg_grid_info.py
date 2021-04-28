# (c) 2020, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

''' Unit Tests NetApp StorageGRID Grid Ansible module: na_sg_grid_info '''

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import json
import pytest

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.netapp.storagegrid.tests.unit.compat import unittest
from ansible_collections.netapp.storagegrid.tests.unit.compat.mock import patch

from ansible_collections.netapp.storagegrid.plugins.modules.na_sg_grid_info \
    import NetAppSgGatherInfo as sg_grid_info_module

# REST API canned responses when mocking send_request
SRR = {
    # common responses
    'empty_good': ({'data': []}, None),
    'end_of_sequence': (None, 'Unexpected call to send_request'),
    'generic_error': (None, 'Expected error'),
    'grid_accounts': (
        {
            'data': [
                {
                    'name': 'TestTenantAccount1',
                    'capabilities': ['management', 's3'],
                    'policy': {
                        'useAccountIdentitySource': True,
                        'allowPlatformServices': False,
                        'quotaObjectBytes': None,
                    },
                    'id': '12345678901234567891',
                },
                {
                    'name': 'TestTenantAccount2',
                    'capabilities': ['management', 's3'],
                    'policy': {
                        'useAccountIdentitySource': True,
                        'allowPlatformServices': False,
                        'quotaObjectBytes': None,
                    },
                    'id': '12345678901234567892',
                },
                {
                    'name': 'TestTenantAccount3',
                    'capabilities': ['management', 's3'],
                    'policy': {
                        'useAccountIdentitySource': True,
                        'allowPlatformServices': False,
                        'quotaObjectBytes': None,
                    },
                    'id': '12345678901234567893',
                },
            ]
        },
        None,
    ),
    'grid_alarms': ({'data': []}, None),
    'grid_audit': ({'data': {}}, None),
    'grid_compliance_global': ({'data': {}}, None),
    'grid_config': ({'data': {}}, None),
    'grid_config_management': ({'data': {}}, None),
    'grid_config_product_version': ({'data': {}}, None),
    'grid_deactivated_features': ({'data': {}}, None),
    'grid_dns_servers': ({'data': []}, None),
    'grid_domain_names': ({'data': []}, None),
    'grid_ec_profiles': ({'data': []}, None),
    'grid_expansion': ({'data': {}}, None),
    'grid_expansion_nodes': ({'data': []}, None),
    'grid_expansion_sites': ({'data': []}, None),
    'grid_grid_networks': ({'data': []}, None),
    'grid_groups': ({'data': []}, None),
    'grid_health': ({'data': {}}, None),
    'grid_health_topology': ({'data': {}}, None),
    'grid_identity_source': ({'data': {}}, None),
    'grid_ilm_criteria': ({'data': []}, None),
    'grid_ilm_policies': ({'data': []}, None),
    'grid_ilm_rules': ({'data': []}, None),
    'grid_license': ({'data': []}, None),
    'grid_management_certificate': ({'data': {}}, None),
    'grid_ntp_servers': ({'data': []}, None),
    'grid_recovery': ({'data': {}}, None),
    'grid_recovery_available_nodes': ({'data': []}, None),
    'grid_regions': ({'data': []}, None),
    'grid_schemes': ({'data': []}, None),
    'grid_snmp': ({'data': {}}, None),
    'grid_storage_api_certificate': ({'data': {}}, None),
    'grid_untrusted_client_network': ({'data': {}}, None),
    'grid_users': (
        {
            'data': [
                {
                    'accountId': '0',
                    'disable': False,
                    'federated': False,
                    'fullName': 'Root',
                    'id': '00000000-0000-0000-0000-000000000000',
                    'memberOf': None,
                    'uniqueName': 'root',
                    'userURN': 'urn:sgws:identity::0:root'
                },
            ]
        },
        None
    ),
    'grid_users_root': (
        {
            'data': {
                'accountId': '0',
                'disable': False,
                'federated': False,
                'fullName': 'Root',
                'id': '00000000-0000-0000-0000-000000000000',
                'memberOf': None,
                'uniqueName': 'root',
                'userURN': 'urn:sgws:identity::0:root'
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

    def set_args_run_sg_gather_facts_for_grid_accounts_info(self):
        return dict({
            'api_url': 'sgmi.example.com',
            'auth_token': '01234567-5678-9abc-78de-9fgabc123def',
            'validate_certs': False,
            'gather_subset': ['grid_accounts_info'],
        })

    def set_args_run_sg_gather_facts_for_grid_accounts_and_grid_users_root_info(self):
        return dict({
            'api_url': 'sgmi.example.com',
            'auth_token': '01234567-5678-9abc-78de-9fgabc123def',
            'validate_certs': False,
            'gather_subset': ['grid_accounts_info', 'grid/users/root'],
        })

    def test_module_fail_when_required_args_missing(self):
        ''' required arguments are reported as errors '''
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args(self.set_default_args_fail_check())
            sg_grid_info_module()
        print(
            'Info: test_module_fail_when_required_args_missing: %s'
            % exc.value.args[0]['msg']
        )

    def test_module_pass_when_required_args_present(self):
        ''' required arguments are reported as errors '''
        with pytest.raises(AnsibleExitJson) as exc:
            set_module_args(self.set_default_args_pass_check())
            sg_grid_info_module()
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
            sg_grid_info_module()
            exit_json(changed=True, msg='Induced arguments check')
        print(
            'Info: test_module_pass_when_optional_args_present: %s'
            % exc.value.args[0]['msg']
        )
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request')
    def test_run_sg_gather_facts_for_all_info_pass(self, mock_request):
        set_module_args(self.set_args_run_sg_gather_facts_for_all_info())
        my_obj = sg_grid_info_module()
        gather_subset = [
            'grid/accounts',
            'grid/alarms',
            'grid/audit',
            'grid/compliance-global',
            'grid/config',
            'grid/config/management',
            'grid/config/product-version',
            'grid/deactivated-features',
            'grid/dns-servers',
            'grid/domain-names',
            'grid/ec-profiles',
            'grid/expansion',
            'grid/expansion/nodes',
            'grid/expansion/sites',
            'grid/grid-networks',
            'grid/groups',
            'grid/health',
            'grid/health/topology',
            'grid/identity-source',
            'grid/ilm-criteria',
            'grid/ilm-policies',
            'grid/ilm-rules',
            'grid/license',
            'grid/management-certificate',
            'grid/ntp-servers',
            'grid/recovery/available-nodes',
            'grid/recovery',
            'grid/regions',
            'grid/schemes',
            'grid/snmp',
            'grid/storage-api-certificate',
            'grid/untrusted-client-network',
            'grid/users',
            'grid/users/root',
            'versions',
        ]
        mock_request.side_effect = [
            SRR['grid_accounts'],
            SRR['grid_alarms'],
            SRR['grid_audit'],
            SRR['grid_compliance_global'],
            SRR['grid_config'],
            SRR['grid_config_management'],
            SRR['grid_config_product_version'],
            SRR['grid_deactivated_features'],
            SRR['grid_dns_servers'],
            SRR['grid_domain_names'],
            SRR['grid_ec_profiles'],
            SRR['grid_expansion'],
            SRR['grid_expansion_nodes'],
            SRR['grid_expansion_sites'],
            SRR['grid_grid_networks'],
            SRR['grid_groups'],
            SRR['grid_health'],
            SRR['grid_health_topology'],
            SRR['grid_identity_source'],
            SRR['grid_ilm_criteria'],
            SRR['grid_ilm_policies'],
            SRR['grid_ilm_rules'],
            SRR['grid_license'],
            SRR['grid_management_certificate'],
            SRR['grid_ntp_servers'],
            SRR['grid_recovery_available_nodes'],
            SRR['grid_recovery'],
            SRR['grid_regions'],
            SRR['grid_schemes'],
            SRR['grid_snmp'],
            SRR['grid_storage_api_certificate'],
            SRR['grid_untrusted_client_network'],
            SRR['grid_users'],
            SRR['grid_users_root'],
            SRR['versions'],
            SRR['end_of_sequence'],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print('Info: test_run_sg_gather_facts_for_all_info_pass: %s' % repr(exc.value.args))
        assert set(exc.value.args[0]['sg_info']) == set(gather_subset)

    @patch('ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request')
    def test_run_sg_gather_facts_for_grid_accounts_info_pass(self, mock_request):
        set_module_args(self.set_args_run_sg_gather_facts_for_grid_accounts_info())
        my_obj = sg_grid_info_module()
        gather_subset = ['grid/accounts']
        mock_request.side_effect = [
            SRR['grid_accounts'],
            SRR['end_of_sequence'],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print('Info: test_run_sg_gather_facts_for_grid_accounts_info_pass: %s' % repr(exc.value.args))
        assert set(exc.value.args[0]['sg_info']) == set(gather_subset)

    @patch('ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request')
    def test_run_sg_gather_facts_for_grid_accounts_and_grid_users_root_info_pass(self, mock_request):
        set_module_args(self.set_args_run_sg_gather_facts_for_grid_accounts_and_grid_users_root_info())
        my_obj = sg_grid_info_module()
        gather_subset = ['grid/accounts', 'grid/users/root']
        mock_request.side_effect = [
            SRR['grid_accounts'],
            SRR['grid_users_root'],
            SRR['end_of_sequence'],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print('Info: test_run_sg_gather_facts_for_grid_accounts_and_grid_users_root_info_pass: %s' % repr(exc.value.args))
        assert set(exc.value.args[0]['sg_info']) == set(gather_subset)
