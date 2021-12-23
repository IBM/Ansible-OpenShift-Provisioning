# Ansible-OpenShift-Provisioning

## Table of Contents
* [Scope](#Scope)
* [Supported Operating Systems](#Supported-Operating-Systems)
* [Pre-Requisites](#Pre-Requisites)
* [Instructions](#Installation-Instructions)
* [Setup](#Setup)
* [Provisioning](#Provisioning)
* [Post-Install Complete](#Post-Install-Complete)
* [Troubleshooting](#Troubleshooting)
* [Teardown](#Teardown)
* [Tags](#Tags)

## Scope
* The goal of this playbook is to automate the setup and deployment of a User Provisioned Infrastructure (UPI) OpenShift cluster on an IBM Z or LinuxONE mainframe utilizing Kernel Virtual Machine (KVM) as the virtualization method.
* This README file gives extremely detailed step-by-step instructions for you to use as a reference. It assumes near-zero experience with Ansible.

## Supported Operating Systems 
for local workstation running Ansible
* Linux (RedHat and Debian)
* MacOS X

## Pre-Requisites:
* A Red Hat account ([Sign Up](https://www.redhat.com/wapps/ugc/register.html?_flowId=register-flow&_flowExecutionKey=e1s1))
* A [license](https://access.redhat.com/products/red-hat-openshift-container-platform/) or [free trial](https://www.redhat.com/en/technologies/cloud-computing/openshift/try-it) of Red Hat OpenShift Container Platform for IBM Z systems - s390x architecture (OCP license comes with licenses for RHEL and CoreOS)
* Python3 intalled on your local computer ([how-to](https://realpython.com/installing-python/))
* Ansible installed on your local computer ([how-to](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html))
* If you are using Mac OS X for your localhost workstation to run Ansible, you also need to have: 
    * Homebrew package manager installed ([how-to](https://brew.sh/))
    * Updated software for command line tools (run "softwareupdate --all --install" and "xcode-select --install" in your terminal)
* Access to a logical partition (LPAR) on an IBM Z or LinuxONE mainframe, with at least:
    * 6 Integrated Facilities for Linux (IFLs) with SMT2 enabled
    * 85 GB of RAM
    * 1 TB of disk space mounted to /var/lib/libvirt/images
    * Red Hat Enterprise Linux (RHEL) 8.4 with networking configured and a root password set
    * Access to 8 (for a minimum installation) pre-allocated IPv4 addresses
* Note on DNS: The [main playbook](main.yaml) will create a DNS server on the bastion by default. If you plan to use a pre-existing DNS server instead, when filling out the variables in [env.yaml](env.yaml) in Step 3, please make sure to mark 'env.networking.dns.setup_on_bastion' to 'false'. Either way, the playbook will double-check the DNS configuration before continuing.

## Installation Instructions:

### Setup:
* **Step 1: Get This Repository**
    * Navigate to a folder where you would like to store this project in your terminal
    * Run "git clone https://github.com/IBM/Ansible-OpenShift-Provisioning.git"
* **Step 2: Get Red Hat Info**
    * In a web browser, navigate to Red Hat's [customer portal](https://access.redhat.com/products/red-hat-enterprise-linux/), click on the 'Download Latest' button, use the drop-down to select Red Hat Enterprise Linux for IBM z Systems, select your desired version, make sure 'Architcture' is 's390x', and then scroll down to 'Red Hat Enterprise Linux X.X Update KVM Guest Image' and click on 'Download Now'. See where it downloads, copy the path and paste it into [env.yaml](env.yaml) as the variable 'env.redhat.path_to_qcow2'.
    * In a web browser, navigate to the Red Hat [console](https://console.redhat.com/openshift/install/ibmz/user-provisioned) and copy the OpenShift pull secret and paste it into [env.yaml](env.yaml) as the variable 'env_pullSecret'.
* **Step 3: Set Variables**
    * In a text editor of your choice, open [env.yaml](env.yaml)
    * Fill out variables marked with '#X' to match your specific installation. 
    * Many variables are pre-filled with defaults, change pre-filled variables at your own discretion.
    * This is the most important step in the process. Take the time to make sure everything here is correct.
* **Step 4: Setup Script** 
    * Navigate to the folder where you cloned the Git Repository in your terminal.
    * Run this shell command: "ansible-playbook setup.yaml --ask-become-pass"

### Provisioning
* **Step 5: Running the Main Playbook** 
    * Navigate to the folder where you cloned the Git repository in your terminal.
    * Start the main playbook by running this shell command: "ansible-playbook main.yaml --ask-become-pass"
    * Watch Ansible as it completes the installation, correcting errors if they arise. 
    * To look at what is running in detail, open roles/'task-you-want-to-inspect'/tasks/main.yaml
    * If the process fails in error, go through the steps in the [troubleshooting](#Troubleshooting) section. use [tags](#Tags) to selectively start from a certain point. See the [main playbook](main.yaml) to determine what part you would like to run and use those tags when running the [main playbook](main.yaml). Example: "ansible-playbook main.yaml --ask-become-pass --tags 'get-ocp,create_nodes'"
    * Note: we chose to not edit the user's .bash_profile/.bashrc with an automatic ssh-add command because that would change the user's local workstation set-up in a way that was potentially undesirable. Therefore, if you close out your terminal session in the middle of provisioning, you will need to run "ansible-playbook main.yaml --tags ssh-agent" before doing anything else.

### Post-Install Complete 
* **Step 6: First-Time Login**
    * The last step of the main playbook will print a URL, username and temporary password for first-time login.
    * Use a web-browser to type in the URL, which should take you to a sign-in page. Use the provided credentials to sign in.
    * Congratulations! Your OpenShift cluster installation is now complete.  

## Troubleshooting:
If you encounter errors while running the main playbook, there are a few things you can do:
1) Double check your variables in [env.yaml](env.yaml)
2) Inspect the part that failed by opening roles/role_name/tasks/main.yaml
3) Google the specific error message
3) Re-run the role indivually with [tags](#Tags) and the verbosity '-v' option to get more debugging information (more v's give more info). For example: "ansible-playbook main.yaml --ask-become-pass --tags get_ocp -vvv"
4) Teardown troublesome KVM guests with [teardown](#Teardown) scripts and start again with [tags](#Tags). To start from the beginning, run "ansible-playbook teardown.yaml --ask-become-pass --tags full_teardown
6) E-mail Jacob Emery at jacob.emery@ibm.com
7) If it's a problem with an OpenShift verification step, first re-reun the role with [tags](#Tags). If that doesn't work, SSH into the bastion as root ("ssh root@bastion-ip-address-here") and then run,"export KUBECONFIG=/ocpinst/auth/kubeconfig" and then "oc whoami" and make sure it ouputs "system:admin". Then run the shell command from the role you would like to check on manually: i.e. 'oc get nodes', 'oc get co', etc.

## Teardown: 
* If you would like to teardown your VMs, first determine whether you would like to do a full or partial teardown, specified below.
* Full: To teardown all the VMs running on your KVM host, run: "ansible-playbook teardown.yaml --ask-become-pass --tags full_teardown". Start back again from the beginning by running "ansible-playbook main.yaml --ask-become-pass"
* Partial: To teardown all the VMS except for the bastion, run: "ansible-playbook teardown.yaml --ask-become-pass --tags partial_teardown". To start the main.yaml playbook back from that point, run main.yaml with "--tags 'get_ocp,create_nodes,verification'"

## Tags
* To be more selective with what parts of playbooks run, use tags. 
* This is especially helpful for troubleshooting. 
* To determine what you part of a playbook you would like to run, check the list below. Tags match their corresponding roles. There are also some tags like "bastion" that cover multiple roles. To see these tags, see the [main playbook](main.yaml).
* Examples: 
* "ansible-playbook main.yaml --ask-become-pass --tags get_ocp" (for one tag), or
* "ansible-playbook main.yaml --ask-become-pass --tags 'bastion,get_ocp'" (for multiple tags)

List of Tags (in alphabetical order):
* approve_certs = Tasks for approve_certs role
* attach_subscription = Auto-attach Red Hat subscription role
* bastion = Configuration of bastion
* check_nodes = Tasks for check_nodes role
* check_dns = Check DNS resolution
* check_ssh = Check SSH role
* compute = Creation of the compute nodes
* control = Creation of the control nodes
* create_bastion = Creation of bastion KVM guest
* create_bootstrap = Creation of boostrap KVM guest
* create_nodes = Second set of KVM host's plays
* dns = Configuration of DNS server on bastion
* full_teardown = Use with teardown.yaml to bring down all KVM guests
* get_ocp = Prepare bastion for installing OpenShift
* haproxy = Configuration of load balancer on bastion
* httpd = Configuration of Apache server on bastion
* install_packages = Install and update packages
* kvm_host = All KVM host tasks
* kvm_prep = First set of KVM host's tasks
* localhost = Tasks that apply to the local machine running Ansible
* prep_kvm_guest = Get Red Hat CoreOS kernel and initramfs on host
* partial_teardown = Use with teardown.yaml to bring down all VMs except bastion
* set_selinux_permissive = Tasks related to SELinux settings
* set_firewall = Configuration of firewall
* setup = First set of setup tasks on the localhost
* ssh = All SSH tasks
* ssh_agent = Setting up SSH agent
* ssh_copy_id = Copying SSH key to target
* ssh_key_gen = Ansible SSH keypair creation
* ssh_ocp_key_gen = Generate SSH key pair for OpenShift on bastion
* verification = All OpenShift cluster verification tasks
* wait_for_bootstrap = Tasks for to wait_for_bootstrap role
* wait_for_cluster_operators = Tasks for wait_for_cluster_operators
* wait_for_install_complete = Tasks for wait_for_install_complete role