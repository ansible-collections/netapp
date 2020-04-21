# (c) 2019, NetApp, Inc
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.module_utils.azure_rm_common import AzureRMModuleBase


HAS_AZURE = True


try:
    from azure.mgmt.netapp import AzureNetAppFilesManagementClient
except ImportError as exc:
    HAS_AZURE = False


class AzureRMNetAppModuleBase(AzureRMModuleBase):
    def __init__(self, derived_arg_spec, supports_check_mode=False):
        self._netapp_client = None
        super(AzureRMNetAppModuleBase, self).__init__(derived_arg_spec=derived_arg_spec,
                                                      supports_check_mode=supports_check_mode)

    @property
    def netapp_client(self):
        self.log('Getting netapp client')
        if self._netapp_client is None:
            self._netapp_client = self.get_mgmt_svc_client(AzureNetAppFilesManagementClient,
                                                           base_url=self._cloud_environment.endpoints.resource_manager,
                                                           api_version='2018-05-01')
        return self._netapp_client
