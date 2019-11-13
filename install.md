# OpenStack/Contrail Installation Steps

The goal of the following steps is to simulate the existing hardware OpenStack/Contrail installation, located in e-shelter/Frankfurt. Therefore we create a new and isolated OpenStack project in the existing hardware deployment and spawn 5 virtual machines.

•	One deploy node from where the installation will be deployed and which will simulate the real deploy server
•	Two compute nodes
•	Three control nodes


   * <a href="#1 Preparations">1 Preparations</a>
      * <a href="#1.1 OpenStack">1.1 OpenStack</a>
      * <a href="#1.2 Terraform">1.2 Terraform</a>
   * <a href="#2 Create new virtual Instances">2 Create new virtual Instances</a>
   * <a href="#3 Install OpenStack and Contrail">3 Install OpenStack and Contrail</a>
   * <a href="#4 Proxy Settings">4 Proxy Settings</a>
      * <a href="#4.1 SecureCRT">4.1 SecureCRT</a>
      * <a href="#4.2 Firefox">4.2 Firefox</a>

</br>
------------
</br>

<a name="1 Preparations"></a>

### 1 Preparations

<a name="1.1 OpenStack"></a>

#### 1.1 OpenStack 

- Access the OpenStack hardware deployment via web browser (http://172.25.1.100/)

       >>> User:     admin
           Password: contrail123

- If you get a "Something went wrong!" message, please replace URL "http://172.25.1.100/project/" with "http://172.25.1.100/admin/" in the web browser.

<p align="center">
  <img src="https://git.xantaro.net/Contrail-Factory/documentation/images/error_login.png">
</p>

- Create a new User, if necessary

       >>> Identity > Users > Create User

           Domain ID > default
           Domain Name > default
           User Name > Xantaro-Username
           Role > Admin

<p align="center">
  <img src="https://git.xantaro.net/Contrail-Factory/documentation/images/create_user.png">
</p>

- Create a new Project, if necessary

       >>> Identity > Projects and click the “Create Project” button. 
       
           Fill out the mask with the mandatory informations
           Add your user as admin

- If you have a user account and a project, login with your personal credentials and associate the new project to your account under "Identity > Projects > 'project name' > Manage Members". 

       >>> Add your user as an admin and save the change.

<p align="center">
  <img src="https://git.xantaro.net/Contrail-Factory/documentation/images/project_association.png">
</p>

- Generate a ssh-key, if necessary, and send the ssh-key (structure: ssh-rsa / [key] / [commend]) to an admin user of s1 deploy environment

- Import your public SSH key, generated on your local laptop, via OpenStack web GUI under "Compute" > "Key Pairs" > "Import Public Key" and copy/paste the string into the mask.

<p align="center">
  <img src="https://git.xantaro.net/Contrail-Factory/documentation/images/import_ssh_key.png">
</p>

</br>

<a name="1.2 Terraform"></a>

#### 1.2 Terraform 

- To create a project for Terraform, login to the deployment server (172.25.1.71) with user "root" after your public SSH key, created on your laptop, was added.

       >>> Putty

           SSH > Auth: 
           Add ppk key
           Allow agent forwarding

           Session:
           root@172.25.1.71

- Check if you’re located in /root. If not, navigate to /root.

       >>> pwd

- Create a new user

       >>> useradd -d /home/[username] -m [username]

- switch from root user to your own user

- Create an new project directory 

       >>> mkdir [project_folder]

- Change to the project directory

       >>> cd [project_folder]

- Clone git repository to load all preconfigured Terraform scripts in your personal project folder

       >>> git clone git@git.xantaro.net:Contrail-Factory/terraform.git

- Change to the Terraform directory

       >>> cd terraform

</br>
------------
</br>

<a name="2 Create new virtual Instances"></a>

### 2 Create new virtual Instances

- To create a project via Terraform, login with your user to the main deploy server (172.25.1.71) and enter the terraform folder

       >>> cd [project_folder]/terraform  

- Copy the "auth_variables.tf_sample" file to "auth_variables.tf".

       >>> cp auth_variables.tf_sample auth_variables.tf

- Adapt the variables in "auth_variables.tf", using vi/vim. Replace <USERNAME>/<OS-PROJECT>/<USER-PW> with your specific user name/project/password in insert mode and save and quit the file in command mode (“:wq”).

       >>> vim auth_variables.tf
	
           variable os_user {
              default = "<USERNAME>"
           }
           variable os_tenant {
              default = "<OS-PROJECT/TENANT-NAME>"
           }
           variable os_password {
              default = "<USER-PW>"
           }

- Generate a SSH keypair in "setup_project" directory (for terraform only)

       >>> ssh-keygen -t rsa
           Generating public/private rsa key pair.
           Enter file in which to save the key (/root/.ssh/id_rsa): id_rsa

           Enter name, no password needed

- Check if the keys (id_rsa/id_rsa.pub) are present in "setup_project"

       >>> ls -l

- Perform "terraform init"

       >>> terraform init

- Perform "terraform plan"

       >>> terraform plan -out plan

- Check if the plan file ‘plan’ is present in ‘setup_project’ folder.

       >>> ls –l

- Apply the previously created plan

       >>> terraform apply plan

- If the plan is not implemented successfully, you can destroy the environment, override the ‘plan’ file and reapply the plan.

       >>> terraform destroy
       >>> terraform plan -out plan
       >>> terraform apply plan

- Sometimes not all elements (e.g. Security Groups) are destroyed by terraform and you have to do it manually in via OpenStack GUI.

       >>> project > networks > securitygroups

</br>
------------
</br>

<a name="3 Install OpenStack and Contrail"></a>

### 3 Install OpenStack and Contrail 

The following steps are performed on the newly created virtual deploy server (172.25.63.X), not on the main deploy server (172.25.1.71). It takes some minutes until the virtual deploy server is ready for use.

- Check via OpenStack GUI if your personal public SSH key and the public key of the main deploy server, created under "/root/sstey/sstey-m4/terraform/setup_project", is present on the virtual deploy server. 

       >>> Go in “Project > Compute > Instances > choose instance ‘deploy’ > go to tab ‘Log’ > click ‘Full Log’ on the right side of the window”.

<p align="center">
  <img src="https://git.xantaro.net/Contrail-Factory/documentation/images/deploy_log.png">
</p>

- Login to the virtual deploy server via SSH (172.25.63.X) with username ‘xuser’ 

- Check if the preconfigured folder “contrail-ansible-deployer” is present.

       >>> ls -l

- Change directory to “contrail-ansible-deployer”

       >>> cd contrail-ansible-deployer/

- Change to another branch (R1909) with “git checkout” command

       >>> git checkout R1909

           Branch R1909 set up to track remote branch R1909 from origin.
           Switched to a new branch 'R1909'

- Change into the “config” folder

       >>> cd config

- Copy instances.yaml

       >>> cp /home/xuser/terraform/contrail_configs/instances.yaml /home/xuser/contrail-ansible-deployer/config/instances.yaml

- Paste the blue text below into the “instances.yaml” file and adapt the blue marked parameters via vim/vi editor, according to your setup and save the file
 
       >>> vim instances.yaml

           Under 'provider_config > bms > domainsuffix’, replace ‘sstey-m4’ with your project name
           Under ‘kolla_config > kolla_globals > keepalived_virtual_router_id’, change the parameter to a random value.

- Change directory to “contrail-ansible-deployer”

       >>> cd ..

- The next steps reference to the following URL

       >>> https://github.com/Juniper/contrail-ansible-deployer/wiki/Contrail-with-Openstack-Kolla

- The following playbook installs packages on the deployer host as well as the target host required to bring up the kolla and contrail containers.

       >>> sudo ansible-playbook -i inventory/ -e orchestrator=openstack playbooks/configure_instances.yml

           The completion of the script takes some minutes (10 or even longer) and you should get similar result, as shown below.
           192.168.2.10               : ok=46   changed=27   unreachable=0    failed=0   
           192.168.2.11               : ok=46   changed=27   unreachable=0    failed=0   
           192.168.2.12               : ok=46   changed=27   unreachable=0    failed=0   
           192.168.2.30               : ok=48   changed=27   unreachable=0    failed=0   
           192.168.2.31               : ok=48   changed=27   unreachable=0    failed=0   
           localhost                  : ok=54   changed=9    unreachable=0    failed=0

           If some nodes are failing, please run the script again.

- Deploy Contrail and Kolla containers.

       >>> sudo ansible-playbook -i inventory/ playbooks/install_openstack.yml

           The completion of the script takes some minutes (10 or even longer) and you should get similar result, as shown below.
           192.168.2.10               : ok=288   changed=163   unreachable=0    failed=0   
           192.168.2.11               : ok=220   changed=118   unreachable=0    failed=0   
           192.168.2.12               : ok=220   changed=118   unreachable=0    failed=0   
           192.168.2.30               : ok=70    changed=35    unreachable=0    failed=0   
           192.168.2.31               : ok=68    changed=35    unreachable=0    failed=0   
           localhost                  : ok=54    changed=2     unreachable=0    failed=0

           If some nodes are failing, please run the script again.

       >>> sudo ansible-playbook -i inventory/ -e orchestrator=openstack playbooks/install_contrail.yml

           The completion of the script takes some minutes (10 or even longer) and you should get similar result, as shown below.
           192.168.2.10               : ok=60    changed=40   unreachable=0    failed=0   
           192.168.2.11               : ok=60    changed=40   unreachable=0    failed=0   
           192.168.2.12               : ok=60    changed=40   unreachable=0    failed=0   
           192.168.2.30               : ok=20    changed=12   unreachable=0    failed=0   
           192.168.2.31               : ok=20    changed=12   unreachable=0    failed=0   
           localhost                  : ok=53    changed=1    unreachable=0    failed=0

           If some nodes are failing, please run the script again.

- Now you should be able to access your OpenStack and Contrail installation via web GUI with the external VIP IP 192.168.1.100. As this is a private IP and not reachable from “outside”, we have to create a SOCKS proxy on your SSH client and use the virtual deploy server as a “gateway” to reach the private IPs. Afterwards you should be able to connect to the Control/Compute hosts via SSH client (e.g. SecureCRT) and the OpenStack/Contrail installation via web browser (e.g. Firefox).

       >>> The following overview shows the relevant IPs/URLs of the hosts which should be reached via SOCKS5 proxy

           Control 1	192.168.2.10
           Control 2	192.168.2.11
           Control 3	192.168.2.12
           Compute 1	192.168.2.30
           Compute 2	192.168.2.31
           OpenStack	http://192.168.2.100

           Contrail 	https://192.168.2.100:8143

</br>
------------
</br>

<a name="4 Proxy Settings"></a>

### 4 Proxy Settings

<a name="4.1 SecureCRT"></a>

#### 4.1 SecureCRT

- Create a SOCKS proxy using SecureCRT. First, create a new folder and configure a “master” session (in this case “1 – vDeploy”). 

       >>> “Session Options > Port Forwarding”, add a new forwarding connection. You need a random name, the port number and you need to enable “Dynamic forwarding using SOCKS 4 or 5”.

<p align="center">
  <img src="https://git.xantaro.net/Contrail-Factory/documentation/images/port_forwarding.png">
</p>

- Since this "master" session will need to be connected and remain connected for all sessions that use the SSH SOCKS proxy, it would also be a good idea to enable “Auto reconnect” and “Send protocol NO-OP” every 240 seconds.

<p align="center">
  <img src="https://git.xantaro.net/Contrail-Factory/documentation/images/port_forwarding_settings_1.png">
</p>

- Under global preferences you need to add a firewall entry with a random name. Choose type “SOCKS version 5 (no authentication)”, add “127.0.0.1” as hostname und “65080” as port.

<p align="center">
  <img src="https://git.xantaro.net/Contrail-Factory/documentation/images/port_forwarding_settings_2.png">
</p>

- Add SSH sessions for the remote hosts (Control 1-3/Compute 1-2) and add the newly created Firewall entry “Gateway Firewall”. Now you should be able to connect to all remote hosts using a SOCKS5 proxy.

<p align="center">
  <img src="https://git.xantaro.net/Contrail-Factory/documentation/images/port_forwarding_settings_3.png">
</p>

<p align="center">
  <img src="https://git.xantaro.net/Contrail-Factory/documentation/images/port_forwarding_settings_4.png">
</p>

</br>

<a name="4.2 Firefox"></a>

#### 4.2 Firefox 

- To reach the OpenStack/Contrail web GUIs we need to add some Proxy config in the Firefox web browser.

- To avoid certification issues, it is a good idea to create a new Firefox profile for every new Contrail deployment. After starting Firefox you can choose between your default “web” profile and your “Contrail” profile.

<p align="center">
  <img src="https://git.xantaro.net/Contrail-Factory/documentation/images/firefox_settings_1.png">
</p>

- Open the Firefox Settings page and search for ‘Proxy’ and open the Proxy settings page. Change the settings as shown in the following screenshot.

<p align="center">
  <img src="https://git.xantaro.net/Contrail-Factory/documentation/images/firefox_settings_2.png">
</p>

- Paste the external VIP IP into the Firefox web browser (http://192.168.1.100) to access your previously installed OpenStack environment via web GUI.

       >>> User:     admin
       >>> Password: contrail123

Comment: This action will only succeed if your previously configured “master” SSH session (SOCKS5 proxy) to the virtual deploy server is established!

<p align="center">
  <img src="https://git.xantaro.net/Contrail-Factory/documentation/images/firefox_settings_3.png">
</p>

- Paste the external VIP IP into the Firefox web browser, using HTTPS and a specified port “8143” (https://192.168.1.100:8143), to access the Contrail/Tungsten web GUI.

       >>> User:     admin
       >>> Password: contrail123

Comment: This action will only succeed if your previously configured “master” SSH session (SOCKS5 proxy) to the virtual deploy server is established!
