# Installation of Nexus on AWS

Last updated: 09.25.2020

## Purpose

The purpose of this document is to teach the reader how to use Ansible
and Ansible Molecule to create an ansible role that installs and configures
Nexus.

## Prerequisites

AWS Account and permissions to create/delete AWS EC2 instances

## Procedure
1. Open up a terminal
1. mkdir -p $HOME/.aws
1. cd $HOME/.aws
1. Make the file **.env**
1. Edit your **.env** file.  Enter the following
environment variables:

      ```yaml
       AWS_REGION="us-east-1 <this value should be different if you don't live close to the US east coast.>"
       AWS_ACCESS_KEY_ID="<your aws access key id: should be in your credentials.csv file>"
       AWS_SECRET_ACCESS_KEY="<your aws secret access key:  should be in your credentials.csv file>"
      ```
   
1. cd
1. Edit your **.bashrc** file.  Add the following line:  

    `source $HOME/.aws/.env`

1. Save your **.bashrc** file and close your terminal window.

Now your AWS account credentials can be accessed by your
Python virtual environment and Ansible Molecule.


## Procedure

1. Open up a terminal window.
1. mkdir **part6-install-nexus**
1. cd **part6-install-nexus**
1. Copy the "requirements" file down for your virtual environment
1. Open up a terminal
1. Activate your virtual environment
1. Install the required AWS software needed to interact with AWS:
   
    ```pip install -r requirements```

1. Create the **nexus-instance** ansible role using the following command:

    ```shell script
     molecule init role -d delegated nexus-instance
    ```
1. cd nexus-instance
1. cd defaults
1. Add the following variables to the **main.yml** file

    ```yaml
    host_name: nexus-server
    fqdn: "{{host_name}}".example.com
    ```

1. cd ../molecule/default
1. Edit the **converge.yml** and add `become: true` before the
      **tasks:** keyword.

1. Change the following in your **molecule.yml**.

    1. Change the **platform[0].name** to be the name of your
       ec2 instance.  We are going to call our EC2 instance
       **nexus-server**.  Notice that **platform** is a list and
       allows you to work with more than one EC2 instance.
    
    1. Add the following section in replace of your **provisioner**
       section:
       
        ```yaml
        provisioner:
          name: ansible
          config_options:
            defaults:
              remote_user: centos
            privileged_escalation:
              become: true
              become_ask_pass: false     
        ```
        Let's explain this section a little more.
        
          1. **name** = The name of the provisioner.  This is the
          default value as there is only one provisioner.
          
          1. **config_options** = The section that allows us to update
          the **ansible.cfg** that molecule generates in the **molecule
          ephemeral** directory.  The **ephemeral** directory is created
          every time you run **molecule create** and gets destroyed when
          you call **molecule destroy**.  Molecule takes its configuration
          from this directory when it runs.
          
          1. **defaults** = This represents the **defaults** section of the
          **ansible.cfg**.  You can set typical variables in the **ansible.cfg**
          here.
          
          1. **remote_user** = The user that ansible uses to login via ssh.
          
          1. **privileged_escalation** = The section that corresponds to 
          the section in the **ansible.cfg**.
          
          1. **become** = States that any playbook run with molecule
          can escalate to **root** privileges if a task needs the permissions.
          
          1. **become_ask_pass** = Tells ansible not to prompt for the
          password when running a task which requires the escalated
          privileges.
          
          1. You can perform QA on this section of the **molecule.yml** 
          by taking a look at the finished **molecule.yml** 
          in the **molecule_artifacts** directory.  
          
    1. At the bottom of the **molecule.yml** file add the following test sequence:
        
        ```yaml
        scenario:
          test_sequence:
            - dependency
            - lint
            - cleanup
            - destroy
            - syntax
            - create
            - prepare
            - converge
            - side_effect
            - verify
            - cleanup
            - destroy
        ```      

:construction: Under Construction.....