# Step 4: Run the Playbooks
## Overview
* Navigate to the [root folder of the cloned Git repository](https://github.com/IBM/Ansible-OpenShift-Provisioning) in your terminal (`ls` should show [ansible.cfg](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/ansible.cfg)).
* Run this shell command:
```
ansible-playbook playbooks/0_setup.yaml
```

* Run each part step-by-step by running one playbook at a time, or all at once using [playbooks/site.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/site.yaml).
* Here's the full list of playbooks to be run in order, full descriptions of each can be found further down the page:
    * 0_setup.yaml ([code](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/0_setup.yaml))
    * 1_create_lpar.yaml ([code](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/1_create_lpar.yaml))
    * 2_create_kvm_host.yaml ([code](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/2_create_kvm_host.yaml))
    * 3_setup_kvm_host.yaml ([code](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/3_setup_kvm_host.yaml))
    * 4_create_bastion.yaml ([code](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/4_create_bastion.yaml))
    * 5_setup_bastion.yaml ([code](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/5_setup_bastion.yaml))
    * 6_create_nodes.yaml ([code](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/6_create_nodes.yaml))
    * 7_ocp_verification.yaml ([code](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/7_ocp_verification.yaml))
* Watch Ansible as it completes the installation, correcting errors if they arise.
* To look at what tasks are running in detail, open the playbook or roles/role-name/tasks/main.yaml
* Alternatively, to run all the playbooks at once, start the master playbook by running this shell command:

```shell
ansible-playbook playbooks/site.yaml
```

* If the process fails in error, go through the steps in the [troubleshooting](troubleshooting.md) page.
* At the end of the the last playbook, follow the printed instructions for first-time login to the cluster.
* If you make cluster configuration changes in all.yaml file, like increased number of nodes or
a new bastion setup, after you have successfully installed a OCP cluster,
then you just need to run these playbooks in order:
  * 5_setup_bastion.yaml
  * 6_create_nodes.yaml
  * 7_ocp_verification.yaml

## 0 Setup Playbook
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
## 1 Create LPAR Playbook
### Overview
Creation of one to three Logical Partitions (LPARs), depending on your configuration. Uses the Hardware Management Console (HMC) API, so your system must be in Dynamic Partition Manager (DPM) mode.
### Outcomes
* One to three LPARs created.
* One to two Networking Interface Cards (NICs) attached per LPAR.
* One to two storage groups attached per LPAR.
* LPARs are in 'Stopped' state.
### Notes
* Recommend opening the HMC via web-browser to watch the LPARs come up.
## 2 Create KVM Host Playbook
### Overview
First-time start-up of Red Hat Enterprise Linux installed natively on the LPAR(s). Uses the Hardware Management Console (HMC) API, so your system must be in Dynamic Partition Manager (DPM) mode. Configuration files are passed to the file server and RHEL is booted and then kickstarted for fully automated setup.
### Outcomes
* LPAR(s) started up in 'Active' state.
* Configuration files (cfg, ins, prm) for the KVM host(s) are on the file server in the provided configs directory.
### Notes
* Recommended to open the HMC via web-browser to watch the Operating System Messages for each LPAR as they boot in order to debug any potential problems.
## 3 Setup KVM Host Playbook
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
## 4 Create Bastion Playbook
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
## 5 Setup Bastion Playbook
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
## 6 Create Nodes Playbook
### Overview
OCP cluster's nodes are created and the control plane is bootstrapped.
### Outcomes
* CoreOS initramfs and kernel are pulled down.
* Control nodes are created and bootstrapped.
* Bootstrap has been created, done its job connecting the control plane, and is then destroyed.
* Compute nodes are created, as many as is specified in groups_vars/all.yaml.
* Infra nodes, if defined in group_vars/all.yaml have been created, but are at this point essentially just compute nodes.
### Notes
* To watch the bootstrap do its job connecting the control plane: first, SSH to the bastion, then change to root (sudo -i), from there SSH to the bootstrap node as user 'core' (e.g. ssh core@bootstrap-ip). Once you're in the bootstrap run 'journalctl -b -f -u release-image.service -u bootkube.service'. Expect many errors as the control planes come up. You're waiting for the message 'bootkube.service complete'
* If the cluster is highly available, the bootstrap node will be created on the last (usually third) KVM host in the group. Since the bastion is on the first host, this was done to spread out the load.
## 7 OCP Verification Playbook
### Overview
Final steps of waiting for and verifying the OpenShift cluster to complete its installation.
### Outcomes
* Certificate Signing Requests (CSRs) have been approved.
* All nodes are in ready state.
* All cluster operators are available.
* OpenShift installation is verified to be complete.
* Temporary credentials and URL are printed to allow easy first-time login to the cluster.
### Notes
* These steps may take a long time and the tasks are very repetitive because of that.
* If your cluster has a very large number of compute nodes or insufficient resources, more rounds of approvals and time may be needed for these tasks.
* If you made it this far, congratulations!
* To install a new cluster, copy your inventory directory, change the default in the ansible.cfg, change the variables, and start again. With all the customizations to the playbooks you made along the way still intact.

# Additional Playbooks

## Create additional compute nodes (create_compute_node.yaml) and delete compute nodes (delete_compute_node.yaml)
### Overview

* In case you want to add additional compute nodes in a day-2 operation to your cluster or delete existing compute nodes in your cluster,
run these playbooks. Currently we support only **env.network_mode** `macvtap` for these two playbooks.
We recommand to create a new config file for the additional compute node with such parameters:

  ```yaml
  day2_compute_node:
    vm_name: worker-4
    vm_hostname: worker-4
    vm_ip: 172.192.100.101
    hostname: kvm01
    host_arch: s390x

  # rhcos_download_url with '/' at the end !
  rhcos_download_url: "https://mirror.openshift.com/pub/openshift-v4/s390x/dependencies/rhcos/4.13/4.13.0/"
  # RHCOS live image filenames
  rhcos_live_kernel: "rhcos-4.13.0-s390x-live-kernel-s390x"
  rhcos_live_initrd: "rhcos-4.13.0-s390x-live-initramfs.s390x.img"
  rhcos_live_rootfs: "rhcos-4.13.0-s390x-live-rootfs.s390x.img"
```

Make sure that the hostname where you want to create the additional compute node is defined in the `inventories/default/hosts` file.
Now you can execute the `add_compute_node` playbook with this command and parameter:

```shell
ansible-playbook playbooks/add_compute_node.yaml --extra-vars "@compute-node.yaml"
```

### Outcomes
* The defind compute node will be added or deleted, depends which playbook you have executed.

## Master Playbook (site.yaml)
### Overview
* Use this playbook to run all required playbooks (0-7) all at once.
### Outcomes
* Same as all the above outcomes for all required playbooks.
* At the end you will have an OpenShift cluster deployed and first-time login credentials.

## Pre-Existing Host Master Playbook (pre-existing_site.yaml)
### Overview
* Use this version of the master playbook if you are using a pre-existing LPAR(s) with RHEL already installed.
### Outcomes
* Same as all the above outcomes for all playbooks excluding 1 & 2.
* This will not create LPAR(s) nor boot your RHEL KVM host(s).
* At the end you will have an OpenShift cluster deployed and first-time login credentials.

## Reinstall Cluster Playbook (reinstall_cluster.yaml)
### Overview
In case the cluster needs to be completely reinstalled, run this playbook. It will refresh the ingitions that expire after 24 hours, teardown the nodes and re-create them, and then verify the installation.
### Outcomes
* get_ocp role runs.
    * Delete the folders /var/www/html/bin and /var/www/html/ignition.
    * CoreOS roofts is pulled to the bastion.
    * OCP client and installer are pulled down.
    * oc, kubectl and openshift-install binaries are installed.
    * OCP install-config is created from scratch, templated and backed up.
    * Manfifests are created.
    * OCP install directory found at /root/ocpinst/ is deleted, re-created and populated with necessary files.
    * Ignition files for the bootstrap, control, and compute nodes are transferred to HTTP-accessible directory for booting nodes.
* 6 Create Nodes playbook runs, tearing down and recreating cluster nodes.
* 7 OCP Verification playbook runs, verifying new deployment.

## Test Playbook (test.yaml)
### Overview
* Use this playbook for your testing purposes, if needed.
