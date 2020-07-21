#!/usr/bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
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

class ModuleDocFragment(object):

    # Documentation fragments for Solace modules
    BROKER = r'''
---
description:
- "Sempv2 Config Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/)."

options:
  host:
    description: Hostname of Solace Broker.
    required: false
    default: "localhost"
    type: str
  port:
    description: Management port of Solace Broker.
    required: false
    default: 8080
    type: int
  secure_connection:
    description: If true, use https rather than http.
    required: false
    default: false
    type: bool
  username:
    description: Administrator username for Solace Broker.
    required: false
    default: "admin"
    type: str
  password:
    description: Administrator password for Solace Broker.
    required: false
    default: "admin"
    type: str
  timeout:
    description: Connection timeout in seconds for the http request.
    required: false
    default: 10
    type: int
  x_broker:
    description: Custom HTTP header with the broker virtual router id, if using a SEMPv2 Proxy/agent infrastructure.
    required: false
    type: str
'''

    VPN = r'''
options:
  msg_vpn:
    description: The message vpn.
    required: true
    type: str
'''

    SETTINGS = r'''
options:
  settings:
    description: JSON dictionary of additional configuration, see Reference documentation.
    required: false
    type: dict
'''

    SEMP_VERSION = r'''
options:
  semp_version:
    description: The Semp API version of the broker. See M(solace_get_facts) for info on how to retrieve the version from the broker.
    required: true
'''

    STATE = r'''
options:
  state:
    description: Target state.
    required: false
    default: present
    type: str
    choices:
      - present
      - absent
'''

    QUERY = r'''
options:
  query_params:
    version_added: "0.3.0"
    description: The query parameters.
    required: false
    type: dict
    default: {}
    suboptions:
        select:
          description: Include in the response only selected attributes of the object, or exclude from the response selected attributes of the object. See the documentation for the select parameter.
          type: list
          default: []
          elements: str
        where:
          description: Include in the response only objects where certain conditions are true. See the the documentation for the where parameter.
          notes: URL encoded automatically, you can safely use '/, <, <=, >, >=, != .. '
          type: list
          default: []
          elements: str
'''

###
# The End.
