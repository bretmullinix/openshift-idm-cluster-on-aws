# 7th TDD Iteration --> Configure RedHat IDM

Last updated: 07.06.2020

## Purpose

The purpose of this iteration is to configure IDM on the target servers.

## Procedure
1. cd idm-install
1. Make the file **vault_secret**
1. Edit your **vault_secret** and add your ansible vault password.
1. Run the following after replacing \~idm-admin-password\~ with your idm admin password.
 
    ```
     ansible-vault  encrypt_string --vault-password-file vault_secret '~idm-admin-password~' --name idm_admin_password > encrypted_admin_password.txt
    ```
    
    When prompted, enter the vault password you added to the **vault_secret** file.
    The output should be the **encrypted_admin_password.txt** file.  The file contains
    the **idm_admin_password** variable for the **idm-install/defaults/main.yml** file.
    The variable will be used for the IDM **admin** password.
    
1. cd defaults
1. Edit the file **main.yml** and add the following variables:

    ```yaml
      idm_domain_name: example.com
      idm_fqdn: "idm.{{ idm_domain_name }}"
   ```

1. Whatever you set your **idm_fqdn** name to, make sure you update the 
**hostname** in your **molecule.yml** file to be the same, or
your IDM server will not work in the docker container. 

1. Copy the **idm_admin_password** in the **../encrypted_admin_password.txt**
to the **main.yml** file.  

1. cd idm-install/molecule/default

1. Edit your **molecule.yml** and replace your **provisioner** section
with the following section:
   
    ```yaml
     provisioner:
       name: ansible
       log: true
       config_options:
         defaults:
           vault_password_file: ${MOLECULE_PROJECT_DIRECTORY}/vault_secret
     ```

1. **RED** --> Test to see if IDM is configured.
    
    1. Add the following code to the end of **verify.yml**.
        
        ```yaml
            - name: Get the IDM Servers IP Address
              shell:
                cmd: >
                  dig +short {{ ansible_fqdn }} A
              register: output_dig_server_ip_address
                
            - name: Check to make sure IDM is configured for DNS
              fail:
                msg: "IDM DNS is not configured.  No IP Address is returned when a DIG is performed."
              when: output_dig_server_ip_address["stdout"] == ""
        
            - name: Check to make sure IDM is a server registered with itself
              ipa_host:
                name: "{{ ansible_fqdn }}"
                state: present
                ipa_host: "{{ ansible_fqdn }}"
                ipa_user: admin
                ipa_pass: "{{  idm_admin_password }}"
        ```
           
        The tasks above checks to see if the IDM is configured.
        
    1. cd ../..
    1. Run `molecule verify`.  The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Add the task to configure IDM.
     
    1. Add the following task to the end of the **tasks/main.yml** file.
    
        ```yaml
        - name: Configure IDM.  Please wait this could take 15-30 minutes....
          shell:
            cmd: >
             ipa-server-install  --mkhomedir 
                --setup-dns --no-forwarders 
                -a '{{ idm_admin_password }}' 
                -r {{ idm_domain_name | upper }} -p '{{ idm_admin_password }}' 
                -n {{ idm_domain_name }} -U
       ```

         The task will configure the IDM server.
   
    1. cd ../..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**
    and installs IDM.  This task will take 15-30 minutes to install.
    
    1. Run `molecule verify`. The test should pass.  The test represents
    the **Green** in the **Red, Green, Refactor** iteration of TDD.

1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **verify.yml** looks a 
    little messy with all the tasks checking for the
    configuration of IDM.  Let's move the tasks to a separate file.
    
        1. Create the file **molecule/default/tasks/check-if-idm-is-configured.yml**  
        1. Edit the file and add the following content:
        
            ```yaml
           - name: Get the IDM Servers IP Address
             shell:
               cmd: >
                 dig +short {{ ansible_fqdn }} A
             register: output_dig_server_ip_address
           
           
           - name: Check to make sure IDM is configured for DNS
             fail:
               msg: "IDM DNS is not configured.  No IP Address is returned when a DIG is performed."
             when: output_dig_server_ip_address["stdout"] == ""
           
           - name: Check to make sure IDM is a server registered with itself
             ipa_host:
               name: "{{ ansible_fqdn }}"
               state: present
               ipa_host: "{{ ansible_fqdn }}"
               ipa_user: admin
               ipa_pass: "{{  idm_admin_password }}"
            ```
        1. In the **molecule/default/verify.yml**, remove the content above from the
        file.
        1. In the **molecule/default/verify.yml**, add the following content to the end:
        
            ```yaml
                 - name: Check to see if IDM is configured
                   include_tasks: tasks/check-if-idm-is-configured.yml
           ```
        
        1. Run `molecule test` (the whole process can take 30-45 minutes) 
        to ensure the role works as intended.
         
    1. We look at the role files and determine that no other refactoring is needed.
    We have completed our refactoring.
 
We have configured RedHat IDM in our 7th TDD iteration.

[**<--Back to main instructions**](../readme.md#7thTDD)