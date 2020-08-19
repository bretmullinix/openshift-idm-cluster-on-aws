# 1st TDD Iteration --> Add AWS Public/Private Keys

Last updated: 08.19.2020

## Purpose

The purpose of this iteration is to add the ec2 instances **AWS public/private keys**
to the aws-ec2-instances/files directory.

## Procedure
1. Edit the aws-ec2-instances/defaults/main.yml and replace 
`ec2_instances: "{{ default[] }}"` with the following content:

    ```yaml
    ec2_instances:
        - name: my_instance
          ami: "ami-00594b9c138e6303d"
          instance_type: "t2.medium" 
          root_volume_size: 30
          subnet_name: "aws_infrastructure_control_subnet"
          key_name: "my_keypair"
        - name: your_instance
          ami: "ami-00594b9c138e6303d"
          instance_type: "t2.medium" 
          root_volume_size: 25
          subnet_name: "aws_infrastructure_control_subnet"
          key_name: "your_keypair"
    ```
1. cd aws-ec2-instances
1. mkdir library
1. cd library
1. Create the file called "ec2_key_info.py"
1. Edit the "ec2_key_info.py" file:

    ```python
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
        client = boto3.client('ec2', aws_access_key_id=aws_access_key,
                              aws_secret_access_key=aws_secret_key,
                              region_name=region)
    
        keypairs = client.describe_key_pairs()
        result['std_output'] = keypairs
    
        # in the event of a successful module execution, you will want to
        # simple AnsibleModule.exit_json(), passing the key/value results
        module.exit_json(**result)
    
    
    def main():
        run_module()
    
    
    if __name__ == '__main__':
        main()
    ```

1. cd aws-ec2-instances/molecule/default
1. Delete the **verify.yml** file.
1. Create a new **verify.yml** file with the following contents.

    ```yaml
    ---
    - name: Verify
      hosts: all
      tasks:
        - name: "Include aws-ec2-instance verify.yml"
          include_role:
            name: "aws-ec2-instances"
            tasks_from: "verify"
    ```
1. cd ../..
1. cd tasks
1. Create the file "verify.yml" and add the following contents:

    ```yaml

    ```

:construction:

[**<--Back to main instructions**](../readme.md#1stTDD)