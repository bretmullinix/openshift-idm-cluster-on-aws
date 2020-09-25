# Installation of Nexus on AWS

Last updated: 09.25.2020

## Purpose

The purpose of this document is to teach the reader how to use Ansible
and Ansible Molecule to create an ansible role that installs and configures
Nexus.

## Prerequisites

Docker

## Procedure
1. Open up a terminal window.

1. Make sure you **source** your virtual environment

1. mkdir **part6-install-nexus**

1. cd part6-install-nexus
  
1. Run `docker build -t part6-install-nexus .`

   The command above will create a docker image
   on your machine called **part6-install-nexus**.
   The image ensures that python3, pip3, boto, boto3 and ansible 2.9
   are installed.  We installed **ansible** on the image
   because the image will be used by **molecule**, and
   molecule requires ansible to run tests.  The Amazon ansible modules
   require the  **boto** and **boto3** packages.

1. Create the Ansible Molecule role called **nexus-instance**

    1. Run `molecule init role --driver-name docker nexus-instance`
    1. Run `tree nexus-instance`
    
1. cd nexus-instance/molecule/default

1. rm molecule.yml

1. Create **molecule.yml** and add the following contents:

    ```yaml
        ---
        dependency:
          name: galaxy
        driver:
          name: docker
        platforms:
          - name: nexus-instance
            image: part6-install-nexus
            pre_build_image: true
        provisioner:
          name: ansible
          log: true
        verifier:
          name: ansible
          options:
            v: 4
        scenario:
          name: default
          test_sequence:
            - create
            - prepare
            - converge
            - verify
            - destroy
    ```

1. Add the following variables to the **default/main.yml**.
 
     ```yaml
     ---
     aws_region: "{{ lookup('env', 'AWS_REGION') }}"
     aws_access_key: "{{ lookup('env', 'AWS_ACCESS_KEY_ID') }}"
     aws_secret_key: "{{ lookup('env', 'AWS_SECRET_ACCESS_KEY') }}"
     ```
 
:construction: Under Construction.....