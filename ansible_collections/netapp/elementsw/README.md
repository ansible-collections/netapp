netapp.elementSW

NetApp ElementSW Collection

Copyright (c) 2019 NetApp, Inc. All rights reserved.
Specifications subject to change without notice.

# Installation
```bash
ansible-galaxy collection install netapp.elementsw
```
To use Collection add the following to the top of your playbook, with out this you will be using Ansible 2.9 version of the module
```
collections:
  - netapp.elementsw
```
# Need help
Join our Slack Channel at [Netapp.io](http://netapp.io/slack)

# Release Notes

## 20.10.0

### New Modules
- na_elementsw_info: support for two subsets `cluster_accounts`, `node_config`.

### New Options
- na_elementsw_cluster: `encryption` to enable encryption at rest.  `order_number` and `serial_number` for demo purposes.
- na_elementsw_network_interfaces: restructure options, into 2 dictionaries `bond_1g` and `bond_10g`, so that there is no shared option.  Disallow all older options.
- na_elementsw_network_interfaces: make all options not required, so that only bond_1g can be set for example.

## 20.9.1

### Bug Fixes
- na_elementsw_node: improve error reporting when cluster name cannot be set because node is already active.
- na_elementsw_schedule - missing imports TimeIntervalFrequency, Schedule, ScheduleInfo have been added back

## 20.9.0

### New Modules
- na_elementsw_qos_policy: create, modify, rename, or delete QOS policy.

### New Options
- na_elementsw_node: `cluster_name` to set the cluster name on new nodes.
- na_elementsw_node: `preset_only` to only set the cluster name before creating a cluster with na_elementsw_cluster.
- na_elementsw_volume: `qos_policy_name` to provide a QOS policy name or ID.

### Bug Fixes
- na_elementsw_node: fix check_mode so that no action is taken.

## 20.8.0

### New Options
- na_elementsw_drive: add all drives in a cluster, allow for a list of nodes or a list of drives.

### Bug Fixes
- na_elementsw_access_group: fix check_mode so that no action is taken.
- na_elementsw_admin_users: fix check_mode so that no action is taken.
- na_elementsw_cluster: create cluster if it does not exist.  Do not expect MVIP or SVIP to exist before create.
- na_elementsw_cluster_snmp: double exception because of AttributeError.
- na_elementsw_drive: node_id or drive_id were not handled properly when using numeric ids.
- na_elementsw_initiators: volume_access_group_id was ignored.  volume_access_groups was ignored and redundant.
- na_elementsw_ldap: double exception because of AttributeError.
- na_elementsw_snapshot_schedule: ignore schedules being deleted (idempotency), remove default values and fix documentation.
- na_elementsw_vlan: AttributeError if VLAN already exists.
- na_elementsw_vlan: fix check_mode so that no action is taken.
- na_elementsw_vlan: change in attributes was ignored.
- na_elementsw_volume: double exception because of AttributeError.
- na_elementsw_volume: Argument '512emulation' in argument_spec is not a valid python identifier - renamed to enable512emulation.

### Module documentation changes
- use a three group format for `version_added`.  So 2.7 becomes 2.7.0.  Same thing for 2.8 and 2.9.
- add type: str (or int, dict) where missing in documentation section.
- add required: true where missing.
- remove required: true for state and use present as default.

## 20.6.0
### Bug Fixes
- galaxy.xml: fix repository and homepage links

## 20.2.0
### Bug Fixes
- galaxy.yml: fix path to github repository.
- netapp.py: report error in case of connection error rather than raising a generic exception by default.

## 20.1.0
### New Module
- na_elementsw_access_group_volumes: add/remove volumes to/from existing access group

## 19.11.0
## 19.10.0
Changes in 19.10.0 and September collection releases compared to Ansible 2.9
### Documentation Fixes:
- na_elementsw_drive: na_elementsw_drive was documented as na_element_drive
