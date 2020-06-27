# 2nd TDD Iteration --> Add firewalld

Last updated: 06.27.2020

## Purpose

The purpose of this iteration is to add **firewalld** to the target servers.

## Procedure
1. cd idm-install/molecule/default

1. **RED** --> Test for the existence of **firewalld**.
    
    1. Add the following code to the end of **verify.yml**.
        
        ```yaml
        - name:  Determine if firewalld exists
          set_fact:
            firewalld_service_exists: true
          loop: "{{ lookup('dict', services_state.ansible_facts.services) }}"
          when: "'firewalld.service' in item.key"
    
        - name: Pass if firewalld service exists
          debug:
            msg: "Firewalld exists!!!"
          when: firewalld_service_exists is defined
    
        - name: Fail if firewalld service doesn't exist
          fail:
            msg: "The firewalld servece does not exist"
          when: firewalld_service_exists is not defined
        ```
           
        The tasks above checks to see if **firewalld** is in the list of
        services.
    1. cd ../..
    1. Run `molecule verify`.  The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **Green** --> Add **firewalld** to the ansible role.
     
    1. cd molecule/default
        
    1. Add the following tasks to the end of the **tasks/main.yml** file.
        
    ```yaml
    - name: Install Firewalld Service
      yum:
        name: firewalld
        state: present
    ```   
           
    The task will install **firewalld**.
        
    1. cd ../..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**
    and installs **firewalld**.
    
    1. Run `molecule verify`. The test should pass.  The test represents
    the **Green** in the **Red, Green, Refactor** iteration of TDD.

1. **Refactor** --> Does any of the code need **Refactoring**?

    1. The **verify.yml** looks a little messy.  Lets us extract the **firewalld**
        tasks out into a file and reference the file from verify.yml.
        
    1. cd molecule/default
        
    1. mkdir tasks
        
    1. cd tasks
        
    1. Create the file called **add-firewalld.yml** and add the following content:
        
        ```yaml
       - name:  Determine if firewalld exists
         set_fact:
           firewalld_service_exists: true
         loop: "{{ lookup('dict', services_state.ansible_facts.services) }}"
         when: "'firewalld.service' in item.key"
       
       - name: Pass if firewalld service exists
         debug:
           msg: "Firewalld exists!!!"
         when: firewalld_service_exists is defined
       
       - name: Fail if firewalld service doesn't exist
         fail:
           msg: "The firewalld service does not exist"
         when: firewalld_service_exists is not defined
    
       ```
        
    1. cd ..
        
    1. Remove the firewalld tasks above from the **verify.yml**.
        
    1. Add the following to the end of **verify.yml**.
        
        ```yaml
          - name:  Determine if firewalld exists
            include_tasks: tasks/add-firewalld.yml
       ```          
           
    1. cd ../..
    1. Run `molecule test`.  The test should pass.  Your refactoring is complete.

We have added **firewalld** and completed our 2nd TDD iteration.

[**<--Back to main instructions**](../readme.md)