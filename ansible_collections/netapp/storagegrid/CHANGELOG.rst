===========================================
NetApp StorageGRID Collection Release Notes
===========================================

.. contents:: Topics


v20.11.0
========

Minor Changes
-------------

- na_sg_grid_account - New option ``root_access_account`` for granting initial root access permissions for the tenant to an existing federated group

New Modules
-----------

- netapp.storagegrid.na_sg_grid_info - NetApp StorageGRID Grid information gatherer
- netapp.storagegrid.na_sg_org_info - NetApp StorageGRID Org information gatherer

v20.10.0
========

Minor Changes
-------------

- na_sg_grid_account - new option ``update_password`` for managing Tenant Account root password changes.
- na_sg_grid_user - new option ``password`` and ``update_password`` for setting or updating Grid Admin User passwords.
- na_sg_org_user - new option ``password`` and ``update_password`` for setting or updating Tenant User passwords.

Breaking Changes / Porting Guide
--------------------------------

- This version introduces a breaking change.
  All modules have been renamed from ``nac_sg_*`` to ``na_sg_*``.
  Playbooks and Roles must be updated to match.

Bugfixes
--------

- na_sg_grid_account - added ``no_log`` flag to password fields.
- na_sg_grid_account - fixed documentation issue.
- na_sg_grid_group - fixed group name parsing.
- na_sg_org_group - fixed group name parsing.

v20.6.1
=======

Minor Changes
-------------

- Fixed documentation issue in README.md

Bugfixes
--------

- nac_sg_org_container - fixed documentation issue.

v20.6.0
=======

New Modules
-----------

- netapp.storagegrid.nac_sg_grid_account - NetApp StorageGRID Manage Tenant account.
- netapp.storagegrid.nac_sg_grid_dns - NetApp StorageGRID Manage Grid DNS servers.
- netapp.storagegrid.nac_sg_grid_group - NetApp StorageGRID Manage Grid admin group.
- netapp.storagegrid.nac_sg_grid_ntp - NetApp StorageGRID Manage Grid NTP servers.
- netapp.storagegrid.nac_sg_grid_regions - NetApp StorageGRID Manage Grid Regions.
- netapp.storagegrid.nac_sg_grid_user - NetApp StorageGRID Manage Grid admin user.
- netapp.storagegrid.nac_sg_org_container - NetApp StorageGRID Manage S3 bucket.
- netapp.storagegrid.nac_sg_org_group - NetApp StorageGRID Manage Tenant group.
- netapp.storagegrid.nac_sg_org_user - NetApp StorageGRID Manage Tenant user.
- netapp.storagegrid.nac_sg_org_user_s3_key - NetApp StorageGRID Manage S3 key.
