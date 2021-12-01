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
* The goal of this playbook is to automate the setup and deployment of a User Provisioned Infrastructure (UPI) OpenShift cluster on an IBM Z or LinuxONE mainframe utilizing Kernel Virtual Machine (KVM) as the virtualization method.
* This README file gives extremely detailed step-by-step instructions for you to use as a reference. It assumes near-zero experience with Ansible.

## Supported Operating Systems 
for local workstation running Ansible
* Linux (RedHat and Debian)
* MacOS X

## Pre-Requisites:
* An acvtive Red Hat account ([Sign Up](https://www.redhat.com/wapps/ugc/register.html?_flowId=register-flow&_flowExecutionKey=e1s1))
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
* On that LPAR, access to 8 (for a minimum installation) pre-allocated IPv4 addresses
* Fully Qualified Domain Names (FQDN) names for all IPv4 addresses 

## Installation Instructions:

### Setup:
* **Step 1: Get This Repository**
    * Navigate to a folder where you would like to store this project in your terminal
    * Run "git clone https://github.com/IBM/Ansible-OpenShift-Provisioning.git"
* **Step 2: Get Red Hat Info**
    * In a web browser, navigate to Red Hat's [customer portal](https://access.redhat.com/products/red-hat-enterprise-linux/), click on the 'Download Latest' button, use the drop-down to select Red Hat Enterprise Linux for IBM z Systems, select your desired version, make sure 'Architcture' is 's390x', and then scroll down to 'Red Hat Enterprise Linux X.X Update KVM Guest Image' and right click on 'Download Now' and copy link. Paste it into [env.yaml](env.yaml) as the variable 'env_rhel_qcow2'.
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
    * If all goes smoothly, this will take approximately 25 minutes.
    * To look at what is running in detail, open roles/'task-you-want-to-inspect'/tasks/main.yaml
    * If the process fails in error, you should be able to run the same shell command to start the process from the top. To be more selective with what parts of the main playbook run, use [tags](#Tags). See the [main playbook](main.yaml) to determine what part you would like to run and use those tags when running the [main playbook](main.yaml). Example: "ansible-playbook main.yaml --ask-become-pass --tags 'get-ocp,create_nodes'"
    * Note: we chose to not edit the user's .bash_profile/.bashrc with an automatic ssh-add command because that would change the user's local workstation set-up in a way that was potentially undesirable. Therefore, if you close out your terminal session in the middle of provisioning, you will need to run "ansible-playbook main.yaml --tags ssh-agent" before doing anything else.

### Verification
* **Step 6: Bootkube Verification**
    * SSH into the bastion (run "ssh root@your-bastion-IP-address-here" in the terminal)
    * Then SSH into the bootstrap as core ("ssh core@your-bootstrap-IP-address-here") 
    * Run "journalctl -u bootkube.service" to watch the bootstrap connect to the control nodes (hold spacebar to get to the bottom of the log). Press "q" to exit the log. 
    * Expect lots of errors in this log, as the control nodes may not be entirely up yet. 
    * This may take some time. Check in occassionally by running the above command again to update the log.
    * Once all control nodes are connected, the end of the bootkube log will read "bootkube.service complete".
* **Step 7: Export Kube Config**
    * Disconnect from bootstrap (Press "Ctrl+d")
    * Make sure you are connected to the bastion as root (if not, run "ssh root@your-bastion-IP-address-here")
    * Then run "export KUBECONFIG=/ocpinst/auth/kubeconfig"
    * Check that worked by running "oc whoami", which should return "system:admin"
    * If this doesn't work, just give it some time for the control nodes to connect and try again.
    * If you are getting "oc: command not found", disconnect from the bastion (press "Ctrl+d") and repeat this step.
* **Step 8: Approve Certificates**
    * From the bastion as root user (as above) run "oc get csr". This will bring up a list of certificates that need approval.
    * To approve all certificates at the same time, run the following command: 
      "for i in \`oc get csr --no-headers | grep -i pending |  awk '{ print $1 }\'`; do oc adm certificate approve $i; done" 
    * If you are viewing this file outside of GitHub, remove \ characters in the above command before running. The slashes are escape characters for formatting on GitHub.
    * It may take some time for all the certificates that need approval to show up. Keep running "oc get csr" to check to make sure that no new certificates have appeared since you last approved them.
    * Once all certificates read "Approved, Issued". You're ready for the next step.
* **Step 9: Wait for Cluster To Become Operational**
    * From the bastion, as root user (as above) check node status by running: "oc get nodes". All nodes need to be "Ready" in the "Status" column.
    * From the bastion, as root user (as above) run "oc get clusteroperators". All cluster operators need to be "True" in the "Available" column. If there are messages regarding revisions, give it some time and check back in a few minutes by running the same command again.
    * This may take some time, especially the cluster operators. Run the above two bullets' commmands to check-in occasionally.
    * Once all nodes are ready and cluster operators are available with no messages, you are ready to continue to the next step.
* **Step 10: Verify OpenShift Installation** 
    * Run "/ocpinst/openshift-install --dir=/ocpinst wait-for install-complete"
    * If installation is ready, running the above command will give you some information about how to log into the OpenShift cluster's dashboard.
    * Copy the provided URL into a web browser using the provided username (kubeadmin) and password for first time sign-on.
    * Congratulations! Your OpenShift cluster provisioning and installation is now complete.

* Optional: Leave the bootstrap running as is, shut it down and destroy it (Run "ansible-playbook teardown.yaml --ask-become-pass --tags boot_teardown"), or convert it into another compute node.

## Teardown: 
* If you would like to teardown your VMs, first determine whether you would like to do a full, partial, or bootstrap teardown, specified below.
* Full: to teardown all the VMs running on your KVM host, run: "ansible-playbook teardown.yaml --ask-become-pass --tags full_teardown"
* Partial: To teardown all the VMS except for the bastion, run: "ansible-playbook teardown.yaml --ask-become-pass --tags partial_teardown"
* Bootstrap: The bootstrap is not needed after OpenShift fully installs. To easily tear it down, run: "ansible-playbook teardown.yaml --ask-become-pass --tags boot_teardown"
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
* bastion = configuration of bastion for OCP
* bastionvm = creation of Bastion KVM guest
* bootstrap = creation of Boostrap KVM guest
* boot_teardown = for use with teardown.yaml to bring down the bootstrap
* compute = creation of the Compute nodes KVM guests
* control = creation of the Control nodes KVM guests
* create_nodes = tasks from the second set of kvm plays
* dns = configuration of DNS server on bastion
* firewall = for tasks related to firewall settings
* full_teardown = for use with teardown.yaml to bring down all VMs
* getocp = download of OCP installer and http server configuration
* haproxy = configuration of haproxy on bastion kvm guest
* httpd = configuration of httpd server on bastion kvm guest
* keymastr = ssh key configuration and testing
* kvm_host = tasks to apply to KVM host for OCP cluster
* kvm_prep = tasks from the first set of kvm plays
* localhost = for tasks that apply to the local machine running Ansible
* partial_teardown = for use with teardown.yaml to bring down all VMs except the bastion
* pkg = install and update all packages
* prep = run all setup playbooks
* selinux = for tasks related to SELinux settings
* setup = first-time setup of ansible
* ssh-agent = setting up ansible ssh-agent
* ssh-copy-id = for copying ssh id
* subscription = Attach Red Hat Subscription