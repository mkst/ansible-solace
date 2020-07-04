#!/usr/bin/env python

# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
# MIT License

"""Ansible-Solace Module for configuring Subscriptions"""
import ansible.module_utils.network.solace.solace_utils as su
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '0.1.0',
    'status': ['preview'],
    'supported_by': 'community'
}


class SolaceSubscriptionTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'subscriptionTopic'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def lookup_item(self):
        return self.module.params['topic']

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['queue']]

    def get_func(self, solace_config, vpn, queue, lookup_item_value):
        """Pull configuration for all Subscriptions associated with a given VPN and Queue"""
        # GET /msgVpns/{msgVpnName}/queues/{queueName}/subscriptions/{subscriptionTopic}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.QUEUES, queue, su.SUBSCRIPTIONS, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, queue, topic, settings=None):
        """Create a Subscription for a Topic/Endpoint on a Queue"""
        # POST /msgVpns/{msgVpnName}/queues/{queueName}/subscriptions
        defaults = {}
        mandatory = {
            'subscriptionTopic': topic
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.QUEUES, queue, su.SUBSCRIPTIONS]
        return su.make_post_request(solace_config, path_array, data)

    def delete_func(self, solace_config, vpn, queue, lookup_item_value):
        """Delete a Subscription"""
        # DELETE /msgVpns/{msgVpnName}/queues/{queueName}/subscriptions/{subscriptionTopic}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.QUEUES, queue, su.SUBSCRIPTIONS, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    """Entrypoint to module"""
    module_args = dict(
        topic=dict(type='str', required=True),
        queue=dict(type='str', required=True),
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

    solace_topic_task = SolaceSubscriptionTask(module)
    result = solace_topic_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()
