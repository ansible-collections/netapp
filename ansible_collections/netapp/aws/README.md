=============================================================
                                                             
netapp.aws                                                   
                                                             
NetApp AWS CVS Collection                                    
                                                             
Copyright (c) 2019 NetApp, Inc. All rights reserved.         
Specifications subject to change without notice.             
                                                             
=============================================================

# Installation
```bash
ansible-galaxy collection install netapp.aws
```
To use Collection add the following to the top of your playbook, with out this you will be using Ansible 2.9 version of the module
```  
collections:
  - netapp.aws
```
# Need help
Join our Slack Channel at [Netapp.io](http://netapp.io/slack)

# Notes

These Ansible modules are supporting NetApp Cloud Volumes Service for AWS.

They require a subscription to the service and your API access keys.

The modules currently support Active Directory, Pool, FileSystem (Volume), and Snapshot services.

# Release Notes
## 19.11.0