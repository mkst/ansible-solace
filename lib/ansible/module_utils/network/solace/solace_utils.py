#!/usr/bin/python

# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
# MIT License

import requests

SEMP_V2_CONFIG = "/SEMP/v2/config"
MSG_VPNS = "msgVpns"
TOPIC_ENDPOINTS = "topicEndpoints"
CLIENT_PROFILES = "clientProfiles"
CLIENT_USERNAMES = "clientUsernames"

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
        self.vmr_timeout = vmr_timeout

        self.vmr_url = ("https" if vmr_secure else "http") + "://" +\
                            vmr_host + ":" + str(vmr_port)

def get_configured_vpns(solace_config):
    """Pull out VPN configuration and return as dictionary keyed by msgVpn"""
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS])
    ok, resp = _make_get_request(solace_config, path)
    if ok:
        config = dict()
        for key in resp:
            config[key["msgVpnName"]] = key
        return (True, config)
    return (False, resp)

def get_vpn_details(solace_config, vpn="default"):
    """Pull configuration for specific VPN"""
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn])
    return _make_get_request(solace_config, path)

def get_topic_details(solace_config, topic, vpn="default"):
    """Pull configuration for specific Topic/Endpoint"""
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, TOPIC_ENDPOINTS, topic])
    return _make_get_request(solace_config, path)

def create_vpn(solace_config, vpn, settings=None):
    """Create a VPN"""
    defaults = {
        "enabled": True
    }
    mandatory = {
        "msgVpnName": vpn
    }
    data = dict()
    data.update(defaults)
    data.update(mandatory)
    if settings:
        data.update(settings)

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

def create_topic(solace_config, topic, owner="admin", vpn="default", settings=None):
    """Create a Topic/Endpoint"""
    defaults = {
        "ingressEnabled": True,
        "egressEnabled": True
    }
    mandatory = {
        "msgVpnName" : vpn,
        "topicEndpointName": topic,
        "owner": owner
    }
    data = dict()
    data.update(defaults)
    data.update(mandatory)
    if settings:
        data.update(settings)

    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, TOPIC_ENDPOINTS])

    return _make_post_request(solace_config, path, data)

def delete_topic(solace_config, topic, vpn="default"):
    """Delete a Topic/Endpoint"""
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, TOPIC_ENDPOINTS, topic])
    return _make_delete_request(solace_config, path)

def create_client_profile(solace_config, client_profile, vpn="default", settings=None):
    """Create a Client Profile"""
    defaults = {
        "allowCutThroughForwardingEnabled": True,
        "allowGuaranteedEndpointCreateEnabled": True,
        "allowGuaranteedMsgReceiveEnabled": True,
        "allowGuaranteedMsgSendEnabled": True,
        "allowTransactedSessionsEnabled": True
    }
    mandatory = {
        "clientProfileName": client_profile
    }
    data = dict()
    data.update(defaults)
    data.update(mandatory)
    if settings:
        data.update(settings)

    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, CLIENT_PROFILES])

    return _make_post_request(solace_config, path, data)

def delete_client_profile(solace_config, client_profile, vpn="default"):
    """Delete a Client Profile"""
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn,
                     CLIENT_PROFILES, client_profile])
    return _make_delete_request(solace_config, path)

def create_client(solace_config, username, password, client_profile,
                  vpn="default", settings=None):
    """Create a Client"""
    defaults = {
        "enabled": True
    }
    mandatory = {
        "clientUsername": username,
        "password": password,
        "clientProfileName": client_profile
    }
    data = dict()
    data.update(defaults)
    data.update(mandatory)
    if settings:
        data.update(settings)

    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, CLIENT_USERNAMES])

    return _make_post_request(solace_config, path, data)

def delete_client(solace_config, username, vpn="default"):
    """Delete a Client"""
    path = "/".join([SEMP_V2_CONFIG, MSG_VPNS, vpn, CLIENT_USERNAMES, username])
    return _make_delete_request(solace_config, path, None)

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

def _make_get_request(solace_config, path):
    resp = requests.get(solace_config.vmr_url + path,
                        auth=solace_config.vmr_auth,
                        timeout=solace_config.vmr_timeout)
    return _parse_response(resp)

def _make_post_request(solace_config, path, json=None):
    resp = requests.post(solace_config.vmr_url + path,
                         json=json,
                         auth=solace_config.vmr_auth,
                         timeout=solace_config.vmr_timeout)
    return _parse_response(resp)

def _make_delete_request(solace_config, path, json=None):
    resp = requests.delete(solace_config.vmr_url + path,
                           json=json,
                           auth=solace_config.vmr_auth,
                           timeout=solace_config.vmr_timeout)
    return _parse_response(resp)

def _make_patch_request(solace_config, path, json=None):
    resp = requests.patch(solace_config.vmr_url + path,
                          json=json,
                          auth=solace_config.vmr_auth,
                          timeout=solace_config.vmr_timeout)
    return _parse_response(resp)
