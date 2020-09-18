# 5th TDD Iteration -->  Configure IDM client on the target server

Last updated: 09.18.2020

## Purpose

The purpose of this iteration is to configure the IDM client on the target server.

## Procedure
1. cd idm-install/molecule/default

1. **RED** --> Test to see if the IDM client is configured.
    
    1. Add the following code to the end of **verify.yml**.
        
        ```yaml

        ```
           
        The tasks above checks to see if IDM client is configured.
        
    1. cd ../..
    1. Run `molecule verify`.  The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Add the tasks to configure the IDM client.
     
    1. cd molecule/default
        
    1. Add the following tasks to the end of the **tasks/main.yml** file.
        
        ```yaml
         
        ```   
           
        The task will the IDM client on the server.
        
    1. cd ../..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**,
       and the server is configured as an IDM client.
    
    1. Run `molecule verify`. The test should pass.  The test represents
    the **Green** in the **Red, Green, Refactor** iteration of TDD.

1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **verify.yml** looks a little messy.  Let us extract the tasks
       we added to another file and reference the file.
        
    1. cd molecule/default
        
    1. mkdir tasks
        
    1. cd tasks
        
    1. Create the file called **verify-the-dns-is-the-idm-server.yml**
    
    1. Copy the tasks from the **verify.yml** starting from the tasks name 
       **Register variable for open ports** to the end of the file and add 
       them to the **verify-the-dns-is-the-idm-server.yml** file.
        
    1. cd ..
        
    1. Remove the tasks that check for the open ports in the **verify.yml**.
        
    1. Add the following to the end of **verify.yml**.
        
        ```yaml
         - name:  Determine if the IDM client is using the IDM Server as its Primary DNS Server
           include_tasks: 
       ```          
           
    1. cd ../..
    1. The **tasks/main.yml** file could be a little cleaner by removing the 
       DNS tasks and putting them into a separate file.
    
    1. cd tasks
    
    1. mkdir main
    
    1. cd main
    
    1. Create the **change-dns-server-to-idm-server.yml**   
    
    1. cd ..
    
    1. Copy the tasks titled **Change the DNS to IDM Server** in the
       **tasks/main.yml** file to the end of the file.
       
    1. Place the copied tasks in the file **change-dns-server-to-idm-server.yml**
    
    1. Remove the tasks starting from the task titled **Change the DNS to IDM Server**
       in the **tasks/main.yml** file to the end of the file.
       
    1. Reference the task file in the **tasks/main.yml** as is shown below.
       
        ```yaml
        - name:  Change the Primary DNS Server for the IDM Client to be the IDM Server
          include_tasks: "{{ role_path }}/tasks/main/change-dns-server-to-idm-server.yml"
        ```
       
   1. Run `molecule test`.  The test should pass.  Your refactoring is complete.

We have changed the primary DNS for the IDM client to the IDM server and completed 
our 4td TDD iteration.

[**<--Back to main instructions**](../readme.md#4thTDD)