# Installation of IDM Client

Last updated: 08.24.2020

## Purpose

The purpose of this document is to teach the reader how to use
Ansible and Ansible Molecule to come up with a working installation
of RedHat IDM (FreeIPA) Client.

## Prerequisites

### Create your Python Virtual Environment

Follow the instructions in [part1](../part1-setup-environment) to
create your virtual environment.

### Setup your AWS Environment

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
1. mkdir **part5-register-idm-client**
1. Copy the "requirements" file down for your virtual environment
1. Open up a terminal
1. Activate your virtual environment
1. Install the required AWS software needed to interact with AWS:
   
    ```pip install -r requirements```

1. Create the **idm-client-install** ansible role using the following command:

    ```shell script
       molecule init role -d delegated idm-client-install
    ```
1. cd idm-client-install
1. cd defaults
1. Add the following variables to the **main.yml** file.

    ```yaml
    idm_domain_name: example2020.com
    idm_fqdn: "idm.{{ idm_domain_name }}"
    aws_vpc_name: "aws_openshift_vpc"
    aws_subnet_name: "aws_subnet"
    aws_security_group: "aws_openshift_vpc_security_group"
    aws_region: "{{ lookup('env', 'AWS_REGION') }}"
    aws_access_key: "{{ lookup('env', 'AWS_ACCESS_KEY_ID') }}"
    aws_secret_key: "{{ lookup('env', 'AWS_SECRET_ACCESS_KEY') }}"
    aws_idm_client_instances:
      - name: "idm-client"
        user: "centos"
        key_pair: "my_keypair"
        aws_ami: "ami-00594b9c138e6303d"
        root_volume_size: 30
        port: 22
    ```
1. cd ..
1. Make the file "vault_secret".  This file will be used to 
   store your vault password.
1. Open up "vault_secret" and enter your password for ansible vault.
1. Run the following command to encrypt your **idm server password**.

      ``` 
      ansible-vault encrypt_string "[your_idm_server_password here]" --vault-password-file ./vault_secret
      ```
1. Copy the output from **!vault** to the last line before **Encryption successful**.
1. cd defaults
1. Open up the main.yml file.
1. Add the variable "idm_admin_password", and the paste the copy encrypted password
   as the value.
1. Save the file.
1. cd files
1. mkdir private_keys
1. cd private_keys
1. Copy your aws private key to this folder and rename the file "my_keypair"
1. cd ../../molecule/default/
1. cd vars
1. Create the file **main.yml** and add the following contents:

    ```yaml
    
    ```
1. Delete the current **create.yml** file.
1. Create the file **create.yml**.
1. Add the following to the **create.yml** file

    ```yaml
 
    ```
         

:construction: