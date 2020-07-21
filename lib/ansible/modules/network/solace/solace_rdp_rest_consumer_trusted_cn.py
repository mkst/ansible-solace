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
module: solace_rdp_restConsumer_trusted_cn

short_description: Configure a trusted common name object on a rest consumer of an RDP.

description:
  - "Allows addition, removal and configuration of trusted common name objects for a rest consumer of an RDP."
  - "Reference: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/restDeliveryPoint/getMsgVpnRestDeliveryPointRestConsumerTlsTrustedCommonNames."

options:
  name:
    description: The expected trusted common name of the remote certificate. Maps to 'tlsTrustedCommonName' in the API.
    required: true
  rdp_name:
    description: The RDP name. Maps to 'restDeliveryPointName' in the API.
    required: true
  rest_consumer_name:
    description: The Rest consumer name. Maps to 'restConsumerName' in the API.
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
    - name: Add the TLS Trusted Common Name
      solace_rdp_restConsumer_trusted_cn:
        secure_connection: "{{ deployment.solaceBrokerSempv2.isSecureConnection }}"
        username: "{{ deployment.solaceBrokerSempv2.username }}"
        password: "{{ deployment.solaceBrokerSempv2.password }}"
        host: "{{ deployment.solaceBrokerSempv2.host }}"
        port: "{{ deployment.solaceBrokerSempv2.port }}"
        timeout: "{{ deployment.solaceBrokerSempv2.httpRequestTimeout }}"
        msg_vpn: "{{ deployment.azRDPFunction.brokerConfig.vpn }}"
        rdp_name: "{{ deployment.azRDPFunction.brokerConfig.rdp.name }}"
        rest_consumer_name: "{{ deployment.azRDPFunction.brokerConfig.rdp.restConsumer.name }}"
        name: "{{ deployment.azRDPFunction.brokerConfig.rdp.restConsumer.tlsOptions.trustedCommonName }}"

        state: present

      register: result

    - debug:
        msg: "(solace_rdp_restConsumer_trustedCommonName): result={{ result }}"
'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
'''


class SolaceRdpRestConsumerTrustedCommonNameTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'tlsTrustedCommonName'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def lookup_item(self):
        return self.module.params['name']

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['rdp_name'], self.module.params['rest_consumer_name']]

    def get_func(self, solace_config, vpn, rdp_name, rest_consumer_name, lookup_item_value):
        """Get all trusted common names"""
        # GET /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/restConsumers/{restConsumerName}/tlsTrustedCommonNames/{tlsTrustedCommonName}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.RDP_REST_DELIVERY_POINTS, rdp_name, su.RDP_REST_CONSUMERS, rest_consumer_name, su.RDP_TLS_TRUSTED_COMMON_NAMES, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, rdp_name, rest_consumer_name, name, settings=None):
        """Add a trusted common name"""
        # POST /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/restConsumers/{restConsumerName}/tlsTrustedCommonNames
        defaults = {}
        mandatory = {
            'msgVpnName': vpn,
            'restConsumerName': rest_consumer_name,
            'restDeliveryPointName': rdp_name,
            'tlsTrustedCommonName': name
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.RDP_REST_DELIVERY_POINTS, rdp_name, su.RDP_REST_CONSUMERS, rest_consumer_name, su.RDP_TLS_TRUSTED_COMMON_NAMES]
        return su.make_post_request(solace_config, path_array, data)

    def delete_func(self, solace_config, vpn, rdp_name, rest_consumer_name, lookup_item_value):
        """Delete an existing rest consumer"""
        # DELETE /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/restConsumers/{restConsumerName}/tlsTrustedCommonNames/{tlsTrustedCommonName}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.RDP_REST_DELIVERY_POINTS, rdp_name, su.RDP_REST_CONSUMERS, rest_consumer_name, su.RDP_TLS_TRUSTED_COMMON_NAMES, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    """Entrypoint to module"""

    """Compose module arguments"""
    module_args = dict(
        rdp_name=dict(type='str', required=True),
        rest_consumer_name=dict(type='str', required=True),
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_crud())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceRdpRestConsumerTrustedCommonNameTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
