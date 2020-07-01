# Installation of IDM on AWS

Last updated: 07.01.2020

## Purpose

The purpose of this document is to teach the reader how to use
Ansible and Ansible Molecule to come up with a working installation
of RedHat IDM (FreeIPA) on AWS.

## Procedure

1. Activate your virtual environment created in
[part1](../part1-setup-environment).

1. Open up a terminal window.

1. mkdir **part2-install-idm**

1. Copy the **ansible.cfg** down from the git repo under the
folder **part2-install-idm**.

1. Set the path to the **ansible.cfg** by setting the environment variable:

    `ANSIBLE_CONFIG=$(pwd)/ansible.cfg`

1. Copy the **Dockerfile** down from the git repo under the
folder **part2-install-idm**  

1. cd part2-install-idm

1. Add **ipv6** support to Docker by editing your **/etc/docker/daemon.json** file
and add the following content:

    ```json
    { "ipv6": true, "fixed-cidr-v6": "2001:db8:1::/64"}
    ```
1. Run `sudo systemctl restart docker` to allow for new **ipv6** setting.
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

1. <a name="1stTDD"></a> Add a **host name** using the [1st TDD Iteration](./1st-tdd-iteration).

1. cd idm-install/molecule/default/

1. Add the following contents at the end of the **verify.yml** file.

    ```yaml
        - name: collect facts about system services
          service_facts:
          register: services_state
   ``` 
   The task above gathers facts about the **services** installed
   on the image.
   
1. <a name="2ndTDD"></a> Add **firewalld** with the [2nd TDD Iteration](./2nd-tdd-iteration).

1. <a name="3rdTDD"></a> Start and enable **firewalld** with the [3rd TDD Iteration](./3rd-tdd-iteration).

1. <a name="4thTDD"></a> Open the necessary ports for IDM with the [4th TDD Iteration](./4th-tdd-iteration).

1. <a name="5thTDD"></a> Enable DNF IDM module with the [5th TDD Iteration](./5th-tdd-iteration).
  
1. <a name="6thTDD"></a> Install IDM with the [6th TDD Iteration](./6th-tdd-iteration).

1. <a name="7thTDD"></a> Configure IDM with the [7th TDD Iteration](./7th-tdd-iteration).
   

        
        
        
        
  
:construction: Under Construction.....