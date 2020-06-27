# 1st TDD Iteration --> Add a Host Name

Last updated: 06.27.2020

## Purpose

The purpose of this iteration is to add the host name to the target servers.

## Procedure

1. cd idm-install/molecule/default

1. **RED** --> Test for the existence of the Host Name
    
    1. rm verify.yml
    
    1. Create the **verify.yml** file and add the following contents:
    
      ```yaml
       ---
       # This is an example playbook to execute Ansible tests.
       
       - name: Verify
         hosts: all
         tasks:
           - name: Run setup
             setup:
             register: output_setup
           - name: Print setup
             debug:
               var: output_setup
       
           - name: Install this only for local dev machine
             debug:
               msg: "Your hostname is correctly set to '{{ ansible_fqdn }}'."
             when: ansible_fqdn == "idm.example.com"
       
           - name: You did not set the host name
             fail:
               msg:  "Your host name is '{{ ansible_fqdn }}' and should be 'idm.example.com'"
             when: ansible_fqdn != "idm.example.com"
    
      ``` 
         
      1. cd ../..
      1. Run `molecule converge`
      1. Run `molecule verify`
    
            The test should fail.  We haven't written any
            code or configuration to name the docker instance.
            The purpose of the test in TDD is to
            first prove that a test fails without writing any
            code.
      1. Run `molecule destroy`

1. **GREEN** --> Add the host name to the **molecule.yml** file.
    1. Add the following line under the **platforms**
        **--name** attribute in the **molecule.yml** and
        save the file.
        
            hostname: idm.example.com
      1. Run `molecule converge`
      1. Run `molecule verify`
        
            Verification should
            be successful.  We added configuration to the
            **molecule.yml** to spin up the docker
            container with the fully qualified domain
            name of **idm.example.com**. We are now
            back in the **Green** state for the
            **Red, Green, Refactor** iteration of Test
            Driven Development (TDD).
      1. Run `molecule destroy`
      
1. **REFACTOR** --> Does any of the code or configuration need refactoring?

    Currently, we don't seem to have any code that needs to be **Refactored**.

We have completed the addition of the **host name** and our TDD iteration.

[**<--Back to main instructions**](../readme.md#1stTDD)