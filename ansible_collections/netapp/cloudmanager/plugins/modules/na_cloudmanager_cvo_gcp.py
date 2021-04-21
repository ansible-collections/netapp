#!/usr/bin/python

# (c) 2021, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

'''
na_cloudmanager_cvo_gcp
'''

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''

module: na_cloudmanager_cvo_gcp
short_description: NetApp Cloud Manager CVO for GCP
extends_documentation_fragment:
    - netapp.cloudmanager.netapp.cloudmanager
version_added: '21.4.0'
author: NetApp Ansible Team (@carchi8py) <ng-ansibleteam@netapp.com>

description:
- Create or delete Cloud Manager CVO for GCP.

options:

  backup_volumes_to_cbs:
    description:
    - Automatically backup all volumes to cloud.
    default: false
    type: bool

  capacity_tier:
    description:
    - Whether to enable data tiering for the first data aggregate.
    choices: ['cloudStorage']
    type: str

  client_id:
    required: true
    description:
    - The client ID of the Cloud Manager Connector.
    - You can find the ID from the Connector tab on U(https://cloudmanager.netapp.com).
    type: str

  data_encryption_type:
    description:
    - Type of encryption to use for this working environment.
    choices: ['GCP']
    type: str

  enable_compliance:
    description:
    - Enable the Cloud Compliance service on the working environment.
    default: false
    type: bool

  firewall_rule:
    description:
    - Firewall name for a single node cluster.
    type: str

  gcp_labels:
    description:
    - Optionally provide up to four key-value pairs with which to all GCP entities created by Cloud Manager.
    type: list
    elements: dict
    suboptions:
      label_key:
        description: The key of the label.
        type: str
      label_value:
        description: The label value.
        type: str

  gcp_service_account:
    description:
    - The gcp_service_account email in order to enable tiering of cold data to Google Cloud Storage.
    required: true
    type: str

  gcp_volume_size:
    description:
    - GCP volume size.
    type: int

  gcp_volume_size_unit:
    description:
    - GCP volume size unit.
    choices: ['GB', 'TB']
    type: str

  gcp_volume_type:
    description:
    - GCP volume type.
    choices: ['pd-standard', 'pd-ssd']
    type: str

  instance_type:
    description:
    - The type of instance to use, which depends on the license type you choose.
    - Explore ['custom-4-16384'].
    - Standard ['n1-standard-8'].
    - Premium ['n1-standard-32'].
    - BYOL all instance types defined for PayGo.
    - For more supported instance types, refer to Cloud Volumes ONTAP Release Notes.
    default: 'n1-standard-8'
    type: str

  is_ha:
    description:
    - Indicate whether the working environment is an HA pair or not.
    type: bool
    default: false

  license_type:
    description:
    - The type of license to use.
    - Single node ['gcp-cot-explore-paygo', 'gcp-cot-standard-paygo', 'gcp-cot-premium-paygo', 'gcp-cot-premium-byol'].
    - HA ['gcp-ha-cot-explore-paygo', 'gcp-ha-cot-standard-paygo', 'gcp-ha-cot-premium-paygo', 'gcp-cot-premium-byol'].
    choices: ['gcp-cot-standard-paygo', 'gcp-cot-explore-paygo', 'gcp-cot-premium-paygo', 'gcp-cot-premium-byol',
    'gcp-ha-cot-standard-paygo', 'gcp-ha-cot-premium-paygo', 'gcp-ha-cot-explore-paygo', 'gcp-ha-cot-premium-byol']
    type: str
    default: 'gcp-cot-standard-paygo'

  mediator_zone:
    description:
    - The zone for mediator.
    - Option for HA pair only.
    type: str

  name:
    description:
    - The name of the Cloud Manager CVO for GCP to manage.
    required: true
    type: str

  network_project_id:
    description:
    - The project id in GCP associated with the Subnet.
    - If not provided, it is assumed that the Subnet is within the previously specified project id.
    type: str

  node1_zone:
    description:
    - Zone for node 1.
    - Option for HA pair only.
    type: str

  node2_zone:
    description:
    - Zone for node 2.
    - Option for HA pair only.
    type: str

  nss_account:
    description:
    - The NetApp Support Site account ID to use with this Cloud Volumes ONTAP system.
    - If the license type is BYOL and an NSS account isn't provided, Cloud Manager tries to use the first existing NSS account.
    type: str

  ontap_version:
    description:
    - The required ONTAP version. Ignored if 'use_latest_version' is set to true.
    type: str
    default: 'latest'

  platform_serial_number_node1:
    description:
    - For HA BYOL, the serial number for the first node.
    - Option for HA pair only.
    type: str

  platform_serial_number_node2:
    description:
    - For HA BYOL, the serial number for the second node.
    - Option for HA pair only.
    type: str

  project_id:
    description:
    - The ID of the GCP project.
    required: true
    type: str

  platform_serial_number:
    description:
    - The serial number for the system. Required when using 'gcp-cot-premium-byol'.
    type: str

  state:
    description:
    - Whether the specified Cloud Manager CVO for GCP should exist or not.
    choices: ['present', 'absent']
    default: 'present'
    type: str

  subnet_id:
    description:
    - The name of the subnet for Cloud Volumes ONTAP.
    type: str

  subnet0_node_and_data_connectivity:
    description:
    - Subnet path for nic1, required for node and data connectivity.
    - If using shared VPC, network_project_id must be provided.
    - Option for HA pair only.
    type: str

  subnet1_cluster_connectivity:
    description:
    - Subnet path for nic2, required for cluster connectivity.
    - Option for HA pair only.
    type: str

  subnet2_ha_connectivity:
    description:
    - Subnet path for nic3, required for HA connectivity.
    - Option for HA pair only.
    type: str

  subnet3_data_replication:
    description:
    - Subnet path for nic4, required for HA connectivity.
    - Option for HA pair only.
    type: str

  svm_password:
    description:
    - The admin password for Cloud Volumes ONTAP.
    type: str

  tier_level:
    description:
    - The tiering level when 'capacity_tier' is set to 'cloudStorage'.
    choices: ['standard', 'nearline', 'coldline']
    default: 'standard'
    type: str

  use_latest_version:
    description:
    - Indicates whether to use the latest available ONTAP version.
    type: bool
    default: true

  vpc_id:
    description:
    - The name of the VPC.
    type: str

  vpc0_firewall_rule_name:
    description:
    - Firewall rule name for vpc1.
    - Option for HA pair only.
    type: str

  vpc0_node_and_data_connectivity:
    description:
    - VPC path for nic1, required for node and data connectivity.
    - If using shared VPC, network_project_id must be provided.
    - Option for HA pair only.
    type: str

  vpc1_cluster_connectivity:
    description:
    - VPC path for nic2, required for cluster connectivity.
    - Option for HA pair only.
    type: str

  vpc1_firewall_rule_name:
    description:
    - Firewall rule name for vpc2.
    - Option for HA pair only.
    type: str

  vpc2_ha_connectivity:
    description:
    - VPC path for nic3, required for HA connectivity.
    - Option for HA pair only.
    type: str

  vpc2_firewall_rule_name:
    description:
    - Firewall rule name for vpc3.
    - Option for HA pair only.
    type: str

  vpc3_data_replication:
    description:
    - VPC path for nic4, required for data replication.
    - Option for HA pair only.
    type: str

  vpc3_firewall_rule_name:
    description:
    - Firewall rule name for vpc4.
    - Option for HA pair only.
    type: str

  workspace_id:
    description:
    - The ID of the Cloud Manager workspace where you want to deploy Cloud Volumes ONTAP.
    - If not provided, Cloud Manager uses the first workspace.
    - You can find the ID from the Workspace tab on [https://cloudmanager.netapp.com].
    type: str

  writing_speed_state:
    description:
    - The write speed setting for Cloud Volumes ONTAP ['NORMAL','HIGH'].
    - This argument is not relevant for HA pairs.
    type: str
    default: 'NORMAL'

  zone:
    description:
    - The zone of the region where the working environment will be created.
    required: true
    type: str

notes:
- Support check_mode.
'''

EXAMPLES = """

- name: Create NetApp Cloud Manager cvo for GCP
  netapp.cloudmanager.na_cloudmanager_cvo_gcp:
    state: present
    name: ansiblecvogcp
    project_id: default-project
    zone: us-east4-b
    subnet_id: default
    gcp_volume_type: pd-ssd
    gcp_volume_size: 500
    gcp_volume_size_unit: GB
    gcp_service_account: "{{ xxxxxxxxxxxxxxx }}"
    data_encryption_type: GCP
    svm_password: "{{ xxxxxxxxxxxxxxx }}"
    ontap_version: latest
    use_latest_version: true
    license_type: gcp-cot-standard-paygo
    instance_type: n1-standard-8
    client_id: "{{ xxxxxxxxxxxxxxx }}"
    workspace_id: "{{ xxxxxxxxxxxxxxx }}"
    capacity_tier: cloudStorage
    writing_speed_state: NORMAL
    refresh_token: "{{ xxxxxxxxxxxxxxx }}"
    gcp_labels:
      - label_key: key1
        label_value: value1
      - label_key: key2
        label_value: value2

- name: Create NetApp Cloud Manager cvo ha for GCP
  netapp.cloudmanager.na_cloudmanager_cvo_gcp:
    state: present
    name: ansiblecvogcpha
    project_id: "default-project"
    zone: us-east1-b
    gcp_volume_type: pd-ssd
    gcp_volume_size: 500
    gcp_volume_size_unit: GB
    gcp_service_account: "{{ xxxxxxxxxxxxxxx }}"
    data_encryption_type: GCP
    svm_password: "{{ xxxxxxxxxxxxxxx }}"
    ontap_version: ONTAP-9.9.0.T1.gcpha
    use_latest_version: false
    license_type: gcp-ha-cot-explore-paygo
    instance_type: custom-4-16384
    client_id: "{{ xxxxxxxxxxxxxxx }}"
    workspace_id:  "{{ xxxxxxxxxxxxxxx }}"
    capacity_tier: cloudStorage
    writing_speed_state: NORMAL
    refresh_token: "{{ xxxxxxxxxxxxxxx }}"
    is_ha: true
    mediator_zone: us-east1-b
    node1_zone: us-east1-b
    node2_zone: us-east1-b
    subnet0_node_and_data_connectivity: default
    subnet1_cluster_connectivity: subnet2
    subnet2_ha_connectivity: subnet3
    subnet3_data_replication: subnet1
    vpc0_node_and_data_connectivity: default
    vpc1_cluster_connectivity: vpc2
    vpc2_ha_connectivity: vpc3
    vpc3_data_replication: vpc1
    vpc_id: default
    subnet_id: default

"""

RETURN = '''
working_environment_id:
  description: Newly created GCP CVO working_environment_id.
  type: str
  returned: success
'''

from ansible.module_utils.basic import AnsibleModule
import ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp as netapp_utils
from ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp_module import NetAppModule
from ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp import CloudManagerRestAPI

CLOUD_MANAGER_HOST = "cloudmanager.cloud.netapp.com"
GCP_LICENSE_TYPES = ["gcp-cot-standard-paygo", "gcp-cot-explore-paygo", "gcp-cot-premium-paygo", "gcp-cot-premium-byol",
                     "gcp-ha-cot-standard-paygo", "gcp-ha-cot-premium-paygo", "gcp-ha-cot-explore-paygo",
                     "gcp-ha-cot-premium-byol"]
GOOGLE_API_URL = "https://www.googleapis.com/compute/v1/projects"


class NetAppCloudManagerCVOGCP:
    ''' object initialize and class methods '''

    def __init__(self):
        self.use_rest = False
        self.argument_spec = netapp_utils.cloudmanager_host_argument_spec()
        self.argument_spec.update(dict(
            backup_volumes_to_cbs=dict(required=False, type='bool', default=False),
            capacity_tier=dict(required=False, type='str', choices=['cloudStorage']),
            client_id=dict(required=True, type='str'),
            data_encryption_type=dict(required=False, choices=['GCP'], type='str'),
            enable_compliance=dict(required=False, type='bool', default=False),
            firewall_rule=dict(required=False, type='str'),
            gcp_labels=dict(required=False, type='list', elements='dict', options=dict(
                label_key=dict(type='str', no_log=False),
                label_value=dict(type='str')
            )),
            gcp_service_account=dict(required=True, type='str'),
            gcp_volume_size=dict(required=False, type='int'),
            gcp_volume_size_unit=dict(required=False, choices=['GB', 'TB'], type='str'),
            gcp_volume_type=dict(required=False, choices=['pd-standard', 'pd-ssd'], type='str'),
            instance_type=dict(required=False, type='str', default='n1-standard-8'),
            is_ha=dict(required=False, type='bool', default=False),
            license_type=dict(required=False, type='str', choices=GCP_LICENSE_TYPES, default='gcp-cot-standard-paygo'),
            mediator_zone=dict(required=False, type='str'),
            name=dict(required=True, type='str'),
            network_project_id=dict(required=False, type='str'),
            node1_zone=dict(required=False, type='str'),
            node2_zone=dict(required=False, type='str'),
            nss_account=dict(required=False, type='str'),
            ontap_version=dict(required=False, type='str', default='latest'),
            platform_serial_number=dict(required=False, type='str'),
            platform_serial_number_node1=dict(required=False, type='str'),
            platform_serial_number_node2=dict(required=False, type='str'),
            project_id=dict(required=True, type='str'),
            state=dict(required=False, choices=['present', 'absent'], default='present'),
            subnet_id=dict(required=False, type='str'),
            subnet0_node_and_data_connectivity=dict(required=False, type='str'),
            subnet1_cluster_connectivity=dict(required=False, type='str'),
            subnet2_ha_connectivity=dict(required=False, type='str'),
            subnet3_data_replication=dict(required=False, type='str'),
            svm_password=dict(required=False, type='str', no_log=True),
            tier_level=dict(required=False, type='str', choices=['standard', 'nearline', 'coldline'],
                            default='standard'),
            use_latest_version=dict(required=False, type='bool', default=True),
            vpc_id=dict(required=False, type='str'),
            vpc0_firewall_rule_name=dict(required=False, type='str'),
            vpc0_node_and_data_connectivity=dict(required=False, type='str'),
            vpc1_cluster_connectivity=dict(required=False, type='str'),
            vpc1_firewall_rule_name=dict(required=False, type='str'),
            vpc2_firewall_rule_name=dict(required=False, type='str'),
            vpc2_ha_connectivity=dict(required=False, type='str'),
            vpc3_data_replication=dict(required=False, type='str'),
            vpc3_firewall_rule_name=dict(required=False, type='str'),
            workspace_id=dict(required=False, type='str'),
            writing_speed_state=dict(required=False, type='str', default='NORMAL'),
            zone=dict(required=True, type='str'),
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

    def get_tenant(self):
        """
        Get workspace ID (tenant)
        """

        api_url = '%s/occm/api/tenants' % CLOUD_MANAGER_HOST
        response, error, dummy = self.rest_api.get(api_url, header=self.headers)
        if error is not None:
            self.module.fail_json(
                msg="Error: unexpected response on getting tenant for gcp cvo: %s, %s" % (str(error), str(response)))

        return response[0]['publicId']

    def get_nss(self):
        """
        Get nss account
        """

        api_url = '%s/occm/api/accounts' % CLOUD_MANAGER_HOST
        response, error, dummy = self.rest_api.get(api_url, header=self.headers)
        if error is not None:
            self.module.fail_json(
                msg="Error: unexpected response on getting nss for gcp cvo: %s, %s" % (str(error), str(response)))

        if len(response['nssAccounts']) == 0:
            self.module.fail_json(msg="could not find any NSS account")

        return response['nssAccounts'][0]['publicId']

    def create_cvo_gcp(self):

        if self.parameters.get('workspace_id') is None:
            self.parameters['workspace_id'] = self.get_tenant()

        if self.parameters.get('nss_account') is None:
            if self.parameters.get('platform_serial_number') is not None:
                if not self.parameters['platform_serial_number'].startswith('Eval-'):
                    if self.parameters['license_type'] == 'gcp-cot-premium-byol' or self.parameters['license_type'] == 'gcp-ha-cot-premium-byol':
                        self.parameters['nss_account'] = self.get_nss()

        json = {"name": self.parameters['name'],
                "region": self.parameters['zone'],
                "tenantId": self.parameters['workspace_id'],
                "vpcId": self.parameters['vpc_id'],
                "gcpServiceAccount": self.parameters['gcp_service_account'],
                "gcpVolumeSize": {
                    "size": self.parameters['gcp_volume_size'],
                    "unit": self.parameters['gcp_volume_size_unit']},
                "gcpVolumeType": self.parameters['gcp_volume_type'],
                "svmPassword": self.parameters['svm_password'],
                "backupVolumesToCbs": self.parameters['backup_volumes_to_cbs'],
                "enableCompliance": self.parameters['enable_compliance'],
                "writingSpeedState": self.parameters['writing_speed_state'],
                "vsaMetadata": {
                    "ontapVersion": self.parameters['ontap_version'],
                    "licenseType": self.parameters['license_type'],
                    "instanceType": self.parameters['instance_type']}
                }

        if self.parameters.get('data_encryption_type'):
            json.update({'dataEncryptionType': self.parameters['data_encryption_type']})

        if self.parameters.get('use_latest_version') is not None:
            json['vsaMetadata'].update({'useLatestVersion': self.parameters['use_latest_version']})

        if self.parameters.get('project_id'):
            json.update({'project': self.parameters['project_id']})

        if self.parameters.get('nss_account'):
            json.update({'nssAccount': self.parameters['nss_account']})

        if self.parameters.get('subnet_id'):
            json.update({'subnetId': self.parameters['subnet_id']})

        if self.parameters.get('platform_serial_number') is not None:
            json.update({"platformSerialNumber": self.parameters['platform_serial_number']})

        if self.parameters.get('capacity_tier') is not None and self.parameters['capacity_tier'] == "cloudStorage":
            json.update({"capacityTier": self.parameters['capacity_tier'],
                         "tierLevel": self.parameters['tier_level']})

        if self.parameters.get('gcp_labels') is not None:
            labels = []
            for each_label in self.parameters['gcp_labels']:
                label = {
                    'labelKey': each_label['label_key'],
                    'labelValue': each_label['label_value']
                }

                labels.append(label)
            json.update({"gcpLabels": labels})

        if self.parameters.get('firewall_rule'):
            json.update({'firewallRule': self.parameters['firewall_rule']})

        if self.parameters['is_ha'] is True:
            ha_params = dict()

            if self.parameters.get('network_project_id') is not None:
                json.update(
                    {'subnetId': 'projects/%s/regions/%s/subnetworks/%s' % (self.parameters.get('network_project_id'),
                                                                            self.parameters['zone'][:-2],
                                                                            self.parameters['subnet_id'])})
            else:
                json.update({'subnetId': 'projects/%s/regions/%s/subnetworks/%s' % (self.parameters.get('project_id'),
                                                                                    self.parameters['zone'][:-2],
                                                                                    self.parameters['subnet_id'])})

            if self.parameters.get('platform_serial_number_node1'):
                ha_params["platformSerialNumberNode1"] = self.parameters['platform_serial_number_node1']

            if self.parameters.get('platform_serial_number_node2'):
                ha_params["platformSerialNumberNode2"] = self.parameters['platform_serial_number_node2']

            if self.parameters.get('node1_zone'):
                ha_params["node1Zone"] = self.parameters['node1_zone']

            if self.parameters.get('node2_zone'):
                ha_params["node2Zone"] = self.parameters['node2_zone']

            if self.parameters.get('mediator_zone'):
                ha_params["mediatorZone"] = self.parameters['mediator_zone']

            if self.parameters.get('vpc0_node_and_data_connectivity'):
                if self.parameters.get("network_project_id") is not None:
                    ha_params["vpc0NodeAndDataConnectivity"] = GOOGLE_API_URL + "/{0}/global/networks/{1}".format(
                        self.parameters["network_project_id"], self.parameters['vpc0_node_and_data_connectivity'])
                else:
                    ha_params["vpc0NodeAndDataConnectivity"] = GOOGLE_API_URL + "/{0}/global/networks/{1}".format(
                        self.parameters["project_id"], self.parameters['vpc0_node_and_data_connectivity'])
            if self.parameters.get('vpc1_cluster_connectivity'):
                ha_params["vpc1ClusterConnectivity"] = GOOGLE_API_URL + "/{0}/global/networks/{1}".format(
                    self.parameters["project_id"], self.parameters['vpc1_cluster_connectivity'])
            if self.parameters.get('vpc2_ha_connectivity'):
                ha_params["vpc2HAConnectivity"] = "https://www.googleapis.com/compute/v1/projects/{0}/global/networks" \
                                                  "/{1}".format(self.parameters["project_id"],
                                                                self.parameters['vpc2_ha_connectivity'])
            if self.parameters.get('vpc3_data_replication'):
                ha_params["vpc3DataReplication"] = GOOGLE_API_URL + "/{0}/global/networks/{1}".format(
                    self.parameters["project_id"], self.parameters['vpc3_data_replication'])

            if self.parameters.get('subnet0_node_and_data_connectivity'):
                if self.parameters.get('network_project_id') is not None:
                    ha_params["subnet0NodeAndDataConnectivity"] = GOOGLE_API_URL + "/{0}/regions/{1}/subnetworks/{2}".\
                        format(self.parameters['network_project_id'], self.parameters['zone'][:-2],
                               self.parameters['subnet0_node_and_data_connectivity'])
                else:
                    ha_params["subnet0NodeAndDataConnectivity"] = GOOGLE_API_URL + "/{0}/regions/{1}/subnetworks/{2}".\
                        format(self.parameters['project_id'], self.parameters['zone'][:-2],
                               self.parameters['subnet0_node_and_data_connectivity'])

            if self.parameters.get('subnet1_cluster_connectivity'):
                ha_params["subnet1ClusterConnectivity"] = GOOGLE_API_URL + "/{0}/regions/{1}/subnetworks/{2}".format(
                    self.parameters['project_id'], self.parameters['zone'][:-2],
                    self.parameters['subnet1_cluster_connectivity'])

            if self.parameters.get('subnet2_ha_connectivity'):
                ha_params["subnet2HAConnectivity"] = GOOGLE_API_URL + "/{0}/regions/{1}/subnetworks/{2}".format(
                    self.parameters['project_id'], self.parameters['zone'][:-2],
                    self.parameters['subnet2_ha_connectivity'])

            if self.parameters.get('subnet3_data_replication'):
                ha_params["subnet3DataReplication"] = GOOGLE_API_URL + "/{0}/regions/{1}/subnetworks/{2}". \
                    format(self.parameters['project_id'], self.parameters['zone'][:-2],
                           self.parameters['subnet3_data_replication'])

            if self.parameters.get('vpc0_firewall_rule_name'):
                ha_params["vpc0FirewallRuleName"] = self.parameters['vpc0_firewall_ruleName']

            if self.parameters.get('vpc1_firewall_rule_name'):
                ha_params["vpc1FirewallRuleName"] = self.parameters['vpc1_firewall_rule_name']

            if self.parameters.get('vpc2_firewall_rule_name'):
                ha_params["vpc2FirewallRuleName"] = self.parameters['vpc2_firewall_rule_name']

            if self.parameters.get('vpc3_firewall_rule_name'):
                ha_params["vpc3FirewallRuleName"] = self.parameters['vpc3_firewall_rule_name']

            json["haParams"] = ha_params

        base_url = '/occm/api/gcp/vsa/working-environments'
        if self.parameters.get('is_ha'):
            base_url = '/occm/api/gcp/ha/working-environments'

        api_url = '%s%s' % (CLOUD_MANAGER_HOST, base_url)
        response, error, on_cloud_request_id = self.rest_api.post(api_url, json, header=self.headers)
        if error is not None:
            self.module.fail_json(
                msg="Error: unexpected response on creating cvo gcp: %s, %s" % (str(error), str(response)))
        working_environment_id = response['publicId']
        wait_on_completion_api_url = '%s/occm/api/audit/activeTask/%s' % (CLOUD_MANAGER_HOST, str(on_cloud_request_id))
        err = self.rest_api.wait_on_completion(wait_on_completion_api_url, "CVO", "create", 60, 60)

        if err is not None:
            self.module.fail_json(msg="Error: unexpected response wait_on_completion for creating CVO GCP: %s" % str(err))
        return working_environment_id

    def get_working_environment(self):
        """
        Get working environment details including:
        name: working environment name
        """
        api_url = '%s/occm/api/working-environments' % CLOUD_MANAGER_HOST
        response, error, dummy = self.rest_api.get(api_url, header=self.headers)
        if error is not None:
            self.module.fail_json(
                msg="Error: unexpected response on getting gcp cvo: %s, %s" % (str(error), str(response)))

        for each in response['gcpVsaWorkingEnvironments']:
            if each['name'] == self.parameters['name']:
                return each

        return None

    def delete_cvo_gcp(self, we_id):
        """
        Delete GCP CVO
        """
        self.na_helper.set_api_root_path(self.get_working_environment(), self.rest_api)
        api_url = '%s%s/%s' % (CLOUD_MANAGER_HOST, self.rest_api.api_root_path + '/working-environments', we_id)
        response, error, on_cloud_request_id = self.rest_api.delete(api_url, None, header=self.headers)
        if error is not None:
            self.module.fail_json(msg="Error: unexpected response on deleting cvo gcp: %s, %s" % (str(error), str(response)))

        wait_on_completion_api_url = '%s/occm/api/audit/activeTask/%s' % (CLOUD_MANAGER_HOST, str(on_cloud_request_id))
        err = self.rest_api.wait_on_completion(wait_on_completion_api_url, "CVO", "delete", 40, 60)
        if err is not None:
            self.module.fail_json(msg="Error: unexpected response wait_on_completion for deleting cvo gcp: %s" % str(err))

    def apply(self):
        working_environment_id = None
        current = self.get_working_environment()
        # check the action
        cd_action = self.na_helper.get_cd_action(current, self.parameters)

        if self.na_helper.changed and not self.module.check_mode:
            if cd_action == "create":
                working_environment_id = self.create_cvo_gcp()
            elif cd_action == "delete":
                self.delete_cvo_gcp(current['publicId'])

        if self.parameters['state'] == "present" and cd_action is None:
            self.module.warn(warning=self.parameters['name'] + ' already exists')

        self.module.exit_json(changed=self.na_helper.changed, working_environment_id=working_environment_id)


def main():
    """
    Create Cloud Manager CVO for GCP class instance and invoke apply
    :return: None
    """
    obj_store = NetAppCloudManagerCVOGCP()
    obj_store.apply()


if __name__ == '__main__':
    main()
