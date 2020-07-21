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
module: solace_get_queues

version_added: '2.9.10'

short_description: Get a list of Queue objects

description:
- "Get a list of Queue objects."
- "Retrieves all queue objects that match the criteria defined in the 'where' clause and returns the fields defined in the 'select' parameter."
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/queue/getMsgVpnQueues)."

extends_documentation_fragment:
- solace.broker
- solace.vpn
- solace.query

seealso:
- module: solace_queue

author:
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''
- name: Get queues
  solace_get_queues:
    msg_vpn: "{{ vpn }}"
    query_params:
      where:
        - "queueName==ansible-solace/test*"
        - "ingressEnabled==true"
        - "maxMsgSpoolUsage<2000"
        - "eventMsgSpoolUsageThreshold.clearPercent<=60"
      select:
        - "queueName"
        - "eventMsgSpoolUsageThreshold"
  register: existing_queues_result

- name: Print existing queue list
  debug:
    msg: "{{ existing_queues_result.queue_list }}"

- name: Print count of existing queue list
  debug:
    msg: "{{ existing_queues_result.queue_list_count }}"

- name: Remove all found queues
  solace_queue:
    name: "{{ item.queueName }}"
    state: absent
  loop: "{{ existing_queues_result.queue_list }}"
'''

RETURN = '''
result_list:
    description: The list of objects found containing requested fields.
    returned: on success
    type: list
    elements: complex
    sample: [
        {
            "eventMsgSpoolUsageThreshold": {
                "clearPercent": 50,
                "setPercent": 60
            },
            "queueName": "ansible-solace/test/__1__/topic/subscription/__xx__"
        },
        {
            "eventMsgSpoolUsageThreshold": {
                "clearPercent": 50,
                "setPercent": 60
            },
            "queueName": "ansible-solace/test/__2__/topic/subscription/__xx__"
        }
    ]

result_list_count:
    description: Number of items in result_list.
    returned: on success
    type: int

'''


class SolaceGetQueuesTask(su.SolaceTask):

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_list(self):
        # GET /msgVpns/{msgVpnName}/queues
        vpn = self.module.params['msg_vpn']
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.QUEUES]

        query_params = self.module.params['query_params']
        ok, resp = su.get_list(self.solace_config, path_array, query_params)
        if ok:
            queue_list = resp
        else:
            return False, resp

        return True, queue_list


def run_module():
    """Entrypoint to module"""

    """Compose module arguments"""
    module_args = dict(
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_query())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    result = dict(
        changed=False
    )

    solace_task = SolaceGetQueuesTask(module)
    ok, resp_or_list = solace_task.get_list()
    if not ok:
        module.fail_json(msg=resp_or_list, **result)

    result['result_list'] = resp_or_list
    result['result_list_count'] = len(resp_or_list)
    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
