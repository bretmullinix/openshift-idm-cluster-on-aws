# 4th TDD Iteration -->  Install the Nexus Software

Last updated: 10.01.2020

## Purpose

The purpose of this iteration is to install the Nexus software on the target server.

## Procedure
1. cd nexus-instance/molecule/default

1. **RED** --> Test to see if Nexus is installed.
    
    1. Add the following code to the end of **verify.yml**.
        
        ```yaml
        
        ```
           
        The tasks above checks to see if the Nexus server software is installed.
    1. cd ../..
    1. Run `molecule verify`.  The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Add the tasks to install the Nexus server.
     
    1. cd molecule/default
        
    1. Add the following tasks to the end of the **tasks/main.yml** file.
        
    ```yaml
   
    ```   
           
    The task installs the Nexus software on the target server.
        
    1. cd ../..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**,
    and the Nexus software installs.
    
    1. Run `molecule verify`. The test should pass.  The test represents
    the **Green** in the **Red, Green, Refactor** iteration of TDD.

1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **verify.yml** looks a little messy.  Let us extract the
       tasks, which check to see if the Nexus software is installed, into a file and reference 
       the file from verify.yml.
        
    1. cd molecule/default
        
    1. mkdir tasks
        
    1. cd tasks
        
    1. Create the file called **is_nexus_software_installed.yml**
    
    1. Copy the tasks from the **verify.yml** starting from the tasks name 
       **Get List of Software Installed on the Nexus Server** to the end of the file and add 
       them to the **is_nexus_software_installed.yml** file.
        
    1. cd ..
        
    1. Remove the tasks that check for the open ports in the **verify.yml**.
        
    1. Add the following to the end of **verify.yml**.
        
        ```yaml
          - name:  Determine if the Nexus Software is Installed
            include_tasks: tasks/is_nexus_software_installed.yml
       ```          
           
    1. cd ../..
    1. Run `molecule test`.  The test should pass.  Your refactoring is complete.

We have installed the Nexus software and completed our 4th TDD iteration.

[**<--Back to main instructions**](../readme.md#4thTDD)