# 8th TDD Iteration --> Configure Ansible Molecule to use AWS EC2 Instances.

Last updated: 07.21.2020

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
     
      1. Open the **create.yml** file for editing.
      1. Create your vpc by adding the following task after the **tasks** section:
     
           ```yaml
                - name: create a VPC with dedicated tenancy and a couple of tags
                  ec2_vpc_net:
                    name: vpc_openshift_idm
                    cidr_block: 10.10.0.0/16
                    region: us-east-1
                    tags:
                      module: ec2_vpc_net
                      this: works
                    tenancy: dedicated
                  register: ec2_vpc_net
           ```
      1. Add the following task to create the **vpc** variable,
        you will use it throughout your **create.yml**.
        
          ```yaml
              - name: Set the VPC Fact
                set_fact:
                  vpc: "{{ ec2_vpc_net.vpc }}"
          ```
      1. Find an Amazon Centos 8 AMI (Image Id) by
         going [here](https://wiki.centos.org/Cloud/AWS).  Copy the
         ami and add it to a file for later.
         
      1. Create the vpc gateway by adding the following task.
      
          ```yaml
              - name: create ec2 vpc internet gateway
                # create an internet gateway for the vpc
                ec2_vpc_igw:
                  vpc_id: "{{ vpc.id }}"
                  state: present
                  tags:
                    Name: "openshift_cluster_idm_gateway"
                register: igw_result
          ```


:construction:

We have configured RedHat IDM in our 7th TDD iteration.

[**<--Back to main instructions**](../readme.md#7thTDD)