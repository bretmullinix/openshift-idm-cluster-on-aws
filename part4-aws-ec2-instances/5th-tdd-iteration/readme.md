# 5th TDD Iteration --> Delete the AWS EC2 Instances

Last updated: 08.24.2020

## Purpose

The purpose of this iteration is to delete the EC2 instances.

## Procedure
1. cd aws-ec2-instances/main.yml
1. change the **ec2-instances** variable to have all instances with the action of
   **delete**.

1. **RED** --> Test for the deletion of the **AWS instances** 
  by just adding a **fail** task to simulate a failure.

    1. cd aws-ec2-instances/tasks/verify
    1. Add the following tasks to the end of the **validate_ec2_instances.yml**
    
        ```yaml
           - name: Intentially fail verify.
             fail:
               msg: "Intentional failure of deleting instances...."
        ```

    1. Run `molecule create`
    1. Run `molecule verify`
    1. The test should fail at the **fail** task we inserted.
    1. The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Delete the EC2 instances by adding the tasks to the
   **main.yml** and **verify.yml**.

    1. The test fails because we added a task that just runs the "fails" module 
       so that **verify** fails on purpose.  Remove the task from the
       **validate_ec2_instances.yml** (called by **verify.yml**).
    1. Run `molecule verify`
    1. Verify should run to completion, and we should be in a **Green** state.
    1. cd aws-ec2-instances/tasks/verify
    1. Add the following tasks to the end of the **validate_ec2_instances.yml**
    
        ```yaml
        - name: Initialize list of EC2 instances that have not been deleted
          set_fact:
            ec2_instances_still_available: "{{ [] }}"
        
        - name: Check to see if AWS EC2 instance is deleted
          include: "{{ role_path }}/tasks/verify/check-if-ec2-instance-is-deleted.yml current_ec2_instance={{ item.name }}"
          with_items: "{{ ec2_instances }}"
          when: item.action == 'delete'
        
        - name: Fail if any AWS EC2 instances are not deleted
          fail:
            msg: "The following EC2 instances did not get deleted: {{ ec2_instances_still_available | join(',') }}"
          when: ec2_instances_still_available | length > 0
        ```
    1. cd ../..
    1. Run 'molecule verify'
    1. The tests should be successful.  We should still be in the **Green** state.
    1. cd tasks/main
    1. Create the file **delete_ec2_instance.yml**.
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
        
        - name: Print instance info
          debug:
            var: ec2_info
        
        - name: Delete EC2 Instance
          ec2:
            instance_ids: "{{ [item_to_delete.instance_id] }}"
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            state: absent
            wait: yes
          with_items: "{{ ec2_info.instances }}"
          loop_control:
            loop_var: item_to_delete
          when:  ec2_info.instances is defined and ec2_info.instances | length > 0
        ```
    1. cd ..
    1. Add the following content before the task 
       **Create the EC2 Instances and Output Results**
       in the **tasks/main.yml**.
    
        ```yaml   
       - name: Delete the EC2 Instances
         include: "{{ role_path }}/tasks/main/delete_ec2_instance.yml current_ec2_instance={{ item.name }}"
         with_items: "{{ ec2_instances }}"
         when: item.action == 'delete'  
       ```
    1. cd ..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**
       and populates the **AWS VPC subnet facts** needed to create the ec2 instances.
    
    1. Run `molecule verify`. The test should pass.  The test represents
       the **Green** in the **Red, Green, Refactor** iteration of TDD.

1. **REFACTOR** --> Does any of the code need **Refactoring**?

None of the files look like refactoring is needed.  We have completed the 
iteration to introduce EC2 instance deletion.

[**<--Back to main instructions**](../readme.md#5thTDD)