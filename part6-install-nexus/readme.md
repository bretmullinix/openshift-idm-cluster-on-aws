# Installation of Nexus on AWS

Last updated: 09.30.2020

## Purpose

The purpose of this document is to teach the reader how to use Ansible
and Ansible Molecule to create an ansible role that installs and configures
Nexus.

## Prerequisites

AWS Account and permissions to create/delete AWS EC2 instances

### Setup your Python Virtual Environment

You will need a Python virtual environment to work in.  Please
set up your environment by following the instructions
[here](../part1-setup-environment/readme.md).

### Setup your AWS Environment

1. Open up a terminal
1. mkdir -p $HOME/.aws
1. cd $HOME/.aws
1. Make the file **.env**
1. Edit your **.env** file.  Enter the following
environment variables:

      ```yaml
       AWS_REGION="us-east-1 <this value should be different if you don't live close to the US east coast.>"
       AWS_ACCESS_KEY_ID="<your aws access key id: should be in your credentials.csv file>"
       AWS_SECRET_ACCESS_KEY="<your aws secret access key:  should be in your credentials.csv file>"
      ```
   
1. cd
1. Edit your **.bashrc** file.  Add the following line:  

    `source $HOME/.aws/.env`

1. Save your **.bashrc** file and close your terminal window.

Now your AWS account credentials can be accessed by your
Python virtual environment and Ansible Molecule.


## Procedure

1. Open up a terminal window.
1. mkdir **part6-install-nexus**
1. cd **part6-install-nexus**
1. Copy the "requirements" file down for your virtual environment
1. Open up a terminal
1. Activate your virtual environment (after you open any new terminal).  
   This is very important and could lead  to a corruption of your system
   if you don't.
1. Install the required AWS software needed to interact with AWS:
   
    ```pip install -r requirements```

1. Create the **nexus-instance** ansible role using the following command:

    ```shell script
     molecule init role -d delegated nexus-instance
    ```
1. cd nexus-instance
1. mkdir files
1. mkdir private_keys
1. cd files/private_keys
1. Create a file with the same name as your AWS private key having no
   extension.
1. Add your AWS private key contents to the file.
1. chmod 600 [your aws private key file]
    
    Note: Please make sure you don't check this file in to git.  If you make the
    repository is public, you would expose your private key.  I always add a
    **.gitignore** file that contains **private_keys/**.  This tells git to ignore
    the folder.
    
1. cd ../..
1. cd default
1. Add the following variables to the **default/main.yml** file
 
    ```yaml
     yum_installs:
       - name: "java-1.8.0-openjdk-devel"
         install_name: "java"
     yum_backend: dnf
     idm_network_interface_name: "eth0"
     idm_nmcli_interface_name:  "System {{ idm_network_interface_name }}"
     idm_admin_password: !vault |
       $ANSIBLE_VAULT;1.1;AES256
       37616332303435313431313964343732336166366363613864303662653137303266353233383266
       3032303064653162386634376464633264643332336263310a373330363466353036346438396331
       65396363353063653166653237623535323738323232323934666434313934373137633234663230
       6636323861323233650a313863393938643064323461626165646233386235326363356535346238
       3762
    ```

    The explanation of the **default/main.yml** file can be found 
    [here](../part5-register-idm-client/readme.md#default_main_explanation).

1. cd vars
1. Edit the file **main.yml** and add the following variables:

    ```yaml
    open_nexus_ports:
      - "80/tcp"
      - "443/tcp"
    ```
    
    The variables deserve some explanation:
    
    1. **open_nexus_ports** = The ports to open up for the nexus
       server.

1. cd ..
1. Make the file "vault_secret".  This file will be used to 
   store your vault password.
1. Open up "vault_secret" and enter your password for ansible vault.
1. Run the following command to encrypt your **idm server password**.

      ``` 
      ansible-vault encrypt_string "[your_idm_server_password here]" --vault-password-file ./vault_secret
      ```
1. Copy the output from **!vault** to the last line before **Encryption successful**.
1. cd defaults
1. Open up the main.yml file.
1. Add the variable "idm_admin_password", and paste the copied encrypted password
   as the value.
1. Save the file.

1. cd ../molecule/default
1. Edit the **converge.yml** and add `become: true` before the
      **tasks:** keyword.

1. Remove the **molecule.yml** file.
1. Create a new **molecule.yml** file and add the following content:

    ```yaml
    ---
    dependency:
      name: galaxy
    driver:
      name: delegated
      ssh_connection_options:
        - '-o ControlPath=~/.ansible/cp/%r@%h-%p'
    platforms:
      - name: nexus-server
    provisioner:
      name: ansible
      log: true
      config_options:
        defaults:
          remote_user: centos
          vault_password_file: ${MOLECULE_PROJECT_DIRECTORY}/vault_secret
        privileged_escalation:
          become: true
          become_ask_pass: false
    verifier:
      name: ansible
    scenario:
      test_sequence:
        - dependency
        - lint
        - cleanup
        - destroy
        - syntax
        - create
        - prepare
        - converge
        - side_effect
        - verify
        - cleanup
        - destroy
    ```

    The explanation of the **molecule.yml** file can be found 
    [here](../part5-register-idm-client/readme.md#molecule_explanation).

1. mkdir vars

1. cd vars

1. Create the file **main.yml** and add the following content:

    ```yaml
    aws_vpc_name: "aws_openshift_vpc"
    aws_subnet_name: "aws_subnet"
    aws_security_group: "aws_openshift_vpc_security_group"
    aws_region: "{{ lookup('env', 'AWS_REGION') }}"
    aws_access_key: "{{ lookup('env', 'AWS_ACCESS_KEY_ID') }}"
    aws_secret_key: "{{ lookup('env', 'AWS_SECRET_ACCESS_KEY') }}"
    ec2_instances:
      - name: "nexus-server"
        user: "centos"
        key_pair: "my_keypair"
        aws_ami: "ami-00594b9c138e6303d"
        root_volume_size: 30
        port: 22
    ```
    
    The explanation of the variables can be found 
    [here](../part5-register-idm-client/readme.md#vars_main_explanation).

1. Delete the **create.yml** file.

1. Add the following content to the **create.yml** file.

    ```yaml
    ---
    - name: Create
      hosts: localhost
      connection: local
      gather_facts: true
      tasks:
    
        - name: Include the variables needed for creation
          include_vars:
            file: "vars/main.yml"
    
        - name: Set molecule directory
          set_fact:
            molecule_ephemeral_directory:
              '{{ lookup(''env'', ''MOLECULE_EPHEMERAL_DIRECTORY'') }}'
    
        - name: AWS Private Key file location
          set_fact:
            aws_private_key_file: "../../files/private_keys/{{ ec2_instances[0].key_pair }}"
    
        - name: Set the molecule directory private key
          set_fact:
            aws_molecule_private_key_file:
              "{{ molecule_ephemeral_directory }}/private_key"
    
        - name: Copy the private key to the molecule config directory
          copy:
            src: "{{ aws_private_key_file }}"
            dest: "{{ aws_molecule_private_key_file }}"
            mode: 0600
    
        - name: Get VPC Facts
          ec2_vpc_net_info:
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            filters:
              "tag:Name": "{{ aws_vpc_name }}"
          register: vpc_info
    
        - name: Fail if the VPC does not exist
          fail:
            msg:  "The VPC called '{{ aws_vpc_name }}' does not exist."
          when:
            - vpc_info.vpcs is not defined or vpc_info.vpcs | length  == 0
    
        - name: Gather facts on the AWS Control subnet
          ec2_vpc_subnet_info:
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            filters:
              "tag:Name": "{{ aws_subnet_name }}"
          register: vpc_control_subnet_info
    
        - name: Fail if we do not get a subnet for the EC2 instance
          fail:
            msg: "We could not obtain the {{ aws_subnet_name }} subnet"
          when:
            - vpc_control_subnet_info is undefined or
              vpc_control_subnet_info.subnets is undefined or
              vpc_control_subnet_info.subnets | length == 0
    
        # Single instance with ssd gp2 root volume
        - name: Create EC2 Instance
          ec2:
            key_name: "{{ ec2_instances[0].key_pair }}"
            group: "{{ aws_security_group }}"
            instance_type: t2.medium
            image: "{{ ec2_instances[0].aws_ami }}"
            wait: true
            wait_timeout: 500
            volumes:
              - device_name: /dev/sda1
                volume_type: gp2
                volume_size: "{{ ec2_instances[0].root_volume_size }}"
                delete_on_termination: true
            vpc_subnet_id: "{{ vpc_control_subnet_info.subnets[0].id }}"
            assign_public_ip: true
            count_tag:
              Name: "{{ ec2_instances[0].name }}"
            instance_tags:
              Name: "{{ ec2_instances[0].name }}"
            exact_count: 1
          register: ec2_facts
    
    
        - name: Set public ip address for ec2 instance
          set_fact:
            aws_public_ip: "{{ ec2_facts.tagged_instances[0].public_ip }}"
    
        - name: Populate instance config dict
          set_fact:
            instance_conf_dict: {
              'instance': "{{ item.name }}",
              'address': "{{ aws_public_ip }}",
              'user': "{{ item.user }}",
              'port': "{{ item.port }}",
              'identity_file': "{{ aws_molecule_private_key_file }}",
              'become_method': "sudo",
              'become_ask_pass': false,
    
            }
          with_items: "{{ ec2_instances }}"
          register: instance_config_dict
    
        - name: Convert instance config dict to a list
          set_fact:
            instance_conf:
              "{{ instance_config_dict.results
              | map(attribute='ansible_facts.instance_conf_dict') | list }}"
    
        - name: Dump instance config
          copy:
            content: "{{ instance_conf
              | to_json | from_json | molecule_to_yaml | molecule_header }}"
            dest: "{{ molecule_instance_config }}"
    
    
        - name: Wait for SSH
          wait_for:
            port: 22
            host: "{{ aws_public_ip }}"
            search_regex: SSH
            delay: 10
            timeout: 320
    
        - name: Wait for boot process to finish
          pause:
            minutes: 2
    ```
    
    The description of the **create.yml** file can be found 
    [here](../part5-register-idm-client/readme.md#create_molecule).

1. Delete the **destroy.yml** file.

1. Create the **destroy.yml** file and add the following contents:

    ```yaml
    ---
    - name: Destroy
      hosts: localhost
      connection: local
      gather_facts: false
      no_log: "{{ molecule_no_log }}"
      tasks:
    
        - name: Include the variables needed for creation
          include_vars:
            file: "vars/main.yml"
    
        - name: Populate instance config
          set_fact:
            instance_conf: {}
    
        - name: Dump instance config
          copy:
            content: "{{ instance_conf | to_json | from_json | molecule_to_yaml | molecule_header }}"
            dest: "{{ molecule_instance_config }}"
          when: server.changed | default(false) | bool
    
        - name: Gather EC2 Instance Facts
          ec2_instance_facts:
          register: ec2_info
    
        - name: terminate
          ec2:
            instance_ids: "{{ item.instance_id }}"
            state: absent
            wait: yes
          with_items: "{{ ec2_info.instances }}"
          when: item.state.name != 'terminated' and item.tags.Name == ec2_instances[0].name
    ```

    The description of the **destroy.yml** file can be found 
    [here](../part5-register-idm-client/readme.md#destroy_explanation).

1. <a name="1stTDD"></a> Install the required yum packages in the [1st TDD Iteration](./1st-tdd-iteration).
1. <a name="2ndTDD"></a> Install **firewalld** to protect and open only necessary ports [2nd TDD Iteration](./2nd-tdd-iteration).

:construction: Under Construction.....