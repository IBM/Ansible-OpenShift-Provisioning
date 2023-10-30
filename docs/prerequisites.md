
# Prerequisites
## Red Hat
* Account ([Sign Up](https://www.redhat.com/wapps/ugc/register.html?_flowId=register-flow&_flowExecutionKey=e1s1))
* [License](https://access.redhat.com/products/red-hat-openshift-container-platform/) or [free trial](https://www.redhat.com/en/technologies/cloud-computing/openshift/try-it) of Red Hat OpenShift Container Platform for IBM Z systems - s390x architecture (comes with the required licenses for Red Hat Enterprise Linux (RHEL) and CoreOS)
## IBM zSystems
* Hardware Management Console (HMC) access on IBM zSystems or LinuxONE
* In order to use the [playbook](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/2_create_kvm_host.yaml) that automates the creation of the KVM host Dynamic Partition Manager (DPM) mode is required.
    * If DPM mode is not an option for your environment, that playbook can be skipped, but a bare-metal RHEL server must be set-up on an LPAR manually (Filipe Miranda's [how-to article](https://www.linkedin.com/pulse/demystifying-install-process-red-hat-enterprise-linux-filipe-miranda/)) before moving on. Once that is done, continue with the [playbook 3](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/3_setup_kvm_host.yaml) that sets up the KVM host.
* For a minimum installation, at least:
    * 6 Integrated Facilities for Linux (IFLs) with SMT2 enabled
    * 85 GB of RAM
    * An FCP storage group created with 1 TB of disk space
    * 8 IPv4 addresses
## File Server
* A file server accessible from your IBM zSystems / LinuxONE server.
* Either FTP or HTTP service configured and active.
* Once a RHEL server is installed natively on the LPAR, pre-existing or configured by this automation, (i.e. the KVM host), you can use that as the file server. 
* If you are not using a pre-existing KVM host(s) and need to create them using this automation, you must use an FTP server because the HMC does not support HTTP.
* A user with sudo and SSH access on that server.
* A DVD ISO file of Red Hat Enterprise Linux (RHEL) 8 for s390x architecture mounted in an accessible folder (e.g. /home/<user>/rhel/ for FTP or /var/www/html/rhel for HTTP)
    * If you do not have RHEL for s390x yet, go to the Red Hat [Customer Portal](https://access.redhat.com/downloads/content) and download it.
    * Under 'Product Variant' use the drop-down menu to select 'Red Hat Enterprise Linux for IBM z Systems' 
    * Double-check it's for version 8 and for s390x architecture
    * Then scroll down to Red Hat Enterprise Linux 8.x Binary DVD and click on the 'Download Now' button.
    * To pull the image directly from the command-line of your file server, copy the link for the 'Download Now' button and use `wget` to pull it down.
        ```
        wget "https://access.cdn.redhat.com/content/origin/files/sha256/13/13[...]40/rhel-8.7-s390x-dvd.iso?user=6[...]e"
        ```
    * Don't forget to mount it too:
        * FTP:
            ```
            mount <rhel-8.7-s390x-dvd.iso> /home/<user>/rhel
            ```
        * or HTTP:
            ```
            mount <rhel-8.7-s390x-dvd.iso> /var/www/html/rhel
            ```
* A folder created to store config files (e.g. /home/user/ocp-config for FTP or /var/www/html/ocp-config for http)
    * For FTP:
        ```
        sudo mkdir /home/<username>/ocp-config
        ```
    * or HTTP:
        ```
        sudo mkdir /var/www/html/ocp-config
        ```
## Ansible Controller
* The computer/virtual machine running Ansible, sometimes referred to as localhost.
* Must be running on with MacOS or Linux operating systems.
* Network access to your IBM zSystems / LinuxONE hardware
* All you need to run Ansible is a terminal and a text editor. However, an IDE like [VS Code](https://code.visualstudio.com/download) is highly recommended for an integrated, user-friendly experience with helpful extensions like [YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml).
* [Python3](https://realpython.com/installing-python/) installed:
    * MacOS, first install [Homebrew](https://brew.sh/) package manager:
        ```
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        ```
        then install Python3
        ```
        brew install python3 #MacOS
        ```
    * Fedora:
        ```
        sudo dnf install python3 #Fedora
        ```
    * Debian:
        ```
        sudo apt install python3 #Debian
        ```
* Once Python3 is installed, you also need [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) version 2.9 or above:
```
pip3 install ansible
```
* Once Ansible is installed, you will need a few collections from Ansible Galaxy:
```
ansible-galaxy collection install community.general community.crypto ansible.posix community.libvirt
```
* If you will be using these playbooks to automate the creation of the LPAR(s) that will act as KVM host(s) for the cluster, you will also need:
```
ansible-galaxy collection install ibm.ibm_zhmc 
```
* If you are using MacOS, you also need to have [Xcode](https://apps.apple.com/us/app/xcode/id497799835?mt=12):
```
xcode-select --install
```
## Jumphost for NAT network
* If for KVM network NAT is used, instead of macvtap, a ssh tunnel using a jumphost is required to access the OCP cluster. To configure the ssh tunnel expect is required on the jumphost. Expect will be installed during the setup of the bastion (4_setup_bastion.yaml playbook). In case of missing access to install additional packages, install it manually on the jumphost by executing following command:
```
yum install expect 
```
In addition make sure that python3 is installed on the jumphost otherwise ansible might fail to run the tasks. You can install python3 manually by executing the following command:
```
yum install python3 
```
