#!/usr/bin/env python

# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke <ricardo.gomez-ulmke@solace.com>
# MIT License

"""Collection of utility classes and functions to aid the solace_* modules."""

import re
import traceback
import logging
import json

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    REQUESTS_IMP_ERR = traceback.format_exc()
    HAS_REQUESTS = False

SEMP_V2_CONFIG = '/SEMP/v2/config'

""" VPN level reources """

MSG_VPNS = 'msgVpns'
TOPIC_ENDPOINTS = 'topicEndpoints'
ACL_PROFILES = 'aclProfiles'
ACL_PROFILES_CLIENT_CONNECT_EXCEPTIONS = 'clientConnectExceptions'
ACL_PROFILES_PUBLISH_TOPIC_EXCEPTIONS = 'publishTopicExceptions'
ACL_PROFILES_SUBSCRIBE_TOPIC_EXCEPTIONS = 'subscribeTopicExceptions'
ACL_PROFILES_PUBLISH_EXCEPTIONS = 'publishExceptions'
ACL_PROFILES_SUBSCRIBE_EXCEPTIONS = 'subscribeExceptions'
CLIENT_PROFILES = 'clientProfiles'
CLIENT_USERNAMES = 'clientUsernames'
DMR_BRIDGES = 'dmrBridges'
BRIDGES = 'bridges'
BRIDGES_REMOTE_MSG_VPNS = 'remoteMsgVpns'
BRIDGES_REMOTE_SUBSCRIPTIONS = 'remoteSubscriptions'
BRIDGES_TRUSTED_COMMON_NAMES = 'tlsTrustedCommonNames'

QUEUES = 'queues'
SUBSCRIPTIONS = 'subscriptions'

""" RDP Resources """
RDP_REST_DELIVERY_POINTS = 'restDeliveryPoints'
RDP_REST_CONSUMERS = 'restConsumers'
RDP_TLS_TRUSTED_COMMON_NAMES = 'tlsTrustedCommonNames'
RDP_QUEUE_BINDINGS = 'queueBindings'

""" DMR Resources """
DMR_CLUSTERS = 'dmrClusters'
LINKS = 'links'
REMOTE_ADDRESSES = 'remoteAddresses'
TLS_TRUSTED_COMMON_NAMES = 'tlsTrustedCommonNames'
""" cert authority resources """
CERT_AUTHORITIES = 'certAuthorities'

################################################################################################
# logging
ENABLE_LOGGING = False  # False to disable


def init_logging():
    logging.basicConfig(filename='ansible_solace.log',
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s(): %(message)s')
    logging.info('Module start #############################################################################################')
    return


if ENABLE_LOGGING:
    init_logging()


class SolaceConfig(object):
    """Solace Configuration object"""

    def __init__(self,
                 vmr_host,
                 vmr_port,
                 vmr_auth,
                 vmr_secure=False,
                 vmr_timeout=1,
                 x_broker=''):
        self.vmr_auth = vmr_auth
        self.vmr_timeout = float(vmr_timeout)

        self.vmr_url = ('https' if vmr_secure else 'http') + '://' + vmr_host + ':' + str(vmr_port)
        self.x_broker = x_broker


class SolaceTask:

    def __init__(self, module):
        self.module = module
        self.solace_config = SolaceConfig(
            vmr_host=self.module.params['host'],
            vmr_port=self.module.params['port'],
            vmr_auth=(self.module.params['username'], self.module.params['password']),
            vmr_secure=self.module.params['secure_connection'],
            vmr_timeout=self.module.params['timeout'],
            x_broker=self.module.params.get('x_broker', '')
        )
        return

    def do_task(self):

        if not HAS_REQUESTS:
            self.module.fail_json(msg='Missing requests module', exception=REQUESTS_IMP_ERR)

        result = dict(
            changed=False,
            response=dict()
        )

        crud_args = self.crud_args()

        settings = self.module.params['settings']

        if settings:
            # jinja treats everything as a string, so cast ints and floats
            settings = _type_conversion(settings)

        ok, resp = self.get_func(self.solace_config, *(self.get_args() + [self.lookup_item()]))

        if not ok:
            self.module.fail_json(msg=resp, **result)
        # else response was good
        current_configuration = resp
        # whitelist of configuration items that are not returned by GET
        whitelist = ['password']

        if self.lookup_item() in current_configuration:
            if self.module.params['state'] == 'absent':
                if not self.module.check_mode:
                    ok, resp = self.delete_func(self.solace_config, *(self.get_args() + [self.lookup_item()]))
                    if not ok:
                        self.module.fail_json(msg=resp, **result)
                result['changed'] = True
            else:
                if settings and len(settings.keys()):
                    # compare new settings against configuration
                    current_settings = current_configuration[self.lookup_item()]
                    bad_keys = [key for key in settings if key not in current_settings.keys()]
                    # remove whitelist items from bad_keys
                    bad_keys = [item for item in bad_keys if item not in whitelist]
                    # removed keys
                    removed_keys = [item for item in settings if item in whitelist]
                    # fail if any unexpected settings found
                    if len(bad_keys):
                        self.module.fail_json(msg='Invalid key(s): ' + ', '.join(bad_keys), **result)
                    # changed keys are those that exist in settings and don't match current settings
                    changed_keys = [x for x in settings if x in current_settings.keys()
                                    and settings[x] != current_settings[x]]
                    # add back in anything from the whitelist
                    changed_keys = changed_keys + removed_keys
                    # add any whitelisted items
                    if len(changed_keys):
                        delta_settings = {key: settings[key] for key in changed_keys}
                        crud_args.append(delta_settings)
                        if not self.module.check_mode:
                            ok, resp = self.update_func(self.solace_config, *crud_args)
                            result['response'] = resp
                            if not ok:
                                self.module.fail_json(msg=resp, **result)
                        result['delta'] = delta_settings
                        result['changed'] = True
                else:
                    result['response'] = current_configuration[self.lookup_item()]
        else:
            if self.module.params['state'] == 'present':
                if not self.module.check_mode:
                    if settings:
                        crud_args.append(settings)
                    ok, resp = self.create_func(self.solace_config, *crud_args)
                    if ok:
                        result['response'] = resp
                    else:
                        self.module.fail_json(msg=resp, **result)
                result['changed'] = True

        return result

    def get_func(self, solace_config, *args):
        return

    def create_func(self, solace_config, *args):
        return

    def update_func(self, solace_config, *args):
        return

    def delete_func(self, solace_config, *args):
        return

    def lookup_item(self):
        return

    def get_args(self):
        return []

    def crud_args(self):
        return self.get_args() + [self.lookup_item()]


# internal helper functions
def merge_dicts(*argv):
    data = dict()
    for arg in argv:
        if arg:
            data.update(arg)
    return data


def _build_config_dict(resp, key):
    if not type(resp) is dict:
        raise TypeError("argument 'resp' is not a 'dict' but {}. Hint: check you are using Sempv2 GET single item call and not a list of items.".format(type(resp)))
    # resp is a single dict, not an array
    # return an array with 1 element
    d = dict()
    d[resp[key]] = resp
    return d


def _type_conversion(d):
    for k, i in d.items():
        t = type(i)
        if (t == str) and re.search(r'^[0-9]+$', i):
            d[k] = int(i)
        elif (t == str) and re.search(r'^[0-9]+\.[0-9]$', i):
            d[k] = float(i)
        elif t == dict:
            d[k] = _type_conversion(i)
    return d


# response contains 1 dict if lookup_item/key is found
# if lookup_item is not found, response http-code: 400 with extra info in meta.error
def get_configuration(solace_config, path_array, key):
    ok, resp = make_get_request(solace_config, path_array)
    if ok:
        return True, _build_config_dict(resp, key)
    else:
        # check if responseCode=400 and error.code=6 ==> not found
        if (type(resp) is dict
                and resp['responseCode'] == 400
                and 'error' in resp.keys()
                and 'code' in resp['error'].keys()
                and resp['error']['code'] == 6):
            return True, dict()
    return False, resp


# request/response handling
def _parse_response(resp):
    if resp.status_code != 200:
        return False, _parse_bad_response(resp)
    return True, _parse_good_response(resp)


def _parse_good_response(resp):
    j = resp.json()
    logging.debug("response=\n%s", json.dumps(j, indent=2))
    if 'data' in j.keys():
        return j['data']
    return dict()


def _parse_bad_response(resp):
    j = resp.json()
    logging.debug("response=\n%s", json.dumps(j, indent=2))
    if 'meta' in j.keys() and \
            'error' in j['meta'].keys() and \
            'description' in j['meta']['error'].keys():
        # return j['meta']['error']['description']
        # we want to see the full message, including the code & request
        return j['meta']
    return 'Unknown error'


def _make_request(func, solace_config, path_array, json=None):
    if not type(path_array) is list:
        raise TypeError("argument 'path_array' is not an array but {}".format(type(path_array)))
    # ensure elements are 'url encoded'
    # except first one: /SEMP/v2/config
    paths = []
    for i, path_elem in enumerate(path_array):
        if i > 0:
            paths.append(path_elem.replace('/', '%2F'))
        else:
            paths.append(path_elem)
    path = '/'.join(paths)
    logging.debug("%s uri=%s", func, path)

    try:
        return _parse_response(
            func(
                solace_config.vmr_url + path,
                json=json,
                auth=solace_config.vmr_auth,
                timeout=solace_config.vmr_timeout,
                headers={'x-broker-name': solace_config.x_broker},
                params=None
            )
        )
    except requests.exceptions.ConnectionError as e:
        return False, str(e)


def make_get_request(solace_config, path_array):
    return _make_request(requests.get, solace_config, path_array)


def make_post_request(solace_config, path_array, json=None):
    return _make_request(requests.post, solace_config, path_array, json)


def make_delete_request(solace_config, path_array, json=None):
    return _make_request(requests.delete, solace_config, path_array, json)


def make_patch_request(solace_config, path_array, json=None):
    return _make_request(requests.patch, solace_config, path_array, json)

###
# The End.
