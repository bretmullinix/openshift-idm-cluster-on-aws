#!/usr/bin/python3

from ansible.module_utils.basic import AnsibleModule
import re
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: get_dnf_modules

short_description: Gets the list of DNF modules.

version_added: "2.9"

description:
    - "The module gets a list of DNF modules installed."

author:
    - Bret Mullinix
'''

EXAMPLES = '''
# List all the modules
- name: Get List of modules
  get_dnf_modules:

- name: Determine if maven exists in the list of modules
  get_dnf_modules:
    module_name: maven

- name: Determine if maven is installed
  get_dnf_modules:
    module_name: maven
    installed: true
- name: Determine if maven is enabled
  get_dnf_modules:
    module_name: maven
    enabled: true
'''

RETURN = '''
dnf_module_output:
    description: All the dnf modules on the server
    type: str
    returned: always
found_module_line:
    description: If a module_name was specified, the line the module_name was found in
    type: str
    returned: conditionally
'''


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        module_name=dict(type='str', required=False),
        installed=dict(type='bool', required=False, default=False),
        enabled=dict(type='bool', required=False, default=False)
    )


    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        dnf_module_output=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    dnf_module_state = "present"
    module_name = module.params["module_name"]
    installed = module.params["installed"]
    enabled = module.params["enabled"]
    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    import subprocess
    dnf_command_to_run = ['dnf','module', 'list', '--all']
    if installed:
        dnf_command_to_run = ['dnf','module', 'list', '--installed']
        dnf_module_state = "installed"
    elif enabled:
        dnf_command_to_run = ['dnf','module', 'list', '--enabled']
        dnf_module_state = "enabled"

    process = subprocess.Popen(dnf_command_to_run,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE
                               )
    stdout, stderr = process.communicate()

    raw_output = stdout.decode("utf-8").splitlines()
    has_module = False
    if module_name:
        for line in raw_output:
            if module_name in line:
                has_module = True
                result['found_module_line'] = line
                break

    result['dnf_module_output'] = raw_output

    # output
    if module_name and has_module is False:
        failure_message = 'The module called \'{0}\' is not {1}.'.format(module_name, dnf_module_state)
        module.fail_json(msg=failure_message, **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
