# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c) 2021, Laurent Nicolas <laurentn@netapp.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" unit tests for module_utils netapp.py

    Provides wrappers for cloudmanager REST APIs
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

# import copy     # for deepcopy
import pytest

from ansible_collections.netapp.cloudmanager.plugins.module_utils.netapp import CloudManagerRestAPI


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""


class MockModule(object):
    ''' rough mock for an Ansible module class '''
    def __init__(self):
        self.params = dict(

        )

    def fail_json(self, *args, **kwargs):  # pylint: disable=unused-argument
        """function to simulate fail_json: package return data into an exception"""
        kwargs['failed'] = True
        raise AnsibleFailJson(kwargs)


def test_missing_params():
    module = MockModule()
    with pytest.raises(KeyError) as exc:
        CloudManagerRestAPI(module)
    assert exc.match('refresh_token')
