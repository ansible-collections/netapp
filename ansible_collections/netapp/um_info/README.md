=============================================================

 netapp.um_info

 NetApp Unified Manager(AIQUM 9.7/OCUM) Collection

 Copyright (c) 2020 NetApp, Inc. All rights reserved.
 Specifications subject to change without notice.

=============================================================
# Installation
```bash
ansible-galaxy collection install netapp.um_info
```
To use Collection add the following to the top of your playbook, with out this you will be using Ansible 2.9 version of the module
```
collections:
  - netapp.um_info
```
# Need help
Join our Slack Channel at [Netapp.io](http://netapp.io/slack)

# Release Notes

## 20.6.0

### New Modules
- na_um_list_volumes: list volumes.

## 20.5.0

### New Modules
- na_um_list_aggregates: list aggregates.
- na_um_list_clusters: list clusters.
- na_um_list_nodes: list nodes.
- na_um_list_svms: list svms.