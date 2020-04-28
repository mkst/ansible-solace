#!/usr/bin/env python

# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
# Copyright (c) 2020, Solace Corporation, Swen-Helge Huber <swen-helge.huber@solace.com
# MIT License

"""Ansible-Solace Module for configuring Client Profiles"""
import ansible.module_utils.network.solace.solace_utils as su
from ansible.module_utils.basic import AnsibleModule


class SolaceACLClientConnectExceptionTask(su.SolaceTask):

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def lookup_item(self):
        return self.module.params['name']

    def get_args(self):
        return [self.module.params['msg_vpn'],self.module.params['acl_profile_name']]

    def get_func(self, solace_config, vpn, acl_profile_name):
        """Pull configuration for all Client Profiles associated with a given VPN"""
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, su.ACL_PROFILES_CLIENT_CONNECT_EXCEPTIONS]
        return su.get_configuration(solace_config, path_array, 'clientConnectExceptionAddress')

    def create_func(self, solace_config, vpn, acl_profile_name, client_connect_exception_address, settings=None):
        """Create a Client Profile"""
        defaults = {
            'msgVpnName': vpn,
            'aclProfileName': acl_profile_name
            
        }
        mandatory = {
            'clientConnectExceptionAddress': client_connect_exception_address
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path = '/'.join([su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, su.ACL_PROFILES_CLIENT_CONNECT_EXCEPTIONS])

        return su.make_post_request(solace_config, path, data)

    def delete_func(self, solace_config, vpn, acl_profile_name, client_connect_exception_address):
        """Delete a Client Profile"""
        path = '/'.join([su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, su.ACL_PROFILES_CLIENT_CONNECT_EXCEPTIONS,client_connect_exception_address])
        return su.make_delete_request(solace_config, path)


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

    solace_acl_connect_task = SolaceACLClientConnectExceptionTask(module)
    result = solace_acl_connect_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()
