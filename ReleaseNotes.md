# Release Notes

## Version: 0.3.0

### New Modules

    - solace_get_queues
    - solace_get_client_usernames
    - solace_client_username

### Removed Modules

    - solace_client

### Framework Changes

#### solace_utils

- framework for get_list() - to support get_xxxx modules
- modularized argument spec:
````python
def arg_spec_broker():
def arg_spec_vpn():
def arg_spec_settings():
def arg_spec_semp_version():
def arg_spec_state():
def arg_spec_name():
def arg_spec_crud():
def arg_spec_query():
````

#### Document Fragments

Introduced `ansible/plugins/doc_fragments/solace.py`. Modularized documentation fragments.


## Version: 0.2.1

### New Modules
    - solace_get_facts
    - solace_acl_publish_topic_exception
    - solace_acl_subscribe_topic_exception
    - solace_acl_client_connect_exception
    - solace_rdp_rest_consumer_trusted_cn
    - solace_queue_subscription
    - solace_topic_endpoint
    - solace_dmr_cluster
    - solace_dmr_cluster_link
    - solace_dmr_cluster_link_remote_address
    - solace_dmr_cluster_link_trusted_cn

#### Module: `solace_get_facts`

Some modules require the Semp API version number to switch behaviour depending on the version.
This module uses the /about/api resource to retrieve the version number and add it to `ansible_facts`.
Subsequent modules can use the output stored in `ansible_facts`.
See example playbooks:

- [Solace Get Facts Playbook](examples/solace_get_facts.playbook.yml)
- [ACL Profile Playbook](examples/solace_acl_profile.playbook.yml)

### Removed Modules

    - solace_acl_publish
    - solace_acl_publish_exception
    - solace_acl_subscribe
    - solace_acl_subscribe_exception
    - solace_acl_connect
    - solace_rdp_rest_consumer_trusted_common_name
    - solace_subscription
    - solace_topic
    - solace_dmr
    - solace_link
    - solace_link_trusted_cn

### Framework Changes

#### solace_utils

    - modules can now switch based on semp API version
    - logging (ansible-solace.log) now controllable via env var: ANSIBLE_SOLACE_ENABLE_LOGGING=[true|false]
    - added 'compose_module_args' so each module only has to provide their own specific arguments


---
The End.
