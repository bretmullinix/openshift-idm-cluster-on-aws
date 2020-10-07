# 6th TDD Iteration --> Start the AWS EC2 Instances

Last updated: 10.07.2020

## Purpose

The purpose of this iteration is to start the EC2 instances.

## Procedure

1. **RED** --> Test for the starting of the **AWS instances**.

    1. cd aws-ec2-instances/defaults
    
    1. Edit the **main.yml** and change the action for all the **ec2_instances** to **start**
    
    1. cd ../tasks/verify
    
    1. Create the file **check-if-ec2-instance-is-started.yml**
    
    1. Add the following tasks to the **check-if-ec2-instance-is-started.yml** file.
    
        ```yaml
        - name: Get EC2 instance information
          ec2_instance_info:
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            filters:
              "tag:Name": "{{ current_ec2_instance }}"
          register: ec2_info
        
        - name: Fail the task if the EC2 Instance is not started
          set_fact:
            ec2_instances_not_started: "{{ ec2_instances_not_started + [current_ec2_instance] }}"
          when:
              (
              ec2_info.instances is not defined or
              ec2_info.instances and ec2_info.instances | length == 0
              ) or
              (
              ec2_info.instances and ec2_info.instances | length > 0 and
              ec2_info.instances[0].state is defined and
              ec2_info.instances[0].state["name"] != 'running'
              )
        ```
    1. cd ../..
    1. Run `molecule create`
    
    1. Run `molecule verify`
    
    1. The test fails because we don't have an action for "start"
    
    1. cd tasks/verify
    
    1. In the file **aws-ec2-instances/tasks/verify/validate_ec2_instances.yml**, replace the task named 
       **Fail if EC2 instance action is invalid** with the following:
    
        ```yaml
        - name: Fail if EC2 instance action is invalid
          fail:
            msg: "The '{{ item.name }}' EC2 instance action '{{ item.action }}' is not valid.
                      You must choose either the action 'create', 'delete', or 'start'."
          with_items: " {{ ec2_instances }}"
          when: item.action != "create" and item.action != "delete" and item.action != "start"
        ```
       
    1. cd ../..
    1. Run `molecule verify`
    
    1. cd tasks/verify
    
    1. The task succeeds, but we haven't added the validation logic to see if the EC2 instances are started.
       Add the following logic to the end of the **validate_ec2_instances.yml** file.
       
       ```yaml
       - name: Initialize list of EC2 instances that have not been started
         set_fact:
           ec2_instances_not_started: "{{ [] }}"
       
       - name: Check to see if AWS EC2 instances are started
         include: "{{ role_path }}/tasks/verify/check-if-ec2-instance-is-started.yml current_ec2_instance={{ item.name }}"
         with_items: "{{ ec2_instances }}"
         when: item.action == 'start'
       
       - name: Fail if any AWS EC2 instances are not started
         fail:
           msg: "The following EC2 instances did not get started: {{ ec2_instances_not_started | join(',') }}"
         when: ec2_instances_not_started | length > 0
       ```
    
    1. cd ../..
    
    1. Run `molecule verify`
      
    1. The test should fail saying that an instance has not been created.  The
       failure is correct because we did not create any instances yet.  
       
    1. The test represents the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Create the EC2 instances by adding the tasks to the
   **main.yml**.

    1. cd aws-ec2-instances/defaults
    
    1. Change the **ec2_instances** action to **create**
    
    1. cd ..
    
    1. Run `molecule converge`
    
    1. cd tasks/main
    
    1. Create the file **start_ec2_instances.yml**
    
    1. Add the following content the file.
    
        ```yaml
        - name: Get EC2 instance information
          ec2_instance_info:
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            filters:
              "tag:Name": "{{ current_ec2_instance }}"
          register: ec2_info
        
        - name: Start EC2 Instance
          ec2:
            instance_ids: "{{ [item_to_start.instance_id] }}"
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            state: running
            wait: yes
          with_items: "{{ ec2_info.instances }}"
          loop_control:
            loop_var: item_to_start
          when:  ec2_info.instances is defined and ec2_info.instances | length > 0 and item_to_start.state.name != 'terminated'
        ```
    
    1. cd ..
    
    1. Add the following task to the **main.yml**.
    
        ```yaml
         - name: Start the EC2 Instances
           include: "{{ role_path }}/tasks/main/start_ec2_instances.yml current_ec2_instance={{ item.name }}"
           with_items: "{{ ec2_instances }}"
           when: item.action == 'start'
       ```
    
    1. cd ../defaults
    
    1. In the **default/main.yml**, change the ec2_instances action to **start**
    
    1. cd ..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**
       and starts the ec2 instances.
    
    1. Run `molecule verify`. The test should pass.
    
    1. Let's run one more step.
    
    1. Go to the AWS console and stop the EC2 instances listed in your **default/main.yml** file.
    
    1. Run `molecule converge`
    
    1. Run `molecule verify`. The test should pass.  The test represents
       the **Green** in the **Red, Green, Refactor** iteration of TDD.
  
1. **REFACTOR** --> Does any of the code need **Refactoring**?

    Looks like the Ansible role does not need any refactoring, so we have finished this TDD iteration.

[**<--Back to main instructions**](../readme.md#6thTDD)