#!/usr/bin/env python

# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
# Copyright (c) 2020, Solace Corporation, Swen-Helge Huber <swen-helge.huber@solace.com
# MIT License

"""Ansible-Solace Module for configuring Bridges"""
import ansible.module_utils.network.solace.solace_utils as su
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '0.1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


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
