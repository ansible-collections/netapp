# ============================================================= #
#                                                               #
# netapp.ontap                                                  #
#                                                               #
# NetApp ONTAP Collection                                       #
#                                                               #
# Copyright (c) 2019 NetApp, Inc. All rights reserved.          #
# Specifications subject to change without notice.              #
#                                                               #
# ============================================================= #

## 19.10.0
- na_ontap_command New options: vserver this allow command to run as either cluster admin or vserver admin.
if using vserver admin you must use the vserver option
- na_ontap_name_service_switch New module: create/modify/delete name service switch configuration.