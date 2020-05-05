#!/usr/bin/python
#
# (c) 2019, NetApp, Inc
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'certified'}


DOCUMENTATION = '''
---
module: azure_rm_netapp_volume

short_description: Manage NetApp Azure Files Volume
version_added: "2.9"
author: NetApp Ansible Team (@carchi8py) <ng-ansibleteam@netapp.com>

description:
    - Create and delete NetApp Azure volume.
extends_documentation_fragment:
    - netapp.azure.netapp.azure_rm_netapp

options:
    name:
        description:
            - The name of the volume.
        required: true
        type: str
    file_path:
        description:
            - A unique file path for the volume. Used when creating mount targets.
        type: str
    pool_name:
        description:
            - The name of the capacity pool.
        required: true
        type: str
    account_name:
        description:
            - The name of the NetApp account.
        required: true
        type: str
    location:
        description:
            - Resource location.
            - Required for create.
        type: str
    subnet_id:
        description:
            - The Azure Resource URI for a delegated subnet. Must have the delegation Microsoft.NetApp/volumes.
            - Provide name of the subnet ID.
            - Required for create.
        type: str
    virtual_network:
        description:
            - The name of the virtual network required for the subnet to create a volume.
            - Required for create.
        type: str
    service_level:
        description:
            - The service level of the file system.
            - default is Premium.
        type: str
        choices:
            - Premium
            - Standard
            - Ultra
    size:
        description:
            - Provisioned size of the volume (in GiB).
            - Minimum size is 100 GiB. Upper limit is 100TiB
            - default is 100GiB.
        version_added: "20.5.0"
        type: int
    state:
        description:
            - State C(present) will check that the volume exists with the requested configuration.
            - State C(absent) will delete the volume.
        default: present
        choices:
            - absent
            - present
        type: str

'''
EXAMPLES = '''

- name: Create Azure NetApp volume
  azure_rm_netapp_volume:
    resource_group: myResourceGroup
    account_name: tests-netapp
    pool_name: tests-pool
    name: tests-volume2
    location: eastus
    file_path: tests-volume2
    virtual_network: myVirtualNetwork
    subnet_id: test
    service_level: Ultra
    size: 100

- name: Delete Azure NetApp volume
  azure_rm_netapp_volume:
    state: absent
    resource_group: myResourceGroup
    account_name: tests-netapp
    pool_name: tests-pool
    name: tests-volume2

'''

RETURN = '''
mount_path:
    description: Returns mount_path of the Volume
    returned: always
    type: str

'''

try:
    from msrestazure.azure_exceptions import CloudError
    from msrestazure.tools import parse_resource_id
    from msrest.polling import LROPoller
except ImportError:
    # This is handled in azure_rm_common
    pass

from ansible.module_utils.basic import to_native, AnsibleModule
from ansible_collections.netapp.azure.plugins.module_utils.azure_rm_netapp_common import AzureRMNetAppModuleBase
from ansible_collections.netapp.azure.plugins.module_utils.netapp_module import NetAppModule
import traceback

AZURE_OBJECT_CLASS = 'NetAppAccount'
HAS_AZURE_MGMT_NETAPP = False
try:
    from azure.mgmt.netapp.models import Volume
    HAS_AZURE_MGMT_NETAPP = True
except ImportError:
    HAS_AZURE_MGMT_NETAPP = False

ONE_GIB = 1073741824


class AzureRMNetAppVolume(AzureRMNetAppModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            resource_group=dict(type='str', required=True),
            name=dict(type='str', required=True),
            file_path=dict(type='str', required=False),
            pool_name=dict(type='str', required=True),
            account_name=dict(type='str', required=True),
            location=dict(type='str', required=False),
            state=dict(choices=['present', 'absent'], default='present', type='str'),
            subnet_id=dict(type='str', required=False),
            virtual_network=dict(type='str', required=False),
            size=dict(type='int', required=False),
            service_level=dict(type='str', required=False, choices=['Premium', 'Standard', 'Ultra'])
        )
        self.module = AnsibleModule(
            argument_spec=self.module_arg_spec,
            required_if=[
                ('state', 'present', ['location', 'file_path', 'subnet_id', 'virtual_network']),
            ],
            supports_check_mode=True
        )
        self.na_helper = NetAppModule()
        self.parameters = self.na_helper.set_parameters(self.module.params)

        if HAS_AZURE_MGMT_NETAPP is False:
            self.module.fail_json(msg="the python Azure-mgmt-NetApp module is required")
        super(AzureRMNetAppVolume, self).__init__(derived_arg_spec=self.module_arg_spec, supports_check_mode=True)

    def get_azure_netapp_volume(self):
        """
            Returns volume object for an existing volume
            Return None if volume does not exist
        """
        try:
            volume_get = self.netapp_client.volumes.get(self.parameters['resource_group'], self.parameters['account_name'],
                                                        self.parameters['pool_name'], self.parameters['name'])
        except CloudError:  # volume does not exist
            return None
        return volume_get

    def create_azure_netapp_volume(self):
        """
            Create a volume for the given Azure NetApp Account
            :return: None
        """
        volume_body = Volume(
            location=self.parameters['location'],
            creation_token=self.parameters['file_path'],
            service_level=self.parameters['service_level'] if self.parameters.get('service_level') is not None else 'Premium',
            usage_threshold=(self.parameters['size'] if self.parameters.get('size') is not None else 100) * ONE_GIB,
            subnet_id='/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/virtualNetworks/%s/subnets/%s'
                      % (self.netapp_client.config.subscription_id, self.parameters['resource_group'],
                         self.parameters['virtual_network'], self.parameters['subnet_id'])
        )
        try:
            result = self.netapp_client.volumes.create_or_update(body=volume_body, resource_group_name=self.parameters['resource_group'],
                                                                 account_name=self.parameters['account_name'],
                                                                 pool_name=self.parameters['pool_name'], volume_name=self.parameters['name'])
            # waiting till the status turns Succeeded
            while result.done() is not True:
                result.result(10)
        except CloudError as error:
            self.module.fail_json(msg='Error creating volume %s for Azure NetApp account %s: %s'
                                      % (self.parameters['name'], self.parameters['account_name'], to_native(error)),
                                  exception=traceback.format_exc())

    def delete_azure_netapp_volume(self):
        """
            Delete a volume for the given Azure NetApp Account
            :return: None
        """
        try:
            result = self.netapp_client.volumes.delete(resource_group_name=self.parameters['resource_group'],
                                                       account_name=self.parameters['account_name'],
                                                       pool_name=self.parameters['pool_name'], volume_name=self.parameters['name'])
            # waiting till the status turns Succeeded
            while result.done() is not True:
                result.result(10)
        except CloudError as error:
            self.module.fail_json(msg='Error deleting volume %s for Azure NetApp account %s: %s'
                                      % (self.parameters['name'], self.parameters['account_name'], to_native(error)),
                                  exception=traceback.format_exc())

    def exec_module(self, **kwargs):
        current = self.get_azure_netapp_volume()
        cd_action = self.na_helper.get_cd_action(current, self.parameters)

        if self.na_helper.changed:
            if self.module.check_mode:
                pass
            else:
                if cd_action == 'create':
                    self.create_azure_netapp_volume()
                elif cd_action == 'delete':
                    self.delete_azure_netapp_volume()

        return_info = ''
        if self.parameters['state'] == 'present':
            return_info = self.get_azure_netapp_volume()
            return_info = return_info.creation_token if return_info is not None else ''
        self.module.exit_json(changed=self.na_helper.changed, msg=str(return_info))


def main():
    AzureRMNetAppVolume()


if __name__ == '__main__':
    main()
