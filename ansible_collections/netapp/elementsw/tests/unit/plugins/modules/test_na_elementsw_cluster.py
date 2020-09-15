''' unit test for Ansible module: na_elementsw_cluster.py '''

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

from ansible_collections.netapp.elementsw.plugins.modules.na_elementsw_cluster \
    import ElementSWCluster as my_module  # module under test


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

    def __init__(self, force_error=False, where=None, nodes=None):
        ''' save arguments '''
        self.force_error = force_error
        self.where = where
        self.nodes = nodes
        self._port = 442
        self.called = list()

    def record(self, args, kwargs):
        name = inspect.stack()[1][3]    # caller function name
        print('%s: , args: %s, kwargs: %s' % (name, args, kwargs))
        self.called.append(name)

    def create_cluster(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.record(repr(args), repr(kwargs))

    def send_request(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.record(repr(args), repr(kwargs))

    def get_config(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.record(repr(args), repr(kwargs))
        if self.force_error and self.where == 'get_config_exception':
            raise ConnectionError
        if self.nodes is not None:
            nodes = ['%d:%s' % (i, node) for i, node in enumerate(self.nodes)]
        else:
            nodes = list()
        cluster = self.Bunch(ensemble=nodes, cluster='cl_name')
        config = self.Bunch(cluster=cluster)
        return self.Bunch(config=config)


class TestMyModule(unittest.TestCase):
    ''' a group of related Unit Tests '''

    ARGS = {
        # 'state': 'present',
        'management_virtual_ip': '10.10.10.10',
        'storage_virtual_ip': '10.10.10.11',
        'nodes': [NODE_ID1, NODE_ID2],
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
    def test_create(self, mock_create_sf_connection):
        ''' create cluster basic '''
        args = dict(self.ARGS)  # deep copy as other tests can modify args
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(force_error=True, where='get_config_exception')
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']
        msg = 'created'
        assert msg in exc.value.args[0]['msg']
        assert 'create_cluster' in my_obj.sfe_node.called
        assert 'send_request' not in my_obj.sfe_node.called

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_create_extra_parms(self, mock_create_sf_connection):
        ''' force a direct call to send_request '''
        args = dict(self.ARGS)  # deep copy as other tests can modify args
        args['order_number'] = '12345'
        args['serial_number'] = '54321'
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(force_error=True, where='get_config_exception')
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']
        assert 'send_request' in my_obj.sfe_node.called
        assert 'create_cluster' not in my_obj.sfe_node.called

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_create_idempotent(self, mock_create_sf_connection):
        ''' cluster already exists with same nodes '''
        args = dict(self.ARGS)
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(nodes=[NODE_ID1, NODE_ID2])
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert not exc.value.args[0]['changed']
        assert 'send_request' not in my_obj.sfe_node.called
        assert 'create_cluster' not in my_obj.sfe_node.called

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_create_idempotent_extra_nodes(self, mock_create_sf_connection):
        ''' cluster already exists with more nodes '''
        args = dict(self.ARGS)
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(nodes=[NODE_ID1, NODE_ID2, NODE_ID3])
        my_obj = my_module()
        with pytest.raises(AnsibleFailJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        msg = 'Error: found existing cluster with more nodes in ensemble.'
        assert msg in exc.value.args[0]['msg']
        assert 'send_request' not in my_obj.sfe_node.called
        assert 'create_cluster' not in my_obj.sfe_node.called

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_create_idempotent_extra_nodes_ok(self, mock_create_sf_connection):
        ''' cluster already exists with more nodes but we're OK with a superset '''
        args = dict(self.ARGS)
        args['fail_if_cluster_already_exists_with_larger_ensemble'] = False
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(nodes=[NODE_ID1, NODE_ID2, NODE_ID3])
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert not exc.value.args[0]['changed']
        msg = 'cluster already exists'
        assert msg in exc.value.args[0]['msg']
        assert 'send_request' not in my_obj.sfe_node.called
        assert 'create_cluster' not in my_obj.sfe_node.called

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_create_idempotent_missing_nodes(self, mock_create_sf_connection):
        ''' cluster already exists with fewer nodes.
            Since not every node is lister in the ensemble, we can't tell if it's an error or not '''
        args = dict(self.ARGS)
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(nodes=[NODE_ID1])
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert not exc.value.args[0]['changed']
        msg = 'cluster already exists'
        assert msg in exc.value.args[0]['msg']
        assert 'send_request' not in my_obj.sfe_node.called
        assert 'create_cluster' not in my_obj.sfe_node.called
