# Release Notes

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
