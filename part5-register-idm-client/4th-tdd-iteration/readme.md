# 4th TDD Iteration -->  Change the IDM Client DNS Server to the IDM Server

Last updated: 09.18.2020

## Purpose

The purpose of this iteration is to change the DNS server to the IDM Server on the target servers.

## Procedure
1. cd idm-install/molecule/default

1. **RED** --> Test to see if the IDM client is using the IDM server as the DNS server.
    
    1. Add the following code to the end of **verify.yml**.
        
        ```yaml
        - name: Get the DNS Servers
          shell: nmcli device show 'eth0' | grep IP4.DNS
          register: dns_servers
    
        - name: Fail if the IDM client does not list a server
          fail:
            msg: "The IDM client does not list a DNS server."
          when:
            - dns_servers.stdout_lines is not defined
            - (dns_servers.stdout_lines | length)  > 0
    
        - name: Register 1st DNS Server
          set_fact:
            first_dns_server: "{{ dns_servers.stdout_lines[0] }}"
    
        - name: Fail if the IDM Server is not listed first
          fail:
            msg: "The IDM server was not listed as the first DNS server"
          when: idm_server_ip_address not in first_dns_server
        ```
           
        The tasks above checks to see if IDM client has the IDM server
        as the first DNS server.
        
    1. cd ../..
    1. Run `molecule verify`.  The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Add the tasks to change the IDM client primary DNS server to the
   IDM server.
     
    1. cd molecule/default
        
    1. Add the following tasks to the end of the **tasks/main.yml** file.
        
        ```yaml
         - name: Change the DNS to IDM Server
           command: "{{ item }}"
           with_items:
             - nmcli conn modify "System eth0" ipv4.ignore-auto-dns yes
             - nmcli conn modify "System eth0" ipv4.dns  "{{ idm_server_ip_address }} 8.8.8.8"
        
         - name: Reboot the Server
           reboot:
             reboot_timeout: 3600
        ```   
           
        The task will change the IDM client DNS primary server to the IDM server.
        
    1. cd ../..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**,
       and the IDM client is now using the IDM server as its primary DNS server.
    
    1. Run `molecule verify`. The test should pass.  The test represents
    the **Green** in the **Red, Green, Refactor** iteration of TDD.

1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **verify.yml** looks a little messy.  Let us extract the tasks
       we added to another file and reference the fie.
        
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
           include_tasks: tasks/verify-the-dns-is-the-idm-server.yml
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
       
        ```yaml
        - name:  Change the Primary DNS Server for the IDM Client to be the IDM Server
          include_tasks: "{{ role_path }}/tasks/main/change-dns-server-to-idm-server.yml"
        ```
       
   1. Run `molecule test`.  The test should pass.  Your refactoring is complete.

We have changed the primary DNS for the IDM client to the IDM server and completed 
our 4td TDD iteration.

[**<--Back to main instructions**](../readme.md#4thTDD)