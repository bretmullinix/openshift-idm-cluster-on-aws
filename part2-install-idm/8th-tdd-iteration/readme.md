# 8th TDD Iteration --> Configure Ansible Molecule to use AWS EC2 Instances.

Last updated: 08.10.2020

## Purpose

The purpose of this iteration is to configure Ansible Molecule to use
AWS EC2 instances for the IDM ansible role testing.

## Procedure

1. Open up a terminal
1. Activate your virtual environment
1. Create the following environment variables:

      ```shell script
            AWS_REGION="us-east-1"
            AWS_ACCESS_KEY_ID="<your aws access key id: should be in your credentials.csv file>"
            AWS_SECRET_ACCESS_KEY="<your aws secret access key:  should be in your credentials.csv file>"
      ```

1. cd idm-install
1. In order to keep the **Docker** testing separate from **AWS** testing,
we will create a scenario called **aws**.  Run the following command to
create the **aws** scenario.

    ```shell script
    molecule init scenario -d delegated --role-name idm-install aws
    ```

    The reason we used the **delegated** provider is because Ansible
    Molecule does not have a driver for AWS.  The **delegated** driver
    provides the developer the ability to create their own
    driver, whether that is AWS, Google, Azure, or something else.
    
    One of the pre-requisites in using the **delegated** driver is
    the developer must provide data to molecule in a format called
    **instance-config.yml**. Molecule expects the storage of the
    file at the following location:
     
    **$HOME/.cache/molecule/<role-name>/<scenario-name>/instance_config.yml**

    Here is an example of the file:
    
    ```yaml
    - address: 10.10.15.17
     identity_file: /home/bmullinix/.ssh/id_rsa # mutually exclusive with
                                            # password
     instance: aws-idm-instance
     port: 22
     user: admin
    # password: ssh_password # mutually exclusive with identity_file
     become_method: sudo # optional
    # become_pass: password_if_required # optional
    ```

    The Ansible Molecule **delegate** driver creates an ansible stub to fill
    in to generate the **instance_config.yml** in our **create.yml**
    and remove it in the **destroy.yml**.  Here are examples
    of the **create.yml** and **destroy.yml** before we fill in the proper
    data for AWS to populate the stubs:
    
      1. **create.yml** -->
      
          ```yaml
          - name: Create
            hosts: localhost
            connection: local
            gather_facts: false
            no_log: "{{ molecule_no_log }}"
            tasks:
          
          # TODO: Developer must implement and populate 'server' variable
      
          - when: server.changed | default(false) | bool
            block:
              - name: Populate instance config dict
                set_fact:
                  instance_conf_dict: {
                    'instance': "{{ }}",
                    'address': "{{ }}",
                    'user': "{{ }}",
                    'port': "{{ }}",
                    'identity_file': "{{ }}", }
                with_items: "{{ server.results }}"
                register: instance_config_dict
      
              - name: Convert instance config dict to a list
                set_fact:
                  instance_conf: "{{ instance_config_dict.results | map(attribute='ansible_facts.instance_conf_dict') | list }}"
      
              - name: Dump instance config
                copy:
                  content: "{{ instance_conf | to_json | from_json | molecule_to_yaml | molecule_header }}"
                  dest: "{{ molecule_instance_config }}"
          ```
      1. **destroy.yml** -->

          ```yaml
          - name: Destroy
            hosts: localhost
            connection: local
            gather_facts: false
            no_log: "{{ molecule_no_log }}"
            tasks:
              # Developer must implement.
          
              # Mandatory configuration for Molecule to function.
          
              - name: Populate instance config
                set_fact:
                  instance_conf: {}
          
              - name: Dump instance config
                copy:
                  content: "{{ instance_conf | to_json | from_json | molecule_to_yaml | molecule_header }}"
                  dest: "{{ molecule_instance_config }}"
                when: server.changed | default(false) | bool
          ```

1. Your **converge.yml** should have the following content:

    ```yaml
    ---
    - name: Converge
      hosts: all
      become: true
      tasks:
        - name: Include the variables needed for creation
          include_vars:
            file: "vars/main.yml"
    
        - name: "Include idm-install"
          include_role:
            name: "idm-install"
    ```

1. **RED** --> Test when no configuration has been added for AWS.
    
    1. cd molecule/aws
    1. rm verify.yml
    1. Make the file **verify.yml**.
    1. Add the following code to the **verify.yml**.
        
        ```yaml
       ---
       - name: Verify
         hosts: all
         tasks:
       
           - name: Run a simple command on the EC2 instance
             shell:
               cmd: "echo 'We have configured AWS and launched the EC2 instance.'"
        ```
           
        The tasks above checks to see if AWS the EC2 instance
        is running and accessible.
        
    1. cd ../..
    1. Run `molecule verify -s aws`.  The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Configure Ansible Molecule for AWS.
     
      1. mkdir -p ./molecule/default/vars
      1. cd ./molecule/default/vars
      1. Create the **main.yml** file by adding the following variables.  Make
         sure you replace the **aws_idm_ami** with the Amazon Centos AMI you plan
         on using.
         
           ```yaml
            idm_domain_name: example2020.com
            idm_fqdn: "idm.{{ idm_domain_name }}"
            aws_idm_instance_name: "idm-instance"
            aws_idm_key_pair: "my_keypair"
            role_path: "../.."
            aws_idm_private_key: "{{ role_path }}/files/aws_private_key"
            create_private_key: false
            aws_default_image_size: 8
            aws_idm_image_size: 30
            aws_idm_ami: "ami-00594b9c138e6303d"
            aws_vpc:
              name: "aws_openshift_vpc"
              label: "Openshift Cluster VPC"
              gateway: "aws_openshift_vpc_gateway"
              route_table: "aws_openshift_vpc_route_table"
              security_group: "aws_openshift_vpc_security_group"
            aws_idm_instances:
              - name: "{{ aws_idm_instance_name }}"
                user: "centos"
                port: 22
           ```           
   
      1. Remove all the contents of the **molecule/default/create.yml** file.
      1. Start the **create.yml** file by adding the following contents.
           
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
           ```
 
      1. So far we have just added the variables to the **create.yml** file.
      1. Add the following contents to the end of the **create.yml** file.
         
            ```yaml
            - name: Set molecule directory
              set_fact:
                molecule_ephemeral_directory: '{{ lookup(''env'', ''MOLECULE_EPHEMERAL_DIRECTORY'') }}'
            ```
            
            This creates the variable called **molecule_ephemeral_directory**.
            The variable holds the directory path where molecule creates all the necessary artifacts to run a molecule scenario.
         
      1. Add the following contents to the end of the **create.yml** file.
         
            ```yaml
              - name: Set the molecule directory private key
                set_fact:
                  aws_molecule_private_key_file: "{{ molecule_ephemeral_directory }}/private_key"
            ```
            
            This creates the variable called **aws_molecule_private_key_file**.
            The variable holds the full file path to where we add the Amazon private key.
         
      1. Add the following contents to the end of the **create.yml** file.
      
            ```yaml
             - name: create a new ec2 key pair, returns generated private key
               ec2_key:
                 name: "{{ aws_idm_key_pair }}"
                 state: absent
               when: create_private_key == true
            ```   
            
            This deletes the existing Amazon EC2 public/private key pair.
            We perform this task when we want to create a new key pair with the same name.
            We use the new key pair to ssh into the Amazon EC2 instance.
      
      1. Add the following contents to the end of the **create.yml** file.
           
            ```yaml
            - name: create a new ec2 key pair, returns generated private key
              ec2_key:
                name: "{{ aws_idm_key_pair }}"
                state: present
              register: key_pair_details
            ```   
            
            This creates the Amazon EC2 public/private key pair.
            We use the key pair to ssh into the Amazon EC2 instance.
        
      1. Add the following contents to the end of the **create.yml** file.
           
         ```yaml
         - name: Set Key Pair Facts
           set_fact:
             aws_keypair: "{{ key_pair_details['key'] }}"
         ```   
         
         This extracts the key pair information from the output
         of the previous task.  We will use the information to
         extract the private key and store the value in our private key file.
 
      1. Add the following contents to the end of the **create.yml** file.
           
          ```yaml
          - name: Copy the private key to a file so we can ssh into it
            copy:
              content: "{{ aws_keypair['private_key'] }}"
              dest: "{{ aws_idm_private_key }}"
            when: create_private_key == true
          ```   
          
          This stores the private key in the 
          **ansible-molecule-aws-role/files/aws_private_key** file.
         
      1. Add the following contents to the end of the **create.yml** file.
               
          ```yaml
          - name: Copy the private key to the molecule config directory
            copy:
              src: "{{ aws_idm_private_key }}"
              dest: "{{ aws_molecule_private_key_file }}"
              mode: 0600
          ```   
          
          This copies the private key file to the ansible 
          molecule directory.  The ansible molecule directory does not
          exist until molecule executes and gets destroyed when the execution
          is complete.
 
      1. Add the following contents to the end of the **create.yml** file.
               
          ```yaml
              - name: Create a VPC with dedicated tenancy and a couple of tags
                ec2_vpc_net:
                  name: "{{ aws_vpc.name }}"
                  cidr_block: 10.10.0.0/16
                  dns_support: true
                  dns_hostnames: true
                  tags:
                    module: "{{ aws_vpc.label }}"
                  tenancy: default
                register: ec2_vpc_net
          ```   
          
          This creates an Amazon EC2 VPC called **vpc_aws**.
          The vpc has a cidr of 10.10.0.0/16.  The cidr binds
          the vpc to this set of ip addresses.  
 
      1. Add the following contents to the end of the **create.yml** file.
               
          ```yaml
          - name: Set the VPC Fact
            set_fact:
              vpc_facts: "{{ ec2_vpc_net.vpc }}"
          ``` 
          
          This creates a variable to hold the Amazon EC2 VPC information. 
              
      1. Add the following contents to the end of the **create.yml** file.
               
          ```yaml
            - name: create ec2 vpc subnet
              # create the subnet for the vpc with a cidr block
              ec2_vpc_subnet:
                vpc_id: "{{ vpc_facts.id }}"
                state: present
                cidr: "10.10.0.0/24"
                # enable public ip
                map_public: true
                resource_tags:
                  Name: "aws_subnet"
              register: subnet_result
          ``` 
          
          This creates the Amazon EC2 vpc subnet.  This subnet has 
          a cidr of 10.10.0.0/24 which indicate all the possible 
          subnet ip addresses. 
              
      1. Add the following contents to the end of the **create.yml** file.
               
          ```yaml
            - name: create ec2 vpc internet gateway
              # create an internet gateway for the vpc
              ec2_vpc_igw:
                vpc_id: "{{ vpc_facts.id }}"
                state: present
                tags:
                  Name: "{{ aws_vpc.gateway }}"
              register: igw
          ``` 
          
          This creates the Amazon EC2 vpc gateway.  The gateway
          is what allows the vpc to get out to the internet.
 
      1. Add the following contents to the end of the **create.yml** file.
               
          ```yaml
         - name: Set the VPC Subnet Fact
           set_fact:
             vpc_subnet: "{{ subnet_result['subnet'] }}"

          ``` 
          
          This creates a variable that holds the subnet information
          obtained from "create ec2 vpc subnet" task. 
  
      1. Add the following contents to the end of the **create.yml** file.
               
          ```yaml
            - name: Route Table to/from Gateway
              ec2_vpc_route_table:
                vpc_id: "{{ vpc_facts.id }}"
                subnets:
                  - "{{ vpc_subnet.id }}"
                routes:
                  - dest: 0.0.0.0/0
                    gateway_id: "{{ igw.gateway_id  }}"
                tags:
                  Name: "{{ aws_vpc.route_table }}"
          ``` 
          
          This creates the route table to allow the internal vpc subnet
          to talk to the internet gateway.  The route says to allow
          all ip addresses (0.0.0.0/0) through the gateway.
              
      1. Add the following contents to the end of the **create.yml** file.

          ```yaml
            - name: create the aws security group for the vpc
              ec2_group:
                name: "{{ aws_vpc.security_group }}"
                description: The security group for the AWS cluster
                vpc_id: "{{ vpc_facts.id }}"
                rules:
                  - proto: tcp
                    ports:
                      - 80
                      - 443
                      - 22
                    cidr_ip: 0.0.0.0/0
                tags:
                  Name: "{{ aws_vpc.security_group }}"
              register: security_group
          ``` 
          
          This creates the security group for the vpc.  The cluster allows
          any inbound internet connections to any machine (0.0.0.0/0) for the ports
          80, 443, and 22.
  
      1. Add the following contents to the end of the **create.yml** file.
                
           ```yaml
            # Single instance with ssd gp2 root volume
            - name: Create EC2 Instance
              ec2:
                key_name: "{{ aws_idm_key_pair }}"
                group: "{{ aws_vpc.security_group }}"
                instance_type: t2.medium
                image: "{{ aws_idm_ami }}"
                wait: true
                wait_timeout: 500
                volumes:
                  - device_name: /dev/sda1
                    volume_type: gp2
                    volume_size: "{{ aws_idm_image_size }}"
                    delete_on_termination: true
                vpc_subnet_id: "{{ vpc_subnet.id }}"
                assign_public_ip: true
                count_tag:
                  Name: "{{ aws_idm_instance_name }}"
                instance_tags:
                  Name: "{{ aws_idm_instance_name }}"
                exact_count: 1
              register: ec2_facts
           ``` 
               
           This creates the **aws-ec2-instance** EC2 instance we will be running
           the molecule tests on.  Notice that the volume can be changed
           to a larger root volume.  Currently, we are using a 30 GB hard drive.            
 
      1. Add the following contents to the end of the **create.yml** file.
                
           ```yaml
           - name: Set public ip address for ec2 instance
             set_fact:
               aws_public_ip: "{{ ec2_facts.tagged_instances[0].public_ip }}"
           ``` 
           
           This creates the variable called **aws_public_ip**.  The variable
           is populated with the **aws-ec2-instance** EC2 instance public ip.
             
      1. Add the following contents to the end of the **create.yml** file.
               
          ```yaml
             - name: Populate instance config dict
               set_fact:
                 instance_conf_dict: {
                   'instance': "{{ item.name }}",
                   'address': "{{ aws_public_ip }}",
                   'user': "{{ item.user  }}",
                   'port': "{{ item.port }}",
                   'identity_file': "{{ aws_molecule_private_key_file }}",
                   'become_method': "sudo",
                   'become_ask_pass': false,
         
                 }
               with_items: "{{ aws_idm_instances }}"
               register: instance_config_dict
          ```   
          
          This creates the **instance_config_dict** variable.
          The variable is a dictionary of **instance_conf_dict** objects.
          Each of the objects represents a container or vm to run the ansible
          role against.  In our case, we only have one vm, the **aws-ec2-instance**
          EC2 instance.
 
      1. Add the following contents to the end of the **create.yml** file.
               
          ```yaml
           - name: Convert instance config dict to a list
             set_fact:
               instance_conf:
                 "{{ instance_config_dict.results
                 | map(attribute='ansible_facts.instance_conf_dict') | list }}"
          ```   
          
          This creates the **instance_conf** variable.
          The variable transformed the **instance_config_dict.results** dictionary
          into a list of objects.
 
      1. Add the following contents to the end of the **create.yml** file.
               
          ```yaml
         - name: Dump instance config
           copy:
             content: "{{ instance_conf
               | to_json | from_json | molecule_to_yaml | molecule_header }}"
             dest: "{{ molecule_instance_config }}"
          ```   
          
          This creates the file describing the vms in the molecule directory 
          that is used to run the ansible role.
   
     1. Add the following contents to the end of the **create.yml** file.
               
          ```yaml
           - name: Wait for SSH
             wait_for:
               port: 22
               host: "{{ aws_public_ip }}"
               search_regex: SSH
               delay: 10
               timeout: 320
          ```   
    
          This tests the EC2 instance to make sure we can reach it via
          ssh.
     
     1. Add the following contents to the end of the **create.yml** file.
               
          ```yaml
          - name: Wait for boot process to finish
            pause:
              minutes: 2
          ```   

          This puts a pause at the end for 2 minutes to ensure the
          EC2 instance boots up.
 
      1. From the terminal, go to the root role directory.
      1. Run `molecule create`.  Your **create.yml** file has been created.
      1. Let's not recreate the AWS key pair.  Change the value of 
         **create_private_key** to **false** in the **molecule/default/vars/main.yml** 
         file.
      1. We have created the vm, but we need
         to destroy the vm after the molecule tests.  This is where we have
         to change the **destroy.yml**.      

      1. Add the following contents to the end of the **destroy.yml** file.
           
         ```yaml
          - name         - name: Delete the vpc
            ec2_vpc_net:
              name: vpc_aws
              cidr_block: 10.10.0.0/16
              state: absent: Include the variables needed for creation
            include_vars:
              file: "vars/main.yml"
         ```      

         This imports our variables.

      1. Add the following contents to the end of the **destroy.yml** file.
              
             ```yaml
             - name: Gather EC2 Instance Facts
               ec2_instance_facts:
               register: ec2_info
 
             - name: terminate
               ec2:
                 instance_ids: "{{ item.instance_id }}"
                 state: absent
                 wait: yes
               with_items: "{{ ec2_info.instances }}"
               when: item.state.name != 'terminated' and item.tags.Name == aws_idm_instance_name
             ```   

             This queries the EC2 facts and then destroys the EC2 **aws-ec2-instance**
             instance.

      1. Add the following contents to the end of the **destroy.yml** file.
              
         ```yaml
            - name: Query a VPC with dedicated tenancy and a couple of tags
              ec2_vpc_net:
                name: "{{ aws_vpc.name }}"
                cidr_block: 10.10.0.0/16
                dns_support: yes
                dns_hostnames: yes
                tags:
                  module: "{{ aws_vpc.label }}"
                tenancy: default
                state: present
              register: ec2_vpc_net


            - name: Set the VPC Fact
              set_fact:
                vpc_facts: "{{ ec2_vpc_net.vpc }}"
         ```   

         This queries the vpc and creates a variable with the vpc information.
      
     1. Add the following contents to the end of the **destroy.yml** file.
              
         ```yaml
         - name: Delete the aws security group for the vpc
           ec2_group:
             name: "{{ aws_vpc.security_group }}"
             state: absent
             vpc_id: "{{ vpc_facts.id }}"
         ```   

         This deletes the security group associated with the vpc.          

    1. Add the following contents to the end of the **destroy.yml** file.
              
         ```yaml
        - name: Delete the subnet
          ec2_vpc_subnet:
            vpc_id: "{{ vpc_facts.id }}"
            state: absent
            cidr: "10.10.0.0/24"
         ```   
    
         This deletes the subnet associated with the vpc.          

    1. Add the following contents to the end of the **destroy.yml** file.
              
         ```yaml
         - name: Delete the gateway
           ec2_vpc_igw:
             vpc_id: "{{ vpc_facts.id }}"
             state: absent
         ```   

         This deletes the internet gateway associated with the vpc.          

    1. Add the following contents to the end of the **destroy.yml** file.
              
         ```yaml
         - name: Delete routing table
           ec2_vpc_route_table:
             vpc_id: "{{ vpc_facts.id }}"
             tags:
               Name: "{{ aws_vpc.route_table }}"
             state: absent
         ```   

         This deletes the routing table associated with the vpc.          

     1. Add the following contents to the end of the **destroy.yml** file.
              
         ```yaml
         - name: Delete the vpc
           ec2_vpc_net:
             name: "{{ aws_vpc.name }}"
             cidr_block: 10.10.0.0/16
             state: absent
         ```   

         This deletes the VPC.  All dependencies of the VPC had to be
         deleted in order for us to delete the VPC.
       
     1. We can create and destroy the EC2 instance and VPC.  We are
       ready to test the ansible role.
       
     1. Run `molecule converge`.  The role works as expected, 
       but we are not in **Green** yet.
       
     1. Run `molecule verify`.  The verification passed, and we are
       now in the **Green**.
       
     1. Run `molecule destroy` to clean up your testing.
       
1. **Refactor** the code.  Take a look at the **tasks/main.yml** and the **verify.yml** to see
    if you can make the code better for maintenance, usability, or any other valid reasons.


We have configured RedHat IDM in our 8th TDD iteration.

[**<--Back to main instructions**](../readme.md#8thTDD)