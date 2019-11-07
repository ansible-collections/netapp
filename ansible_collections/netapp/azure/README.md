=============================================================

netapp.azure

Azure NetApp Files (ANF) Collection

Copyright (c) 2019 NetApp, Inc. All rights reserved.
Specifications subject to change without notice.

=============================================================

## Requirements
- python >= 2.7
- azure >= 2.0.0
- Python azure-mgmt. Install using 'pip install azure-mgmt'
- Python azure-mgmt-netapp. Install using 'pip install azure-mgmt-netapp'
- For authentication with Azure NetApp log in before you run your tasks or playbook with 'az login'.

## 19.11.1

## 19.10.0
Changes in 19.10.0 and September collection releases compared to Ansible 2.9
### New Modules
- azure_rm_netapp_account: create/delete NetApp Azure Files Account.
- azure_rm_netapp_capacity_pool: create/delete NetApp Azure Files capacity pool.
- azure_rm_netapp_snapshot: create/delete NetApp Azure Files Snapshot.
- azure_rm_netapp_volume: create/delete NetApp Azure Files volume.