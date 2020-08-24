# Create or Destroy EC2 Instances on AWS

Last updated: 08.24.2020

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
            action: "create"       
            
        ```
        The ec2_instances variable is a list of ec2 instances that you want to
        create or delete (destroy).  When you set the **action** attribute to
        **create**, the ec2 instance will be created.  When you set the **action**
        attribute to **delete**, the ec2 instance will be deleted.
        
1. <a name="1stTDD"></a> Add the ec2 host keys using the [1st TDD Iteration](./1st-tdd-iteration).
1. <a name="2ndTDD"></a> Get the AWS VPC facts using the [2nd TDD Iteration](./2nd-tdd-iteration).
1. <a name="3rdTDD"></a> Get the AWS VPC subnet facts using the [3rd TDD Iteration](./3rd-tdd-iteration).
1. <a name="4thTDD"></a> Create the AWS EC2 instances using the [4th TDD Iteration](./4th-tdd-iteration).
1. <a name="5thTDD"></a> Delete the AWS EC2 instances using the [5th TDD Iteration](./5th-tdd-iteration).

The output is one or two time stamped files in
the **aws-ec2-instances/files/ec2_facts** folder. Below is an example:

Example:

1. The inventory file will be created if EC2 instances exist.  
   The file contains the following information:
   
    ```text
    name:  my_instance
    public_ip:  34.200.250.109
    private_ip:  192.168.1.53
    key_pair:  my_keypair
    ssh connection: ssh -i /home/bmullini/Documents/redhat_tools/git/repos/openshift-idm-cluster-on-aws/part4-aws-ec2-instances/aws-ec2-instances/files/private_keys/my_keypair centos@34.200.250.109
    
    
    name:  your_instance
    public_ip:  18.215.124.223
    private_ip:  192.168.1.135
    key_pair:  your_keypair
    ssh connection: ssh -i /home/bmullini/Documents/redhat_tools/git/repos/openshift-idm-cluster-on-aws/part4-aws-ec2-instances/aws-ec2-instances/files/private_keys/your_keypair centos@18.215.124.223


    ```
    The output includes the ssh
    command needed to log into the ec2 instances.


1. The facts file will be created regardless of the existence of EC2 instances.
   The file contains all the AWS facts about the ec2 instances:

    ```json
      {
        "results": [
          {
            "changed": true,
            "instance_ids": [
              "i-04d6dd6b0df376d0c"
            ],
            "instances": [
              {
                "id": "i-04d6dd6b0df376d0c",
                "ami_launch_index": "0",
                "private_ip": "192.168.1.53",
                "private_dns_name": "ip-192-168-1-53.ec2.internal",
                "public_ip": "34.200.250.109",
                "dns_name": "ec2-34-200-250-109.compute-1.amazonaws.com",
                "public_dns_name": "ec2-34-200-250-109.compute-1.amazonaws.com",
                "state_code": 16,
                "architecture": "x86_64",
                "image_id": "ami-00594b9c138e6303d",
                "key_name": "my_keypair",
                "placement": "us-east-1a",
                "region": "us-east-1",
                "kernel": null,
                "ramdisk": null,
                "launch_time": "2020-08-21T19:20:28.000Z",
                "instance_type": "t2.medium",
                "root_device_type": "ebs",
                "root_device_name": "/dev/sda1",
                "state": "running",
                "hypervisor": "xen",
                "tags": {
                  "Name": "my_instance"
                },
                "groups": {
                  "sg-0624c8049df85e7d9": "openshift_dev_vpc_security_group"
                },
                "virtualization_type": "hvm",
                "ebs_optimized": false,
                "block_device_mapping": {
                  "/dev/sda1": {
                    "status": "attached",
                    "volume_id": "vol-0a792c1fc6ccf126b",
                    "delete_on_termination": true
                  }
                },
                "tenancy": "default"
              }
            ],
            "tagged_instances": [
              {
                "id": "i-04d6dd6b0df376d0c",
                "ami_launch_index": "0",
                "private_ip": "192.168.1.53",
                "private_dns_name": "ip-192-168-1-53.ec2.internal",
                "public_ip": "34.200.250.109",
                "dns_name": "ec2-34-200-250-109.compute-1.amazonaws.com",
                "public_dns_name": "ec2-34-200-250-109.compute-1.amazonaws.com",
                "state_code": 16,
                "architecture": "x86_64",
                "image_id": "ami-00594b9c138e6303d",
                "key_name": "my_keypair",
                "placement": "us-east-1a",
                "region": "us-east-1",
                "kernel": null,
                "ramdisk": null,
                "launch_time": "2020-08-21T19:20:28.000Z",
                "instance_type": "t2.medium",
                "root_device_type": "ebs",
                "root_device_name": "/dev/sda1",
                "state": "running",
                "hypervisor": "xen",
                "tags": {
                  "Name": "my_instance"
                },
                "groups": {
                  "sg-0624c8049df85e7d9": "openshift_dev_vpc_security_group"
                },
                "virtualization_type": "hvm",
                "ebs_optimized": false,
                "block_device_mapping": {
                  "/dev/sda1": {
                    "status": "attached",
                    "volume_id": "vol-0a792c1fc6ccf126b",
                    "delete_on_termination": true
                  }
                },
                "tenancy": "default"
              }
            ],
            "invocation": {
              "module_args": {
                "key_name": "my_keypair",
                "group": [
                  "openshift_dev_vpc_security_group"
                ],
                "instance_type": "t2.medium",
                "image": "ami-00594b9c138e6303d",
                "aws_access_key": "AKIA4WSAY74RIHA552EL",
                "aws_secret_key": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
                "region": "us-east-1",
                "wait": true,
                "wait_timeout": 500,
                "volumes": [
                  {
                    "device_name": "/dev/sda1",
                    "volume_type": "gp2",
                    "volume_size": "30",
                    "delete_on_termination": true
                  }
                ],
                "vpc_subnet_id": "subnet-0c9343e888d486fa8",
                "assign_public_ip": true,
                "count_tag": {
                  "Name": "my_instance"
                },
                "instance_tags": {
                  "Name": "my_instance"
                },
                "exact_count": 1,
                "debug_botocore_endpoint_logs": false,
                "validate_certs": true,
                "spot_type": "one-time",
                "count": 1,
                "monitoring": false,
                "spot_wait_timeout": 600,
                "state": "present",
                "instance_initiated_shutdown_behavior": "stop",
                "ebs_optimized": false,
                "tenancy": "default",
                "ec2_url": null,
                "security_token": null,
                "profile": null,
                "id": null,
                "group_id": null,
                "zone": null,
                "spot_price": null,
                "spot_launch_group": null,
                "kernel": null,
                "ramdisk": null,
                "placement_group": null,
                "user_data": null,
                "private_ip": null,
                "instance_profile_name": null,
                "instance_ids": null,
                "source_dest_check": null,
                "termination_protection": null,
                "network_interfaces": null
              }
            },
            "failed": false,
            "item": {
              "name": "my_instance",
              "ami": "ami-00594b9c138e6303d",
              "instance_type": "t2.medium",
              "root_volume_size": 30,
              "subnet_name": "aws_infrastructure_control_subnet",
              "key_name": "my_keypair",
              "action": "create"
            },
            "ansible_loop_var": "item"
          },
          {
            "changed": true,
            "instance_ids": [
              "i-045e1dd80235d651e"
            ],
            "instances": [
              {
                "id": "i-045e1dd80235d651e",
                "ami_launch_index": "0",
                "private_ip": "192.168.1.135",
                "private_dns_name": "ip-192-168-1-135.ec2.internal",
                "public_ip": "18.215.124.223",
                "dns_name": "ec2-18-215-124-223.compute-1.amazonaws.com",
                "public_dns_name": "ec2-18-215-124-223.compute-1.amazonaws.com",
                "state_code": 16,
                "architecture": "x86_64",
                "image_id": "ami-00594b9c138e6303d",
                "key_name": "your_keypair",
                "placement": "us-east-1a",
                "region": "us-east-1",
                "kernel": null,
                "ramdisk": null,
                "launch_time": "2020-08-21T19:20:59.000Z",
                "instance_type": "t2.medium",
                "root_device_type": "ebs",
                "root_device_name": "/dev/sda1",
                "state": "running",
                "hypervisor": "xen",
                "tags": {
                  "Name": "your_instance"
                },
                "groups": {
                  "sg-0624c8049df85e7d9": "openshift_dev_vpc_security_group"
                },
                "virtualization_type": "hvm",
                "ebs_optimized": false,
                "block_device_mapping": {
                  "/dev/sda1": {
                    "status": "attached",
                    "volume_id": "vol-053ef0173c9b3b0f4",
                    "delete_on_termination": true
                  }
                },
                "tenancy": "default"
              }
            ],
            "tagged_instances": [
              {
                "id": "i-045e1dd80235d651e",
                "ami_launch_index": "0",
                "private_ip": "192.168.1.135",
                "private_dns_name": "ip-192-168-1-135.ec2.internal",
                "public_ip": "18.215.124.223",
                "dns_name": "ec2-18-215-124-223.compute-1.amazonaws.com",
                "public_dns_name": "ec2-18-215-124-223.compute-1.amazonaws.com",
                "state_code": 16,
                "architecture": "x86_64",
                "image_id": "ami-00594b9c138e6303d",
                "key_name": "your_keypair",
                "placement": "us-east-1a",
                "region": "us-east-1",
                "kernel": null,
                "ramdisk": null,
                "launch_time": "2020-08-21T19:20:59.000Z",
                "instance_type": "t2.medium",
                "root_device_type": "ebs",
                "root_device_name": "/dev/sda1",
                "state": "running",
                "hypervisor": "xen",
                "tags": {
                  "Name": "your_instance"
                },
                "groups": {
                  "sg-0624c8049df85e7d9": "openshift_dev_vpc_security_group"
                },
                "virtualization_type": "hvm",
                "ebs_optimized": false,
                "block_device_mapping": {
                  "/dev/sda1": {
                    "status": "attached",
                    "volume_id": "vol-053ef0173c9b3b0f4",
                    "delete_on_termination": true
                  }
                },
                "tenancy": "default"
              }
            ],
            "invocation": {
              "module_args": {
                "key_name": "your_keypair",
                "group": [
                  "openshift_dev_vpc_security_group"
                ],
                "instance_type": "t2.medium",
                "image": "ami-00594b9c138e6303d",
                "aws_access_key": "AKIA4WSAY74RIHA552EL",
                "aws_secret_key": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
                "region": "us-east-1",
                "wait": true,
                "wait_timeout": 500,
                "volumes": [
                  {
                    "device_name": "/dev/sda1",
                    "volume_type": "gp2",
                    "volume_size": "25",
                    "delete_on_termination": true
                  }
                ],
                "vpc_subnet_id": "subnet-0c9343e888d486fa8",
                "assign_public_ip": true,
                "count_tag": {
                  "Name": "your_instance"
                },
                "instance_tags": {
                  "Name": "your_instance"
                },
                "exact_count": 1,
                "debug_botocore_endpoint_logs": false,
                "validate_certs": true,
                "spot_type": "one-time",
                "count": 1,
                "monitoring": false,
                "spot_wait_timeout": 600,
                "state": "present",
                "instance_initiated_shutdown_behavior": "stop",
                "ebs_optimized": false,
                "tenancy": "default",
                "ec2_url": null,
                "security_token": null,
                "profile": null,
                "id": null,
                "group_id": null,
                "zone": null,
                "spot_price": null,
                "spot_launch_group": null,
                "kernel": null,
                "ramdisk": null,
                "placement_group": null,
                "user_data": null,
                "private_ip": null,
                "instance_profile_name": null,
                "instance_ids": null,
                "source_dest_check": null,
                "termination_protection": null,
                "network_interfaces": null
              }
            },
            "failed": false,
            "item": {
              "name": "your_instance",
              "ami": "ami-00594b9c138e6303d",
              "instance_type": "t2.medium",
              "root_volume_size": 25,
              "subnet_name": "aws_infrastructure_control_subnet",
              "key_name": "your_keypair",
              "action": "create"
            },
            "ansible_loop_var": "item"
          }
        ],
        "changed": true,
        "msg": "All items completed"
      }

    ```