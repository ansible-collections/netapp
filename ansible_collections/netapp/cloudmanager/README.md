# Ansible Collection - netapp.cloudmanager

Copyright (c) 2021 NetApp, Inc. All rights reserved.
Specifications subject to change without notice.

This collection requires python 3.5 or better.

# Installation
```bash
ansible-galaxy collection install netapp.cloudmanager
```
To use this collection, add the following to the top of your playbook:
```
collections:
  - netapp.cloudmanager
```
# Requirements
- ansible version >= 2.9
- requests >= 2.20

# Need help
Join our Slack Channel at [Netapp.io](http://netapp.io/slack)

# Code of Conduct
This collection follows the [Ansible project's Code of Conduct](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html).

# Documentation
https://github.com/ansible-collections/netapp/wiki

# Release Notes

## 21.5.1

### Bug fixes
  - na_cloudmanager_cifs_server: Fix incorrect API call when is_workgroup is true

## 21.5.0

### New Options
  - na_cloudmanager_connector_aws: Return newly created Azure client ID in cloud manager, instance ID and account ID. New option `proxy_certificates`.
  - na_cloudmanager_cvo_aws: Return newly created AWS working_environment_id
  - na_cloudmanager_cvo_azure: Return newly created AZURE working_environment_id
  - na_cloudmanager_cvo_gcp: Return newly created GCP working_environment_id

## Bug Fixes
  - na_cloudmanager_cvo_aws: Fix incorrect placement of platformSerialNumber in the resulting json structure

## 21.4.0

### Module documentation changes
  - Remove the period at the end of the line on short_description
  - Add period at the end of the names in examples
  - Add notes mentioning support check_mode

### New Modules
  - na_cloudmanager_connector_azure: Create or delete Cloud Manager connector for Azure.
  - na_cloudmanager_cvo_azure: Create or delete Cloud Manager CVO for AZURE for both single and HA.
  - na_cloudmanager_info: Gather Cloud Manager subset information using REST APIs. Support for subsets `working_environments_info`, `aggregates_info`, `accounts_info`.
  - na_cloudmanager_connector_gcp: Create or delete Cloud Manager connector for GCP.
  - na_cloudmanager_cvo_gcp: Create or delete Cloud Manager CVO for GCP for both single and HA.

## 21.3.0

### New Modules
  - na_cloudmanager_aggregate: Create or delete an aggregate on Cloud Volumes ONTAP, or add disks on an aggregate.
  - na_cloudmanager_cifs_server: Create or delete CIFS server for Cloud Volumes ONTAP.
  - na_cloudmanager_connector_aws: Create or delete Cloud Manager connector for AWS.
  - na_cloudmanager_cvo_aws: Create or delete Cloud Manager CVO for AWS for both single and HA.
  - na_cloudmanager_nss_account: Create or delete a nss account on Cloud Manager.
  - na_cloudmanager_volume: Create, modify or delete a volume on Cloud Volumes ONTAP.

