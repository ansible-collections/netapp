#!/usr/bin/python

# (c) 2021, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

'''
na_cloudmanager_volume
'''

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'certified'}

DOCUMENTATION = '''

module: na_cloudmanager_volume
short_description: NetApp Cloud Manager volume.
extends_documentation_fragment:
    - netapp.cloudmanager.netapp.cloudmanager
version_added: '21.3.0'
author: NetApp Ansible Team (@carchi8py) <ng-ansibleteam@netapp.com>

description:
- Create, Modify or Delete volume on Cloud Manager.

options:
    state:
        description:
        - Whether the specified volume should exist or not.
        choices: ['present', 'absent']
        default: 'present'
        type: str

    name:
        description:
        - The name of the volume.
        required: true
        type: str

    working_environment_name:
        description:
        - The working environment name where the volume will be created.
        type: str

    working_environment_id:
        description:
        - The public ID of the working environment where the volume will be created.
        type: str

    client_id:
        description:
        - The client ID of the Cloud Manager Connector.
        required: true
        type: str

    size:
        description:
        - The size of the volume.
        type: float

    size_unit:
        description:
        - The size unit of volume.
        choices: ['GB']
        default: 'GB'
        type: str

    snapshot_policy_name:
        description:
        - The snapshot policy name.
        type: str

    provider_volume_type:
        description:
        - The underlying cloud provider volume type.
        - For AWS is ["gp2", "io1", "st1", "sc1"].
        - For Azure is ['Premium_LRS','Standard_LRS','StandardSSD_LRS'].
        - For GCP is ['pd-ssd','pd-standard']
        type: str

    enable_deduplication:
        description:
        - Enabling deduplication.
        - Default to true if not specified.
        type: bool

    enable_compression:
        description:
        - Enabling cpmpression.
        - Default to true if not specified.
        type: bool

    enable_thin_provisioning:
        description:
        - Enabling thin provisioning.
        - Default to true if not specified.
        type: bool

    svm_name:
        description:
        - The name of the SVM. The default SVM name is used, if a name isn't provided.
        type: str

    capacity_tier:
        description:
        - The volume's capacity tier for tiering cold data to object storage.
        - The default values for each cloud provider are as follows. Amazon as 'S3', Azure as 'Blob', GCP as 'cloudStorage'.
        - If 'NONE', the capacity tier won't be set on volume creation.
        choices: ['NONE', 'S3', 'Blob', 'cloudStorage']
        type: str

    tiering_policy:
        description:
        - The tiering policy.
        choices: ['none', 'snapshot_only', 'auto', 'all']
        type: str

    export_policy_type:
        description:
        - The export policy type. (NFS protocol parameters)
        type: str

    export_policy_ip:
        description:
        - Custom export policy list of IPs. (NFS protocol parameters)
        type: list
        elements: str

    export_policy_nfs_version:
        description:
        - Export policy protocol. (NFS protocol parameters)
        type: list
        elements: str

    iops:
        description:
        - Provisioned IOPS. Needed only when provider_volume_type is "io1".
        type: int

'''

EXAMPLES = '''
    - name: create volume with working_environment_name
      na_cloudmanager_volume:
        state: present
        name: test_vol
        size: 15
        size_unit: GB
        working_environment_name: working_environment_1
        client_id: client_id
        refresh_token: refresh_token
        svm_name: svm_1
        snapshot_policy_name: default
        export_policy_type: custom
        export_policy_ip: ["10.0.0.1/16"]
        export_policy_nfs_version: ["nfs3","nfs4"]

    - name: delete volume
      na_cloudmanager_volume:
        state: absent
        name: test_vol
        working_environment_name: working_environment_1
        client_id: client_id
        refresh_token: refresh_token
        svm_name: svm_1
'''

from ansible.module_utils.basic import AnsibleModule
import ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp as netapp_utils
from ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp_module import NetAppModule


class NetAppCloudmanagerVolume(object):

    def __init__(self):
        """
        Parse arguments, setup state variables,
        check parameters and ensure request module is installed
        """
        self.argument_spec = netapp_utils.cloudmanager_host_argument_spec()
        self.argument_spec.update(dict(
            state=dict(required=False, choices=['present', 'absent'], default='present'),
            name=dict(required=True, type='str'),
            working_environment_id=dict(required=False, type='str'),
            working_environment_name=dict(required=False, type='str'),
            client_id=dict(required=True, type='str'),
            size=dict(required=False, type='float'),
            size_unit=dict(required=False, choices=['GB'], default='GB'),
            snapshot_policy_name=dict(required=False, type='str'),
            provider_volume_type=dict(required=False, type='str'),
            enable_deduplication=dict(required=False, type='bool'),
            enable_thin_provisioning=dict(required=False, type='bool'),
            enable_compression=dict(required=False, type='bool'),
            svm_name=dict(required=False, type='str'),
            capacity_tier=dict(required=False, type='str', choices=['NONE', 'S3', 'Blob', 'cloudStorage']),
            tiering_policy=dict(required=False, type='str', choices=['none', 'snapshot_only', 'auto', 'all']),
            export_policy_type=dict(required=False, type='str'),
            export_policy_ip=dict(required=False, type='list', elements='str'),
            export_policy_nfs_version=dict(required=False, type='list', elements='str'),
            iops=dict(required=False, type='int')
        ))
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            required_one_of=[
                ('working_environment_name', 'working_environment_id'),
            ],
            supports_check_mode=True
        )
        self.na_helper = NetAppModule()
        # set up state variables
        self.parameters = self.na_helper.set_parameters(self.module.params)
        # Calling generic rest_api class
        self.rest_api = netapp_utils.CloudManagerRestAPI(self.module)
        self.rest_api.token_type, self.rest_api.token = self.rest_api.get_token()
        self.rest_api.url += "cloudmanager.cloud.netapp.com"
        if self.parameters.get('working_environment_id'):
            working_environment_detail, error = self.na_helper.get_working_environment_details(self.rest_api)
        else:
            working_environment_detail, error = self.na_helper.get_working_environment_details_by_name(self.rest_api)
        if working_environment_detail is not None:
            self.parameters['working_environment_id'] = working_environment_detail['publicId']
            if self.parameters.get('svm_name') is None:
                self.parameters['svm_name'] = working_environment_detail['svmName']
        else:
            self.module.fail_json(msg="Error: Cannot find working environment: %s" % str(error))
        self.na_helper.set_api_root_path(working_environment_detail, self.rest_api)

        if self.parameters.get('capacity_tier') == 'S3' and not self.parameters.get('tiering_policy'):
            self.module.fail_json(msg="Error: tiering policy is required when capacity tier is S3")

        if self.parameters.get('provider_volume_type') and not self.parameters.get('iops'):
            self.module.fail_json(msg="Error: iops is required when provider_volume_type is io1")

    def get_volume(self):
        headers = {
            'X-Agent-Id': self.parameters['client_id'] + "clients"
        }
        response, err = self.rest_api.send_request("GET", "%s/volumes?workingEnvironmentId=%s" % (
            self.rest_api.api_root_path, self.parameters['working_environment_id']), None, header=headers)
        if err is not None:
            self.module.fail_json(changed=False, msg=err)
        target_vol = dict()
        if response is None:
            return None
        for volume in response:
            if volume['name'] == self.parameters['name']:
                target_vol['name'] = volume['name']
                target_vol['enable_deduplication'] = volume['deduplication']
                target_vol['enable_thin_provisioning'] = volume['thinProvisioning']
                target_vol['enable_compression'] = volume['compression']
                if self.parameters.get('export_policy_nfs_version') and volume.get('exportPolicyInfo'):
                    target_vol['export_policy_nfs_version'] = volume['exportPolicyInfo']['nfsVersion']
                if self.parameters.get('export_policy_ip') and volume.get('exportPolicyInfo'):
                    target_vol['export_policy_ip'] = volume['exportPolicyInfo']['ips']
                if self.parameters.get('export_policy_type') and volume.get('exportPolicyInfo'):
                    target_vol['export_policy_type'] = volume['exportPolicyInfo']['policyType']
                if self.parameters.get('snapshot_policy'):
                    target_vol['snapshot_policy'] = volume['snapshotPolicy']
                if self.parameters.get('provider_volume_type'):
                    target_vol['provider_volume_type'] = volume['providerVolumeType']
                if self.parameters.get('capacity_tier'):
                    target_vol['capacity_tier'] = volume['capacityTier']
                if self.parameters.get('tiering_policy'):
                    target_vol['tiering_policy'] = volume['tieringPolicy']
                return target_vol
        return None

    def create_volume(self):
        headers = {
            'X-Agent-Id': self.parameters['client_id'] + "clients"
        }
        exclude_list = ['client_id', 'size_unit', 'export_policy_name', 'export_policy_type', 'export_policy_ip',
                        'export_policy_nfs_version', 'capacity_tier']
        quote = self.na_helper.convert_module_args_to_api(self.parameters, exclude_list)
        quote['verifyNameUniqueness'] = True  # Always hard coded to true.
        quote['unit'] = self.parameters['size_unit']
        quote['size'] = {'size': self.parameters['size'], 'unit': self.parameters['size_unit']}
        if self.parameters.get('aggregate_name'):
            quote['aggregateName'] = self.parameters['aggregate_name']
        response, err = self.rest_api.send_request("POST", "%s/volumes/quote" % self.rest_api.api_root_path, None,
                                                   quote, header=headers)
        if err is not None:
            self.module.fail_json(changed=False, msg=err)
        quote['aggregateName'] = response['aggregateName']
        quote['maxNumOfDisksApprovedToAdd'] = response['numOfDisks']
        quote['exportPolicyInfo'] = dict()
        if self.parameters.get('enable_deduplication'):
            quote['deduplication'] = self.parameters.get('enable_deduplication')
        if self.parameters.get('enable_thin_provisioning'):
            quote['thinProvisioning'] = self.parameters.get('enable_thin_provisioning')
        if self.parameters.get('enable_compression'):
            quote['compression'] = self.parameters.get('enable_compression')
        if self.parameters.get('export_policy_type'):
            quote['exportPolicyInfo']['policyType'] = self.parameters['export_policy_type']
        if self.parameters.get('export_policy_ip'):
            quote['exportPolicyInfo']['ips'] = self.parameters['export_policy_ip']
        if self.parameters.get('export_policy_nfs_version'):
            quote['exportPolicyInfo']['nfsVersion'] = self.parameters['export_policy_nfs_version']
        if self.parameters.get('snapshot_policy_name'):
            quote['snapshotPolicy'] = self.parameters['snapshot_policy_name']
        if self.parameters.get('capacity_tier') and self.parameters['capacity_tier'] != "NONE":
            quote['capacityTier'] = self.parameters['capacity_tier']
        if self.parameters.get('tiering_policy'):
            quote['tieringPolicy'] = self.parameters['tiering_policy']
        if self.parameters.get('provider_volume_type'):
            quote['providerVolumeType'] = self.parameters['provider_volume_type']
        if self.parameters.get('iops'):
            quote['iops'] = self.parameters.get('iops')
        response, err = self.rest_api.send_request("POST", "%s/volumes?createAggregateIfNotFound=%s" % (
            self.rest_api.api_root_path, True), None, quote, header=headers)
        if err is not None:
            self.module.fail_json(changed=False, msg=err)

    def modify_volume(self, modify):
        headers = {
            'X-Agent-Id': self.parameters['client_id'] + "clients"
        }
        vol = dict()
        export_policy_info = dict()
        if self.parameters.get('export_policy_type'):
            export_policy_info['policyType'] = self.parameters['export_policy_type']
        if self.parameters.get('export_policy_ip'):
            export_policy_info['ips'] = self.parameters['export_policy_ip']
        if self.parameters.get('export_policy_nfs_version'):
            export_policy_info['nfsVersion'] = self.parameters['export_policy_nfs_version']
        vol['exportPolicyInfo'] = export_policy_info
        if modify.get('snapshot_policy_name'):
            vol['snapshotPolicyName'] = self.parameters.get('snapshot_policy_name')
        dummy, err = self.rest_api.send_request("PUT", "%s/volumes/%s/%s/%s" % (
            self.rest_api.api_root_path, self.parameters['working_environment_id'], self.parameters['svm_name'],
            self.parameters['name']), None, vol, header=headers)
        if err is not None:
            self.module.fail_json(changed=False, msg=err)

    def delete_volume(self):
        headers = {
            'X-Agent-Id': self.parameters['client_id'] + "clients"
        }
        dummy, err = self.rest_api.send_request("DELETE", "%s/volumes/%s/%s/%s" % (
            self.rest_api.api_root_path, self.parameters['working_environment_id'], self.parameters['svm_name'],
            self.parameters['name']), None, None, header=headers)
        if err is not None:
            self.module.fail_json(changed=False, msg=err)

    def apply(self):
        current = self.get_volume()
        cd_action, modify = None, None
        cd_action = self.na_helper.get_cd_action(current, self.parameters)
        if cd_action is None:
            modify = self.na_helper.get_modified_attributes(current, self.parameters)
            unmodifiable = []
            for attr in modify:
                if attr not in ['export_policy_ip', 'export_policy_nfs_version', 'snapshot_policy_name']:
                    unmodifiable.append(attr)
            if len(unmodifiable) > 0:
                self.module.fail_json(changed=False, msg="%s can't be modified." % str(unmodifiable))
        if self.na_helper.changed and not self.module.check_mode:
            if cd_action == 'create':
                self.create_volume()
            elif cd_action == 'delete':
                self.delete_volume()
            elif modify:
                self.modify_volume(modify)
        self.module.exit_json(changed=self.na_helper.changed)


def main():
    '''Main Function'''
    volume = NetAppCloudmanagerVolume()
    volume.apply()


if __name__ == '__main__':
    main()
