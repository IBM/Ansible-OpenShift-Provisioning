# Step 3: Set Variables (host_vars)

## Overview
* Similar to the group_vars file, the host_vars files for each LPAR (KVM host) must be filled in. 
* For each KVM host to be acted upon with Ansible, you must have a corresponding host_vars file named `<kvm-hostname>.yaml` (i.e. ocpz1.yaml, ocpz2.yaml, ocpz3.yaml), so you must copy and rename the templates found in the [host_vars folder](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/inventories/default/host_vars) accordingly.
* The variables marked with an `X` are required to be filled in. Many values are pre-filled or are optional. 
* Optional values are commented out; in order to use them, remove the `#` and fill them in.
* Many of the variables in these host_vars files are only required if you are NOT using pre-existing LPARs with RHEL installed. See the `Important Note` below this first section for more details.
* This is the most important step in the process. Take the time to make sure everything here is correct.
* <u>Note on YAML syntax</u>: Only the lowest value in each hierarchicy needs to be filled in. For example, at the top of the variables file networking does not need to be filled in, but the hostname does. There are X's where input is required to help you with this.
* Scroll the table to the right to see examples for each variable.

## 1 - KVM Host
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**networking.hostname** | The hostname of the LPAR with RHEL installed natively (the KVM host). | kvm-host-01
**networking.ip** | The IPv4 address of the LPAR with RHEL installed natively (the KVM host). | 192.168.10.2
**networking.internal_ip** | The internal IPv4 address of the LPAR required when booting the LPAR with HiperSocket card. Currently supports only when bastion is on LPAR or on zVM host. Incase of zVM bastion enable the HiperSocket card prior to the playbook run with vmcp commands on the bastion. Alternative Option would be setting up the bridge port on OSA or RoCE.| 10.42.6.2
**networking.mode** | Type of network card | osa/roce/hipersocket 
**networking.ipv6** | IPv6 address for the bastion if use_ipv6 variable is 'True'. | fd00::3
**networking.subnetmask** | The subnet that the LPAR resides in within your network. | 255.255.255.0
**networking.gateway** | The IPv4 address of the gateway to the network where the KVM host resides. | 192.168.10.0
**networking.ipv6_gateway** | IPv6 of he bastion's gateway server. | fd00::1
**networking.ipv6_prefix** | IPv6 prefix. | 64
**networking.nameserver1** | The IPv4 address from which the KVM host gets its hostname resolved. | 192.168.10.200
**networking.nameserver2** | <b>(Optional)</b> A second IPv4 address from which the KVM host can get its hostname resolved. Used for high availability. | 192.168.10.201
**networking.device1** | The network interface card from Linux's perspective. Usually enc and then a number that comes from the dev_num of the network adapter. | enc100
**networking.device2** | <b>(Optional)</b> Another Linux network interface card. Usually enc and then a number that comes from the dev_num of the second network adapter. | enc1
**storage.pool_path** | The absolute path to a directory on your KVM host that will be used to store qcow2 images for the cluster and other installation artifacts. A sub-directory will be created here that matches your clsuter's metadata name that will act as the cluster's libvirt storage pool directory. Note: all directories present in this path will be made executable for the 'qemu' group, as is required. | /home/kvm_admin/VirtualMachines

## Important Note
* You can skip the rest of the variables on this page IF you are using existing LPAR(s) that has RHEL already installed.
* If you are installing an LPAR based cluster then the information below must be provided and are not optional. You must create a host file corresponding to each lpar node.
    * Since this is how most production deployments on-prem are done on IBM zSystems, these variables have been marked as optional. 
    * With pre-existing LPARs with RHEL installed, you can also skip [1_create_lpar.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/1_create_lpar.yaml) and [2_create_kvm_host.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/2_create_kvm_host.yaml) playbooks. Make sure to still do [0_setup.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/0_setup.yaml) first though, then skip to [3_setup_kvm_host.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/3_setup_kvm_host.yaml)
    * In the scenario of lpar based installation you can skip [1_create_lpar.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/1_create_lpar.yaml) and [2_create_kvm_host.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/2_create_kvm_host.yaml). You can also optionally skip [3_setup_kvm_host.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/3_setup_kvm_host.yaml) and [4_create_bastion.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/3_setup_kvm_host.yaml) unless you are planning on having the bastion on the same host.
    * In case of lpar based installation one is expected to have a tessia live disk accessible by the lpar nodes for network boot. The details of which are to be filled in section #7 below. The steps to create a tessia livedisk can be found [here](https://gitlab.com/tessia-project/tessia-baselib/-/blob/master/doc/users/live_image.md).

## 2 - (Optional) CPC & HMC
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**cpc_name** | The name of the IBM zSystems / LinuxONE mainframe that you are creating a Red Hat OpenShift Container Platform cluster on. Can be found under the "Systems Management" tab of the Hardware Management Console (HMC). | SYS1
**hmc.host** | The IPv4 address of the HMC you will be connecting to in order to create a Logical Partition (LPAR) on which will act as the Kernel-based Virtual Machine (KVM) host aftering installing and setting up Red Hat Enterprise Linux (RHEL). | 192.168.10.1
**hmc.user** | The username that the HMC API call will use to connect to the HMC. Must have access to create LPARs, attach storage groups and networking cards. | hmc-user
**hmc.pass** | The password that the HMC API call will use to connect to the HMC. Must have access to create LPARs, attach storage groups and networking cards. | hmcPas$w0rd!

## 3 - (Optional) LPAR
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**lpar.name** | The name of the Logical Partition (LPAR) that you would like to create/target for the creation of your cluster. This LPAR will act as the KVM host, with RHEL installed natively. | OCPKVM1
**lpar.description** | A short description of what this LPAR will be used for, will only be displayed in the HMC next to the LPAR name for identification purposes. | KVM host LPAR for RHOCP cluster.
**lpar.access.user** | The username that will be created in RHEL when it is installed on the LPAR (the KVM host). | kvm-admin
**lpar.access.pass** | The password for the user that will be created in RHEL when it is installed on the LPAR (the KVM host). | ch4ngeMe!
**lpar.root_pass** | The root password for RHEL installed on the LPAR (the KVM host). | $ecureP4ass!

## 4 - (Optional) IFL & Memory
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**lpar.ifl.count** | Number of Integrated Facilities for Linux (IFL) processors will be assigned to this LPAR. 6 or more recommended. | 6
**lpar.ifl.initial memory** | Initial memory allocation for LPAR to have at start-up (in megabytes). | 55000
**lpar.ifl.max_memory** | The most amount of memory this LPAR can be using at any one time (in megabytes). | 99000
**lpar.ifl.initial_weight** | For LPAR load balancing purposes, the processing weight this LPAR will have at start-up (1-999). | 100
**lpar.ifl.min_weight** | For LPAR load balancing purposes, the minimum weight that this LPAR can have at any one time (1-999). | 50
**lpar.ifl.max_weight** | For LPAR load balancing purposes, the maximum weight that this LPAR can have at any one time (1-999). | 500

## 5 - (Optional) Networking
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**lpar.networking.subnet_cidr** | The same value as the above variable but in Classless Inter-Domain Routing (CIDR) notation. | 23
**lpar.networking.nic.osa_card.dev_num** | <b>(Optional) Required only when network mode is HIPERSOCKET</b>The logical device number for the OSA Network Interface Card (NIC). In hex format. |
**lpar.networking.nic.card1.name** | The logical name of the Network Interface Card (NIC) within the HMC. An arbitrary value that is human-readable that points to the NIC. | SYS-NIC-01
**lpar.networking.nic.card1.adapter** | The physical adapter name reference to the logical adapter for the LPAR. | 10Gb-A
**lpar.networking.nic.card1.port** | The port number for the NIC. | 0
**lpar.networking.nic.card1.dev_num** | The logical device number for the NIC. In hex format. | 0x0100
**lpar.networking.nic.card2.name** | <b>(Optional)</b> The logical name of a second Network Interface Card (NIC) within the HMC. An arbitrary value that is human-readable that points to the NIC. | SYS-NIC-02
**lpar.networking.nic.card2.adapter** | <b>(Optional)</b> The physical adapter name of a second NIC. | 10Gb-B
**lpar.networking.nic.card2.port** | <b>(Optional)</b> The port number for a second NIC. | 1
**lpar.networking.nic.card2.dev_num** | <b>(Optional)</b> The logical device number for a second NIC. In hex format. | 0x0001

## 6 - (Optional) Storage
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**lpar.storage_group_1.name** | The name of the storage group that will be attached to the LPAR. | OCP-storage-01
**lpar.storage_group_1.type** | Storage type. FCP is the only tested type as of now. | fcp
**lpar.storage_group_1.storage_wwpn** | World-wide port numbers for storage group. Use provided list formatting. | 500708680235c3f0<br />500708680235c3f1<br />500708680235c3f2<br />500708680235c3f3
**lpar.storage_group_1.dev_num** | The logical device number of the Host Bus Adapter (HBA) for the storage group. | C001
**lpar.storage_group_1.lun_name** | The Logical Unit Numbers (LUN) that points to a specific virtual disk behind the WWPN. | 4200569309ahhd240000000000000c001
**lpar.storage_group_2.name** | <b>(Optional)</b> The name of the storage group that will be attached to the LPAR. | OCP-storage-01
**lpar.storage_group_2.auto_config** | <b>(Optional)</b> Attempt to automate the addition of the disk space to the existing logical volume. Check out roles/configure_storage/tasks/main.yaml to ensure this will work properly with your setup. | True
**lpar.storage_group_2.type** | <b>(Optional)</b> Storage type. FCP is the only tested type as of now. | fcp
**lpar.storage_group_2_.storage_wwpn** | <b>(Optional)</b> World-wide port numbers for storage group. Use provided list formatting. | 500708680235c3f0<br />500708680235c3f1<br />500708680235c3f2<br />500708680235c3f3
**lpar.storage_group_2_.dev_num** | <b>(Optional)</b> The logical device number of the Host Bus Adapter (HBA) for the storage group. | C001
**lpar.storage_group_2_.lun_name** | <b>(Optional)</b> The Logical Unit Numbers (LUN) that points to a specific virtual disk behind the WWPN. | 4200569309ahhd240000000000000c001

## 7 - (Optional) Livedisk info
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**lpar.livedisk.livedisktype** | <b>(Optional)</b> Storage type. DASD and SCSI are tested types as of now. | dasd/scsi
**lpar.livedisk.lun** | <b>(Required if livedisktype is scsi)</b> The Lunid of the disk when the livedisktype is SCSI. | 4003402b00000000
**lpar.livedisk.wwpn** | <b>(Required if livedisktype is scsi)</b> World-wide port number when livedisktype is SCSI. | 500507630a1b50a4
**lpar.livedisk.devicenr** | <b>(Optional)</b> the device no of the live disk | c6h1
**lpar.livedisk.livedisk_root_pass** | <b>(Optional)</b> root password for the livedisk | p@ssword

## 8 - Bastion Node (KVM)

Each bastion listed in `bastion_nodes` (all.yaml) must have a corresponding
`host_vars` file. Copy `bastion-kvm-example.yaml.template` from the `host_vars`
directory to `<your-bastion-hostname>.yaml` in the same directory and fill in all
values marked `#X`.

> **Note** — `ansible_become_password` and `ansible_password` must live in the
> `host_vars` file. They reference vault variables and Ansible cannot evaluate
> Jinja2 expressions inside the static `hosts` inventory file.

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**ansible_become_password** | Sudo password for Ansible on the bastion (vault reference). | `"{{ vault_bastion_pass }}"`
**ansible_password** | SSH password for Ansible on the bastion (vault reference). | `"{{ vault_bastion_pass }}"`
**bastion.type** | Dispatcher key. `kvm` for a KVM-hosted bastion. | `kvm`
**bastion.create** | Create the VM? `false` to use a pre-existing bastion. | `true`
**bastion.hypervisor_host** | KVM host that will run this bastion. Must match a host in `[kvm_host]`. | `a311lp59`
**bastion.vm_name** | Libvirt domain name for the bastion VM. | `bastion-lp59`
**bastion.resources.disk_size** | Root disk size in GB. Recommended 100 or more. | `500`
**bastion.resources.ram** | RAM in MB. Recommended 8192 or more. | `8192`
**bastion.resources.swap** | Swap in MB. | `4096`
**bastion.resources.vcpu** | Virtual CPUs. Recommended 4 or more. | `4`
**bastion.resources.vcpu_model_option** | CPU model option passed to `virt-install`. | `--cpu host`
**bastion.networking.ip** | IPv4 address of the bastion. | `192.168.122.2`
**bastion.networking.internal_ip** | **(Optional)** Private IPv4 for HiperSocket LPAR clusters. | `10.42.16.1`
**bastion.networking.ipv6** | **(Optional)** IPv6 address. | `fd00::2`
**bastion.networking.mac** | **(Optional)** MAC address when using DHCP. | `52:54:00:18:1A:2B`
**bastion.networking.hostname** | Bastion short hostname. Combined with `base_domain` → FQDN. | `bastion-lp59`
**bastion.networking.base_domain** | DNS base domain. | `example.com`
**bastion.networking.subnetmask** | IPv4 subnet mask. | `255.255.255.0`
**bastion.networking.gateway** | IPv4 gateway. | `192.168.122.1`
**bastion.networking.ipv6_gateway** | **(Optional)** IPv6 gateway. | `fd00::1`
**bastion.networking.ipv6_prefix** | **(Optional)** IPv6 prefix length. | `64`
**bastion.networking.nameserver1** | Primary DNS resolver for the bastion. | `192.168.10.200`
**bastion.networking.nameserver2** | **(Optional)** Secondary DNS resolver. | `192.168.10.201`
**bastion.networking.forwarder** | External DNS forwarder. | `1.1.1.1`
**bastion.networking.interface** | Linux network interface name (simple string for KVM). | `enc1`
**bastion.access.user** | Admin username on the bastion. | `root`
**bastion.access.pass** | Admin password (vault reference). | `"{{ vault_bastion_pass }}"`
**bastion.access.root_pass** | Root password (vault reference). | `"{{ vault_bastion_root_pass }}"`
**bastion.options.dns** | Host DNS for the cluster on this bastion. | `true`
**bastion.options.loadbalancer.on_bastion** | Run HAProxy load balancer on the bastion. | `true`
**bastion.options.loadbalancer.public_ip** | **(Optional)** External LB IP when `on_bastion: false`. | `192.168.10.50`
**bastion.options.loadbalancer.private_ip** | **(Optional)** Internal LB IP when `on_bastion: false`. | `10.24.17.12`

## 9 - Bastion Node (z/VM)

For a bastion to be created as a z/VM guest, copy `bastion-zvm-example.yaml.template`
to `<zvm-guest-name-lowercase>.yaml` (e.g. `a3e06001.yaml`) and fill in all `#X` values.
All common variables from section 8 apply. The z/VM-specific additions are:

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**bastion.type** | Dispatcher key. Must be `zvm`. | `zvm`
**bastion.hypervisor_host** | z/VM host that manages this guest. Must match a host in `[zvm_host]`. | `zvm-host1`
**bastion.zvm_name** | z/VM user ID — uppercase, max 8 characters. | `A3E06001`
**bastion.zvm_host** | IP or hostname of the z/VM hypervisor. | `10.10.10.5`
**bastion.zvm_user** | z/VM administrative user. | `hscroot`
**bastion.zvm_pass** | z/VM admin password (vault reference). | `"{{ vault_zvm_pass }}"`
**bastion.networking.interface.ifname** | Linux interface name inside the guest. | `enc1000`
**bastion.networking.interface.nettype** | z/VM network type. | `qeth`
**bastion.networking.interface.subchannels** | Three OSA subchannel device numbers (comma-separated). | `0.0.1000,0.0.1001,0.0.1002`
**bastion.networking.interface.options** | QETH options string. | `layer2=1`
**bastion.disk_type** | Storage type: `dasd` or `fcp`. | `dasd`
**bastion.dasd.disk_id** | DASD device number *(when `disk_type: dasd`)*. | `0B00`
**bastion.fcp.lun[].id** | FCP LUN ID *(when `disk_type: fcp`)*. | `0x4000000000000000`
**bastion.fcp.lun[].paths[].wwpn** | FCP WWPN for a path. | `0x500507680b2a5f7e`
**bastion.fcp.lun[].paths[].fcp** | FCP device number for a path. | `0x1a00`

See [Bastion on z/VM Feature Guide](bastion-on-zvm.md) for full context, inventory requirements,
and playbook descriptions.
