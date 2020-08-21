# 4th TDD Iteration --> Create the AWS EC2 Instances

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
        
        - name: Register failure count
          set_fact:
            ec2_instances_not_created: "{{ ec2_instances_not_created + [current_ec2_instance] }}"
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
            ec2_instances_still_available: "{{ ec2_instances_still_available + [current_ec2_instance] }}"
          when: ec2_info.instances and ec2_info.instances | length > 0
        ```
    1. cd ..
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

1. **GREEN** --> Create the EC2 instances by adding the tasks to the
   **main.yml**.

    1. cd aws-ec2-instances/tasks
    1. Add the following content to the end of the main.yml
    
        ```yaml
        # Single instance with ssd gp2 root volume
        - name: Create EC2 Instance
          ec2:
            key_name: "{{ item.key_name }}"
            group: "{{ aws_vpc.security_group }}"
            instance_type: "{{ item.instance_type }}"
            image: "{{ item.ami }}"
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            wait: true
            wait_timeout: 500
            volumes:
              - device_name: /dev/sda1
                volume_type: gp2
                volume_size: "{{ item.root_volume_size }}"
                delete_on_termination: true
            vpc_subnet_id: "{{ vpc_control_subnet.id }}"
            assign_public_ip: true
            count_tag:
              Name: "{{ item.name }}"
            instance_tags:
              Name: "{{ item.name }}"
            exact_count: 1
          with_items: "{{ ec2_instances }}"
          when: item.action == "create"
          register: ec2_facts
        
        - name: Recursively remove ec2 facts directory
          file:
            path: "{{ role_path }}/files/ec2_facts"
            state: absent
       
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
                         ['name:  ' + item.tagged_instances[0].tags.Name  ]
                         + [ 'public_ip:  ' + item.tagged_instances[0].public_ip  ]
                         + [ 'private_ip:  ' + item.tagged_instances[0].private_ip  ]
                         + [ 'key_pair:  ' + item.tagged_instances[0].key_name ]
                         + [ 'ssh connection: ssh -i ' + role_path  + '/files/private_keys/'
                         + item.tagged_instances[0].key_name
                         + ' centos@' + item.tagged_instances[0].public_ip ]
                         + ['\n']
                         }}"
          with_items: "{{ ec2_facts.results }}"
          when: ec2_facts.results is defined and ec2_facts.results | length > 0
        
        - name: Output the EC2 Facts
          copy:
            content: "{{ ec2_facts }}"
            dest: "{{ role_path}}/files/ec2_facts/{{ lookup('pipe','date +%m-%d-%Y-%H-%M-%S') }}_facts"
          delegate_to: localhost
        
        - name: Output the EC2 Inventory Information
          copy:
            content: "{{ ec2_results | join('\n') }}"
            dest: "{{ role_path}}/files/ec2_facts/{{ lookup('pipe','date +%m-%d-%Y-%H-%M-%S') }}_inventory"
          delegate_to: localhost
          when: ec2_results and ec2_results | length > 0
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
    
        1. Create the file **aws-ec2-instances/tasks/verify/validate_ec2_instances.yml**  
        
        1. Remove all the content starting from the 
           **Fail if EC2 instance action is invalid** task in the
           **aws-ec2-instances/tasks/verify.yml**
           and place the contents in the **validate_ec2_instance.yml**.
        
        1. In the **aws-ec2-instances/tasks/verify.yml**, 
           add the following content to the end:
        
            ```yaml
               - name: Validate the EC2 Instances.
                 include_tasks: "{{ role_path }}/tasks/verify/validate_ec2_instances.yml"
           ```
        1. Run `molecule test` to ensure the role works as intended.
        
    1. We have not completed our refactoring.  The **aws-ec2-instances/tasks/main.yml**
       file looks messy as well. 
        
        1. Create the file **aws-ec2-instances/tasks/main/create_ec2_instances.yml**  
    
            1. Remove all the content starting from the
               **Create EC2 Instance** task
               in the **aws-ec2-instances/tasks/main.yml** file
               and place the contents in the **create_ec2_instances.yml**.
                
            1. In the **aws-ec2-instances/tasks/main.yml**, 
               add the following content to the end:
                
                 ```yaml
                  - name: Create the EC2 Instances and Output Results
                    include_tasks: "{{ role_path }}/tasks/main/create_ec2_instances.yml"
                 ```
                
            1. Run `molecule test` to ensure the role works as intended.
        
    1. We look at the role files and determine that no other refactoring is needed.
       We have completed our refactoring.  

[**<--Back to main instructions**](../readme.md#4thTDD)