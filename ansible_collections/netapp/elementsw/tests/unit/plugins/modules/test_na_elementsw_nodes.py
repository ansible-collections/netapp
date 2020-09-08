''' unit test for Ansible module: na_elementsw_node.py '''

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import pytest

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.netapp.elementsw.tests.unit.compat import unittest
from ansible_collections.netapp.elementsw.tests.unit.compat.mock import patch
import ansible_collections.netapp.elementsw.plugins.module_utils.netapp as netapp_utils

if not netapp_utils.has_sf_sdk():
    pytestmark = pytest.mark.skip('skipping as missing required SolidFire Python SDK')

from ansible_collections.netapp.elementsw.plugins.modules.na_elementsw_node \
    import ElementSWNode as my_module  # module under test


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


MODIFY_ERROR = 'some_error_in_modify_access_group'

NODE_ID1 = 777
NODE_ID2 = 888
NODE_NAME1 = 'node_name1'
NODE_NAME2 = 'node_name2'


class MockSFConnection(object):
    ''' mock connection to ElementSW host '''

    class Bunch(object):  # pylint: disable=too-few-public-methods
        ''' create object with arbitrary attributes '''
        def __init__(self, **kw):
            ''' called with (k1=v1, k2=v2), creates obj.k1, obj.k2 with values v1, v2 '''
            setattr(self, '__dict__', kw)

    def __init__(self, force_error=False, where=None, node_id=None, cluster_name='', node_state='Pending'):
        ''' save arguments '''
        self.force_error = force_error
        self.where = where
        self.node_id = node_id
        self.cluster_name = cluster_name
        self.node_state = node_state

    def list_all_nodes(self, *args, **kwargs):  # pylint: disable=unused-argument
        ''' build access_group list: access_groups.name, access_groups.account_id '''
        nodes = list()
        pending_nodes = list()
        active_pending_nodes = list()
        if self.node_id is None:
            node_list = list()
        else:
            node_list = [self.node_id]
        attrs1 = dict(mip='10.10.10.101', name=NODE_NAME1, node_id=NODE_ID1)
        attrs2 = dict(mip='10.10.10.101', name=NODE_NAME2, node_id=NODE_ID2)
        if self.where == 'pending':
            attrs1['pending_node_id'] = NODE_ID1
            attrs2['pending_node_id'] = NODE_ID2
        node1 = self.Bunch(**attrs1)
        node2 = self.Bunch(**attrs2)
        if self.where == 'nodes':
            nodes = [node1, node2]
        elif self.where == 'pending':
            pending_nodes = [node1, node2]
        elif self.where == 'active_pending':
            active_pending_nodes = [node1, node2]
        node_list = self.Bunch(nodes=nodes, pending_nodes=pending_nodes, pending_active_nodes=active_pending_nodes)
        return node_list

    def add_nodes(self, *args, **kwargs):  # pylint: disable=unused-argument
        print('adding_node: ', repr(args), repr(kwargs))

    def remove_nodes(self, *args, **kwargs):  # pylint: disable=unused-argument
        print('adding_node: ', repr(args), repr(kwargs))

    def get_cluster_config(self, *args, **kwargs):  # pylint: disable=unused-argument
        print('get_cluster_config: ', repr(args), repr(kwargs))
        cluster = self.Bunch(cluster=self.cluster_name, state=self.node_state)
        return self.Bunch(cluster=cluster)

    def set_cluster_config(self, *args, **kwargs):  # pylint: disable=unused-argument
        print('set_cluster_config: ', repr(args), repr(kwargs))

    def list_drives(self, *args, **kwargs):  # pylint: disable=unused-argument
        print('list_drives: ', repr(args), repr(kwargs))
        drive = self.Bunch(node_id=self.node_id, status="active")
        return self.Bunch(drives=[drive])


class TestMyModule(unittest.TestCase):
    ''' a group of related Unit Tests '''

    ARGS = {
        'state': 'present',
        'node_ids': [NODE_ID1, NODE_ID2],
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
    def test_add_node_fail_not_pending(self, mock_create_sf_connection):
        ''' adding a node - fails as these nodes are unknown '''
        args = dict(self.ARGS)  # deep copy as other tests can modify args
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleFailJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        msg = 'nodes not in pending or active lists'
        assert msg in exc.value.args[0]['msg']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_add_node(self, mock_create_sf_connection):
        ''' adding a node '''
        args = dict(self.ARGS)  # deep copy as other tests can modify args
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(where='pending')
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_add_node_idempotent(self, mock_create_sf_connection):
        ''' adding a node that is already in the cluster '''
        args = dict(self.ARGS)
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(where='nodes')
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert not exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_remove_node(self, mock_create_sf_connection):
        ''' removing a node that is in the cluster '''
        args = dict(self.ARGS)
        args['state'] = 'absent'
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(where='nodes')
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_remove_node_idempotent(self, mock_create_sf_connection):
        ''' removing a node that is not in the cluster '''
        args = dict(self.ARGS)
        args['state'] = 'absent'
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert not exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_remove_node_with_active_drive(self, mock_create_sf_connection):
        ''' removing a node that is in the cluster but still associated with a drive '''
        args = dict(self.ARGS)
        args['state'] = 'absent'
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(node_id=NODE_ID1, where='nodes')
        my_obj = my_module()
        with pytest.raises(AnsibleFailJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        msg = 'Error deleting node %s: node has active drives' % NODE_NAME1
        assert msg in exc.value.args[0]['msg']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_set_cluster_name_only(self, mock_create_sf_connection):
        ''' set cluster name without adding the node '''
        args = dict(self.ARGS)
        args['preset_only'] = True
        args['cluster_name'] = 'cluster_name'
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']
        message = 'List of updated nodes with cluster_name:'
        assert message in exc.value.args[0]['msg']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_set_cluster_name_only_idempotent(self, mock_create_sf_connection):
        ''' set cluster name without adding the node - name already set '''
        args = dict(self.ARGS)
        args['preset_only'] = True
        args['cluster_name'] = 'cluster_name'
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(cluster_name=args['cluster_name'])
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert not exc.value.args[0]['changed']
        message = ''
        assert message == exc.value.args[0]['msg']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_set_cluster_name_and_add(self, mock_create_sf_connection):
        ''' set cluster name and add the node '''
        args = dict(self.ARGS)
        args['cluster_name'] = 'cluster_name'
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(where='pending')
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']
        message = 'List of updated nodes with cluster_name:'
        assert message in exc.value.args[0]['msg']
        message = 'List of added nodes: '
        assert message in exc.value.args[0]['msg']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_set_cluster_name_and_add_idempotent(self, mock_create_sf_connection):
        ''' set cluster name and add the node '''
        args = dict(self.ARGS)
        args['cluster_name'] = 'cluster_name'
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(where='nodes', cluster_name=args['cluster_name'])
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert not exc.value.args[0]['changed']
        message = ''
        assert message == exc.value.args[0]['msg']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_set_cluster_name_already_active_no_change(self, mock_create_sf_connection):
        ''' set cluster name fails because node state is 'Active' '''
        args = dict(self.ARGS)
        args['cluster_name'] = 'cluster_name'
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(where='nodes', cluster_name=args['cluster_name'], node_state='Active')
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert not exc.value.args[0]['changed']
        message = ''
        assert message == exc.value.args[0]['msg']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_set_cluster_name_already_active_change_not_allowed(self, mock_create_sf_connection):
        ''' set cluster name fails because node state is 'Active' '''
        args = dict(self.ARGS)
        args['cluster_name'] = 'new_cluster_name'
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(where='nodes', cluster_name='old_cluster_name', node_state='Active')
        my_obj = my_module()
        with pytest.raises(AnsibleFailJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        message = "Error updating cluster name for node %s, already in 'Active' state" % NODE_ID1
        assert message == exc.value.args[0]['msg']
