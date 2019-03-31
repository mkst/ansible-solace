# ansible-solace
Ansible module(s) to configure Solace via [SEMP v2](https://docs.solace.com/SEMP/Using-SEMP.htm)

# QUICKSTART

In order to use these modules, Ansible needs to know about them. You can either copy the files into one of Ansible's expected locations (per [Adding modules and plugins locally](https://docs.ansible.com/ansible/latest/dev_guide/developing_locally.html#adding-a-module-locally)) or you can set the `ANSIBLE_MODULE_UTILS` and `ANSIBLE_LIBRARY` environment variables at runtime:

```bash
ANSIBLE_MODULE_UTILS=$(pwd)/lib/ansible/module_utils \
ANSIBLE_LIBRARY=$(pwd)/lib/ansible/modules \
ansible-playbook examples/solace_vpn_add.yml
```
## EXAMPLES

```yaml
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
```

# MODULES

Status of the `solace_*` modules:

| Module | SEMP Endpoint | Type | Status |
| ------ | ------------- |:----:|:------:|
| solace_about | about | Query | |
| solace_acl_profile | aclProfile | Action | |
| solace_authorization_group | authorizationGroup | Action | |
| solace_bridge | bridge | Action | |
| solace_client_username | clientUsername | Action | |
| solace_client_profile | clientProfile | Action | |
| solace_jndi | jndi | Action | |
| solace_mqtt_session | mqttSession | Action | |
| solace_queue | queue | Action | |
| solace_replay_log | replayLog | Action | |
| solace_replicated_topic | replicatedTopic | Action | |
| solace_rest_delivery_point | restDeliveryPoint | Action | |
| solace_topic | topicEndpoint | Action | |
| [solace_vpn](modules/network/solace/solace_vpn.py) | msgVpn | Action | :sunny: |
