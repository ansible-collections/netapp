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

## 21.3.0

### New Modules

  - na_cloudmanager_aggregate: Create or delete an aggregate on Cloud Volumes ONTAP, or add disks on an aggregate.
  - na_cloudmanager_cifs_server: Create or delete CIFS server for Cloud Volumes ONTAP.
  - na_cloudmanager_connector_aws: Create or delete Cloud Manager connector for AWS.
  - na_cloudmanager_cvo_aws: Create or delete Cloud Manager CVO for AWS for both single and HA.
  - na_cloudmanager_volume: Create or delete a volume on Cloud Volumes ONTAP.
