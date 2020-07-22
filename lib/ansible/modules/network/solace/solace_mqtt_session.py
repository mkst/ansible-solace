#!/usr/bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
# Copyright (c) 2020, Solace Corporation, Swen-Helge Huber <swen-helge.huber@solace.com
# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ---------------------------------------------------------------------------------------------

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

import ansible.module_utils.network.solace.solace_utils as su
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: solace_mqtt_session

short_description: Configure a MQTT Session object.

version_added: "2.9.10"

description:
- "Configure a MQTT Session object. Allows addition, removal and update of a MQTT Session object in an idempotent manner."
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/mqttSession)."

options:
  name:
    description: The MQTT session client id. Maps to 'mqttSessionClientId' in the API.
    type: str
    required: true
    aliases: [mqtt_session_client_id]

extends_documentation_fragment:
- solace.broker
- solace.vpn
- solace.virtual_router
- solace.settings
- solace.state

author:
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''
    - name: Create Mqtt Session
      solace_mqtt_session:
        name: "{{ mqtt_session_client_id }}"
        settings:
          enabled: false
          owner: "{{ mqtt_client_username }}"
        state: present

    - name: Update Mqtt Session
      # skip task if version not correct
      solace_mqtt_session:
        name: "{{ mqtt_session_client_id }}"
        settings:
          queueMaxMsgSize: 300000
          queueMaxBindCount: 30
        state: present
      when: ansible_facts['solace']['about']['api']['sempVersion'] | float >= 2.14

    - name: Delete Mqtt Session
      solace_mqtt_session:
        name: "{{ mqtt_session_client_id }}"
        state: absent

'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
'''


class SolaceMqttSessionTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'mqttSessionClientId'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['virtual_router']]

    def lookup_item(self):
        return self.module.params['name']

    def get_func(self, solace_config, vpn, virtual_router, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}
        uri_ext = ','.join([lookup_item_value, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.MQTT_SESSIONS, uri_ext]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, virtual_router, mqtt_session_client_id, settings=None):
        # POST /msgVpns/{msgVpnName}/mqttSessions
        defaults = {
            'msgVpnName': vpn,
            'mqttSessionVirtualRouter': virtual_router
        }
        mandatory = {
            self.LOOKUP_ITEM_KEY: mqtt_session_client_id
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.MQTT_SESSIONS]
        return su.make_post_request(solace_config, path_array, data)

    def update_func(self, solace_config, vpn, virtual_router, lookup_item_value, settings=None):
        # PATCH /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}
        uri_ext = ','.join([lookup_item_value, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.MQTT_SESSIONS, uri_ext]
        return su.make_patch_request(solace_config, path_array, settings)

    def delete_func(self, solace_config, vpn, virtual_router, lookup_item_value):
        # DELETE /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}
        uri_ext = ','.join([lookup_item_value, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.MQTT_SESSIONS, uri_ext]
        return su.make_delete_request(solace_config, path_array, None)


def run_module():
    """Entrypoint to module"""

    """Compose module arguments"""
    module_args = dict(
        name=dict(type='str', aliases=['mqtt_session_client_id'], required=True)
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_virtual_router())
    arg_spec.update(su.arg_spec_crud())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceMqttSessionTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
