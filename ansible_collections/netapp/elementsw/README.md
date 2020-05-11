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
                                         
#Release Notes

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
