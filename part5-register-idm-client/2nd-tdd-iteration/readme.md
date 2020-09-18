# 2nd TDD Iteration -->  firewalld

Last updated: 09.18.2020

## Purpose

The purpose of this iteration is to add **firewalld** to the target servers.

## Procedure
1. cd idm-install/molecule/default

1. **RED** --> Test for the existence of **firewalld**.
    
    1. Add the following code to the end of **verify.yml**.
        
        ```yaml
        - name: Get Firewalld Service
          set_fact:
            firewalld_service: "{{ item.value }}"
          loop: "{{ lookup('dict', services_state.ansible_facts.services) }}"
          when: item.key == 'firewalld.service'
    
        - name: Print firewalld variable
          debug:
            var: firewalld_service
    
        - name: Fail if firewalld is not installed
          fail:
            msg: "The firewalld service is not installed"
          when: firewalld_service is not defined
    
        - name: Fail if firewalld is not started and enabled
          fail:
            msg: "Your firewalld service has a '{{ firewalld_service.state }}' state
                  and '{{ firewalld_service.status }}' status.  Your firewall must
                  be started and enabled."
          when:
            - firewalld_service.state != 'running' or firewalld_service.status != 'enabled'
        ```
           
        The tasks above checks to see if **firewalld** is in the list of
        services.
    1. cd ../..
    1. Run `molecule verify`.  The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Add **firewalld** to the ansible role.
     
    1. cd molecule/default
        
    1. Add the following tasks to the end of the **tasks/main.yml** file.
        
    ```yaml
    - name: Install Firewalld Service
      yum:
        name: firewalld
        state: present
    
    - name:  Start and enable firewalld
      service:
        name: firewalld
        state: started
        enabled: yes
    ```   
           
    The task will install **firewalld**.
        
    1. cd ../..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**
    and installs **firewalld**.
    
    1. Run `molecule verify`. The test should pass.  The test represents
    the **Green** in the **Red, Green, Refactor** iteration of TDD.

1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **verify.yml** looks a little messy.  Lets us extract the **firewalld**
        tasks out into a file and reference the file from verify.yml.
        
    1. cd molecule/default
        
    1. mkdir tasks
        
    1. cd tasks
        
    1. Create the file called **add-firewalld.yml**
    
    1. Copy the tasks from the
       **verify.yml** starting from the tasks name **Get Firewalld Service**
       to the end of the file and add them to the **add-firewalld.yml** file.
        
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

[**<--Back to main instructions**](../readme.md#2ndTDD)