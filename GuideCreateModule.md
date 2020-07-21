# Guide to Creating a Module

This guide explains how to implement new modules using the framework.

1) Duplicate an existing module
   * path: `lib/ansible/modules/network/solace`
   * chose a module that is similar in functionality
   * duplicate the file:
     - naming convention: `solace_{sempv2-resource}`
     - all lowercase
     - no special characters
     - use underscore `_` not minus `-` to separate words

    Example:
    ````bash
    lib/ansible/modules/network/solace/solace_rdp_queue_binding.py
    ````

2) Adjust the code for the new module
   - check whether the module needs to use the API version to switch behaviour/params. See [Supporting Multiple API Versions](#supporting-multiple-api-versions).

3) Test the new module

4) Create an example

5) Update the README with your new module

# Adjusting the code for the new module

## License & metadata

Copy the license. Add your name & e-mail to the list.

Keep `ANSIBLE_METADATA` as is.

## Documentation

Provide at a minimum:

* module
* short_description
* description
  - add the link to the Sempv2 Resource.
  - add api versions supported if applicable. Example:  [solace_acl_publish_topic_exception](lib/ansible/modules/network/solace/solace_acl_publish_topic_exception.py).
* options
  - add module specific options
* author
  - add your name & e-mail
* example
  - add a short example

Note: use the fragments in `ansible/plugins/doc_fragments/solace.py`.
For Example:

````python
extends_documentation_fragment:
- solace.broker
- solace.vpn
- solace.settings
- solace.state

````

Test:
````bash
ansible-doc <module-name>
````

## Class name
Choose a class name. Use Pascal Case notation.
Pattern:
````python
class Solace{NewModuleName}Task(su.SolaceTask)
````

Example:
````python
class SolaceRdpQueueBindingTask(su.SolaceTask):
````

## Function `__init__()`

Leave unchanged.

## Concepts: The functions & their arguments

The following functions implement the respective Sempv2 actions:

````python
get_func()    # retrieve the object from the broker to ascertain it's state.
create_func() # create the object if it doesn't exist. state: present
update_func() # update an existing object. uses output of get_func() to see if updates are required. state: present
delete_func() # delete the object for state: absent
````

The arguments to these functions are dynamically constructed using the following mechanism:

````python
def {get|create|update|delete}_func(self, solace_config, get_args(), lookup_item(), settings)
````

## Function: get_args()

Specify here the array of required parameters from ansible that are passed to the functions.

This example will read `msg_vpn` and `rdp_name` from the ansible playbook and pass it to the functions:

````python
def get_args(self):
      return [self.module.params['msg_vpn'], self.module.params['rdp_name']]
````

## Function: lookup_item()

Returns the value of the unique key of the object as used in the ansible playbook.

_Note: always use `name` as the primary key as per ansible's convention._

Example:
````python
def lookup_item(self):
    return self.module.params['name']
````

## Constant: LOOKUP_ITEM_KEY

Set to the key name in the Sempv2 API. It maps the value returned by `lookup_item()` to the key in the API.

Example:
````python
LOOKUP_ITEM_KEY = 'queueBindingName'

````

## Function: get_func()

Retrieves the object from the broker. Used by the other functions to decide whether changes need to be applied.

Example:

````python
def get_func(self, solace_config, vpn, rdp_name, lookup_item_value):
      # Resrouce URL pattern:
      # GET /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/queueBindings/{queueBindingName}

      # construct the path_array to match the URL pattern:
      # su refers to lib/ansible/module_utils/network/solace_utils.py
      #
      # su.SEMP_V2_CONFIG = '/SEMP/v2/config'
      # su.MSG_VPNS = 'msgVpns'
      # vpn: argument set by get_args()
      # su.RDP_REST_DELIVERY_POINTS = 'restDeliveryPoints'
      # rdp_name: argument set by get_args()
      # su.RDP_QUEUE_BINDINGS = 'queueBindings'
      # lookup_item_value: return from lookup_item()
      path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.RDP_REST_DELIVERY_POINTS, rdp_name, su.RDP_QUEUE_BINDINGS, lookup_item_value]

      # call the resource
      # solace_config: leave as is
      # path_array: the URI constructed above
      # self.LOOKUP_ITEM_KEY: the constant defined above
      return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)
````

## Function: create_func()

Creates the object if it doesn't exist.

`state: present`

Example:
````python
def create_func(self, solace_config, vpn, rdp_name, name, settings=None):
      # Resrouce URL pattern:
      # POST /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/queueBindings

      # Provide any default values that make sense. Empty here.
      defaults = {}
      # Provide the mandatory key:value pairs for the POST call.
      mandatory = {
          'msgVpnName': vpn,
          'restDeliveryPointName': rdp_name,
          'queueBindingName': name
      }

      # data is the POST body for the Sempv2 call
      # note that settings are defined as optional here
      data = su.merge_dicts(defaults, mandatory, settings)

      # Construct the path array to match the URL pattern
      path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.RDP_REST_DELIVERY_POINTS, rdp_name, su.RDP_QUEUE_BINDINGS]
      # make the POST request
      return su.make_post_request(solace_config, path_array, data)
````

## Function: update_func()

Updates the object if it does exist already and if new settings/changes are required.

_Note: If no PATCH API exists, delete the entire update_func()._

`state: present`

Example:

````python
def update_func(self, solace_config, vpn, rdp_name, lookup_item_value, settings):
    # Resrouce URL pattern:
    # PATCH /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/queueBindings/{queueBindingName}
    path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.RDP_REST_DELIVERY_POINTS, rdp_name, su.RDP_QUEUE_BINDINGS, lookup_item_value]
    return su.make_patch_request(solace_config, path_array, settings)
````

## Function: delete_func()

Deletes the object.

`state: absent`

Example:

````python
def delete_func(self, solace_config, vpn, rdp_name, lookup_item_value):
    # Resrouce URL pattern:
    # DELETE /msgVpns/{msgVpnName}/restDeliveryPoints/{restDeliveryPointName}/queueBindings/{queueBindingName}
    path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.RDP_REST_DELIVERY_POINTS, rdp_name, su.RDP_QUEUE_BINDINGS, lookup_item_value]
    return su.make_delete_request(solace_config, path_array)

````

## Dict: module_args

Adjust the dictionary for the particular resource.

Example:

````python
"""Compose module arguments"""
module_args = dict(
    acl_profile_name=dict(type='str', required=True),
    topic_syntax=dict(type='str', default='smf'),
)
arg_spec = su.arg_spec_broker()
arg_spec.update(su.arg_spec_vpn())
arg_spec.update(su.arg_spec_crud())
arg_spec.update(su.arg_spec_semp_version())
# module_args override standard arg_specs
arg_spec.update(module_args)

module = AnsibleModule(
    argument_spec=arg_spec,
    supports_check_mode=True
)
````

## Task: solace_task

Replace the class name with the new class name.

Example:
````python
    solace_task = SolaceRdpQueueBindingTask(module)
````

## Supporting Multiple API Versions

See the following modules for examples:
- [solace_acl_publish_topic_exception](lib/ansible/modules/network/solace/solace_acl_publish_topic_exception.py).
- [solace_acl_subscribe_topic_exception](lib/ansible/modules/network/solace/solace_acl_subscribe_topic_exception.py).

In the playbook, use `solace_get_facts`.
See examples: [Solace Get Facts Playbook](examples/solace_get_facts.playbook.yml) & [ACL Profile Playbook](examples/solace_acl_profile.playbook.yml).

Create a lookup structure:

````python
KEY_LOOKUP_ITEM_KEY = "LOOKUP_ITEM_KEY"
  KEY_URI_SUBSCR_EX = "URI_SUBSCR_EX"
  KEY_TOPIC_SYNTAX_KEY = "TOPIC_SYNTAX_KEY"
  SEMP_VERSION_KEY_LOOKUP = {
      '2.13': {
          KEY_LOOKUP_ITEM_KEY: 'subscribeExceptionTopic',
          KEY_URI_SUBSCR_EX: 'subscribeExceptions',
          KEY_TOPIC_SYNTAX_KEY: 'topicSyntax'
      },
      '2.14': {
          KEY_LOOKUP_ITEM_KEY: 'subscribeTopicException',
          KEY_URI_SUBSCR_EX: 'subscribeTopicExceptions',
          KEY_TOPIC_SYNTAX_KEY: 'subscribeTopicExceptionSyntax'
      }
  }
````

Implement version 'switch' function:

````python
def lookup_semp_version(self, semp_version):
    if semp_version <= 2.13:
        return True, '2.13'
    elif semp_version >= 2.14:
        return True, '2.14'
    return False, ''

````

Use `self.get_semp_version_key()` function.

Example:

````python
def get_func(self, solace_config, vpn, acl_profile_name, topic_syntax, lookup_item_value):
    # vmr_sempVersion <= "2.13" : GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeExceptions/{topicSyntax},{subscribeExceptionTopic}
    # vmr_sempVersion >= "2.14": GET /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/subscribeTopicExceptions/{subscribeTopicExceptionSyntax},{subscribeTopicException}
    uri_subscr_ex = self.get_semp_version_key(self.SEMP_VERSION_KEY_LOOKUP, solace_config.vmr_sempVersion, self.KEY_URI_SUBSCR_EX)
    lookup_item_key = self.get_semp_version_key(self.SEMP_VERSION_KEY_LOOKUP, solace_config.vmr_sempVersion, self.KEY_LOOKUP_ITEM_KEY)

    ex_uri = ','.join([topic_syntax, lookup_item_value])
    path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.ACL_PROFILES, acl_profile_name, uri_subscr_ex, ex_uri]
    return su.get_configuration(solace_config, path_array, lookup_item_key)
````


---
The End.
