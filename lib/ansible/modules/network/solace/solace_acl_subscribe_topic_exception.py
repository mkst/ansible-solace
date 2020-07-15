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
from ansible.errors import AnsibleError
import json

DOCUMENTATION = '''
---
module: solace_acl_subscribe_topic_exception

short_description: Configure a subscribe topic exception object for an ACL Profile.

description:
  - "Allows addition and removal of a subscribe topic exception object for an ACL Profile."
  - "Supported versions: [ <2.14, >=2.14 ]."
  - "Reference: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/aclProfile/createMsgVpnAclProfileSubscribeTopicException."
  - "Reference: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/aclProfile/createMsgVpnAclProfileSubscribeException."

options:
  name:
    description: The subscribe topic exception.
    required: true
  acl_profile_name:
    description: The ACL Profile.
    required: true
  topic_syntax:
    description: The topic syntax.
    required: false
    default: "smf"
  settings:
    description: JSON dictionary of additional configuration, see Reference documentation.
    required: false
  state:
    description: Target state. [present|absent].
    required: false
    default: present
  host:
    description: Hostname of Solace Broker.
    required: false
    default: "localhost"
  port:
    description: Management port of Solace Broker.
    required: false
    default: 8080
  msg_vpn:
    description: The message vpn.
    required: true
  secure_connection:
    description: If true, use https rather than http for querying.
    required: false
    default: false
  username:
    description: Administrator username for Solace Broker.
    required: false
    default: "admin"
  password:
    description: Administrator password for Solace Broker.
    required: false
    default: "admin"
  timeout:
    description: Connection timeout in seconds for the http request.
    required: false
    default: 1
  x_broker:
    description: Custom HTTP header with the broker virtual router id, if using a SMEPv2 Proxy/agent infrastructure.
    required: false
  semp_version:
    description: The Semp API version of the broker. See 'solace_get_facts' for info on how to retrieve the version from the broker.
    required: true


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

    - name: Add Subscribe Topic Exceptions to ACL Profile
      solace_acl_subscribe_topic_exception:
        semp_version: "{{ ansible_facts.solace.about.api.sempVersion }}"
        acl_profile_name: "test_ansible_solace"
        name: "test/ansible/solace"
        state: present

    - name: Delete Subscribe Topic Exceptions from ACL Profile
      solace_acl_subscribe_topic_exception:
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


class SolaceACLSubscribeTopicExceptionTask(su.SolaceTask):

    SEMP_VERSION_KEY_LOOKUP = {
        '<2.14': {
            'LOOKUP_ITEM_KEY': 'subscribeExceptionTopic',
            'URI_SUBSCR_EX': 'subscribeExceptions',
            'TOPIC_SYNTAX_KEY': 'topicSyntax'
        },
        '>=2.14': {
            'LOOKUP_ITEM_KEY': 'subscribeTopicException',
            'URI_SUBSCR_EX': 'subscribeTopicExceptions',
            'TOPIC_SYNTAX_KEY': 'subscribeTopicExceptionSyntax'
        }
    }

    def get_semp_version_lookup(self, vmr_sempVersion, key):
        if vmr_sempVersion < "2.14":
            version_key = '<2.14'
        elif vmr_sempVersion >= "2.14":
            version_key = ">=2.14"
        else:
            raise AnsibleError("unsupported semp_version: '{}'".format(vmr_sempVersion))
        if version_key not in self.SEMP_VERSION_KEY_LOOKUP:
            raise AnsibleError("version_key: '{}' not found in dict: SEMP_VERSION_KEY_LOOKUP: {}".format(version_key, json.dumps(self.SEMP_VERSION_KEY_LOOKUP)))
        lookup_dict = self.SEMP_VERSION_KEY_LOOKUP[version_key]
        if key not in lookup_dict:
            raise AnsibleError("key: '{}' not found in dict SEMP_VERSION_KEY_LOOKUP['{}']: '{}'".format(key, version_key, json.dumps(lookup_dict)))
        return lookup_dict[key]

    # LOOKUP_ITEM_KEY_LT_2_14 = 'subscribeExceptionTopic'
    # LOOKUP_ITEM_KEY_GT_EQ_2_14 = 'subscribeTopicException'
    #
    # URI_SUBSCR_EX_VERSION_LT_2_14 = 'subscribeExceptions'
    # URI_SUBSCR_EX_VERSION_GT_EQ_2_14 = 'subscribeTopicExceptions'
    #
    # TOPIC_SYNTAX_KEY_LT_2_14 = 'topicSyntax'
    # TOPIC_SYNTAX_KEY_GT_EQ_2_14 = 'subscribeTopicExceptionSyntax'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['acl_profile_name'], self.module.params['topic_syntax']]

    def lookup_item(self):
        return self.module.params['name']

    # def get_uri_subscr_ex(self, vmr_sempVersion):
    #     if vmr_sempVersion < "2.14":
    #         return self.URI_SUBSCR_EX_VERSION_LT_2_14
    #     elif vmr_sempVersion >= "2.14":
    #         return self.URI_SUBSCR_EX_VERSION_GT_EQ_2_14
    #     else:
    #         raise AnsibleError("unsupported semp_version=%s" % vmr_sempVersion)
    #
    # def get_lookup_item_key(self, vmr_sempVersion):
    #     if vmr_sempVersion < "2.14":
    #         return self.LOOKUP_ITEM_KEY_LT_2_14
    #     elif vmr_sempVersion >= "2.14":
    #         return self.LOOKUP_ITEM_KEY_GT_EQ_2_14
    #     else:
    #         raise AnsibleError("unsupported semp_version=%s" % vmr_sempVersion)
    #
    # def get_topic_syntax_key(self, vmr_sempVersion):
    #     if vmr_sempVersion < "2.14":
    #         return self.TOPIC_SYNTAX_KEY_LT_2_14
    #     elif vmr_sempVersion >= "2.14":
    #         return self.TOPIC_SYNTAX_KEY_GT_EQ_2_14
    #     else:
    #         raise AnsibleError("unsupported semp_version=%s" % vmr_sempVersion)

    def get_func(self, solace_config, vpn, acl_profile_name, topic_syntax, lookup_item_value):
        # vmr_sempVersion < "2.14" : GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeExceptions/{topicSyntax},{subscribeExceptionTopic}
        # vmr_sempVersion >= "2.14": GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeTopicExceptions/{subscribeTopicExceptionSyntax},{subscribeTopicException}
        # uri_subscr_ex = self.get_uri_subscr_ex(solace_config.vmr_sempVersion)
        # lookup_item_key = self.get_lookup_item_key(solace_config.vmr_sempVersion)

        uri_subscr_ex = self.get_semp_version_lookup(solace_config.vmr_sempVersion, "URI_SUBSCR_EX")
        lookup_item_key = self.get_semp_version_lookup(solace_config.vmr_sempVersion, "LOOKUP_ITEM_KEY")

        ex_uri = ','.join([topic_syntax, lookup_item_value])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, uri_subscr_ex, ex_uri]
        return su.get_configuration(solace_config, path_array, lookup_item_key)

    def create_func(self, solace_config, vpn, acl_profile_name, topic_syntax, subscribe_topic_exception, settings=None):
        # vmr_sempVersion: <2.14 : POST /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeExceptions
        # vmr_sempVersion: >=2.14: POST /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeTopicExceptions
        defaults = {
            'msgVpnName': vpn,
            'aclProfileName': acl_profile_name,
            self.get_semp_version_lookup(solace_config.vmr_sempVersion, "TOPIC_SYNTAX_KEY"): topic_syntax
            # self.get_topic_syntax_key(solace_config.vmr_sempVersion): topic_syntax
        }
        mandatory = {
            self.get_semp_version_lookup(solace_config.vmr_sempVersion, "LOOKUP_ITEM_KEY"): subscribe_topic_exception
            # self.get_lookup_item_key(solace_config.vmr_sempVersion): subscribe_topic_exception
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        uri_subscr_ex = self.get_semp_version_lookup(solace_config.vmr_sempVersion, "URI_SUBSCR_EX")
        # uri_subscr_ex = self.get_uri_subscr_ex(solace_config.vmr_sempVersion)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, uri_subscr_ex]
        return su.make_post_request(solace_config, path_array, data)

    def delete_func(self, solace_config, vpn, acl_profile_name, topic_syntax, lookup_item_value):
        # vmr_sempVersion: <2.14 : DELETE /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeExceptions/{topicSyntax},{subscribeExceptionTopic}
        # vmr_sempVersion: >=2.14: DELETE /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeTopicExceptions/{subscribeTopicExceptionSyntax},{subscribeTopicException}
        ex_uri = ",".join([topic_syntax, lookup_item_value])
        uri_subscr_ex = self.get_semp_version_lookup(solace_config.vmr_sempVersion, "URI_SUBSCR_EX")
        # uri_subscr_ex = self.get_uri_subscr_ex(solace_config.vmr_sempVersion)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, uri_subscr_ex, ex_uri]
        return su.make_delete_request(solace_config, path_array)


def run_module():
    """Entrypoint to module"""

    module_args = dict(
        name=dict(type='str', required=True),
        msg_vpn=dict(type='str', required=True),
        acl_profile_name=dict(type='str', required=True),
        topic_syntax=dict(type='str', default='smf'),
        semp_version=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=su.compose_module_args(module_args),
        supports_check_mode=True
    )

    solace_task = SolaceACLSubscribeTopicExceptionTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()


###
# The End.
