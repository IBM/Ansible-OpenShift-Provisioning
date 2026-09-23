# Run the Playbooks

## Overview

This document describes the typical execution flow for provisioning and for day-2 compute-node operations.

The standard cluster creation flow remains:

1. Run [`playbooks/0_setup.yaml`](../playbooks/0_setup.yaml)
2. Run [`playbooks/1_create_lpar.yaml`](../playbooks/1_create_lpar.yaml) if new LPARs are required
3. Run [`playbooks/2_create_kvm_host.yaml`](../playbooks/2_create_kvm_host.yaml) if new KVM hosts are required
4. Run [`playbooks/3_setup_kvm_host.yaml`](../playbooks/3_setup_kvm_host.yaml)
5. Run [`playbooks/4_create_bastion.yaml`](../playbooks/4_create_bastion.yaml)
6. Run [`playbooks/5_setup_bastion.yaml`](../playbooks/5_setup_bastion.yaml)
7. Run [`playbooks/6_create_nodes.yaml`](../playbooks/6_create_nodes.yaml)
8. Run [`playbooks/7_ocp_verification.yaml`](../playbooks/7_ocp_verification.yaml)

## Standard cluster creation flow

### 1. Initial setup

Run [`playbooks/0_setup.yaml`](../playbooks/0_setup.yaml) first.

This playbook:
- validates the inventory input
- installs required controller dependencies
- generates [`inventories/default/hosts`](../inventories/default/hosts)
- adds eligible day-2 hypervisors to the [`day2_hosts`](../inventories/default/hosts) section when [`day2_compute_node`](../inventories/default/group_vars/all.yaml) is defined and the referenced host_vars files have `setup_host: true`

Example:

```bash
ansible-playbook -i inventories/default playbooks/0_setup.yaml
```

If no eligible day-2 hypervisors are defined, the [`day2_hosts`](../inventories/default/hosts) section is omitted.

### 2. Create LPARs if needed

If your KVM hosts must be created first, run [`playbooks/1_create_lpar.yaml`](../playbooks/1_create_lpar.yaml).

```bash
ansible-playbook -i inventories/default playbooks/1_create_lpar.yaml
```

### 3. Create KVM hosts if needed

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
* TigerVNC server is configured and enabled for remote desktop administration. Connect with a VNC client at kvm-ip-here:5901 (display :1).
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

## Delete Cluster Nodes Playbook (delete_cluster_nodes.yaml)
### Overview
* Use this playbook to delete all cluster nodes (bootstrap, control, compute, and infra nodes) from the configured KVM hosts based on your `inventories/default/group_vars/all.yaml` configuration.
* This is useful when you need to tear down the cluster nodes while keeping the bastion and infrastructure intact.

### Usage
To delete all cluster nodes from all configured KVM hosts:
```
ansible-playbook playbooks/delete_cluster_nodes.yaml
```

To delete nodes from a specific KVM host only, use tags:
```
ansible-playbook playbooks/delete_cluster_nodes.yaml --tags kvm_host_1
ansible-playbook playbooks/delete_cluster_nodes.yaml --tags kvm_host_2
ansible-playbook playbooks/delete_cluster_nodes.yaml --tags kvm_host_3
```

### Outcomes
* All cluster nodes (bootstrap, control, compute, and infra) are destroyed and undefined from the configured KVM hosts.
* Virtual machine storage is removed.
* A summary message is displayed upon completion.

### Notes
* This playbook does **NOT** delete:
    * The bastion node
    * Network configurations
    * Storage pools
    * DNS or HAProxy configurations
* To verify deletion, run `virsh list --all` on each KVM host.
* The playbook uses the existing `delete_nodes` role which safely handles non-existent VMs.
* If you need to reinstall the cluster after deletion, use the `reinstall_cluster.yaml` playbook or run playbooks 6 and 7.

## Create additional compute nodes (create_compute_node.yaml) and delete compute nodes (delete_compute_node.yaml)
### Overview

* In case you want to add additional compute nodes in a day-2 operation to your cluster or delete existing compute nodes in your cluster,
run these playbooks. Currently we support only **env.network_mode** `macvtap` for these two playbooks.
We recommand to create a new config file for the additional compute node with such parameters:

```bash
ansible-playbook -i inventories/default playbooks/2_create_kvm_host.yaml
```

### 4. Configure KVM hosts

Run [`playbooks/3_setup_kvm_host.yaml`](../playbooks/3_setup_kvm_host.yaml).

This playbook configures:
- the primary KVM hosts from the main inventory
- any eligible day-2 hypervisors listed in [`day2_hosts`](../inventories/default/hosts)

Example:

```bash
ansible-playbook -i inventories/default playbooks/3_setup_kvm_host.yaml
```

### 5. Create the bastion

Run [`playbooks/4_create_bastion.yaml`](../playbooks/4_create_bastion.yaml).

```bash
ansible-playbook -i inventories/default playbooks/4_create_bastion.yaml
```

### 6. Configure the bastion

Run [`playbooks/5_setup_bastion.yaml`](../playbooks/5_setup_bastion.yaml).

This playbook configures bastion services such as DNS, HAProxy, HTTPD, and firewall rules.

Example:

```bash
ansible-playbook -i inventories/default playbooks/5_setup_bastion.yaml
```

### 7. Create cluster nodes

Run [`playbooks/6_create_nodes.yaml`](../playbooks/6_create_nodes.yaml).

```bash
ansible-playbook -i inventories/default playbooks/6_create_nodes.yaml
```

### 8. Verify the cluster

Run [`playbooks/7_ocp_verification.yaml`](../playbooks/7_ocp_verification.yaml).

```bash
ansible-playbook -i inventories/default playbooks/7_ocp_verification.yaml
```

## Day-2 compute-node workflow

Day-2 compute nodes are defined through host_vars files referenced by [`day2_compute_node`](../inventories/default/group_vars/all.yaml).

Example in [`inventories/default/group_vars/all.yaml`](../inventories/default/group_vars/all.yaml):

```yaml
day2_compute_node:
  - example-day2-node
```

The referenced file must exist in [`inventories/default/host_vars`](../inventories/default/host_vars), for example:
- [`inventories/default/host_vars/compute-day2.yaml.template`](../inventories/default/host_vars/compute-day2.yaml.template)
- [`inventories/default/host_vars/example-day2-node.yaml`](../inventories/default/host_vars/example-day2-node.yaml)

### Day-2 preparation flow

If the day-2 node uses a hypervisor that must be prepared, run these playbooks in order:

1. [`playbooks/0_setup.yaml`](../playbooks/0_setup.yaml)
2. [`playbooks/3_setup_kvm_host.yaml`](../playbooks/3_setup_kvm_host.yaml)
3. [`playbooks/5_setup_bastion.yaml`](../playbooks/5_setup_bastion.yaml)

Why this is required:
- [`playbooks/0_setup.yaml`](../playbooks/0_setup.yaml) refreshes [`inventories/default/hosts`](../inventories/default/hosts) and rebuilds [`day2_hosts`](../inventories/default/hosts)
- [`playbooks/3_setup_kvm_host.yaml`](../playbooks/3_setup_kvm_host.yaml) configures the hypervisor when `setup_host: true`
- [`playbooks/5_setup_bastion.yaml`](../playbooks/5_setup_bastion.yaml) reconciles bastion DNS and HAProxy entries for the day-2 nodes when:
  - `dns: true`
  - `loadbalancer.on_bastion: true`

If a day-2 node is removed from [`day2_compute_node`](../inventories/default/group_vars/all.yaml) and [`playbooks/5_setup_bastion.yaml`](../playbooks/5_setup_bastion.yaml) is rerun, the bastion reconciliation removes obsolete DNS and HAProxy entries.

### Create a single day-2 compute node

After the preparation flow is complete, create the node with [`playbooks/create_compute_node.yaml`](../playbooks/create_compute_node.yaml).

```bash
ansible-playbook -i inventories/default playbooks/create_compute_node.yaml
```

This playbook:
- loads the first entry from [`day2_compute_node`](../inventories/default/group_vars/all.yaml)
- reads the matching host_vars file
- creates the VM on the referenced hypervisor
- uses `disk_size` when defined
- otherwise falls back to [`env.cluster.nodes.compute.disk_size`](../inventories/default/group_vars/all.yaml)
- uses `storage.pool_name` when defined
- otherwise falls back to `{{ env.cluster.networking.metadata_name }}-vdisk`
- uses `networking.dhcp: true` to boot the day-2 node with DHCP and apply the configured guest MAC address
- uses `networking.dhcp: false` to boot the day-2 node with static network kernel arguments from the host_vars file

### Create multiple day-2 compute nodes

For multiple nodes, use [`playbooks/create_multiple_compute_nodes.yaml`](../playbooks/create_multiple_compute_nodes.yaml) with an extra-vars file.

Example extra-vars file:

```yaml
day2_compute_nodes:
  - example-day2-node
  - another-day2-node
```

Run:

```bash
ansible-playbook -i inventories/default playbooks/create_multiple_compute_nodes.yaml -e @day2-nodes.yaml
```

If those nodes require new hypervisors to be configured first, temporarily add the relevant host_vars entry names to [`day2_compute_node`](../inventories/default/group_vars/all.yaml), rerun:
- [`playbooks/0_setup.yaml`](../playbooks/0_setup.yaml)
- [`playbooks/3_setup_kvm_host.yaml`](../playbooks/3_setup_kvm_host.yaml)
- [`playbooks/5_setup_bastion.yaml`](../playbooks/5_setup_bastion.yaml)

and then run [`playbooks/create_multiple_compute_nodes.yaml`](../playbooks/create_multiple_compute_nodes.yaml).

### Delete a day-2 compute node

To delete a day-2 node, keep the matching host_vars entry available and run [`playbooks/delete_compute_node.yaml`](../playbooks/delete_compute_node.yaml).

```bash
ansible-playbook -i inventories/default playbooks/delete_compute_node.yaml
```

This playbook loads the same host_vars-based node definition and removes the VM from the referenced hypervisor.

## Notes

- [`playbooks/0_setup.yaml`](../playbooks/0_setup.yaml) should be rerun whenever you change inventory-relevant variables such as [`day2_compute_node`](../inventories/default/group_vars/all.yaml).
- [`playbooks/3_setup_kvm_host.yaml`](../playbooks/3_setup_kvm_host.yaml) uses the generated [`day2_hosts`](../inventories/default/hosts) inventory group for day-2 hypervisor preparation.
- [`playbooks/5_setup_bastion.yaml`](../playbooks/5_setup_bastion.yaml) is the reconciliation step for bastion DNS and HAProxy state related to day-2 nodes.
