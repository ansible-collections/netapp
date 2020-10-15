# (c) 2020, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

""" unit tests NetApp StorageGRID Org Group Ansible module: na_sg_org_group"""

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
from ansible_collections.netapp.storagegrid.plugins.modules.na_sg_org_group import (
    SgOrgGroup as org_group_module,
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
    "org_groups": (
        {
            "data": [
                {
                    "displayName": "TestOrgGroup",
                    "uniqueName": "group/testorggroup",
                    "policies": {
                        "management": {
                            "manageAllContainers": True,
                            "manageEndpoints": True,
                            "manageOwnS3Credentials": True,
                        },
                        "s3": {
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": "s3:*",
                                    "Resource": "arn:aws:s3:::*",
                                }
                            ]
                        },
                    },
                    "accountId": "12345678901234567890",
                    "id": "00000000-0000-0000-0000-000000000000",
                    "federated": False,
                    "groupURN": "urn:sgws:identity::12345678901234567890:group/testorggroup",
                }
            ]
        },
        None,
    ),
    "org_group_record": (
        {
            "data": {
                "displayName": "TestOrgGroup",
                "uniqueName": "group/testorggroup",
                "policies": {
                    "management": {
                        "manageAllContainers": True,
                        "manageEndpoints": True,
                        "manageOwnS3Credentials": True,
                    },
                    "s3": {
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": "s3:*",
                                "Resource": "arn:aws:s3:::*",
                            }
                        ]
                    },
                },
                "accountId": "12345678901234567890",
                "id": "00000000-0000-0000-0000-000000000000",
                "federated": False,
                "groupURN": "urn:sgws:identity::12345678901234567890:group/testorggroup",
            }
        },
        None,
    ),
    "org_group_record_update": (
        {
            "data": {
                "displayName": "TestOrgGroup",
                "uniqueName": "group/testorggroup",
                "policies": {
                    "management": {
                        "manageAllContainers": True,
                        "manageEndpoints": True,
                        "manageOwnS3Credentials": True,
                        # "rootAccess": False,
                    },
                    "s3": {
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": "s3:*",
                                "Resource": "arn:aws:s3:::mybucket/*",
                            }
                        ]
                    },
                },
                "accountId": "12345678901234567890",
                "id": "00000000-0000-0000-0000-000000000000",
                "federated": False,
                "groupURN": "urn:sgws:identity::12345678901234567890:group/testorggroup",
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
                "display_name": "TestGroup",
                "management_policy": {
                    "manage_all_containers": True,
                    "manage_endpoints": True,
                    "manage_own_s3_credentials": True,
                    "root_access": False,
                },
                "s3_policy": {
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": "s3:*",
                            "Resource": "arn:aws:s3:::*",
                        }
                    ]
                },
                "auth_token": "01234567-5678-9abc-78de-9fgabc123def",
                "validate_certs": False,
            }
        )

    def set_default_args_pass_check(self):
        return dict(
            {
                "state": "present",
                "display_name": "TestGroup",
                "unique_name": "group/testgroup",
                "management_policy": {
                    "manage_all_containers": True,
                    "manage_endpoints": True,
                    "manage_own_s3_credentials": True,
                    "root_access": False,
                },
                "s3_policy": {
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": "s3:*",
                            "Resource": "arn:aws:s3:::*",
                        }
                    ]
                },
                "api_url": "gmi.example.com",
                "auth_token": "01234567-5678-9abc-78de-9fgabc123def",
                "validate_certs": False,
            }
        )

    def set_args_create_na_sg_org_group(self):
        return dict(
            {
                "state": "present",
                "display_name": "TestOrgGroup",
                "unique_name": "group/testorggroup",
                "management_policy": {
                    "manage_all_containers": True,
                    "manage_endpoints": True,
                    "manage_own_s3_credentials": True,
                    "root_access": False,
                },
                "s3_policy": {
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": "s3:*",
                            "Resource": "arn:aws:s3:::*",
                        }
                    ]
                },
                "api_url": "gmi.example.com",
                "auth_token": "01234567-5678-9abc-78de-9fgabc123def",
                "validate_certs": False,
            }
        )

    def set_args_delete_na_sg_org_group(self):
        return dict(
            {
                "state": "absent",
                # "display_name": "TestOrgGroup",
                "unique_name": "group/testorggroup",
                # "management_policy": {
                #     "manage_all_containers": True,
                #     "manage_endpoints": True,
                #     "manage_own_s3_credentials": True,
                #     "root_access": False,
                # },
                # "s3_policy": {
                #     "Statement": [
                #         {
                #             "Effect": "Allow",
                #             "Action": "s3:*",
                #             "Resource": "arn:aws:s3:::*",
                #         }
                #     ]
                # },
                "api_url": "gmi.example.com",
                "auth_token": "01234567-5678-9abc-78de-9fgabc123def",
                "validate_certs": False,
            }
        )

    def test_module_fail_when_required_args_missing(self):
        """ required arguments are reported as errors """
        with pytest.raises(AnsibleFailJson) as exc:
            set_module_args(self.set_default_args_fail_check())
            org_group_module()
        print(
            "Info: test_module_fail_when_required_args_missing: %s"
            % exc.value.args[0]["msg"]
        )

    def test_module_fail_when_required_args_present(self):
        """ required arguments are reported as errors """
        with pytest.raises(AnsibleExitJson) as exc:
            set_module_args(self.set_default_args_pass_check())
            org_group_module()
            exit_json(changed=True, msg="Induced arguments check")
        print(
            "Info: test_module_fail_when_required_args_present: %s"
            % exc.value.args[0]["msg"]
        )
        assert exc.value.args[0]["changed"]

    def test_module_fail_with_bad_unique_name(self):
        """ error returned if unique_name doesn't start with group or federated_group """
        with pytest.raises(AnsibleFailJson) as exc:
            args = self.set_default_args_pass_check()
            args["unique_name"] = "noprefixgroup"
            set_module_args(args)
            org_group_module()
        print(
            "Info: test_module_fail_with_bad_unique_name: %s"
            % exc.value.args[0]["msg"]
        )

    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_create_na_sg_org_group_pass(self, mock_request):
        set_module_args(self.set_args_create_na_sg_org_group())
        my_obj = org_group_module()
        mock_request.side_effect = [
            SRR["not_found"],  # get
            SRR["org_group_record"],  # post
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(
            "Info: test_create_na_sg_org_group_pass: %s"
            % repr(exc.value.args[0])
        )
        assert exc.value.args[0]["changed"]

    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_idempotent_create_na_sg_org_group_pass(self, mock_request):
        set_module_args(self.set_args_create_na_sg_org_group())
        my_obj = org_group_module()
        mock_request.side_effect = [
            SRR["org_group_record"],  # get
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(
            "Info: test_idempotent_create_na_sg_org_group_pass: %s"
            % repr(exc.value.args[0])
        )
        assert not exc.value.args[0]["changed"]

    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_update_na_sg_org_group_pass(self, mock_request):
        args = self.set_args_create_na_sg_org_group()
        args["s3_policy"] = (
            {
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "s3:*",
                        "Resource": "arn:aws:s3:::mybucket/*",
                    }
                ]
            },
        )

        args["management_policy"]["manage_endpoints"] = False

        set_module_args(args)
        my_obj = org_group_module()
        mock_request.side_effect = [
            SRR["org_group_record"],  # get
            SRR["org_group_record_update"],  # put
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(
            "Info: test_update_na_sg_org_group_pass: %s"
            % repr(exc.value.args[0])
        )
        assert exc.value.args[0]["changed"]

    @patch(
        "ansible_collections.netapp.storagegrid.plugins.module_utils.netapp.SGRestAPI.send_request"
    )
    def test_delete_na_sg_org_group_pass(self, mock_request):
        set_module_args(self.set_args_delete_na_sg_org_group())
        my_obj = org_group_module()
        mock_request.side_effect = [
            SRR["org_group_record"],  # get
            SRR["delete_good"],  # delete
            SRR["end_of_sequence"],
        ]
        with pytest.raises(AnsibleExitJson) as exc:
            my_obj.apply()
        print(
            "Info: test_delete_na_sg_org_group_pass: %s"
            % repr(exc.value.args[0])
        )
        assert exc.value.args[0]["changed"]
