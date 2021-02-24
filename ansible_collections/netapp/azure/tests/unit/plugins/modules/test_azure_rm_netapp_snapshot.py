# (c) 2019, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

''' unit tests ONTAP Ansible module: azure_rm_netapp_snapshot'''

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import json
import sys

import pytest
from requests import Response

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.netapp.azure.tests.unit.compat import unittest
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
    from ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_snapshot \
        import AzureRMNetAppSnapshot as snapshot_module
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
        self.valid_snapshots = ['test1', 'test2']

    def get(self, resource_group, account_name, pool_name, volume_name, snapshot_name):  # pylint: disable=unused-argument
        if snapshot_name not in self.valid_snapshots:
            invalid = Response()
            invalid.status_code = 404
            raise CloudError(response=invalid)
        else:
            return Mock(name=snapshot_name)

    def create(self, body, resource_group, account_name, pool_name, volume_name, snapshot_name):  # pylint: disable=unused-argument
        return None


class TestMyModule(unittest.TestCase):
    ''' a group of related Unit Tests '''

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)
        self.netapp_client = Mock()
        self.netapp_client.pools = MockAzureClient()
        self._netapp_client = None

    def set_default_args(self):
        resource_group = 'azure'
        account_name = 'azure'
        pool_name = 'azure'
        volume_name = 'azure'
        name = 'test1'
        location = 'abc'
        return dict({
            'resource_group': resource_group,
            'account_name': account_name,
            'pool_name': pool_name,
            'volume_name': volume_name,
            'name': name,
            'location': location
        })

    def test_module_fail_when_required_args_missing(self):
        ''' required arguments are reported as errors '''
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({})
            snapshot_module()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
    @patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
    def test_ensure_get_called_valid_snapshot(self, mock_base, client_f):
        set_module_args(self.set_default_args())
        mock_base.return_value = Mock()
        client_f.return_value = Mock()
        my_obj = snapshot_module()
        my_obj.netapp_client.snapshots = self.netapp_client.snapshots
        assert my_obj.get_azure_netapp_snapshot() is not None

    @patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
    @patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
    @patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_snapshot.AzureRMNetAppSnapshot.get_azure_netapp_snapshot')
    @patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_snapshot.AzureRMNetAppSnapshot.create_azure_netapp_snapshot')
    def test_ensure_create_called(self, mock_create, mock_get, client_f, mock_base):
        data = self.set_default_args()
        data['name'] = 'create'
        set_module_args(data)
        mock_get.return_value = None
        mock_base.return_value = Mock()
        client_f.return_value = Mock()
        my_obj = snapshot_module()
        my_obj.netapp_client.snapshots = self.netapp_client.snapshots
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.exec_module()
        assert exc.value.args[0]['changed']
        mock_create.assert_called_with()

    @patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.netapp_client')
    @patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
    @patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_snapshot.AzureRMNetAppSnapshot.get_azure_netapp_snapshot')
    @patch('ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_snapshot.AzureRMNetAppSnapshot.delete_azure_netapp_snapshot')
    def test_ensure_delete_called(self, mock_delete, mock_get, client_f, mock_base):
        data = self.set_default_args()
        data['state'] = 'absent'
        set_module_args(data)
        mock_base.return_value = Mock()
        client_f.return_value = Mock()
        mock_get.return_value = Mock()
        my_obj = snapshot_module()
        my_obj.netapp_client.snapshots = self.netapp_client.snapshots
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.exec_module()
        assert exc.value.args[0]['changed']
        mock_delete.assert_called_with()
