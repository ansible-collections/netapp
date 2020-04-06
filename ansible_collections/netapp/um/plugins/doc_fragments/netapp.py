# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Suhas Bangalore Shekar <bsuhas@netapp.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r'''
options:
  - See respective platform section for more details
requirements:
  - See respective platform section for more details
notes:
  - Ansible modules are available for the following NetApp Storage Management Platforms: AIQUM 9.7, OCUM
'''

    # Documentation fragment for AIQUM/OCUM (um)
    UM = r'''
options:
  hostname:
      description:
      - The hostname or IP address of the Unified Manager instance.
      type: str
      required: true
  username:
      description:
      - username of the Unified Manager instance.
      type: str
      required: true
  password:
      description:
      - Password for the specified user.
      type: str
      required: true
  validate_certs:
      description:
      - If set to C(False), the SSL certificates will not be validated.
      - This should only set to C(False) used on personally controlled sites using self-signed certificates.
      type: bool
      default: True
  http_port:
      description:
      - Override the default port (443) with this port
      type: int


requirements:
  - A AIQUM/OCUM 9.7 system.
  - Ansible 2.9

notes:
  - The modules prefixed with na\\_um are built to support the AIQUM/OCUM 9.7 platform.

'''
