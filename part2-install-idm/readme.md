# Installation of IDM on AWS

Last updated: 06.23.2020

## Purpose

The purpose of this document is to teach the reader how to use
Ansible and Ansible Molecule to come up with a working installation
of RedHat IDM (FreeIPA) on AWS.

## Procedure
1. Activate your virtual environment created in
[part1](../part1-setup-environment).

1. Open up a terminal window.

1. Copy the **ansible.cfg** down from the git repo under the
folder **part2-install-idm**.

1. Set the path to the **ansible.cfg** by setting the environment variable:

    `ANSIBLE_CONFIG=$(pwd)/ansible.cfg`

1.  Run `ANSIBLE_CONFIG`

1. Copy the **Dockerfile** down from the git repo under the
folder **part2-install-idm**  

1. cd part2-install-idm

1. Run `docker build -t part2-install-idm-image .`

   The command above will create a docker image
   on your machine called **part2-install-idm-image**.
   The image ensures that python3, pip3, and ansible 2.9
   are installed.  We installed **ansible** on the image
   because the image will be used by **Molecule**, and
   Molecule requires ansible to run tests.

1. Create the Ansible Molecule role called **idm-install**

    1. Run `molecule init role --driver-name docker idm-install`
    1. Run `tree idm-install`
    
        You should get the following output:
        
        ![tree output idm role](../images/initial-idm-install-molecule-role-tree-output.png)

    1. cd idm-install/molecule/default
    1. rm molecule.yml
    1. Create **molecule.yml** and add the following contents:
    
        ```yaml
        dependency:
          name: galaxy
        driver:
          name: docker
        platforms:
          - name: instance
            image: part2-install-idm-image
            pre_build_image: true
            command: /sbin/init
            tmpfs:
              - /run
              - /tmp
            volumes:
              - /sys/fs/cgroup:/sys/fs/cgroup:ro
        provisioner:
          name: ansible
        verifier:
          name: ansible
        scenario:
          name: default
          test_sequence:
            - create
            - prepare
            - converge
            - verify
            - destroy

        ```
            
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
      1. Add the following line under the **platforms**
        **--name** attribute in the **molecule.yml** and
        save the file.
        
            hostname: idm.example.com
      1. Run `molecule converge`
      1. Run `molecule verify`.  
        
            Verification should
            be successful.  We added configuration to the
            **molecule.yml** to spin up the docker
            container with the fully qualified domain
            name of **idm.example.com**. We are now
            back in the **Green** state for the
            **Red, Green, Refactor** iteration of Test
            Driven Development (TDD).
      1.  Currently, we don't seem to have any code that needs to be **Refactored**,
          so we complete our **TDD** iteration for checking for the **fqdn**.

1. Modify the **idm-install** role to add **firewalld**.

    1. cd idm-install/molecule/default/
    1. Add the following contents at the end of the **verify.yml** file.
    
        ```yaml
            - name: collect facts about system services
              service_facts:
              register: services_state
       ``` 
       The task above gathers facts about the **services** installed
       on the image.
       
    1. Test for the existence of **firewalld**.
    
        1. Add the following code to the end of **verify.yml**.
        
            ```yaml
            - name:  Determine if firewalld exists
              set_fact:
                firewalld_service_exists: true
              loop: "{{ lookup('dict', services_state.ansible_facts.services) }}"
              when: "'firewalld.service' in item.key"
        
            - name: Pass if firewalld service exists
              debug:
                msg: "Firewalld exists!!!"
              when: firewalld_service_exists is defined
        
            - name: Fail if firewalld service doesn't exist
              fail:
                msg: "The firewalld servece does not exist"
              when: firewalld_service_exists is not defined
            ```
           
            The tasks above checks to see if **firewalld** is in the list of
            services.
        1. cd ../..
        1. Run `molecule verify`.  The test should fail.  The test represents
        the **Red** in the **Red, Green, Refactor** iteration of TDD.
        
    1.  Add **firewalld** to the ansible role.
     
        1. cd molecule/default
        
        1. Add the following tasks to the end of the **tasks/main.yml** file.
        
            ```yaml
            - name: Install Firewalld Service
              yum:
                name: firewalld
                state: present
            ```   
           
           The task will install **firewalld**.
        
        1. cd ../..
        
        1. Run `molecule converge`.  The command runs the **tasks/main.yml**
        and installs **firewalld**.
        
        1. Run `molecule verify`. The test should pass.  The test represents
        the **Green** in the **Red, Green, Refactor** iteration of TDD.
    
    1. Take a look at the **tasks/main.yml** and the **molecule/default/verify.yml**.
    Does any of the code need **Refactoring**?
    
        1. The **verify.yml** looks a little messy.  Lets us extract the **firewalld**
        tasks out into a file and reference the file from verify.yml.
        
        1. cd molecule/default
        
        1. mkdir tasks
        
        1. cd tasks
        
        1. Create the file called **add-firewalld.yml** and add the following content:
        
            ```yaml
           - name:  Determine if firewalld exists
             set_fact:
               firewalld_service_exists: true
             loop: "{{ lookup('dict', services_state.ansible_facts.services) }}"
             when: "'firewalld.service' in item.key"
           
           - name: Pass if firewalld service exists
             debug:
               msg: "Firewalld exists!!!"
             when: firewalld_service_exists is defined
           
           - name: Fail if firewalld service doesn't exist
             fail:
               msg: "The firewalld service does not exist"
             when: firewalld_service_exists is not defined
        
           ```
        
        1. cd ..
        
        1. Remove the firewalld tasks above from the **verify.yml**.
        
        1. Add the following to the end of **verify.yml**.
        
            ```yaml
              - name:  Determine if firewalld exists
                include_tasks: tasks/add-firewalld.yml
           ```          
           
        1. cd ../..
        1. Run `molecule test`.  The test should pass.  Your refactoring is complete.


        
        
        
        
  
:construction: Under Construction.....