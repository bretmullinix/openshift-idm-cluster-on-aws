# Installation of IDM Client

Last updated: 08.24.2020

## Purpose

The purpose of this document is to teach the reader how to use
Ansible and Ansible Molecule to come up with a working installation
of RedHat IDM (FreeIPA) Client.

## Prerequisites

### Create your Python Virtual Environment

Follow the instructions in [part1](../part1-setup-environment) to
create your virtual environment.

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
1. mkdir **part5-register-idm-client**
1. Copy the "requirements" file down for your virtual environment
1. Open up a terminal
1. Activate your virtual environment
1. Install the required AWS software needed to interact with AWS:
   
    ```pip install -r requirements```

1. Create the **idm-client-install** ansible role using the following command:

    ```shell script
       molecule init role -d delegated idm-client-install
    ```
1. cd idm-client-install/molecule/default
1. Change the following in your **molecule.yml**.

    1. Change the **platform[0].name** to be the name of your
       ec2 instance.  We are going to call our EC2 instance
       **idm-client**.  Notice that **platform** is a list and
       allows you to work with more than one EC2 instance.
    
    1. Add the following section in replace of your **provisioner**
       section:
       
        ```yaml
        provisioner:
          name: ansible
          config_options:
            defaults:
              remote_user: centos
              vault_password_file: ${MOLECULE_PROJECT_DIRECTORY}/vault_secret
            privileged_escalation:
              become: true
              become_ask_pass: false     
        ```
        Let's explain this section a little more.
        
          1. **name** = The name of the provisioner.  This is the
          default value as there is only one provisioner.
          
          1. **config_options** = The section that allows us to update
          the **ansible.cfg** that molecule generates in the **molecule
          ephemeral** directory.  The **ephemeral** directory is created
          every time you run **molecule create** and gets destroyed when
          you call **molecule destroy**.  Molecule takes its configuration
          from this directory when it runs.
          
          1. **defaults** = This represents the **defaults** section of the
          **ansible.cfg**.  You can set typical variables in the **ansible.cfg**
          here.
          
          1. **remote_user** = The user that ansible uses to login via ssh.
          
          1. **vault_password_file** = The location of the private file that
          has the password to decrypt vault encoded variables.
          
          1. **privileged_escalation** = The section that corresponds to 
          the section in the **ansible.cfg**.
          
          1. **become** = States that any playbook run with molecule
          can escalate to **root** privileges if a task needs the permissions.
          
          1. **become_ask_pass** = Tells ansible not to prompt for the
          password when running a task which requires the escalated
          privileges.
          
          1. You can perform QA on this section of the **molecule.yml** 
          by taking a look at the finished **molecule.yml** 
          in the **molecule_artifacts** directory.
    
1. mkdir vars
1. cd vars
1. Make the file **main.yml** and add the following variables:

   ```yaml
   aws_vpc_name: "aws_openshift_vpc"
   aws_subnet_name: "aws_subnet"
   aws_security_group: "aws_openshift_vpc_security_group"
   aws_region: "{{ lookup('env', 'AWS_REGION') }}"
   aws_access_key: "{{ lookup('env', 'AWS_ACCESS_KEY_ID') }}"
   aws_secret_key: "{{ lookup('env', 'AWS_SECRET_ACCESS_KEY') }}"
   ec2_instances:
     - name: "idm-client"
       user: "centos"
       key_pair: "my_keypair"
       aws_ami: "ami-00594b9c138e6303d"
       root_volume_size: 30
       port: 22
   ```
   
   The variables deserve some explanation.
   
   1. **aws_vpc_name** = The name of your AWS VPC.  Note:  Your
   VPC must have a tag called **Name**, and your value goes here.
   
   1. **aws_vpc_subnet** = The name of your AWS VPC subnet the EC2
   instance goes on.  Note:  Your VPC subnet must have a tag called **Name**,
   and your value goes here.
   
   1. **aws_security_group** = The name of your AWS security group the EC2
   instance uses.  Note:  Your security group must have a tag called **Name**,
   and your value goes here.
   
   1. **aws_region** = The AWS region you plan on deploying your EC2 instance in.
   Notice how the value gets its value from the **AWS_REGION** environment variable.
   This must be set in order for molecule to work with AWS.
   
   1. **aws_access_key** = The AWS access key you need to deploy your EC2 instance in.
   Notice how the value gets its value from the **AWS_ACCESS_KEY_ID** environment variable.
   This must be set in order for molecule to work with AWS.
   
   1. **aws_secret_key** = The AWS access secret key you need to deploy your EC2 instance in.
   Notice how the value gets its value from the **AWS_SECRET_ACCESS_KEY** environment variable.
   This must be set in order for molecule to work with AWS.
   
   1. **ec2_instances** =  A list of EC2 instances you would like molecule to 
   spin up to test the installation of IDM client.  In our case, we only need
   one instance to test the ansible role.
   
   1. **ec2_instancess[0].name** = The name of the EC2 instance.  This name
   corresponds to the **platform[0].name** in the molecule.yml.
   
   1.  **ec2_instances[0].user** = The user name to login to your EC2 instance
   with.  
   
   1. **ec2_instances[0].key_pair** = The AWS key pair you need to login to
   your EC2 instance.
   
   1. **ec2_instances[0].aws_ami** = The AWS AMI you plan to use for your
   EC2 instance.  Note, this value changes depending on your AWS region.
   
   1. **ec2_instances[0].root_volume_size** = The EC2 root volume size in GB.
   
   1. **ec2_instances[0].port** = The SSH port you plan on using to remote into
   your EC2 instance.

1. cd ..
1. Delete the file **create.yml**.
1. Create a new **create.yml** file and add the following contents.

    ```yaml
    ---
    - name: Create
      hosts: localhost
      connection: local
      gather_facts: true
      no_log: "{{ molecule_no_log }}"
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
    
      Let's explain the tasks below.
    
      ```yaml
      - name: Include the variables needed for creation
        include_vars:
          file: "vars/main.yml"
     ```
   
     The task above includes the necessary molecule variables to create
     the AWS EC2 instance for the molecule tests.

      ```yaml
       - name: Set molecule directory
         set_fact:
           molecule_ephemeral_directory:
              '{{ lookup(''env'', ''MOLECULE_EPHEMERAL_DIRECTORY'') }}'
     ```
   
     The task above creates the variable to hold the molecule ephemeral
     directory path.  The **ephemeral** directory is the temp directory
     which is used by **molecule** to configure and run tests.

      ```yaml
        - name: AWS Private Key file location
          set_fact:
            aws_private_key_file: "../../files/private_keys/{{ ec2_instances[0].key_pair }}"
     ```
   
     The task above creates the variable to hold the 
     directory path to the private key for your EC2 instance.

      ```yaml
       - name: Copy the private key to the molecule config directory
         copy:
           src: "{{ aws_private_key_file }}"
           dest: "{{ aws_molecule_private_key_file }}"
           mode: 0600
     ```
   
     The task above copies your EC2 private key to the molecule
     **ephemeral** directory.

      ```yaml
          ec2_vpc_net_info:
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            filters:
              "tag:Name": "{{ aws_vpc_name }}"
          register: vpc_info    
     ```
   
     The task gets the AWS VPC facts for your VPC.

      

1. Replace your molecule **delete.yml** to use an AWS EC2 Instance

    1. rm idm-client-install/molecule/default/destroy.yml
    1. cp molecule_artifacts/destroy.yml idm-client-install/molecule/default/destroy.yml

1. Copy and modify the variables needed to use an EC2 instance for molecule

   1. cp -r molecule_artifacts/vars idm-client-install/molecule/default/
   1. cd idm-client-install/molecule/default/vars
   1. In the **main.yml**, change the variable **ec2_instances** to what you
      want for an EC2 instance.  Note:  The AMI can change depending on the region.
   1. Copy the **ec2_instances[0].name**.
   1. cd ..
   1. In the **molecule.yml** under **platforms[0].name**, paste your
      **ec2_instances[0].name**.

1. cd ../..
1. cd defaults
1. Add the following variables to the **main.yml** file.

    ```yaml
    idm_domain_name: example2020.com
    idm_fqdn: "idm.{{ idm_domain_name }}"
    ```
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
1. Add the variable "idm_admin_password", and the paste the copy encrypted password
   as the value.
1. Save the file.
1. cd ..
1. cd files
1. mkdir private_keys
1. cd private_keys
1. Copy your **aws private key** for the idm client 
   to this folder and rename the file "my_keypair"
1. cd ../../molecule/default/

         

:construction: