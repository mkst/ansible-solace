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


class SolaceBridgeTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'bridgeName'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['virtual_router']]

    def lookup_item(self):
        return self.module.params['name']

    def get_func(self, solace_config, vpn, virtual_router, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}
        bridge_uri = ','.join([lookup_item_value, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, virtual_router, bridge_name, settings=None):
        # POST /msgVpns/{msgVpnName}/bridges
        defaults = {
            'msgVpnName': vpn,
            'bridgeVirtualRouter': virtual_router
        }
        mandatory = {
            'bridgeName': bridge_name
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES]
        return su.make_post_request(solace_config, path_array, data)

    def update_func(self, solace_config, vpn, virtual_router, lookup_item_value, settings=None):
        # PATCH /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}
        bridge_uri = ','.join([lookup_item_value, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri]
        return su.make_patch_request(solace_config, path_array, settings)

    def delete_func(self, solace_config, vpn, virtual_router, lookup_item_value):
        # DELETE /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}
        bridge_uri = ','.join([lookup_item_value, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri]
        return su.make_delete_request(solace_config, path_array, None)


def run_module():
    """Entrypoint to module"""
    module_args = dict(
        name=dict(type='str', required=True),
        virtual_router=dict(type='str', required=True),
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

    solace_task = SolaceBridgeTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
