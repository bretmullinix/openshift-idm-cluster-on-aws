# 4th TDD Iteration --> Add the AWS VPC Gateway

Last updated: 08.12.2020

## Purpose

The purpose of this iteration is to add the AWS VPC Route Table to the AWS environment.

## Procedure

1. Open a terminal
2. Activate your virtual environment
1. cd aws-infrastructure-install/molecule/default


1. **RED** --> Test for the existence of the VPC subnet
    
    1. Edit the **verify.yml** file.
    
    1. Add the following contents to the end of the **verify.yml** file:
    
          ```yaml    
            # Gather information about any VPC route table with a tag key Name and value Example
             - name: Create the EC2 Route Table Information
               ec2_vpc_route_table_info:
                 aws_access_key: "{{ aws_access_key }}"
                 aws_secret_key: "{{ aws_secret_key }}"
                 region: "{{ aws_region }}"
                 filters:
                   "tag:Name": "{{ aws_infrastructure_install_vpc.route_table }}"
               register: route_table_info
         
             - name: Print the EC2 Route Table information
               debug:
                 var: route_table_info
         
             - name: Fail if the route table does not exist
               fail:
                 msg:  "The route table called '{{ aws_infrastructure_install_vpc.route_table  }}' does not exist."
               when:
                 - route_table_info.route_tables is not defined or route_table_info.route_tables | length  == 0
            
          ``` 
         
      1. cd ../..
      1. Run `molecule converge`
      1. Run `molecule verify`
    
            The test should fail.  We haven't written any
            code to create the AWS vpc route table.
            The purpose of the test in TDD is to
            first prove that a test fails without writing any
            code.
      1. Run `molecule destroy`

1. **GREEN** --> Add the task to create the vpc route table to the **tasks/main.yml** file.
    
    1. Add the following task to the end of th **tasks/main.yml** file.
        
        ```yaml
          # create routing to/from internet
          - name: Route Table to/from Gateway
            ec2_vpc_route_table:
              vpc_id: "{{ vpc_facts.id }}"
              aws_access_key: "{{ aws_access_key }}"
              aws_secret_key: "{{ aws_secret_key }}"
              region: "{{ aws_region }}"
              subnets:
                - "{{ vpc_control_subnet.id }}"
              routes:
                - dest: 0.0.0.0/0
                  gateway_id: "{{ igw.gateway_id  }}"
              tags:
                Name: "{{ aws_infrastructure_install_vpc.route_table }}"
        ```
            
      1. Run `molecule converge`
      1. Run `molecule verify`
        
            Verification should be successful.  We added the AWS vpc route table tasks to
            create the vpc route table in the
            **tasks/main.yml** file.  We are now
            back in the **Green** state for the
            **Red, Green, Refactor** iteration of Test
            Driven Development (TDD).
      1. Run `molecule destroy`
      
1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **verify.yml** looks a little messy.  Let's extract the new **vpc route table**
        tasks into a file and reference the file from verify.yml.
    1. cd molecule/default/tasks
    1. Create the file called **check-for-vpc-route_table-existence.yml**.
    1. Remove the tasks starting with the task **Create the EC2 Route Table Information**
    and add them to the **check-for-vpc-route_table-existence.yml** file.
    1. Add the following task to include the new task file in the **verify.yml** file.
    
          ```yaml
            - name:  Determine if vpc exists
              include_tasks: tasks/check-for-vpc-route_table-existence.yml
         ``` 
    
    1. cd ../..
    1. Run `molecule test`.  The test should pass.

We have tested and added the Amazon VPC Gateway and completed our 4th TDD iteration.

[**<--Back to main instructions**](../readme.md#4thTDD)