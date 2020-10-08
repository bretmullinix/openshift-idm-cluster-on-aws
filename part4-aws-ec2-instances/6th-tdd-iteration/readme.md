# 6th TDD Iteration --> Start the AWS EC2 Instances

Last updated: 10.08.2020

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
    
    1. Create the file **get_ec2_instance_id.yml**
    
    1. Add the following content to the file.
    
        ```yaml
        - name: Get EC2 instance information
          ec2_instance_info:
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            filters:
              "tag:Name": "{{ current_ec2_instance }}"
          register: ec2_info
        
        - name: Populate Instance Id
          set_fact:
            ec2_instance_ids: "{{ ec2_instance_ids + [item_to_get_id_for.instance_id] }}"
          with_items: "{{ ec2_info.instances }}"
          loop_control:
            loop_var: item_to_get_id_for
          when:
            - ec2_info is defined
            - ec2_info.instances is defined
            - ec2_info.instances | length > 0
            - item_to_get_id_for.state.name != 'terminated'
        ```
    
    1. Create the file **start_ec2_instances.yml**
    
    1. Add the following content the file.
    
        ```yaml
        - name: Initialize list of EC2 instances Ids
          set_fact:
            ec2_instance_ids: "{{ [] }}"
        
        - name: Get list of EC2 Instances
          include: "{{ role_path }}/tasks/main/get_ec2_instance_id.yml current_ec2_instance={{ item.name }}"
          with_items: "{{ ec2_instances }}"
          when: item.action == 'start'
        
        - name: Start EC2 Instances
          ec2:
            instance_ids: "{{ ec2_instance_ids }}"
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            state: running
            wait: yes
          when: ec2_instance_ids | length > 0
          register: started_ec2_facts
        
        - name: Create a folder to hold the ec2 facts
          file:
            path: "{{ role_path }}/files/ec2_facts"
            state: directory
            mode: '0755'
          delegate_to: localhost
        
        - name: Initialize EC2 list of dictionaries
          set_fact:
            ec2_results: []
        
        
        - name: Populate the EC2 list of dictionaries
          set_fact:
            ec2_results: "{{ ec2_results +
                         ['name:  ' + item.tags.Name  ]
                         + [ 'public_ip:  ' + item.public_ip  ]
                         + [ 'private_ip:  ' + item.private_ip  ]
                         + [ 'key_pair:  ' + item.key_name ]
                         + [ 'ssh connection: ssh -i ' + role_path  + '/files/private_keys/'
                         + item.key_name
                         + ' centos@' + item.public_ip ]
                         + ['\n']
                         }}"
          with_items: "{{ started_ec2_facts.instances }}"
        
        - name: Output the EC2 Facts
          copy:
            content: "{{ ec2_facts }}"
            dest: "{{ role_path}}/files/ec2_facts/{{ lookup('pipe','date +%m-%d-%Y-%H-%M-%S') }}_facts_for_started"
          delegate_to: localhost
        
        - name: Output the EC2 Inventory Information
          copy:
            content: "{{ ec2_results | join('\n') }}"
            dest: "{{ role_path}}/files/ec2_facts/{{ lookup('pipe','date +%m-%d-%Y-%H-%M-%S') }}_inventory_for_started"
          delegate_to: localhost
          when: ec2_results and ec2_results | length > 0
        ```
    
    1. cd ..
    
    1. Add the following task to the **main.yml**.
    
        ```yaml
        - name: Start the EC2 Instances
          include_tasks: "{{ role_path }}/tasks/main/start_ec2_instances.yml"
       ```
    
    1. cd ../defaults
    
    1. In the **default/main.yml**, change the ec2_instances action to **start**
    
    1. cd ..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**
       and starts the ec2 instances.
    
    1. Run `molecule verify`. The test should pass.
    
    1. Let's run one more step.
    
    1. Go to the AWS console and **stop** the EC2 instances listed in your **default/main.yml** file.
    
    1. Run `molecule converge`
    
    1. Run `molecule verify`. The test should pass.  The test represents
       the **Green** in the **Red, Green, Refactor** iteration of TDD.
  
1. **REFACTOR** --> Does any of the code need **Refactoring**?

    We output Ansible Facts and Inventory for EC2 instances with the actions of **create**
    and **start**.  We need to consolidate this into one output at the end.
    
    1. cd **tasks/main**
    
    1. Create the file **output_facts_and_inventory.yml**.
    
    1. Add the following content to the file.
    
        ```yaml
        - name: Initialize list of EC2 instances Ids
          set_fact:
            ec2_instance_ids: "{{ [] }}"
        
        - name: Get list of EC2 Instances
          include: "{{ role_path }}/tasks/main/get_ec2_instance_id.yml current_ec2_instance={{ item.name }}"
          with_items: "{{ ec2_instances }}"
          when: item.action == 'start' or item.action == 'create'
        
        - name: Get EC2 instance facts for those with an action of 'start' and 'create'
          ec2_instance_info:
            instance_ids: "{{ ec2_instance_ids }}"
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
          when: ec2_instance_ids | length > 0
          register: ec2_facts_to_output
        
        - name: Create a folder to hold the ec2 facts
          file:
            path: "{{ role_path }}/files/ec2_facts"
            state: directory
            mode: '0755'
          delegate_to: localhost
        
        - name: Initialize EC2 list of dictionaries
          set_fact:
            ec2_results: []
        
        
        - name: Populate the EC2 list of dictionaries
          set_fact:
            ec2_results: "{{ ec2_results +
                         ['name:  ' + item.tags.Name  ]
                         + [ 'public_ip:  ' + item.public_ip_address  ]
                         + [ 'private_ip:  ' + item.private_ip_address  ]
                         + [ 'key_pair:  ' + item.key_name ]
                         + [ 'ssh connection: ssh -i ' + role_path  + '/files/private_keys/'
                         + item.key_name
                         + ' centos@' + item.public_ip_address ]
                         + ['\n']
                         }}"
          with_items: "{{ ec2_facts_to_output.instances }}"
          when:
            -  ec2_facts_to_output is defined
            -  ec2_facts_to_output.instances is defined
        
        - name: Output the EC2 Facts
          copy:
            content: "{{ ec2_facts }}"
            dest: "{{ role_path}}/files/ec2_facts/{{ lookup('pipe','date +%m-%d-%Y-%H-%M-%S') }}_facts"
          delegate_to: localhost
          when: ec2_facts is defined
        
        - name: Output the EC2 Inventory Information
          copy:
            content: "{{ ec2_results | join('\n') }}"
            dest: "{{ role_path}}/files/ec2_facts/{{ lookup('pipe','date +%m-%d-%Y-%H-%M-%S') }}_inventory"
          delegate_to: localhost
          when: ec2_results and ec2_results | length > 0
        ```
    
    1. In the **start_ec2_instances.yml** file, starting with the task labeled **Create a folder to hold the
       ec2 facts**, remove this task and any following task.
       
    1. In the **create_ec2_instances.yml** file, starting with the task labeled **Recursively remove ec2 
       facts directory**, remove this task and any following task.
       
    1. cd ..
    
    1. Add the following task to the end of the **main.yml**
    
        ```yaml
        - name: Output the EC2 Instance Facts and Inventory for 'create' and 'start' actions
          include_tasks: "{{ role_path }}/tasks/main/output_facts_and_inventory.yml"
       ```
    
    1. In the **aws-ec2-instances/defaults/main.yml** file, add the following **ec2_instance** to the 
       **ec2_instances** variable.
    
        ``yaml
          - name: third_instance
            ami: "ami-00594b9c138e6303d"
            instance_type: "t2.medium"
            root_volume_size: 25
            subnet_name: "aws_infrastructure_control_subnet"
            key_name: "your_keypair"
            action: "create"
        ``
    
    1. Run `molecule test`.  The test should pass.
    
        The code looks pretty good, so we have completed our 6th TDD iteration.
    
    

[**<--Back to main instructions**](../readme.md#6thTDD)