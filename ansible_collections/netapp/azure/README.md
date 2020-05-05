=============================================================

netapp.azure

Azure NetApp Files (ANF) Collection

Copyright (c) 2019 NetApp, Inc. All rights reserved.
Specifications subject to change without notice.

=============================================================

# Installation
```bash
ansible-galaxy collection install netapp.azure
```
To use Collection add the following to the top of your playbook, with out this you will be using Ansible 2.9 version of the module
```  
collections:
  - netapp.azure
```
# Need help
Join our Slack Channel at [Netapp.io](http://netapp.io/slack)

# Requirements
- python >= 2.7
- azure >= 2.0.0
- Python azure-mgmt. Install using ```pip install azure-mgmt```
- Python azure-mgmt-netapp. Install using ```pip install azure-mgmt-netapp```
- For authentication with Azure NetApp log in before you run your tasks or playbook with 'az login'.

# Release Notes

## 20.5.0

### New Options
- azure_rm_netapp_account: new option `tags`.
- azure_rm_netapp_capacity_pool: new option `service_level`.
- azure_rm_netapp_volume: new option `size`.
- azure_rm_netapp_volume: now returns mount_path of the volume specified.

## 20.4.0

### Bug Fixes
- fix changes to azure-mgmt-netapp as per new release.
- removed ONTAP dependency import.

## 20.2.0

### Bug Fixes
- galaxy.yml: fix path to github repository.

## 19.11.0
- Initial release.
### New Modules
- azure_rm_netapp_account: create/delete NetApp Azure Files Account.
- azure_rm_netapp_capacity_pool: create/delete NetApp Azure Files capacity pool.
- azure_rm_netapp_snapshot: create/delete NetApp Azure Files Snapshot.
- azure_rm_netapp_volume: create/delete NetApp Azure Files volume.
