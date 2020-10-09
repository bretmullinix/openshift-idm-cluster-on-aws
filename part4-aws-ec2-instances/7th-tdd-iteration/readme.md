# 7th TDD Iteration --> Stop the AWS EC2 Instances

Last updated: 10.09.2020

## Purpose

The purpose of this iteration is to stop the EC2 instances.

## Procedure

1. **RED** --> Test for the starting of the **AWS instances**.

    1. cd aws-ec2-instances/defaults
    
    1. Edit the **main.yml** and change the action for all the **ec2_instances** to **stop**
    
    1. cd ../tasks/verify
    
    1. Create the file **check-if-ec2-instance-is-stopped.yml**
    
    1. Add the following tasks to the **check-if-ec2-instance-is-stopped.yml** file.
    
        ```yaml
        - name: Populate filter for EC2 Instance
          set_fact:
            filter_for_ec2_info: "{{  {'tag:Name': current_ec2_instance,
                                                'instance-state-name': 'stopped' }
                                          }}"
        - name: Get EC2 instance information
          ec2_instance_info:
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            filters: "{{ filter_for_ec2_info }}"
          register: ec2_stop_info
        
        - name: Add the task to the ec2_start_info list if the EC2 Instance is not stopped
          set_fact:
            ec2_instances_not_stopped: "{{ ec2_instances_not_stopped + [current_ec2_instance] }}"
          when: >
            ec2_stop_info is undefined or
            ec2_stop_info.instances is undefined or
            ec2_stop_info.instances | length == 0
        ```
    
    1. cd ../..
    
    1. Run `molecule create`
    
    1. Run `molecule verify`
    
    1. The test fails because we don't have an action for **stop**.
    
    1. cd tasks/verify
    
    1. In the file **aws-ec2-instances/tasks/verify/validate_ec2_instances.yml**, replace the task named 
       **Fail if EC2 instance action is invalid** with the following:
    
        ```yaml
         - name: Fail if EC2 instance action is invalid
           fail:
             msg: "The '{{ item.name }}' EC2 instance action '{{ item.action }}' is not valid.
                      You must choose either the action 'create', 'delete', 'start', or 'stop'."
           with_items: " {{ ec2_instances }}"
           when: item.action != "create" and item.action != "delete" and item.action != "start" and 
                 item.action != "stop"
        ```
       
    1. cd ../..
    1. Run `molecule verify`
    
    1. cd tasks/verify
    
    1. The task succeeds, but we haven't added the validation logic to see if the EC2 instances are stopped.
       Add the following logic to the end of the **validate_ec2_instances.yml** file.
       
       ```yaml
       - name: Initialize list of EC2 instances that have not been stopped
         set_fact:
           ec2_instances_not_stopped: "{{ [] }}"
       
       - name: Check to see if AWS EC2 instances are stopped
         include: "{{ role_path }}/tasks/verify/check-if-ec2-instance-is-stopped.yml 
                    current_ec2_instance={{ item.name }}"
         with_items: "{{ ec2_instances }}"
         when: item.action == 'stop'
       
       - name: Fail if any AWS EC2 instances are not stopped
         fail:
           msg: "The following EC2 instances did not get stopped: {{ ec2_instances_not_stopped | join(',') }}"
         when: ec2_instances_not_stopped | length > 0
       ```
    
    1. cd ../..
    
    1. Run `molecule verify`
      
    1. The test should fail saying that the instance(s) have not been stopped.  The
       failure is correct because we did not create any instances yet.  
       
    1. The test represents the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Start the EC2 instances by adding the tasks to the
   **main.yml**.

    1. cd aws-ec2-instances/defaults
    
    1. Change the **ec2_instances** action to **create**
    
    1. cd ..
    
    1. Run `molecule converge`
    
    1. cd tasks/main
    
    1. Create the file **stop_ec2_instances.yml**
    
    1. Add the following content the file.
    
        ```yaml
        - name: Initialize list of EC2 instances Ids
          set_fact:
            ec2_instance_ids: "{{ [] }}"
        
        - name: Get list of EC2 Instances
          include: "{{ role_path }}/tasks/main/get_ec2_instance_id.yml current_ec2_instance={{ item.name }}"
          with_items: "{{ ec2_instances }}"
          when: item.action == 'stop'
        
        - name: Stop EC2 Instances
          ec2:
            instance_ids: "{{ ec2_instance_ids }}"
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            state: running
            wait: yes
          when: ec2_instance_ids | length > 0
          register: started_ec2_facts       
        ```
    
    1. cd ..
    
    1. Before the task named **Output the EC2 Instance Facts and Inventory for 'create' and 'start' actions**  in the
       **main.yml**, add the following task.
    
        ```yaml
        - name: Stop the EC2 Instances
          include_tasks: "{{ role_path }}/tasks/main/stop_ec2_instances.yml"
       ```
    
    1. cd ../defaults
    
    1. In the **default/main.yml**, change the ec2_instances action to **stop**
    
    1. cd ..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**
       and stops the ec2 instances.
    
    1. Run `molecule verify`. The test should pass.
    
    1. Let's run one more step.
    
    1. Go to the AWS console and **start** the EC2 instances listed in your **default/main.yml** file.
    
    1. Run `molecule converge`
    
    1. Run `molecule verify`. The test should pass.  The test represents
       the **Green** in the **Red, Green, Refactor** iteration of TDD.
  
1. **REFACTOR** --> Does any of the code need **Refactoring**?

    The code looks pretty good, so we have completed our 7th TDD iteration.  Please return to the main page.
    
    

[**<--Back to main instructions**](../readme.md#6thTDD)
