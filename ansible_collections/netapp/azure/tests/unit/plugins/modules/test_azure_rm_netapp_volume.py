# (c) 2019, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

''' unit tests ONTAP Ansible module: azure_rm_netapp_volume'''

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import json
import sys

import pytest
from requests import Response

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.netapp.azure.tests.unit.compat.mock import patch, Mock


# We can't import ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common in the UT environment
# and anyway, it's better to remove any external dependency in UTs.
class MockAzureRMModuleBase(object):
    ''' dummy base class for AzureRMNetAppModuleBase '''


mocked_module = type(sys)('mock_azure_import')
mocked_module.AzureRMModuleBase = MockAzureRMModuleBase
sys.modules['ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common'] = mocked_module

HAS_AZURE_RMNETAPP_IMPORT = True
try:
    # At this point, python believes the module is already loaded, so the import inside azure_rm_netapp_volume will be skipped.
    from ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume \
        import AzureRMNetAppVolume as volume_module
except ImportError:
    HAS_AZURE_RMNETAPP_IMPORT = False

# clean up to avoid side effects
del sys.modules['ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common']

HAS_AZURE_CLOUD_ERROR_IMPORT = True
try:
    from msrestazure.azure_exceptions import CloudError
except ImportError:
    HAS_AZURE_CLOUD_ERROR_IMPORT = False

if not HAS_AZURE_CLOUD_ERROR_IMPORT and sys.version_info < (3, 5):
    pytestmark = pytest.mark.skip('skipping as missing required azure_exceptions on 2.6 and 2.7')


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)  # pylint: disable=protected-access


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""


def exit_json(*args, **kwargs):  # pylint: disable=unused-argument
    """function to patch over exit_json; package return data into an exception"""
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):  # pylint: disable=unused-argument
    """function to patch over fail_json; package return data into an exception"""
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class MockAzureClient(object):
    ''' mock server connection to ONTAP host '''
    def __init__(self):
        ''' save arguments '''
        self.valid_volumes = ['test1', 'test2']

    def get(self, resource_group, account_name, pool_name, volume_name):  # pylint: disable=unused-argument
        if volume_name not in self.valid_volumes:
            invalid = Response()
            invalid.status_code = 404
            raise CloudError(response=invalid)
        else:
            return Mock(name=volume_name,
                        subnet_id='/resid/whatever/subnet_name',
                        mount_targets=[Mock(ip_address='1.2.3.4')]
                        )

    def create_or_update(self, body, resource_group, account_name, pool_name, volume_name):             # pylint: disable=unused-argument
        return None

    def begin_create_or_update(self, body, resource_group_name, account_name, pool_name, volume_name):  # pylint: disable=unused-argument
        return Mock(done=Mock(side_effect=[False, True]))

    def begin_update(self, body, resource_group_name, account_name, pool_name, volume_name):            # pylint: disable=unused-argument
        return Mock(done=Mock(side_effect=[False, True]))

    def begin_delete(self, resource_group_name, account_name, pool_name, volume_name):                  # pylint: disable=unused-argument
        return Mock(done=Mock(side_effect=[False, True]))


class MockAzureClientRaise(MockAzureClient):
    ''' mock server connection to ONTAP host '''
    response = Mock(status_code=400, context=None, headers=[], text=lambda: 'Forced exception')

    def begin_create_or_update(self, body, resource_group_name, account_name, pool_name, volume_name):  # pylint: disable=unused-argument
        raise CloudError(MockAzureClientRaise.response)

    def begin_update(self, body, resource_group_name, account_name, pool_name, volume_name):            # pylint: disable=unused-argument
        raise CloudError(MockAzureClientRaise.response)

    def begin_delete(self, resource_group_name, account_name, pool_name, volume_name):                  # pylint: disable=unused-argument
        raise CloudError(MockAzureClientRaise.response)


# using pytest natively, without unittest.TestCase
@pytest.fixture(name="patch_ansible")
def fixture_patch_ansible():
    with patch.multiple(basic.AnsibleModule,
                        exit_json=exit_json,
                        fail_json=fail_json) as mocks:
        yield mocks


def set_default_args():
    resource_group = 'azure'
    account_name = 'azure'
    pool_name = 'azure'
    name = 'test1'
    location = 'abc'
    file_path = 'azure'
    subnet_id = 'azure'
    virtual_network = 'azure'
    size = 100
    return dict({
        'resource_group': resource_group,
        'account_name': account_name,
        'pool_name': pool_name,
        'name': name,
        'location': location,
        'file_path': file_path,
        'subnet_id': subnet_id,
        'virtual_network': virtual_network,
        'size': size,
        'protocol_types': 'nfs'
    })


def test_module_fail_when_required_args_missing(patch_ansible):     # pylint: disable=unused-argument
    ''' required arguments are reported as errors '''
    with pytest.raises(AnsibleFailJson) as exc:
        set_module_args({})
        volume_module()
    print('Info: %s' % exc.value.args[0]['msg'])


@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
def test_ensure_get_called_valid_volume(mock_base, client_f):
    set_module_args(set_default_args())
    mock_base.return_value = Mock()
    client_f.return_value = Mock()
    my_obj = volume_module()
    my_obj.netapp_client.volumes = MockAzureClient()
    assert my_obj.get_azure_netapp_volume() is not None


@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
def test_ensure_get_called_non_existing_volume(mock_base, client_f):
    data = set_default_args()
    data['name'] = 'invalid'
    set_module_args(data)
    mock_base.return_value = Mock()
    client_f.return_value = Mock()
    my_obj = volume_module()
    my_obj.netapp_client.volumes = MockAzureClient()
    assert my_obj.get_azure_netapp_volume() is None


@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
@patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume.AzureRMNetAppVolume.get_azure_netapp_volume')
@patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume.AzureRMNetAppVolume.create_azure_netapp_volume')
def test_ensure_create_called(mock_create, mock_get, mock_base, client_f, patch_ansible):   # pylint: disable=unused-argument
    data = set_default_args()
    data['name'] = 'create'
    set_module_args(data)
    mock_get.side_effect = [
        None,                                                       # first get
        dict(mount_targets=[dict(ip_address='11.22.33.44')],        # get after create
             creation_token='abcd')
    ]
    mock_base.return_value = Mock()
    client_f.return_value = Mock()
    my_obj = volume_module()
    my_obj.netapp_client.volumes = MockAzureClient()
    with pytest.raises(AnsibleExitJson) as exc:
        my_obj.exec_module()
    assert exc.value.args[0]['changed']
    expected_mount_path = '11.22.33.44:/abcd'
    assert exc.value.args[0]['mount_path'] == expected_mount_path
    mock_create.assert_called_with()


@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
@patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume.AzureRMNetAppVolume.get_azure_netapp_volume')
def test_create(mock_get, mock_base, client_f, patch_ansible):  # pylint: disable=unused-argument
    data = set_default_args()
    data['name'] = 'create'
    data['protocol_types'] = 'nfsv4.1'
    set_module_args(data)
    mock_get.side_effect = [
        None,                                                       # first get
        dict(mount_targets=[dict(ip_address='11.22.33.44')],        # get after create
             creation_token='abcd')
    ]
    mock_base.return_value = Mock()
    client_f.return_value = Mock()
    my_obj = volume_module()
    my_obj.azure_auth = Mock(subscription_id='1234')
    my_obj._new_style = True
    my_obj.netapp_client.volumes = MockAzureClient()
    with pytest.raises(AnsibleExitJson) as exc:
        my_obj.exec_module()
    assert exc.value.args[0]['changed']
    expected_mount_path = '11.22.33.44:/abcd'
    assert exc.value.args[0]['mount_path'] == expected_mount_path


@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
@patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume.AzureRMNetAppVolume.get_azure_netapp_volume')
def test_create_exception(mock_get, mock_base, client_f, patch_ansible):    # pylint: disable=unused-argument
    data = set_default_args()
    data['name'] = 'create'
    data['protocol_types'] = 'nfsv4.1'
    set_module_args(data)
    mock_get.side_effect = [
        None,                                                       # first get
        dict(mount_targets=[dict(ip_address='11.22.33.44')],        # get after create
             creation_token='abcd')
    ]
    mock_base.return_value = Mock()
    client_f.return_value = Mock()
    my_obj = volume_module()
    my_obj.azure_auth = Mock(subscription_id='1234')
    my_obj._new_style = True
    my_obj.netapp_client.volumes = MockAzureClientRaise()
    with pytest.raises(AnsibleFailJson) as exc:
        my_obj.exec_module()
    expected_msg = 'Error creating volume'
    assert expected_msg in exc.value.args[0]['msg']


@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
@patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume.AzureRMNetAppVolume.get_azure_netapp_volume')
@patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume.AzureRMNetAppVolume.create_azure_netapp_volume')
def test_ensure_create_called_but_fail_on_get(mock_create, mock_get, mock_base, client_f, patch_ansible):   # pylint: disable=unused-argument
    data = set_default_args()
    data['name'] = 'create'
    set_module_args(data)
    mock_get.side_effect = [
        None,                                                       # first get
        dict(mount_targets=None,                                    # get after create
             creation_token='abcd')
    ]
    mock_base.return_value = Mock()
    client_f.return_value = Mock()
    my_obj = volume_module()
    my_obj.netapp_client.volumes = MockAzureClient()
    with pytest.raises(AnsibleFailJson) as exc:
        my_obj.exec_module()
    error = 'Error: volume create was created successfully, but mount target(s) cannot be found - volume details:'
    assert exc.value.args[0]['msg'].startswith(error)
    mock_create.assert_called_with()


@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
@patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume.AzureRMNetAppVolume.get_azure_netapp_volume')
@patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume.AzureRMNetAppVolume.create_azure_netapp_volume')
def test_ensure_create_called_but_fail_on_mount_target(mock_create, mock_get, mock_base, client_f, patch_ansible):  # pylint: disable=unused-argument
    data = set_default_args()
    data['name'] = 'create'
    set_module_args(data)
    mock_get.return_value = None
    mock_base.return_value = Mock()
    client_f.return_value = Mock()
    my_obj = volume_module()
    my_obj.netapp_client.volumes = MockAzureClient()
    with pytest.raises(AnsibleFailJson) as exc:
        my_obj.exec_module()
    error = 'Error: volume create was created successfully, but cannot be found.'
    assert exc.value.args[0]['msg'] == error
    mock_create.assert_called_with()


@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
@patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume.AzureRMNetAppVolume.get_azure_netapp_volume')
@patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume.AzureRMNetAppVolume.delete_azure_netapp_volume')
def test_ensure_delete_called(mock_delete, mock_get, mock_base, client_f, patch_ansible):   # pylint: disable=unused-argument
    data = set_default_args()
    data['state'] = 'absent'
    set_module_args(data)
    mock_base.return_value = Mock()
    client_f.return_value = Mock()
    mock_get.return_value = Mock()
    my_obj = volume_module()
    my_obj.netapp_client.volumes = MockAzureClient()
    with pytest.raises(AnsibleExitJson) as exc:
        my_obj.exec_module()
    assert exc.value.args[0]['changed']
    mock_delete.assert_called_with()


@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
@patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume.AzureRMNetAppVolume.get_azure_netapp_volume')
def test_delete(mock_get, mock_base, client_f, patch_ansible):  # pylint: disable=unused-argument
    data = set_default_args()
    data['name'] = 'delete'
    data['state'] = 'absent'
    set_module_args(data)
    mock_get.side_effect = [
        dict(mount_targets=[dict(ip_address='11.22.33.44')],        # first get
             creation_token='abcd')
    ]
    mock_base.return_value = Mock()
    client_f.return_value = Mock()
    my_obj = volume_module()
    my_obj.azure_auth = Mock(subscription_id='1234')
    my_obj._new_style = True
    my_obj.netapp_client.volumes = MockAzureClient()
    with pytest.raises(AnsibleExitJson) as exc:
        my_obj.exec_module()
    assert exc.value.args[0]['changed']
    expected_mount_path = ''
    assert exc.value.args[0]['mount_path'] == expected_mount_path


@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
@patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume.AzureRMNetAppVolume.get_azure_netapp_volume')
def test_delete_exception(mock_get, mock_base, client_f, patch_ansible):    # pylint: disable=unused-argument
    data = set_default_args()
    data['name'] = 'delete'
    data['state'] = 'absent'
    set_module_args(data)
    mock_get.side_effect = [
        dict(mount_targets=[dict(ip_address='11.22.33.44')],        # first get
             creation_token='abcd')
    ]
    mock_base.return_value = Mock()
    client_f.return_value = Mock()
    my_obj = volume_module()
    my_obj.azure_auth = Mock(subscription_id='1234')
    my_obj._new_style = True
    my_obj.netapp_client.volumes = MockAzureClientRaise()
    with pytest.raises(AnsibleFailJson) as exc:
        my_obj.exec_module()
    expected_msg = 'Error deleting volume'
    assert expected_msg in exc.value.args[0]['msg']


@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
@patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume.AzureRMNetAppVolume.get_azure_netapp_volume')
def test_modify(mock_get, mock_base, client_f, patch_ansible):  # pylint: disable=unused-argument
    data = set_default_args()
    data['name'] = 'modify'
    data['size'] = 200
    set_module_args(data)
    mock_get.side_effect = [
        dict(mount_targets=[dict(ip_address='11.22.33.44')],        # first get
             creation_token='abcd',
             usage_threshold=0),
        dict(mount_targets=[dict(ip_address='11.22.33.44')],        # get after modify
             creation_token='abcd',
             usage_threshold=10000000)
    ]
    mock_base.return_value = Mock()
    client_f.return_value = Mock()
    my_obj = volume_module()
    my_obj.azure_auth = Mock(subscription_id='1234')
    my_obj._new_style = True
    my_obj.netapp_client.volumes = MockAzureClient()
    with pytest.raises(AnsibleExitJson) as exc:
        my_obj.exec_module()
    assert exc.value.args[0]['changed']
    expected_mount_path = '11.22.33.44:/abcd'
    assert exc.value.args[0]['mount_path'] == expected_mount_path


@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
@patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume.AzureRMNetAppVolume.get_azure_netapp_volume')
def test_modify_exception(mock_get, mock_base, client_f, patch_ansible):    # pylint: disable=unused-argument
    data = set_default_args()
    data['name'] = 'modify'
    data['size'] = 200
    set_module_args(data)
    mock_get.side_effect = [
        dict(mount_targets=[dict(ip_address='11.22.33.44')],        # first get
             creation_token='abcd',
             usage_threshold=0),
        dict(mount_targets=[dict(ip_address='11.22.33.44')],        # get after modify
             creation_token='abcd',
             usage_threshold=10000000)
    ]
    mock_base.return_value = Mock()
    client_f.return_value = Mock()
    my_obj = volume_module()
    my_obj.azure_auth = Mock(subscription_id='1234')
    my_obj._new_style = True
    my_obj.netapp_client.volumes = MockAzureClientRaise()
    with pytest.raises(AnsibleFailJson) as exc:
        my_obj.exec_module()
    expected_msg = 'Error modifying volume'
    assert expected_msg in exc.value.args[0]['msg']


@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
@patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume.AzureRMNetAppVolume.get_azure_netapp_volume')
def test_modify_not_supported(mock_get, mock_base, client_f, patch_ansible):    # pylint: disable=unused-argument
    data = set_default_args()
    data['name'] = 'modify'
    data['location'] = 'east'
    set_module_args(data)
    mock_get.side_effect = [
        dict(mount_targets=[dict(ip_address='11.22.33.44')],        # first get
             creation_token='abcd',
             usage_threshold=0,
             location='west',
             name='old_name'),
        dict(mount_targets=[dict(ip_address='11.22.33.44')],        # get after modify
             creation_token='abcd',
             usage_threshold=10000000)
    ]
    mock_base.return_value = Mock()
    client_f.return_value = Mock()
    my_obj = volume_module()
    my_obj.azure_auth = Mock(subscription_id='1234')
    my_obj._new_style = True
    my_obj.netapp_client.volumes = MockAzureClient()
    with pytest.raises(AnsibleFailJson) as exc:
        my_obj.exec_module()
    expected_msg = "Error: the following properties cannot be modified: {'location': 'east'}"
    assert expected_msg in exc.value.args[0]['msg']


@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
@patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
def test_get_export_policy_rules(mock_base, client_f, patch_ansible):
    set_module_args(set_default_args())
    mock_base.return_value = Mock()
    client_f.return_value = Mock()
    my_obj = volume_module()
    my_obj.netapp_client.volumes = MockAzureClient()
    rules = my_obj.get_export_policy_rules()
    assert rules is None
    del my_obj.parameters['protocol_types']
    rules = my_obj.get_export_policy_rules()
    assert rules is None
    my_obj.parameters['protocol_types'] = ['nFsv4.1']
    rules = my_obj.get_export_policy_rules()
    assert rules is not None
    rules = vars(rules)
    assert 'rules' in rules
    rules = rules['rules']
    assert rules
    rule = vars(rules[0])
    assert rule['nfsv41']
    assert not rule['cifs']
