# NetApp Ansible Collections

As of May 10, 2021, after releasing 21.6.0 for four collections, we discontinued and archived ansible-collections/netapp repository.

It is being replaced with 7 new repositories, one for each collection

* ansible-collections/netapp.azure
* ansible-collections/netapp.aws
* ansible-collections/netapp.cloudmanager
* ansible-collections/netapp.elementsw
* ansible-collections/netapp.ontap
* ansible-collections/netapp.storagegrid
* ansible-collections/netapp.um_info

This meets a requirement from Red Hat that each repository hosts a single collection, and it makes it easier to version and publish each collection independently.

This is also part of a move to fully comply with semantic versioning

There are currently 7 NetApp Collections
* [ONTAP](https://galaxy.ansible.com/netapp/ontap)
  * over 100 modules to support ONTAP configuration.
* [CloudManager](https://galaxy.ansible.com/netapp/cloudmanager)
  * new modules to create a connector, single or HA CVO instances, aggregates, volumes, CIFS server, NSS accounts, iSCSI igroups/initiators.
  * new info module to gather information about accounts, working_environments, aggregates. 
  * modules for connector and CVO support AWS, Azure, and GCP.  Modules are specialized for each cloud provider.
  * modules for aggregates and volumes support AWS, Azure, and GCP.
  * In addition, a [Terraform provider for CloudManager](https://registry.terraform.io/providers/NetApp/netapp-cloudmanager/latest) already supports all of the above on the 3 clouds.
* [ANF for Azure](https://galaxy.ansible.com/netapp/azure)
  * Azure NetApp Files on Azure - accounts, resource pools, volumes, snapshots.
* [CVS for AWS](https://galaxy.ansible.com/netapp/aws)
  * Cloud Volumes Service on AWS - AD, pools, volumes (filesystems), snapshots.
* [UM info for ONTAP](https://galaxy.ansible.com/netapp/um_info)
  * Retrieve information about ONTAP systems from Unified Manager - clusters, nodes, aggregates, svms, volumes.
* [ElementSW (SolidFire)](https://galaxy.ansible.com/netapp/elementsw)
  * modules to support ElementSW configuration on SolidFire and HCI systems.
* [StorageGRID](https://galaxy.ansible.com/netapp/storagegrid)
  * modules to support StorageGRID configuration.

## Versioning
[Releasing, Versioning and Deprecation](https://github.com/ansible-collections/netapp/issues/93)

## Requirements
- ansible version >= 2.9
- requests >= 2.20
- only for ONTAP
  - netapp-lib version >= 2018.11.13
  - six
- only for ElementSW, or when using ONTAP SnapMirror with ElementSW
  - solidfire-sdk-python >= 1.5.0.87
- check the `requirements.txt` file provided with the collection as of 21.3.0 for a detailed list.

## Installation
### ONTAP
```bash
ansible-galaxy collection install netapp.ontap
```
### CloudManager
```bash
ansible-galaxy collection install netapp.cloudmanager
```
### ANF for Azure
```bash
ansible-galaxy collection install netapp.azure
```
### CVS for AWS
```bash
ansible-galaxy collection install netapp.aws
```
### UM info for ONTAP
```bash
ansible-galaxy collection install netapp.um_info
```
### ElementSW
```bash
ansible-galaxy collection install netapp.elementsw
```
### StorageGRID
```bash
ansible-galaxy collection install netapp.storagegrid
```

## Installation in a closed environment
https://github.com/ansible-collections/netapp.ontap/wiki/NetApp-ONTAP-Ansible-Collection
https://github.com/ansible-collections/netapp.ontap/wiki/NetApp-ONTAP-Ansible-Collection---installing-from-GitHub

## Automation Hub
The collections that are certified are also available in Red Hat Automation Hub if you have a subscription.

## Source code
As of 21.6.0 (May 7, 2021), the common repository for the 7 collections as been split into 7 new repositories, one for each collection:

[ONTAP](https://github.com/ansible-collections/netapp.ontap)

[CloudManager](https://github.com/ansible-collections/netapp.cloudmanager)

[ANF for Azure](https://github.com/ansible-collections/netapp.azure)

[CVS for AWS](https://https://github.com/ansible-collections/netapp.aws)

[UM info for ONTAP](https://github.com/ansible-collections/netapp.um_info)

[ElementSW](https://github.com/ansible-collections/netapp.elementsw)

[StorageGRID](https://github.com/ansible-collections/netapp.storagegrid)

## Resource Supported
See https://docs.ansible.com/ansible/latest/collections/ for documentation.

# Need help
Join our Slack Channel at [Netapp.io](http://netapp.io/slack)
