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

# Code of Conduct
This collection follows the [Ansible project's Code of Conduct](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html).

# Need help
Join our Slack Channel at [Netapp.io](http://netapp.io/slack)

# Release Notes

## 21.5.0

### Minor changes
- minor changes to meet Red Hat requirements to be certified.

## 20.7.0

### Minor changes
- na_um_list_aggregates: Now sort by performance_capacity.used
- na_um_list_nodes: Now sort by performance_capacity.used

## 20.6.0

### New Modules
- na_um_list_volumes: list volumes.

## 20.5.0

### New Modules
- na_um_list_aggregates: list aggregates.
- na_um_list_clusters: list clusters.
- na_um_list_nodes: list nodes.
- na_um_list_svms: list svms.
