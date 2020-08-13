# 5th TDD Iteration --> Add the AWS VPC security group

Last updated: 08.13.2020

## Purpose

The purpose of this iteration is to add the AWS VPC security group to the AWS environment.

## Procedure

1. Open a terminal
2. Activate your virtual environment
1. cd aws-infrastructure-install/molecule/default


1. **RED** --> Test for the existence of the VPC security group
    
    1. Edit the **verify.yml** file.
    
    1. Add the following contents to the end of the **verify.yml** file:
    
          ```yaml    
          - name:  Determine if security group exists
            ec2_group_info:
              aws_access_key: "{{ aws_access_key }}"
              aws_secret_key: "{{ aws_secret_key }}"
              region: "{{ aws_region }}"
              filters:
                "tag:Name": "{{ aws_infrastructure_install_vpc.security_group }}"
            register: security_group_facts
      
          - name: Print out the security group facts
            debug:
              var: security_group_facts
      
          - name: Fail if the Security Group does not exist
            fail:
              msg:  "The security group called '{{ aws_infrastructure_install_vpc.security_group }}' does not exist."
            when:
              - security_group_facts.security_groups is not defined or security_group_facts.security_groups | length  == 0   
          ``` 
         
      1. cd ../..
      1. Run `molecule converge`
      1. Run `molecule verify`
    
            The test should fail.  We haven't written any
            code to create the AWS vpc security group.
            The purpose of the test in TDD is to
            first prove that a test fails without writing any
            code.
      1. Run `molecule destroy`

1. **GREEN** --> Add the task to create the vpc security group to the **tasks/main.yml** file.
    
    1. Add the following task to the end of th **tasks/main.yml** file.
        
        ```yaml
         - name: create the aws security group for the vpc
           ec2_group:
             name: "{{ aws_infrastructure_install_vpc.security_group }}"
             description: The security group for the AWS cluster
             vpc_id: "{{ vpc_facts.id }}"
             aws_access_key: "{{ aws_access_key }}"
             aws_secret_key: "{{ aws_secret_key }}"
             region: "{{ aws_region }}"
             rules:
               - proto: tcp
                 ports:
                   - 80
                   - 443
                   - 22
                 cidr_ip: 0.0.0.0/0
             tags:
               Name: "{{ aws_infrastructure_install_vpc.security_group }}"
           register: security_group
        ```
            
      1. Run `molecule converge`
      1. Run `molecule verify`
        
            Verification should be successful.  We added the AWS vpc security group tasks to
            create the vpc security group in the
            **tasks/main.yml** file.  We are now
            back in the **Green** state for the
            **Red, Green, Refactor** iteration of Test
            Driven Development (TDD).
      1. Run `molecule destroy`
      
1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **verify.yml** looks a little messy.  Let's extract the new **vpc security group**
        tasks into a file and reference the file from verify.yml.
    1. cd molecule/default/tasks
    1. Create the file called **check-for-vpc-security-group-existence.yml**.
    1. Remove the tasks starting with the task **Determine if security group exists**
    and add them to the **check-for-vpc-security-group-existence.yml** file.
    1. Add the following task to include the new task file in the **verify.yml** file.
    
          ```yaml
            - name:  Determine if the security group exists
              include_tasks: tasks/check-for-vpc-security-group-existence.yml
         ``` 
    
    1. cd ../..
    1. Run `molecule test`.  The test should pass.

We have tested and added the Amazon VPC security group and completed our 5th TDD iteration.

[**<--Back to main instructions**](../readme.md#5thTDD)