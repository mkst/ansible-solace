# ansible-solace
Ansible module(s) to configure Solace via [SEMP v2](https://docs.solace.com/SEMP/Using-SEMP.htm)

# QUICKSTART

In order to use these modules, Ansible needs to know about them. You can either copy the files into one of Ansible's expected locations (per [Adding modules and plugins locally](https://docs.ansible.com/ansible/latest/dev_guide/developing_locally.html#adding-a-module-locally)) or you can set the `ANSIBLE_MODULE_UTILS` and `ANSIBLE_LIBRARY` environment variables at runtime:

```bash
ANSIBLE_MODULE_UTILS=$(pwd)/lib/ansible/module_utils \
ANSIBLE_LIBRARY=$(pwd)/lib/ansible/modules \
ansible-playbook examples/solace_vpn.yml
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
# Add a queue to VPN foo
- name: Add a queue to VPN foo
  solace_queue:
    name: baz
    msg_vpn: foo
    settings:
      owner: "admin"
```

# MODULES

Status of the `solace_*` modules:

| Module | SEMP Endpoint | Type | Status | Example |
| ------ | ------------- |:----:|:------:|:-------:|
| solace_about | about | Query | | |
| [solace_acl_profile](lib/ansible/modules/network/solace/solace_acl_profile.py) | aclProfile | Action | :sunny: | [:page_facing_up:](examples/solace_acl_profile.yml) |
| [solace_acl_connect](lib/ansible/modules/network/solace/solace_acl_connect.py) | aclProfile | Action | :sunny: | [:page_facing_up:](examples/solace_acl_profile.yml) |
| [solace_acl_publish](lib/ansible/modules/network/solace/solace_acl_publish.py) | aclProfile | Action | :sunny: | [:page_facing_up:](examples/solace_acl_profile.yml) |
| [solace_acl_connect](lib/ansible/modules/network/solace/solace_acl_connect.py) | aclProfile | Action | :sunny: | [:page_facing_up:](examples/solace_acl_profile.yml) |
| [solace_acl_publish_exception](lib/ansible/modules/network/solace/solace_acl_publish_exception.py) (deprecated) | aclProfile | Action | :sunny: |  |
| [solace_acl_subscribe_exception](lib/ansible/modules/network/solace/solace_acl_subscribe_exception.py) (deprecated) | aclProfile | Action | :sunny: |  |
| solace_authorization_group | authorizationGroup | Action | | |
| [solace_bridge](lib/ansible/modules/network/solace/solace_bridge.py) | bridge | Action | :sunny: | [:page_facing_up:](examples/solace_bridge.yml)|
| [solace_bridge_remote_subscription](lib/ansible/modules/network/solace/solace_bridge_remote_subscription.py) | bridge | Action | :sunny: | [:page_facing_up:](examples/solace_bridge.yml)|
| [solace_bridge_remote_vpn](lib/ansible/modules/network/solace/solace_bridge_remote_vpn.py) | bridge | Action | :sunny: | [:page_facing_up:](examples/solace_bridge.yml)|
| [solace_bridge_tls_cn](lib/ansible/modules/network/solace/solace_bridge_tls_cn.py) | bridge | Action | :sunny: | [:page_facing_up:](examples/solace_bridge.yml)|
| [solace_client](lib/ansible/modules/network/solace/solace_client.py) | clientUsername | Action | :sunny: | [:page_facing_up:](examples/solace_client.yml) |
| [solace_client_profile](lib/ansible/modules/network/solace/solace_client_profile.py) | clientProfile | Action | :sunny: | |
| solace_jndi | jndi | Action | | |
| solace_mqtt_session | mqttSession | Action | | |
| [solace_queue](lib/ansible/modules/network/solace/solace_queue.py) | queue | Action | :sunny: | [:page_facing_up:](examples/solace_queue.yml) |
| solace_replay_log | replayLog | Action | | |
| solace_replicated_topic | replicatedTopic | Action | | |
| solace_rest_delivery_point | restDeliveryPoint | Action | | |
| [solace_subscription](lib/ansible/modules/network/solace/solace_subscription.py) | queue/{..}/subscriptions | Action | :sunny: | |
| [solace_topic](lib/ansible/modules/network/solace/solace_topic.py) | topicEndpoint | Action | :sunny: | |
| [solace_vpn](lib/ansible/modules/network/solace/solace_vpn.py) | msgVpn | Action | :sunny: | [:page_facing_up:](examples/solace_vpn.yml) |
| [solace_cert_authority](lib/ansible/modules/network/solace/solace_cert_authority.py) | certAuthority | Action | :sunny: | [:page_facing_up:](examples/solace_cert_authority.yml) |
| [solace_dmr_bridge](lib/ansible/modules/network/solace/solace_dmr_bridge.py) | dmrBridge | Action | :sunny: | [:page_facing_up:](examples/solace_dmr.yml) |
| [solace_dmr](lib/ansible/modules/network/solace/solace_dmr.py) | dmrCluster | Action | :sunny: | [:page_facing_up:](examples/solace_dmr.yml) |
| [solace_link](lib/ansible/modules/network/solace/solace_link.py) | dmrCluster | Action | :sunny: | [:page_facing_up:](examples/solace_dmr.yml) |
| [solace_link_remote_address](lib/ansible/modules/network/solace/solace_link_remote_address.py) | dmrCluster | Action | :sunny: | [:page_facing_up:](examples/solace_dmr.yml) |
| [solace_link_trusted_cn](lib/ansible/modules/network/solace/solace_link_trusted_cn.py) | dmrCluster | Action | :sunny: | [:page_facing_up:](examples/solace_dmr.yml) |


