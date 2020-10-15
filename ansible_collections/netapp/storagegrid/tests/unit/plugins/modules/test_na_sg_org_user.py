# (c) 2020, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests NetApp StorageGRID Org Group Ansible module: na_sg_org_user"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type
import json
import pytest

from ansible_collections.netapp.storagegrid.tests.unit.compat import unittest
from ansible_collections.netapp.storagegrid.tests.unit.compat.mock import (
    patch,
    Mock,
)
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from requests import Response
from ansible_collections.netapp.storagegrid.plugins.modules.na_sg_org_user import (
    SgOrgUser as org_user_module,
)

# REST API canned responses when mocking send_request
SRR = {
    # common responses
    "empty_good": ({"data": []}, None),
    "not_found": ({"status": "error", "code": 404, "data": {}}, {"key": "error.404"},),
    "end_of_sequence": (None, "Unexpected call to send_request"),
    "generic_error": (None, "Expected error"),
    "delete_good": ({"code": 204}, None),
    "pw_change_good": ({"code": 204}, None),
    "org_groups": (
        {
            "data": [
                {
                    "displayName": "TestOrgGroup1",
                    "uniqueName": "group/testorggroup1",
                    "accountId": "12345678901234567890",
                    "id": "12345678-abcd-1234-abcd-1234567890ab",
                    "federated": False,
                    "groupURN": "urn:sgws:identity::12345678901234567890:group/testorggroup1",
                },
                {
                    "displayName": "TestOrgGroup2",
                    "uniqueName": "group/testorggroup2",
                    "accountId": "12345678901234567890",
                    "id": "87654321-abcd-1234-cdef-1234567890ab",
                    "federated": False,
                    "groupURN": "urn:sgws:identity::12345678901234567890:group/testorggroup2",
                },
            ]
        },
        None,
    ),
    "org_users": (
        {
            "data": [
                {
                    "id": "09876543-abcd-4321-abcd-0987654321ab",
                    "accountId": "12345678901234567890",
                    "fullName": "testorguser",
                    "uniqueName": "user/ansible-sg-demo-user1",
                    "userURN": "urn:sgws:identity::12345678901234567890:user/testorguser",
                    "federated": False,
                    "memberOf": ["12345678-abcd-1234-abcd-1234567890ab"],
                    "disable": False,
                }
            ]
        },
        None,
    ),
    "org_user_record_no_group": (
        {
            "data": {
                "id": "09876543-abcd-4321-abcd-0987654321ab",
                "accountId": "12345678901234567890",
                "fullName": "testorguser",
                "uniqueName": "user/ansible-sg-demo-user1",
                "userURN": "urn:sgws:identity::12345678901234567890:user/testorguser",
                "federated": False,
                "disable": False,
            }
        },
        None,
    ),
    "org_user_record": (
        {
            "data": {
                "id": "09876543-abcd-4321-abcd-0987654321ab",
                "accountId": "12345678901234567890",
                "fullName": "testorguser",
                "uniqueName": "user/ansible-sg-demo-user1",
                "userURN": "urn:sgws:identity::12345678901234567890:user/testorguser",
                "federated": False,
                "memberOf": ["12345678-abcd-1234-abcd-1234567890ab"],
                "disable": False,
            }
        },
        None,
    ),
    "org_user_record_update": (
        {
            "data": {
                "id": "09876543-abcd-4321-abcd-0987654321ab",
                "accountId": "12345678901234567890",
                "fullName": "testorguser",
                "uniqueName": "user/ansible-sg-demo-user1",
                "userURN": "urn:sgws:identity::12345678901234567890:user/testorguser",
                "federated": False,
                "memberOf": [
                    "12345678-abcd-1234-abcd-1234567890ab",
                    "87654321-abcd-1234-cdef-1234567890ab",
                ],
                "disable": False,
            }
        },
        None,
    ),
}


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)  # pylint: disable=protected-access


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""

    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""

    pass


def exit_json(*args, **kwargs):  # pylint: disable=unused-argument
    """function to patch over exit_json; package return data into an exception"""
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):  # pylint: disable=unused-argument
    """function to patch over fail_json; package return data into an exception"""
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


class TestMyModule(unittest.TestCase):
    """ a group of related Unit Tests """

    def setUp(self):
        self.mock_module_helper = patch.multiple(
            basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json
        )
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def set_default_args_fail_check(self):
        return dict(
            {
                "full_name": "TestUser",
                "api_url": "gmi.example.com",
                "auth_token": "01234567-5678-9abc-78de-9fgabc123def",
                "validate_certs": False,
            }
        )

    def set_default_args_pass_check(self):
        return dict(
            {
                "state": "present",
                "full_name": "TestUser",
                "unique_name": "user/testuser",
                "api_url": "gmi.example.com",
                "auth_token": "01234567-5678-9abc-78de-9fgabc123def",
                "validate_certs": False,
            }
        )

    def set_args_create_na_sg_org_user_no_group(self):
        return dict(
            {
                "state": "present",
                "full_name": "TestUser",
                "unique_name": "user/testuser",
                "api_url": "gmi.example.com",
                "auth_token": "01234567-5678-9abc-78de-9fgabc123def",
                "validate_certs": False,
            }
        )

    def set_args_create_na_sg_org_user(self):
        return dict(
            {
                "state": "present",
                "full_name": "TestUser",
                "unique_name": "user/testuser",
                "member_of": ["group/testorggroup1"],
                "api_url": "gmi.example.com",
                "auth_token": "01234567-5678-9abc-78de-9fgabc123def",
                "validate_certs": False,
            }
        )

    def set_args_delete_na_sg_org_user(self):
        return dict(
            {
                "state": "absent",
                # "full_name": "TestUser",
                "unique_name": "user/testuser",
                # "member_of": ["group/testorggroup1"],
                "api_url": "gmi.example.com",
                "auth_token": "01234567-5678-9abc-78de-9fgabc123def",
                "validate_certs": False,
            }
        )

    def test_module_fail_when_required_args_missing(self):
        """ required arguments are reported as errors """
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args(self.set_default_args_fail_check())
            org_user_module()
        print(
            "Info: test_module_fail_when_required_args_missing: %s"
            % exc.value.args[0]["msg"]
        )

    def test_module_fail_when_required_args_present(self):
        """ required arguments are reported as errors """
        with pytest.raises(AnsibleExitJson) as exc:
            set_module_args(self.set_default_args_pass_check())
            org_user_module()
            exit_json(changed=True, msg="Induced arguments check")
        print(
            "Info: test_module_fail_when_required_args_present: %s"
            % exc.value.args[0]["msg"]
        )
        assert exc.value.args[0]["changed"]

    def test_module_fail_with_bad_unique_name(self):
        """ error returned if unique_name doesn't start with user or federated_user """
        with pytest.raises(AnsibleFailJson) as exc:
            args = self.set_default_args_pass_check()
            args["unique_name"] = "noprefixuser"
            set_module_args(args)
            org_user_module()
        print(
            "Info: test_module_fail_with_bad_unique_name: %s" % exc.value.args[0]["msg"]
        )

    def set_args_create_na_sg_org_user_with_password(self):
        return dict(
            {
                "state": "present",
                "full_name": "TestUser",
                "unique_name": "user/testuser",
                "member_of": ["group/testorggroup1"],
                "password": "netapp123",
                "api_url": "gmi.example.com",
                "auth_token": "01234567-5678-9abc-78de-9fgabc123def",
                "validate_certs": False,
            }
        )

    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_create_na_sg_org_user_no_group_pass(self, mock_request):
        set_module_args(self.set_args_create_na_sg_org_user_no_group())
        my_obj = org_user_module()
        mock_request.side_effect = [
            SRR["not_found"],  # get
            SRR["org_user_record_no_group"],  # post
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(
            "Info: test_create_na_sg_org_user_no_group_pass: %s"
            % repr(exc.value.args[0])
        )
        assert exc.value.args[0]["changed"]

    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_create_na_sg_org_user_pass(self, mock_request):
        set_module_args(self.set_args_create_na_sg_org_user())
        my_obj = org_user_module()
        mock_request.side_effect = [
            SRR["not_found"],  # get
            SRR["org_groups"],  # get
            SRR["org_user_record"],  # post
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print("Info: test_create_na_sg_org_user_pass: %s" % repr(exc.value.args[0]))
        assert exc.value.args[0]["changed"]

    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_idempotent_create_na_sg_org_user_pass(self, mock_request):
        set_module_args(self.set_args_create_na_sg_org_user())
        my_obj = org_user_module()
        mock_request.side_effect = [
            SRR["org_user_record"],  # get
            SRR["org_groups"],  # get
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(
            "Info: test_idempotent_create_na_sg_org_user_pass: %s"
            % repr(exc.value.args[0])
        )
        assert not exc.value.args[0]["changed"]

    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_update_na_sg_org_user_pass(self, mock_request):
        args = self.set_args_create_na_sg_org_user()
        args["member_of"] = ["group/testorggroup1", "group/testorggroup2"]

        set_module_args(args)
        my_obj = org_user_module()
        mock_request.side_effect = [
            SRR["org_user_record"],  # get
            SRR["org_groups"],  # get
            SRR["org_user_record_update"],  # put
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print("Info: test_update_na_sg_org_user_pass: %s" % repr(exc.value.args[0]))
        assert exc.value.args[0]["changed"]

    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_delete_na_sg_org_user_pass(self, mock_request):
        set_module_args(self.set_args_delete_na_sg_org_user())
        my_obj = org_user_module()
        mock_request.side_effect = [
            SRR["org_user_record"],  # get
            SRR["org_groups"],  # get
            SRR["delete_good"],  # delete
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print("Info: test_delete_na_sg_org_user_pass: %s" % repr(exc.value.args[0]))
        assert exc.value.args[0]["changed"]

    # create user and set pass
    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_create_na_sg_org_user_and_set_password_pass(self, mock_request):
        set_module_args(self.set_args_create_na_sg_org_user_with_password())
        my_obj = org_user_module()
        mock_request.side_effect = [
            SRR["not_found"],  # get
            SRR["org_groups"],  # get
            SRR["org_user_record"],  # post
            SRR["pw_change_good"],  # post
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(
            "Info: test_create_na_sg_org_user_and_set_password_pass: %s"
            % repr(exc.value.args[0])
        )
        assert exc.value.args[0]["changed"]

    # Idempotent user with password defined
    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_idempotent_create_na_sg_org_user_and_set_password_pass(self, mock_request):
        set_module_args(self.set_args_create_na_sg_org_user_with_password())
        my_obj = org_user_module()
        mock_request.side_effect = [
            SRR["org_user_record"],  # get
            SRR["org_groups"],  # get
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(
            "Info: test_idempotent_create_na_sg_org_user_and_set_password_pass: %s"
            % repr(exc.value.args[0])
        )
        assert not exc.value.args[0]["changed"]

    # update user and set pass
    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_update_na_sg_org_user_and_set_password_pass(self, mock_request):
        args = self.set_args_create_na_sg_org_user_with_password()
        args["member_of"] = ["group/testorggroup1", "group/testorggroup2"]
        args["update_password"] = "always"

        set_module_args(args)
        my_obj = org_user_module()
        mock_request.side_effect = [
            SRR["org_user_record"],  # get
            SRR["org_groups"],  # get
            SRR["org_user_record_update"],  # put
            SRR["pw_change_good"],  # post
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(
            "Info: test_update_na_sg_org_user_and_set_password_pass: %s"
            % repr(exc.value.args[0])
        )
        assert exc.value.args[0]["changed"]

    # set pass only

    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_set_na_sg_org_user_password_pass(self, mock_request):
        args = self.set_args_create_na_sg_org_user_with_password()
        args["update_password"] = "always"

        set_module_args(args)
        my_obj = org_user_module()
        mock_request.side_effect = [
            SRR["org_user_record"],  # get
            SRR["org_groups"],  # get
            SRR["pw_change_good"],  # post
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(
            "Info: test_set_na_sg_org_user_password_pass: %s" % repr(exc.value.args[0])
        )
        assert exc.value.args[0]["changed"]

    # attempt to set password on federated user

    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_fail_set_federated_user_password(self, mock_request):
        with pytest.raises(AnsibleFailJson) as exc:
            args = self.set_args_create_na_sg_org_user_with_password()
            args["unique_name"] = "federated-user/abc123"
            args["update_password"] = "always"
            set_module_args(args)
            org_user_module()
        print(
            "Info: test_fail_set_federated_user_password: %s" % repr(exc.value.args[0])
        )
