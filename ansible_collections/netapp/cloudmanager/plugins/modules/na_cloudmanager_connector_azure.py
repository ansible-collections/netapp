#!/usr/bin/python

# (c) 2021, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

'''
na_cloudmanager_connector_azure
'''

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''

module: na_cloudmanager_connector_azure
short_description: NetApp Cloud Manager connector for Azure.
extends_documentation_fragment:
    - netapp.cloudmanager.netapp.cloudmanager
version_added: '21.4.0'
author: NetApp Ansible Team (@carchi8py) <ng-ansibleteam@netapp.com>

description:
- Create or delete Cloud Manager connector for Azure.

options:

  state:
    description:
    - Whether the specified Cloud Manager connector for Azure should exist or not.
    choices: ['present', 'absent']
    default: 'present'
    type: str

  name:
    required: true
    description:
    - The name of the Cloud Manager connector for Azure to manage.
    type: str

  virtual_machine_size:
    description:
    - The virtual machine type. (for example, Standard_D2s_v3).
    - At least 4 CPU and 16 GB of memory are required.
    type: str
    default: Standard_D2s_v3

  resource_group:
    required: true
    description:
    - The resource group in Azure where the resources will be created.
    type: str

  subnet_id:
    required: true
    description:
    - The name of the subnet for the virtual machine.
    type: str

  location:
    required: true
    description:
    - The location where the Cloud Manager Connector will be created.
    type: str

  client_id:
    description:
    - The unique client ID of the Connector.
    type: str

  subscription_id:
    required: true
    description:
    - The ID of the Azure subscription.
    type: str

  company:
    required: true
    description:
    - The name of the company of the user.
    type: str

  vnet_id:
    required: true
    description:
    - The name of the virtual network.
    type: str

  vnet_resource_group:
    description:
    - The resource group in Azure associated with the virtual network.
    - If not provided, its assumed that the VNet is within the previously specified resource group.
    type: str

  network_security_resource_group:
    description:
    - The resource group in Azure associated with the security group.
    - If not provided, its assumed that the security group is within the previously specified resource group.
    type: str

  network_security_group_name:
    required: true
    description:
    - The name of the security group for the deployment.
    type: str

  proxy_certificates:
    description:
    - The proxy certificates, a list of certificate file names.
    type: list
    elements: str

  associate_public_ip_address:
    description:
    - Indicates whether to associate the public IP address to the virtual machine.
    type: bool
    default: true

  account_id:
    description:
    - The NetApp tenancy account ID.
    type: str

  proxy_url:
    description:
    - The proxy URL, if using a proxy to connect to the internet.
    type: str

  proxy_user_name:
    description:
    - The proxy user name, if using a proxy to connect to the internet.
    type: str

  proxy_password:
    description:
    - The proxy password, if using a proxy to connect to the internet.
    type: str

  admin_username:
    required: true
    description:
    - The user name for the Connector.
    type: str

  admin_password:
    required: true
    description:
    - The password for the Connector.
    type: str

'''

EXAMPLES = """
- name: Create NetApp Cloud Manager connector for Azure.
  netapp.cloudmanager.na_cloudmanager_connector_azure:
    state: present
    refresh_token: "{{ xxxxxxxxxxxxxxx }}"
    name: bsuhas_ansible_occm
    location: westus
    resource_group: occm_group_westus
    subnet_id: subnetxxxxx
    vnet_id: Vnetxxxxx
    subscription_id: "{{ xxxxxxxxxxxxxxxxx }}"
    security_group_ids: [sg-xxxxxxxxxxx]
    iam_instance_profile_name: OCCM_AUTOMATION
    account_id: "{{ account-xxxxxxx }}"
    company: NetApp
    admin_password: Netapp123456
    admin_username: bsuhas
    network_security_group_name: OCCM_SG
    proxy_url: abc.com
    proxy_user_name: xyz
    proxy_password: abcxyz
    proxy_certificates: [abc.crt.txt, xyz.crt.txt]

- name: Delete NetApp Cloud Manager connector for Azure.
  netapp.cloudmanager.na_cloudmanager_connector_azure:
    state: absent
    name: ansible
    location: westus
    resource_group: occm_group_westus
    network_security_group_name: OCCM_SG
    subnet_id: subnetxxxxx
    company: NetApp
    admin_password: Netapp123456
    admin_username: bsuhas
    vnet_id: Vnetxxxxx
    subscription_id: "{{ xxxxxxxxxxxxxxxxx }}"
    client_id: xxxxxxxxxxxxxxxxxxx
"""

RETURN = """
msg:
  description: Newly created Azure connector id in cloud manager.
  type: str
  returned: success
  sample: 'xxxxxxxxxxxxxxxx'
"""

import traceback
import time
import base64
import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
import ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp as netapp_utils
from ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp_module import NetAppModule
from ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp import CloudManagerRestAPI

IMPORT_EXCEPTION = None

try:
    from azure.mgmt.resource import ResourceManagementClient
    from azure.mgmt.compute import ComputeManagementClient
    from azure.mgmt.network import NetworkManagementClient
    from azure.mgmt.storage import StorageManagementClient
    from azure.common.client_factory import get_client_from_cli_profile
    from msrestazure.azure_exceptions import CloudError
    HAS_AZURE_LIB = True
except ImportError as exc:
    HAS_AZURE_LIB = False
    IMPORT_EXCEPTION = exc

CLOUD_MANAGER_HOST = "cloudmanager.cloud.netapp.com"


class NetAppCloudManagerConnectorAzure(object):
    ''' object initialize and class methods '''

    def __init__(self):
        self.use_rest = False
        self.argument_spec = netapp_utils.cloudmanager_host_argument_spec()
        self.argument_spec.update(dict(
            name=dict(required=True, type='str'),
            state=dict(required=False, choices=['present', 'absent'], default='present'),
            virtual_machine_size=dict(required=False, type='str', default='Standard_D2s_v3'),
            resource_group=dict(required=True, type='str'),
            subscription_id=dict(required=True, type='str'),
            subnet_id=dict(required=True, type='str'),
            vnet_id=dict(required=True, type='str'),
            vnet_resource_group=dict(required=False, type='str'),
            location=dict(required=True, type='str'),
            network_security_resource_group=dict(required=False, type='str'),
            network_security_group_name=dict(required=True, type='str'),
            client_id=dict(required=False, type='str'),
            company=dict(required=True, type='str'),
            proxy_certificates=dict(required=False, type='list', elements='str'),
            associate_public_ip_address=dict(required=False, type='bool', default=True),
            account_id=dict(required=False, type='str'),
            proxy_url=dict(required=False, type='str', default=''),
            proxy_user_name=dict(required=False, type='str', default=''),
            proxy_password=dict(required=False, type='str', default='', no_log=True),
            admin_username=dict(required=True, type='str'),
            admin_password=dict(required=True, type='str', no_log=True),
        ))

        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            required_if=[
                ['state', 'absent', ['client_id']]
            ],
            supports_check_mode=True
        )

        if HAS_AZURE_LIB is False:
            self.module.fail_json(msg="the python AZURE library azure.mgmt and azure.common is required. Command is pip install azure-mgmt, azure-common."
                                      " Import error: %s" % str(IMPORT_EXCEPTION))

        self.na_helper = NetAppModule()
        self.parameters = self.na_helper.set_parameters(self.module.params)

        self.rest_api = CloudManagerRestAPI(self.module)

    def get_deploy_azure_vm(self):
        """
        Get Cloud Manager connector for AZURE
        :return:
            Dictionary of current details if Cloud Manager connector for AZURE
            None if Cloud Manager connector for AZURE is not found
        """

        exists = False

        resource_client = get_client_from_cli_profile(ResourceManagementClient)

        try:
            exists = resource_client.deployments.check_existence(self.parameters['resource_group'], self.parameters['name'])

        except CloudError as error:
            self.module.fail_json(msg=to_native(error), exception=traceback.format_exc())

        if not exists:
            return None

        return exists

    def deploy_azure(self):
        """
        Create Cloud Manager connector for Azure
        :return: client_id
        """

        user_data, client_id = self.register_agent_to_service()

        template = json.loads(self.na_helper.call_template())
        params = json.loads(self.na_helper.call_parameters())

        params['adminUsername']['value'] = self.parameters['admin_username']
        params['adminPassword']['value'] = self.parameters['admin_password']
        params['customData']['value'] = json.dumps(user_data)
        params['location']['value'] = self.parameters['location']
        params['virtualMachineName']['value'] = self.parameters['name']
        if self.parameters.get('vnet_resource_group') is not None:
            network = '/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/virtualNetworks/%s' % (
                self.parameters['subscription_id'], self.parameters['vnet_resource_group'], self.parameters['vnet_id'])
        else:
            network = '/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/virtualNetworks/%s' % (
                self.parameters['subscription_id'], self.parameters['resource_group'], self.parameters['vnet_id'])

        subnet = '%s/subnets/%s' % (network, self.parameters['subnet_id'])

        if self.parameters.get('network_security_resource_group') is not None:
            network_seecurity_group_name = '/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/networkSecurityGroups/%s' % (
                self.parameters['subscription_id'], self.parameters['network_security_resource_group'], self.parameters['network_security_group_name'])
        else:
            network_seecurity_group_name = '/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/networkSecurityGroups/%s' % (
                self.parameters['subscription_id'], self.parameters['resource_group'], self.parameters['network_security_group_name'])

        params['virtualNetworkId']['value'] = network
        params['networkSecurityGroupName']['value'] = network_seecurity_group_name
        params['virtualMachineSize']['value'] = self.parameters['virtual_machine_size']
        params['subnetId']['value'] = subnet

        try:
            resource_client = get_client_from_cli_profile(ResourceManagementClient)

            resource_client.resource_groups.create_or_update(
                self.parameters['resource_group'],
                {"location": self.parameters['location']})

            resource_client.deployments.create_or_update(
                self.parameters['resource_group'],
                self.parameters['name'],
                {
                    'mode': 'Incremental',
                    'template': template,
                    'parameters': params
                })

        except CloudError as error:
            self.module.fail_json(msg="Error in deploy_azure: %s" % to_native(error), exception=traceback.format_exc())

        # Sleep for 2 minutes
        time.sleep(120)
        retries = 30
        while retries > 0:
            occm_resp, error = self.na_helper.check_occm_status(CLOUD_MANAGER_HOST, self.rest_api,
                                                                self.parameters['client_id'])
            if error is not None:
                self.module.fail_json(
                    msg="Error: Not able to get occm status: %s, %s" % (str(error), str(occm_resp)))
            if occm_resp['agent']['status'] == "active":
                break
            else:
                time.sleep(30)
            retries = retries - 1
        if retries == 0:
            # Taking too long for status to be active
            return self.module.fail_json(msg="Taking too long for OCCM agent to be active or not properly setup")
        return client_id

    def register_agent_to_service(self):
        """
        Register agent to service and collect userdata by setting up connector
        :return: UserData, ClientID
        """

        if self.parameters.get('vnet_resource_group') is not None:
            network = '/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/virtualNetworks/%s' % (
                self.parameters['subscription_id'], self.parameters['vnet_resource_group'], self.parameters['vnet_id'])
        else:
            network = '/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/virtualNetworks/%s' % (
                self.parameters['subscription_id'], self.parameters['resource_group'], self.parameters['vnet_id'])

        subnet = '%s/subnets/%s' % (network, self.parameters['subnet_id'])

        if self.parameters.get('account_id') is None:
            response, error = self.na_helper.get_account(CLOUD_MANAGER_HOST, self.rest_api)
            if error is not None:
                self.module.fail_json(
                    msg="Error: unexpected response on getting account: %s, %s" % (str(error), str(response)))
            self.parameters['account_id'] = response

        headers = {
            "X-User-Token": self.rest_api.token_type + " " + self.rest_api.token,
        }
        body = {
            "accountId": self.parameters['account_id'],
            "name": self.parameters['name'],
            "company": self.parameters['company'],
            "placement": {
                "provider": "AZURE",
                "region": self.parameters['location'],
                "network": network,
                "subnet": subnet,
            },
            "extra": {
                "proxy": {
                    "proxyUrl": self.parameters.get('proxy_url'),
                    "proxyUserName": self.parameters.get('proxy_user_name'),
                    "proxyPassword": self.parameters.get('proxy_password')
                }
            }
        }

        register_url = "%s/agents-mgmt/connector-setup" % CLOUD_MANAGER_HOST
        response, error, dummy = self.rest_api.post(register_url, body, header=headers)
        if error is not None:
            self.module.fail_json(msg="Error: unexpected response on getting userdata for connector setup: %s, %s" % (str(error), str(response)))
        client_id = response['clientId']

        proxy_certificates = []
        if self.parameters.get('proxy_certificates') is not None:
            for each in self.parameters['proxy_certificates']:
                try:
                    data = open(each, "r").read()
                except OSError:
                    self.module.fail_json(msg="Error: Could not open/read file of proxy_certificates: %s" % str(each))

                encoded_certificate = base64.b64encode(data)
                proxy_certificates.append(encoded_certificate)

        if len(proxy_certificates) > 0:
            response['proxySettings']['proxyCertificates'] = proxy_certificates

        return response, client_id

    def delete_azure_occm(self):
        """
        Delete OCCM
        :return:
            None
        """
        # delete vm deploy
        try:
            compute_client = get_client_from_cli_profile(ComputeManagementClient)
            vm_delete = compute_client.virtual_machines.delete(
                self.parameters['resource_group'],
                self.parameters['name'])
            while not vm_delete.done():
                vm_delete.wait(2)
        except CloudError as error:
            self.module.fail_json(msg=to_native(error), exception=traceback.format_exc())

        # delete interfaces deploy
        try:
            network_client = get_client_from_cli_profile(NetworkManagementClient)
            interface_delete = network_client.network_interfaces.begin_delete(
                self.parameters['resource_group'],
                self.parameters['name'] + '-nic')
            while not interface_delete.done():
                interface_delete.wait(2)
        except CloudError as error:
            self.module.fail_json(msg=to_native(error), exception=traceback.format_exc())

        # delete storage account deploy
        try:
            storage_client = get_client_from_cli_profile(StorageManagementClient)
            storage_client.storage_accounts.delete(
                self.parameters['resource_group'],
                self.parameters['name'] + 'sa')
        except CloudError as error:
            self.module.fail_json(msg=to_native(error), exception=traceback.format_exc())

        # delete storage account deploy
        try:
            network_client = get_client_from_cli_profile(NetworkManagementClient)
            public_ip_addresses_delete = network_client.public_ip_addresses.begin_delete(
                self.parameters['resource_group'],
                self.parameters['name'] + '-ip')
            while not public_ip_addresses_delete.done():
                public_ip_addresses_delete.wait(2)
        except CloudError as error:
            self.module.fail_json(msg=to_native(error), exception=traceback.format_exc())

        # delete deployment
        try:
            resource_client = get_client_from_cli_profile(ResourceManagementClient)
            deployments_delete = resource_client.deployments.delete(
                self.parameters['resource_group'],
                self.parameters['name'] + '-ip')
            while not deployments_delete.done():
                deployments_delete.wait(5)
        except CloudError as error:
            self.module.fail_json(msg=to_native(error), exception=traceback.format_exc())

        retries = 16
        while retries > 0:
            occm_resp, error = self.na_helper.check_occm_status(CLOUD_MANAGER_HOST, self.rest_api,
                                                                self.parameters['client_id'])
            if error is not None:
                self.module.fail_json(
                    msg="Error: Not able to get occm status: %s, %s" % (str(error), str(occm_resp)))
            if occm_resp['agent']['status'] != "active":
                break
            else:
                time.sleep(10)
            retries = retries - 1
        if retries == 0:
            # Taking too long for terminating OCCM
            return self.module.fail_json(msg="Taking too long for instance to finish terminating")

        delete_occum_url = "%s/agents-mgmt/agent/%sclients" % (CLOUD_MANAGER_HOST, self.parameters['client_id'])
        headers = {
            "X-User-Token": self.rest_api.token_type + " " + self.rest_api.token,
            "X-Tenancy-Account-Id": self.parameters['account_id']
        }

        response, error, dummy = self.rest_api.delete(delete_occum_url, None, header=headers)
        if error is not None:
            self.module.fail_json(msg="Error: unexpected response on deleting OCCM: %s, %s" % (str(error), str(response)))

    def apply(self):
        """
        Apply action to the Cloud Manager connector for AZURE
        :return: None
        """
        client_id = None
        if self.module.check_mode:
            pass
        else:
            if self.parameters['state'] == 'present':
                client_id = self.deploy_azure()
                self.na_helper.changed = True
            elif self.parameters['state'] == 'absent':
                get_deploy = self.get_deploy_azure_vm()
                if get_deploy:
                    self.delete_azure_occm()
                    self.na_helper.changed = True

        self.module.exit_json(changed=self.na_helper.changed, msg={'client_id': client_id})


def main():
    """
    Create Cloud Manager connector for AZURE class instance and invoke apply
    :return: None
    """
    obj_store = NetAppCloudManagerConnectorAzure()
    obj_store.apply()


if __name__ == '__main__':
    main()
