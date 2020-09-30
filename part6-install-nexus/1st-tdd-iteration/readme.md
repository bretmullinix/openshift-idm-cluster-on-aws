# 1st TDD Iteration --> Install the required yum packages

Last updated: 09.30.2020

## Purpose

The purpose of this iteration is to install the required yum packages 
on the target servers.

## Procedure
1. cd idm-install/molecule/default
1. Edit **verify.yml** and add the following tasks.

    ```yaml
    - name: Include the module vars file.
      include_vars:
        file: ../../defaults/main.yml
    ```

1. **RED** --> Test for the existence of the yum packages
    
    1. Replace the contents of the **verify.yml** with the code below.
        
        ```yaml
           - name: Verify
             hosts: all
             become: true
             become_method: sudo
             tasks:
                - name: Include the module vars file.
                  include_vars:
                    file: ../../defaults/main.yml
       
                - name: yum_command
                  yum:
                    list=installed
                  register: yum_packages
                
                - name: Initialize variable to list packages that are installed
                  set_fact:
                    installed_packages: "{{ [] }}"
                
                - name: Populate installed packages
                  set_fact:
                    installed_packages: "{{ installed_packages + [item.name] }}"
                  with_items: "{{ yum_packages.results }}"
                  when:
                    - yum_packages is defined
                    - yum_packages.results is defined
                    - yum_packages.results | length > 0
                
                - name: Fail if package is not installed
                  fail:
                    msg:  "The {{ item.name }} is not installed."
                  with_items: "{{ yum_installs }}"
                  when: item.install_name not in installed_packages
        ```
                  
        The tasks above checks to see if the yum packages are in the list of
        installed packages.

    1. cd ../..
    1. Run `molecule verify`.  The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Add the tasks to install the yum packages to the ansible role.
     
    1. cd molecule/default
        
    1. Add the following tasks to the end of the **tasks/main.yml** file.
        
    ```yaml
    - name: Install the Required Libraries
      yum:
        name: "{{ item.name }}"
        state: present
        use_backend: "{{ yum_backend }}"
      with_items: "{{ yum_installs }}"
    ```   
           
    The task will install the yum packages.
        
    1. cd ../..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**
    and installs the required packages.
    
    1. Run `molecule verify`. The test should pass.  The test represents
    the **Green** in the **Red, Green, Refactor** iteration of TDD.

1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **verify.yml** looks a little messy.  Lets us extract the 
        tasks needed to install the yum packages out into a file and
       reference the file from verify.yml.
        
    1. cd molecule/default
        
    1. mkdir tasks
        
    1. cd tasks
    
    1. Create the file called **check-if-yum-packages-are-installed.yml** 
       and add the following content:
        
        ```yaml
           - name: yum_command
             yum:
               list=installed
             register: yum_packages
       
           - name: Initialize variable to list packages that are installed
             set_fact:
               installed_packages: "{{ [] }}"
       
           - name: Populate installed packages
             set_fact:
               installed_packages: "{{ installed_packages + [item.name] }}"
             with_items: "{{ yum_packages.results }}"
             when:
               - yum_packages is defined
               - yum_packages.results is defined
               - yum_packages.results | length > 0
       
           - name: Print the new variable
             debug:
               var: installed_packages
       
           - name: Fail if package is not installed
             fail:
               msg:  "The {{ item }} is not installed."
             with_items: "{{ yum_installs }}"
             when: item not in installed_packages
       ```
        
    1. cd ..
        
    1. Remove the tasks starting from the task named **yum_command** to the
       end of the **verify.yml** file.
        
    1. Add the following to the end of **verify.yml**.
        
        ```yaml
          - name:  Determine if yum packages exist
            include_tasks: tasks/check-if-yum-packages-are-installed.yml
       ```          
           
    1. cd ../..
    1. Run `molecule test`.  The test should pass.  Your refactoring is complete.

We have added the necessary yum packages and completed our 1st TDD iteration.

[**<--Back to main instructions**](../readme.md#1stTDD)