# 4th TDD Iteration --> Open Ports for RedHat IDM

Last updated: 06.28.2020

## Purpose

The purpose of this iteration is to open ports for FreeIPA on the target servers.

## Procedure
1. cd idm-install/molecule/default

1. **RED** --> Test to see if the necessary ports are open.
    
    1. Add the following code to the end of **verify.yml**.
        
        ```yaml
        - name: Fail if an IDM Port is closed
          fail:
            msg: "The port '{{ item }}' is not open."
          with_items:
            - "80/tcp"
            - "443/tcp"
            - "389/tcp"
            - "636/tcp"
            - "88/tcp"
            - "88/udp"
            - "464/tcp"
            - "464/udp"
            - "53/tcp"
            - "53/udp"
            - "123/udp"
          when: "'{{ item }}' not in open_ports.stdout"

        ```
           
        The tasks above checks to see if the necessary ports for IDM are open.
        
    1. cd ../..
    1. Run `molecule verify`.  The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Add the task to open the ports.
     
    1. cd molecule/default
        
    1. Add the following task to the end of the **tasks/main.yml** file.
        
    ```yaml
    - name: Open Ports for IDM
      firewalld:
        port: "{{ item }}"
        permanent: true
        immediate: true
        state: enabled
      with_items:
        - "80/tcp"
        - "443/tcp"
        - "389/tcp"
        - "636/tcp"
        - "88/tcp"
        - "88/udp"
        - "464/tcp"
        - "464/udp"
        - "53/tcp"
        - "53/udp"
        - "123/udp"         
    ```   
           
    The task will open the necessary ports for IDM.
        
    1. cd ../..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**
    and opens the necessary ports.
    
    1. Run `molecule verify`. The test should pass.  The test represents
    the **Green** in the **Red, Green, Refactor** iteration of TDD.

1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **main/tasks.yml** and **verify.yml** look a 
    little messy with all the ports listed in both files.
    Let's remove the ports and use a variable instead.
    
        1. Add the following to the **vars/main.yml**
        
            ```yaml
           open_idm_ports:
             - "80/tcp"
             - "443/tcp"
             - "389/tcp"
             - "636/tcp"
             - "88/tcp"
             - "88/udp"
             - "464/tcp"
             - "464/udp"
             - "53/tcp"
             - "53/udp"
             - "123/udp"
           ```
        1. In the **tasks/main.yml**, change the task to the following:
        
            ```yaml
            - name: Open Ports for IDM
              firewalld:
                port: "{{ item }}"
                permanent: true
                immediate: true
                state: enabled
              with_items: "{{ open_idm_ports }}"
           ```
        
        1. In the **molecule/default/verify.yml**, change the task to the following:
        
            ```yaml
            - name: Fail if an IDM Port is Closed
              fail:
                msg: "The port '{{ item }}' is not open."
              with_items: "{{ open_idm_ports }}"
              when: "'{{ item }}' not in open_ports.stdout"
           ```
       
        1. In the **molecule/default/verify.yml**, make the following task the
        first task in the playbook.
        
           ```yaml
               - name: Include the module vars file.
                 include_vars:
                   file: ../../vars/main.yml
           ```  
         
           By default, molecule does not include the **vars/main.yml** in the
           **verify.yml** file.  We have to explicitly add the variables.
        
        1. Run `molecule test` to ensure the role works as intended.
         
    1. We look at the role files and determine that no other refactoring is needed.
    We have completed our refactoring.
 
We have enabled the necessary ports for RedHat IDM in our 4th TDD iteration.

[**<--Back to main instructions**](../readme.md#4thTDD)