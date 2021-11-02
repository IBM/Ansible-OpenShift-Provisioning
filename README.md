# Ansible-OpenShift-Provisioning

## Table of Contents
* [Scope](#Scope)
* [Supported Operating Systems](#Supported-Operating-Systems)
* [Pre-Requisites](#Pre-Requisites)
* [Instructions](#Installation-Instructions)
* [Setup](#Setup)
* [Provisioning](#Provisioning)
* [Verification](#Verification)
* [Teardown](#Teardown)
* [Tags](#Tags)

## Scope
* The goal of this playbook is to setup and deploy a User Provisioned Infrastructure (UPI) OpenShift cluster on an IBM Z or LinuxONE mainframe utilizing KVM as the virtualization method.
* This README file gives extremely detailed step-by-step instructions for you to use as a reference. It assumes near zero experience with Ansible.

## Supported Operating Systems 
for local workstation running Ansible
* Linux (RedHat and Debian)
* MacOS X

## Pre-Requisites:
* Red Hat Enterprise Linux (RHEL) license or free trial
* Red Hat OpenShift Container Platform license or free trial
* Python3 intalled on your local computer (how-to: https://realpython.com/installing-python/)
* Ansible installed on your local computer (how-to: https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
* If you are using Mac OS X for your localhost workstation to run Ansible, you also need to have: 
    * homebrew package manager installed (how-to: https://brew.sh/)
    * Updated software for command line tools (run "softwareupdate --all --install" in your terminal)
* Access to a logical partition (LPAR) on an IBM Z or LinuxONE mainframe, with at least:
    * 6 Dedicated Integrated Facilities for Linux (IFLs)
    * 85 GB of RAM
    * 1 TB of disk space
* On that LPAR, bare-metal Red Hat Enterprise Linux (RHEL) 8.4 with Kernel Virtual Machine (KVM) installed with
  the following options enabled:
    * server
    * hardware monitoring utilities
    * networking file system client
    * remote management for linux
    * virtualization hypervisor
    * headless management
    * system tools
* On that LPAR, access to 8 (for a minimum installation) pre-allocated IPv4 addresses
* Fully Qualified Domain Names (FQDN) names for all IPv4 addresses
* DNS configuration files (forward (.db), reverse (.rev), and named.conf). 

## Installation Instructions:

### Setup:
* **Step 1: Get This Repository**
    * Navigate to a folder where you would like to store this project in your terminal
    * Run "git clone https://github.com/IBM/Ansible-OpenShift-Provisioning.git"
* **Step 2: Get OpenShift Information**
    * In a web browser, navigate to https://console.redhat.com/openshift/install/ibmz/user-provisioned
    * Download your local command line tools (oc and kubectl)
    * Copy the OpenShift pull secret (for use in the next step)
* **Step 3: Set Variables**
    * In a text editor of your choice, open [env.yaml](env.yaml)
    * Fill out all of the required variables for your specific installation
* **Step 4: DNS Configuration**
    * Get DNS configuration files (forward (.db), reverse (.rev), and named.conf), or have them pre-defined by your networking team.
    * Place them in the [roles/dns/files folder](roles/dns/files) 
    * Please leave the named.conf the same name.
    * Rename the .db and .rev files with the same name you set for "env_metadata_name" in [env.yaml](env.yaml) (i.e. distribution.rev)
* **Step 5: Setup Script** 
    * Navigate to the folder where you saved the Git Repository
    * Run "ansible-playbook setup.yaml --ask-become-pass"
    * When the setup playbook starts, it will prompt you for a password to use for encrypting Ansible vault files
    * No files are encrypted until you run the [main playbook](main.yaml) in step 5 below
    * If you would like to decrypt a file protected by Ansible vault, run: "ansible-vault decrypt file-name-here"

### Provisioning
* **Step 6: Running the Main Playbook** 
    * If you are not already there, navigate to the folder where you saved the Git repository in your terminal
    * Execute the main playbook by running this shell command: "ansible-playbook main.yaml --ask-become-pass"
    * Watch Ansible as it completes the installation, correcting errors if they arise. 
    * To look at what is running in detail, from the main directory open roles/'task-you-want-to-inspect'/tasks/main.yaml
    * If the process fails in error, you should be able to run the same shell command to start the process from the top. To be more selective with what parts of the main playbook run, use [tags](#Tags). See the [main playbook](main.yaml) to determine what part you would like to run and use those tags when running the [main playbook](main.yaml). Example: "ansible-playbook main.yaml --ask-become-pass -- tags 'bastion,get-ocp'
    * Note: we chose to not edit the user's .bash_profile/.bashrc with an automatic ssh-add command because that would change the user's local workstation set-up in a way that was undesirable. Therefore, if you close out your terminal session in the middle of provisioning, you will need to run "ansible-playbook main.yaml --tags ssh-agent" before doing anything else.
* **Step 7: Bastion Configuration** 
    * Once the [create_bastion](roles/create_bastion/tasks/main.yaml) task runs, it will pause the playbook to give you time to configure it.
    * Use a web browser to open the cockpit by going to: "https://your-KVM-host-IP-address-here:9090"
    * Click on the "Virtual Machines" tab, then click on bastion from the list, click on the black terminal screen and press Enter. Wait until you see it asking for you to make a selection.
    * To finish the bastion's installation, you will need to configure the VM by doing the following:
      * Press 2 to enter Text Mode (hit the Enter key after every step)
      * From the main menu, press 3 to configure the Installation Source
        * Press 3 to use Network
        * Type in the URL that points to your RHEL ISO
      * From the main menu, press 4 to go to Software Selection
        * Press 2 for Server, Enter, then "c" to continue
        * From this list, press the number and then hit Enter for each:
          * 1 - Hardware Monitoring utilities
          * 8 - Networking File System Client
          * 9 - Network Servers
          * 11 - Remote Management for Linux
          * 13 - Basic Web Server
          * 17 - Headless Management
          * 21 - System Tools
        * Press "c" to continue, and 'c' again to get back to the main menu
      * From the main menu, press 5 to set the installation destination
        * If there is a disk already checked, press "c" to use the continue. If not, select the disk you would like to use.
        * If it is not already selected, press 2 to use all free space, otherwise, press "c" to continue.
        * Select "LVM" from the list and press "c" to continue
      * From the main menu, press 7 to set Network Configurations
        * Press 2 to configure device enc1
          * Press 1 and enter the bastion's IP address
          * Press 2 and enter the netmask
          * Press 3 and enter the default gateway
          * Press 4 and type "ignore"
          * Press 6 and enter DNS nameservers
          * Press 'c' to continue 
      * From the main menu, press 9 to set the Root Password
      * From the main menu, press 10 to create a user
        * Press 1 to create user
        * Press 2 to set full name
        * Press 3 to set a username
        * Press 5 to set a password
        * Press 6 to give the user root access (optional)
      * From the main menu, double check that all check boxes have an X
    * Once you fill out all the required configuration settings, press "b" to begin installation.
    * Wait for the installation to complete, this may take some time. Monitor its progress, it may need you to press 'Enter' to continue. Once the installation completes, you will have to press the 'Run' button on the cockpit for it to start up and finish configuration.
    * Once you see "bastion login", come back to the terminal to continue your run by pressing "ctrl+c" and then "c". 
    * If there was a problem and you need to stop the playbook, press "ctrl+c" and then "a" to Abort. If configuration and installation took longer than the pause and the playbook continued and then failed, continue the playbook by running the following command: "ansible-playbook main.yaml --ask-become-pass --tags 'bastion,create_nodes'"
* **Step 8: Starting Up Bootstrap and Control Nodes**
    * The playbook will continue to run, preparing the bootstrap and control nodes.
    * To monitor the nodes as they come up, watch them on the cockpit at: "https://your-KVM-host-IP-address-here:9090"
    * Click on the "Virtual Machines" tab and then click on the VM you want to monitor. Click on the black 
      terminal screen and press Enter.
    * Once you see "'node-name' login" prompt come back to the terminal where you ran Ansible and press "ctrl+c" and 
      then "c" to continue running the playbook. 
    * If you encounter an error that does not resolve with time, press "ctrl+c" and then "a" to stop the process and debug.
* **Step 9: Bootkube Verification**
    * SSH into the bastion (run "ssh your-bastion-IP-address-here" in the terminal)
    * From there, change to root user (run "su root") and type in the root password that you set during bastion configuration
    * Then SSH into the bootstrap as core ("ssh core@your-bootstrap-IP-address-here") 
    * Run "journalctl -u bootkube.service" to watch the bootstrap connect to the control nodes (hold spacebar to 
      get to the bottom of the log). Press "q" to exit the log. 
    * Expect lots of errors, as the control nodes may not be entirely up yet. 
    * This may take some time, 30 minutes or more. Check in occassionally by running "journalctl -u bootkube.service" again
      to update the log. Remember to hold the spacebar to go to the bottom, press "q" to quit.
    * Once all control nodes are connected, the bootkube log will read "bootkube.service complete".
* **Step 10: Starting Up Compute Nodes**  
    * Repeat Step 7 with the Compute nodes. 
    * Monitor their status at the cockpit, found at "https://your-KVM-host-IP-address:9090"
    * They are ready once their terminal screen shows a login prompt
    * Once all your compute nodes are up and running, and bootkube is complete, you are ready for cluster verification

### Verification
* **Step 11: Export Kube Config**
    * SSH into the bastion (run "ssh your-bastion-IP-address-here")
    * Change to root user (run "su root") and type in your password from when you configured the bastion.
    * Then run "export KUBECONFIG=/ocpinst/auth/kubeconfig"
    * Check that worked by running "oc whoami", which should return "system:admin"
* **Step 12: Approve Certificates**
    * From the bastion, running as root user (as above) run "oc get csr". This will bring up a list of certificates that need approval.
    * To approve all certificates at the same time, run the following command: 
      "for i in \`oc get csr --no-headers | grep -i pending |  awk '{ print $1 }\'`; do oc adm certificate approve $i; done" 
    * It may take some time for all the certificates that need approval to show up. Keep running "oc get csr" to check to make sure that 
      no new certificates have appeared since you last approved them.
    * Once all certificates read "Approved, Issued". You're ready for the next step.
* **Step 13: Wait for Cluster To Become Operational**
    * From the bastion, as root user (as above) check node status by running: "oc get nodes". All nodes need to be "Ready" in the "Status" column.
    * From the bastion, as root user (as above) run "oc get clusteroperators". All cluster operators need to be "True" in the "Available" column.
    * It may take hours, especially the cluster operators. Run the above two bullets' commmands to check in occasionally.
    * Once all nodes are ready and cluster operators are available, you are ready to continue to the next step.
* **Step 14: Verify OpenShift Installation** 
    * From the bastion as root user (as above), navigate to /ocpinst ("cd /ocpinst")
    * Run "./openshift-install --dir=/ocpinst wait-for install-complete"
    * If installation is ready, running the above command will give you some information about how to log into the OpenShift cluster's dashboard. 
    * Copy the provided URL into a web browser and use "kubeadmin" as login and the provided password for first time sign-on.
* **Step 15: Celebrate!**
    * Your OpenShift cluster provisioning and installation is now complete.

* Optional: Leave the bootstrap running as is, shut it down and destroy it, or convert it into a compute node.

## Teardown: 
* If you would like to teardown your VMs, first determine whether you would like to do a full or partial teardown.
* Full: to teardown all the VMs running on your KVM host, run: "ansible-playbook teardown.yaml --ask-become-pass --tags full"
* Partial: To teardown all the VMS except for the bastion, run: "ansible-playbook teardown.yaml --ask-become-pass --tags partial"
* If you have provisioned more than the minimum number of nodes for your installation, add them to the
  respective list found in roles/teardown_vms/tasks/main.yaml.
* Once you run the full teardown, to start the main.yaml playbook back from that point, run:
  "run ansible-playbook main.yaml --ask-become-pass --tags "bastionvm,bastion,create_nodes"
* Once you run the partial teardown, to start the main.yaml playbook back from that point, run main.yaml with the tags "bastion,create_nodes".

## Tags
* If the process fails in error, you should be able to run the same shell command to start the process from the top. To be more selective with what parts of playbooks run, use tags. Open a playbook and look at the "tags: " section under hosts for each play to determine what you part you would like to run and then use those tags when running the main playbook. 
Examples: 
ansible-playbook main.yaml --ask-become-pass --tags getocp (for one tag), or
ansible-playbook main.yaml --ask-become-pass --tags 'bastion,get-ocp' (for multiple tags)

In alphabetical order:
* bastion = configuration of bastion for OCP
* bastionvm = creation of Bastion KVM guest
* boostrap = creation of Boostrap KVM guest
* compute = creation of the Compute nodes KVM guests
* control = creation of the Control nodes KVM guests
* create_nodes = tasks from the second set of kvm plays
* dns = configuration of DNS server on bastion
* firewall = for tasks related to firewall settings
* full = for use with teardown.yaml to bring down all VMs
* getocp = download of OCP installer and http server configuration
* haproxy = configuration of haproxy on bastion kvm guest
* httpconf = configuration of httpd server on bastion kvm guest
* keymastr = ssh key configuration and testing
* kvm_host = tasks to apply to KVM host for OCP cluster
* kvm_prep = tasks from the first set of kvm plays
* localhost = for tasks that apply to the local machine running Ansible
* partial = for use with teardown.yaml to bring down VMs except bastion
* pkg = install and update all packages
* prep = run all setup playbooks
* selinux = for tasks related to SELinux settings
* setup = first-time setup of ansible
* ssh-agent = setting up ansible ssh-agent
* ssh-copy-id = for copying ssh id