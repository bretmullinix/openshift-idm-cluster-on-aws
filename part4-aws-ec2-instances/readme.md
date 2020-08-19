# Create or Destroy EC2 Instances on AWS

Last updated: 08.13.2020

## Purpose

The purpose of this document is to teach the reader how to use Ansible
and Ansible Molecule to create an ansible role that creates or destroys
EC2 instances.

## Prerequisites

None.

## Procedure

1. Open up a terminal window.

1. Make sure you **source** your virtual environment

1. mkdir **part4-aws-ec2-instances**

1. cd part4-aws-ec2-instances
  
1. Run `docker build -t part4-aws-ec2-instances .`

   The command above will create a docker image
   on your machine called **part4-aws-ec2-instances**.
   The image ensures that python3, pip3, boto, boto3 and ansible 2.9
   are installed.  We installed **ansible** on the image
   because the image will be used by **molecule**, and
   molecule requires ansible to run tests.  The Amazon ansible modules
   require the  **boto** and **boto3** packages.

1. Create the Ansible Molecule role called **aws-ec2-instance**

    1. Run `molecule init role --driver-name docker aws-ec2-instances`
    1. Run `tree aws-ec2-instances`
    
1. cd aws-ec2-instances/molecule/default

1. rm molecule.yml

1. Create **molecule.yml** and add the following contents:

    ```yaml
        ---
        dependency:
          name: galaxy
        driver:
          name: docker
        platforms:
          - name: aws-instances
            image: part4-aws-ec2-instances
            pre_build_image: true
        provisioner:
          name: ansible
          log: true
        verifier:
          name: ansible
          options:
            v: 4
        scenario:
          name: default
          test_sequence:
            - create
            - prepare
            - converge
            - verify
            - destroy


    ```

 1. Add the following variables to the **default/main.yml**.
 
     ```yaml
         ---
         aws_vpc:
           name: "openshift_dev_vpc"
           label: "Openshift Development Cluster VPC"
           gateway: "openshift_dev_vpc_gateway"
           route_table: "openshift_dev_vpc_route_table"
           security_group: "openshift_dev_vpc_security_group"
           subnets:
             control:
               name: "aws_infrastructure_control_subnet"
               cidr: "192.168.1.0/24"
               mtu: 1500
             data:
               name: "aws_infrastructure_data_subnet"
               cidr: "192.168.2.0/24"
               mtu: 9200
           cidr: "192.168.0.0/16"
         ec2_instances: "{{ default[] }}"
         aws_region: "{{ lookup('env', 'AWS_REGION') }}"
         aws_access_key: "{{ lookup('env', 'AWS_ACCESS_KEY_ID') }}"
         aws_secret_key: "{{ lookup('env', 'AWS_SECRET_ACCESS_KEY') }}"
     ```  
   
:construction: Under Construction.....