# Ansible-OpenShift-Provisioning

## Scope

The goal of this playbook is to setup and deploy an OpenShift cluster utilizing KVM as the virtualization method.

## Supported operating systems for the localhost (the starting workstation) are: 
* Linux (RedHat and Debian families)
* Unix and Unix-like (i.e. MacOS X)

## Pre-requisites:

* Python3 intalled on your local computer [how-to:] (https://realpython.com/installing-python/)
* Ansible installed on your local computer  [how-to:] (https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
* If you are using Mac OS X for your localhost workstation to run Ansible, you need to have: 
    * homebrew package manager installed ( how-to: https://brew.sh/ )
    * Updated software for command line tools ( run "softwareupdate --all --install" in your terminal )
* A logical partition (LPAR) on an IBM Z or LinuxONE mainframe, with at least:
    * 6 Integrated Facilities for Linux (IFLs)
    * 75 GB of RAM
    * 1 TB of disk space
* On that LPAR, bare-metal Red Hat Enterprise Linux (RHEL) 8.4 with Kernel Virtual Machine (KVM) installed
* On that LPAR, access to 8 (for a minimum installation) pre-allocated IPv4 addresses
* Fully Qualified Domain Names (FQDN) names for all IPv4 addresses

## When you are ready:

* Step 1: Download this Git repository to a folder on your local computer
* Step 2: Go to <https://console.redhat.com/openshift/install/ibmz/user-provisioned> to:
     * download your local command line tools (oc and kubectl)
     * OpenShift pull secret (for inputting it into env.yaml)
* Step 2: Fill out the required variables for your specific installation in the env.yaml file
* Step 3: Get DNS configuration files (forward (.db), reverse (.rev), and named.conf configuration files) or have it pre-defined by your networking team. And place them in the roles/dns/files folder.
* Step 4: Run the appropriate Ansible setup shell script, which can be found in the main directory. While in the main directory, run "./ansible-setup-mac.sh" or "./ansible-setup-linux.sh" depending on your operating system to download the required Ansible modules and packages.
* Step 5: Navigate to the folder where you saved the Git Repository and execute the main playbook by running this shell command: "ansible-playbook main.yaml --ask-become-pass". Watch Ansible as it completes the installation, correcting errors if they arise. If the process fails in error, you should be able to run the same shell command to start the process from the top. Alternatively, use tags to run only the tasks that have that tag. See list of tags below for reference.
* Step 6: Once the create_bastion playbook runs, open the cockpit at <https://<your kvm_host IP address>:9090>, go to the "Virtual Machines" tab, and complete the bastion's installation with these options:
        - list options here
        - list options here
        - list options here
* Step 7: When the playbooks for creating nodes run, watch them on the cockpit at "https://<your kvm_host IP address>:9090". Go to the "Virtual Machines" tab and click on the VM you created. Once the operating system installs, it will power down. Click the blue "Run" button to start it back up. It will then run some more setup. Then, when you see "<node-name> login" come back to the terminal here where you ran ansible and press "ctrl-C" and then "C" to continue. If you do not see the login prompt, press "ctrl+C" and then "A" to stop the process.
* Step 8: Repeat Step 7 with the Bootstrap and Control nodes. Then, SSH into the bastion (run "ssh <your bastion IP address>" in the terminal). From there, change to root user (run "su root"). Then ssh into the bootstrap ("ssh core@<your bootstrap IP address>") and run "journalctl -u bootkube.service" to watch the bootstrap connect to the control nodes (hold space to get to the bottom of the log). Expect lots of errors, as all the nodes may not be entirely up yet. Once all control nodes are connected, the bootkube log will read "bootkube.service complete".
* Step 9: Repeat Step 7 with the Compute nodes. 
* Step 10: Once all the Compute nodes up and prompting login, log in to the bastion and run "export KUBECONFIG=/ocpinst/auth/kubeconfig". Then run "oc get csr". It will bring up a list of certificates that need approval. For each cert that is "Pending", run "oc adm certiciate approve <csr name>". The csr names will be something like "csr-v8qqv". Once you approve all the certificates, double check that there are not more that have appeared by running "oc get csr" again. Once all certs are "Approved, Issued". You're ready for the next step.
* Step 11: From the bastion, run "oc get nodes". Once all nodes are "Ready", run "oc get clusteroperators". Wait for them to all read "True" under the "Available" column. This may take hours.
* Step 8: Verify installation by running: "./openshift-install --dir=/ocpinst wait-for install-complete"
* Step 9: Running the command in the above step will give you some information about how to log into the OpenShift cluster's dashboard. Copy the URL into a web browser and use the provided "kubeadmin" login and password for first time sign-on.
* Step 10: Celebrate! Your OpenShift cluster installation is complete.

* Optional: Leave the bootstrap running as is, shut it down and destroy it, or convert it into a compute node.

## Tags:

* setup = first-time setup of ansible
* prep = run all setup playbooks
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
