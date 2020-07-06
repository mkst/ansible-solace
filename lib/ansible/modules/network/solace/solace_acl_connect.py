#!/usr/bin/env python

# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
# Copyright (c) 2020, Solace Corporation, Swen-Helge Huber <swen-helge.huber@solace.com
# MIT License

import ansible.module_utils.network.solace.solace_utils as su
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '0.1.0',
    'status': ['preview'],
    'supported_by': 'community'
}


class SolaceACLClientConnectExceptionTask(su.SolaceTask):

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['acl_profile_name']]

    LOOKUP_ITEM_KEY = 'clientConnectExceptionAddress'

    def lookup_item(self):
        return self.module.params['name']

    def get_func(self, solace_config, vpn, acl_profile_name, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/clientConnectExceptions/{clientConnectExceptionAddress}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, su.ACL_PROFILES_CLIENT_CONNECT_EXCEPTIONS, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, acl_profile_name, client_connect_exception_address, settings=None):
        defaults = {
            'msgVpnName': vpn,
            'aclProfileName': acl_profile_name
        }
        mandatory = {
            self.LOOKUP_ITEM_KEY: client_connect_exception_address
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, su.ACL_PROFILES_CLIENT_CONNECT_EXCEPTIONS]
        return su.make_post_request(solace_config, path_array, data)

    def delete_func(self, solace_config, vpn, acl_profile_name, lookup_item_value):
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, su.ACL_PROFILES_CLIENT_CONNECT_EXCEPTIONS, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    """Entrypoint to module"""
    module_args = dict(
        name=dict(type='str', required=True),
        msg_vpn=dict(type='str', required=True),
        acl_profile_name=dict(type='str', required=True),
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

    solace_task = SolaceACLClientConnectExceptionTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
