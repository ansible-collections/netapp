# Ansible Collection - netapp.cloudmanager

Copyright (c) 2021 NetApp, Inc. All rights reserved.
Specifications subject to change without notice.

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

# Release Notes

# Code of Conduct
This collection follows the [Ansible project's Code of Conduct](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html).

# Documentation
https://github.com/ansible-collections/netapp/wiki

## 21.4.0

### Module documentation changes
  - Remove the period at the end of the line on short_description
  - Add period at the end of the names in examples
  - Add notes mentioning support check_mode

### New Modules
  - na_cloudmanager_info: Gather Cloud Manager subset information using REST APIs. Support for subsets `working_environments_info`, `aggregates_info`, `accounts_info`.

## 21.3.0

### New Modules
  - na_cloudmanager_aggregate: Create or delete an aggregate on Cloud Volumes ONTAP, or add disks on an aggregate.
  - na_cloudmanager_cifs_server: Create or delete CIFS server for Cloud Volumes ONTAP.
  - na_cloudmanager_connector_aws: Create or delete Cloud Manager connector for AWS.
  - na_cloudmanager_cvo_aws: Create or delete Cloud Manager CVO for AWS for both single and HA.
  - na_cloudmanager_nss_account: Create or delete a nss account on Cloud Manager.
  - na_cloudmanager_volume: Create, modify or delete a volume on Cloud Volumes ONTAP.

