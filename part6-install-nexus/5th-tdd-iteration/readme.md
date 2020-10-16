# 5th TDD Iteration -->  Securing Nexus with SSL

Last updated: 10.16.2020

## Purpose

The purpose of this iteration is to configure and run Nexus using SSL on the target server.

## Procedure

### 5th TDD Iteration
1. cd nexus-instance

1. mkdir templates
    
1. cd templates
    
1. Make the file **jetty-https.xml.j2**
    
1. Add the following content to the **jetty-https.xml** file.
    
    ```yaml
    <?xml version="1.0"?>
    <!DOCTYPE Configure PUBLIC "-//Jetty//Configure//EN" "http://www.eclipse.org/jetty/configure_9_0.dtd">
    <Configure id="Server" class="org.eclipse.jetty.server.Server">
    
      <!--
      ==== HTTPS ====
      Set the following inside nexus.properties:
      application-port-ssl: the port to listen for https connections
      -->
    
      <Ref refid="httpConfig">
        <Set name="secureScheme">https</Set>
        <Set name="securePort"><Property name="application-port-ssl" /></Set>
      </Ref>
    
      <New id="httpsConfig" class="org.eclipse.jetty.server.HttpConfiguration">
        <Arg><Ref refid="httpConfig"/></Arg>
        <Call name="addCustomizer">
          <Arg>
            <New id="secureRequestCustomizer" class="org.eclipse.jetty.server.SecureRequestCustomizer">
              <!-- 7776000 seconds = 90 days -->
              <Set name="stsMaxAge"><Property name="jetty.https.stsMaxAge" default="7776000"/></Set>
              <Set name="stsIncludeSubDomains"><Property name="jetty.https.stsIncludeSubDomains" default="false"/></Set>
              <Set name="sniHostCheck"><Property name="jetty.https.sniHostCheck" default="false"/></Set>
            </New>
          </Arg>
        </Call>
      </New>
    
      <New id="sslContextFactory" class="org.eclipse.jetty.util.ssl.SslContextFactory$Server">
        <Set name="certAlias">nexus</Set>
        <Set name="KeyStorePath"><Property name="ssl.etc"/>/keystore.jks</Set>
        <Set name="KeyStorePassword">{{ nexus_jetty_keystore_password }}</Set>
        <Set name="KeyManagerPassword">{{ nexus_jetty_keystore_password }}</Set>
        <Set name="TrustStorePath"><Property name="ssl.etc"/>/keystore.jks</Set>
        <Set name="TrustStorePassword">{{ nexus_jetty_keystore_password }}</Set>
        <Set name="EndpointIdentificationAlgorithm"></Set>
        <Set name="NeedClientAuth"><Property name="jetty.ssl.needClientAuth" default="false"/></Set>
        <Set name="WantClientAuth"><Property name="jetty.ssl.wantClientAuth" default="false"/></Set>
        <Set name="ExcludeCipherSuites">
          <Array type="String">
            <Item>SSL_RSA_WITH_DES_CBC_SHA</Item>
            <Item>SSL_DHE_RSA_WITH_DES_CBC_SHA</Item>
            <Item>SSL_DHE_DSS_WITH_DES_CBC_SHA</Item>
            <Item>SSL_RSA_EXPORT_WITH_RC4_40_MD5</Item>
            <Item>SSL_RSA_EXPORT_WITH_DES40_CBC_SHA</Item>
            <Item>SSL_DHE_RSA_EXPORT_WITH_DES40_CBC_SHA</Item>
            <Item>SSL_DHE_DSS_EXPORT_WITH_DES40_CBC_SHA</Item>
          </Array>
        </Set>
      </New>
    
      <Call  name="addConnector">
        <Arg>
          <New id="httpsConnector" class="org.eclipse.jetty.server.ServerConnector">
            <Arg name="server"><Ref refid="Server" /></Arg>
            <Arg name="acceptors" type="int"><Property name="jetty.https.acceptors" default="-1"/></Arg>
            <Arg name="selectors" type="int"><Property name="jetty.https.selectors" default="-1"/></Arg>
            <Arg name="factories">
              <Array type="org.eclipse.jetty.server.ConnectionFactory">
                <Item>
                  <New class="org.sonatype.nexus.bootstrap.jetty.InstrumentedConnectionFactory">
                    <Arg>
                      <New class="org.eclipse.jetty.server.SslConnectionFactory">
                        <Arg name="next">http/1.1</Arg>
                        <Arg name="sslContextFactory"><Ref refid="sslContextFactory"/></Arg>
                      </New>
                    </Arg>
                  </New>
                </Item>
                <Item>
                  <New class="org.eclipse.jetty.server.HttpConnectionFactory">
                    <Arg name="config"><Ref refid="httpsConfig" /></Arg>
                  </New>
                </Item>
              </Array>
            </Arg>
    
            <Set name="host"><Property name="application-host" /></Set>
            <Set name="port"><Property name="application-port-ssl" /></Set>
            <Set name="idleTimeout"><Property name="jetty.https.timeout" default="30000"/></Set>
            <Set name="acceptorPriorityDelta"><Property name="jetty.https.acceptorPriorityDelta" default="0"/></Set>
            <Set name="acceptQueueSize"><Property name="jetty.https.acceptQueueSize" default="0"/></Set>
          </New>
        </Arg>
      </Call>
    
    </Configure>

    ```
    Let's explain what we did different from the default **jetty-https.yml** file.
    
    1. We added the line `<Set name="certAlias">nexus</Set>`.  When we install SSL, we create a cert
       with an **alias** of **nexus**.  We need to let Jetty know the cert alias.
       
    1. When we add the SSL keystore, the passwords all change to the **nexus_jetty_keystore_password**.
       We add the code `{{ nexus_jetty_keystore_password }}` to the file where Jetty requires the password
       change.
    
1. Make the file **jetty-https.xml.j2**
1. Add the following content to the file.

    ```yaml
    # Jetty section
    # application-port=8081
    # application-host=0.0.0.0
    # nexus-context-path=/
    
    
    nexus-args=${jetty.etc}/jetty.xml,${jetty.etc}/jetty-https.xml,${jetty.etc}/jetty-requestlog.xml
    application-port-ssl=8443
    ssl.etc=${karaf.data}/etc/ssl
    
    # Nexus section
    # nexus-edition=nexus-pro-edition
    # nexus-features=\
    #  nexus-pro-feature
    
    # nexus.hazelcast.discovery.isEnabled=true

    ```
    Let's explain what we did different from the default **nexus.properties** file.
    
    1. The environment variable **${jetty.etc}** represents the same value as our
       **nexus_jetty_config_dir** variable value in the **nexus-instance/var/main.yml** file.
       
    1. We took out the **jetty-http.yml** argument from the following line to disable http access.
    
        ```properties
        nexus-args=${jetty.etc}/jetty.xml,${jetty.etc}/jetty-https.xml,${jetty.etc}/jetty-requestlog.xml
        ```
    
    1. Also, in the property above, we add the **jetty-https.yml** file to let Nexus know we
       plan on using https, and the configuration in this file.
       
    1. We inform Nexus we plan on using port **8443** with the following line.
    
        ```properties
        application-port-ssl=8443
        ```
    
    1. In the following property, we inform Nexus of the SSL certificate location.  The directory
       path **${karaf.data}/etc/ssl** has the same path as **nexus_ssl_dir** variable value in the 
       **nexus-instance/var/main.yml** file.
       
         ```properties
         ssl.etc=${karaf.data}/etc/ssl
         ```

1. cd nexus-instance/molecule/default/tasks

1. **RED** --> Test to see if Nexus is installed.
    1. Create the file **check-if-ssh-is-installed-and-working.yml**
    
    1. Add the following code to the end of **check-if-ssh-is-installed-and-working.yml**.
                
        ```yaml
         - name: Check that the keystore.jks exists
           stat:
             path: "{{ nexus_ssl_dir }}/keystore.jks"
           register: stat_result
       
         - name: Fail If Keystore doesn't exist
           fail:
             msg: "SSL has not been configured.  You don't have a Java Keystore file for the certs."
           when: not stat_result.stat.exists
       
       
         - name: Check that you can connect (GET) to a page and it returns a status 200
           uri:
             url: "{{ 'https://' + hostvars[inventory_hostname]['ansible_default_ipv4']['address'] + ':8443' }}"
             validate_certs: no
        ```
        
        Let's explain the tasks:
      
        1. **Check that the keystore.jks exists** --> This task checks for the existence of the
           **keystore.jks** file we create at the end of configuring SSL.
             
        1. **Fail If Keystore doesn't exist** --> This task will cause **verify** to fail if
           the **keystore.jks** file doesn't exist.  If the file doesn't exist, we haven't 
           fully configured SSL.
           
        1. **Check that you can connect (GET) to a page and it returns a status 200** --> This task
           checks to make sure we can reach the Nexus Server over https.  If we can't, we know
           something went wrong with configuring SSL.
                 
    1. cd ../..
    
    1. Run `molecule verify`.  The test should fail.  The test represents
       the **Red** in the **Red, Green, Refactor** iteration of TDD.

1. **GREEN** --> Add the tasks to configure the Nexus server for SSL
     
    1. cd tasks/main
    1. Make the file **generate_certificate_for_https.yml**
    1. Add the following tasks to the end of the **generate_certificate_for_https** file.
        
        ```yaml
        - name: Delete the SSL Directory for Nexus Server
          file:
            path: "{{ nexus_ssl_dir }}"
            state: absent
        
        - name: Create the SSL Directory for Nexus Server
          file:
            path: "{{ nexus_ssl_dir }}"
            state: directory
            mode: '0755'
            owner: nexus
            group: nexus
        
        - name: Generate Private Key
          openssl_privatekey:
            path: "{{ nexus_ssl_dir }}/nexis.pem"
            size: 2048
        
        - name: Generate Certificate Signing Request
          openssl_csr:
            path: "{{ nexus_ssl_dir }}/nexis.csr"
            privatekey_path: "{{ nexus_ssl_dir }}/nexis.pem"
            common_name: "{{ fqdn }}"
        
        - name: Generate Self Signed Certificate
          openssl_certificate:
            path: "{{ nexus_ssl_dir }}/nexis.cert"
            privatekey_path: "{{ nexus_ssl_dir }}/nexis.pem"
            csr_path: "{{ nexus_ssl_dir }}/nexis.csr"
            provider: selfsigned
        
        - name: "Convert the signed certificate into a PKCS12 file with the attached private key"
          openssl_pkcs12:
            friendly_name: nexus
            action: export
            path: "{{ nexus_ssl_dir }}/nexis.p12"
            privatekey_path: "{{ nexus_ssl_dir }}/nexis.pem"
            passphrase: "{{ nexus_jetty_keystore_password }}"
            certificate_path: "{{ nexus_ssl_dir }}/nexis.cert"
            state: present
        
        - name: Create Keystore and Add Self Signed Certificate and Private Key to the KeyStore
          command:  "keytool -importkeystore -srckeystore '{{ nexus_ssl_dir }}/nexis.p12' -srcstoretype pkcs12
                     -srcalias nexus -destkeystore '{{ nexus_ssl_dir }}/keystore.jks'
                     -deststoretype jks -deststorepass '{{ nexus_jetty_keystore_password }}'
                     -srcstorepass '{{ nexus_jetty_keystore_password }}' -destalias nexus -noprompt"
        
        - name: Create Jetty HTTPS Properties
          template:
            src: "{{ role_path }}/templates/jetty-https.xml.j2"
            dest: "{{ nexus_jetty_config_dir }}/jetty-https.xml"
            owner: nexus
            group: nexus
        
        - name: Create Nexus Properties
          template:
            src: "{{ role_path }}/templates/nexus.properties.j2"
            dest: "{{ nexus_properties_dir }}/nexus.properties"
            owner: nexus
            group: nexus
        
        - name: Change permissions on the nexus software folder to 0755 recursively
          file:
            path: "/opt/nexus"
            mode: 0755
            owner: nexus
            group: nexus
            recurse: True
        
        - name: Restart Nexus
          service:
            name: nexus
            state: restarted
        ```   
           
        The tasks configure the Nexus software on the target server for SSL.  Let's explain these tasks:
        
        Let's explain these tasks.
        
        1. **Delete the SSL Directory for Nexus Server** --> We delete the Nexus SSL folder
           on the target server to ensure we clean up the SSL files.
           
        1. **Create the SSL Directory for Nexus Server** --> We create the Nexus SSL folder.
        
        1. **Generate Private Key** --> We create the certificate private key in the Nexus
           SSL folder.
           
        1. **Generate Certificate Signing Request** --> We create a certificate signing request
           file (CSR) using our certificate private key with the common name being our domain name.
           The CSR contains the new certificate public key and certificate attributes, such as 
           the common name, organizational name, and organization unit.  In our case, we are just 
           setting the common name.  The CSR file is what you send to a certificate authority (CA) 
           to get a signed certificate. In our case, we are just generating a self signed certificate.
           
        1. **Generate Self Signed Certificate** --> We generate our certificate using the CSR
           and private key.
           
        1. **Convert the signed certificate into a PKCS12 file with the attached private key** -->
           Creates an archive file with a **.p12** extension.  The archive file will be password
           protected using the **nexus_jetty_keystore_password** variable value declared in the
           **nexus-instance/default/main.yml** file.  The archive is a common format containing
           the certificate and the certificate private key.
           
        1.  **Create Keystore and Add Self Signed Certificate and Private Key to the KeyStore** -->
            The task imports the certificate and certificate private key from the PKCS12 archive 
            file into a newly created **keystore.jks** Java archive file.  The Nexus Jetty server
            uses the **keystore.jks** file to configure SSL.
        
        1. **Create Jetty HTTPS Properties** --> Converts the Jinja2 **jetty-https.xml.j2**
           to a new **jetty-https.xml** file and overwrites the default jetty https configuration.
           NOTE: If you change the Nexus software included in this Ansible role, 
           you might have to change the **nexus_jetty_config_dir** variable value to where the 
           Jetty configuration exists.
           
        1. **Create Nexus Properties** --> Converts the Jinja2 **nexus.properties.j2**
           to a new **nexus.properties** file and overwrites the default nexus properties.
           NOTE: If you change the Nexus software included in this ansible role, you might
           have to change the **nexus_properties_dir** variable value to where the Nexus
           properties exist.
           
        1. **Change permissions on the nexus software folder to 0755 recursively** --> Changes
           the owner and group to the user and group **nexus** and gives all files the **0755** 
           permissions.
           
        1. **Restart Nexus** --> Restarts the Nexus service to apply SSL and be able to access
           the nexus server remotely over **https** on port **8443**.
        
    1. cd ../
    
    1. Add the following code to the **main.yml** file
    
        ```yaml
        - name: Configure Nexus for SSL
          include_tasks: "{{role_path}}/tasks/main/generate_certificate_for_https.yml"
          when: use_ssl == true
       ```
    
    1. cd ..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**,
    and the Nexus software is configured for SSL.
    
    1. Run `molecule verify`. The test should pass.  The test represents
    the **Green** in the **Red, Green, Refactor** iteration of TDD.

1. **REFACTOR** --> Does any of the code need **Refactoring**?

   The code looks pretty good so we won't do any refactoring at this time.

We have configured the Nexus software for SSL and completed our 5th TDD iteration.

[**<--Back to main instructions**](../readme.md#5thTDD)