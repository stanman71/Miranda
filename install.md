# OpenStack/Contrail Installation Steps

The goal of the following steps is to simulate the existing hardware OpenStack/Contrail installation, located in e-shelter/Frankfurt. Therefore we create a new and isolated OpenStack project in the existing hardware deployment and spawn 5 virtual machines.

•	One deploy node from where the installation will be deployed and which will simulate the real deploy server
•	Two compute nodes
•	Three control nodes


   * <a href="#1 Preparations in OpenStack">1 Preparations in OpenStack</a>
   * <a href="#2 Preparations for Terraform">2 Preparations for Terraform</a>


   * <a href="#2 Client Music">2 Client Music</a>
   * <a href="#3 Squeezelite Client">3 Squeezelite Client</a>
   * <a href="#4 Raspotify">4 Raspotify</a>

</br>
------------
</br>

<a name="1 Preparations in OpenStack"></a>

### 1 Preparations in OpenStack

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

       >>> Identity > Projects and click the “Create Project” button. Fill out the mask with the mandatory information

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
------------
</br>

<a name="2 Preparations for Terraform"></a>

### 2 Preparations for Terraform 

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

<a name="3 Setup the new project and spawn virtual instances via Terraform"></a>

### 3 Setup the new project and spawn virtual instances via Terraform

- To create a project via Terraform, login with your user to the deploy server (172.25.1.71) and enter the terraform folder

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



