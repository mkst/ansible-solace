#!/usr/bin/python

# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
# MIT License

import requests

SEMP_V2_CONFIG = "/SEMP/v2/config"
MSG_VPNS = "msgVpns"
TOPIC_ENDPOINTS = "topicEndpoints"
CLIENT_PROFILES = "clientProfiles"
CLIENT_USERNAMES = "clientUsernames"
QUEUES = "queues"
SUBSCRIPTIONS = "subscriptions"

""" Collection of utility classes and functions to aid the solace_* modules. """
class SolaceConfig(object):
    """Solace Configuration object"""
    def __init__(self,
                 vmr_host,
                 vmr_port,
                 vmr_auth,
                 vmr_secure=False,
                 vmr_timeout=1):

        self.vmr_auth = vmr_auth
        self.vmr_timeout = float(vmr_timeout)

        self.vmr_url = ("https" if vmr_secure else "http") + "://" +\
                            vmr_host + ":" + str(vmr_port)

### Ansible Module handler

def perform_module_actions(module,
                           lookup_item,
                           settings,
                           get_func,
                           get_args,
                           create_func,
                           delete_func,
                           update_func):

    solace_config = SolaceConfig(
        vmr_host=module.params["host"],
        vmr_port=module.params["port"],
        vmr_auth=(module.params["username"], module.params["password"]),
        vmr_secure=module.params["secure_connection"],
        vmr_timeout=module.params["timeout"]
    )

    result = dict(
        changed=False,
        response=dict()
    )

    crud_args = get_args + [lookup_item]

    settings = module.params["settings"]

    ok, resp = get_func(solace_config, *get_args)

    if not ok:
        module.fail_json(msg=resp, **result)
    configured = resp

    whitelist = ["password"]


    if lookup_item in configured:
        if module.params["state"] == "absent":
            if not module.check_mode:
                ok, resp = delete_func(solace_config, *crud_args)
                if not ok:
                    module.fail_json(msg=resp, **result)
            result["changed"] = True
        else:
            if settings and len(settings.keys()):
                # compare new settings against configuration
                current_settings = configured[lookup_item]
                bad_keys = [key for key in settings if key not in current_settings.keys()]

                # remove whitelist items from bad_keys
                bad_keys = [item for item in bad_keys if not item in whitelist]
                # removed keys
                removed_keys = [item for item in settings if item in whitelist]
                # fail if any unexpected settings found
                if len(bad_keys):
                    module.fail_json(msg="Invalid key(s): " + ", ".join(bad_keys), **result)

                changed_keys = [x for x in settings if x in current_settings.keys() and settings[x] != current_settings[x]]
                # add back in anything from the whitelist
                changed_keys = changed_keys + removed_keys

                # add any whitelisted items
                if len(changed_keys):
                    delta_settings = {key:settings[key] for key in changed_keys}
                    crud_args.append(delta_settings)
                    ok, resp = update_func(solace_config, *crud_args)
                    if not ok:
                        module.fail_json(msg=resp, **result)

                    result["delta"] = delta_settings
                    result["response"] = resp
                    result["changed"] = True
            result["response"] = configured[lookup_item]
    else:
        if module.params["state"] == "present":
            if not module.check_mode:
                ok, resp = create_func(solace_config, *crud_args)
                if ok:
                    result["response"] = resp
                else:
                    module.fail_json(msg=resp, **result)
            result["changed"] = True

    return result

### GETTERS

def get_configured_vpns(solace_config):
    """Pull out VPN configuration and return as dictionary keyed by VPN name"""
    path_array = [SEMP_V2_CONFIG, MSG_VPNS]
    return _get_configuration(solace_config, path_array, "msgVpnName")

def get_configured_client_profiles_for_vpn(solace_config, vpn):
    """Pull configuration for all Client Profiles associated with a given VPN"""
    path_array = [SEMP_V2_CONFIG, MSG_VPNS, vpn, CLIENT_PROFILES]
    return _get_configuration(solace_config, path_array, "clientProfileName")

def get_configured_clients_for_vpn(solace_config, vpn):
    """Pull configuration for all Clients associated with a given VPN"""
    path_array = [SEMP_V2_CONFIG, MSG_VPNS, vpn, CLIENT_USERNAMES]
    return _get_configuration(solace_config, path_array, "clientUsername")

def get_configured_queues_for_vpn(solace_config, vpn):
    """Pull configuration for all Queues associated with a given VPN"""
    path_array = [SEMP_V2_CONFIG, MSG_VPNS, vpn, QUEUES]
    return _get_configuration(solace_config, path_array, "queueName")

def get_configured_topic_endpoints_for_vpn(solace_config, vpn):
    """Pull configuration for all Topic/Endpoints associated with a given VPN"""
    path_array = [SEMP_V2_CONFIG, MSG_VPNS, vpn, TOPIC_ENDPOINTS]
    return _get_configuration(solace_config, path_array, "topicEndpointName")

def get_configured_subscriptions_for_vpn_and_queue(solace_config, vpn, queue):
    """Pull configuration for all Subscriptions associated with a given VPN and Queue"""
    path_array = [SEMP_V2_CONFIG, MSG_VPNS, vpn, QUEUES, queue, SUBSCRIPTIONS]
    return _get_configuration(solace_config, path_array, "subscriptionTopic")

### MESSAGE VPN

def create_vpn(solace_config, vpn, settings=None):
    """Create a VPN"""
    defaults = {
        "enabled": True
    }
    mandatory = {
        "msgVpnName": vpn
    }
    data = _merge_dicts(defaults, mandatory, settings)
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS])

    return _make_post_request(solace_config, path, data)

def update_vpn(solace_config, vpn, settings):
    """Update an existing VPN"""
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn])
    return _make_patch_request(solace_config, path, settings)

def delete_vpn(solace_config, vpn):
    """Delete a VPN"""
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn])
    return _make_delete_request(solace_config, path)

### QUEUES

def create_queue(solace_config, vpn, queue, settings=None):
    """Create a Queue"""
    defaults = {}
    mandatory = {
        "msgVpnName": vpn,
        "queueName": queue
    }
    data = _merge_dicts(defaults, mandatory, settings)
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, QUEUES])

    return _make_post_request(solace_config, path, data)

def update_queue(solace_config, vpn, queue, settings):
    """Update an existing Queue"""
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, QUEUES, queue])
    return _make_patch_request(solace_config, path, settings)

def delete_queue(solace_config, vpn, queue):
    """Delete a Queue"""
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, QUEUES, queue])
    return _make_delete_request(solace_config, path)

### TOPICS

def create_topic_endpoint(solace_config, vpn, topic, settings=None):
    """Create a Topic/Endpoint"""
    defaults = {}
    mandatory = {
        "msgVpnName" : vpn,
        "topicEndpointName": topic
    }
    data = _merge_dicts(defaults, mandatory, settings)
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, TOPIC_ENDPOINTS])

    return _make_post_request(solace_config, path, data)

def update_topic_endpoint(solace_config, vpn, topic, settings):
    """Update an existing Topic/Endpoint"""
    # escape forwardslashes
    topic = topic.replace("/","%2F")
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, TOPIC_ENDPOINTS, topic])
    return _make_patch_request(solace_config, path, settings)

def delete_topic_endpoint(solace_config, vpn, topic):
    """Delete a Topic/Endpoint"""
    # escape forwardslashes
    topic = topic.replace("/","%2F")
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, TOPIC_ENDPOINTS, topic])
    return _make_delete_request(solace_config, path)

### SUBSCRIPTIONS

def create_subscription(solace_config, vpn, queue, topic, settings=None):
    """Create a Subscription for a Topic/Endpoint on a Queue"""
    defaults = {}
    mandatory = {
        "subscriptionTopic":topic
    }
    data = _merge_dicts(defaults, mandatory, settings)
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, QUEUES, queue, SUBSCRIPTIONS])

    return _make_post_request(solace_config, path, data)

def update_subscription(solace_config, vpn, queue, topic, settings):
    """Update an existing Subscription"""
    # escape forwardslashes
    topic = topic.replace("/","%2F")
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, QUEUES, queue, SUBSCRIPTIONS, topic])
    return _make_patch_request(solace_config, path, settings)

def delete_subscription(solace_config, vpn, queue, topic):
    """Delete a Subscription"""
    # escape forwardslashes
    topic = topic.replace("/","%2F")
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, QUEUES, queue, SUBSCRIPTIONS, topic])
    return _make_delete_request(solace_config, path)

### CLIENT PROFILES

def create_client_profile(solace_config, vpn, client_profile, settings=None):
    """Create a Client Profile"""
    defaults = {
    }
    mandatory = {
        "clientProfileName": client_profile
    }
    data = _merge_dicts(defaults, mandatory, settings)
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, CLIENT_PROFILES])

    return _make_post_request(solace_config, path, data)

def update_client_profile(solace_config, vpn, client_profile, settings=None):
    """Update an existing Client Profile"""
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, CLIENT_PROFILES, client_profile])
    return _make_patch_request(solace_config, path, settings)

def delete_client_profile(solace_config, vpn, client_profile):
    """Delete a Client Profile"""
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, CLIENT_PROFILES, client_profile])
    return _make_delete_request(solace_config, path)

### CLIENTS

def create_client(solace_config, vpn, client, settings=None):
    """Create a Client"""
    defaults = {
        "enabled": True
    }
    mandatory = {
        "clientUsername": client,
    }
    data = _merge_dicts(defaults, mandatory, settings)
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, CLIENT_USERNAMES])

    return _make_post_request(solace_config, path, data)

def update_client(solace_config, vpn, client, settings=None):
    """Update an existing Client"""
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, CLIENT_USERNAMES, client])
    return _make_patch_request(solace_config, path, settings)

def delete_client(solace_config, vpn, client):
    """Delete a Client"""
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, CLIENT_USERNAMES, client])
    return _make_delete_request(solace_config, path, None)

### internal helper functions
def _merge_dicts(*argv):
    data = dict()
    for arg in argv:
        if arg:
            data.update(arg)
    return data

def _build_config_dict(resp, key):
    d = dict()
    for k in resp:
        d[k[key]] = k
    return d

def _get_configuration(solace_config, path_array, key):
    path = "/".join(path_array)
    ok, resp = _make_get_request(solace_config, path)
    if ok:
        return (True, _build_config_dict(resp, key))
    return (False, resp)

### request/response handling
def _parse_response(resp):
    if resp.status_code is not 200:
        return (False, _parse_bad_response(resp))
    return (True, _parse_good_response(resp))

def _parse_good_response(resp):
    j = resp.json()
    if "data" in j.keys():
        return j["data"]
    return dict()

def _parse_bad_response(resp):
    j = resp.json()
    if "meta" in j.keys() and \
       "error" in j["meta"].keys() and \
       "description" in j["meta"]["error"].keys():
        return j["meta"]["error"]["description"]
    return "Unknown error"

def _make_request(func, solace_config, path, json=None):
    if func is requests.get:
        path += "?count=1000" # TODO: variable-ise this
    try:
        return _parse_response(
            func(
                solace_config.vmr_url + path,
                json=json,
                auth=solace_config.vmr_auth,
                timeout=solace_config.vmr_timeout
            )
        )
    except requests.exceptions.ConnectionError as e:
        return (False, str(e))

def _make_get_request(solace_config, path):
    return _make_request(requests.get, solace_config, path)

def _make_post_request(solace_config, path, json=None):
    return _make_request(requests.post, solace_config, path, json)

def _make_delete_request(solace_config, path, json=None):
    return _make_request(requests.delete, solace_config, path, json)

def _make_patch_request(solace_config, path, json=None):
    return _make_request(requests.patch, solace_config, path, json)
