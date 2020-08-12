# 1st TDD Iteration --> Add the AWS VPC

Last updated: 08.12.2020

## Purpose

The purpose of this iteration is to add the AWS VPC to the AWS environment.

## Procedure

1. Open a terminal
2. Activate your virtual environment
1. cd aws-infrastructure-install/molecule/default

1. **RED** --> Test for the existence of the VPC
    
    1. rm verify.yml
    
    1. Create the **verify.yml** file and add the following contents:
    
          ```yaml
          ---
          # This is an example playbook to execute Ansible tests.
          
          - name: Verify
            hosts: all
            tasks:
              - name: Include the module vars file.
                include_vars:
                  file: ../../defaults/main.yml
          
              - name: Gather facts on the AWS VPC
                ec2_vpc_net_info:
                    aws_access_key: "{{ aws_access_key }}"
                    aws_secret_key: "{{ aws_secret_key }}"
                    region: "{{ aws_region }}"
                    filters:
                          "tag:Name": "{{ aws_infrastructure_install_vpc.name }}"
                register: vpc_info
          
              - name: Print the vpc info
                debug:
                  var: vpc_info
          
              - name: Fail if the VPC does not exist
                fail:
                  msg:  "The VPC called '{{ aws_infrastructure_install_vpc.name }}' does not exist."
                when:
                  - vpc_info.vpcs is defined
                  - vpc_info.vpcs | length  == 0
        
          ``` 
         
      1. cd ../..
      1. Run `molecule converge`
      1. Run `molecule verify`
    
            The test should fail.  We haven't written any
            code to create the AWS vpc.
            The purpose of the test in TDD is to
            first prove that a test fails without writing any
            code.
      1. Run `molecule destroy`

1. **GREEN** --> Add the task to create the vpc to the **tasks/main.yml** file.
    1. Add the following task to the end of th **tasks/main.yml** file.
        
        ```yaml
        - name: Create a VPC with dedicated tenancy and a couple of tags
          ec2_vpc_net:
            name: "{{ aws_infrastructure_install_vpc.name }}"
            cidr_block: 192.168.0.0/16
            dns_support: true
            dns_hostnames: true
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            tags:
              module: "{{ aws_infrastructure_install_vpc.label }}"
            tenancy: default
          register: ec2_vpc_net
        ```
            
      1. Run `molecule converge`
      1. Run `molecule verify`
        
            Verification should
            be successful.  We added the AWS vpc task to
             create the vpc in the
            **tasks/main.yml** file.  We are now
            back in the **Green** state for the
            **Red, Green, Refactor** iteration of Test
            Driven Development (TDD).
      1. Run `molecule destroy`
      
1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **verify.yml** looks a little messy.  Let's extract the new **vpc**
        tasks into a file and reference the file from verify.yml.
    1. mkdir -p molecule/default/tasks
    1. cd molecule/default/tasks
    1. Create the file called **check-for-vpc-existence.yml**.
    1. Remove the tasks starting with the task **Gather facts on the AWS VPC**
    and add them to the **check-for-vpc-existence.yml**.
    1. Add the following task to include the new task file in the **verify.yml* file.
    
          ```yaml
            - name:  Determine if vpc exists
              include_tasks: tasks/check-for-vpc-existence.yml
         ``` 
    
    1. cd ../..
    1. Run `molecule test`.  The test should pass.

We have tested and added the Amazon VPC and completed our 1st TDD iteration.

[**<--Back to main instructions**](../readme.md#1stTDD)