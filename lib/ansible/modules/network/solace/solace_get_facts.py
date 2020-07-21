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
import requests

DOCUMENTATION = '''
---
module: solace_get_facts

short_description: Retrieves facts from the Solace event broker using the '/about' API and sets 'ansible_facts'.

description:
  - "Retrieves facts from the Solace event broker from the '/about' resource and sets 'ansible_facts.solace' for the rest of the playbook."
  - "Ideally, call at the beginning of the playbook so all subsequent tasks can use '{{ ansible_facts.solace.<path-to-fact> }}'."
  - "Reference: https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/about."

options:
  host:
    description: Hostname of Solace Broker.
    required: false
    default: "localhost"
  port:
    description: Management port of Solace Broker.
    required: false
    default: 8080
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
    description: Custom HTTP header with the broker virtual router id, if using a SEMPv2 Proxy/agent infrastructure.
    required: false

author:
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''
-
  name: Get Facts

  hosts: "{{ broker }}"

  module_defaults:
    solace_get_facts:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"

  tasks:

    - name: Get Solace Facts
      solace_get_facts:

    - name: show ansible_facts.solace
      debug:
        msg: "ansible_facts.solace={{ ansible_facts.solace }}"

    - name: show API version
      debug:
        msg: "api version={{ ansible_facts.solace.about.api.sempVersion }}"

    - name: show server
      debug:
        msg: "server={{ ansible_facts.solace.about.Server }}"

    - name: show msg vpns
      debug:
        msg: "msg vpns={{ ansible_facts.solace.about.user.msgVpns }}"

'''

RETURN = '''
ansible_facts.solace:
    description: The facts as returned from '/about' calls.
    type: dict
'''


class SolaceGetFactsTask(su.SolaceTask):

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_facts(self):

        facts = dict()

        paths = [
            ["about"],
            ["about", "user"],
            ["about", "user", "msgVpns"],
            ["about", "api"]
        ]

        for path in paths:
            ok, resp, headers = make_get_request(self.solace_config, [su.SEMP_V2_CONFIG] + path)
            if ok:
                addPathValue(facts, path, resp)
            else:
                return False, resp

        facts['about']['Server'] = headers['Server']

        return True, facts


def make_get_request(solace_config, path_array):

    path = su.compose_path(path_array)

    try:
        resp = requests.get(
                    solace_config.vmr_url + path,
                    json=None,
                    auth=solace_config.vmr_auth,
                    timeout=solace_config.vmr_timeout,
                    headers={'x-broker-name': solace_config.x_broker},
                    params=None
        )
        if su.ENABLE_LOGGING:
            su.log_http_roundtrip(resp)
        if resp.status_code != 200:
            return False, su.parse_bad_response(resp), dict(resp.headers)
        return True, su.parse_good_response(resp), dict(resp.headers)

    except requests.exceptions.ConnectionError as e:
        return False, str(e), dict()


def addPathValue(dictionary, path_array, value):
    if len(path_array) > 1:
        if path_array[0] not in dictionary.keys():
            dictionary[path_array[0]] = {}
        addPathValue(dictionary[path_array[0]], path_array[1:], value)
    else:
        dictionary[path_array[0]] = value


def run_module():
    """Entrypoint to module"""

    """Compose module arguments"""
    module_args = dict(
    )
    arg_spec = su.arg_spec_broker()
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        ansible_facts=dict()
    )

    solace_task = SolaceGetFactsTask(module)
    ok, resp_or_facts = solace_task.get_facts()
    if not ok:
        module.fail_json(msg=resp_or_facts, **result)

    result['ansible_facts']['solace'] = resp_or_facts
    module.exit_json(**result)


def main():
    """Standard boilerplate"""
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
