# 3rd TDD Iteration -->  Open Nexus Client Ports

Last updated: 09.30.2020

## Purpose

The purpose of this iteration is to open Nexus client ports on the target servers.

## Procedure
1. cd nexus-instance/molecule/default

1. **RED** --> Test to see if the Nexus ports are open using **firewalld**.
    
    1. Add the following code to the end of **verify.yml**.
        
        ```yaml
        - name: Register variable for open ports
          command:  firewall-cmd --list-ports
          register: open_ports
    
        - name: Fail if an Nexus Port is Closed
          fail:
            msg: "The port '{{ item }}' is not open."
          with_items: "{{ open_nexus_ports }}"
          when: "'{{ item }}' not in open_ports.stdout"
        ```
           
        The tasks above checks to see if Nexus server ports are open
        in **firewalld**.
    1. cd ../..
    1. Run `molecule verify`.  The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Add the tasks to open the Nexus server ports to the ansible role.
     
    1. cd molecule/default
        
    1. Add the following tasks to the end of the **tasks/main.yml** file.
        
    ```yaml
    - name: Open Ports for Nexus
      firewalld:
        port: "{{ item }}"
        permanent: true
        immediate: true
        state: enabled
      with_items: "{{ open_nexus_ports }}"
    ```   
           
    The task will open the Nexus server ports using **firewalld**.
        
    1. cd ../..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**
    and the Nexus server ports are open using **firewalld**.
    
    1. Run `molecule verify`. The test should pass.  The test represents
    the **Green** in the **Red, Green, Refactor** iteration of TDD.

1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **verify.yml** looks a little messy.  Let us extract the
       tasks, that check if the ports are open, out into a file and reference 
       the file from verify.yml.
        
    1. cd molecule/default
        
    1. mkdir tasks
        
    1. cd tasks
        
    1. Create the file called **open-ports-with-firewalld.yml**
    
    1. Copy the tasks from the **verify.yml** starting from the tasks name 
       **Register variable for open ports** to the end of the file and add 
       them to the **open-ports-with-firewalld.yml** file.
        
    1. cd ..
        
    1. Remove the tasks that check for the open ports in the **verify.yml**.
        
    1. Add the following to the end of **verify.yml**.
        
        ```yaml
          - name:  Determine if firewall ports are open
            include_tasks: tasks/open-ports-with-firewalld.yml
       ```          
           
    1. cd ../..
    1. Run `molecule test`.  The test should pass.  Your refactoring is complete.

We have opened the Nexus server ports and completed our 3rd TDD iteration.

[**<--Back to main instructions**](../readme.md#3rdTDD)