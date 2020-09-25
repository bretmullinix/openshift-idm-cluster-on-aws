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
1. Copy the "requirements" file down for your virtual environment
1. Open up a terminal
1. Activate your virtual environment
1. Install the required AWS software needed to interact with AWS:
   
    ```pip install -r requirements```

1. Create the **nexus-instance** ansible role using the following command:

    ```shell script
     molecule init role -d delegated nexus-instance
    ```
    

:construction: Under Construction.....