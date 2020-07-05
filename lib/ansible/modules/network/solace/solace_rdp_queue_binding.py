#!/usr/bin/env python

# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke <ricardo.gomez-ulmke@solace.com>
# MIT License

"""Ansible-Solace Module for configuring Queue Bindings for an RDP"""
import ansible.module_utils.network.solace.solace_utils as su
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '0.1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: solace_rdp_queueBindings

short_description: Configure a queue bindining for an RDP.

version_added: "2.9"

description:
    - "Allows addition, removal and configuration of Queue Bindings for a Rest Delivery Point on Solace Brokers in an idempotent manner. "
    - "Reference documentation: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/restDeliveryPoint/getMsgVpnRestDeliveryPointQueueBindings."

options:
    rdp_name:
        description:
            - This is the RDP name the Rest Consumer will be configured for
        required: true
    name:
        description:
            - This is the Rest Consumer name
        required: true
    msg_vpn:
        description:
            - The message vpn the RDP/Rest Consumer is on/created
        required: true
    settings:
        description:
            - JSON dictionary of additional configuration, see Reference documentation
        required: false
    state:
        description:
            - Target state, present/absent
        required: false
    host:
        description:
            - Hostname of Solace Broker, default is "localhost"
        required: false
    port:
        description:
            - Management port of Solace Broker, default is 8080
        required: false
    secure_connection:
        description:
            - If true use https rather than http for querying
        required: false
    username:
        description:
            - Administrator username for Solace Broker, default is "admin"
        required: false
    password:
        description:
            - Administrator password for Solace Broker, default is "admin"
        required: false
    timeout:
        description:
            - Connection timeout when making requests, defaults to 1 (second)
        required: false
    x_broker:
        description:
            - Custom HTTP header with the broker virtual router id, if using a SMEPv2 Proxy/agent infrastructure
        required: false

author:
    - Mark Street (mkst@protonmail.com)
    - Swen-Helge Huber (swen-helge.huber@solace.com)
    - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''

# Loop to Create a Series of Queue Bindings
    - name: Create a Queue Binding
      solace_rdp_queueBinding:
        secure_connection: "{{ deployment.solaceBrokerSempv2.isSecureConnection }}"
        username: "{{ deployment.solaceBrokerSempv2.username }}"
        password: "{{ deployment.solaceBrokerSempv2.password }}"
        host: "{{ deployment.solaceBrokerSempv2.host }}"
        port: "{{ deployment.solaceBrokerSempv2.port }}"
        timeout: "{{ deployment.solaceBrokerSempv2.httpRequestTimeout }}"
        msg_vpn: "{{ deployment.azRDPFunction.brokerConfig.vpn }}"
        rdp_name: "{{ deployment.azRDPFunction.brokerConfig.rdp.name }}"
        name: "{{ item.queue }}"
        settings:
          postRequestTarget: "{{ item.postRequestTarget }}"
        state: present

      loop: "{{ deployment.azRDPFunction.brokerConfig.rdp.queueBindings }}"

      register: result

    - debug:
        msg: "(solace_rdp_queueBinding): result={{ result }}"

'''

RETURN = '''
response:
    description: The response back from the Solace Sempv2 request
    type: dict
'''


class SolaceRdpQueueBindingTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'queueBindingName'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def lookup_item(self):
        return self.module.params['name']

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['rdp_name']]

    def get_func(self, solace_config, vpn, rdp_name, lookup_item_value):
        """Pull configuration for all queue bindings for a given RDP"""
        # GET /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/queueBindings/{queueBindingName}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.RDP_REST_DELIVERY_POINTS, rdp_name, su.RDP_QUEUE_BINDINGS, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, rdp_name, name, settings=None):
        """Create a queue binding for an RDP"""
        # POST /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/queueBindings
        defaults = {}
        mandatory = {
            'msgVpnName': vpn,
            'restDeliveryPointName': rdp_name,
            'queueBindingName': name
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.RDP_REST_DELIVERY_POINTS, rdp_name, su.RDP_QUEUE_BINDINGS]
        return su.make_post_request(solace_config, path_array, data)

    def update_func(self, solace_config, vpn, rdp_name, lookup_item_value, settings):
        """Update an existing queue binding"""
        # PATCH /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/queueBindings/{queueBindingName}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.RDP_REST_DELIVERY_POINTS, rdp_name, su.RDP_QUEUE_BINDINGS, lookup_item_value]
        return su.make_patch_request(solace_config, path_array, settings)

    def delete_func(self, solace_config, vpn, rdp_name, lookup_item_value):
        """Delete an existing queue binding"""
        # DELETE /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/queueBindings/{queueBindingName}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.RDP_REST_DELIVERY_POINTS, rdp_name, su.RDP_QUEUE_BINDINGS, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    """Entrypoint to module"""
    module_args = dict(
        rdp_name=dict(type='str', required=True),
        name=dict(type='str', required=True),
        msg_vpn=dict(type='str', required=True),
        host=dict(type='str', default='localhost'),
        port=dict(type='int', default=8080),
        secure_connection=dict(type='bool', default=False),
        username=dict(type='str', default='admin'),
        password=dict(type='str', default='admin', no_log=True),
        settings=dict(type='dict', require=False),
        state=dict(default='present', choices=['absent', 'present']),
        timeout=dict(default='30', require=False),
        x_broker=dict(type='str', default='')
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    solace_task = SolaceRdpQueueBindingTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
