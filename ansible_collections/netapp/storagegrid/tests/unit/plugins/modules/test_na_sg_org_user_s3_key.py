# (c) 2020, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests NetApp StorageGRID Org Group Ansible module: na_sg_org_user_s3_key"""

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
from ansible_collections.netapp.storagegrid.plugins.modules.na_sg_org_user_s3_key import (
    SgOrgUserS3Key as org_s3_key_module,
)

# REST API canned responses when mocking send_request
SRR = {
    # common responses
    "empty_good": ({"data": []}, None),
    "not_found": (
        {"status": "error", "code": 404, "data": {}},
        {"key": "error.404"},
    ),
    "end_of_sequence": (None, "Unexpected call to send_request"),
    "generic_error": (None, "Expected error"),
    "delete_good": ({"code": 204}, None),
    "org_user_record": (
        {
            "data": {
                "id": "09876543-abcd-4321-abcd-0987654321ab",
                "accountId": "12345678901234567890",
                "fullName": "testorguser",
                "uniqueName": "user/testorguser",
                "userURN": "urn:sgws:identity::12345678901234567890:user/testorguser",
                "federated": False,
                "memberOf": ["12345678-abcd-1234-abcd-1234567890ab"],
                "disable": False,
            }
        },
        None,
    ),
    "org_s3_key": (
        {
            "data": {
                "id": "abcABC_01234-0123456789abcABCabc0123456789==",
                "accountId": 12345678901234567000,
                "displayName": "****************AB12",
                "userURN": "urn:sgws:identity::12345678901234567890:root",
                "userUUID": "09876543-abcd-4321-abcd-0987654321ab",
                "expires": "2020-09-04T00:00:00.000Z",
                "accessKey": "ABCDEFabcd1234567890",
                "secretAccessKey": "abcABC+123456789012345678901234567890123",
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
                "unique_user_name": "user/testorguser",
                "auth_token": "01234567-5678-9abc-78de-9fgabc123def",
                "validate_certs": False,
            }
        )

    def set_default_args_pass_check(self):
        return dict(
            {
                "state": "present",
                "unique_user_name": "user/testorguser",
                "api_url": "gmi.example.com",
                "auth_token": "01234567-5678-9abc-78de-9fgabc123def",
                "validate_certs": False,
            }
        )

    def set_args_create_na_sg_org_user_s3_keys(self):
        return dict(
            {
                "state": "present",
                "unique_user_name": "user/testorguser",
                "api_url": "gmi.example.com",
                "auth_token": "01234567-5678-9abc-78de-9fgabc123def",
                "validate_certs": False,
            }
        )

    def set_args_delete_na_sg_org_user_s3_keys(self):
        return dict(
            {
                "state": "absent",
                "unique_user_name": "user/testorguser",
                "access_key": "ABCDEFabcd1234567890",
                "api_url": "gmi.example.com",
                "auth_token": "01234567-5678-9abc-78de-9fgabc123def",
                "validate_certs": False,
            }
        )

    def test_module_fail_when_required_args_missing(self):
        """ required arguments are reported as errors """
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args(self.set_default_args_fail_check())
            org_s3_key_module()
        print(
            "Info: test_module_fail_when_required_args_missing: %s"
            % exc.value.args[0]["msg"]
        )

    def test_module_fail_when_required_args_present(self):
        """ required arguments are reported as errors """
        with pytest.raises(AnsibleExitJson) as exc:
            set_module_args(self.set_default_args_pass_check())
            org_s3_key_module()
            exit_json(changed=True, msg="Induced arguments check")
        print(
            "Info: test_module_fail_when_required_args_present: %s"
            % exc.value.args[0]["msg"]
        )
        assert exc.value.args[0]["changed"]

    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_create_na_sg_org_user_s3_key_pass(self, mock_request):
        set_module_args(self.set_args_create_na_sg_org_user_s3_keys())
        my_obj = org_s3_key_module()
        mock_request.side_effect = [
            SRR["org_user_record"],  # get
            SRR["org_s3_key"],  # post
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(
            "Info: test_create_na_sg_org_user_s3_key_pass: %s"
            % repr(exc.value.args[0])
        )
        assert exc.value.args[0]["changed"]

    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_idempotent_create_na_sg_org_user_s3_key_pass(self, mock_request):
        args = self.set_args_create_na_sg_org_user_s3_keys()
        args["access_key"] = "ABCDEFabcd1234567890"
        set_module_args(args)
        my_obj = org_s3_key_module()
        mock_request.side_effect = [
            SRR["org_user_record"],  # get
            SRR["org_s3_key"],  # get
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(
            "Info: test_idempotent_create_na_sg_org_user_s3_key_pass: %s"
            % repr(exc.value.args[0])
        )
        assert not exc.value.args[0]["changed"]

    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_delete_na_sg_org_user_s3_keys_pass(self, mock_request):
        set_module_args(self.set_args_delete_na_sg_org_user_s3_keys())
        my_obj = org_s3_key_module()
        mock_request.side_effect = [
            SRR["org_s3_key"],  # get
            SRR["delete_good"],  # delete
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(
            "Info: test_delete_na_sg_org_user_s3_keys_pass: %s"
            % repr(exc.value.args[0])
        )
        assert exc.value.args[0]["changed"]
