# NetApp Ansible Collections

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
If you do not have connectivity to Galaxy in your production environment, you will need to:
- download a collection tarball in an environment with access to internet,
- move the tarball from the public environment to your private environment.  The specifics depends on your company,
- use `galaxy collection install` with the tarball file in your private environment.

There are two ways to download the collection tarball:
- CLI: `galaxy collection download <collection_path>`
- GUI: using the Ansible Galaxy web site, locate the collection of interest and click the `Download tarball` button.

### Example
```bash
ansible-galaxy collection download netapp.cloudmanager
```

Transfer file, then install it:

```bash
ansible-galaxy collection install collections/netapp-cloudmanager-21.3.0.tar.gz
```

If you see a certificate issue when accessing galaxy, you can update your certificate, or disable the security check (at your own risk!):
    `-c, --ignore-certs    Ignore SSL certificate validation errors.`

If a collection is already installed, use the `--force` option to force an update if needed.

### Reference
https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html

## Automation Hub
The collections that are certified are also available in Red Hat Automation Hub if you have a subscription.

## Update History
[ONTAP](https://github.com/ansible/ansible_collections_netapp/blob/master/ansible_collections/netapp/ontap/README.md)

[CloudManager](https://github.com/ansible/ansible_collections_netapp/blob/master/ansible_collections/netapp/cloudmanager/README.md)

[ANF for Azure](https://github.com/ansible-collections/ansible_collections_netapp/blob/master/ansible_collections/netapp/azure/README.md)

[CVS for AWS](https://github.com/ansible-collections/ansible_collections_netapp/blob/master/ansible_collections/netapp/aws/README.md)

[UM info for ONTAP](https://github.com/ansible-collections/ansible_collections_netapp/blob/master/ansible_collections/netapp/um_info/README.md)

[ElementSW](https://github.com/ansible-collections/ansible_collections_netapp/blob/master/ansible_collections/netapp/elementsw/README.md)

[StorageGRID](https://github.com/ansible-collections/ansible_collections_netapp/blob/master/ansible_collections/netapp/storagegrid/README.md)

## Resource Supported
See https://docs.ansible.com/ansible/latest/collections/ for documentation.

The documentation generation may lag, in the meantime use ansible-doc for the latest updates.  For instance:
```
  ansible-doc netapp.ontap.na_ontap_svm

  ansible-doc netapp.cloudmanager.na_cloudmanager_aggregate
```

New collections which are not yet visible on Ansible docs site are documented at:
https://github.com/ansible-collections/netapp/wiki

# Need help
Join our Slack Channel at [Netapp.io](http://netapp.io/slack)
