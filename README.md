# Ansible Modules for Solace PubSub+ Event Brokers SEMP(v2) REST API

Ansible modules to configure Solace PubSub+ event brokers with [SEMP v2](https://docs.solace.com/SEMP/Using-SEMP.htm).

# QUICKSTART

## Install

Install ansible & python3.
Check that python points to the right version:
````bash
python -V

==> must be >=3.6
````

Install / upgrade ansible-solace:
````bash
pip3 install ansible-solace
````
Get the location of the package:
````bash
pip3 show ansible-solace

...
Location: .../Python/3.7/lib/python/site-packages
...

````
Add location to `set-ansible-env.sh`:
````bash
vi set-ansbile-env.sh

export ANSIBLE_SOLACE_HOME="ansible-solace-location"

````

Source the script:
````bash
source set-ansbile-env.sh

env | grep ANSIBLE
````

## Run the Example

### Pre-requisites

* a Solace PubSub+ Broker (Cloud or Software)
* credentials for the admin (sempv2) interface

### Configure the Inventory

Copy the example below to `brokers.inventory.json` and enter the values:

````json
{
  "all": {
    "hosts": {
      "{your broker name}": {
        "ansible_connection": "local",
        "sempv2_host": "{host, e.g. xxxx.messaging.solace.cloud}",
        "sempv2_port": 943,
        "sempv2_is_secure_connection": true,
        "sempv2_username": "{admin user name}",
        "sempv2_password": "{admin user password}",
        "sempv2_timeout": "60",
        "vpn": "{message vpn}"
      }
    }
  }
}
````

Copy the example below to `setUpQueue.yml`:

````yaml
-
  name: Setup A Queue with a Subscription

  hosts: all

  module_defaults:
    solace_subscription:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
    solace_queue:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"

  tasks:

    - name: Add / update the queue
      solace_queue:
        name: "my-queue"
        settings:
          egressEnabled: true
          ingressEnabled: true
          permission: "consume"
        state: present

    - name: Create subscription on queues
      solace_subscription:
        queue: "my-queue"
        topic: "my/subscription/topic"
        state: present

````
### Run the playbook

````bash
ansible-playbook -i brokers.inventory.json setUpQueue.yml
````

# TODO from here


# MODULES

Status of the `solace_*` modules:

| Module | SEMP Endpoint | Type | Status | Example |
| ------ | ------------- |:----:|:------:|:-------:|
| solace_about | about | Query | | |
| [solace_acl_profile](lib/ansible/modules/network/solace/solace_acl_profile.py) | aclProfile | Action | :sunny: | [:page_facing_up:](examples/solace_acl_profile.yml) |
| [solace_acl_connect](lib/ansible/modules/network/solace/solace_acl_connect.py) | aclProfile | Action | :sunny: | [:page_facing_up:](examples/solace_acl_profile.yml) |
| [solace_acl_publish](lib/ansible/modules/network/solace/solace_acl_publish.py) | aclProfile | Action | :sunny: | [:page_facing_up:](examples/solace_acl_profile.yml) |
| [solace_acl_subscribe](lib/ansible/modules/network/solace/solace_acl_subscribe.py) | aclProfile | Action | :sunny: | [:page_facing_up:](examples/solace_acl_profile.yml) |
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
| [solace_queue](lib/ansible/modules/network/solace/solace_queue.py) | queue | Action | :sunny: | [:page_facing_up:](examples/solace_queue.yml) [:page_facing_up:](examples/solace_queues_and_subscriptions.playbook.yml) |
| [solace_subscription](lib/ansible/modules/network/solace/solace_subscription.py) | queue/{..}/subscriptions | Action | :sunny: | [:page_facing_up:](examples/solace_queues_and_subscriptions.playbook.yml) |
| [solace_topic](lib/ansible/modules/network/solace/solace_topic.py) | topicEndpoint | Action | :sunny: | |
| solace_replay_log | replayLog | Action | | |
| solace_replicated_topic | replicatedTopic | Action | | |
| [solace_rdp](lib/ansible/modules/network/solace/solace_rdp.py) | restDeliveryPoint | Action | :sunny: | [:page_facing_up:](examples/solace_rdp.yml) |
| [solace_rdp_rest_consumer](lib/ansible/modules/network/solace/solace_rdp_rest_consumer.py) | restDeliveryPoint | Action | :sunny: | [:page_facing_up:](examples/solace_rdp.yml) |
| [solace_rdp_rest_consumer_trusted_common_name](lib/ansible/modules/network/solace/solace_rdp_rest_consumer_trusted_common_name.py) | restDeliveryPoint | Action | :sunny: |[:page_facing_up:](examples/solace_rdp.yml) |
| [solace_rdp_queue_binding](lib/ansible/modules/network/solace/solace_rdp_queue_binding.py) | restDeliveryPoint | Action | :sunny: | [:page_facing_up:](examples/solace_rdp.yml)|
| [solace_vpn](lib/ansible/modules/network/solace/solace_vpn.py) | msgVpn | Action | :sunny: | [:page_facing_up:](examples/solace_vpn.yml) |
| [solace_cert_authority](lib/ansible/modules/network/solace/solace_cert_authority.py) | certAuthority | Action | :sunny: | [:page_facing_up:](examples/solace_cert_authority.yml) |
| [solace_dmr_bridge](lib/ansible/modules/network/solace/solace_dmr_bridge.py) | dmrBridge | Action | :sunny: | [:page_facing_up:](examples/solace_dmr.yml) |
| [solace_dmr](lib/ansible/modules/network/solace/solace_dmr.py) | dmrCluster | Action | :sunny: | [:page_facing_up:](examples/solace_dmr.yml) |
| [solace_link](lib/ansible/modules/network/solace/solace_link.py) | dmrCluster | Action | :sunny: | [:page_facing_up:](examples/solace_dmr.yml) |
| [solace_link_remote_address](lib/ansible/modules/network/solace/solace_link_remote_address.py) | dmrCluster | Action | :sunny: | [:page_facing_up:](examples/solace_dmr.yml) |
| [solace_link_trusted_cn](lib/ansible/modules/network/solace/solace_link_trusted_cn.py) | dmrCluster | Action | :sunny: | [:page_facing_up:](examples/solace_dmr.yml) |

# Writing New Modules

[See Guide to Creating new Modules.](./GuideCreateModule.md)

# Open Issues

Open items to potentially enhance the framework.
[See Open Issues.](./OpenIssues.md)

---
The End.
