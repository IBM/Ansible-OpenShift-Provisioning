# Ansible-OpenShift-Provisioning

## Table of Contents
* [Scope](#Scope)
* [Supported Operating Systems](#Supported-Operating-Systems)
* [Pre-Requisites](#Pre-Requisites)
* [Instructions](#Installation-Instructions)
* [Setup](#Setup)
* [Provisioning](#Provisioning)
* [Install Complete](*Install-Complete)
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
    * homebrew package manager installed ([how-to](https://brew.sh/))
    * Updated software for command line tools (run "softwareupdate --all --install" in your terminal)
* Access to a logical partition (LPAR) on an IBM Z or LinuxONE mainframe, with at least:
    * 6 Integrated Facilities for Linux (IFLs) with SMT2 enabled
    * 85 GB of RAM
    * 1 TB of disk space
* On that LPAR, Red Hat Enterprise Linux (RHEL) with networking configured and a root password set
* On that LPAR, access to 8 (for a minimum installation) pre-allocated IPv4 addresses with Fully Qualified Domain Names (FQDN)

## Installation Instructions:

### Setup:
* **Step 1: Get This Repository**
    * Navigate to a folder where you would like to store this project in your terminal
    * Run "git clone https://github.com/IBM/Ansible-OpenShift-Provisioning.git"
* **Step 2: Get Red Hat Info**
    * In a web browser, navigate to Red Hat's [customer portal](https://access.redhat.com/products/red-hat-enterprise-linux/), click on the 'Download Latest' button, use the drop-down to select Red Hat Enterprise Linux for IBM z Systems, select your desired version, make sure 'Architcture' is 's390x', and then scroll down to 'Red Hat Enterprise Linux X.X Update KVM Guest Image' and click on 'Download Now'. See where it downloads, copy the path and paste it into [env.yaml](env.yaml) as the variable 'env_rhel_qcow2'.
    * In a web browser, navigate to the Red Hat [console](https://console.redhat.com/openshift/install/ibmz/user-provisioned) and copy the OpenShift pull secret and paste it into [env.yaml](env.yaml) as the variable 'env_pullSecret'.
* **Step 3: Set Variables**
    * In a text editor of your choice, open [env.yaml](env.yaml)
    * Fill out the remaining variables to match your specific installation. Many variables are pre-filled with defaults. For a default installation, you only need to fill in the empty variables.
* **Step 4: Setup Script** 
    * Navigate to the folder where you cloned the Git Repository
    * Run "ansible-playbook setup.yaml --ask-become-pass"

### Provisioning
* **Step 5: Running the Main Playbook** 
    * If you are not already there, navigate to the folder where you cloned the Git repository in your terminal.
    * Run the main playbook by running this shell command: "ansible-playbook main.yaml --ask-become-pass"
    * Watch Ansible as it completes the installation, correcting errors if they arise. 
    * To look at what is running in detail, open roles/'task-you-want-to-inspect'/tasks/main.yaml
    * If the process fails in error, you should be able to run the same shell command to start the process from the top. To be more selective with what parts of the main playbook run, use [tags](#Tags). See the [main playbook](main.yaml) to determine what part you would like to run and use those tags when running the [main playbook](main.yaml). Example: "ansible-playbook main.yaml --ask-become-pass --tags 'get-ocp,create_nodes'"
    * Note: we chose to not edit the user's .bash_profile/.bashrc with an automatic ssh-add command because that would change the user's local workstation set-up in a way that was potentially undesirable. Therefore, if you close out your terminal session in the middle of provisioning, you will need to run "ansible-playbook main.yaml --tags ssh-agent" before doing anything else.

### Install Complete
* **Step 6: First-Time Login**
    * The last step of the main playbook will print a URL, username and temporary password for first-time login.
    * Use a web-browser to type in the URL, which should take you to a sign-in page. Use the provided credentials to sign in.
    * Congratulations! Your OpenShift cluster installation is now complete.  

## Troubleshooting:
If you encounter errors while running the main playbook, there are a few things you can do:
* 1) Check your variables in env.yaml
* 2) Inspect the task that failed by inspecting the task in roles/role_name/tasks_main.yaml
* 3) Google the specific error message
* 3) Re-Run the role indivually with with [tags](#Tags)
* 4) Teardown troublesome KVM guests with [teardown](#Teardown) scripts and start again with [tags](#Tags)
* 6) E-mail Jacob Emery at jacob.emery@ibm.com

## Teardown: 
* If you would like to teardown your VMs, first determine whether you would like to do a full, partial, or bootstrap teardown, specified below.
* Full: to teardown all the VMs running on your KVM host, run: "ansible-playbook teardown.yaml --ask-become-pass --tags full_teardown"
* Partial: To teardown all the VMS except for the bastion, run: "ansible-playbook teardown.yaml --ask-become-pass --tags partial_teardown"
* Bootstrap: The bootstrap is not needed after OpenShift fully installs and will be automatically brough down in the process of running the main playbook. To easily tear it down, run: "ansible-playbook teardown.yaml --ask-become-pass --tags boot_teardown"
* If you have provisioned more than the minimum number of nodes for your installation, add them to the
  respective list found in roles/teardown_vms/tasks/main.yaml.
* Once you run the full teardown, to start the main.yaml playbook back from that point, run:
  "run ansible-playbook main.yaml --ask-become-pass --tags "bastionvm,bastion,create_nodes"
* Once you run the partial teardown, to start the main.yaml playbook back from that point, run main.yaml with "--tags 'getocp,create_nodes'"

## Tags
If the process fails in error, you should be able to run the same shell command to start the process from the top. To be more selective with what parts of playbooks run, use tags. To determine what you part of a playbook or role you would like to run, open the file (either main.yaml or a role/tasks/main.yaml file) and look at the "tags: " section for a task and then use those tags when running the main playbook (examples below). 
* Examples: 
* ansible-playbook main.yaml --ask-become-pass --tags getocp (for one tag), or
* ansible-playbook main.yaml --ask-become-pass --tags 'bastion,get-ocp' (for multiple tags)

List of Tags (in alphabetical order):
* approve_certs = Tasks for approve_certs role
* bastion = Configuration of bastion
* bastionvm = Creation of Bastion KVM guest
* bootstrap = Creation of Boostrap KVM guest
* boot_teardown = Use with teardown.yaml to bring down the bootstrap
* check_nodes = Tasks for check_nodes role
* check_dns = Check DNS resolution
* compute = Creation of the compute nodes
* control = Creation of the control nodes
* create_nodes = Second set of KVM host's plays
* dns = Configuration of DNS server on bastion
* firewall = Configuration of firewall
* full_teardown = Use with teardown.yaml to bring down all KVM guests
* get-ocp = Prepare bastion for OCP
* haproxy = Configuration of load balancer on bastion
* httpd = Configuration of Apache server on bastion
* ssh-keygen = SSH key configuration and testing
* kvm_host = All KVM host tasks
* kvm_prep = First set of KVM host's tasks
* localhost = Tasks that apply to the local machine running Ansible
* partial_teardown = Use with teardown.yaml to bring down all VMs except bastion
* pkg = Install and update packages
* selinux = Tasks related to SELinux settings
* setup = First set of setup tasks on the localhost
* ssh = All SSH tasks
* ssh-agent = Setting up SSH agent
* ssh-copy-id = Copying SSH key to target
* subscription = Attach Red Hat Subscription
* verification = All OpenShift cluster verification tasks
* wait_for_bootstrap = Tasks for to wait_for_bootstrap role
* wait_for_cluster_operators = Tasks for wait_for_cluster_operators
* wait_for_install_complete = Tasks for wait_for_install_complete role