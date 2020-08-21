# 3rd TDD Iteration --> Create the AWS EC2 Instances

Last updated: 08.21.2020

## Purpose

The purpose of this iteration is to create the EC2 instances.

## Procedure

1. **RED** --> Test for the existence of the **AWS instances** 
   using a fake ec2_instance.

    1. cd aws-ec2-instances/tasks/verify
    1. Create the file **check-if-ec2-instance-is-created.yml**
    1. Add the following tasks to the **check-if-ec2-instance-is-created.yml** file.
    
        ```yaml
        - name: Get EC2 instance information
          ec2_instance_info:
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            filters:
              "tag:Name": "{{ current_ec2_instance }}"
          register: ec2_info
        
        
        - name: Fail if EC2 instance is not created
          fail:
            msg: "The '{{ current_ec2_instance }}' EC2 instance has not been created."
          when: ec2_info.instances is not defined or ec2_info.instances | length == 0
        ```
    1. Create the file **check-if-ec2-instance-is-deleted.yml**
    1. Add the following tasks to the **check-if-ec2-instance-is-deleted.yml** file.
    
        ```yaml
        - name: Get EC2 instance information
          ec2_instance_info:
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            filters:
              "tag:Name": "{{ current_ec2_instance }}"
          register: ec2_info
        
        - name: Register failure count
          set_fact:
            ec2_instances_not_created: "{{ ec2_instances_not_created + [current_ec2_instance] }}"
          when: ec2_info.instances is not defined or ec2_info.instances | length == 0
        ```
    1. Add the following tasks to the end of the **verify.yml**
    
        ```yaml
        - name: Force a failure by changing the an ec2_instance action to an invalid value
          set_fact:
            ec2_instances: "{{ ec2_instances + [item] }}"
          with_items:
            - name: "fake_instance"
              action: "fake_action"

        - name: Fail if EC2 instance action is invalid
          fail:
            msg: "The '{{ item.name }}' EC2 instance action '{{ item.action }}' is not valid.
                  You must choose either the action 'create' or 'delete'."
          with_items: " {{ ec2_instances }}"
          when: item.action != "create" and item.action != "delete"
        

        - name: Initialize list of EC2 instances that have not been created
          set_fact:
            ec2_instances_not_created: "{{ [] }}"
        
        - name: Check to see if AWS EC2 instance is created
          include: "{{ role_path }}/tasks/verify/check-if-ec2-instance-is-created.yml current_ec2_instance={{ item.name }}"
          with_items: "{{ ec2_instances }}"
          when: item.action == 'create'
        
        - name: Fail if any AWS EC2 instances are not created
          fail:
            msg: "The following EC2 instances did not get created: {{ ec2_instances_not_created | join(',') }}"
          when: ec2_instances_not_created | length > 0
        ```
    
    1. Run `molecule verify`
    1. The test fails because we created an ec2 instance with a fake action called
      **fake_action**.  Remove the task called 
      "Force a failure by changing the an ec2_instance action to an invalid value"
      in the **verify.yml**.
    1. Run `molecule verify`
    1. The test should fail saying that an instance has not been created.  The
    failure is correct because we did not create any instances yet.     
    1. The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Remove the fake vpc name from verify.yml and add the
gathering of VPC facts to the main.yml

    1. cd aws-ec2-instances/tasks
    1. Remove the task labeled **Force a failure by naming a non-existent VPC subnet**
    from the **verify.yml** file.
    1. Add the following content to the end of the main.yml
    
        ```yaml
        - name: Gather facts on the AWS Control subnet
          ec2_vpc_subnet_info:
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            filters:
              "tag:Name": "{{ aws_vpc.subnets.control.name }}"
          register: vpc_control_subnet_info
        
        - name: Fail if the control subnet does not exist
          fail:
            msg:  "The subnet called '{{ aws_vpc.subnets.control.name  }}' does not exist."
          when:
            - vpc_control_subnet_info.subnets is defined
            - vpc_control_subnet_info.subnets | length  == 0
        
        - name: Get the subnet fact
          set_fact:
            vpc_control_subnet: "{{ vpc_control_subnet_info.subnets[0]  }}"
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
           **Gather facts on the AWS Control subnet** task in the
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
               **Gather facts on the AWS Control subnet** task
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