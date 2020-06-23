# Installation of IDM on AWS

Last updated: 06.23.2020

## Purpose

The purpose of this document is to teach the reader how to use
Ansible and Ansible Molecule to come up with a working installation
of RedHat IDM (FreeIPA) on AWS.

## Procedure
1. Activate your virtual environment created in
[part1](../part1-setup-environment).
  
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
            image: centos:8
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
     1. Create the **prepare.yml** and add the following
     contents:
     
         ```yaml
         ---
         - name: Prepare
           hosts: all
           gather_facts: false
           tasks:
             - name: Install python for Ansible
               yum:
                 name: "{{ item }}"
                 use_backend: "dnf"
               with_items:
                 - python3
                 - python3-pip
             - name: Install Ansible
               command: "pip3 install ansible==2.9"
         ```
         The **prepare.yml** will install python3 and 
         ansible before running the **tasks/main.yml**.    


:construction: Under Construction.....