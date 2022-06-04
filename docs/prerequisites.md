
# Prerequisites
## Red Hat
* Account ([Sign Up](https://www.redhat.com/wapps/ugc/register.html?_flowId=register-flow&_flowExecutionKey=e1s1))
* [License](https://access.redhat.com/products/red-hat-openshift-container-platform/) or [free trial](https://www.redhat.com/en/technologies/cloud-computing/openshift/try-it) of Red Hat OpenShift Container Platform for IBM Z systems - s390x architecture (comes with the required licenses for Red Hat Enterprise Linux (RHEL) and CoreOS)
## IBM zSystems
* Hardware Management Console (HMC) access on IBM zSystems or LinuxONE
* Must be in Dynamic Partition Manager (DPM) mode in order to use the [playbook](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/create_kvm_host.yaml) that automates the creation of the KVM host. 
    * If DPM mode is not an option for your environment, that playbook can be skipped, but a bare-metal RHEL server must be set-up on an LPAR manually (Filipe Miranda's [how-to article](https://www.linkedin.com/pulse/demystifying-install-process-red-hat-enterprise-linux-filipe-miranda/)) before moving on. Once that is done, continue with the [playbook](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/setup_kvm_host.yaml) that sets up the KVM host.
* For a minimum installation, at least:
    * 6 Integrated Facilities for Linux (IFLs) with SMT2 enabled
    * 85 GB of RAM
    * An FCP storage group created with 1 TB of disk space
    * 8 IPv4 addresses
## FTP Server
* On the same network as your IBM zSystems / LinuxONE hardware.
* Red Hat Enterprise Linux (RHEL) 8 for s390x architecture mounted in an accessible folder (e.g. /home/ftpuser/rhel/)
    * If you do not yet have RHEL for s390x, go to the Red Hat [Customer Portal](https://access.redhat.com/downloads/content) and download it.
    * Under 'Product Variant' use the drop-down menu to select 'Red Hat Enterprise Linux for IBM z Systems' 
    * Double-check it's for version 8 and for s390x architecture
    * Then scroll down to Red Hat Enterprise Linux 8.x Binary DVD and click on the 'Download Now' button.
* A folder to store config files (e.g. /home/ftpuser/ocp-config)
## Workstation
* A computer/virtual machine with MacOS or Linux operating system
* Network access to your IBM zSystems / LinuxONE hardware
* [Python3](https://realpython.com/installing-python/) installed:
```
brew install python3 #MacOS, see note below
```
```
sudo dnf install python3 #Fedora
```
```
sudo apt install python3 #Debian
```
* Once Python3 is installed, you also need [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html):
```
pip3 install ansible
```
* Note: If you are using MacOS, you also need to have [Homebrew](https://brew.sh/) package manager installed:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
  * and [Xcode](https://apps.apple.com/us/app/xcode/id497799835?mt=12):
```
xcode-select --install
```