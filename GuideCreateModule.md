# Guide to Creating a Module

This guide walks through how new Sempv2 requests are implemented using the framework.

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
* options
  - copy the common options and add the module specific options.
* author
  - add your name & e-mail
* example
  - add a short example

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
module_args = dict(
    # always required
    name=dict(type='str', required=True),
    # Resource specific parameters
    rdp_name=dict(type='str', required=True),
    msg_vpn=dict(type='str', required=True),
    # framework parameters
    # do not change from here
    host=dict(type='str', default='localhost'),
    port=dict(type='int', default=8080),
    secure_connection=dict(type='bool', default=False),
    username=dict(type='str', default='admin'),
    password=dict(type='str', default='admin', no_log=True),
    settings=dict(type='dict', require=False),
    state=dict(default='present', choices=['absent', 'present']),
    timeout=dict(default='30', require=False),
    x_broker=dict(type='str', default='')
)
````

## Task: solace_task

Replace the class name with the new class name.

Example:
````python
    solace_task = SolaceRdpQueueBindingTask(module)
````

---
The End.
