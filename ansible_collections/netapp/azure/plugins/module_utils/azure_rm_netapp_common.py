# (c) 2019, NetApp, Inc
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

'''
azure_rm_netapp_common
Wrapper around AzureRMModuleBase base class
'''

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

HAS_AZURE_COLLECTION = True
NEW_STYLE = None
COLLECTION_VERSION = "21.5.0"
IMPORT_ERRORS = list()

try:
    from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common import AzureRMModuleBase
except ImportError as exc:
    IMPORT_ERRORS.append(str(exc))
    from ansible_collections.netapp.azure.plugins.module_utils.netapp_module import AzureRMModuleBaseMock as AzureRMModuleBase
    HAS_AZURE_COLLECTION = False

try:
    from azure.mgmt.netapp import NetAppManagementClient                    # 1.0.0 or newer
    NEW_STYLE = True
except ImportError as exc:
    IMPORT_ERRORS.append(str(exc))
    try:
        from azure.mgmt.netapp import AzureNetAppFilesManagementClient      # 0.10.0 or older
        NEW_STYLE = False
    except ImportError as exc:
        IMPORT_ERRORS.append(str(exc))


class AzureRMNetAppModuleBase(AzureRMModuleBase):
    ''' Wrapper around AzureRMModuleBase base class '''
    def __init__(self, derived_arg_spec, supports_check_mode=False):
        self._netapp_client = None
        self._new_style = NEW_STYLE
        if not HAS_AZURE_COLLECTION:
            # we can't use self.module yet
            raise ImportError(IMPORT_ERRORS)
        super(AzureRMNetAppModuleBase, self).__init__(derived_arg_spec=derived_arg_spec,
                                                      supports_check_mode=supports_check_mode)

    def get_mgmt_svc_client(self, client_type, base_url=None, api_version=None):
        if not self._new_style:
            return super(AzureRMNetAppModuleBase, self).get_mgmt_svc_client(client_type, base_url, api_version)
        self.log('Getting management service client NetApp {0}'.format(client_type.__name__))
        self.check_client_version(client_type)

        if not base_url:
            # most things are resource_manager, don't make everyone specify
            base_url = self.azure_auth._cloud_environment.endpoints.resource_manager

        client_kwargs = dict(credential=self.azure_auth.azure_credentials, subscription_id=self.azure_auth.subscription_id, base_url=base_url)

        return client_type(**client_kwargs)

    @property
    def netapp_client(self):
        self.log('Getting netapp client')
        if self._new_style is None:
            # note that we always have at least one import error
            self.fail_when_import_errors(IMPORT_ERRORS)
        if self._netapp_client is None:
            if self._new_style:
                self._netapp_client = self.get_mgmt_svc_client(NetAppManagementClient)
            else:
                self._netapp_client = self.get_mgmt_svc_client(AzureNetAppFilesManagementClient,
                                                               base_url=self._cloud_environment.endpoints.resource_manager,
                                                               api_version='2018-05-01')
        return self._netapp_client

    @property
    def new_style(self):
        return self._new_style

    def get_method(self, category, name):
        try:
            methods = getattr(self.netapp_client, category)
        except AttributeError as exc:
            self.module.fail_json('Error: category %s not found for netapp_client: %s' % (category, str(exc)))

        if self._new_style:
            name = 'begin_' + name
        try:
            method = getattr(methods, name)
        except AttributeError as exc:
            self.module.fail_json('Error: method %s not found for netapp_client category: %s - %s' % (name, category, str(exc)))
        return method

    def fail_when_import_errors(self, import_errors, has_azure_mgmt_netapp=True):
        if has_azure_mgmt_netapp and not import_errors:
            return
        msg = ''
        if not has_azure_mgmt_netapp:
            msg = "The python azure-mgmt-netapp package is required.  "
        msg += 'Import errors: %s' % str(import_errors)
        self.module.fail_json(msg=msg)
