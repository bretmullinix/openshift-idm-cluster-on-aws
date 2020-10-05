# 4th TDD Iteration -->  Install the Nexus Software

Last updated: 10.05.2020

## Purpose

The purpose of this iteration is to install the Nexus software on the target server.

## Procedure
1. cd nexus-instance/molecule/default

1. **RED** --> Test to see if Nexus is installed.
    
    1. Add the following code to the end of **verify.yml**.
        
        ```yaml
        - name: Get Nexus Service
          set_fact:
            nexus_service: "{{ item.value }}"
          loop: "{{ lookup('dict', services_state.ansible_facts.services) }}"
          when: item.key == 'nexus.service'
    
        - name: Fail if Nexus is not installed
          fail:
            msg: "The nexus service is not installed"
          when: nexus_service is not defined
        ```
           
        The tasks above checks to see if the Nexus server software is installed.
    1. cd ../..
    1. Run `molecule verify`.  The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Add the tasks to install the Nexus server.
     
    1. cd molecule/default
        
    1. Add the following tasks to the end of the **tasks/main.yml** file.
        
        ```yaml
        - name: Add Nexus User
          user:
            name: nexus
            comment: Nexus Service Account User
            home: /opt/nexus
        
        - name: Give Nexus User Ownership on /opt/nexus Directory
          file:
            path: /opt/nexus
            owner: nexus
            group: nexus
            state: directory
            mode: '0755'
        
        - name: Make sure the Nexus tar file does not exist
          file:
            path: "{{ role_path }}/files/nexus_software/{{ nexus_file }}"
            state: absent
          delegate_to: 127.0.0.1
          run_once: true
        
        - name: Combine the Nexus software into tar file.  Was split to be put into git.
          shell: 'cat {{ role_path }}/files/nexus_software/{{ nexus_file }}.parta* > {{ role_path }}/files/nexus_software/{{ nexus_file }}'
          delegate_to: 127.0.0.1
          run_once: true
        
        - name: Get sha1sum of file
          stat:
            path: "{{ role_path }}/files/nexus_software/{{ nexus_file }}"
            checksum_algorithm: sha1
            get_checksum: yes
          register: sha
          delegate_to: 127.0.0.1
          run_once: true
        
        
        - name: Fail if the original Nexus software checksum is different from the original file.
          fail:
            msg:  "The Nexus software tar file does not have the same sha1 checksum as the original."
          delegate_to: 127.0.0.1
          run_once: true
          when: nexus_software_sha1_checksum != sha.stat.checksum
        
        - name: Copy the nexus software to the target server
          copy:
            src: "{{ role_path }}/files/nexus_software/{{ nexus_file }}"
            dest: "/opt/nexus/{{ nexus_file }}"
            owner: nexus
            group: nexus
            mode: 755
        
        - name: Get the remote server sha1sum of the file
          stat:
            path: "/opt/nexus/{{ nexus_file }}"
            checksum_algorithm: sha1
            get_checksum: yes
          register: sha
        
        - name: Fail if the original Nexus software checksum is different from the remote file.
          fail:
            msg:  "The Nexus software tar file on the target server does not have the same sha1 checksum as the original."
          when: nexus_software_sha1_checksum != sha.stat.checksum
        
        - name: Extract the nexus tar file into /opt/nexus
          unarchive:
            src: "/opt/nexus/{{ nexus_file }}"
            dest: "/opt/nexus"
            owner: nexus
            mode: 755
            remote_src: yes
        
        - name: Change permissions on the nexus software folder to 0755 recursively
          file:
            path: "/opt/nexus"
            mode: 0755
            owner: nexus
            group: nexus
            recurse: True
        
        - name: Run nexus software as the nexus user
          blockinfile:
            path: /opt/nexus/{{ nexus_file_name }}/bin/nexus.rc
            block: |
              run_as_user="nexus"
        
        - name: Create symbolic link to create the Nexus Service
          file:
            src: "/opt/nexus/{{ nexus_file_name }}/bin/nexus"
            dest: "/etc/init.d/nexus"
            state: link
        
        - name: Add Nexus As A Service
          command: 'chkconfig --add /etc/init.d/nexus'
        
        - name: Start and Enable Nexus
          service:
            name: nexus
            state: started
            enabled: yes
        ```   
           
        The task installs the Nexus software on the target server.  Let's explain these tasks:
        
        1. **Add Nexus User** task --> The task creates the **nexus** user on the target machine
           with the default home directory of **/opt/nexus**.  The home directory is also where the
           nexus software is installed.
           
        1. **Give Nexus User Ownership on /opt/nexus Directory** --> The task makes the **nexus** user
            the owner and sets the group to the default group for the nexus user.  Also, the task
            changes permissions on the folder to **755**.
        
        1. **Make sure the Nexus tar file does not exist** --> This task deletes the nexus software tar file.
        
        1. **Combine the Nexus software into tar file.  Was split to be put into git.** --> This task combines
          all the nexus software part files in the **files/nexus_software** folder into the original 
          downloaded software tar file from Sonatype.  The splitting and re-combining of the tar file was
          necessary because, by default, git does not allow files checked in that are larger than 100 MB.
          
        1. **Get sha1sum of file** --> This task gets the sha1 checksum hash for the new tar file produced
           in the previous task.
          
        1. **Fail if the original Nexus software checksum is different from the original file.** --> Compares the
           original sha1 checksum hash to the sha1 checksum hash of the newly combined tar file.  If they don't
           match, we know the Sonatype Nexus software file is corrupted.
        
        1. **Copy the nexus software to the target server** --> Copies the newly created Sonatype Nexus software
           tar file to the target server **/opt/nexus** directory.
           
        1. **Get the remote server sha1sum of the file** -->  This task gets the sha1 checksum 
           hash for the copied tar file produced in the previous task.
        
        1. **Fail if the original Nexus software checksum is different from the remote file.** --> Compares the
           original sha1 checksum hash to the sha1 checksum hash of the copied tar file.  If they don't
           match, we know the Sonatype Nexus software file is corrupted.
        
        1. **Extract the nexus tar file into /opt/nexus** --> Unarchives the copied Sonatype Nexus software
           on the target server.
           
        1. **Change permissions on the nexus software folder to 0755 recursively** --> Changes ownership and
           group of all files in the **/opt/nexus** to the nexus user and his group.
           
        1. **Run nexus software as the nexus user** --> Changes the user who runs the **nexus** software on
           the server from **root** to the user **nexus**.  By not using the **root** user, we make sure that if
           a person hacks the software, we ensure the hacker does not have privileged access to the server.
           
        1. **Create symbolic link to create the Nexus Service** --> creates a symbolic link to the
          nexus software executable in **/etc/init.d**.  This is needed to make Sonatype Nexus a service
          on the target server.
          
        1. **Add Nexus As A Service** --> Installs Sonatype Nexus as a service.
        
        1. **Start and Enable Nexus** --> Starts and enables Nexus as a service.  After this task runs,
           Sonatype Nexus software will restart when the target server is rebooted.
        
    1. cd ../..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**,
    and the Nexus software installs.
    
    1. Run `molecule verify`. The test should pass.  The test represents
    the **Green** in the **Red, Green, Refactor** iteration of TDD.

1. **REFACTOR** --> Does any of the code need **Refactoring**?

    1. The **verify.yml** looks a little messy.  Let us extract the
       tasks, which check to see if the Nexus software is installed, into a file and reference 
       the file from verify.yml.
        
    1. cd molecule/default
        
    1. mkdir tasks
        
    1. cd tasks
        
    1. Create the file called **is_nexus_software_installed.yml**
    
    1. Copy the tasks from the **verify.yml** starting from the tasks name 
       **Get Nexus Service** to the end of the file and add 
       them to the **is_nexus_software_installed.yml** file.
        
    1. cd ..
        
    1. In the **verify.yml**, remove the task titled **Get Nexus Service** and all preceding tasks.
        
    1. Add the following to the end of **verify.yml**.
        
        ```yaml
          - name:  Determine if the Nexus Software is Installed
            include_tasks: tasks/is_nexus_software_installed.yml
       ```          
           
    1. cd ../..
    1. We still have some refactoring to do.
    1. cd tasks
    1. mkdir main
    1. cd main
    1. Make the file **install_nexus.yml**
    1. Copy the tasks from the **tasks/main.yml** file starting with the task titled
       **Add Nexus User** to the end of the file.
    1. Paste the tasks in the **install_nexus.yml** file.
    1. cd ..
    1. Edit the **tasks/main.yml** file by removing the tasks starting with **Add Nexus User** to the end
       of the file.
    1. Add the following to the end of **tasks/main.yml**.
        
        ```yaml
          - name:  Install Nexus Software
            include_tasks: "{{role_path}}/tasks/main/install_nexus.yml"
       ```     
    1. Run `molecule test`.  The test should pass.  Your refactoring is complete.

We have installed the Nexus software and completed our 4th TDD iteration.

[**<--Back to main instructions**](../readme.md#4thTDD)