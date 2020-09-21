''' unit tests for Ansible module: na_elementsw_info.py '''

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import inspect
import json
import pytest

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.netapp.elementsw.tests.unit.compat import unittest
from ansible_collections.netapp.elementsw.tests.unit.compat.mock import patch
import ansible_collections.netapp.elementsw.plugins.module_utils.netapp as netapp_utils

if not netapp_utils.has_sf_sdk():
    pytestmark = pytest.mark.skip('skipping as missing required SolidFire Python SDK')

from ansible_collections.netapp.elementsw.plugins.modules.na_elementsw_network_interfaces \
    import ElementSWNetworkInterfaces as my_module  # module under test


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


NODE_ID1 = 777
NODE_ID2 = 888
NODE_ID3 = 999

DEFAULT_KEYS_1G = ('mtu_1g', 'bond_mode_1g', 'lacp_1g')
DEFAULT_KEYS_10G = ('mtu_10g', 'bond_mode_10g', 'lacp_10g')

DEFAULT_ATTRS = dict({'mtu': '1500', 'bond-mode': 'ActivePassive', 'bond-lacp_rate': 'Slow'})
# don't use keys() as order is not guaranteed with python 2.x
DEFAULT_ATTR_KEYS = ('mtu', 'bond-mode', 'bond-lacp_rate')
MAPPING_1G = zip(DEFAULT_KEYS_1G, DEFAULT_ATTR_KEYS)
MAPPING_10G = zip(DEFAULT_KEYS_10G, DEFAULT_ATTR_KEYS)
print('zip', repr(list(MAPPING_1G)))


class MockSFConnection(object):
    ''' mock connection to ElementSW host '''

    class Bunch(object):  # pylint: disable=too-few-public-methods
        ''' create object with arbitrary attributes '''
        def __init__(self, **kw):
            ''' called with (k1=v1, k2=v2), creates obj.k1, obj.k2 with values v1, v2 '''
            setattr(self, '__dict__', kw)

        def __repr__(self):
            results = dict()
            for key, value in vars(self).items():
                results[key] = repr(value)
            return repr(results)

        def to_json(self):
            return json.loads(json.dumps(self, default=lambda x: x.__dict__))

    def __init__(self, force_error=False, where=None):
        ''' save arguments '''
        self.force_error = force_error
        self.where = where
        self.nodes = [NODE_ID1, NODE_ID2, NODE_ID3]
        self._port = 442
        self.called = list()
        self.set_network_config_args = dict()
        if force_error and where == 'cx':
            raise netapp_utils.solidfire.common.ApiConnectionError('testme')

    def record(self, args, kwargs):     # pylint: disable=unused-argument
        name = inspect.stack()[1][3]    # caller function name
        # print('%s: , args: %s, kwargs: %s' % (name, args, kwargs))
        self.called.append(name)

    def set_network_config(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.record(repr(args), repr(kwargs))
        print('network:', kwargs['network'].to_json())
        self.set_network_config_args = kwargs['network'].to_json()


class TestMyModule(unittest.TestCase):
    ''' a group of related Unit Tests '''

    ARGS = {
        'ip_address_1g': 'ip_address_1g',
        'subnet_1g': 'subnet_1g',
        'gateway_address_1g': 'gateway_address_1g',
        'mtu_1g': 'mtu_1g',         # make sure the use a value != from default
        'bond_mode_1g': 'ALB',      # make sure the use a value != from default
        'lacp_1g': 'Fast',          # make sure the use a value != from default
        'ip_address_10g': 'ip_address_10g',
        'subnet_10g': 'subnet_10g',
        'gateway_address_10g': 'gateway_address_10g',
        'mtu_10g': 'mtu_10g',       # make sure the use a value != from default
        'bond_mode_10g': 'LACP',    # make sure the use a value != from default
        'lacp_10g': 'Fast',         # make sure the use a value != from default
        'method': 'static',
        'dns_nameservers': 'dns_nameservers',
        'dns_search_domains': 'dns_search_domains',
        'virtual_network_tag': 'virtual_network_tag',
        'hostname': 'hostname',
        'username': 'username',
        'password': 'password',
    }

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
            my_module()
        print('Info: %s' % exc.value.args[0]['msg'])

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_create_all(self, mock_create_sf_connection):
        ''' create with all options '''
        args = dict(self.ARGS)  # deep copy as other tests can modify args
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']
        assert 'Bond1G' in my_obj.sfe.set_network_config_args

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_create_1g_only(self, mock_create_sf_connection):
        ''' create with 1g options only '''
        args = dict(self.ARGS)  # deep copy as other tests can modify args
        for key in list(args):
            if '10g' in key:
                del args[key]
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']
        assert 'Bond1G' in my_obj.sfe.set_network_config_args
        assert my_obj.sfe.set_network_config_args['Bond1G']['bond-lacp_rate'] == args['lacp_1g']
        for key, attr in MAPPING_1G:
            assert my_obj.sfe.set_network_config_args['Bond1G'][attr] == args[key]

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_create_1g_only_with_default(self, mock_create_sf_connection):
        ''' create with 1g options only '''
        args = dict(self.ARGS)  # deep copy as other tests can modify args
        for key in list(args):
            if '10g' in key:
                del args[key]
        for key in DEFAULT_KEYS_1G:
            del args[key]
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']
        assert 'Bond1G' in my_obj.sfe.set_network_config_args
        for attr, value in DEFAULT_ATTRS.items():
            if attr == 'bond-lacp_rate':
                # not set with ActivePassive
                continue
            assert my_obj.sfe.set_network_config_args['Bond1G'][attr] == value

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_create_10g_only(self, mock_create_sf_connection):
        ''' create with 10g options only '''
        args = dict(self.ARGS)  # deep copy as other tests can modify args
        for key in list(args):
            if '1g' in key:
                del args[key]
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']
        assert 'Bond1G' not in my_obj.sfe.set_network_config_args
        for key, attr in MAPPING_10G:
            assert my_obj.sfe.set_network_config_args['Bond10G'][attr] == args[key]

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_create_10g_only_with_default(self, mock_create_sf_connection):
        ''' create with 10g options only '''
        args = dict(self.ARGS)  # deep copy as other tests can modify args
        for key in list(args):
            if '1g' in key:
                del args[key]
        for key in DEFAULT_KEYS_10G:
            del args[key]
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']
        assert 'Bond1G' not in my_obj.sfe.set_network_config_args
        for attr, value in DEFAULT_ATTRS.items():
            if attr == 'bond-lacp_rate':
                # not set with ActivePassive
                continue
            assert my_obj.sfe.set_network_config_args['Bond10G'][attr] == value

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_create_nothing(self, mock_create_sf_connection):
        ''' create without 1g or 10g options '''
        args = dict(self.ARGS)  # deep copy as other tests can modify args
        for key in list(args):
            if '1g' in key or '10g' in key:
                del args[key]
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert not exc.value.args[0]['changed']
        assert len(my_obj.sfe.set_network_config_args) == 0
