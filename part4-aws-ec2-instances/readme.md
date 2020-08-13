# Create or Destroy EC2 Instances on AWS

Last updated: 08.13.2020

## Purpose

The purpose of this document is to teach the reader how to use Ansible
and Ansible Molecule to create an ansible role that creates or destroys
EC2 instances.

## Prerequisites

### Create your AWS Infrastructure

Follow the instructions in [part3](../part3-install-aws-infrastructure) to
create your AWS Infrastructure.

## Procedure

1. Open up a terminal window.

1. Make sure you **source** your virtual environment

1. mkdir **part4-aws-ec2-instances**

1. cd part4-aws-ec2-instances

1. Create the Ansible Molecule role called **aws-ec2-instance**

    1. Run `molecule init role --driver-name docker aws-ec2-instance`
    1. Run `tree aws-ec2-instance`
    
1. cd aws-ec2-instance/molecule/default

1. rm molecule.yml

1. Create **molecule.yml** and add the following contents:

    ```yaml
        ---
        dependency:
          name: galaxy
        driver:
          name: docker
        platforms:
          - name: aws-ec2-instance
            image: part3-install-aws-infrastructure
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

:construction: Under Construction.....