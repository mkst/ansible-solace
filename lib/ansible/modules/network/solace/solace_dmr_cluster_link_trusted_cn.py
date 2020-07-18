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
module: solace_dmr_cluster_link_trusted_cn

short_description: Configure a trusted common name object on a DMR cluster link.

description:
  - "Allows addition, removal and configuration of trusted common name objects on DMR cluster links."
  - "Reference: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/dmrCluster/createDmrClusterLinkTlsTrustedCommonName."

options:
  name:
    description: The expected trusted common name of the remote certificate. Maps to 'tlsTrustedCommonName' in the API.
    required: true
  dmr:
    description: The name of the DMR cluster. Maps to 'dmrClusterName' in the API.
    required: true
  remote_node_name:
    description: The name of the remote node. Maps to 'remoteNodeName' in the API.
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
  - name: Remove 'remoteNode' DMR Link Trusted CN
    solace_dmr_cluster_link_trusted_cn:
      name: "*.messaging.solace.cloud"
      remote_node_name: remoteNode
      dmr: foo
      state: absent

  - name: Add 'remoteNode' DMR Link Trusted CN
    solace_dmr_cluster_link_trusted_cn:
      name: "*.messaging.solace.cloud"
      remote_node_name: remoteNode
      dmr: foo
      state: present
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
'''


class SolaceLinkTrustedCNTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'tlsTrustedCommonName'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def lookup_item(self):
        return self.module.params['name']

    def get_args(self):
        return [self.module.params['dmr'], self.module.params['remote_node_name']]

    def get_func(self, solace_config, dmr, link, lookup_item_value):
        path_array = [su.SEMP_V2_CONFIG, su.DMR_CLUSTERS, dmr, su.LINKS, link, su.TLS_TRUSTED_COMMON_NAMES, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, dmr, link, trusted_cn, settings=None):
        """Create a DMR Cluster"""
        defaults = {
            'dmrClusterName': dmr,
            'remoteNodeName': link
        }
        mandatory = {
            'tlsTrustedCommonName': trusted_cn
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.DMR_CLUSTERS, dmr, su.LINKS, link, su.TLS_TRUSTED_COMMON_NAMES]
        return su.make_post_request(solace_config, path_array, data)

    def delete_func(self, solace_config, dmr, link, lookup_item_value):
        """Delete a VPN"""
        path_array = [su.SEMP_V2_CONFIG, su.DMR_CLUSTERS, dmr, su.LINKS, link, su.TLS_TRUSTED_COMMON_NAMES, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    """Entrypoint to module"""
    module_args = dict(
        name=dict(type='str', required=True),
        dmr=dict(type='str', required=True),
        remote_node_name=dict(type='str', required=True),
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

    solace_task = SolaceLinkTrustedCNTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
