#!/usr/bin/env python

# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
# Copyright (c) 2020, Solace Corporation, Swen-Helge Huber <swen-helge.huber@solace.com
# MIT License

"""Ansible-Solace Module for configuring Client Profiles"""
import ansible.module_utils.network.solace.solace_utils as su
from ansible.module_utils.basic import AnsibleModule

import logging
logging.basicConfig(filename='solace.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(funcName)s -%(message)s' )

class SolaceACLPublishExceptionDeprecatedTask(su.SolaceTask):

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def lookup_item(self):
        return self.module.params['name']

    def get_args(self):
        ret_val = [self.module.params['msg_vpn'],self.module.params['acl_profile_name'],self.module.params['topic_syntax']]
        logging.debug('get args ' + str(ret_val))
        return ret_val

    def get_func(self, solace_config, vpn, acl_profile_name, topic_syntax):
        """Pull configuration for all Client Profiles associated with a given VPN"""
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, su.ACL_PROFILES_PUBLISH_EXCEPTIONS]
        logging.debug('path array ' + "/".join(path_array))
        return su.get_configuration(solace_config, path_array, 'publishExceptionTopic')

    def create_func(self, solace_config, vpn, acl_profile_name, topic_syntax, publish_topic_exception, settings=None):
        """Create a Client Profile"""
        defaults = {
            'msgVpnName': vpn,
            'aclProfileName': acl_profile_name,
            'topicSyntax': topic_syntax
            
        }
        mandatory = {
            'publishExceptionTopic': publish_topic_exception
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path = '/'.join([su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, su.ACL_PROFILES_PUBLISH_EXCEPTIONS])

        return su.make_post_request(solace_config, path, data)

    def delete_func(self, solace_config, vpn, acl_profile_name, topic_syntax, publish_topic_exception):
        """Delete a Client Profile"""
        publish_topic_exception = publish_topic_exception.replace('/', '%2F')
        uri = ','.join([topic_syntax, publish_topic_exception])
        path = '/'.join([su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, su.ACL_PROFILES_PUBLISH_EXCEPTIONS,uri])
        logging.debug('delete  ' + path)
        return su.make_delete_request(solace_config, path)


def run_module():
    """Entrypoint to module"""
    module_args = dict(
        name=dict(type='str', required=True),
        msg_vpn=dict(type='str', required=True),
        acl_profile_name=dict(type='str', required=True),
        topic_syntax=dict(type='str', default='smf'),
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

    solace_acl_publish_task = SolaceACLPublishExceptionDeprecatedTask(module)
    result = solace_acl_publish_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()
