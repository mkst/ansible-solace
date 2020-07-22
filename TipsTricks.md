# Tips & Tricks

## Using the API Version in Playbooks

The `settings` fieldnames can differ from version to version.
Here are some examples of how to deal with it.

````yaml
# main playbook

tasks:

- name: Get Solace Facts
  solace_get_facts:

- include_vars:
    file: "./lib/mqtt.vars.json"
    name: target_list

- name: Adding Mqtt Sessions
  include_tasks: mqtt.tasks.yml
  loop: "{{ target_list.mqttSessions }}"
  loop_control:
    loop_var: mqtt_session_item
````

````yaml

# mqtt.tasks.yml

- name: Update Mqtt Session
  # switch settings from vars
  solace_mqtt_session:
    mqtt_session_client_id: "{{ mqtt_session_item.mqttSessionClientId }}"
    settings: "{{ mqtt_session_item.settings._gt_eq_2_14 if ansible_facts.solace.about.api.sempVersion | float >= 2.14 else omit }}"
    state: present

- name: Update Mqtt Session
  # skip task if version not correct
  solace_mqtt_session:
    mqtt_session_client_id: "{{ mqtt_session_item.mqttSessionClientId }}"
    settings:
      queueMaxMsgSize: 200000
      queueMaxBindCount: 10
    state: present
  when: ansible_facts['solace']['about']['api']['sempVersion'] | float >= 2.14

````

The include file:

````json
{
  "mqttSessions": [
    {
      "mqttSessionClientId": "ansible-solace_test_mqtt__1__",
      "settings": {
        "_gt_eq_2_14": {
          "queueMaxMsgSize": 200000,
          "queueMaxBindCount": 10
        }
      },
      "subscriptions": [
        "ansible-solace/test/__1__/topic/subscription/1/>",
        "ansible-solace/test/__1__/topic/subscription/2/>",
        "ansible-solace/test/__1__/topic/subscription/3/>"
        ]
    },
    {
      "mqttSessionClientId": "ansible-solace_test_mqtt__2__",
      "subscriptions": [
        "ansible-solace/test/__2__/topic/subscription/1/>",
        "ansible-solace/test/__2__/topic/subscription/2/>",
        "ansible-solace/test/__2__/topic/subscription/3/>"
        ]
    }
  ]
}

````
---
The End.
