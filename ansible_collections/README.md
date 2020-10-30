# NetApp Ansible Collections

There are currently 6 NetApp Collections
* [ONTAP](https://galaxy.ansible.com/netapp/ontap)
* [ElementSW (Solidfire)](https://galaxy.ansible.com/netapp/elementsw)
* [ANF for Azure](https://galaxy.ansible.com/netapp/azure)
* [CVS for AWS](https://galaxy.ansible.com/netapp/aws)
* [UM info for ONTAP](https://galaxy.ansible.com/netapp/um_info)
* [StorageGRID](https://galaxy.ansible.com/netapp/storagegrid)

## Requirements
- ansible version >= 2.9
- requests >= 2.20
- only for ONTAP
  - netapp-lib version >= 2018.11.13
- only for ElementSW, or when using ONTAP SnapMirror with ElementSW
  - solidfire-sdk-python >= 1.5.0.87

## Installation
### Ontap
```bash
ansible-galaxy collection install netapp.ontap
```
### ElementSW
```bash
ansible-galaxy collection install netapp.elementsw
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
### StorageGRID
```bash
ansible-galaxy collection install netapp.storagegrid
```

## Update History
[Ontap](https://github.com/ansible/ansible_collections_netapp/blob/master/ansible_collections/netapp/ontap/README.md)

[ElementSW](https://github.com/ansible-collections/ansible_collections_netapp/blob/master/ansible_collections/netapp/elementsw/README.md)

[ANF for Azure](https://github.com/ansible-collections/ansible_collections_netapp/blob/master/ansible_collections/netapp/azure/README.md)

[CVS for AWS](https://github.com/ansible-collections/ansible_collections_netapp/blob/master/ansible_collections/netapp/aws/README.md)

[UM info for ONTAP](https://github.com/ansible-collections/ansible_collections_netapp/blob/master/ansible_collections/netapp/um_info/README.md)

[StorageGRID](https://github.com/ansible-collections/ansible_collections_netapp/blob/master/ansible_collections/netapp/storagegrid/README.md)

## Resource Supported
