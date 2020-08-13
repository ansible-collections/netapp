''' unit test for Ansible module: na_elementsw_volume.py '''

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

from ansible_collections.netapp.elementsw.plugins.modules.na_elementsw_volume \
    import ElementSWVolume as my_module  # module under test


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


CREATE_ERROR = 'create', 'some_error_in_create_volume'
MODIFY_ERROR = 'modify', 'some_error_in_modify_volume'
DELETE_ERROR = 'delete', 'some_error_in_delete_volume'

POLICY_ID = 888
POLICY_NAME = 'element_qos_policy_name'
VOLUME_ID = 777
VOLUME_NAME = 'element_volume_name'


class MockSFConnection(object):
    ''' mock connection to ElementSW host '''

    class Bunch(object):  # pylint: disable=too-few-public-methods
        ''' create object with arbitrary attributes '''
        def __init__(self, **kw):
            ''' called with (k1=v1, k2=v2), creates obj.k1, obj.k2 with values v1, v2 '''
            setattr(self, '__dict__', kw)

    def __init__(self, force_error=False, where=None, with_qos_policy_id=True):
        ''' save arguments '''
        self.force_error = force_error
        self.where = where
        self.with_qos_policy_id = with_qos_policy_id

    def list_qos_policies(self, *args, **kwargs):  # pylint: disable=unused-argument
        ''' build qos_policy list '''
        qos_policy_name = POLICY_NAME
        qos = self.Bunch(min_iops=1000, max_iops=20000, burst_iops=20000)
        qos_policy = self.Bunch(name=qos_policy_name, qos_policy_id=POLICY_ID, qos=qos)
        qos_policy_1 = self.Bunch(name=qos_policy_name + '_1', qos_policy_id=POLICY_ID + 1, qos=qos)
        qos_policies = [qos_policy, qos_policy_1]
        qos_policy_list = self.Bunch(qos_policies=qos_policies)
        return qos_policy_list

    def list_volumes_for_account(self, *args, **kwargs):  # pylint: disable=unused-argument
        ''' build volume list: volume.name, volume.id '''
        volume = self.Bunch(name=VOLUME_NAME, volume_id=VOLUME_ID, delete_time='')
        volumes = [volume]
        volume_list = self.Bunch(volumes=volumes)
        return volume_list

    def list_volumes(self, *args, **kwargs):  # pylint: disable=unused-argument
        ''' build volume details: volume.name, volume.id '''
        if self.with_qos_policy_id:
            qos_policy_id = POLICY_ID
        else:
            qos_policy_id = None
        qos = self.Bunch(min_iops=1000, max_iops=20000, burst_iops=20000)
        volume = self.Bunch(name=VOLUME_NAME, volume_id=VOLUME_ID, delete_time='', access='rw',
                            account_id=1, qos=qos, qos_policy_id=qos_policy_id, total_size=1000000000,
                            attributes={'config-mgmt': 'ansible', 'event-source': 'na_elementsw_volume'}
                            )
        volumes = [volume]
        volume_list = self.Bunch(volumes=volumes)
        return volume_list

    def get_account_by_name(self, *args, **kwargs):  # pylint: disable=unused-argument
        ''' returns account_id '''
        if self.force_error and 'get_account_id' in self.where:
            account_id = None
        else:
            account_id = 1
        account = self.Bunch(account_id=account_id)
        result = self.Bunch(account=account)
        return result

    def create_volume(self, *args, **kwargs):  # pylint: disable=unused-argument
        ''' We don't check the return code, but could force an exception '''
        if self.force_error and 'create_exception' in self.where:
            raise netapp_utils.solidfire.common.ApiServerError(*CREATE_ERROR)

    def modify_volume(self, *args, **kwargs):  # pylint: disable=unused-argument
        ''' We don't check the return code, but could force an exception '''
        print("modify: %s, %s " % (repr(args), repr(kwargs)))
        if self.force_error and 'modify_exception' in self.where:
            raise netapp_utils.solidfire.common.ApiServerError(*MODIFY_ERROR)

    def delete_volume(self, *args, **kwargs):  # pylint: disable=unused-argument
        ''' We don't check the return code, but could force an exception '''
        if self.force_error and 'delete_exception' in self.where:
            raise netapp_utils.solidfire.common.ApiServerError(*DELETE_ERROR)

    def purge_deleted_volume(self, *args, **kwargs):  # pylint: disable=unused-argument
        ''' We don't check the return code, but could force an exception '''
        if self.force_error and 'delete_exception' in self.where:
            raise netapp_utils.solidfire.common.ApiServerError(*DELETE_ERROR)


class TestMyModule(unittest.TestCase):
    ''' a group of related Unit Tests '''

    ARGS = {
        'state': 'present',
        'name': VOLUME_NAME,
        'account_id': 'element_account_id',
        'qos': {'minIOPS': 1000, 'maxIOPS': 20000, 'burstIOPS': 20000},
        'qos_policy_name': POLICY_NAME,
        'size': 1,
        'enable512e': True,
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
    def test_add_volume(self, mock_create_sf_connection):
        ''' adding a volume '''
        args = dict(self.ARGS)      # deep copy as other tests can modify args
        args['name'] += '_1'        # new name to force a create
        args.pop('qos')             # parameters are mutually exclusive: qos|qos_policy_name
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_add_or_modify_volume_idempotent_qos_policy(self, mock_create_sf_connection):
        ''' adding a volume '''
        args = dict(self.ARGS)
        args.pop('qos')         # parameters are mutually exclusive: qos|qos_policy_name
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert not exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_add_or_modify_volume_idempotent_qos(self, mock_create_sf_connection):
        ''' adding a volume '''
        args = dict(self.ARGS)
        args.pop('qos_policy_name')         # parameters are mutually exclusive: qos|qos_policy_name
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(with_qos_policy_id=False)
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert not exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_delete_volume(self, mock_create_sf_connection):
        ''' removing a volume '''
        args = dict(self.ARGS)
        args['state'] = 'absent'
        args.pop('qos')         # parameters are mutually exclusive: qos|qos_policy_name
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_delete_volume_idempotent(self, mock_create_sf_connection):
        ''' removing a volume '''
        args = dict(self.ARGS)
        args['state'] = 'absent'
        args['name'] += '_1'  # new name to force idempotency
        args.pop('qos')         # parameters are mutually exclusive: qos|qos_policy_name
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert not exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_modify_volume_qos(self, mock_create_sf_connection):
        ''' modifying a volume  '''
        args = dict(self.ARGS)
        args['qos'] = {'minIOPS': 2000}
        args.pop('qos_policy_name')         # parameters are mutually exclusive: qos|qos_policy_name
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(with_qos_policy_id=False)
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_modify_volume_qos_policy_to_qos(self, mock_create_sf_connection):
        ''' modifying a volume  '''
        args = dict(self.ARGS)
        args['qos'] = {'minIOPS': 2000}
        args.pop('qos_policy_name')         # parameters are mutually exclusive: qos|qos_policy_name
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_modify_volume_qos_policy(self, mock_create_sf_connection):
        ''' modifying a volume  '''
        args = dict(self.ARGS)
        args['qos_policy_name'] += '_1'
        args.pop('qos')         # parameters are mutually exclusive: qos|qos_policy_name
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_modify_volume_qos_to_qos_policy(self, mock_create_sf_connection):
        ''' modifying a volume  '''
        args = dict(self.ARGS)
        args.pop('qos')         # parameters are mutually exclusive: qos|qos_policy_name
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(with_qos_policy_id=False)
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_create_volume_exception(self, mock_create_sf_connection):
        ''' creating a volume can raise an exception '''
        args = dict(self.ARGS)
        args['name'] += '_1'  # new name to force a create
        args.pop('qos')         # parameters are mutually exclusive: qos|qos_policy_name
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(force_error=True, where=['create_exception'])
        my_obj = my_module()
        with pytest.raises(AnsibleFailJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        message = 'Error provisioning volume: %s' % args['name']
        assert exc.value.args[0]['msg'].startswith(message)

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_modify_volume_exception(self, mock_create_sf_connection):
        ''' modifying a volume can raise an exception '''
        args = dict(self.ARGS)
        args['qos'] = {'minIOPS': 2000}
        args.pop('qos_policy_name')         # parameters are mutually exclusive: qos|qos_policy_name
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(force_error=True, where=['modify_exception'])
        my_obj = my_module()
        with pytest.raises(AnsibleFailJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        message = 'Error updating volume: %s' % VOLUME_ID
        assert exc.value.args[0]['msg'].startswith(message)

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_delete_volume_exception(self, mock_create_sf_connection):
        ''' deleting a volume can raise an exception '''
        args = dict(self.ARGS)
        args['state'] = 'absent'
        args.pop('qos')         # parameters are mutually exclusive: qos|qos_policy_name
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(force_error=True, where=['delete_exception'])
        my_obj = my_module()
        with pytest.raises(AnsibleFailJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        message = 'Error deleting volume: %s' % VOLUME_ID
        assert exc.value.args[0]['msg'].startswith(message)

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_check_error_reporting_on_non_existent_qos_policy(self, mock_create_sf_connection):
        ''' report error if qos option is not given on create '''
        args = dict(self.ARGS)
        args['name'] += '_1'  # new name to force a create
        args.pop('qos')
        args['qos_policy_name'] += '_2'
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleFailJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        message = "Cannot find qos policy with name/id: %s" % args['qos_policy_name']
        assert exc.value.args[0]['msg'] == message
