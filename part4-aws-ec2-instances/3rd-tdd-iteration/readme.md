# 3rd TDD Iteration --> Get the VPC Subnet Facts

Last updated: 08.21.2020

## Purpose

The purpose of this iteration is to get the VPC subnet facts needed to
create the EC2 instances.

## Procedure

1. **RED** --> Test for the existence of the **AWS VPC subnet** 
   using a fake vpc subnet name.

    1. cd aws-ec2-instances/tasks
    1. Edit the **verify.yml** file.
    1. At the end of the **verify.yml** file, add the following tasks.
    
        ```yaml
        - name: Force a failure by naming a non-existent VPC subnet
          set_fact:
            aws_vpc: "{{ aws_vpc|default({}) | combine( { 'subnets':  { 'control': { 'name': 'fake_subnet_name' } } } ) }}"
        
        - name: Gather facts on the AWS Control Subnet
          ec2_vpc_subnet_info:
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            filters:
              "tag:Name": "{{ aws_vpc.subnets.control.name }}"
          register: vpc_control_subnet_info
        
        
        - name: Print the vpc control subnet info
          debug:
            var: vpc_control_subnet_info
        
        - name: Fail if the control subnet does not exist
          fail:
            msg:  "The subnet called '{{ aws_vpc.subnets.control.name  }}' does not exist."
          when:
            - vpc_control_subnet_info.subnets is defined
            - vpc_control_subnet_info.subnets | length  == 0
        ```

    1. Run `molecule verify`
    1. The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Remove the fake vpc name from verify.yml and add the
gathering of VPC facts to the main.yml

    1. cd aws-ec2-instances/tasks
    1. Remove the task labeled **Force a failure by naming a non-existent VPC subnet**
    from the **verify.yml** file.
    1. Add the following content to the end of the main.yml
    
        ```yaml
        
        ```
    1. cd ..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**
       and populates the **AWS VPC subnet facts** needed to create the ec2 instances.
    
    1. Run `molecule verify`. The test should pass.  The test represents
       the **Green** in the **Red, Green, Refactor** iteration of TDD.
  
1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **aws-ec2-instances/tasks/verify.yml** looks a 
       little messy with all the tasks verifying the existence of the vpc subnet.
       Let's move the tasks to a separate file.
    
        1. Create the file **aws-ec2-instances/tasks/verify/check-if-vpc-subnet-is-present.yml**  
        
        1. Remove all the content starting from the 
           **Gather facts on the AWS VPC subnet using the Tag 'Name'** task in the
           **aws-ec2-instances/tasks/verify.yml**
           and place the contents in the **check-if-vpc-is-subnet-present.yml**.
        
        1. In the **aws-ec2-instances/tasks/verify.yml**, 
           add the following content to the end:
        
            ```yaml
               - name: Check if the AWS VPC is present.
                 include_tasks: "{{ role_path }}/tasks/verify/check-if-vpc-subnet-is-present.yml"
           ```
        1. Run `molecule test` to ensure the role works as intended.
        
    1. We have not completed our refactoring.  The **aws-ec2-instances/tasks/main.yml**
       file looks messy as well. 
        
        1. Create the file **aws-ec2-instances/tasks/main/get_vpc_subnet_facts.yml**  
    
            1. Remove all the content starting from the
               **Gather facts on the AWS VPC subnet using the Tag 'Name'** task
               in the **aws-ec2-instances/tasks/main.yml** file
               and place the contents in the **get_vpc_subnet_facts.yml**.
                
            1. In the **aws-ec2-instances/tasks/main.yml**, 
               add the following content to the end:
                
                 ```yaml
                  - name: Get the VPC subnet information
                    include_tasks: "{{ role_path }}/tasks/main/get_vpc_subnet_facts.yml"
                 ```
                
            1. Run `molecule test` to ensure the role works as intended.
        
    1. We look at the role files and determine that no other refactoring is needed.
       We have completed our refactoring.  

[**<--Back to main instructions**](../readme.md#3rdTDD)