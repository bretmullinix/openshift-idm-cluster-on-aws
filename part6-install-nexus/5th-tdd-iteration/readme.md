# 5th TDD Iteration -->  Securing Nexus with SSL

Last updated: 10.14.2020

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

1. cd nexus-instance/molecule/default

1. **RED** --> Test to see if Nexus is installed.
    
    1. Add the following code to the end of **verify.yml**.
        
        **TODO:** Task(s) under construction....
        
        ```yaml
       
        ```
           
        The tasks above checks to see if the Nexus server is configured for SSL.
        
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
        
        **TODO:** Steps under construction....
        
    1. cd ../
    1. Add the following code to the **main.yml** file
    
        ```yaml
        - name: Add Self Signed Certificate to Jetty Key Store
          include_tasks: "{{role_path}}/tasks/main/generate_certificate_for_https.yml"
          when: use_ssl == true
       ```
    
    1. cd ..
    
    1. Run `molecule converge`.  The command runs the **tasks/main.yml**,
    and the Nexus software installs.
    
    1. Run `molecule verify`. The test should pass.  The test represents
    the **Green** in the **Red, Green, Refactor** iteration of TDD.

1. **REFACTOR** --> Does any of the code need **Refactoring**?

   :construction: Under construction...

We have configured the Nexus software for SSL and completed our 5th TDD iteration.

[**<--Back to main instructions**](../readme.md#5thTDD)