# 3rd TDD Iteration --> Start and Enable firewalld

Last updated: 06.27.2020

## Purpose

The purpose of this iteration is to start and enable **firewalld** on the target servers.

## Procedure
1. cd idm-install/molecule/default

1. **RED** --> Test to see if **firewalld** is started.
    
    1. Add the following code to the end of **verify.yml**.
        
        ```yaml
           - name:  Determine if firewalld is started
             set_fact:
               firewall_service_started: true
             loop: "{{ lookup('dict', services_state.ansible_facts.services) }}"
             when: "'firewalld.service' in item.key and item.value.state == 'running'"
       
           - name: Pass if firewalld service is started
             debug:
               msg: "Firewalld is started!!!"
             when: firewall_service_started is defined
       
           - name: Fail if firewalld service is not started
             fail:
               msg: "The firewalld service is not started"
             when: firewall_service_started is not defined
       
           - name:  Determine if firewalld is enabled
             set_fact:
               firewall_service_enabled: true
             loop: "{{ lookup('dict', services_state.ansible_facts.services) }}"
             when: "'firewalld.service' in item.key and item.value.status == 'enabled'"
       
           - name: Pass if firewalld service is enabled
             debug:
               msg: "Firewalld is enabled!!!"
             when: firewall_service_enabled is defined
       
           - name: Fail if firewalld service is not enabled
             fail:
               msg: "The firewalld service is not enabled"
             when: firewall_service_enabled is not defined
        ```
           
        The tasks above checks to see if **firewalld** is started and enabled.
        
    1. cd ../..
    1. Run `molecule verify`.  The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **Green** --> Add the tasks to start and enable **firewalld** to the ansible role.
     
    1. cd molecule/default
        
    1. Add the following tasks to the end of the **tasks/main.yml** file.
        
    ```yaml
      - name: Start Firewalld Service
        service:
          name: firewalld
          state: started
          enabled: yes
    ```   
           
    The task will start and enable **firewalld**.
        
    1. cd ../..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**
    and installs **firewalld**.
    
    1. Run `molecule verify`. The test should pass.  The test represents
    the **Green** in the **Red, Green, Refactor** iteration of TDD.

1. **Refactor** --> Does any of the code need **Refactoring**?

    1. The **verify.yml** looks a little messy.  Lets us extract the new **firewalld**
        tasks into a file and reference the file from verify.yml.
        
    1. cd molecule/default/tasks
        
    1. Create the file called **start-and-enable-firewalld.yml** and add the following content:
        
        ```yaml
         - name:  Determine if firewalld is started
           set_fact:
             firewall_service_started: true
           loop: "{{ lookup('dict', services_state.ansible_facts.services) }}"
           when: "'firewalld.service' in item.key and item.value.state == 'running'"
     
         - name: Pass if firewalld service is started
           debug:
             msg: "Firewalld is started!!!"
           when: firewall_service_started is defined
     
         - name: Fail if firewalld service is not started
           fail:
             msg: "The firewalld service is not started"
           when: firewall_service_started is not defined
     
         - name:  Determine if firewalld is enabled
           set_fact:
             firewall_service_enabled: true
           loop: "{{ lookup('dict', services_state.ansible_facts.services) }}"
           when: "'firewalld.service' in item.key and item.value.status == 'enabled'"
     
         - name: Pass if firewalld service is enabled
           debug:
             msg: "Firewalld is enabled!!!"
           when: firewall_service_enabled is defined
     
         - name: Fail if firewalld service is not enabled
           fail:
             msg: "The firewalld service is not enabled"
           when: firewall_service_enabled is not defined
    
       ```
        
    1. cd ..
        
    1. Remove the firewalld tasks above from the **verify.yml**.
        
    1. Add the following to the end of **verify.yml**.
        
        ```yaml
          - name:  Determine if firewalld exists
            include_tasks: tasks/start-and-enable-firewalld.yml
       ```          
           
    1. cd ../..
    1. Run `molecule verify`.  The test should pass.
    
    We have one more refactoring to do.  When you ran **molecule verify**,
    we were looping through the services many times to get boolean statuses.
    This is inefficient.  Lets capture the firewalld service information in a
    variable and reference it when we populate the variables.
    
    1. Add the following content to the **verify.yml** file after the task titled
    **collect facts about system services**.
    
        ```yaml
          - name:  Get firewall service information
            set_fact:
              firewall_service: "{{ item.value }}"
            loop: "{{ lookup('dict', services_state.ansible_facts.services) }}"
            when: "'firewalld.service' in item.key"
       ```
       
       We look for the firewall service information here.  This is the only loop
       needed to determine if the firewall is installed, started, and enabled.
       
    1. Remove the contents of the **add-firewall.yml** file and add the following:
    
            ```yaml
            - name: Pass if firewalld service exists
              debug:
                msg: "Firewalld exists!!!"
              when: firewall_service is defined
            
            - name: Fail if firewalld service doesn't exist
              fail:
                msg: "The firewalld servece does not exist"
              when: firewall_service is not defined
           ```
     
       We are no longer looking for the firewall service to populate a boolean variable.
       We loop once for the firewall service information in the **verify.yml**.
       
     1. Remove the contents of the **start-and-enable-firewalld.yaml** and add the
     following.
     
         ```yaml
            - name: Pass if firewalld service is started
              debug:
                msg: "Firewalld is started!!!"
              when: firewall_service.state == 'running'
            
            - name: Fail if firewalld service is not started
              fail:
                msg: "The firewalld service is not started"
              when: firewall_service.state != 'running'
            
            - name: Pass if firewalld service is enabled
              debug:
                msg: "Firewalld is enabled!!!"
              when: firewall_service.status == 'enabled'
            
            - name: Fail if firewalld service is not enabled
              fail:
                msg: "The firewalld service is not enabled"
              when: firewall_service.status != 'enabled'
        ```
    
        We have removed two loops that populated the firewall started and
        firewall enabled boolean variables, and we add readability
        by explicitly showing that were checking for the firewall service is running
        and enabled in the **when** conditions.
     1. We take another look at our code and our refactoring is complete.

We have started and enabled **firewalld** and completed our 3rd TDD iteration.

[**<--Back to main instructions**](../readme.md#3rdTDD)