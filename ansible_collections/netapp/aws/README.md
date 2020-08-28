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


## 20.9.0

Fix pylint or flake8 warnings reported by galaxy importer.

## 20.8.0

### Module documentation changes
- use a three group format for `version_added`.  So 2.7 becomes 2.7.0.  Same thing for 2.8 and 2.9.
- add `elements:` and update `required:` to match module requirements.

## 20.6.0

### Bug Fixes
- galaxy.xml: fix repository and homepage links.

## 20.2.0

### Bug Fixes
- galaxy.yml: fix path to github repository.

## 19.11.0
- Initial release as a collection.
