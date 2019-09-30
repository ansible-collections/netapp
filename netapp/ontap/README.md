=============================================================

 netapp.ontap

 NetApp ONTAP Collection

 Copyright (c) 2019 NetApp, Inc. All rights reserved.
 Specifications subject to change without notice.

=============================================================


## 19.10.0
### New Modules
- na_ontap_name_service_switch: create/modify/delete name service switch configuration.
### New Options
- na_ontap_command: `vserver`: to allow command to run as either cluster admin or vserver admin.  To run as vserver admin you must use the vserver option.
### Bug Fixes
- na_ontap_qtree: REST API takes "unix_permissions" as parameter instead of "mode".
- na_ontap_user: minor documentation update for application parameter.
