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
* The goal of this playbook is to automate the setup and deployment of a User Provisioned Infrastructure (UPI) OpenShift cluster on an IBM Z or LinuxONE mainframe utilizing Kernel Virtual Machine (KVM) as the hypervisor.
* This README file gives extremely detailed step-by-step instructions for you to use as a reference. It assumes basic understanding of the command-line, but near-zero experience with Ansible itself.

## Supported Operating Systems 
(for local workstation running Ansible)
* Linux (RedHat and Debian)
* MacOS X

## Pre-Requisites
* A Red Hat account ([Sign Up](https://www.redhat.com/wapps/ugc/register.html?_flowId=register-flow&_flowExecutionKey=e1s1))
* A [license](https://access.redhat.com/products/red-hat-openshift-container-platform/) or [free trial](https://www.redhat.com/en/technologies/cloud-computing/openshift/try-it) of Red Hat OpenShift Container Platform for IBM Z systems - s390x architecture (OCP license comes with licenses for RHEL and CoreOS)
* Access to a logical partition (LPAR) on an IBM Z or LinuxONE mainframe, with at least:
    * 6 Integrated Facilities for Linux (IFLs) with SMT2 enabled
    * 85 GB of RAM
    * 1 TB of disk space mounted to /var/lib/libvirt/images
    * Red Hat Enterprise Linux (RHEL) 8.4 installed with networking configured and a user with sudo privileges created.
    * Access to 8 (for a minimum installation) pre-allocated IPv4 addresses
      * Note on DNS: The [main playbook](main.yaml) will create a DNS server on the bastion by default. If you plan to use a existing DNS server instead, when filling out the variables in [env.yaml](env.yaml) in Step 3, please make sure to mark `env.networking.dns.setup_on_bastion` to `false`. Either way, the playbook will double-check the DNS configuration before continuing.
* If you are using MacOS for your workstation running Ansible, you also need to have: 
    * [Homebrew](https://brew.sh/) package manager installed:
      ~~~
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      ~~~
    * Updated software for command line tools:
      ~~~
      softwareupdate --all --install
      ~~~
      ~~~
      xcode-select --install
      ~~~
* [Python3]((https://realpython.com/installing-python/)) and [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) intalled on your local workstation \
  * <u>Mac</u>:
    ~~~
    brew install python3
    ~~~
    ~~~
    brew install ansible
    ~~~
  * <u>Linux</u>:
    ~~~
    sudo apt install python3
    ~~~
    ~~~
    sudo apt install ansible
    ~~~
    * or (depending on your distribution),
    ~~~
    sudo yum install python3
    ~~~
    ~~~
    sudo yum install ansible
    ~~~

## Installation Instructions

### Setup
* **Step 1: Get This Repository**
    * In your terminal, navigate to a folder where you would like to store this project, copy/paste the following and hit Enter:
      ~~~
      git clone https://github.com/IBM/Ansible-OpenShift-Provisioning.git
      ~~~
* **Step 2: Get Red Hat Info**
    * In a web browser, navigate to Red Hat's [customer portal](https://access.redhat.com/products/red-hat-enterprise-linux/), click on the 'Download Latest' button, use the drop-down to select Red Hat Enterprise Linux for IBM z Systems, select your desired version, make sure 'Architcture' is 's390x', and then scroll down to 'Red Hat Enterprise Linux X.X Update KVM Guest Image' and click on 'Download Now'. 
    * See where it downloads, copy the path and paste it into [env.yaml](env.yaml) as the variable `env.redhat.path_to_qcow2`.
    * In a web browser, navigate to the Red Hat [console](https://console.redhat.com/openshift/install/ibmz/user-provisioned) and copy the OpenShift pull secret and paste it into [env.yaml](env.yaml) as the variable `env.redhat.pull_secret`.
* **Step 3: Set Variables**
    * In a text editor of your choice, open [env.yaml](env.yaml)
    * Fill out variables marked with `X` to match your specific installation. 
    * There are two sections of this file, separated by a comment block, which distinguishes variables that need to be filled in and variables that are pre-filled with defaults but can be altered if desired.
    * This is the most important step in the process. Take the time to make sure everything here is correct.
* **Step 4: Setup Script** 
    * Navigate to the folder where you cloned the Git Repository in your terminal.
    * Run this shell command:
      ~~~
      ansible-playbook setup.yaml
      ~~~
    * If you'd like to make any last changes to the [variables file](env.yaml), the [inventory](inventory) or the Ansible [configuration file](ansible.cfg), do so now.

### Provisioning
* **Step 5: Running the Main Playbook** 
    * Navigate to the folder where you cloned the Git repository in your terminal.
    * Start the main playbook by running this shell command: 
      ~~~
      ansible-playbook main.yaml
      ~~~
    * Watch Ansible as it completes the installation, correcting errors if they arise. 
    * To look at what is running in detail, open roles/'task-you-want-to-inspect'/tasks/main.yaml
    * If the process fails in error:
      * Go through the steps in the [troubleshooting](#Troubleshooting) section. 
      * Use [tags](#Tags) to selectively start from a certain point. See the [main playbook](main.yaml) to determine what part you would like to run and use those tags when running the [main playbook](main.yaml), for example: 
        ~~~
        ansible-playbook main.yaml --tags 'get_ocp,create_nodes'
        ~~~

### Post-Install Complete 
* **Step 6: First-Time Login**
    * The last step of the main playbook will print a URL, username and temporary password for first-time login.
    * Use a web-browser to type in the URL, which should take you to a sign-in page. Use the provided credentials to sign in.
    * Congratulations! Your OpenShift cluster installation is now complete.  

## Troubleshooting
If you encounter errors while running the main playbook, there are a few things you can do:
1) Double check your variables in [env.yaml](env.yaml).
2) Inspect the part that failed by opening `roles/role_name_to_inspect/tasks/main.yaml`
3) Google the specific error message.
3) Re-run the role indivually with [tags](#Tags) and the verbosity '-v' option to get more debugging information (more v's give more info). For example: 
    ~~~
    ansible-playbook main.yaml --ask-become-pass --tags get_ocp -vvv
    ~~~
4) Teardown troublesome KVM guests with [teardown](#Teardown) scripts and start again with [tags](#Tags). To start from the beginning, run: 
    ~~~
    ansible-playbook teardown.yaml --ask-become-pass --tags full
    ~~~
6) E-mail Jacob Emery at jacob.emery@ibm.com
7) If it's a problem with an OpenShift verification step, first re-reun the role with [tags](#Tags). If that doesn't work, SSH into the bastion as root ("ssh root@bastion-ip-address-here") and then run,"export KUBECONFIG=~/ocpinst/auth/kubeconfig" and then "oc whoami" and make sure it ouputs "system:admin". Then run the shell command from the role you would like to check on manually: i.e. 'oc get nodes', 'oc get co', etc.

## Teardown: 
* If you would like to teardown your VMs, first determine whether you would like to do a `full`, `partial`, or `app` teardown, specified below.
* `full`:
  * To teardown all the OpenShift KVM guest virtual machines (will not teardown KVM host or extra RHEL app VMs) run:
    ~~~
    ansible-playbook teardown.yaml --tags full
    ~~~
  * Start back again from the beginning by running
    ~~~
    ansible-playbook main.yaml
    ~~~
* `partial`: 
  * To teardown all OpenShift KVM guest virtual machines <i>except the bastion</i> (will also not teardown KVM host or extra RHEL app VMs) run:
    ~~~
    ansible-playbook teardown.yaml --tags partial
    ~~~ 
  * To start the main.yaml playbook back from that point, run:
    ~~~
    ansible-playbook main.yaml --tags 'get_ocp,create_nodes,verification'
    ~~~
* `app`:
  * To teardown only the extra RHEL VMs for non-cluster applications, run:
    ~~~
    ansible-playbook teardown.yaml --tags partial
    ~~~ 
  * To re-create those VMs, run:
    ~~~
    ansible-playbook main.yaml --tags app
    ~~~

## Tags
* To be more selective with what parts of playbooks run, use tags. 
* This is especially helpful for troubleshooting. 
* To determine what part of a playbook you would like to run, check the list below. Each [role](roles) has a corresponding tag. There are also some tags like "bastion" that cover multiple roles. To see these tags, see the [main playbook](main.yaml). Here's how to use the tags:
  * with one tag:
    ~~~
    ansible-playbook main.yaml --tags get_ocp
    ~~~
  * with multiple tags (enclose tags with single or double quotes, separate with commas):
    ~~~
    ansible-playbook main.yaml --tags 'bastion,get_ocp'
    ~~~

* <u>List of Tags</u>:
    * `approve_certs`: Tasks for approve_certs role
    * `app_setup`: Tasks related to setting up the extra RHEL VMs
    * `attach_subscription`: Auto-attach Red Hat subscription role
    * `bastion`: All bastion tasks
    * `bastion_setup`: Configuration of the bastion node, not including verification steps.
    * `check_nodes`: Tasks for check_nodes role
    * `check_dns`: Check DNS resolution
    * `check_ssh`: Check SSH role
    * `compute`: Creation of the compute nodes
    * `control`: Creation of the control nodes
    * `create_bastion`: Creation of bastion KVM guest
    * `create_bootstrap`: Creation of boostrap KVM guest
    * `create_nodes`: Second set of KVM host's plays
    * `dns`: Configuration of DNS server on bastion
    * `full`: Use with teardown.yaml to bring down all KVM guests
    * `get_ocp`: Prepare bastion for installing OpenShift
    * `haproxy`: Configuration of load balancer on bastion
    * `httpd`: Configuration of Apache server on bastion
    * `install_packages`: Install and update packages
    * `kvm_host`: All KVM host tasks
    * `kvm_prep`: First set of KVM host's tasks
    * `workstation`: Tasks that apply to the local machine running Ansible
    * `prep_kvm_guest`: Get Red Hat CoreOS kernel and initramfs on host
    * `partial`: Use with teardown.yaml to bring down all VMs except bastion
    * `set_selinux_permissive`: Tasks related to SELinux settings
    * `set_firewall`: Configuration of firewall
    * `setup`: First set of setup tasks on the workstation
    * `ssh`: All SSH tasks
    * `ssh_agent`: Setting up SSH agent
    * `ssh_copy_id`: Copying SSH key to target
    * `ssh_key_gen`: Ansible SSH keypair creation
    * `ssh_ocp_key_gen`: Generate SSH key pair for OpenShift on bastion
    * `verification`: All OpenShift cluster verification tasks
    * `wait_for_bootstrap`: Tasks for to wait_for_bootstrap role
    * `wait_for_cluster_operators`: Tasks for wait_for_cluster_operators
    * `wait_for_install_complete`: Tasks for wait_for_install_complete role