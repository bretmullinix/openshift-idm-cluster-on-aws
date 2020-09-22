# 5th TDD Iteration -->  Configure IDM client on the target server

Last updated: 09.21.2020

## Purpose

The purpose of this iteration is to configure the IDM client on the target server.

## Procedure
1. cd idm-install/molecule/default

1. **RED** --> Test to see if the IDM client is configured.
    
    1. Add the following code to the end of **verify.yml**.
        
        ```yaml
        - name: Determine if IDM DNS server is working
          command: 'dig +short {{ idm_fqdn }} A'
          register: dig_result
        
        - name: Fail if we can't resolve the IDM server
          fail:
            msg: "Can't resolve the IDM Server."
          when:
            - dig_result is not defined or
              dig_result.stdout_lines is not defined or
              dig_result.stdout_lines | length == 0 or
              dig_result.stdout_lines[0] != idm_server_ip_address
        
        
        - name: Make sure we have registered IDM as Kerberos server.
          command: 'egrep  "^\s*kdc\s=\s{{idm_fqdn}}" /etc/krb5.conf'
          register: kdc_results
        
        - name: Print KDC Results
          debug:
            var: kdc_results
        
        - name: Fail if IDM is not a Kerberos Server
          fail:
            msg: "IDM is not a Kerberos Server.  Something went wrong in registering the server as an IDM client."
          when:
            - kdc_results is not defined or
              kdc_results.stdout_lines is not defined or
              kdc_results.stdout_lines | length == 0 or
              idm_fqdn not in kdc_results.stdout_lines[0]
        ```
           
        The tasks above checks to see if the IDM client is configured.
        
    1. cd ../..
    1. Run `molecule verify`.  The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Add the tasks to configure the IDM client.
     
    1. cd molecule/default
        
    1. Add the following tasks to the end of the **tasks/main.yml** file.
        
        ```yaml
        - name: Set the host name
          hostname:
            name: "{{idm_client_hostname + '.' + idm_domain_name }}"
        
        - name: Insert the IPA Server Host Name into the /etc/hosts
          blockinfile:
            path: /etc/hosts
            block: "{{ idm_server_ip_address + ' ' + idm_fqdn }}"
        
        - name: Test to see if we registered as an IDM client already
          command: 'egrep  "^\s*kdc\s=\s{{idm_fqdn}}" /etc/krb5.conf'
          ignore_errors: true
          register: kdc_results
        
        - name: Run the FreeIPA client installer
          command: "{{ freeipa_client_install_base_command }} {{ freeipa_client_install_options | join(' ') }}"
          args:
            creates: /etc/ipa/default.conf
          when:
            - kdc_results is defined
            - kdc_results.stdout_lines is defined
            - kdc_results.stdout_lines | length == 0
        
        - name: Make sure we remove the IDM server from the /etc/hosts
          lineinfile:
            path: /etc/hosts
            state: absent
            regexp: '^{{idm_server_ip_address}}'
        ```   
           
        The task will configure the IDM client on the server.
        
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
        
    1. Create the file called **verify-idm-server-connectivity.yml**
    
    1. Copy the tasks from the **verify.yml** starting from the tasks name 
       **Determine if IDM DNS server is working** to the end of the file and add 
       them to the **verify-idm-server-connectivity.yml** file.
        
    1. cd ..
        
    1. Remove the tasks that checks for the configuration of IDM client in the **verify.yml**.
        
    1. Add the following to the end of **verify.yml**.
        
        ```yaml
          - name: Determine if we have IDM Server Connectivity
            include_tasks: tasks/verify-idm-server-connectivity.yml
       ```          
           
    1. cd ../..
    1. The **tasks/main.yml** file could be a little cleaner by removing the 
       IDM client configuration tasks and putting them into a separate file.
    
    1. cd tasks
    
    1. mkdir main
    
    1. cd main
    
    1. Create the **make-server-idm-client.yml**   
    
    1. cd ..
    
    1. Copy the tasks titled **Set the host name** in the
       **tasks/main.yml** file to the end of the file.
       
    1. Place the copied tasks in the file **make-server-idm-client.yml**
    
    1. Remove the tasks starting from the task titled **Set the host name**
       in the **tasks/main.yml** file to the end of the file.
       
    1. Reference the task file in the **tasks/main.yml** as is shown below.
       
        ```yaml
        - name:  Make server an IDM Client
          include_tasks: "{{ role_path }}/tasks/main/make-server-idm-client.yml"
        ```
       
   1. Run `molecule test`.  The test should pass.  Your refactoring is complete.

We have configured the IDM client and completed our 5th TDD iteration.

[**<--Back to main instructions**](../readme.md#5thTDD)