#!/usr/bin/python

# (c) 2021, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

'''
na_cloudmanager_cvo_azure
'''

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''

module: na_cloudmanager_cvo_azure
short_description: NetApp Cloud Manager CVO/working environment in single or HA mode for Azure.
extends_documentation_fragment:
    - netapp.cloudmanager.netapp.cloudmanager
version_added: '21.4.0'
author: NetApp Ansible Team (@carchi8py) <ng-ansibleteam@netapp.com>

description:
- Create or delete Cloud Manager CVO/working environment in single or HA mode for Azure.

options:

  state:
    description:
    - Whether the specified Cloud Manager CVO for AZURE should exist or not.
    choices: ['present', 'absent']
    default: 'present'
    type: str

  name:
    required: true
    description:
    - The name of the Cloud Manager CVO for AZURE to manage.
    type: str

  subscription_id:
    required: true
    description:
    - The ID of the Azure subscription.
    type: str

  instance_type:
    description:
    - The type of instance to use, which depends on the license type you chose.
    - Explore ['Standard_DS3_v2']
    - Standard ['Standard_DS4_v2, Standard_DS13_v2,Standard_L8s_v2']
    - Premium ['Standard_DS5_v2', 'Standard_DS14_v2']
    - For more supported instance types, refer to Cloud Volumes ONTAP Release Notes.
    type: str
    default: Standard_DS4_v2

  license_type:
    description:
    - The type of license to use.
    - For single node ['azure-cot-explore-paygo', 'azure-cot-standard-paygo', 'azure-cot-premium-paygo', 'azure-cot-premium-byol']
    - For HA ['azure-ha-cot-standard-paygo', 'azure-ha-cot-premium-paygo', 'azure-ha-cot-premium-byol']
    choices: ['azure-cot-standard-paygo', 'azure-cot-premium-paygo', 'azure-cot-premium-byol', 'azure-cot-explore-paygo',
    'azure-ha-cot-standard-paygo', 'azure-ha-cot-premium-paygo', 'azure-ha-cot-premium-byol']
    default: 'azure-cot-standard-paygo'
    type: str

  workspace_id:
    description:
    - The ID of the Cloud Manager workspace where you want to deploy Cloud Volumes ONTAP.
    - If not provided, Cloud Manager uses the first workspace.
    - You can find the ID from the Workspace tab on [https://cloudmanager.netapp.com].
    type: str

  subnet_id:
    required: true
    description:
    - The name of the subnet for the Cloud Volumes ONTAP system.
    type: str

  vnet_id:
    required: true
    description:
    - The name of the virtual network.
    type: str

  vnet_resource_group:
    description:
    - The resource group in Azure associated to the virtual network.
    type: str

  resource_group:
    description:
    - The resource_group where Cloud Volumes ONTAP will be created.
    - If not provided, Cloud Manager generates the resource group name (name of the working environment/CVO with suffix '-rg').
    - If the resource group does not exist, it is created.
    type: str

  allow_deploy_in_existing_rg:
    description:
    - Indicates if to allow creation in existing resource group
    type: bool
    default: false

  cidr:
    required: true
    description:
    - The CIDR of the VNET.
    type: str

  location:
    required: true
    description:
    - The location where the working environment will be created.
    type: str

  data_encryption_type:
    description:
    - The type of encryption to use for the working environment.
    choices: ['AZURE', 'NONE']
    default: 'AZURE'
    type: str

  storage_type:
    description:
    - The type of storage for the first data aggregate.
    choices: ['Premium_LRS', 'Standard_LRS', 'StandardSSD_LRS']
    default: 'Premium_LRS'
    type: str

  client_id:
    required: true
    description:
    - The client ID of the Cloud Manager Connector.
    - You can find the ID from the Connector tab on [https://cloudmanager.netapp.com].
    type: str

  disk_size:
    description:
    - Azure volume size for the first data aggregate.
    - For GB, the value can be [100, 500].
    - For TB, the value can be [1,2,4,8,16].
    default: 1
    type: int

  disk_size_unit:
    description:
    - The unit for disk size.
    choices: ['GB', 'TB']
    default: 'TB'
    type: str

  security_group_id:
    description:
    - The ID of the security group for the working environment. If not provided, Cloud Manager creates the security group.
    type: str

  svm_password:
    required: true
    description:
    - The admin password for Cloud Volumes ONTAP.
    type: str

  ontap_version:
    description:
    - The required ONTAP version. Ignored if 'use_latest_version' is set to true
    type: str
    default: 'latest'

  use_latest_version:
    description:
    - Indicates whether to use the latest available ONTAP version.
    type: bool
    default: true

  serial_number:
    description:
    - The serial number for the cluster
    - Required when using one of these, 'azure-cot-premium-byol' or 'azure-ha-cot-premium-byol'
    type: str

  tier_level:
    description:
    - If capacity_tier is Blob, this argument indicates the tiering level.
    choices: ['normal', 'cool']
    default: 'normal'
    type: str

  nss_account:
    description:
    - The NetApp Support Site account ID to use with this Cloud Volumes ONTAP system.
    - If the license type is BYOL and an NSS account isn't provided, Cloud Manager tries to use the first existing NSS account.
    type: str

  writing_speed_state:
    description:
    - The write speed setting for Cloud Volumes ONTAP ['NORMAL','HIGH'].
    - This argument is not relevant for HA pairs.
    type: str

  capacity_tier:
    description:
    - Whether to enable data tiering for the first data aggregate
    choices: ['Blob', 'NONE']
    default: 'Blob'
    type: str

  cloud_provider_account:
    description:
    - The cloud provider credentials id to use when deploying the Cloud Volumes ONTAP system.
    - You can find the ID in Cloud Manager from the Settings > Credentials page.
    - If not specified, Cloud Manager uses the instance profile of the Connector.
    type: str

  backup_volumes_to_cbs:
    description:
    - Automatically enable back up of all volumes to S3.
    default: false
    type: bool

  enable_compliance:
    description:
    - Enable the Cloud Compliance service on the working environment.
    default: false
    type: bool

  enable_monitoring:
    description:
    - Enable the Monitoring service on the working environment.
    default: false
    type: bool

  azure_tag:
    description:
    - Additional tags for the AZURE CVO working environment.
    type: list
    elements: dict
    suboptions:
      tag_key:
        description: The key of the tag.
        type: str
      tag_value:
        description: The tag value.
        type: str

  is_ha:
    description:
    - Indicate whether the working environment is an HA pair or not.
    type: bool
    default: false

  platform_serial_number_node1:
    description:
    - For HA BYOL, the serial number for the first node.
    type: str

  platform_serial_number_node2:
    description:
    - For HA BYOL, the serial number for the second node.
    type: str

  refresh_token:
    required: true
    description:
    - The refresh token for NetApp Cloud Manager API operations.
    type: str

'''

EXAMPLES = """
- name: create NetApp Cloud Manager CVO for Azure single
  netapp.cloudmanager.na_cloudmanager_cvo_azure:
    state: present
    refresh_token: "{{ xxxxxxxxxxxxxxx }}"
    name: TerraformCVO
    location: westus
    subnet_id: subnet-xxxxxxx
    vnet_id: vnetxxxxxxxx
    svm_password: P@assword!
    client_id: "{{ xxxxxxxxxxxxxxx }}"
    writing_speed_state: NORMAL
    azure_tag: [
        {tag_key: abc,
        tag_value: a123}]

- name: create NetApp Cloud Manager CVO for Azure HA
  netapp.cloudmanager.na_cloudmanager_cvo_azure:
    state: present
    refresh_token: "{{ xxxxxxxxxxxxxxx }}"
    name: TerraformCVO
    location: westus
    subnet_id: subnet-xxxxxxx
    vnet_id: vnetxxxxxxxx
    svm_password: P@assword!
    client_id: "{{ xxxxxxxxxxxxxxx }}"
    writing_speed_state: NORMAL
    azure_tag: [
        {tag_key: abc,
        tag_value: a123}]
    is_ha: true

- name: delete NetApp Cloud Manager cvo for Azure
  netapp.cloudmanager.na_cloudmanager_cvo_azure:
    state: absent
    name: ansible
    location: westus
    subnet_id: subnet-xxxxxxx
    vnet_id: vnetxxxxxxxx
    svm_password: P@assword!
    client_id: "{{ xxxxxxxxxxxxxxx }}"
"""

RETURN = '''
working_environment_id:
  description: Newly created AZURE CVO working_environment_id.
  type: str
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
import ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp as netapp_utils
from ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp_module import NetAppModule
from ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp import CloudManagerRestAPI

IMPORT_EXCEPTION = None

Cloud_Manager_Host = "cloudmanager.cloud.netapp.com"
AZURE_License_Types = ['azure-cot-standard-paygo', 'azure-cot-premium-paygo', 'azure-cot-premium-byol', 'azure-cot-explore-paygo',
                       'azure-ha-cot-standard-paygo', 'azure-ha-cot-premium-paygo', 'azure-ha-cot-premium-byol']


class NetAppCloudManagerCVOAZURE:
    ''' object initialize and class methods '''

    def __init__(self):
        self.use_rest = False
        self.argument_spec = netapp_utils.cloudmanager_host_argument_spec()
        self.argument_spec.update(dict(
            name=dict(required=True, type='str'),
            state=dict(required=False, choices=['present', 'absent'], default='present'),
            instance_type=dict(required=False, type='str', default='Standard_DS4_v2'),
            license_type=dict(required=False, type='str', choices=AZURE_License_Types, default='azure-cot-standard-paygo'),
            workspace_id=dict(required=False, type='str'),
            subnet_id=dict(required=True, type='str'),
            vnet_id=dict(required=True, type='str'),
            vnet_resource_group=dict(required=False, type='str'),
            resource_group=dict(required=False, type='str'),
            cidr=dict(required=True, type='str'),
            location=dict(required=True, type='str'),
            subscription_id=dict(required=True, type='str'),
            data_encryption_type=dict(required=False, type='str', choices=['AZURE', 'NONE'], default='AZURE'),
            storage_type=dict(required=False, type='str', choices=['Premium_LRS', 'Standard_LRS', 'StandardSSD_LRS'], default='Premium_LRS'),
            disk_size=dict(required=False, type='int', default=1),
            disk_size_unit=dict(required=False, type='str', choices=['GB', 'TB'], default='TB'),
            svm_password=dict(required=True, type='str', no_log=True),
            ontap_version=dict(required=False, type='str', default='latest'),
            use_latest_version=dict(required=False, type='bool', default=True),
            tier_level=dict(required=False, type='str', choices=['normal', 'cool'], default='normal'),
            nss_account=dict(required=False, type='str'),
            writing_speed_state=dict(required=False, type='str'),
            capacity_tier=dict(required=False, type='str', choices=['Blob', 'NONE'], default='Blob'),
            security_group_id=dict(required=False, type='str'),
            cloud_provider_account=dict(required=False, type='str'),
            backup_volumes_to_cbs=dict(required=False, type='bool', default=False),
            enable_compliance=dict(required=False, type='bool', default=False),
            enable_monitoring=dict(required=False, type='bool', default=False),
            allow_deploy_in_existing_rg=dict(required=False, type='bool', default=False),
            client_id=dict(required=True, type='str'),
            azure_tag=dict(required=False, type='list', elements='dict', options=dict(
                tag_key=dict(type='str', no_log=False),
                tag_value=dict(type='str')
            )),
            serial_number=dict(required=False, type='str'),
            is_ha=dict(required=False, type='bool', default=False),
            platform_serial_number_node1=dict(required=False, type='str'),
            platform_serial_number_node2=dict(required=False, type='str'),
        ))

        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True
        )

        self.na_helper = NetAppModule()
        self.parameters = self.na_helper.set_parameters(self.module.params)

        self.rest_api = CloudManagerRestAPI(self.module)
        self.headers = {
            'X-Agent-Id': self.parameters['client_id'] + "clients"
        }

    def get_working_environment(self):
        """
        Get working environment details including:
        name: working environment name
        """

        api_url = '%s/occm/api/working-environments' % Cloud_Manager_Host
        response, error, dummy = self.rest_api.get(api_url, header=self.headers)
        if error is not None:
            self.module.fail_json(
                msg="Error: unexpected response on getting azure cvo: %s, %s" % (str(error), str(response)))

        for each in response['azureVsaWorkingEnvironments']:
            if each['name'] == self.parameters['name']:
                return each

        return None

    def get_tenant(self):
        """
        Get workspace ID (tenant)
        """

        api_url = '%s/occm/api/tenants' % Cloud_Manager_Host
        response, error, dummy = self.rest_api.get(api_url, header=self.headers)
        if error is not None:
            self.module.fail_json(
                msg="Error: unexpected response on getting tenant for azure cvo: %s, %s" % (str(error), str(response)))

        return response[0]['publicId']

    def get_nss(self):
        """
        Get nss account
        """

        api_url = '%s/occm/api/accounts' % Cloud_Manager_Host
        response, error, dummy = self.rest_api.get(api_url, header=self.headers)
        if error is not None:
            self.module.fail_json(
                msg="Error: unexpected response on getting nss for azure cvo: %s, %s" % (str(error), str(response)))

        if len(response['nssAccounts']) == 0:
            self.module.fail_json(msg="could not find any NSS account")

        return response['nssAccounts'][0]['publicId']

    def create_cvo_azure(self):
        """
        Create AZURE CVO
        """

        if self.parameters.get('workspace_id') is None:
            self.parameters['workspace_id'] = self.get_tenant()

        if self.parameters.get('nss_account') is None:
            if self.parameters.get('serial_number') is not None:
                if not self.parameters['serial_number'].startswith('Eval-') and self.parameters['license_type'] == 'azure-cot-premium-byol':
                    self.parameters['nss_account'] = self.get_nss()
            elif self.parameters.get('platform_serial_number_node1') is not None and self.parameters.get('platform_serial_number_node2') is not None:
                if not self.parameters['platform_serial_number_node1'].startswith('Eval-')\
                        and not self.parameters['platform_serial_number_node2'].startswith('Eval-')\
                        and self.parameters['license_type'] == 'azure-ha-cot-premium-byol':
                    self.parameters['nss_account'] = self.get_nss()

        json = {"name": self.parameters['name'],
                "region": self.parameters['location'],
                "subscriptionId": self.parameters['subscription_id'],
                "tenantId": self.parameters['workspace_id'],
                "storageType": self.parameters['storage_type'],
                "dataEncryptionType": self.parameters['data_encryption_type'],
                "optimizedNetworkUtilization": True,
                "diskSize": {
                    "size": self.parameters['disk_size'],
                    "unit": self.parameters['disk_size_unit']},
                "svmPassword": self.parameters['svm_password'],
                "backupVolumesToCbs": self.parameters['backup_volumes_to_cbs'],
                "enableCompliance": self.parameters['enable_compliance'],
                "enableMonitoring": self.parameters['enable_monitoring'],
                "vsaMetadata": {
                    "ontapVersion": self.parameters['ontap_version'],
                    "useLatestVersion": self.parameters['use_latest_version'],
                    "licenseType": self.parameters['license_type'],
                    "instanceType": self.parameters['instance_type']}
                }

        if self.parameters['capacity_tier'] == "Blob":
            json.update({"capacityTier": self.parameters['capacity_tier'],
                         "tierLevel": self.parameters['tier_level']})

        if self.parameters.get('cidr') is not None:
            json.update({"cidr": self.parameters['cidr']})

        if self.parameters.get('writing_speed_state') is not None:
            json.update({"writingSpeedState": self.parameters['writing_speed_state']})

        if self.parameters.get('resource_group') is not None:
            json.update({"resourceGroup": self.parameters['resource_group'],
                         "allowDeployInExistingRg": self.parameters['allow_deploy_in_existing_rg']})
        else:
            json.update({"resourceGroup": (self.parameters['name'] + '-rg')})

        if self.parameters.get('serial_number') is not None:
            json.update({"serialNumber": self.parameters['serial_number']})

        if self.parameters.get('security_group_id') is not None:
            json.update({"securityGroupId": self.parameters['security_group_id']})

        if self.parameters.get('cloud_provider_account') is not None:
            json.update({"cloudProviderAccount": self.parameters['cloud_provider_account']})

        if self.parameters.get('backup_volumes_to_cbs') is not None:
            json.update({"backupVolumesToCbs": self.parameters['backup_volumes_to_cbs']})

        if self.parameters.get('nss_account') is not None:
            json.update({"nssAccount": self.parameters['nss_account']})

        if self.parameters.get('azure_tag') is not None:
            tags = []
            for each_tag in self.parameters['azure_tag']:
                tag = {
                    'tagKey': each_tag['tag_key'],
                    'tagValue': each_tag['tag_value']
                }

                tags.append(tag)
            json.update({"azureTags": tags})

        if self.parameters['is_ha']:
            ha_params = dict()

            if self.parameters.get('platform_serial_number_node1'):
                ha_params["platformSerialNumberNode1"] = self.parameters['platform_serial_number_node1']

            if self.parameters.get('platform_serial_number_node2'):
                ha_params["platformSerialNumberNode2"] = self.parameters['platform_serial_number_node2']

            json["haParams"] = ha_params

        if self.parameters.get('vnet_resource_group') is not None:
            json.update({"vnetId": ('/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/virtualNetworks/%s' % (
                self.parameters['subscription_id'], self.parameters['vnet_resource_group'], self.parameters['vnet_id']))})
            json.update({"subnetId": ('/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/virtualNetworks/%s/subnets/%s' % (
                self.parameters['subscription_id'], self.parameters['vnet_resource_group'], self.parameters['vnet_id'], self.parameters['subnet_id']))})
        else:
            json.update({"vnetId": ('/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/virtualNetworks/%s' % (
                self.parameters['subscription_id'], self.parameters['resource_group'], self.parameters['vnet_id']))})
            json.update({"subnetId": ('/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/virtualNetworks/%s/subnets/%s' % (
                self.parameters['subscription_id'], self.parameters['resource_group'], self.parameters['vnet_id'], self.parameters['subnet_id']))})

        base_url = '/occm/api/azure/%s/working-environments' % ('ha' if self.parameters['is_ha'] else 'vsa')

        api_url = '%s%s' % (Cloud_Manager_Host, base_url)
        response, error, on_cloud_request_id = self.rest_api.post(api_url, json, header=self.headers)
        if error is not None:
            self.module.fail_json(
                msg="Error: unexpected response on creating cvo azure: %s, %s" % (str(error), str(response)))
        working_environment_id = response['publicId']
        wait_on_completion_api_url = '%s/occm/api/audit/activeTask/%s' % (Cloud_Manager_Host, str(on_cloud_request_id))
        err = self.rest_api.wait_on_completion(wait_on_completion_api_url, "CVO", "create", 60, 60)

        if err is not None:
            self.module.fail_json(msg="Error: unexpected response wait_on_completion for creating CVO AZURE: %s" % str(err))

        return working_environment_id

    def delete_cvo_azure(self, we_id):
        """
        Delete AZURE CVO
        """
        base_url = '/occm/api/azure/%s/working-environments' % ('ha' if self.parameters['is_ha'] else 'vsa')

        api_url = '%s%s/%s' % (Cloud_Manager_Host, base_url, we_id)
        response, error, on_cloud_request_id = self.rest_api.delete(api_url, None, header=self.headers)
        if error is not None:
            self.module.fail_json(msg="Error: unexpected response on deleting cvo azure: %s, %s" % (str(error), str(response)))

        wait_on_completion_api_url = '%s/occm/api/audit/activeTask/%s' % (Cloud_Manager_Host, str(on_cloud_request_id))
        err = self.rest_api.wait_on_completion(wait_on_completion_api_url, "CVO", "delete", 40, 60)

        if err is not None:
            self.module.fail_json(msg="Error: unexpected response wait_on_completion for deleting CVO AZURE: %s" % str(err))

    def validate_cvo_params(self):
        if self.parameters['use_latest_version'] is True and self.parameters['ontap_version'] != "latest":
            self.module.fail_json(msg="ontap_version parameter not required when having use_latest_version as true")

        if self.parameters.get('serial_number') is None and self.parameters['license_type'] == "azure-cot-premium-byol":
            self.module.fail_json(msg="serial_number parameter required when having license_type as azure-cot-premium-byol")

        if self.parameters['is_ha'] and self.parameters['license_type'] == "azure-ha-cot-premium-byol":
            if self.parameters.get('platform_serial_number_node1') is None or self.parameters.get('platform_serial_number_node2') is None:
                self.module.fail_json(msg="both platform_serial_number_node1 and platform_serial_number_node2 parameters are required"
                                          "when having ha type as true and license_type as azure-ha-cot-premium-byol")

    def apply(self):
        """
        Apply action to the Cloud Manager CVO for AZURE
        :return: None
        """
        working_environment_id = None
        current = self.get_working_environment()
        # check the action whether to create, delete, or not
        cd_action = self.na_helper.get_cd_action(current, self.parameters)

        if self.na_helper.changed and not self.module.check_mode:
            if cd_action == "create":
                self.validate_cvo_params()
                working_environment_id = self.create_cvo_azure()
            elif cd_action == "delete":
                self.delete_cvo_azure(current['publicId'])

        self.module.exit_json(changed=self.na_helper.changed, working_environment_id=working_environment_id)


def main():
    """
    Create Cloud Manager CVO for AZURE class instance and invoke apply
    :return: None
    """
    obj_store = NetAppCloudManagerCVOAZURE()
    obj_store.apply()


if __name__ == '__main__':
    main()
