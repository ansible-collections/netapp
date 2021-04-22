#!/usr/bin/python

# (c) 2021, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

'''
na_cloudmanager_cvo_aws
'''

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''

module: na_cloudmanager_cvo_aws
short_description: NetApp Cloud Manager CVO for AWS
extends_documentation_fragment:
    - netapp.cloudmanager.netapp.cloudmanager
version_added: '21.3.0'
author: NetApp Ansible Team (@carchi8py) <ng-ansibleteam@netapp.com>

description:
- Create or delete Cloud Manager CVO for AWS.

options:

  state:
    description:
    - Whether the specified Cloud Manager CVO for AWS should exist or not.
    choices: ['present', 'absent']
    default: 'present'
    type: str

  name:
    required: true
    description:
    - The name of the Cloud Manager CVO for AWS to manage.
    type: str

  instance_type:
    description:
    - The instance type to use, which depends on the license type.
    - Explore ['m5.xlarge'].
    - Standard ['m5.2xlarge','r5.xlarge'].
    - Premium ['m5.4xlarge','r5.2xlarge','c4.8xlarge'].
    - For more supported instance types, refer to Cloud Volumes ONTAP Release Notes.
    type: str
    default: m5.2xlarge

  license_type:
    description:
    - The type of license to use.
    - For single node ['cot-explore-paygo','cot-standard-paygo', 'cot-premium-paygo', 'cot-premium-byol'].
    - For HA ['ha-cot-explore-paygo','ha-cot-standard-paygo','ha-cot-premium-paygo','ha-cot-premium-byol'].
    choices: ['cot-standard-paygo', 'cot-premium-paygo', 'cot-explore-paygo', 'cot-premium-byol',
    'ha-cot-standard-paygo','ha-cot-premium-paygo', 'ha-cot-premium-byol', 'ha-cot-explore-paygo']
    default: 'cot-standard-paygo'
    type: str

  workspace_id:
    description:
    - The ID of the Cloud Manager workspace where you want to deploy Cloud Volumes ONTAP.
    - If not provided, Cloud Manager uses the first workspace.
    - You can find the ID from the Workspace tab on U(https://cloudmanager.netapp.com).
    type: str

  subnet_id:
    description:
    - The subnet id where the working environment will be created. Required when single node only.
    type: str

  vpc_id:
    description:
    - The VPC ID where the working environment will be created.
    - If this argument is not provided, the VPC will be calculated by using the provided subnet ID.
    type: str

  region:
    required: true
    description:
    - The region where the working environment will be created.
    type: str

  data_encryption_type:
    description:
    - The type of encryption to use for the working environment.
    choices: ['AWS', 'NONE']
    default: 'AWS'
    type: str

  client_id:
    required: true
    description:
    - The client ID of the Cloud Manager Connector.
    - You can find the ID from the Connector tab on U(https://cloudmanager.netapp.com).
    type: str

  ebs_volume_size:
    description:
    - EBS volume size for the first data aggregate.
    - For GB, the value can be [100 or 500].
    - For TB, the value can be [1,2,4,8,16].
    default: 1
    type: int

  ebs_volume_size_unit:
    description:
    - The unit for ebs volume size.
    choices: ['GB', 'TB']
    default: 'TB'
    type: str

  ebs_volume_type:
    description:
    - The EBS volume type for the first data aggregate.
    choices: ['gp2', 'io1', 'sc1', 'st1']
    default: 'gp2'
    type: str

  security_group_id:
    description:
    - The ID of the security group for the working environment. If not provided, Cloud Manager creates the security group.
    type: str

  instance_profile_name:
    description:
    - The instance profile name for the working environment. If not provided, Cloud Manager creates the instance profile.
    type: str

  svm_password:
    required: true
    description:
    - The admin password for Cloud Volumes ONTAP.
    type: str

  ontap_version:
    description:
    - The required ONTAP version. Ignored if 'use_latest_version' is set to true.
    type: str
    default: 'latest'

  use_latest_version:
    description:
    - Indicates whether to use the latest available ONTAP version.
    type: bool
    default: true

  platform_serial_number:
    description:
    - The serial number for the cluster. This is required when using 'cot-premium-byol'.
    type: str

  tier_level:
    description:
    - The tiering level when 'capacity_tier' is set to 'S3'.
    choices: ['normal', 'ia', 'ia-single', 'intelligent']
    default: 'normal'
    type: str

  nss_account:
    description:
    - The NetApp Support Site account ID to use with this Cloud Volumes ONTAP system.
    - If the license type is BYOL and an NSS account is not provided, Cloud Manager tries to use the first existing NSS account.
    type: str

  writing_speed_state:
    description:
    - The write speed setting for Cloud Volumes ONTAP ['NORMAL','HIGH'].
    - This argument is not relevant for HA pairs.
    type: str

  iops:
    description:
    - Provisioned IOPS. Required only when provider_volume_type is 'io1'.
    type: int

  capacity_tier:
    description:
    - Whether to enable data tiering for the first data aggregate.
    choices: ['S3', 'NONE']
    default: 'S3'
    type: str

  instance_tenancy:
    description:
    - The EC2 instance tenancy.
    choices: ['default', 'dedicated']
    default: 'default'
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

  optimized_network_utilization:
    description:
    - Use optimized network utilization.
    default: true
    type: bool

  kms_key_id:
    description:
    - Aws Encryption.
    type: str

  aws_tag:
    description:
    - Additional tags for the AWS CVO working environment.
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
    - For HA BYOL, the serial number for the first node. This is required when using 'ha-cot-premium-byol'.
    type: str

  platform_serial_number_node2:
    description:
    - For HA BYOL, the serial number for the second node. This is required when using 'ha-cot-premium-byol'.
    type: str

  node1_subnet_id:
    description:
    - For HA, the subnet ID of the first node.
    type: str

  node2_subnet_id:
    description:
    - For HA, the subnet ID of the second node.
    type: str

  mediator_subnet_id:
    description:
    - For HA, the subnet ID of the mediator.
    type: str

  failover_mode:
    description:
    - For HA, the failover mode for the HA pair. 'PrivateIP' is for a single availability zone and 'FloatingIP' is for multiple availability zones.
    type: str
    choices: ['PrivateIP', 'FloatingIP']

  mediator_assign_public_ip:
    description:
    - Boolean option to assign public IP.
    type: bool
    default: true

  mediator_key_pair_name:
    description:
    - For HA, the key pair name for the mediator instance.
    type: str

  cluster_floating_ip:
    description:
    - For HA FloatingIP, the cluster management floating IP address.
    type: str

  data_floating_ip:
    description:
    - For HA FloatingIP, the data floating IP address.
    type: str

  data_floating_ip2:
    description:
    - For HA FloatingIP, the data floating IP address.
    type: str

  svm_floating_ip:
    description:
    - For HA FloatingIP, the SVM management floating IP address.
    type: str

  route_table_ids:
    description:
    - For HA FloatingIP, the list of route table IDs that will be updated with the floating IPs.
    type: list
    elements: str

  refresh_token:
    required: true
    description:
    - The refresh token for NetApp Cloud Manager API operations.
    type: str

notes:
- Support check_mode.
'''

EXAMPLES = """
- name: Create NetApp Cloud Manager CVO for AWS single
  netapp.cloudmanager.na_cloudmanager_cvo_aws:
    state: present
    refresh_token: "{{ xxxxxxxxxxxxxxx }}"
    name: TerraformCVO
    region: us-west-1
    subnet_id: subnet-xxxxxxx
    vpc_id: vpc-xxxxxxxx
    svm_password: P@assword!
    client_id: "{{ xxxxxxxxxxxxxxx }}"
    writing_speed_state: NORMAL
    aws_tag: [
        {tag_key: abc,
        tag_value: a123}]

- name: Create NetApp Cloud Manager CVO for AWS HA
  netapp.cloudmanager.na_cloudmanager_cvo_aws:
    state: present
    refresh_token: "{{ xxxxxxxxxxxxxxx }}"
    name: TerraformCVO
    region: us-west-1
    subnet_id: subnet-xxxxxxx
    vpc_id: vpc-xxxxxxxx
    svm_password: P@assword!
    client_id: "{{ xxxxxxxxxxxxxxx }}"
    writing_speed_state: NORMAL
    aws_tag: [
        {tag_key: abc,
        tag_value: a123}]
    is_ha: true
    failover_mode: FloatingIP
    node1_subnet_id: subnet-1
    node2_subnet_id: subnet-1
    mediator_subnet_id: subnet-1
    mediator_key_pair_name: key1
    cluster_floating_ip: 2.1.1.1
    data_floating_ip: 2.1.1.2
    data_floating_ip2: 2.1.1.3
    svm_floating_ip: 2.1.1.4
    route_table_ids: [rt-1,rt-2]

- name: Delete NetApp Cloud Manager cvo for AWS
  netapp.cloudmanager.na_cloudmanager_cvo_aws:
    state: absent
    name: ansible
    region: us-west-1
    subnet_id: subnet-xxxxxxx
    vpc_id: vpc-xxxxxxxx
    svm_password: P@assword!
    client_id: "{{ xxxxxxxxxxxxxxx }}"
"""

RETURN = '''
working_environment_id:
  description: Newly created AWS CVO working_environment_id.
  type: str
  returned: success
'''

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
import ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp as netapp_utils
from ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp_module import NetAppModule
from ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp import CloudManagerRestAPI
IMPORT_EXCEPTION = None

try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_AWS_LIB = True
except ImportError as exc:
    HAS_AWS_LIB = False
    IMPORT_EXCEPTION = exc

Cloud_Manager_Host = "cloudmanager.cloud.netapp.com"
AWS_License_Types = ['cot-standard-paygo', 'cot-premium-paygo', 'cot-explore-paygo', 'cot-premium-byol', 'ha-cot-standard-paygo',
                     'ha-cot-premium-paygo', 'ha-cot-premium-byol', 'ha-cot-explore-paygo']


class NetAppCloudManagerCVOAWS:
    ''' object initialize and class methods '''

    def __init__(self):
        self.use_rest = False
        self.argument_spec = netapp_utils.cloudmanager_host_argument_spec()
        self.argument_spec.update(dict(
            name=dict(required=True, type='str'),
            state=dict(required=False, choices=['present', 'absent'], default='present'),
            instance_type=dict(required=False, type='str', default='m5.2xlarge'),
            license_type=dict(required=False, type='str', choices=AWS_License_Types, default='cot-standard-paygo'),
            workspace_id=dict(required=False, type='str'),
            subnet_id=dict(required=False, type='str'),
            vpc_id=dict(required=False, type='str'),
            region=dict(required=True, type='str'),
            data_encryption_type=dict(required=False, type='str', choices=['AWS', 'NONE'], default='AWS'),
            ebs_volume_size=dict(required=False, type='int', default='1'),
            ebs_volume_size_unit=dict(required=False, type='str', choices=['GB', 'TB'], default='TB'),
            ebs_volume_type=dict(required=False, type='str', choices=['gp2', 'io1', 'sc1', 'st1'], default='gp2'),
            svm_password=dict(required=True, type='str', no_log=True),
            ontap_version=dict(required=False, type='str', default='latest'),
            use_latest_version=dict(required=False, type='bool', default=True),
            platform_serial_number=dict(required=False, type='str'),
            tier_level=dict(required=False, type='str', choices=['normal', 'ia', 'ia-single', 'intelligent'], default='normal'),
            nss_account=dict(required=False, type='str'),
            writing_speed_state=dict(required=False, type='str'),
            iops=dict(required=False, type='int'),
            capacity_tier=dict(required=False, type='str', choices=['S3', 'NONE'], default='S3'),
            instance_tenancy=dict(required=False, type='str', choices=['default', 'dedicated'], default='default'),
            instance_profile_name=dict(required=False, type='str'),
            security_group_id=dict(required=False, type='str'),
            cloud_provider_account=dict(required=False, type='str'),
            backup_volumes_to_cbs=dict(required=False, type='bool', default=False),
            enable_compliance=dict(required=False, type='bool', default=False),
            enable_monitoring=dict(required=False, type='bool', default=False),
            optimized_network_utilization=dict(required=False, type='bool', default=True),
            kms_key_id=dict(required=False, type='str'),
            client_id=dict(required=True, type='str'),
            aws_tag=dict(required=False, type='list', elements='dict', options=dict(
                tag_key=dict(type='str', no_log=False),
                tag_value=dict(type='str')
            )),
            is_ha=dict(required=False, type='bool', default=False),
            platform_serial_number_node1=dict(required=False, type='str'),
            platform_serial_number_node2=dict(required=False, type='str'),
            failover_mode=dict(required=False, type='str', choices=['PrivateIP', 'FloatingIP']),
            mediator_assign_public_ip=dict(required=False, type='bool', default=True),
            node1_subnet_id=dict(required=False, type='str'),
            node2_subnet_id=dict(required=False, type='str'),
            mediator_subnet_id=dict(required=False, type='str'),
            mediator_key_pair_name=dict(required=False, type='str'),
            cluster_floating_ip=dict(required=False, type='str'),
            data_floating_ip=dict(required=False, type='str'),
            data_floating_ip2=dict(required=False, type='str'),
            svm_floating_ip=dict(required=False, type='str'),
            route_table_ids=dict(required=False, type='list', elements='str'),
        ))

        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True
        )

        if HAS_AWS_LIB is False:
            self.module.fail_json(msg="the python AWS library boto3 and botocore is required. Command is pip install boto3."
                                      "Import error: %s" % str(IMPORT_EXCEPTION))

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
                msg="Error: unexpected response on getting aws cvo: %s, %s" % (str(error), str(response)))

        for each in response['vsaWorkingEnvironments']:
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
                msg="Error: unexpected response on getting tenant for aws cvo: %s, %s" % (str(error), str(response)))

        return response[0]['publicId']

    def get_nss(self):
        """
        Get nss account
        """

        api_url = '%s/occm/api/accounts' % Cloud_Manager_Host
        response, error, dummy = self.rest_api.get(api_url, header=self.headers)
        if error is not None:
            self.module.fail_json(
                msg="Error: unexpected response on getting nss for aws cvo: %s, %s" % (str(error), str(response)))

        if len(response['nssAccounts']) == 0:
            self.module.fail_json(msg="could not find any NSS account")

        return response['nssAccounts'][0]['publicId']

    def get_vpc(self):
        """
        Get vpc
        :return: vpc ID
        """

        vpc_result = None
        ec2 = boto3.client('ec2', region_name=self.parameters['region'])

        vpc_input = {'SubnetIds': [self.parameters['subnet_id']]}

        try:
            vpc_result = ec2.describe_subnets(**vpc_input)
        except ClientError as error:
            self.module.fail_json(msg=to_native(error), exception=traceback.format_exc())

        return vpc_result['Subnets'][0]['VpcId']

    def create_cvo_aws(self):
        """
        Create AWS CVO
        """

        if self.parameters.get('workspace_id') is None:
            self.parameters['workspace_id'] = self.get_tenant()

        if self.parameters.get('vpc_id') is None and self.parameters['is_ha'] is False:
            self.parameters['vpc_id'] = self.get_vpc()

        if self.parameters.get('nss_account') is None:
            if self.parameters.get('platform_serial_number') is not None:
                if not self.parameters['platform_serial_number'].startswith('Eval-') and self.parameters['license_type'] == 'cot-premium-byol':
                    self.parameters['nss_account'] = self.get_nss()
            elif self.parameters.get('platform_serial_number_node1') is not None and self.parameters.get('platform_serial_number_node2') is not None:
                if not self.parameters['platform_serial_number_node1'].startswith('Eval-')\
                        and not self.parameters['platform_serial_number_node2'].startswith('Eval-')\
                        and self.parameters['license_type'] == 'ha-cot-premium-byol':
                    self.parameters['nss_account'] = self.get_nss()

        json = {"name": self.parameters['name'],
                "region": self.parameters['region'],
                "tenantId": self.parameters['workspace_id'],
                "vpcId": self.parameters['vpc_id'],
                "dataEncryptionType": self.parameters['data_encryption_type'],
                "ebsVolumeSize": {
                    "size": self.parameters['ebs_volume_size'],
                    "unit": self.parameters['ebs_volume_size_unit']},
                "ebsVolumeType": self.parameters['ebs_volume_type'],
                "svmPassword": self.parameters['svm_password'],
                "backupVolumesToCbs": self.parameters['backup_volumes_to_cbs'],
                "enableCompliance": self.parameters['enable_compliance'],
                "enableMonitoring": self.parameters['enable_monitoring'],
                "optimizedNetworkUtilization": self.parameters['optimized_network_utilization'],
                "vsaMetadata": {
                    "ontapVersion": self.parameters['ontap_version'],
                    "useLatestVersion": self.parameters['use_latest_version'],
                    "licenseType": self.parameters['license_type'],
                    "instanceType": self.parameters['instance_type']}
                }

        if self.parameters['capacity_tier'] == "S3":
            json.update({"capacityTier": self.parameters['capacity_tier'],
                         "tierLevel": self.parameters['tier_level']})

        if self.parameters.get('platform_serial_number') is not None:
            json['vsaMetadata'].update({"platformSerialNumber": self.parameters['platform_serial_number']})

        if self.parameters.get('writing_speed_state') is not None:
            json.update({"writingSpeedState": self.parameters['writing_speed_state']})

        if self.parameters.get('iops') is not None:
            json.update({"iops": self.parameters['iops']})

        if self.parameters.get('instance_tenancy') is not None:
            json.update({"instanceTenancy": self.parameters['instance_tenancy']})

        if self.parameters.get('instance_profile_name') is not None:
            json.update({"instanceProfileName": self.parameters['instance_profile_name']})

        if self.parameters.get('security_group_id') is not None:
            json.update({"securityGroupId": self.parameters['security_group_id']})

        if self.parameters.get('cloud_provider_account') is not None:
            json.update({"cloudProviderAccount": self.parameters['cloud_provider_account']})

        if self.parameters.get('backup_volumes_to_cbs') is not None:
            json.update({"backupVolumesToCbs": self.parameters['backup_volumes_to_cbs']})

        if self.parameters.get('kms_key_id') is not None:
            json.update({"awsEncryptionParameters": {"kmsKeyId": self.parameters['kms_key_id']}})

        if self.parameters.get('aws_tag') is not None:
            tags = []
            for each_tag in self.parameters['aws_tag']:
                tag = {
                    'tagKey': each_tag['tag_key'],
                    'tagValue': each_tag['tag_value']
                }

                tags.append(tag)
            json.update({"awsTags": tags})

        if self.parameters['is_ha'] is True:
            ha_params = dict({
                "mediatorAssignPublicIP": self.parameters['mediator_assign_public_ip']
            })

            if self.parameters.get('failover_mode'):
                ha_params["failoverMode"] = self.parameters['failover_mode']

            if self.parameters.get('node1_subnet_id'):
                ha_params["node1SubnetId"] = self.parameters['node1_subnet_id']

            if self.parameters.get('node2_subnet_id'):
                ha_params["node2SubnetId"] = self.parameters['node2_subnet_id']

            if self.parameters.get('mediator_subnet_id'):
                ha_params["mediatorSubnetId"] = self.parameters['mediator_subnet_id']

            if self.parameters.get('mediator_key_pair_name'):
                ha_params["mediatorKeyPairName"] = self.parameters['mediator_key_pair_name']

            if self.parameters.get('cluster_floating_ip'):
                ha_params["clusterFloatingIP"] = self.parameters['cluster_floating_ip']

            if self.parameters.get('data_floating_ip'):
                ha_params["dataFloatingIP"] = self.parameters['data_floating_ip']

            if self.parameters.get('data_floating_ip2'):
                ha_params["dataFloatingIP2"] = self.parameters['data_floating_ip2']

            if self.parameters.get('svm_floating_ip'):
                ha_params["svmFloatingIP"] = self.parameters['svm_floating_ip']

            if self.parameters.get('route_table_ids'):
                ha_params["routeTableIds"] = self.parameters['route_table_ids']

            if self.parameters.get('platform_serial_number_node1'):
                ha_params["platformSerialNumberNode1"] = self.parameters['platform_serial_number_node1']

            if self.parameters.get('platform_serial_number_node2'):
                ha_params["platformSerialNumberNode2"] = self.parameters['platform_serial_number_node2']

            json["haParams"] = ha_params

        else:
            json["subnetId"] = self.parameters['subnet_id']

        if self.parameters['is_ha'] is True:
            base_url = '/occm/api/aws/ha/working-environments'
        else:
            base_url = '/occm/api/vsa/working-environments'

        api_url = '%s%s' % (Cloud_Manager_Host, base_url)

        response, error, on_cloud_request_id = self.rest_api.post(api_url, json, header=self.headers)
        if error is not None:
            self.module.fail_json(
                msg="Error: unexpected response on creating cvo aws: %s, %s" % (str(error), str(response)))
        working_environment_id = response['publicId']
        wait_on_completion_api_url = '%s/occm/api/audit/activeTask/%s' % (Cloud_Manager_Host, str(on_cloud_request_id))
        err = self.rest_api.wait_on_completion(wait_on_completion_api_url, "CVO", "create", 60, 60)

        if err is not None:
            self.module.fail_json(msg="Error: unexpected response wait_on_completion for creating CVO AWS: %s" % str(err))

        return working_environment_id

    def delete_cvo_aws(self, we_id):
        """
        Delete AWS CVO
        """
        if self.parameters['is_ha'] is True:
            base_url = '/occm/api/aws/ha/working-environments'
        else:
            base_url = '/occm/api/vsa/working-environments'

        api_url = '%s%s/%s' % (Cloud_Manager_Host, base_url, we_id)
        response, error, on_cloud_request_id = self.rest_api.delete(api_url, None, header=self.headers)
        if error is not None:
            self.module.fail_json(msg="Error: unexpected response on deleting cvo aws: %s, %s" % (str(error), str(response)))

        wait_on_completion_api_url = '%s/occm/api/audit/activeTask/%s' % (Cloud_Manager_Host, str(on_cloud_request_id))
        err = self.rest_api.wait_on_completion(wait_on_completion_api_url, "CVO", "delete", 40, 60)

        if err is not None:
            self.module.fail_json(msg="Error: unexpected response wait_on_completion for deleting CVO AWS: %s" % str(err))

    def validate_cvo_params(self):
        if self.parameters['use_latest_version'] is True and self.parameters['ontap_version'] != "latest":
            self.module.fail_json(msg="ontap_version parameter not required when having use_latest_version as true")

        if self.parameters.get('platform_serial_number') is not None and self.parameters['license_type'] != "cot-premium-byol":
            self.module.fail_json(msg="platform_serial_number parameter required only when having license_type as cot-premium-byol")

        if (self.parameters.get('iops') is None and self.parameters['ebs_volume_type'] == "io1")\
                or (self.parameters.get('iops') is not None and self.parameters['ebs_volume_type'] != "io1"):
            self.module.fail_json(msg="iops parameter required when having ebs_volume_type as io1")

        if self.parameters['is_ha'] is True and self.parameters['license_type'] == "ha-cot-premium-byol":
            if self.parameters.get('platform_serial_number_node1') is None or self.parameters.get('platform_serial_number_node2') is None:
                self.module.fail_json(msg="both platform_serial_number_node1 and platform_serial_number_node2 parameters are required"
                                          "when having ha type as true and license_type as ha-cot-premium-byol")

    def apply(self):
        """
        Apply action to the Cloud Manager CVO for AWS
        :return: None
        """
        working_environment_id = None
        current = self.get_working_environment()
        # check the action
        cd_action = self.na_helper.get_cd_action(current, self.parameters)

        if self.na_helper.changed and not self.module.check_mode:
            if cd_action == "create":
                self.validate_cvo_params()
                working_environment_id = self.create_cvo_aws()
            elif cd_action == "delete":
                self.delete_cvo_aws(current['publicId'])

        if self.parameters['state'] == "present" and cd_action is None:
            self.module.warn(warning=self.parameters['name'] + ' already exists')

        self.module.exit_json(changed=self.na_helper.changed, working_environment_id=working_environment_id)


def main():
    """
    Create Cloud Manager CVO for AWS class instance and invoke apply
    :return: None
    """
    obj_store = NetAppCloudManagerCVOAWS()
    obj_store.apply()


if __name__ == '__main__':
    main()
