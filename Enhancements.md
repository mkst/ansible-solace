# Potential Enhancements

## Framework Enhancements

- Create a Test Framework & CI/CD Pipeline

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

## Modules

### Create

- [solace_queue_template](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/queueTemplate)
- [solace_authentication_oauth_provider](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/authenticationOauthProvider)
- [solace_authorization_group](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/authorizationGroup/getMsgVpnAuthorizationGroups)
- [solace_jndi](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/jndi)
- [solace_replay_log](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/replayLog)
- [solace_replicated_topic](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/replicatedTopic)
- [solace_topic_endpoint_template](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/topicEndpointTemplate)
- [solace_virtual_hostname](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/virtualHostname)

### Create get_&lt;module> modules

Create remaining *_get_* module for each module.

Examples: `solace_get_queues`, `solace_get_client_usernames`

### Update

  * [solace_rdp_rest_consumer_trusted_cn](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/restDeliveryPoint/getMsgVpnRestDeliveryPointRestConsumerTlsTrustedCommonNames)
    - deprecated since 2.17 - replaced by "Common Name validation has been replaced by Server Certificate Name validation".

---
The End.
