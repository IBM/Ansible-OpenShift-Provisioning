# Ansible-OpenShift-Provisioning

## Scope

* The goal of this playbook is to setup and deploy a User Provisioned Infrastructure (UPI) OpenShift cluster on an
  IBM Z or LinuxONE mainframe utilizing KVM as the virtualization method.
* This README file gives an extremely detailed step-by-step instruction for you to use as a reference. It assumes near zero experience.

## Supported Operating Systems (for local workstation): 

* Linux (RedHat and Debian)
* MacOS X

## Pre-requisites:

* Python3 intalled on your local computer (how-to: https://realpython.com/installing-python/)
* Ansible installed on your local computer  (how-to: https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
* If you are using Mac OS X for your localhost workstation to run Ansible, you also need to have: 
    * homebrew package manager installed (how-to: https://brew.sh/)
    * Updated software for command line tools (run "softwareupdate --all --install" in your terminal)
* Access to a logical partition (LPAR) on an IBM Z or LinuxONE mainframe, with at least:
    * 6 Integrated Facilities for Linux (IFLs)
    * 75 GB of RAM
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
* DNS configuration files (forward (.db), reverse (.rev), and named.conf). Note: we plan to automate this in the future.

## Installation Instructions:

### Setup:
* **Step 1: Get This Repository**
    * Navigate to a folder where you would like to store this project in your terminal
    * Run "git clone https://github.com/IBM/Ansible-OpenShift-Provisioning.git"
* **Step 2: Get OpenShift Information**
    * In a web browser, navigate to https://console.redhat.com/openshift/install/ibmz/user-provisioned in order to:
    * Download your local command line tools (oc and kubectl)
    * Copy the OpenShift pull secret (for use in the next step)
* **Step 2: Set Variables**
    * In a text editor of your choice, open env.yaml, found in the main directory of this repository
    * Fill out all of the required variables for your specific installation
* **Step 3: DNS Configuration**
    * Get DNS configuration files (forward (.db), reverse (.rev), and named.conf), or have them pre-defined by
      your networking team, and place them in the roles/dns/files folder.
* **Step 4: Setup Script** 
    * Navigate to the folder where you saved the Git Repository
    * Depending on which operating system you are using on your local workstation, run either
      "ansible-playbook setup-mac.yaml --ask-become-pass" or "ansible-playbook setup-linux.yaml --ask-become-pass" 

### Provisioning
* **Step 5: Running the Main Playbook** 
    * If you are not already there, navigate to the folder where you saved the Git Repository in your terminal
    * Execute the main playbook by running this shell command: "ansible-playbook main.yaml --ask-become-pass"
    * Watch Ansible as it completes the installation, correcting errors if they arise. 
    * If the process fails in error, you should be able to run the same shell command to start the process from the top. 
    * Alternatively, use tags to run only the tasks that have that tag. See main.yaml to determine what you would like 
      to run. There is also a list of all the tags at the bottom of this page for reference.
* **Step 6: Bastion Configuration** 
    * Once the create_bastion task runs, it will pause the playbook to give you time to configure it.
    * Use a web browser to open the cockpit by going to: "https://your-KVM-host-IP-address-here:9090"
    * Click on the "Virtual Machines" tab, then click on bastion from the list, click on the black terminal 
      screen and press Enter. Complete its installation with these options enabled:
        * server
        * hardware monitoring utilities
        * networking file system client
        * remote management for linux
        * headless mgmt
        * system tools
        * basic web server
        * network servers
    * Once you fill out all the required configuration settings, press "b" to begin installation.
    * Once you see "bastion login", come back to the terminal to continue your run by pressing "ctrl+c" and then
      "c". If there was a problem and you need to stop the playbook, press "ctrl+c" and then "a".
    * Note: we plan to automate the installation configuration in the future.
* **Step 7: Starting Up Bootstrap and Control Nodes**
    * The playbook will continue to run, preparing the bootstrap and control nodes.
    * To monitor the nodes as they come up, watch them on the cockpit at: "https://your-KVM-host-IP-address-here:9090"
    * Click on the "Virtual Machines" tab and then click on the VM you want to monitor. Click on the black 
      terminal screen and press Enter.
    * Once you see "node-name login" prompt come back to the terminal where you ran Ansible and press "ctrl+c" and 
      then "c" to continue running the playbook. 
    * If you encounter an error that does not resolve with time, press "ctrl+c" and then "a" to stop the process and debug.
* **Step 8: Bootkube Verification**
    * SSH into the bastion (run "ssh your-bastion-IP-address-here" in the terminal)
    * From there, change to root user (run "su root") and type in the root password that you set during configuration
    * Then SSH into the bootstrap as core ("ssh core@your-bootstrap-IP-address-here") 
    * Run "journalctl -u bootkube.service" to watch the bootstrap connect to the control nodes (hold spacebar to 
      get to the bottom of the log). Press "q" to exit the log. 
    * Expect lots of errors, as the control nodes may not be entirely up yet. 
    * This may take some time, 30 minutes or more. Check in occassionally by running "journalctl -u bootkube.service" again
      to update the log. Remember to hold the spacebar to go to the bottom, press "q" to quit.
    * Once all control nodes are connected, the bootkube log will read "bootkube.service complete".
* **Step 9: Starting Up Compute Nodes**  
    * Repeat Step 7 with the Compute nodes. 
    * Monitor their status at the cockpit, found at "https://your-KVM-host-IP-address:9090"
    * They are ready once their terminal screen shows a login prompt
    * Once all your compute nodes are up and running, and bootkube is complete, you are ready for cluster verification

### Verification
* **Step 10: Export Kube Config**
    * SSH into the bastion (run "ssh your-bastion-IP-address-here")
    * Change to root user (run "su root") and type in your password from when you configured the bastion.
    * Then run "export KUBECONFIG=/ocpinst/auth/kubeconfig"
    * Check that worked by running "oc whoami", which should return "system:admin"
* **Step 11: Approve Certificates**
    * Fromm the bastion, running as root user (as above) run "oc get csr". This will bring up a list of certificates that need approval.
    * To approve all certificates at the same time, run the following command: 
      "for i in `oc get csr --no-headers | grep -i pending |  awk '{ print $1 }'`; do oc adm certificate approve $i; done" 
    * It may take some time for all the certificates that need approval to show up. Keep running "oc get csr" to check to make sure that 
      no new certificates have appeared since you last approved them.
    * Once all certificates read "Approved, Issued". You're ready for the next step.
* **Step 11: Wait for Cluster To Become Operational**
    * From the bastion, as root user (as above) check node status by running: "oc get nodes". All nodes need to be "Ready" in the "Status" column.
    * From the bastion, as root user (as above) run "oc get clusteroperators". All cluster operators need to be "True" in the "Available" column.
    * It may take hours, especially the cluster operators. Run the above two bullets' commmands to check in occasionally.
    * Once all nodes are ready and cluster operators are available, you are ready to continue to the next step.
* **Step 12: Verify OpenShift Installation** 
    * From the bastion as root user (as above), run: "./openshift-install --dir=/ocpinst wait-for install-complete"
    * If installation is ready, running the above command will give you some information about how to log into the OpenShift cluster's dashboard. 
    * Copy the provided URL into a web browser and use the provided "kubeadmin" login and password for first time sign-on.
* **Step 14: Celebrate!**
    * Your OpenShift cluster provisioning and installation is now complete.

* Optional: Leave the bootstrap running as is, shut it down and destroy it, or convert it into a compute node.

## Teardown: 

* If you would like to teardown your VMs, first determine whether you would like to do a full or partial teardown.
* Full: to teardown all the VMs running on your KVM host, run: "ansible-playbook teardown.yaml --ask-become-pass --tags "full"
* Partial: To teardown all the VMS except for the bastion, run: "ansible-playbook teardown.yaml --ask-become-pass --tags "partial"
* If you have provisioned more than the minimum number of nodes for your installation, add them to the
  respective list found in roles/teardown_vms/tasks/main.yaml.
* Once you run the full teardown, to start the main.yaml playbook back from that point, run:
  "run ansible-playbook main.yaml --ask-become-pass --tags "bastionvm,bastion,create_nodes"
* Once you run the partial teardown, to start the main.yaml playbook back from that point, run main.yaml with the tags "bastion,create_nodes".

## Tags:

* setup = first-time setup of ansible
* prep = run all setup playbooks
* pkg = install and update all packages
* bastion = configuration of bastion for OCP
* keymastr = ssh key configuration and testing
* bastionvm = creation of Bastion KVM guest
* boostrap = creation of Boostrap KVM guest
* compute = creation of the Compute nodes KVM guests
* control = creation of the Control nodes KVM guests
* ssh-copy-id = for copying ssh id
* dns = configuration of dns server on bastion
* getocp = download of OCP installer and http server configuration
* haproxy = configuration of haproxy on bastion kvm guest
* httpconf = configuration of httpd server on bastion kvm guest
* kvm_host = tasks to apply to KVM host for OCP cluster
* kvm_prep = tasks from the first set of kvm plays
* create_nodes = tasks from the second set of kvm plays
* localhost = for tasks that apply to the local machine running Ansible
* firewall = for tasks related to firewall settings
* selinux = for tasks related to SELinux settings
* partial = for use with teardown.yaml to bring down VMs except bastion
* full = for use with teardown.yaml to bring down all VMs
