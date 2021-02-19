# -*- coding: utf-8 -*-

# Copyright: (c) 2021, NetApp Ansible Team <ng-ansibleteam@netapp.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


class ModuleDocFragment(object):
    # Documentation fragment for CLOUDMANAGER
    CLOUDMANAGER = """
options:
  api_url:
    required: false
    type: str
    description:
    - The url to the cloudmanager.
  refresh_token:
    required: true
    type: str
    description:
    - The refresh token for NetApp Cloud Manager API operations.
notes:
  - The modules prefixed with cloudmanager\\_netapp are built to Manage AWS/GCP/Azure CLOUDMANAGER.
"""
