# 7th TDD Iteration --> Configure RedHat IDM

Last updated: 07.04.2020

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
        
        ```
           
        The tasks above checks to see if the IDM is configured.
        
    1. cd ../..
    1. Run `molecule verify`.  The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Add the task to configure IDM.
     
    1. Add the following task to the end of the **tasks/main.yml** file.
    
        ```yaml
        - name: Configure IDM.  Please wait this could take a couple of minutes....
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
    and installs IDM.  This task will take 5-10 minutes to install.
    
    1. Run `molecule verify`. The test should pass.  The test represents
    the **Green** in the **Red, Green, Refactor** iteration of TDD.

1. **REFACTOR** --> Does any of the code need **Refactoring**?
         
    1. We look at the role files and determine that no refactoring is needed.
    We have completed our refactoring.
 
We have configured RedHat IDM in our 7th TDD iteration.

[**<--Back to main instructions**](../readme.md#7thTDD)