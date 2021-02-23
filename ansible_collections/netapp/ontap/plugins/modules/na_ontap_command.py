#!/usr/bin/python
'''
# (c) 2018, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
'''

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'certified'}

DOCUMENTATION = '''
author: NetApp Ansible Team (@carchi8py) <ng-ansibleteam@netapp.com>
description:
  - "Run system-cli commands on ONTAP"
  - Can't be used with cert authentication and domain authentication accounts.
  - Requires ontapi and console permissions. Console is not supported for data vservers.
extends_documentation_fragment:
  - netapp.ontap.netapp.na_ontap
module: na_ontap_command
short_description: NetApp ONTAP Run any cli command, the username provided needs to have console login permission.
version_added: 2.7.0
options:
    command:
        description:
        - a comma separated list containing the command and arguments.
        required: true
        type: list
        elements: str
    privilege:
        description:
        - privilege level at which to run the command.
        choices: ['admin', 'advanced']
        default: admin
        type: str
        version_added: 2.8.0
    return_dict:
        description:
        - Returns a parsesable dictionary instead of raw XML output
        - C(result_value)
        - C(status) > passed, failed..
        - C(stdout) > command output in plaintext)
        - C(stdout_lines) > list of command output lines)
        - C(stdout_lines_filter) > empty list or list of command output lines matching I(include_lines) or I(exclude_lines) parameters.
        type: bool
        default: false
        version_added: 2.9.0
    vserver:
        description:
        - If running as vserver admin, you must give a I(vserver) or module will fail
        version_added: "19.10.0"
        type: str
    include_lines:
        description:
        - applied only when I(return_dict) is true
        - return only lines containing string pattern in C(stdout_lines_filter)
        default: ''
        type: str
        version_added: "19.10.0"
    exclude_lines:
        description:
        - applied only when I(return_dict) is true
        - return only lines containing string pattern in C(stdout_lines_filter)
        default: ''
        type: str
        version_added: "19.10.0"
'''

EXAMPLES = """
    - name: run ontap cli command
      na_ontap_command:
        hostname: "{{ hostname }}"
        username: "{{ admin username }}"
        password: "{{ admin password }}"
        command: ['version']

    # Same as above, but returns parseable dictonary
    - name: run ontap cli command
      na_ontap_command:
        hostname: "{{ hostname }}"
        username: "{{ admin username }}"
        password: "{{ admin password }}"
        command: ['node', 'show', '-fields', 'node,health,uptime,model']
        privilege: 'admin'
        return_dict: true

    # Same as above, but with lines filtering
    - name: run ontap cli command
      na_ontap_command:
        hostname: "{{ hostname }}"
        username: "{{ admin username }}"
        password: "{{ admin password }}"
        command: ['node', 'show', '-fields', 'node,health,uptime,model']
        exlude_lines: 'ode ' # Exclude lines with 'Node ' or 'node'
        privilege: 'admin'
        return_dict: true
"""

RETURN = """
"""

import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
import ansible_collections.netapp.ontap.plugins.module_utils.netapp as netapp_utils

HAS_NETAPP_LIB = netapp_utils.has_netapp_lib()


class NetAppONTAPCommand(object):
    ''' calls a CLI command '''

    def __init__(self):
        self.argument_spec = netapp_utils.na_ontap_host_argument_spec()
        self.argument_spec.update(dict(
            command=dict(required=True, type='list', elements='str'),
            privilege=dict(required=False, type='str', choices=['admin', 'advanced'], default='admin'),
            return_dict=dict(required=False, type='bool', default=False),
            vserver=dict(required=False, type='str'),
            include_lines=dict(required=False, type='str', default=''),
            exclude_lines=dict(required=False, type='str', default=''),
        ))
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True
        )
        parameters = self.module.params
        # set up state variables
        self.command = parameters['command']
        self.privilege = parameters['privilege']
        self.vserver = parameters['vserver']
        self.return_dict = parameters['return_dict']
        self.include_lines = parameters['include_lines']
        self.exclude_lines = parameters['exclude_lines']

        self.result_dict = dict()
        self.result_dict['status'] = ""
        self.result_dict['result_value'] = 0
        self.result_dict['invoked_command'] = " ".join(self.command)
        self.result_dict['stdout'] = ""
        self.result_dict['stdout_lines'] = []
        self.result_dict['stdout_lines_filter'] = []
        self.result_dict['xml_dict'] = dict()

        if HAS_NETAPP_LIB is False:
            self.module.fail_json(msg="the python NetApp-Lib module is required")
        else:
            self.server = netapp_utils.setup_na_ontap_zapi(module=self.module, wrap_zapi=True)

    def asup_log_for_cserver(self, event_name):
        """
        Fetch admin vserver for the given cluster
        Create and Autosupport log event with the given module name
        :param event_name: Name of the event log
        :return: None
        """
        results = netapp_utils.get_cserver(self.server)
        cserver = netapp_utils.setup_na_ontap_zapi(module=self.module, vserver=results)
        try:
            netapp_utils.ems_log_event(event_name, cserver)
        except netapp_utils.zapi.NaApiError as error:
            self.module.fail_json(msg='Cluster Admin required if -vserver is not passed %s: %s' %
                                  (self.command, to_native(error)),
                                  exception=traceback.format_exc())

    def run_command(self):
        ''' calls the ZAPI '''
        self.ems()
        command_obj = netapp_utils.zapi.NaElement("system-cli")

        args_obj = netapp_utils.zapi.NaElement("args")
        for arg in self.command:
            args_obj.add_new_child('arg', arg)
        command_obj.add_child_elem(args_obj)
        command_obj.add_new_child('priv', self.privilege)

        try:
            output = self.server.invoke_successfully(command_obj, True)
            if self.return_dict:
                # Parseable dict output
                retval = self.parse_xml_to_dict(output.to_string())
            else:
                # Raw XML output
                retval = output.to_string()

            return retval
        except netapp_utils.zapi.NaApiError as error:
            self.module.fail_json(msg='Error running command %s: %s' %
                                  (self.command, to_native(error)),
                                  exception=traceback.format_exc())

    def ems(self):
        """
        Error out if Cluster Admin username is used with Vserver, or Vserver admin used with out vserver being set
        :return:
        """
        if self.vserver:
            ems_server = netapp_utils.setup_na_ontap_zapi(module=self.module, vserver=self.vserver)
            try:
                netapp_utils.ems_log_event("na_ontap_command" + str(self.command), ems_server)
            except netapp_utils.zapi.NaApiError as error:
                self.module.fail_json(msg='Vserver admin required if -vserver is given %s: %s' %
                                          (self.command, to_native(error)),
                                      exception=traceback.format_exc())
        else:
            self.asup_log_for_cserver("na_ontap_command: " + str(self.command))

    def apply(self):
        ''' calls the command and returns raw output '''
        changed = True
        output = self.run_command()
        self.module.exit_json(changed=changed, msg=output)

    def parse_xml_to_dict(self, xmldata):
        '''Parse raw XML from system-cli and create an Ansible parseable dictonary'''
        xml_import_ok = True
        xml_parse_ok = True

        try:
            importing = 'ast'
            import ast
            importing = 'xml.parsers.expat'
            import xml.parsers.expat
        except ImportError:
            self.result_dict['status'] = "XML parsing failed. Cannot import %s!" % importing
            self.result_dict['stdout'] = str(xmldata)
            self.result_dict['result_value'] = -1
            xml_import_ok = False

        if xml_import_ok:
            xml_str = xmldata.decode('utf-8').replace('\n', '---')
            xml_parser = xml.parsers.expat.ParserCreate()
            xml_parser.StartElementHandler = self._start_element
            xml_parser.CharacterDataHandler = self._char_data
            xml_parser.EndElementHandler = self._end_element

            try:
                xml_parser.Parse(xml_str)
            except xml.parsers.expat.ExpatError as errcode:
                self.result_dict['status'] = "XML parsing failed: " + str(errcode)
                self.result_dict['stdout'] = str(xmldata)
                self.result_dict['result_value'] = -1
                xml_parse_ok = False

            if xml_parse_ok:
                self.result_dict['status'] = self.result_dict['xml_dict']['results']['attrs']['status']
                stdout_string = self._format_escaped_data(self.result_dict['xml_dict']['cli-output']['data'])
                self.result_dict['stdout'] = stdout_string
                # Generate stdout_lines list
                for line in stdout_string.split('\n'):
                    stripped_line = line.strip()
                    if len(stripped_line) > 1:
                        self.result_dict['stdout_lines'].append(stripped_line)

                        # Generate stdout_lines_filter_list
                        if self.exclude_lines:
                            if self.include_lines in stripped_line and self.exclude_lines not in stripped_line:
                                self.result_dict['stdout_lines_filter'].append(stripped_line)
                        else:
                            if self.include_lines and self.include_lines in stripped_line:
                                self.result_dict['stdout_lines_filter'].append(stripped_line)

                self.result_dict['xml_dict']['cli-output']['data'] = stdout_string
                cli_result_value = self.result_dict['xml_dict']['cli-result-value']['data']
                try:
                    # get rid of extra quotes "'1'", but maybe "u'1'" or "b'1'"
                    cli_result_value = ast.literal_eval(cli_result_value)
                except (SyntaxError, ValueError):
                    pass
                try:
                    self.result_dict['result_value'] = int(cli_result_value)
                except ValueError:
                    self.result_dict['result_value'] = cli_result_value

        return self.result_dict

    def _start_element(self, name, attrs):
        ''' Start XML element '''
        self.result_dict['xml_dict'][name] = dict()
        self.result_dict['xml_dict'][name]['attrs'] = attrs
        self.result_dict['xml_dict'][name]['data'] = ""
        self.result_dict['xml_dict']['active_element'] = name
        self.result_dict['xml_dict']['last_element'] = ""

    def _char_data(self, data):
        ''' Dump XML elemet data '''
        self.result_dict['xml_dict'][str(self.result_dict['xml_dict']['active_element'])]['data'] = repr(data)

    def _end_element(self, name):
        self.result_dict['xml_dict']['last_element'] = name
        self.result_dict['xml_dict']['active_element'] = ""

    @classmethod
    def _format_escaped_data(cls, datastring):
        ''' replace helper escape sequences '''
        formatted_string = datastring.replace('------', '---').replace('---', '\n').replace("###", "    ").strip()
        retval_string = ""
        for line in formatted_string.split('\n'):
            stripped_line = line.strip()
            if len(stripped_line) > 1:
                retval_string += stripped_line + "\n"
        return retval_string


def main():
    """
    Execute action from playbook
    """
    command = NetAppONTAPCommand()
    command.apply()


if __name__ == '__main__':
    main()
