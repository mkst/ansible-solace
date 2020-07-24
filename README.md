# Ansible Modules for Solace PubSub+ Event Brokers SEMP(v2) REST API

Ansible modules to configure [Solace PubSub+ Event Brokers](https://solace.com/products/event-broker/) with [SEMP v2](https://docs.solace.com/SEMP/Using-SEMP.htm).


[Release Notes](./ReleaseNotes.md).

# QUICKSTART

## Install

Install ansible & python3.
Check that python points to the right version:
````bash
python -V   # ==> must be >=3.6
````

Install / upgrade ansible-solace:
````bash
pip3 install ansible-solace
````

**Package location:**

Get the location of the package:
````bash
pip3 show ansible-solace

Name: ansible-solace
...
Location: {your-install-path}/site-packages
...
````
If your Ansible install location is different to the ansible-solace package, you have to tell Ansible about these modules.
You can find a description here: [Adding modules and plugins locally](https://docs.ansible.com/ansible/latest/dev_guide/developing_locally.html#adding-a-module-locally)
or you can set the `ANSIBLE_MODULE_UTILS` and `ANSIBLE_LIBRARY` environment variables:

```bash
export ANSIBLE_MODULE_UTILS={your-install-path}/ansible/module_utils
export ANSIBLE_LIBRARY={your-install-path}/ansible/modules

# check:
ansible-doc -l | grep solace

```

_Note: You can also have a look at `set-ansible-env.sh`._

**Python interpreter:**

Depending on your OS/environment, you may have to set the python interpreter explicitly.
For example, set the `ANSIBLE_PYTHON_INTERPRETER` variable:
````bash
# find the location of your python installation
brew info python
# or
which python
# set the location
# e.g.
export ANSIBLE_PYTHON_INTERPRETER=/usr/local/bin/python
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

Copy the example below to `setup-queue.playbook.yml`:

````yaml
-
  name: Setup A Queue with a Subscription

  hosts: all

  module_defaults:
    solace_queue_subscription:
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
      solace_queue_subscription:
        queue: "my-queue"
        name: "my/subscription/topic"
        state: present

````
### Run the playbook

````bash
ansible-playbook -i brokers.inventory.json setup-queue.playbook.yml
````

# MODULES

Status of the `solace_*` modules:

| Module | SEMP Endpoint | Type | Status | Example |
| ------ | ------------- |:----:|:------:|:-------:|
| [solace_get_facts](lib/ansible/modules/network/solace/solace_get_facts.py) | about/... | Query | :sunny: | [:page_facing_up:](examples/solace_get_facts.playbook.yml) |
|  |  |  | | |
| [solace_acl_profile](lib/ansible/modules/network/solace/solace_acl_profile.py) | aclProfile | Action | :sunny: | [:page_facing_up:](examples/solace_acl_profile.playbook.playbook.yml) |
| [solace_acl_client_connect_exception](lib/ansible/modules/network/solace/solace_acl_client_connect_exception.py) | aclProfile | Action | :sunny: | [:page_facing_up:](examples/solace_acl_profile.playbook.yml) |
| [solace_acl_publish_topic_exception](lib/ansible/modules/network/solace/solace_acl_publish_topic_exception.py) | aclProfile | Action | :sunny: | [:page_facing_up:](examples/solace_acl_profile.playbook.yml) |
| [solace_acl_subscribe_topic_exception](lib/ansible/modules/network/solace/solace_acl_subscribe_topic_exception.py) | aclProfile | Action | :sunny: | [:page_facing_up:](examples/solace_acl_profile.playbook.yml) |
|   |   |   |   |   |
| [solace_bridge](lib/ansible/modules/network/solace/solace_bridge.py) | bridge | Action | :sunny: | [:page_facing_up:](examples/solace_bridge.yml)|
| [solace_bridge_remote_subscription](lib/ansible/modules/network/solace/solace_bridge_remote_subscription.py) | bridge | Action | :sunny: | [:page_facing_up:](examples/solace_bridge.yml)|
| [solace_bridge_remote_vpn](lib/ansible/modules/network/solace/solace_bridge_remote_vpn.py) | bridge | Action | :sunny: | [:page_facing_up:](examples/solace_bridge.yml)|
| [solace_bridge_tls_cn](lib/ansible/modules/network/solace/solace_bridge_tls_cn.py) | bridge | Action | :sunny: | [:page_facing_up:](examples/solace_bridge.yml)|
|   |   |   |   |   |
| [solace_cert_authority](lib/ansible/modules/network/solace/solace_cert_authority.py) | certAuthority | Action | :sunny: | [:page_facing_up:](examples/solace_cert_authority.yml) |
|   |   |   |   |   |
| [solace_get_client_usernames](lib/ansible/modules/network/solace/solace_get_client_usernames.py) | clientUsername | Query | :sunny: | [:page_facing_up:](test-test/solace_get_client_usernames/solace_get_client_usernames.playbook.yml) |
| [solace_client_username](lib/ansible/modules/network/solace/solace_client_username.py) | clientUsername | Action | :sunny: | [:page_facing_up:](examples/solace_client_username.yml) |
|   |   |   |   |   |
| [solace_client_profile](lib/ansible/modules/network/solace/solace_client_profile.py) | clientProfile | Action | :sunny: | |
|   |   |   |   |   |
| [solace_dmr_bridge](lib/ansible/modules/network/solace/solace_dmr_bridge.py) | dmrBridge | Action | :sunny: | [:page_facing_up:](examples/solace_dmr.yml) |
|   |   |   |   |   |
| [solace_dmr_cluster](lib/ansible/modules/network/solace/solace_dmr_cluster.py) | dmrCluster | Action | :sunny: | [:page_facing_up:](examples/solace_dmr_cluster.playbook.yml) |
| [solace_dmr_cluster_link](lib/ansible/modules/network/solace/solace_dmr_cluster_link.py) | dmrCluster | Action | :sunny: | [:page_facing_up:](examples/solace_dmr.playbook.yml) |
| [solace_dmr_cluster_link_remote_address](lib/ansible/modules/network/solace/solace_dmr_cluster_link_remote_address.py) | dmrCluster | Action | :sunny: | [:page_facing_up:](examples/solace_dmr.playbook.yml) |
| [solace_dmr_cluster_link_trusted_cn](lib/ansible/modules/network/solace/solace_dmr_cluster_link_trusted_cn.py) | dmrCluster | Action | :sunny: | [:page_facing_up:](examples/solace_dmr.playbook.yml) |
|   |   |   |   |   |
| [solace_get_mqtt_sessions](lib/ansible/modules/network/solace/solace_get_mqtt_sessions.py) | mqttSession | Query | :sunny: | [:page_facing_up:](test-test/solace_mqtt_session/solace_mqtt_session.playbook.yml) |
| [solace_get_mqtt_session_subscriptions](lib/ansible/modules/network/solace/solace_get_mqtt_session_subscriptions.py) | mqttSession | Query | :sunny: | [:page_facing_up:](test-test/solace_mqtt_session/solace_mqtt_session.playbook.yml) |
| [solace_mqtt_session](lib/ansible/modules/network/solace/solace_mqtt_session.py) | mqttSession | Action | :sunny: | [:page_facing_up:](test-test/solace_mqtt_session/solace_mqtt_session.playbook.yml) |
| [solace_mqtt_session_subscription](lib/ansible/modules/network/solace/solace_mqtt_session_subscription.py) | mqttSession | Action | :sunny: | [:page_facing_up:](test-test/solace_mqtt_session/solace_mqtt_session.playbook.yml) |
|   |   |   |   |   |
| [solace_get_queues](lib/ansible/modules/network/solace/solace_get_queues.py) | queue | Query | :sunny: | [:page_facing_up:](test-test/solace_get_queues/solace_get_queues.playbook.yml) |
| [solace_queue](lib/ansible/modules/network/solace/solace_queue.py) | queue | Action | :sunny: | [:page_facing_up:](examples/solace_queue.yml) [:page_facing_up:](examples/solace_queues_and_subscriptions.playbook.yml) |
| [solace_queue_subscription](lib/ansible/modules/network/solace/solace_queue_subscription.py) | queue | Action | :sunny: | [:page_facing_up:](examples/solace_queues_and_subscriptions.playbook.yml) |
|   |   |   |   |   |
| [solace_rdp](lib/ansible/modules/network/solace/solace_rdp.py) | restDeliveryPoint | Action | :sunny: | [:page_facing_up:](examples/solace_rdp.playbook.yml) |
| [solace_rdp_rest_consumer](lib/ansible/modules/network/solace/solace_rdp_rest_consumer.py) | restDeliveryPoint | Action | :sunny: | [:page_facing_up:](examples/solace_rdp.playbook.yml) |
| [solace_rdp_rest_consumer_trusted_cn](lib/ansible/modules/network/solace/solace_rdp_rest_consumer_trusted_cn.py) | restDeliveryPoint | Action | :sunny: |[:page_facing_up:](examples/solace_rdp.playbook.yml) |
| [solace_rdp_queue_binding](lib/ansible/modules/network/solace/solace_rdp_queue_binding.py) | restDeliveryPoint | Action | :sunny: | [:page_facing_up:](examples/solace_rdp.playbook.yml)|
|   |   |   |   |   |
| [solace_topic_endpoint](lib/ansible/modules/network/solace/solace_topic_endpoint.py) | topicEndpoint | Action | :sunny: | |
|   |   |   |   |   |
| [solace_vpn](lib/ansible/modules/network/solace/solace_vpn.py) | msgVpn | Action | :sunny: | [:page_facing_up:](examples/solace_vpn.yml) |

# Tips & Tricks

[See Tips & Tricks](./TipsTricks.md).

# Writing New Modules

[See Guide to Creating new Modules.](./GuideCreateModule.md)

# Enhancements

[See Potential Enhancements](./Enhancements.md).

---
The End.
