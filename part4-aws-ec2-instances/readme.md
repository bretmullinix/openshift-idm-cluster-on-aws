# Create or Destroy EC2 Instances on AWS

Last updated: 08.19.2020

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
           security_group: "openshift_dev_vpc_security_group"
    
         ec2_instances: "{{ default[] }}"
         aws_region: "{{ lookup('env', 'AWS_REGION') }}"
         aws_access_key: "{{ lookup('env', 'AWS_ACCESS_KEY_ID') }}"
         aws_secret_key: "{{ lookup('env', 'AWS_SECRET_ACCESS_KEY') }}"
     ```
    
    The variables need some explanation:
    
    1. aws_vpc.name = The name of your vpc to add the EC2 instances to.  The ansible
    role checks to see if the AWS VPC "Tags" "Name" value matches this variable, or the
    AWS VPC "name".
    
    1. aws_vpc.security_group = The name of the security group you want to add the
    EC2 instances to.
    
    1. ec2_instances = The list of EC2 Instances that you plan to create.  The default
    value is an empty list.  An example of one EC2 instance is below.
    
        ```yaml
        ec2_instances:
          - name: my_instance
            ami: "ami-00594b9c138e6303d"
            instance_type: "t2.medium" 
            root_volume_size: 30
            subnet_name: "aws_infrastructure_control_subnet"
            key_name: "my_keypair"       
            
        ```

1. <a name="1stTDD"></a> Add the ec2 host keys using the [1st TDD Iteration](./1st-tdd-iteration).
   
:construction: Under Construction.....