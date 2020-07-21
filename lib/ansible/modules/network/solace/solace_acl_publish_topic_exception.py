#!/usr/bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
# Copyright (c) 2020, Solace Corporation, Swen-Helge Huber <swen-helge.huber@solace.com
# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ---------------------------------------------------------------------------------------------

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

import ansible.module_utils.network.solace.solace_utils as su
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: solace_acl_publish_topic_exception

short_description: Configure a publish topic exception object for an ACL Profile.

description:
- "Configure a publish topic exception object for an ACL Profile."
- "Allows addition and removal of a publish topic exception object for an ACL Profile."
- "Supported versions: [ <=2.13, >=2.14 ]."
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/aclProfile/createMsgVpnAclProfilePublishTopicException)."
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/aclProfile/createMsgVpnAclProfilePublishException)."

options:
  name:
    description: The publish topic exception.
    required: true
  acl_profile_name:
    description: The ACL Profile.
    required: true
  topic_syntax:
    description: The topic syntax.
    required: false
    default: "smf"

extends_documentation_fragment:
- solace.broker
- solace.vpn
- solace.state
- solace.semp_version

seealso:
- module: solace_acl_profile

author:
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''

    - name: Get Solace Facts
      solace_get_facts:

    - name: Create ACL Profile
      solace_acl_profile:
        name: "test_ansible_solace"
        settings:
          clientConnectDefaultAction: "disallow"
          publishTopicDefaultAction: "disallow"
          subscribeTopicDefaultAction: "disallow"
        state: present

    - name: Add Publish Topic Exceptions to ACL Profile
      solace_acl_publish_topic_exception:
        semp_version: "{{ ansible_facts.solace.about.api.sempVersion }}"
        acl_profile_name: "test_ansible_solace"
        name: "test/ansible/solace"
        state: present

    - name: Delete Publish Topic Exceptions from ACL Profile
      solace_acl_publish_topic_exception:
        semp_version: "{{ ansible_facts.solace.about.api.sempVersion }}"
        acl_profile_name: "test_ansible_solace"
        name: "test/ansible/solace"
        state: absent

'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
'''


class SolaceACLPublishTopicExceptionTask(su.SolaceTask):

    KEY_LOOKUP_ITEM_KEY = "LOOKUP_ITEM_KEY"
    KEY_URI_SUBSCR_EX = "URI_SUBSCR_EX"
    KEY_TOPIC_SYNTAX_KEY = "TOPIC_SYNTAX_KEY"
    SEMP_VERSION_KEY_LOOKUP = {
        '2.13': {
            KEY_LOOKUP_ITEM_KEY: 'publishExceptionTopic',
            KEY_URI_SUBSCR_EX: 'publishExceptions',
            KEY_TOPIC_SYNTAX_KEY: 'topicSyntax'
        },
        '2.14': {
            KEY_LOOKUP_ITEM_KEY: 'publishTopicException',
            KEY_URI_SUBSCR_EX: 'publishTopicExceptions',
            KEY_TOPIC_SYNTAX_KEY: 'publishTopicExceptionSyntax'
        }
    }

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['acl_profile_name'], self.module.params['topic_syntax']]

    def lookup_semp_version(self, semp_version):
        if semp_version <= 2.13:
            return True, '2.13'
        elif semp_version >= 2.14:
            return True, '2.14'
        return False, ''

    def lookup_item(self):
        return self.module.params['name']

    def get_func(self, solace_config, vpn, acl_profile_name, topic_syntax, lookup_item_value):
        # vmr_sempVersion <= "2.13" : GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/publishExceptions/{topicSyntax},{publishExceptionTopic}
        # vmr_sempVersion >= "2.14": GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/publishTopicExceptions/{publishTopicExceptionSyntax},{publishTopicException}
        uri_subscr_ex = self.get_semp_version_key(self.SEMP_VERSION_KEY_LOOKUP, solace_config.vmr_sempVersion, self.KEY_URI_SUBSCR_EX)
        lookup_item_key = self.get_semp_version_key(self.SEMP_VERSION_KEY_LOOKUP, solace_config.vmr_sempVersion, self.KEY_LOOKUP_ITEM_KEY)

        ex_uri = ','.join([topic_syntax, lookup_item_value])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, uri_subscr_ex, ex_uri]
        return su.get_configuration(solace_config, path_array, lookup_item_key)

    def create_func(self, solace_config, vpn, acl_profile_name, topic_syntax, publish_topic_exception, settings=None):
        # vmr_sempVersion: <=2.13 : POST /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/publishExceptions
        # vmr_sempVersion: >=2.14: POST /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/publishTopicExceptions
        defaults = {
            'msgVpnName': vpn,
            'aclProfileName': acl_profile_name,
            self.get_semp_version_key(self.SEMP_VERSION_KEY_LOOKUP, solace_config.vmr_sempVersion, self.KEY_TOPIC_SYNTAX_KEY): topic_syntax
        }
        mandatory = {
            self.get_semp_version_key(self.SEMP_VERSION_KEY_LOOKUP, solace_config.vmr_sempVersion, self.KEY_LOOKUP_ITEM_KEY): publish_topic_exception
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        uri_subscr_ex = self.get_semp_version_key(self.SEMP_VERSION_KEY_LOOKUP, solace_config.vmr_sempVersion, self.KEY_URI_SUBSCR_EX)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, uri_subscr_ex]
        return su.make_post_request(solace_config, path_array, data)

    def delete_func(self, solace_config, vpn, acl_profile_name, topic_syntax, lookup_item_value):
        # vmr_sempVersion: <=2.13 : DELETE /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/publishExceptions/{topicSyntax},{publishExceptionTopic}
        # vmr_sempVersion: >=2.14: DELETE /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/publishTopicExceptions/{publishTopicExceptionSyntax},{publishTopicException}
        ex_uri = ",".join([topic_syntax, lookup_item_value])
        uri_subscr_ex = self.get_semp_version_key(self.SEMP_VERSION_KEY_LOOKUP, solace_config.vmr_sempVersion, self.KEY_URI_SUBSCR_EX)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, uri_subscr_ex, ex_uri]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    """Entrypoint to module"""

    """Compose module arguments"""
    module_args = dict(
        acl_profile_name=dict(type='str', required=True),
        topic_syntax=dict(type='str', default='smf'),
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_crud())
    arg_spec.update(su.arg_spec_semp_version())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceACLPublishTopicExceptionTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()


###
# The End.
