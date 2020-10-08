#!/usr/bin/python3
import sys
import traceback

from ansible.module_utils.basic import AnsibleModule
import re
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: ec2_key_info

short_description: Gets the list of AWS keys

version_added: "2.9"

description:
    - "The module gets a list of AWS keys."

author:
    - Bret Mullinix
'''

EXAMPLES = '''
# List all the modules
- name: Get Key Info
  ec2_key_info:
    aws_access_key: "{{ aws_access_key }}"
    aws_secret_key: "{{ aws_secret_key }}"
    region: "{{ region }}"

'''

RETURN = '''
---
KeyPairs:
- KeyPairId: key-05f7f5e306d3d35b9
  KeyFingerprint: fa:10:45:77:8f:35:9b:99:5f:98:1c:e2:d7:f0:ae:d3:75:1f:54:a5
  KeyName: my_keypair
  Tags: []
ResponseMetadata:
  RequestId: ed5f1abd-f73d-428d-93ea-7dc9763edf8b
  HTTPStatusCode: 200
  HTTPHeaders:
    x-amzn-requestid: ed5f1abd-f73d-428d-93ea-7dc9763edf8b
    content-type: text/xml;charset=UTF-8
    content-length: '491'
    date: Wed, 19 Aug 2020 19:29:33 GMT
    server: AmazonEC2
  RetryAttempts: 0
'''


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        aws_access_key=dict(type='str', required=True),
        aws_secret_key=dict(type='str', required=True),
        region=dict(type='str', required=True),

    )


    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        std_output=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    import boto3
    aws_access_key = module.params["aws_access_key"]
    aws_secret_key = module.params["aws_secret_key"]
    region = module.params["region"]

    try:
        client = boto3.client('ec2', aws_access_key_id=aws_access_key,
                          aws_secret_access_key=aws_secret_key,
                          region_name=region)
        result['std_output'] = client.describe_key_pairs()

    except Exception as ex:
        failure_message = 'Could not retrieve the AWS keys.  There was an error in retrieving them from AWS'
        result['std_output'] = traceback.format_exception(*sys.exc_info())
        module.fail_json(msg=failure_message, **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
