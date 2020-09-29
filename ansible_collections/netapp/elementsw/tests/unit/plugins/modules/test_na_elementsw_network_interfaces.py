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

MAPPING = dict(
    bond_mode='bond-mode',
    bond_lacp_rate='bond-lacp_rate',
    dns_nameservers='dns-nameservers',
    dns_search='dns-search',
    virtual_network_tag='virtualNetworkTag',
)


def mapkey(key):
    if key in MAPPING:
        return MAPPING[key]
    return key


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
        # self._port = 442
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

    DEPRECATED_ARGS = {
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

    ARGS = {
        'bond_1g': {
            'address': '10.10.10.10',
            'netmask': '255.255.255.0',
            'gateway': '10.10.10.1',
            'mtu': '1500',
            'bond_mode': 'ActivePassive',
            'dns_nameservers': ['dns_nameservers'],
            'dns_search': ['dns_search_domains'],
            'virtual_network_tag': 'virtual_network_tag',
        },
        'bond_10g': {
            'bond_mode': 'LACP',
            'bond_lacp_rate': 'Fast',
        },
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

    def test_deprecated_nothing(self):
        ''' deprecated without 1g or 10g options '''
        args = dict(self.DEPRECATED_ARGS)  # deep copy as other tests can modify args
        for key in list(args):
            if '1g' in key or '10g' in key:
                del args[key]
        set_module_args(args)
        with pytest.raises(AnsibleFailJson) as exc:
            my_module()
        msg = 'Please use the new bond_1g or bond_10g options to configure the bond interfaces.'
        assert msg in exc.value.args[0]['msg']
        msg = 'This module cannot set or change "method"'
        assert msg in exc.value.args[0]['msg']

    def test_deprecated_all(self):
        ''' deprecated with all options '''
        args = dict(self.DEPRECATED_ARGS)  # deep copy as other tests can modify args
        set_module_args(args)
        with pytest.raises(AnsibleFailJson) as exc:
            my_module()
        msg = 'Please use the new bond_1g and bond_10g options to configure the bond interfaces.'
        assert msg in exc.value.args[0]['msg']
        msg = 'This module cannot set or change "method"'
        assert msg in exc.value.args[0]['msg']

    def test_deprecated_1g_only(self):
        ''' deprecated with 1g options only '''
        args = dict(self.DEPRECATED_ARGS)  # deep copy as other tests can modify args
        for key in list(args):
            if '10g' in key:
                del args[key]
        set_module_args(args)
        with pytest.raises(AnsibleFailJson) as exc:
            my_module()
        msg = 'Please use the new bond_1g option to configure the bond 1G interface.'
        assert msg in exc.value.args[0]['msg']
        msg = 'This module cannot set or change "method"'
        assert msg in exc.value.args[0]['msg']

    def test_deprecated_10g_only(self):
        ''' deprecated with 10g options only '''
        args = dict(self.DEPRECATED_ARGS)  # deep copy as other tests can modify args
        for key in list(args):
            if '1g' in key:
                del args[key]
        set_module_args(args)
        with pytest.raises(AnsibleFailJson) as exc:
            my_module()
        msg = 'Please use the new bond_10g option to configure the bond 10G interface.'
        assert msg in exc.value.args[0]['msg']
        msg = 'This module cannot set or change "method"'
        assert msg in exc.value.args[0]['msg']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_modify_nothing(self, mock_create_sf_connection):
        ''' modify without 1g or 10g options '''
        args = dict(self.ARGS)  # deep copy as other tests can modify args
        for key in list(args):
            if '1g' in key or '10g' in key:
                del args[key]
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        print('LN:', my_obj.module.params)
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert not exc.value.args[0]['changed']
        assert len(my_obj.sfe.set_network_config_args) == 0

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_modify_all(self, mock_create_sf_connection):
        ''' modify with all options '''
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
    def test_modify_1g_only(self, mock_create_sf_connection):
        ''' modify with 1g options only '''
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
        assert 'Bond10G' not in my_obj.sfe.set_network_config_args
        print(my_obj.sfe.set_network_config_args['Bond1G'])
        for key in args['bond_1g']:
            if key != 'bond_lacp_rate':
                assert my_obj.sfe.set_network_config_args['Bond1G'][mapkey(key)] == args['bond_1g'][key]

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_modify_10g_only(self, mock_create_sf_connection):
        ''' modify with 10g options only '''
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
        assert 'Bond10G' in my_obj.sfe.set_network_config_args
        assert my_obj.sfe.set_network_config_args['Bond10G']['bond-lacp_rate'] == args['bond_10g']['bond_lacp_rate']
        for key in args['bond_10g']:
            assert my_obj.sfe.set_network_config_args['Bond10G'][mapkey(key)] == args['bond_10g'][key]
