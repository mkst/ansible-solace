#!/usr/bin/python

# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
# MIT License

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
    }

DOCUMENTATION = '''
---
module: solace_vpn

short_description: Configure VPNs on Solace Appliances

version_added: "2.9"

description:
    - "Allows addition, removal and configuration of VPNs on Solace Applicances in an idempotent manner."

options:
    name:
        description:
            - This is the name of the VPN being configured
        required: true
    state:
        description:
            - Target state of the VPN, present/absent
        required: false
    host:
        description:
            - Hostname of Solace Appliance, default is "localhost"
        required: false
    port:
        description:
            - Management port of Solace Appliance, default is 8080
        required: false
    secure_connection:
        description:
            - If true use https rather than http for querying
        required: false
    username:
        description:
            - Administrator username for Solace Appliance, defaults is "admin"
        required: false
    password:
        description:
            - Administrator password for Solace Appliance, defaults is "admin"
        required: false
    settings:
        description:
            - JSON dictionary of additional configuration
        required: false
    timeout:
        description:
            - Connection timeout when making requests, defaults to 1 (second)
        required: false

author:
    - Mark Street (mkst@protonmail.com)
'''

EXAMPLES = '''
# Create a vpn with default settings
- name: Create vpn foo
  solace_vpn:
    name: foo
# Ensure a vpn called bar does not exist
- name: Remove vpn bar
  solace_vpn:
    name: bar
    state: absent
# Set specific vpn setting on foo
- name: Set MQTT listen port to 1234 on vpn foo
  solace_vpn:
    name: foo
    settings:
      serviceMqttPlainTextListenPort: 1234
'''

RETURN = '''
response:
    description: The response back from the Solace device
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
import ansible.module_utils.network.solace.solace_utils as solace

def run_module():
    """Entrypoint to module"""
    module_args = dict(
        name=dict(type='str', required=True),
        host=dict(type='str', default='localhost'),
        port=dict(type='int', default=8080),
        secure_connection=dict(type='bool', default=False),
        username=dict(type='str', default='admin'),
        password=dict(type='str', default='admin', no_log=True),
        settings=dict(type='dict', require=False),
        state=dict(default="present", choices=["absent", "present"]),
        timeout=dict(default=1, require=False)
    )
    result = dict(
        changed=False,
        response=dict()
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    solace_config = solace.SolaceConfig(
        vmr_host=module.params["host"],
        vmr_port=module.params["port"],
        vmr_auth=(module.params["username"], module.params["password"]),
        vmr_secure=module.params["secure_connection"],
        vmr_timeout=module.params["timeout"]
    )

    vpn_name = module.params["name"]
    vpn_settings = module.params["settings"]

    ok, resp = solace.get_configured_vpns(solace_config)

    if not ok:
        module.fail_json(msg=resp, **result)
    configured_vpns = resp

    if vpn_name in configured_vpns:
        if module.params["state"] == "absent":
            if not module.check_mode:
                ok, resp = solace.delete_vpn(solace_config, vpn_name)
                if not ok:
                    module.fail_json(msg=resp, **result)
            result["changed"] = True
        else:
            if len(vpn_settings.keys()):
                # compare new settings against configuration
                current_settings = configured_vpns[vpn_name]
                bad_keys = [key for key in vpn_settings if key not in current_settings.keys()]
                # fail if any unexpected settings found
                if len(bad_keys):
                    module.fail_json(msg="Invalid key(s): " + ", ".join(bad_keys), **result)

                changed_keys = [x for x in vpn_settings if vpn_settings[x] != current_settings[x]]

                if len(changed_keys):
                    delta_settings = {key:vpn_settings[key] for key in changed_keys}
                    ok, resp = solace.update_vpn(solace_config, vpn_name, settings=delta_settings)
                    if not ok:
                        module.fail_json(msg=resp, **result)

                    result["delta"] = delta_settings
                    result["response"] = resp
                    result["changed"] = True
            result["response"] = configured_vpns[vpn_name]


    else:
        if module.params["state"] == "present":
            if not module.check_mode:
                ok, resp = solace.create_vpn(solace_config, vpn_name, settings=vpn_settings)
                if ok:
                    result["response"] = resp
                else:
                    module.fail_json(msg=resp, **result)
            result["changed"] = True

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
