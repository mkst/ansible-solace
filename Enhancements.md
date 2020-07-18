# Potential Enhancements

## Framework Enhancements

### GET list of objects for each object

Examples:
  - solace_get_queues
  - solace_get_acl_profiles
  - ...

Usage:
  - get a list of queues
  - use the result to remove all queues in a loop

### Define a Group

- group/solace to set the defaults for the entire group and not every single module in a playbook?

- see: https://docs.ansible.com/ansible/latest/user_guide/playbooks_module_defaults.html

```yaml
- hosts: all
  module_defaults:
    # example of aws group
    group/aws:
      region: us-west-2
    # new
    group/solace:
      password: "{{ password }}"
      host: "{{ host }}"
      port: "{{ port }}"
      username: "{{ username }}"
      secure_connection: "{{ secure_connection }}"
      timeout: 25
      x_broker: "{{ x_broker | default() }}"
```

## Modules

  - solace_mqtt_session

---
The End.
