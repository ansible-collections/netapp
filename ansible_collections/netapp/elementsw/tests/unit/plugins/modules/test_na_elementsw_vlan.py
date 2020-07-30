''' unit test for Ansible module: na_elementsw_account.py '''

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import json
import pytest

from ansible_collections.netapp.elementsw.tests.unit.compat import unittest
from ansible_collections.netapp.elementsw.tests.unit.compat.mock import patch, Mock
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
import ansible_collections.netapp.elementsw.plugins.module_utils.netapp as netapp_utils

if not netapp_utils.has_sf_sdk():
    pytestmark = pytest.mark.skip('skipping as missing required SolidFire Python SDK')

from ansible_collections.netapp.elementsw.plugins.modules.na_elementsw_vlan \
    import ElementSWVlan as vlan  # module under test


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)  # pylint: disable=protected-access


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass


def exit_json(*args, **kwargs):  # pylint: disable=unused-argument
    """function to patch over exit_json; package return data into an exception"""
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):  # pylint: disable=unused-argument
    """function to patch over fail_json; package return data into an exception"""
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


ADD_ERROR = 'some_error_in_add_account'


class MockSFConnection(object):
    ''' mock connection to ElementSW host '''

    class Bunch(object):  # pylint: disable=too-few-public-methods
        ''' create object with arbitrary attributes '''
        def __init__(self, **kw):
            ''' called with (k1=v1, k2=v2), creates obj.k1, obj.k2 with values v1, v2 '''
            setattr(self, '__dict__', kw)

    class Vlan(object):
        def __init__(self, entries):
            self.__dict__.update(entries)

    def __init__(self, force_error=False, where=None):
        ''' save arguments '''
        self.force_error = force_error
        self.where = where

    def list_virtual_networks(self, virtual_network_tag=None):  # pylint: disable=unused-argument
        ''' list of vlans '''
        if virtual_network_tag == '1':
            add1 = self.Bunch(
                start='2.2.2.2',
                size=4
            )
            add2 = self.Bunch(
                start='3.3.3.3',
                size=4
            )
            vlan = self.Bunch(
                attributes={'key': 'value', 'config-mgmt': 'ansible', 'event-source': 'na_elementsw_vlan'},
                name="test",
                address_blocks=[
                    add1,
                    add2
                ],
                svip='192.168.1.2',
                gateway='0.0.0.0',
                netmask='255.255.248.0',
                namespace=False
            )
            vlans = self.Bunch(
                virtual_networks=[vlan]
            )
        else:
            vlans = self.Bunch(
                virtual_networks=[]
            )
        return vlans

    def add_virtual_network(self, virtual_network_tag=None, **create):  # pylint: disable=unused-argument
        ''' We don't check the return code, but could force an exception '''
        if self.force_error and 'add' in self.where:
            # The module does not check for a specific exception :(
            raise OSError(ADD_ERROR)

    def remove_virtual_network(self, virtual_network_tag=None):  # pylint: disable=unused-argument
        ''' We don't check the return code, but could force an exception '''
        if self.force_error and 'remove' in self.where:
            # The module does not check for a specific exception :(
            raise OSError(ADD_ERROR)

    def modify_virtual_network(self, virtual_network_tag=None, **modify):  # pylint: disable=unused-argument
        ''' We don't check the return code, but could force an exception '''
        if self.force_error and 'modify' in self.where:
            # The module does not check for a specific exception :(
            raise OSError(ADD_ERROR)


class TestMyModule(unittest.TestCase):
    ''' a group of related Unit Tests '''

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def test_module_fail_when_required_args_missing(self):
        ''' required arguments are reported as errors '''
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args({})
            vlan()
        print('Info: %s' % exc.value.args[0]['msg'])

    def mock_args(self):
        args = {
            'state': 'present',
            'name': 'test',
            'vlan_tag': 1,
            'address_blocks': [
                {'start': '192.168.1.2', 'size': 5}
            ],
            'hostname': 'hostname',
            'username': 'username',
            'password': 'password',
            'netmask': '255.255.248.0',
            'gateway': '0.0.0.0',
            'namespace': False,
            'svip': '192.168.1.2'
        }
        return dict(args)

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp_elementsw_module.NaElementSWModule.set_element_attributes')
    def test_successful_create(self, mock_set_attributes, mock_create_sf_connection):
        ''' successful create'''
        mock_set_attributes.return_value = {'key': 'new_value'}
        data = self.mock_args()
        data['vlan_tag'] = '3'
        set_module_args(data)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = vlan()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_successful_delete(self, mock_create_sf_connection):
        ''' successful delete'''
        data = self.mock_args()
        data['state'] = 'absent'
        set_module_args(data)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = vlan()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_successful_modify(self, mock_create_sf_connection):
        ''' successful modify'''
        data = self.mock_args()
        data['svip'] = '3.4.5.6'
        set_module_args(data)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = vlan()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    @patch('ansible_collections.netapp.elementsw.plugins.modules.na_elementsw_vlan.ElementSWVlan.get_network_details')
    def test_successful_modify_address_blocks_same_length(self, mock_get, mock_create_sf_connection):
        ''' successful modify'''
        mock_get.return_value = {
            'address_blocks': [
                {'start': '10.10.10.20', 'size': 5},
                {'start': '10.10.10.40', 'size': 5}
            ]
        }
        data = self.mock_args()
        data['address_blocks'] = [{'start': '10.10.10.20', 'size': 5},
                                  {'start': '10.20.10.50', 'size': 5}]
        set_module_args(data)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = vlan()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    @patch('ansible_collections.netapp.elementsw.plugins.modules.na_elementsw_vlan.ElementSWVlan.get_network_details')
    def test_successful_modify_address_blocks_different_length_1(self, mock_get, mock_create_sf_connection):
        ''' successful modify'''
        mock_get.return_value = {
            'address_blocks': [
                {'start': '10.10.10.20', 'size': 5},
                {'start': '10.20.10.30', 'size': 5}
            ]
        }
        data = self.mock_args()
        data['address_blocks'] = [{'start': '10.10.10.20', 'size': 5},
                                  {'start': '10.20.10.30', 'size': 5},
                                  {'start': '10.20.10.50', 'size': 5}]
        set_module_args(data)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = vlan()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    @patch('ansible_collections.netapp.elementsw.plugins.modules.na_elementsw_vlan.ElementSWVlan.get_network_details')
    def test_successful_modify_address_blocks_different_length_2(self, mock_get, mock_create_sf_connection):
        ''' successful modify'''
        mock_get.return_value = {
            'address_blocks': [
                {'start': '10.10.10.20', 'size': 5},
                {'start': '10.20.10.30', 'size': 5},
                {'start': '10.20.10.40', 'size': 5}
            ]
        }
        data = self.mock_args()
        data['address_blocks'] = [{'start': '10.10.10.20', 'size': 5},
                                  {'start': '10.20.10.40', 'size': 5},
                                  {'start': '10.20.10.30', 'size': 5}]
        set_module_args(data)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = vlan()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        assert not exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    @patch('ansible_collections.netapp.elementsw.plugins.modules.na_elementsw_vlan.ElementSWVlan.get_network_details')
    def test_successful_modify_address_blocks_different_length_3(self, mock_get, mock_create_sf_connection):
        ''' successful modify'''
        mock_get.return_value = {
            'address_blocks': [
                {'start': '10.10.10.20', 'size': 5},
                {'start': '10.10.10.30', 'size': 5},
                {'start': '10.20.10.40', 'size': 5}
            ]
        }
        data = self.mock_args()
        data['address_blocks'] = [{'start': '10.10.10.20', 'size': 5},
                                  {'start': '10.20.10.40', 'size': 5},
                                  {'start': '10.20.10.30', 'size': 5}]
        set_module_args(data)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = vlan()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_helper_validate_keys(self, mock_create_sf_connection):
        '''test validate_keys()'''
        data = self.mock_args()
        del data['svip']
        set_module_args(data)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = vlan()
        with pytest.raises(AnsibleFailJson) as exc:
            my_obj.validate_keys()
        msg = "One or more required fields ['address_blocks', 'svip', 'netmask', 'name'] for creating VLAN is missing"
        assert exc.value.args[0]['msg'] == msg

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_successful_modify_idempotent(self, mock_create_sf_connection):
        ''' successful modify'''
        data = self.mock_args()
        data['address_blocks'] = [{'start': '2.2.2.2', 'size': 4},
                                  {'start': '3.3.3.3', 'size': 4}]
        set_module_args(data)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = vlan()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        assert not exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_successful_modify_attribute_value(self, mock_create_sf_connection):
        ''' successful modify'''
        data = self.mock_args()
        data['address_blocks'] = [{'start': '2.2.2.2', 'size': 4},
                                  {'start': '3.3.3.3', 'size': 4}]
        data['attributes'] = {'key': 'value2'}
        set_module_args(data)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = vlan()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_successful_modify_attribute_key(self, mock_create_sf_connection):
        ''' successful modify'''
        data = self.mock_args()
        data['address_blocks'] = [{'start': '2.2.2.2', 'size': 4},
                                  {'start': '3.3.3.3', 'size': 4}]
        data['attributes'] = {'key2': 'value2'}
        set_module_args(data)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = vlan()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        assert exc.value.args[0]['changed']
