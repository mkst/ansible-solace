#!/usr/bin/env python

# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
# Copyright (c) 2020, Solace Corporation, Swen-Helge Huber <swen-helge.huber@solace.com
# MIT License

"""Ansible-Solace Module for configuring Bridges"""
import ansible.module_utils.network.solace.solace_utils as su
from ansible.module_utils.basic import AnsibleModule


class SolaceBridgeRemoteSubscriptionsTask(su.SolaceTask):

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def lookup_item(self):
        return self.module.params['name']

    def get_args(self):
        return [self.module.params['msg_vpn'],self.module.params['virtual_router'],self.module.params['bridge_name'],self.module.params['deliver_always']]

    def get_func(self, solace_config, vpn, virtual_router, bridge_name, deliver_always):
        """Pull configuration for all Bridges associated with a given VPN"""
        bridge_uri = ','.join([bridge_name, virtual_router]) 
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_REMOTE_SUBSCRIPTIONS]
        return su.get_configuration(solace_config, path_array, 'remoteSubscriptionTopic')

    def create_func(self, solace_config, vpn, virtual_router, bridge_name, deliver_always, remote_subscription, settings=None):
        """Create a Bridge"""
        defaults = {
            'msgVpnName': vpn,
            'bridgeName': bridge_name,
            'bridgeVirtualRouter': virtual_router,
            'deliverAlwaysEnabled': True
        }
        mandatory = {
            'remoteSubscriptionTopic': remote_subscription, 
            'deliverAlwaysEnabled': deliver_always
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        bridge_uri = ','.join([bridge_name, virtual_router])
        path = '/'.join([su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_REMOTE_SUBSCRIPTIONS])

        return su.make_post_request(solace_config, path, data)

    def delete_func(self, solace_config, vpn, virtual_router, bridge_name, deliver_always, remote_subscription):
        """Delete a Bridge"""
        bridge_uri = ','.join([bridge_name, virtual_router])
        path = '/'.join([su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_REMOTE_SUBSCRIPTIONS, remote_subscription])
        return su.make_delete_request(solace_config, path, None)


def run_module():
    """Entrypoint to module"""
    module_args = dict(
        name=dict(type='str', required=True),
        bridge_name=dict(type='str', required=True),
        virtual_router=dict(type='str', required=True),
        deliver_always=dict(type='bool', required=False),
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

    solace_bridge_remote_subscription_task = SolaceBridgeRemoteSubscriptionsTask(module)
    result = solace_bridge_remote_subscription_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()
