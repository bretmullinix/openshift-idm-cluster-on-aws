# 2nd TDD Iteration --> Get the VPC Facts

Last updated: 08.20.2020

## Purpose

The purpose of this iteration is to get the VPC facts need to
create the EC2 instances.

## Procedure

1. **RED** --> Test for the existence of the **AWS VPC** using a fake vpc name.

    1. cd aws-ec2-instances/tasks
    1. Edit the **verify.yml** file.
    1. At the end of the **verify.yml** file, add the following tasks.
    
        ```yaml
        - name: Force a failure by naming a non-existent VPC
          set_fact:
            aws_vpc: "{{ aws_vpc|default({}) | combine( { 'name': 'the_fake_vpc'} ) }}"
        
        - name: Gather facts on the AWS VPC using the Tag 'Name'
          ec2_vpc_net_info:
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            filters:
              "tag:Name": "{{ aws_vpc.name }}"
          register: vpc_info
        
        
        - name: Fail if the VPC does not exist
          fail:
            msg:  "The VPC called '{{ aws_vpc.name }}' does not exist."
          when:
            - vpc_info.vpcs is not defined or vpc_info.vpcs | length  == 0
        ```
    1. Run `molecule verify`
    1. The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Remove the fake vpc name from verify.yml and add the
gathering of VPC facts to the main.yml

    1. cd aws-ec2-instances/tasks
    1. Remove the task labeled **Force a failure by naming a non-existent VPC**
    from the **verify.yml** file.
    1. Add the following content to the end of the main.yml
    
        ```yaml
        - name: Gather facts on the AWS VPC using the Tag 'Name'
          ec2_vpc_net_info:
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            filters:
              "tag:Name": "{{ aws_vpc.name }}"
          register: vpc_info
        
        - name: Create vpc facts
          set_fact:
            vpc: "{{ vpc_info.vpcs[0] }}"
          when: vpc_info is defined and vpc_info.vpcs is defined and vpc_info.vpcs | length > 0
        ```
    1. cd ..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**
       and populates the **AWS VPC facts** needed to create the ec2 instances.
    
    1. Run `molecule verify`. The test should pass.  The test represents
       the **Green** in the **Red, Green, Refactor** iteration of TDD.
  
1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **aws-ec2-instances/tasks/verify.yml** looks a 
       little messy with all the tasks verifying the existence of the vpc.
       Let's move the tasks to a separate file.
    
        1. Create the file **aws-ec2-instances/tasks/verify/check-if-vpc-is-present.yml**  
        1. Remove all the content starting from the 
        **Gather facts on the AWS VPC using the Tag 'Name'** task in the
        **aws-ec2-instances/tasks/verify.yml**
           and place the contents in the **check-if-vpc-is-present.yml**.
        1. In the **aws-ec2-instances/tasks/verify.yml**, add the following content to the end:
        
            ```yaml
               - name: Check if the AWS VPC is present.
                 include_tasks: "{{ role_path }}/tasks/verify/check-if-vpc-is-present.yml"
           ```
        1. Run `molecule test` to ensure the role works as intended.
        
    1. We have not completed our refactoring.  The **aws-ec2-instances/tasks/main.yml**
       file looks messy as well. 
        
        1. Create the file **aws-ec2-instances/tasks/main/get_vpc_facts.yml**  
    
            1. Remove all the content starting from the
               **Gather facts on the AWS VPC using the Tag 'Name'** task
               in the **aws-ec2-instances/tasks/main.yml** file
               and place the contents in the **get_vpc_facts.yml**.
                
            1. In the **aws-ec2-instances/tasks/main.yml**, add the following content to the end:
                
                 ```yaml
                  - name: Get the VPC information
                    include_tasks: "{{ role_path }}/tasks/main/get_vpc_facts.yml"
                 ```
                
            1. Run `molecule test` to ensure the role works as intended.
        
    1. We look at the role files and determine that no other refactoring is needed.
       We have completed our refactoring.  

[**<--Back to main instructions**](../readme.md#2ndTDD)