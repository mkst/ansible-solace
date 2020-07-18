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
module: solace_bridge_remote_vpn

short_description: Configure a remote vpn on a bridge.

description:
  - "Allows addition and removal of remote vpn objects on a bridge in an idempotent manner."
  - "Reference: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/bridge/createMsgVpnBridgeRemoteMsgVpn."

options:
  name:
    description: The remote vpn name. Maps to 'remoteMsgVpnName' in the API.
    required: true
  bridge_name:
    description: The bridge.
    required: true
  virtual_router:
    description: The virtual router.
    required: true
  remote_vpn_location:
    description: The remote vpn location.
    required: true
  settings:
    description: JSON dictionary of additional configuration, see Reference documentation.
    required: false
  state:
    description: Target state. [present|absent].
    required: false
    default: present
  host:
    description: Hostname of Solace Broker.
    required: false
    default: "localhost"
  port:
    description: Management port of Solace Broker.
    required: false
    default: 8080
  msg_vpn:
    description: The message vpn.
    required: true
  secure_connection:
    description: If true, use https rather than http for querying.
    required: false
    default: false
  username:
    description: Administrator username for Solace Broker.
    required: false
    default: "admin"
  password:
    description: Administrator password for Solace Broker.
    required: false
    default: "admin"
  timeout:
    description: Connection timeout in seconds for the http request.
    required: false
    default: 1
  x_broker:
    description: Custom HTTP header with the broker virtual router id, if using a SEMPv2 Proxy/agent infrastructure.
    required: false


author:
  - Mark Street (mkst@protonmail.com)
  - Swen-Helge Huber (swen-helge.huber@solace.com)
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''
  - name: Remove Bridge Remote VPN
    solace_bridge_remote_vpn:
      name: "{{ remote_vpn }}"
      bridge_name: "{{ bridge }}"
      msg_vpn: "{{ msg_vpn }}"
      remote_vpn_location: "{{remote_vpn_location}}"
      virtual_router: "{{ virtual_router }}"
      state: absent

  - name: Add Bridge Remote VPN
    solace_bridge_remote_vpn:
      name: "{{ remote_vpn }}"
      msg_vpn: "{{ msg_vpn }}"
      bridge_name: "{{ bridge }}"
      remote_vpn_location: "{{remote_vpn_location}}"
      virtual_router: "{{ virtual_router }}"
      settings:
        enabled: false
        clientUsername: default
        password: password
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
'''


class SolaceBridgeRemoteVpnTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'remoteMsgVpnName'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['virtual_router'], self.module.params['bridge_name'], self.module.params['remote_vpn_location']]

    def lookup_item(self):
        return self.module.params['name']

    def get_func(self, solace_config, vpn, virtual_router, bridge_name, remote_vpn_location, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteMsgVpns/{remoteMsgVpnName},{remoteMsgVpnLocation},{remoteMsgVpnInterface}
        # here: omitting {remoteMsgVpnInterface}
        bridge_uri = ','.join([bridge_name, virtual_router])
        remote_vpn_uri = ','.join([lookup_item_value, remote_vpn_location]) + ','
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_REMOTE_MSG_VPNS, remote_vpn_uri]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, virtual_router, bridge_name, remote_vpn_location, remote_vpn, settings=None):
        """Create a Bridge"""
        defaults = {
            'msgVpnName': vpn,
            'remoteMsgVpnLocation': remote_vpn_location
        }
        mandatory = {
            'bridgeName': bridge_name,
            'remoteMsgVpnName': remote_vpn
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        bridge_uri = ','.join([bridge_name, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_REMOTE_MSG_VPNS]
        return su.make_post_request(solace_config, path_array, data)

    def update_func(self, solace_config, vpn, virtual_router, bridge_name, remote_vpn_location, lookup_item_value, settings=None):
        """Update an existing Bridge"""
        bridge_uri = ','.join([bridge_name, virtual_router])
        remote_vpn_uri = ','.join([lookup_item_value, remote_vpn_location])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_REMOTE_MSG_VPNS, remote_vpn_uri]
        return su.make_patch_request(solace_config, path_array, settings)

    def delete_func(self, solace_config, vpn, virtual_router, bridge_name, remote_vpn_location, lookup_item_value):
        """Delete a Bridge"""
        bridge_uri = ','.join([bridge_name, virtual_router])
        remote_vpn_uri = ','.join([lookup_item_value, remote_vpn_location])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_REMOTE_MSG_VPNS, remote_vpn_uri]
        return su.make_delete_request(solace_config, path_array, None)


def run_module():
    """Entrypoint to module"""
    module_args = dict(
        name=dict(type='str', required=True),
        bridge_name=dict(type='str', required=True),
        virtual_router=dict(type='str', required=True),
        msg_vpn=dict(type='str', required=True),
        remote_vpn_location=dict(type='str', required=True),
        host=dict(type='str', default='localhost'),
        port=dict(type='int', default=8080),
        secure_connection=dict(type='bool', default=False),
        username=dict(type='str', default='admin'),
        password=dict(type='str', default='admin', no_log=True),
        settings=dict(type='dict', require=False),
        state=dict(default='present', choices=['absent', 'present']),
        timeout=dict(default='1', require=False),
        x_broker=dict(type='str', default='')
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    solace_task = SolaceBridgeRemoteVpnTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
