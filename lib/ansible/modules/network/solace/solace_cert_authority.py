#!/usr/bin/env python

# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
# Copyright (c) 2020, Solace Corporation, Swen-Helge Huber <swen-helge.huber@solace.com
# MIT License

"""Ansible-Solace Module for configuring cert_authorities"""

import ansible.module_utils.network.solace.solace_utils as su
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '0.1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: solace_cert_authority

short_description: Configure cert authorities on Solace Appliances

version_added: "2.9"

description:
    - "Allows addition, removal and configuration of cert authorities on Solace Applicances in an idempotent manner."

options:
    name:
        description:
            - This is the name of the cert authority being configured
        required: true
    state:
        description:
            - Target state of the cert authority, present/absent
        required: false
    host:
        description:
            - Hostname of Solace Appliance, default is "localhost"
        required: false
    port:
        description:
            - Management port of Solace Appliance, default is 8080
        required: false
    secure_connection:
        description:
            - If true use https rather than http for querying
        required: false
    username:
        description:
            - Administrator username for Solace Appliance, defaults is "admin"
        required: false
    password:
        description:
            - Administrator password for Solace Appliance, defaults is "admin"
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


class SolaceCertAuthorityTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'certAuthorityName'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['cert_content']]

    def lookup_item(self):
        return self.module.params['name']

    def get_func(self, solace_config, cert_content, lookup_item_value):
        path_array = [su.SEMP_V2_CONFIG, su.CERT_AUTHORITIES, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, cert_content, cert_authority, settings=None):
        """Create a cert_authority"""
        defaults = {
            'certContent': cert_content
        }
        mandatory = {
            'certAuthorityName': cert_authority,
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.CERT_AUTHORITIES]
        return su.make_post_request(solace_config, path_array, data)

    def update_func(self, solace_config, cert_content, lookup_item_value, settings):
        """Update an existing cert_authority"""
        path_array = [su.SEMP_V2_CONFIG, su.CERT_AUTHORITIES, lookup_item_value]
        return su.make_patch_request(solace_config, path_array, settings)

    def delete_func(self, solace_config, cert_content, lookup_item_value):
        """Delete a cert_authority"""
        path_array = [su.SEMP_V2_CONFIG, su.CERT_AUTHORITIES, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    """Entrypoint to module"""
    module_args = dict(
        name=dict(type='str', required=True),
        cert_content=dict(type='str', default=''),
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

    solace_task = SolaceCertAuthorityTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
