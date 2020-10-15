#!/usr/bin/python

# (c) 2020, NetApp Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""NetApp StorageGRID - Manage Buckets"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}


DOCUMENTATION = """
module: na_sg_org_container
short_description: Manage buckets on StorageGRID.
extends_documentation_fragment:
    - netapp.storagegrid.netapp.sg
version_added: '20.6.0'
author: NetApp Ansible Team (@edmonds) <ng-ansibleteam@netapp.com>
description:
- Create S3 buckets on NetApp StorageGRID.
options:
  state:
    description:
    - Whether the specified bucket should exist or not.
    type: str
    choices: ['present']
    default: present
  name:
    description:
    - Name of the bucket.
    required: true
    type: str
  region:
    description:
    - Required for specifing a bucket region
    type: str
  compliance:
    description:
    - Required if specifing bucket compliance
    type: dict
    suboptions:
      auto_delete:
        description:
        - If enabled, objects will be deleted automatically when its retention period expires, unless the bucket is under a legal hold
        default: false
        type: bool
      legal_hold:
        description:
        - If enabled, objects in this bucket cannot be deleted, even if their retention period has expired.
        default: false
        type: bool
      retention_period_minutes:
        description:
        - specify the length of the retention period for objects added to this bucket, in minutes.
        type: int
"""

EXAMPLES = """
  - name: create a s3 bucket
    netapp.storagegrid.na_sg_org_container:
      api_url: "https://<storagegrid-endpoint-url>"
      auth_token: "storagegrid-auth-token"
      validate_certs: false
      state: present
      name: ansiblebucket1
"""

RETURN = """
"""

import json

import ansible_collections.netapp.storagegrid.plugins.module_utils.netapp as netapp_utils
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.netapp.storagegrid.plugins.module_utils.netapp_module import (
    NetAppModule,
)
from ansible_collections.netapp.storagegrid.plugins.module_utils.netapp import SGRestAPI


class SgOrgContainer(object):
    """
    Create, modify and delete StorageGRID Tenant Account
    """

    def __init__(self):
        """
        Parse arguments, setup state variables,
        check parameters and ensure request module is installed
        """
        self.argument_spec = netapp_utils.na_storagegrid_host_argument_spec()
        self.argument_spec.update(
            dict(
                state=dict(required=False, type="str", choices=["present"], default="present"),
                name=dict(required=True, type="str"),
                region=dict(required=False, type="str"),
                compliance=dict(
                    required=False,
                    type="dict",
                    options=dict(
                        auto_delete=dict(required=False, type="bool"),
                        legal_hold=dict(required=False, type="bool"),
                        retention_period_minutes=dict(required=False, type="int"),
                    ),
                ),
            )
        )
        parameter_map = {
            "auto_delete": "autoDelete",
            "legal_hold": "legalHold",
            "retention_period_minutes": "retentionPeriodMinutes",
        }
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            # required_if=[("state", "present", ["state", "name", "protocol"])],
            supports_check_mode=True,
        )

        self.na_helper = NetAppModule()

        # set up state variables
        self.parameters = self.na_helper.set_parameters(self.module.params)
        # Calling generic SG rest_api class
        self.rest_api = SGRestAPI(self.module)
        # Checking for the parameters passed and create new parameters list
        self.data = {}
        self.data["name"] = self.parameters["name"]
        self.data["region"] = self.parameters.get("region")
        if self.parameters.get("compliance"):
            # self.data["compliance"] = {
            #     parameter_map[k]: v
            #     for (k, v) in self.parameters["compliance"].items()
            #     if v
            # }
            self.data["compliance"] = dict(
                (parameter_map[k], v)
                for (k, v) in self.parameters["compliance"].items()
                if v
            )

    def get_org_container(self):
        # Check if bucket/container exists
        # Return info if found, or None

        params = {"include": "compliance,region"}
        response, error = self.rest_api.get("api/v3/org/containers", params=params)

        if error:
            self.module.fail_json(msg=error)

        for container in response["data"]:
            if container["name"] == self.parameters["name"]:
                return container

        return None

    def create_org_container(self):
        api = "api/v3/org/containers"

        response, error = self.rest_api.post(api, self.data)

        if error:
            self.module.fail_json(msg=error)

        return response["data"]

    def update_org_container_compliance(self):
        api = "api/v3/org/containers/%s/compliance" % self.parameters["name"]

        response, error = self.rest_api.put(api, self.data["compliance"])
        if error:
            self.module.fail_json(msg=error)

        return response["data"]

    def apply(self):
        """
        Perform pre-checks, call functions and exit
        """
        org_container = self.get_org_container()

        cd_action = self.na_helper.get_cd_action(org_container, self.parameters)

        if cd_action is None and self.parameters["state"] == "present":
            # let's see if we need to update parameters
            update_compliance = False

            if (
                self.parameters.get("compliance")
                and org_container.get("compliance") != self.data["compliance"]
            ):
                update_compliance = True
                self.na_helper.changed = True

        # ### DEBUG self.module.fail_json(msg=tenant_account, action=cd_action)
        result_message = ""
        resp_data = org_container
        if self.na_helper.changed:
            if self.module.check_mode:
                pass
            else:
                if cd_action == "create":
                    resp_data = self.create_org_container()
                    result_message = "Org Container created"

                elif update_compliance:
                    resp_data = self.update_org_container_compliance()
                    result_message = "Org Container updated"

        self.module.exit_json(
            changed=self.na_helper.changed, msg=result_message, resp=resp_data
        )


def main():
    """
    Main function
    """
    na_sg_org_container = SgOrgContainer()
    na_sg_org_container.apply()


if __name__ == "__main__":
    main()
