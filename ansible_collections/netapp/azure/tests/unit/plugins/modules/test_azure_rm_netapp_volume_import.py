# (c) 2021, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

''' unit tests ONTAP Ansible module: azure_rm_netapp_volume'''

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import json
import sys

import pytest
# from typing import Collection
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.netapp.azure.tests.unit.compat.mock import patch


if sys.version_info < (3, 5):
    pytestmark = pytest.mark.skip('skipping as missing imports on 2.6 and 2.7')


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)  # pylint: disable=protected-access


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""


def fail_json(*args, **kwargs):  # pylint: disable=unused-argument
    """function to patch over fail_json; package return data into an exception"""
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


@pytest.fixture(name="patch_ansible")
def fixture_patch_ansible():
    with patch.multiple(basic.AnsibleModule,
                        fail_json=fail_json) as mocks:
        yield mocks


# @patch('ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common.AzureRMNetAppModuleBase.__init__')
def test_import_error():
    orig_import = __import__

    def import_mock(name, *args):
        print('importing: %s' % name)
        if name.startswith('ansible_collections.netapp.azure.plugins.modules'):
            # force a relead to go through secondary imports
            sys.modules.pop(name, None)
        if name in ('azure.core.exceptions', 'azure.mgmt.netapp.models'):
            raise ImportError('forced error on %s' % name)
        return orig_import(name, *args)

    # mock_base.return_value = Mock()
    data = dict()
    set_module_args(data)
    with patch('builtins.__import__', side_effect=import_mock):
        from ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume import IMPORT_ERRORS
    assert any('azure.core.exceptions' in error for error in IMPORT_ERRORS)
    assert any('azure.mgmt.netapp.models' in error for error in IMPORT_ERRORS)


def test_main(patch_ansible):   # pylint: disable=unused-argument
    data = dict()
    set_module_args(data)
    from ansible_collections.netapp.azure.plugins.modules.azure_rm_netapp_volume import main
    with pytest.raises(AnsibleFailJson) as exc:
        main()
    expected_msg = "missing required arguments:"
    assert expected_msg in exc.value.args[0]['msg']
