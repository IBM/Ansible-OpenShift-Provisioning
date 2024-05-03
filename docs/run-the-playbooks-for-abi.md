# Run the Playbooks
## Prerequisites 
* KVM host with root user access or user with sudo privileges.

## Note: 
* This playbook only support for single node cluster (SNO) on KVM using ABI.
* As of now we are supporting only macvtap for Agent based installation (ABI) on KVM

### Steps: 

## Step-1: Initial Setup for ABI
* Navigate to the [root folder of the cloned Git repository](https://github.com/IBM/Ansible-OpenShift-Provisioning) in your terminal (`ls` should show [ansible.cfg](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/ansible.cfg)).
* Update variables in Section (1 - 9) and Section 12 - OpenShift Settings 
* Update variables in Section - 19 ( Agent Based Installer ) in [all.yaml](https://github.com/veera-damisetti/Ansible-OpenShift-Provisioning/blob/main/inventories/default/group_vars/all.yaml.template) before running the playbooks.
* In case of SNO Section 9 ( Compute Nodes ) need to be comment or remove 
* First playbook to be run is 0_setup.yaml which will create inventory file for ABI and will add ssh key to the kvm host.

* Run this shell command:
```
ansible-playbook playbooks/0_setup.yaml
```

* Run each part step-by-step by running one playbook at a time, or all at once using [playbooks/master_playbook_for_abi.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/master_playbook_for_abi.yaml).
* Here's the full list of playbooks to be run in order, full descriptions of each can be found further down the page:
    * 0_setup.yaml ([code](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/0_setup.yaml))
    * 3_setup_kvm_host.yaml ([code](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/3_setup_kvm_host.yaml))
    * 4_create_bastion.yaml ([code](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/4_create_bastion.yaml))
    * 5_setup_bastion.yaml ([code](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/5_setup_bastion.yaml))
    * create_abi_cluster.yaml ([code](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/create_abi_cluster.yaml))
   
* Watch Ansible as it completes the installation, correcting errors if they arise.
* To look at what tasks are running in detail, open the playbook or roles/role-name/tasks/main.yaml
* Alternatively, to run all the playbooks at once, start the master playbook by running this shell command:

```shell
ansible-playbook playbooks/master_playbook_for_abi.yaml
```

* If the process fails in error, go through the steps in the [troubleshooting](troubleshooting.md) page.

## Step-2: Setup Playbook (0_setup.yaml)
### Overview
First-time setup of the Ansible Controller, the machine running Ansible.
### Outcomes
* Packages and Ansible Galaxy collections are confirmed to be installed properly.
* host_vars files are confirmed to match KVM host(s) hostnames.
* Ansible inventory is templated out and working properly.
* SSH key generated for Ansible passwordless authentication.
* SSH agent is setup on the Ansible Controller.
* Ansible SSH key is copied to the file server.
### Notes
* You can use an existing SSH key as your Ansible key, or have Ansible create one for you. It is highly recommended to use one without a passphrase.

## Step-3: Setup KVM Host Playbook (3_setup_kvm_host.yaml)
### Overview
Configures the RHEL server(s) installed natively on the LPAR(s) to act as virtualization hypervisor(s) to host the virtual machines that make up the eventual cluster.
### Outcomes
* Ansible SSH key is copied to all KVM hosts for passwordless authentication.
* RHEL subscription is auto-attached to all KVM hosts.
* Software packages specified in group_vars/all.yaml have been installed.
* Cockpit console enabled for Graphical User Interface via web browser. Go to http://kvm-ip-here:9090 to view it.
* Libvirt is started and enabled.
* Logical volume group that was created during kickstart is extended to fill all available space.
* A macvtap bridge has been created on the host's networking interface.
### Notes
* If you're using a pre-existing LPAR, take a look at roles/configure_storage/tasks/main.yaml to make sure that the commands that will be run to extend the logical volume will work. Storage configurations can vary widely. The values there are the defaults from using autopart during kickstart. Also be aware that if lpar.storage_group_2.auto_config is True, the role roles/configure_storage/tasks/main.yaml will be non-idempotent. Meaning, it will fail if you run it twice.

## Step-4: Create Bastion Playbook (4_create_bastion.yaml)
### Overview
Creates the bastion KVM guest on the first KVM host. The bastion hosts essential services for the cluster. If you already have a bastion server, that can be used instead of running this playbook.
### Outcomes
* Bastion configs are templated out to the file server.
* Bastion is booted using virt-install.
* Bastion is kickstarted for fully automated setup of the operating system.
### Notes
* This can be a particularly sticky part of the process.
* If any of the variables used in the virt-install or kickstart are off, the bastion won't be able to boot.
* Recommend watching it come up from the first KVM host's cockpit. Go to http://kvm-ip-here:9090 via web-browser to view it. You'll have to sign in, enable administrative access (top right), and then click on the virtual machines tab on the left-hand toolbar.
## Step-5: Setup Bastion Playbook (5_setup_bastion.yaml)
### Overview
Configuration of the bastion to host essential infrastructure services for the cluster. Can be first-time setup or use an existing server.
### Outcomes
* Ansible SSH key copied to bastion for passwordless authentication.
* Software packages specified in group_vars/all.yaml have been installed.
* An OCP-specific SSH key is generated for passing into the install-config (then passed to the nodes).
* Firewall is configured to permit traffic through the necessary ports.
* Domain Name Server (DNS) configured to resolve cluster's IP addresses and APIs. Only done if env.bastion.options.dns is true.
* DNS is checked to make sure all the necessary Fully Qualified Domain Names, including APIs resolve properly. Also ensures outside access is working.
* High Availability Proxy (HAProxy) load balancer is configured. Only done if env.bastion.options.loadbalancer.on_bastion is true.
* If the the cluster is to be highly available (meaning spread across more than one LPAR), an OpenVPN server is setup on the bastion to allow for the KVM hosts to communicate between eachother. OpenVPN clients are configured on the KVM hosts.
* CoreOS roofts is pulled to the bastion if not already there.
* OCP client and installer are pulled down if not there already.
* oc, kubectl and openshift-install binaries are installed.
* OCP install-config is templated and backed up. In disconnected mode, if platform is mirrored (currently only legacy), image content source policy and additionalTrustBundle is also patched.
* Manfifests are created.
* OCP install directory found at /root/ocpinst/ is created and populated with necessary files.
* Ignition files for the bootstrap, control, and compute nodes are transferred to HTTP-accessible directory for booting nodes.
### Notes
* The stickiest part is DNS setup and get_ocp role at the end.

## Step-6: Master Playbook (master_playbook_for_abi)
### Overview
* Use this playbook to run all required 5 playbooks (0_setup, 3_setup_kvm_host,4_create_bastion, 5_setup_bastion, create_abi_cluster) at once.
### Outcomes
* Same as all the above outcomes for all required playbooks.
* At the end you will have an OpenShift cluster deployed and first-time login credentials.

# Destroy ABI Cluster

### Overview
* Destroy the ABI Cluster and other resources created as part of installation

### Procedure
* Run the playbook [destroy_abi_cluster.yaml](https://github.com/isumitsolanki/Ansible-OpenShift-Provisioning/blob/abi_ha_kvm/playbooks/destroy_abi_cluster.yaml) to destroy all the resources created while installation
```
ansible-playbook playbooks/destroy_abi_cluster.yaml
```

## destroy_abi_cluster Playbook
### Overview
* Delete all the resources on ABI Cluster.
* Destroy the Bastion, Compute and Control Nodes.
### Outcomes
* Monitors Deletion Of Compute Machines and Control Machines.
* Destroys VMs of Bastion and Compute and Control.

## Test Playbook (test.yaml)
### Overview
* Use this playbook for your testing purposes, if needed.
