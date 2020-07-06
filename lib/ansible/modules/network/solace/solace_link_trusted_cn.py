#!/usr/bin/env python

# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
# Copyright (c) 2020, Solace Corporation, Swen-Helge Huber <swen-helge.huber@solace.com
# MIT License

import ansible.module_utils.network.solace.solace_utils as su
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '0.1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: solace_link_trusted_cn

short_description: Configure DMR Cluster on Solace Appliances

version_added: "2.9"

description:
    - "Allows addition, removal and configuration of DMR Clusters on Solace Brokers in an idempotent manner."

options:
    name:
        description:
            - This is the trusted tls common name of the DMR link being configured
        required: true
    remote_node_name:
            - Remote node name, identifier of the DMR link
        required: true
    dmr:
            - Name of the DMR Cluster
        required: true
    state:
        description:
            - Target state of the DMR Cluster, present/absent
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
            - Administrator username for Solace Broker, defaults is "admin"
        required: false
    password:
        description:
            - Administrator password for Solace Broker, defaults is "admin"
        required: false
    settings:
        description:
            - JSON dictionary of additional configuration
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
'''

EXAMPLES = '''

'''

RETURN = '''
response:
    description: The response back from the Solace device
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
