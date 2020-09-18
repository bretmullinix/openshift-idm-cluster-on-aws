# Installation of IDM Client

Last updated: 09.18.2020

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
    
1. cd idm-client-install
1. cd vars
1. Edit the file **main.yml** and add the following variables:

    ```yaml
    open_idm_ports:
      - "80/tcp"
      - "443/tcp"
      - "389/tcp"
      - "636/tcp"
      - "88/tcp"
      - "88/udp"
      - "464/tcp"
      - "464/udp"
      - "53/tcp"
      - "53/udp"
      - "123/udp"
    pip_requirements:
      - "ansible==2.9.11"
    
    # Primary DNS domain of the IPA deployment
    # Type: Str
    freeipa_client_domain: "{{ idm_domain_name }}"
    # The hostname of this machine (FQDN)
    # Type: Str
    freeipa_client_fqdn: "{{ idm_client_hostname + '.' + idm_domain_name }}"
    # Password to join the IPA realm
    # Type: Str
    freeipa_client_password: "{{ idm_admin_password }}"
    # Principal to use to join the IPA realm
    # Type: Str
    freeipa_client_principal: admin
    # Kerberos realm name of the IPA deployment
    # Type: Str
    freeipa_client_realm: "{{ idm_domain_name | upper }}"
    # FQDN of IPA server
    # Type: Str
    freeipa_client_server: "{{ idm_fqdn }}"
    
    # vars file for idm-client-install
    freeipa_client_install_base_command: ipa-client-install --unattended
    # The default FreeIPA client installation options
    # Type: List
    freeipa_client_install_options:
      - "--domain={{ freeipa_client_domain }}"
      - "--server={{ freeipa_client_server }}"
      - "--realm={{ freeipa_client_realm }}"
      - "--principal={{ freeipa_client_principal }}"
      - "--password={{ freeipa_client_password }}"
      - "--mkhomedir"
      - "--hostname={{ freeipa_client_fqdn | default(ansible_fqdn) }}"
    ```
    
    The variables deserve some explanation:
    
    1. **open_idm_ports** = The ports to open up for the IDM client
       server.
    1. **pip_requirements** = The python packages installed on the IDM client
       server.
    1. **freeipa_client_domain** = The domain name of the IPA server and client.
    1. **freeipa_client_fqdn** = The FQDN of the IPA client server.
    1. **freeipa_client_password** = The IPA server password.
    1. **freeipa_client_principal** = The IPA server user name to login as.
    1. **freeipa_client_realm** = The IPA realm for the IPA server.  This is
       usually an upper case version of the domain name.
    1. **freeipa_client_server** = The IPA server FQDN.
    1. **freeipa_client_install_base_command** = The base command to run
       in order to install the IPA client.
    1. **freeipa_client_install_options** = The options to choose
       when installing the IPA client.  You may change the options
       to tailor the IPA client install.

1. cd ..
1. cd defaults
1. Add the following variables to the **main.yml** file.

    ```yaml
      yum_installs:
        - "python36"
        - "firewalld"
        - "nscd"
        - "@idm:client"
      yum_backend: dnf
      idm_server_ip_address: 10.10.0.111
      idm_domain_name: example2020.com
      idm_fqdn: "idm.{{ idm_domain_name }}"
      idm_client_hostname: "idm-client"
    ```
    Note: The packages installed are those used for **Centos 8**.  If you
    plan on using the ansible role on another version of linux, these
    packages and the **yum** task may need to be changed.
   
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
1. cd ..
1. cd files
1. mkdir private_keys
1. cd private_keys
1. Copy your **aws private key** for the IDM client EC2 instance
   to this folder and rename the file "my_keypair"
1. cd ../../molecule/default
1. Edit the **converge.yml** and add `become: true` before the
   **tasks:** keyword.
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
1. Edit the file **main.yml** and add the following variables:

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
    
      The following task includes the necessary molecule variables to create
      the AWS EC2 instance for the molecule tests.
      
      ```yaml
      - name: Include the variables needed for creation
        include_vars:
          file: "vars/main.yml"
     ```
   
     The following task creates the variable to hold the molecule ephemeral
     directory path.  The **ephemeral** directory is the temp directory
     which is used by **molecule** to configure and run tests. 

      ```yaml
       - name: Set molecule directory
         set_fact:
           molecule_ephemeral_directory:
              '{{ lookup(''env'', ''MOLECULE_EPHEMERAL_DIRECTORY'') }}'
     ```
   
     The following task creates the variable to hold the 
     directory path to the private key for your EC2 instance.

      ```yaml
        - name: AWS Private Key file location
          set_fact:
            aws_private_key_file: "../../files/private_keys/{{ ec2_instances[0].key_pair }}"
     ```
   
     The following task copies your EC2 private key to the molecule
     **ephemeral** directory.

      ```yaml
       - name: Copy the private key to the molecule config directory
         copy:
           src: "{{ aws_private_key_file }}"
           dest: "{{ aws_molecule_private_key_file }}"
           mode: 0600
     ```
   
     The following task gets the AWS VPC facts for your VPC.

      ```yaml
          ec2_vpc_net_info:
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            filters:
              "tag:Name": "{{ aws_vpc_name }}"
          register: vpc_info    
     ```
   
     The following task will fail the molecule testing if no AWS VPC is found.

      ```yaml
       - name: Fail if the VPC does not exist
         fail:
           msg:  "The VPC called '{{ aws_vpc_name }}' does not exist."
         when:
           - vpc_info.vpcs is not defined or vpc_info.vpcs | length  == 0
     ```
   
     The following task will gather the facts for the AWS subnet.

     ```yaml
      - name: Gather facts on the AWS Control subnet
        ec2_vpc_subnet_info:
          aws_access_key: "{{ aws_access_key }}"
          aws_secret_key: "{{ aws_secret_key }}"
          region: "{{ aws_region }}"
          filters:
           "tag:Name": "{{ aws_subnet_name }}"
       register: vpc_control_subnet_info
    ```
   
    The following task will fail the molecule testing if no AWS subnet is found. 
 
     ```yaml
     - name: Fail if we do not get a subnet for the EC2 instance
       fail:
         msg: "We could not obtain the {{ aws_subnet_name }} subnet"
       when:
         - vpc_control_subnet_info is undefined or
           vpc_control_subnet_info.subnets is undefined or
           vpc_control_subnet_info.subnets | length == 0
    ```
   
    The following task will create the EC2 instance that is used by molecule to
    run the tests.  
 
     ```yaml
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
    ```
   
    The following task will assign the variable **aws_public_ip** to the public
    ip of the newly created EC2 instance.
 
     ```yaml
      - name: Set public ip address for ec2 instance
        set_fact:
          aws_public_ip: "{{ ec2_facts.tagged_instances[0].public_ip }}"
    ```
   
    The following task will assign the variable **instance_conf_dict** 
    to a dictionary with the values of the ansible molecule instances.
    Molecule monitors the instances using these values.  

     ```yaml
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
    ```
   
    The following task will assign the variable **instance_conf** to a list
    with the values of the variables above.  Molecule monitors
    the instances using these values.

     ```yaml
    - name: Convert instance config dict to a list
      set_fact:
        instance_conf:
          "{{ instance_config_dict.results
          | map(attribute='ansible_facts.instance_conf_dict') | list }}"
    ```
   
    The following task will save the variable **instance_conf** to a file.  
    Molecule uses these values to manage and use the ec2 instances. 

     ```yaml
     - name: Dump instance config
       copy:
         content: "{{ instance_conf
           | to_json | from_json | molecule_to_yaml | molecule_header }}"
         dest: "{{ molecule_instance_config }}"
    ```
   
    The following task will make sure molecule can ssh into the EC2 instance.     
      
     ```yaml
      - name: Wait for SSH
        wait_for:
          port: 22
          host: "{{ aws_public_ip }}"
          search_regex: SSH
          delay: 10
          timeout: 320
    ```   
    
    The following task will 
    pause for 2 minutes to make sure the EC2 instance boots up.       
      
     ```yaml
       - name: Wait for boot process to finish
         pause:
           minutes: 2
    ```

1. Delete the file **destroy.yml**.
1. Create a new **destroy.yml** file and add the following contents.

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
 
    Let's explain the tasks below.
      
      The following task will include
      the necessary variables to delete
      the EC2 instances.

      ```yaml
       - name: Include the variables needed for creation
         include_vars:
           file: "vars/main.yml"
      ```
      
      The following task will clear out the molecule **instance_conf** variable.  
      The variable provides the EC2 instance information for molecule to use.
      
      ```yaml
       - name: Populate instance config
         set_fact:
           instance_conf: {}
      ```
      
      The following task will save the molecule **instance_conf** 
      variable to a file.  The file is used by molecule to manage 
      and run tests using the EC2 instances.
      The variable saved is cleared out in the task above.  As a result,
      the file does not contain any information in it about the EC2 instances.
      
      ```yaml
       - name: Dump instance config
         copy:
           content: "{{ instance_conf | to_json | from_json | molecule_to_yaml | molecule_header }}"
           dest: "{{ molecule_instance_config }}"
         when: server.changed | default(false) | bool
      ```
      
      The following task will get information from AWS about all
      the EC2 instances.
      
      ```yaml
        - name: Gather EC2 Instance Facts
          ec2_instance_facts:
          register: ec2_info
      ```
      
      The following task will delete the EC2 instance used to run the molecule tests.

      ```yaml
       - name: terminate
         ec2:
           instance_ids: "{{ item.instance_id }}"
           state: absent
           wait: yes
         with_items: "{{ ec2_info.instances }}"____
         when: item.state.name != 'terminated' and item.tags.Name == ec2_instances[0].name
      ```
1. <a name="1stTDD"></a> Install the required yum packages in the [1st TDD Iteration](./1st-tdd-iteration).
1. <a name="2ndTDD"></a> Make sure **firewalld** is started in the [2nd TDD Iteration](./2nd-tdd-iteration).
1. <a name="3rdTDD"></a> Make sure IDM client ports are open in the [3rd TDD Iteration](./3rd-tdd-iteration).
1. <a name="4thTDD"></a> Make sure the Primary DNS Server for the IDM client is
   the IDM Server [4th TDD Iteration](./4th-tdd-iteration).

TODO:  Working on 5thTDD----->
1. <a name="5thTDD"></a>Configure the IDM client on the target server [5th TDD Iteration](./5th-tdd-iteration).

:construction: