# 3rd TDD Iteration --> Add the AWS VPC Gateway

Last updated: 08.12.2020

## Purpose

The purpose of this iteration is to add the AWS VPC Gateway to the AWS environment.

## Procedure

1. Open a terminal
2. Activate your virtual environment
1. cd aws-infrastructure-install/molecule/default


1. **RED** --> Test for the existence of the VPC subnet
    
    1. Edit the **verify.yml** file.
    
    1. Add the following contents to the end of the **verify.yml** file:
    
      ```yaml

       - name: Gather facts on the AWS Control Subnet
         ec2_vpc_igw_info:
           aws_access_key: "{{ aws_access_key }}"
           aws_secret_key: "{{ aws_secret_key }}"
           region: "{{ aws_region }}"
           filters:
                "tag:Name": "{{ aws_infrastructure_install_vpc.gatway }}"
         register: gateway_info


       - name: Print the vpc info
         debug:
           var: gateway_info

       - name: Fail if the gateway does not exist
         fail:
           msg:  "The gateway called '{{ aws_infrastructure_install_vpc.gateway  }}' does not exist."
         when:
           - gateway_info.internet_gateways is defined
           - gateway_info.internet_gateways | length  == 0

 
      ``` 
         
      1. cd ../..
      1. Run `molecule converge`
      1. Run `molecule verify`
    
            The test should fail.  We haven't written any
            code to create the AWS vpc gateway.
            The purpose of the test in TDD is to
            first prove that a test fails without writing any
            code.
      1. Run `molecule destroy`

1. **GREEN** --> Add the task to create the vpc gateway to the **tasks/main.yml** file.
    1. Add the following task to the end of th **tasks/main.yml** file.
        
        ```yaml
          - name: create ec2 vpc internet gateway
          # create an internet gateway for the vpc
            ec2_vpc_igw:
              vpc_id: "{{ vpc_facts.id }}"
              state: present
              aws_access_key: "{{ aws_access_key }}"
              aws_secret_key: "{{ aws_secret_key }}"
              region: "{{ aws_region }}"
              tags:
                Name: "{{ aws_infrastructure_install_vpc.gateway }}"
            register: igw
        ```
            
      1. Run `molecule converge`
      1. Run `molecule verify`
        
            Verification should be successful.  We added the AWS vpc subnet tasks to
            create the vpc gateway in the
            **tasks/main.yml** file.  We are now
            back in the **Green** state for the
            **Red, Green, Refactor** iteration of Test
            Driven Development (TDD).
      1. Run `molecule destroy`
      
1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **verify.yml** looks a little messy.  Let's extract the new **vpc subnet**
        tasks into a file and reference the file from verify.yml.
    1. cd molecule/default/tasks
    1. Create the file called **check-for-vpc-gateway-existence.yml**.
    1. Remove the tasks starting with the task **Gather facts on the AWS VPC Gateway**
    and add them to the **check-for-vpc-gateway-existence.yml** file.
    1. Add the following task to include the new task file in the **verify.yml* file.
    
          ```yaml
            - name:  Determine if vpc exists
              include_tasks: tasks/check-for-vpc-gateway-existence.yml
         ``` 
    
    1. cd ../..
    1. Run `molecule test`.  The test should pass.

We have tested and added the Amazon VPC Gateway and completed our 3rd TDD iteration.

[**<--Back to main instructions**](../readme.md#3rdTDD)