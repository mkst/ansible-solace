#!/usr/bin/env python

# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
# MIT License

import ansible.module_utils.network.solace.solace_utils as su
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '0.1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


class SolaceClientProfileTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'clientProfileName'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn']]

    def lookup_item(self):
        return self.module.params['name']

    def get_func(self, solace_config, vpn, lookup_item_value):
        """Pull configuration for all Client Profiles associated with a given VPN"""
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_PROFILES, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, client_profile, settings=None):
        """Create a Client Profile"""
        defaults = {
        }
        mandatory = {
            'clientProfileName': client_profile
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_PROFILES]
        return su.make_post_request(solace_config, path_array, data)

    def update_func(self, solace_config, vpn, lookup_item_value, settings=None):
        """Update an existing Client Profile"""
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_PROFILES, lookup_item_value]
        return su.make_patch_request(solace_config, path_array, settings)

    def delete_func(self, solace_config, vpn, lookup_item_value):
        """Delete a Client Profile"""
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_PROFILES, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    """Entrypoint to module"""
    module_args = dict(
        name=dict(type='str', required=True),
        msg_vpn=dict(type='str', required=True),
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

    solace_task = SolaceClientProfileTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()


###
# The End.
