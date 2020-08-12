# 2nd TDD Iteration --> Add the AWS 

Last updated: 08.12.2020

## Purpose

The purpose of this iteration is to add the AWS VPC Subnets to the AWS environment.

## Procedure

1. Open a terminal
2. Activate your virtual environment
1. cd aws-infrastructure-install/molecule/default

1. **RED** --> Test for the existence of the VPC subnet
    
    1. Edit the **verify.yml** file.
    
    1. Add the following contents to the end of the **verify.yml** file:
    
          ```yaml    
            - name: Gather facts on the AWS Control Subnet
              ec2_vpc_subnet_info:
                  aws_access_key: "{{ aws_access_key }}"
                  aws_secret_key: "{{ aws_secret_key }}"
                  region: "{{ aws_region }}"
                  filters:
                        "tag:Name": "{{ aws_infrastructure_install_vpc.subnets.control.name }}"
              register: vpc_control_subnet_info
            
            
            - name: Print the vpc control subnet info
              debug:
                var: vpc_control_subnet_info
            
            - name: Fail if the control subnet does not exist
              fail:
                msg:  "The subnet called '{{ aws_infrastructure_install_vpc.subnets.control.name  }}' does not exist."
              when:
                - vpc_control_subnet_info.subnets is defined
                - vpc_control_subnet_info.subnets | length  == 0
            
            - name: Gather facts on the AWS Data Subnet
              ec2_vpc_subnet_info:
                  aws_access_key: "{{ aws_access_key }}"
                  aws_secret_key: "{{ aws_secret_key }}"
                  region: "{{ aws_region }}"
                  filters:
                        "tag:Name": "{{ aws_infrastructure_install_vpc.subnets.data.name }}"
              register: vpc_data_subnet_info
            
            
            - name: Print the vpc data subnet info
              debug:
                var: vpc_data_subnet_info
            
            - name: Fail if the data subnet does not exist
              fail:
                msg:  "The subnet called '{{ aws_infrastructure_install_vpc.subnets.data.name  }}' does not exist."
              when:
                - vpc_data_subnet_info.subnets is not defined or vpc_data_subnet_info.subnets | length  == 0

          ``` 
         
      1. cd ../..
      1. Run `molecule converge`
      1. Run `molecule verify`
    
            The test should fail.  We haven't written any
            code to create the AWS vpc subnets.
            The purpose of the test in TDD is to
            first prove that a test fails without writing any
            code.
      1. Run `molecule destroy`

1. **GREEN** --> Add the task to create the vpc subnets to the **tasks/main.yml** file.
    1. Add the following task to the end of th **tasks/main.yml** file.
        
        ```yaml
        - name: Create the ec2 vpc control subnet
          # create the subnet for the vpc with a cidr block
          ec2_vpc_subnet:
            vpc_id: "{{ vpc_facts.id }}"
            state: present
            cidr: "{{ aws_infrastructure_install_vpc.subnets.control.cidr  }}"
            # enable public ip
            map_public: true
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            resource_tags:
              Name: "{{ aws_infrastructure_install_vpc.subnets.control.name  }}"
          register: control_subnet_result
        
        - name: Create the ec2 vpc data subnet
          # create the subnet for the vpc with a cidr block
          ec2_vpc_subnet:
            vpc_id: "{{ vpc_facts.id }}"
            state: present
            cidr: "{{ aws_infrastructure_install_vpc.subnets.data.cidr  }}"
            # enable public ip
            map_public: true
            aws_access_key: "{{ aws_access_key }}"
            aws_secret_key: "{{ aws_secret_key }}"
            region: "{{ aws_region }}"
            resource_tags:
              Name: "{{ aws_infrastructure_install_vpc.subnets.data.name  }}"
          register: data_subnet_result
        
        - name: Set the Control VPC Subnet Fact
          set_fact:
            vpc_control_subnet: "{{ control_subnet_result['subnet'] }}"
        
        - name: Set the Data VPC Subnet Fact
          set_fact:
            vpc_data_subnet: "{{ data_subnet_result['subnet'] }}"
        ```
            
      1. Run `molecule converge`
      1. Run `molecule verify`
        
            Verification should
            be successful.  We added the AWS vpc subnet tasks to
             create the vpc subnets in the
            **tasks/main.yml** file.  We are now
            back in the **Green** state for the
            **Red, Green, Refactor** iteration of Test
            Driven Development (TDD).
      1. Run `molecule destroy`
      
1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **verify.yml** looks a little messy.  Let's extract the new **vpc subnet**
        tasks into a file and reference the file from verify.yml.
    1. mkdir -p molecule/default/tasks
    1. cd molecule/default/tasks
    1. Create the file called **check-for-vpc-subnet-existence.yml**.
    1. Remove the tasks starting with the task **Gather facts on the AWS Control Subnet**
    and add them to the **check-for-vpc-subnet-existence.yml** file.
    1. Add the following task to include the new task file in the **verify.yml* file.
    
          ```yaml
            - name:  Determine if vpc exists
              include_tasks: tasks/check-for-subnet-existence.yml
         ``` 
    
    1. cd ../..
    1. The code still "smells" in the **tasks/main.yml**.  We should refactor the 
    subnet tasks into another task file and include it.
    1. Create the file called **create-vpc-subnets.yml**.
    1. Remove the tasks starting with the task **Create the ec2 vpc control subnet**
    and add them to the **create-vpc-subnets.yml** file.
    1. Add the following task to include the new task file in the **verify.yml** file.
        
          ```yaml
            - name:  Add the subnets
              include_tasks: create-vpc-subnets.yml
         ``` 
        
    1. cd ..
    1. Run `molecule test`.  The test should pass.

We have tested and added the Amazon VPC subnets and completed our 2nd TDD iteration.

[**<--Back to main instructions**](../readme.md#2ndTDD)