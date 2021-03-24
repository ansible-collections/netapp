#!/usr/bin/python

# (c) 2021, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

'''
na_cloudmanager_connector_aws
'''

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''

module: na_cloudmanager_connector_aws
short_description: NetApp Cloud Manager connector for AWS
extends_documentation_fragment:
    - netapp.cloudmanager.netapp.cloudmanager
version_added: '21.3.0'
author: NetApp Ansible Team (@carchi8py) <ng-ansibleteam@netapp.com>

description:
- Create or delete Cloud Manager connector for AWS.

options:

  state:
    description:
    - Whether the specified Cloud Manager connector for AWS should exist or not.
    choices: ['present', 'absent']
    default: 'present'
    type: str

  name:
    required: true
    description:
    - The name of the Cloud Manager connector for AWS to manage.
    type: str

  instance_type:
    description:
    - The type of instance (for example, t3.xlarge). At least 4 CPU and 16 GB of memory are required.
    type: str
    default: t3.xlarge

  key_name:
    required: true
    description:
    - The name of the key pair to use for the Connector instance.
    type: str

  subnet_id:
    required: true
    description:
    - The ID of the subnet for the instance.
    type: str

  region:
    required: true
    description:
    - The region where the Cloud Manager Connector will be created.
    type: str

  instance_id:
    description:
    - The ID of the EC2 instance used for delete.
    type: str

  client_id:
    description:
    - The unique client ID of the Connector.
    type: str

  ami:
    description:
    - The image ID.
    type: str

  company:
    required: true
    description:
    - The name of the company of the user.
    type: str

  security_group_ids:
    required: true
    description:
    - The IDs of the security groups for the instance, multiple security groups can be provided separated by ','.
    type: list
    elements: str

  iam_instance_profile_name:
    required: true
    description:
    - The name of the instance profile for the Connector.
    type: str

  enable_termination_protection:
    description:
    - Indicates whether to enable termination protection on the instance.
    type: bool
    default: false

  associate_public_ip_address:
    description:
    - Indicates whether to associate a public IP address to the instance. If not provided, the association will be done based on the subnet's configuration.
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

  aws_tag:
    description:
    - Additional tags for the AWS EC2 instance.
    type: list
    elements: dict
    suboptions:
      tag_key:
        description: The key of the tag.
        type: str
      tag_value:
        description: The tag value.
        type: str

  refresh_token:
    required: true
    description:
    - The refresh token for NetApp Cloud Manager API operations.
    type: str

notes:
- Support check_mode.
'''

EXAMPLES = """
- name: Create NetApp Cloud Manager connector for AWS
  netapp.cloudmanager.na_cloudmanager_connector_aws:
    state: present
    refresh_token: "{{ xxxxxxxxxxxxxxx }}"
    name: bsuhas_ansible_occm
    region: us-west-1
    key_name: dev_automation
    subnet_id: subnet-xxxxx
    ami: "{{ ami-xxxxxxxxxxxxxxxxx }}"
    security_group_ids: [sg-xxxxxxxxxxx]
    iam_instance_profile_name: OCCM_AUTOMATION
    account_id: "{{ account-xxxxxxx }}"
    company: NetApp
    proxy_url: abc.com
    proxy_user_name: xyz
    proxy_password: abcxyz
    aws_tag: [
        {tag_key: abc,
        tag_value: a123}]

- name: Delete NetApp Cloud Manager connector for AWS
  netapp.cloudmanager.na_cloudmanager_connector_aws:
    state: absent
    name: ansible
    region: us-west-1
    instance_id: i-xxxxxxxxxxxxx
    client_id: xxxxxxxxxxxxxxxxxxx
"""

RETURN = r''' # '''

import traceback
import uuid
import time

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

AWS_ACCOUNT = '952013314444'
UUID = str(uuid.uuid4())


class NetAppCloudManagerConnectorAWS(object):
    ''' object initialize and class methods '''

    def __init__(self):
        self.use_rest = False
        self.argument_spec = netapp_utils.cloudmanager_host_argument_spec()
        self.argument_spec.update(dict(
            name=dict(required=True, type='str'),
            state=dict(required=False, choices=['present', 'absent'], default='present'),
            instance_type=dict(required=False, type='str', default='t3.xlarge'),
            key_name=dict(required=True, type='str'),
            subnet_id=dict(required=True, type='str'),
            region=dict(required=True, type='str'),
            instance_id=dict(required=False, type='str'),
            client_id=dict(required=False, type='str'),
            ami=dict(required=False, type='str'),
            company=dict(required=True, type='str'),
            security_group_ids=dict(required=True, type='list', elements='str'),
            iam_instance_profile_name=dict(required=True, type='str'),
            enable_termination_protection=dict(required=False, type='bool', default=False),
            associate_public_ip_address=dict(required=False, type='bool', default=True),
            account_id=dict(required=False, type='str'),
            proxy_url=dict(required=False, type='str', default=''),
            proxy_user_name=dict(required=False, type='str', default=''),
            proxy_password=dict(required=False, type='str', default='', no_log=True),
            aws_tag=dict(required=False, type='list', elements='dict', options=dict(
                tag_key=dict(type='str'),
                tag_value=dict(type='str')
            )),
        ))

        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            required_if=[
                ['state', 'absent', ['instance_id', 'client_id']]
            ],
            supports_check_mode=True
        )

        if HAS_AWS_LIB is False:
            self.module.fail_json(msg="the python AWS library boto3 and botocore is required. Command is pip install boto3."
                                      "Import error: %s" % str(IMPORT_EXCEPTION))

        self.na_helper = NetAppModule()
        self.parameters = self.na_helper.set_parameters(self.module.params)

        self.rest_api = CloudManagerRestAPI(self.module)

    def get_instance(self):
        """
        Get Cloud Manager connector for AWS
        :return:
            Dictionary of current details if Cloud Manager connector for AWS
            None if Cloud Manager connector for AWS is not found
        """

        response = None
        client = boto3.client('ec2')

        if self.parameters.get('ami') is None:
            self.parameters['ami'] = self.get_ami()

        # filters = [{'Name': 'instance-type', 'Values': [self.parameters['instance_type']]},
        #            {'Name': 'key-name', 'Values': [self.parameters['key_name']]},
        #            {'Name': 'subnet-id', 'Values': [self.parameters['subnet_id']]},
        #            {'Name': 'image-id', 'Values': [self.parameters['ami']]},
        #            {'Name': 'tag:Name', 'Values': [self.parameters['name']]}
        #            ]

        try:
            response = client.describe_instances(InstanceIds=[self.parameters['instance_id']])

        except ClientError as error:
            self.module.fail_json(msg=to_native(error), exception=traceback.format_exc())

        if len(response['Reservations']) == 0:
            return None

        return response['Reservations'][0]['Instances'][0]['State']['Name']

    def get_ami(self):
        """
        Get AWS EC2 Image
        :return:
            Latest AMI
        """

        instance_ami = None
        client = boto3.client('ec2')

        try:
            instance_ami = client.describe_images(
                Filters=[
                    {
                        'Name': 'name',
                        'Values': [
                            'Setup-As-Service-AMI-Prod*',
                        ]
                    },
                ],
                Owners=[
                    AWS_ACCOUNT,
                ],
            )
        except ClientError as error:
            self.module.fail_json(msg=to_native(error), exception=traceback.format_exc())

        latest_date = instance_ami['Images'][0]['CreationDate']
        latest_ami = instance_ami['Images'][0]['ImageId']

        for image in instance_ami['Images']:
            if image['CreationDate'] > latest_date:
                latest_date = image['CreationDate']
                latest_ami = image['ImageId']

        return latest_ami

    def create_instance(self):
        """
        Create Cloud Manager connector for AWS
        :return: None
        """

        if self.parameters.get('ami') is None:
            self.parameters['ami'] = self.get_ami()

        user_data, client_id = self.register_agent_to_service()

        ec2 = boto3.client('ec2', region_name=self.parameters['region'])

        tags = [
            {
                'Key': 'Name',
                'Value': self.parameters['name']
            },
            {
                'Key': 'OCCMInstance',
                'Value': 'true'
            },
        ]

        if self.parameters.get('aws_tag') is not None:
            for each_tag in self.parameters['aws_tag']:
                tag = {
                    'Key': each_tag['tag_key'],
                    'Value': each_tag['tag_value']
                }

                tags.append(tag)

        instance_input = {
            'BlockDeviceMappings': [
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'Encrypted': True,
                        'VolumeSize': 100,
                        'VolumeType': 'gp2',
                    },
                },
            ],
            'ImageId': self.parameters['ami'],
            'MinCount': 1,
            'MaxCount': 1,
            'KeyName': self.parameters['key_name'],
            'InstanceType': self.parameters['instance_type'],
            'DisableApiTermination': self.parameters['enable_termination_protection'],
            'TagSpecifications': [
                {
                    'ResourceType': 'instance',
                    'Tags': tags
                },
            ],
            'IamInstanceProfile': {
                'Name': self.parameters['iam_instance_profile_name']
            },
            'UserData': user_data
        }

        if self.parameters.get('associate_public_ip_address') is True:
            instance_input['NetworkInterfaces'] = [
                {
                    'AssociatePublicIpAddress': self.parameters['associate_public_ip_address'],
                    'DeviceIndex': 0,
                    'SubnetId': self.parameters['subnet_id'],
                    'Groups': self.parameters['security_group_ids']
                }
            ]
        else:
            instance_input['SubnetId'] = self.parameters['subnet_id']
            instance_input['SecurityGroupIds'] = self.parameters['security_group_ids']

        try:
            ec2.run_instances(**instance_input)
        except ClientError as error:
            self.module.fail_json(msg=to_native(error), exception=traceback.format_exc())

        # Sleep for 2 minutes
        time.sleep(120)
        retries = 16
        while retries > 0:
            occm_resp = self.check_occm_status(client_id)
            if occm_resp['agent']['status'] == "active":
                break
            else:
                time.sleep(30)
            retries = retries - 1
        if retries == 0:
            # Taking too long for status to be active
            return self.module.fail_json(msg="Taking too long for OCCM agent to be active or not properly setup")

    def get_account(self):
        """
        Get Account
        :return: Account ID
        """
        headers = {
            "X-User-Token": self.rest_api.token_type + " " + self.rest_api.token,
        }

        account_res, error, dummy = self.rest_api.get("cloudmanager.cloud.netapp.com/tenancy/account", header=headers)
        if error is not None:
            self.module.fail_json(msg="Error: unexpected response on getting account: %s, %s" % (str(error), str(account_res)))
        if len(account_res) == 0:
            account_id = self.create_account()
            return account_id
        account_id = account_res[0]['accountPublicId']

        return account_id

    def create_account(self):
        """
        Create Account
        :return: Account ID
        """
        headers = {
            "X-User-Token": self.rest_api.token_type + " " + self.rest_api.token,
        }

        account_res, error, dummy = self.rest_api.post("cloudmanager.cloud.netapp.com//tenancy/account/MyAccount", header=headers)
        if error is not None:
            self.module.fail_json(msg="Error: unexpected response on creating account: %s, %s" % (str(error), str(account_res)))

        account_id = account_res['accountPublicId']

        return account_id

    def check_occm_status(self, client):
        """
        Check OCCM status
        :return: status
        """

        get_occum_url = "cloudmanager.cloud.netapp.com/agents-mgmt/agent/" + client + "clients"
        headers = {
            "X-User-Token": self.rest_api.token_type + " " + self.rest_api.token,
        }

        occm_status, error, dummy = self.rest_api.get(get_occum_url, header=headers)
        if error is not None:
            self.module.fail_json(msg="Error: unexpected response on checking occm status: %s, %s" % (str(error), str(occm_status)))

        return occm_status

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

    def register_agent_to_service(self):
        """
        Register agent to service and collect userdata by setting up connector
        :return: UserData, ClientID
        """

        vpc = self.get_vpc()

        if self.parameters.get('account_id') is None:
            self.parameters['account_id'] = self.get_account()

        headers = {
            "X-User-Token": self.rest_api.token_type + " " + self.rest_api.token,
            "X-Service-Request-Id": "111"
        }
        body = {
            "accountId": self.parameters['account_id'],
            "name": self.parameters['name'],
            "company": self.parameters['company'],
            "placement": {
                "provider": "AWS",
                "region": self.parameters['region'],
                "network": vpc,
                "subnet": self.parameters['subnet_id'],
            },
            "extra": {
                "proxy": {
                    "proxyUrl": self.parameters.get('proxy_url'),
                    "proxyUserName": self.parameters.get('proxy_user_name'),
                    "proxyPassword": self.parameters.get('proxy_password')
                }
            }
        }

        response, error, dummy = self.rest_api.post("cloudmanager.cloud.netapp.com/agents-mgmt/connector-setup", body, header=headers)
        if error is not None:
            self.module.fail_json(msg="Error: unexpected response on getting userdata for connector setup: %s, %s" % (str(error), str(response)))
        client_id = response['clientId']
        client_secret = response['clientSecret']

        u_data = {
            'instanceName': self.parameters['name'],
            'company': self.parameters['company'],
            'clientId': client_id,
            'clientSecret': client_secret,
            'systemId': UUID,
            'tenancyAccountId': self.parameters['account_id'],
            'proxySettings': {'proxyPassword': self.parameters.get('proxy_password'),
                              'proxyUserName': self.parameters.get('proxy_user_name'),
                              'proxyUrl': self.parameters.get('proxy_url'),
                              },
            'localAgent': True
        }

        user_data = self.na_helper.convert_data_to_tabbed_jsonstring(u_data)

        return user_data, client_id

    def delete_instance(self):
        """
        Delete OCCM instance
        :return:
            None
        """

        ec2 = boto3.client('ec2', region_name=self.parameters['region'])
        try:
            ec2.terminate_instances(
                InstanceIds=[
                    self.parameters['instance_id'],
                ],
            )
        except ClientError as error:
            self.module.fail_json(msg=to_native(error), exception=traceback.format_exc())

        retries = 30
        while retries > 0:
            occm_resp = self.check_occm_status(self.parameters['client_id'])
            if occm_resp['agent']['status'] != "active":
                break
            else:
                time.sleep(10)
            retries = retries - 1
        if retries == 0:
            # Taking too long for terminating OCCM
            return self.module.fail_json(msg="Taking too long for instance to finish terminating")

        delete_occum_url = "cloudmanager.cloud.netapp.com/agents-mgmt/agent/" + self.parameters['client_id'] + "clients"
        headers = {
            "X-User-Token": self.rest_api.token_type + " " + self.rest_api.token,
            "X-Tenancy-Account-Id": self.parameters['account_id']
        }

        response, error, dummy = self.rest_api.delete(delete_occum_url, None, header=headers)
        if error is not None:
            self.module.fail_json(msg="Error: unexpected response on deleting OCCM: %s, %s" % (str(error), str(response)))

    def apply(self):
        """
        Apply action to the Cloud Manager connector for AWS
        :return: None
        """
        if self.module.check_mode:
            pass
        else:
            if self.parameters['state'] == 'present':
                self.create_instance()
                self.na_helper.changed = True
            elif self.parameters['state'] == 'absent':
                status = self.get_instance()
                if status != 'terminated':
                    self.delete_instance()
                    self.na_helper.changed = True

        self.module.exit_json(changed=self.na_helper.changed)


def main():
    """
    Create Cloud Manager connector for AWS class instance and invoke apply
    :return: None
    """
    obj_store = NetAppCloudManagerConnectorAWS()
    obj_store.apply()


if __name__ == '__main__':
    main()
