# 1st TDD Iteration --> Add AWS Public/Private Keys

Last updated: 08.20.2020

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
    - name: List all EC2 key pairs
      ec2_key_info:
        aws_access_key: "{{ aws_access_key }}"
        aws_secret_key: "{{ aws_secret_key }}"
        region: "{{ aws_region }}"
      register: result
    
    - name: Create Keys Facts
      set_fact:
        the_keys: "{{ result.std_output.KeyPairs }}"
      when: result is defined and result.std_output is defined and result.std_output.KeyPairs is defined
    
    - name: Initialize an empty list for the key names
      set_fact:
        the_key_names: "{{ [] }}"
    - name: Build a list of all the key names
      set_fact:
        the_key_names: "{{ the_key_names }} + [ '{{ item.KeyName }}' ]"
      with_items: "{{ the_keys }}"
      when: the_keys is defined
    
    - name: Fail if all keys don't exist
      fail:
        msg: "The Key '{{ item.key_name }}' does not exist in AWS."
      with_items: "{{ ec2_instances }}"
      when: item.key_name not in the_key_names
    
    - name: List the private keys that you have
      find:
        paths: "{{role_path}}/files/private_keys"
      register: output_private_key_files
      delegate_to: localhost
    
    - name: Initialize private_key_files to an empty list
      set_fact:
        private_key_files: "{{ [] }}"
    
    - name: Populate the private_key_files variable with the private key file names
      set_fact:
        private_key_files: "{{ private_key_files }} + [ '{{ item.path |  basename }}' ]"
      with_items: "{{ output_private_key_files.files }}"
      when: output_private_key_files.files is defined
    
    - name: Fail if we have no private key files
      fail:
        msg: >
           We don't have any private key files.
           Please create the files in the 'files/private_keys' directory by
           placing each private key in its respective file (each file is named
           as the AWS private key name).  If you are not using the key in AWS,
           delete the key out of AWS and re-run the role.
      when:  private_key_files | length  == 0
    
    - name: Fail if a key doesn't exist but should in the 'files/private_keys' directory
      fail:
        msg: >
          The Key '{{ item.key_name }}' does not exist in the 'files/private_keys' directory of the role.
          Please create the file '{{ item.key_name }}' in the 'files/private_keys' directory and,
          place your private key in the file, or if you are not using the key in AWS,
          delete the key out of AWS and re-run the role
      with_items: "{{ ec2_instances }}"
      when:  item.key_name not in private_key_files

    ```

1. **RED** --> Test for the existence of the **AWS key pairs**.

    1. cd aws-ec2-instances
    1. Run `molecule converge`
    1. The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Add the **AWS key pairs** to the ansible role.

    1. cd aws-ec2-instances/tasks
    1. mkdir main
    1. mkdir verify
    1. cd main
    1. Create the file called **create_key_pairs.yml** and add the
    following content.
    
        ```yaml
        - name: create a new ec2 key pair, returns generated private key
          ec2_key:
            name: "{{ current_key }}"
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            state: present
          register: key_pair_details
        
        
        - name: Set Key Pair Facts
          set_fact:
            aws_keypair: "{{ key_pair_details['key'] }}"
        
        
        - name: Copy the private key to a file so we can ssh into it
          copy:
            content: "{{ aws_keypair['private_key'] }}"
            dest: "{{role_path}}/files/private_keys/{{current_key}}"
          delegate_to: localhost

        ```
    1. cd .. 
    1. Add the following tasks to the "main.yml" file.
    
        ```yaml
        ---
        - name: List all EC2 key pairs
          ec2_key_info:
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
          register: result
        
        - name: Create Keys Facts
          set_fact:
            the_keys: "{{ result.std_output.KeyPairs }}"
          when: result is defined and result.std_output is defined and result.std_output.KeyPairs is defined
        
        - name: Initialize an empty list for the key names
          set_fact:
            the_key_names: "{{ [] }}"
        
        - name: Build a list of all the key names
          set_fact:
            the_key_names: "{{ the_key_names }} + [ '{{ item.KeyName }}' ]"
          with_items: "{{ the_keys }}"
          when: the_keys is defined
        
        - name: Create the files/private_keys directory
          file:
            path: "{{ role_path }}/files/private_keys"
            state: directory
            mode: '0755'
          delegate_to: localhost
        
        - name: Create those keys that were not defined
          include: "{{ role_path }}/tasks/main/create_key_pairs.yml current_key={{ item.key_name }}"
          with_items: "{{ ec2_instances }}"
          when: item.key_name not in the_key_names
        ```
    1. cd ../..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**
       and creates the **AWS public/private keys** and places the private keys
       in the **aws-ec2-instances/files/private_keys** folder.
    
    1. Run `molecule verify`. The test should pass.  The test represents
       the **Green** in the **Red, Green, Refactor** iteration of TDD.
  
1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **aws-ec2-instances/tasks/verify.yml** looks a 
       little messy with all the tasks checking for the
       existence of IDM.  Let's move the tasks to a separate file.
    
        1. Create the file **aws-ec2-instances/tasks/verify/check-if-the-aws-keys-are-present.yml**  
        1. Remove all the content from the **aws-ec2-instances/tasks/verify.yml**
           and place the contents in the **check-if-the-aws-keys-are-present.yml**.
        1. In the **aws-ec2-instances/tasks/verify.yml**, add the following content to the end:
        
            ```yaml
               - name: Check if the AWS Keys are present.
                 include_tasks: "{{ role_path }}/tasks/verify/check-if-the-aws-keys-are-present.yml"
           ```
        1. Run `molecule test` to ensure the role works as intended.
        
    1. We have not completed our refactoring.  The **aws-ec2-instances/tasks/main.yml**
       file looks messy as well. 
        
        1. Create the file **aws-ec2-instances/tasks/main/add-aws-keys.yml**  
    
            1. Remove all the content from the **aws-ec2-instances/tasks/main.yml**
               and place the contents in the **add-aws-keys.yml**.
                
            1. In the **aws-ec2-instances/tasks/main.yml**, add the following content to the end:
                
                 ```yaml
                  - name: Add AWS Keys
                    include_tasks: "{{ role_path }}/tasks/main/add-aws-keys.yml"
                 ```
                
            1. Run `molecule test` to ensure the role works as intended.
        
    1. We look at the role files and determine that no other refactoring is needed.
       We have completed our refactoring.  

[**<--Back to main instructions**](../readme.md#1stTDD)