# Open Issues

## Create Install Package

  - http://packaging.python.org/tutorials/packaging-projects/

## Guide to Create new Sempv2 Modules

Write a guide how to create a new module - paint by numbers...

## Create Tests

  - https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html

## Framework Enhancements

### API Versions for Different Brokers

- Ability to gather broker facts: broker version & supported API version.
- Switch based on API version where required
- Sempv2: about resource

**Example: POST /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeTopicExceptions**
- API Version: ?
  - parameter: topicSyntax works
  - module: ``solace_acl_publish_exception.py``

- API Version: 2.14
  - parameter: subscribeTopicExceptionSyntax works
  - module: ``solace_acl_publish.py``

### Http Session

- every request opens a new connection
- change to use Session with a keep alive connection


### Logging, flag -vvv

- use ``module_stdout`` in the JSON output
- log entire request (uri, headers, body)
- log entire response
- see https://docs.ansible.com/ansible/latest/dev_guide/debugging.html

Not using -vvv should suppress it.

### Standardize Common Args

- have a standard, common args dict in solace_utils.py
- add here module specific args

```python
module_args = dict(
    # module specific
    name=dict(type='str', required=True),
    cert_content=dict(type='str', default=''),
    # standard args
    host=dict(type='str', default='localhost'),
    port=dict(type='int', default=8080),
    secure_connection=dict(type='bool', default=False),
    username=dict(type='str', default='admin'),
    password=dict(type='str', default='admin', no_log=True),
    settings=dict(type='dict', require=False),
    state=dict(default='present', choices=['absent', 'present']),
    timeout=dict(default='1', require=False),
    x_broker=dict(type='str', default='')
)
```

### Define a Group: ansible_solace?

- is it possible to define a group to set the defaults for the entire group and not every single module in a playbook?

- see: https://docs.ansible.com/ansible/latest/user_guide/playbooks_module_defaults.html

```yaml
- hosts: all
  module_defaults:
    # example of aws group
    group/aws:
      region: us-west-2
    # can we do this?
    group/ansible_solace:
      password: "{{ password }}"
      host: "{{ host }}"
      port: "{{ port }}"
      username: "{{ username }}"
      secure_connection: "{{ secure_connection }}"
      timeout: 25
      x_broker: "{{ x_broker | default() }}"
```


---
The End.
