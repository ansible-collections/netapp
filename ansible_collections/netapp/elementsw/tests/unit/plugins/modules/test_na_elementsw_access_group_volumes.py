''' unit test for Ansible module: na_elementsw_access_group_volumes.py '''

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import pytest

from ansible_collections.netapp.elementsw.tests.unit.compat import unittest
from ansible_collections.netapp.elementsw.tests.unit.compat.mock import patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
import ansible_collections.netapp.elementsw.plugins.module_utils.netapp as netapp_utils

if not netapp_utils.has_sf_sdk():
    pytestmark = pytest.mark.skip('skipping as missing required SolidFire Python SDK')

from ansible_collections.netapp.elementsw.plugins.modules.na_elementsw_access_group_volumes \
    import ElementSWAccessGroupVolumes as my_module  # module under test


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


MODIFY_ERROR = 'some_error_in_modify_access_group'

VOLUME_ID = 777


class MockSFConnection(object):
    ''' mock connection to ElementSW host '''

    class Bunch(object):  # pylint: disable=too-few-public-methods
        ''' create object with arbitrary attributes '''
        def __init__(self, **kw):
            ''' called with (k1=v1, k2=v2), creates obj.k1, obj.k2 with values v1, v2 '''
            setattr(self, '__dict__', kw)

    def __init__(self, force_error=False, where=None, volume_id=None):
        ''' save arguments '''
        self.force_error = force_error
        self.where = where
        self.volume_id = volume_id

    def list_volume_access_groups(self, *args, **kwargs):  # pylint: disable=unused-argument
        ''' build access_group list: access_groups.name, access_groups.account_id '''
        group_name = 'element_groupname'
        if self.volume_id is None:
            volume_list = list()
        else:
            volume_list = [self.volume_id]
        access_group = self.Bunch(name=group_name, volume_access_group_id=888, volumes=volume_list)
        access_groups = [access_group]
        access_group_list = self.Bunch(volume_access_groups=access_groups)
        return access_group_list

    def list_volumes_for_account(self, *args, **kwargs):  # pylint: disable=unused-argument
        ''' build volume list: volume.name, volume.id '''
        volume = self.Bunch(name='element_volumename', volume_id=VOLUME_ID, delete_time='')
        volumes = [volume]
        volume_list = self.Bunch(volumes=volumes)
        return volume_list

    def modify_volume_access_group(self, *args, **kwargs):  # pylint: disable=unused-argument
        ''' We don't check the return code, but could force an exception '''
        if self.force_error and 'modify_exception' in self.where:
            # The module does not check for a specific exception :(
            raise OSError(MODIFY_ERROR)

    def get_account_by_name(self, *args, **kwargs):  # pylint: disable=unused-argument
        ''' returns account_id '''
        if self.force_error and 'get_account_id' in self.where:
            account_id = None
        else:
            account_id = 1
        print('account_id', account_id)
        account = self.Bunch(account_id=account_id)
        result = self.Bunch(account=account)
        return result


class TestMyModule(unittest.TestCase):
    ''' a group of related Unit Tests '''

    ARGS = {
        'state': 'present',
        'access_group': 'element_groupname',
        'volumes': 'element_volumename',
        'account_id': 'element_account_id',
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
        args = dict(self.ARGS)  # deep copy as other tests can modify args
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_add_volume_idempotent(self, mock_create_sf_connection):
        ''' adding a volume that is already in the access group '''
        args = dict(self.ARGS)
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(volume_id=VOLUME_ID)
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert not exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_remove_volume(self, mock_create_sf_connection):
        ''' removing a volume that is in the access group '''
        args = dict(self.ARGS)
        args['state'] = 'absent'
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(volume_id=VOLUME_ID)
        my_obj = my_module()
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        assert exc.value.args[0]['changed']

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_remove_volume_idempotent(self, mock_create_sf_connection):
        ''' removing a volume that is not in the access group '''
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
    def test_check_error_reporting_on_modify_exception(self, mock_create_sf_connection):
        ''' modify does not return anything but can raise an exception '''
        args = dict(self.ARGS)
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(force_error=True, where=['modify_exception'])
        my_obj = my_module()
        with pytest.raises(AnsibleFailJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        message = 'Error updating volume access group element_groupname: %s' % MODIFY_ERROR
        assert exc.value.args[0]['msg'] == message

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_check_error_reporting_on_invalid_volume_name(self, mock_create_sf_connection):
        ''' report error if volume does not exist '''
        args = dict(self.ARGS)
        args['volumes'] = ['volume1']
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleFailJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        message = 'Error: Specified volume %s does not exist' % 'volume1'
        assert exc.value.args[0]['msg'] == message

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_check_error_reporting_on_invalid_account_group_name(self, mock_create_sf_connection):
        ''' report error if access group does not exist '''
        args = dict(self.ARGS)
        args['access_group'] = 'something_else'
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection()
        my_obj = my_module()
        with pytest.raises(AnsibleFailJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        message = 'Error: Specified access group "%s" does not exist for account id: %s.' % ('something_else', 'element_account_id')
        assert exc.value.args[0]['msg'] == message

    @patch('ansible_collections.netapp.elementsw.plugins.module_utils.netapp.create_sf_connection')
    def test_check_error_reporting_on_invalid_account_id(self, mock_create_sf_connection):
        ''' report error if account id is not found '''
        args = dict(self.ARGS)
        set_module_args(args)
        # my_obj.sfe will be assigned a MockSFConnection object:
        mock_create_sf_connection.return_value = MockSFConnection(force_error=True, where='get_account_id')
        my_obj = my_module()
        with pytest.raises(AnsibleFailJson) as exc:
            my_obj.apply()
        print(exc.value.args[0])
        message = 'Error: Specified account id "%s" does not exist.' % 'element_account_id'
        assert exc.value.args[0]['msg'] == message
