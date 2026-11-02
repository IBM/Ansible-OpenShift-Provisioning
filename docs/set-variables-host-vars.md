# Step 3: Set Variables (host_vars)

## Overview
* Similar to the group_vars file, the host_vars files for each LPAR (KVM host) must be filled in.
* For each KVM host to be acted upon with Ansible, you must have a corresponding host_vars file named `<kvm-hostname>.yaml` (i.e. ocpz1.yaml, ocpz2.yaml, ocpz3.yaml), so you must copy and rename the template [`lpar.yaml.template`](../inventories/default/host_vars/lpar.yaml.template) found in the [host_vars folder](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/inventories/default/host_vars) accordingly.
* **Template:** [`lpar.yaml.template`](../inventories/default/host_vars/lpar.yaml.template) is the single template for all LPAR use cases. It replaces the deprecated `KVMhostname1-here.yaml.template`, `KVMhostname2-here.yaml.template` and `KVMhostname3-here.yaml.template`, which will be removed in upcoming PRs. It covers:
    * **KVM installation:** the LPAR is a KVM host (RHEL + libvirt) that runs the cluster nodes as KVM guests. The file name must match `env.z.lpar1.hostname`, `env.z.lpar2.hostname` or `env.z.lpar3.hostname`. For the second and third KVM host use the secrets `vault_lpar2_user_pass` / `vault_lpar2_root_pass` and `vault_lpar3_user_pass` / `vault_lpar3_root_pass` instead of the `vault_lpar1_*` names used in the template.
    * **LPAR / ABI installation:** the cluster node itself runs in the LPAR. The file name must match the node's `vm_name` (see Section 8).
    * **LPAR creation on DPM:** when Ansible creates the LPAR (`env.z.lpar1.create: True`, role `create_lpar`), the template defines the DPM partition on the HMC: its IFL and memory (Section 4), NICs (Section 5) and storage groups (Section 6). The CPC must be DPM enabled. For a classic (PR/SM) LPAR that already exists, these items are not required.
    * In the template, items needed only for one case are marked `[KVM]` or `[DPM]`.
* The variables marked with an `X` are required to be filled in. Many values are pre-filled or are optional. 
* Optional values are commented out; in order to use them, remove the `#` and fill them in.
* Many of the variables in these host_vars files are only required if you are NOT using pre-existing LPARs with RHEL installed. See the `Important Note` below this first section for more details.
* **LPAR ABI deployments:** The filename of each host_vars file (`<vm_name>.yaml`) must match the corresponding `env.cluster.nodes.control.vm_name[n]` or `env.cluster.nodes.compute.vm_name[n]` value in `group_vars/all.yaml`. This is **not** the same as the OCP node hostname (set via `env.cluster.nodes.*.hostname[n]`). See Section 8 for a full explanation.
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
**networking.device2** | <b>(Optional)</b> Another Linux network interface card. Currently not evaluated by the playbooks. When a second NIC (`lpar.networking.nic.card2`) is defined for a KVM host, the bond is built from `card1.name` and `card2.name` and named `networking.device1`. | enc1
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
**hmc.auth.user** | The username that the HMC API call will use to connect to the HMC. Must have access to create LPARs, attach storage groups and networking cards. | hmc-user
**hmc.auth.pass** | The password that the HMC API call will use to connect to the HMC. Must have access to create LPARs, attach storage groups and networking cards. Reference it from the vault: `"{{ vault_hmc_pass }}"`. | hmcPas$w0rd!

## 3 - (Optional) LPAR
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**lpar.name** | The name of the Logical Partition (LPAR) that you would like to create/target for the creation of your cluster. This LPAR will act as the KVM host, with RHEL installed natively. | OCPKVM1
**lpar.description** | <b>(DPM creation only)</b> A short description of what this LPAR will be used for, will only be displayed in the HMC next to the LPAR name for identification purposes. Read by the `create_lpar` role. | KVM host LPAR for RHOCP cluster.
**lpar.access.user** | The username that will be created in RHEL when it is installed on the LPAR (the KVM host). | kvm-admin
**lpar.access.pass** | The password for the user that will be created in RHEL when it is installed on the LPAR (the KVM host). Reference it from the vault, e.g. `"{{ vault_lpar1_user_pass }}"`. | ch4ngeMe!
**lpar.access.root_pass** | The root password for RHEL installed on the LPAR (the KVM host). Reference it from the vault, e.g. `"{{ vault_lpar1_root_pass }}"`. | $ecureP4ass!

## 4 - (Optional) IFL & Memory
Used only when Ansible creates the LPAR on the HMC (DPM partition, `env.z.lpar1.create`). All six values are read by the `create_lpar` role.

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**lpar.ifl.count** | Number of Integrated Facilities for Linux (IFL) processors will be assigned to this LPAR. 6 or more recommended. | 6
**lpar.ifl.initial_memory** | Initial memory allocation for LPAR to have at start-up (in megabytes). | 55000
**lpar.ifl.max_memory** | The most amount of memory this LPAR can be using at any one time (in megabytes). | 99000
**lpar.ifl.initial_weight** | For LPAR load balancing purposes, the processing weight this LPAR will have at start-up (1-999). | 100
**lpar.ifl.min_weight** | For LPAR load balancing purposes, the minimum weight that this LPAR can have at any one time (1-999). | 50
**lpar.ifl.max_weight** | For LPAR load balancing purposes, the maximum weight that this LPAR can have at any one time (1-999). | 500

## 5 - Networking
The network of the LPAR is activated at boot with the kernel parameter `rd.znet=qeth,<read>,<write>,<data>,layer2=1,portno=<port>`, which is built from `card1`. Therefore **`card1.dev_num` and `card1.port` are required for every LPAR installation** (KVM host or LPAR / ABI node). `card1.name` and `card1.adapter` are only needed to create the NIC in the HMC partition when Ansible creates the LPAR (DPM).

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**lpar.networking.subnet_cidr** | The same value as the above variable but in Classless Inter-Domain Routing (CIDR) notation. Used in the `ip=` boot parameter of the KVM host. | 23
**lpar.networking.nic.osa_card.dev_num** | <b>(Optional) Required only when network mode is HIPERSOCKET</b> The device numbers of the OSA Network Interface Card (NIC) as a comma separated string. When defined, it is passed as the network device to the HMC load. | 0.0.1100,0.0.1101,0.0.1102
**lpar.networking.nic.card1.name** | <b>(DPM creation only)</b> The logical name of the Network Interface Card (NIC) within the HMC. An arbitrary value that is human-readable that points to the NIC. For a KVM host with two NICs it is also used as bond slave interface name. | SYS-NIC-01
**lpar.networking.nic.card1.adapter** | <b>(DPM creation only)</b> The physical adapter name reference to the logical adapter for the LPAR. | 10Gb-A
**lpar.networking.nic.card1.port** | <b>(Required)</b> The port number for the NIC. Used as `portno=` in `rd.znet`. | 0
**lpar.networking.nic.card1.dev_num** | <b>(Required)</b> The device number of the NIC. The format depends on the use case, see the note below the table. | 0x0100 or 0.0.1100,0.0.1101,0.0.1102
**lpar.networking.nic.card2.name** | <b>(Optional)</b> The logical name of a second Network Interface Card (NIC) within the HMC. An arbitrary value that is human-readable that points to the NIC. | SYS-NIC-02
**lpar.networking.nic.card2.adapter** | <b>(Optional)</b> The physical adapter name of a second NIC. | 10Gb-B
**lpar.networking.nic.card2.port** | <b>(Optional)</b> The port number for a second NIC. | 1
**lpar.networking.nic.card2.dev_num** | <b>(Optional)</b> The logical device number for a second NIC. Same format rules as `card1.dev_num` for a KVM host / LPAR creation (hex integer). | 0x0001

**Format of `card1.dev_num`:**
* **LPAR / ABI node** (`boot_LPAR`, `boot_LPAR_abi`) and network mode `hipersocket`: the three CCW devices (read, write, data) as one comma separated string, e.g. `0.0.1100,0.0.1101,0.0.1102`.
* **KVM host installation** (`update_cfgs`) and **LPAR creation** (`create_lpar`): only the first device number is given. The write and data devices are derived as +1 and +2. The value is evaluated as an integer and converted to 4 hex digits, so use unquoted YAML hex notation, e.g. `0x1100` (becomes `1100`, `1101`, `1102`).

## 6 - (Optional) Storage
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**lpar.storage_group_1.name** | <b>(DPM creation only)</b> The name of the storage group that will be attached to the LPAR. | OCP-storage-01
**lpar.storage_group_1.type** | Storage type. FCP is the only tested type as of now for KVM hosts. LPAR / ABI nodes also support `dasd`. | fcp
**lpar.storage_group_1.storage_wwpn** | World-wide port numbers for storage group. Use provided list formatting. For a KVM host every entry gets its own `rd.zfcp=` line in the RHEL kickstart parameter file (the role adds the `0x` prefix, so give the WWPN without it). For LPAR / ABI only the first entry is used. | 500708680235c3f0<br />500708680235c3f1<br />500708680235c3f2<br />500708680235c3f3
**lpar.storage_group_1.dev_num** | The logical device number of the Host Bus Adapter (HBA) for the storage group. | C001
**lpar.storage_group_1.lun_name** | The Logical Unit Numbers (LUN) that points to a specific virtual disk behind the WWPN. | 4200569309ahhd240000000000000c001
**lpar.storage_group_2.name** | <b>(Optional, DPM creation only)</b> The name of the storage group that will be attached to the LPAR. | OCP-storage-01
**lpar.storage_group_2.auto_config** | <b>(Optional)</b> Attempt to automate the addition of the disk space to the existing logical volume. Check out roles/configure_storage/tasks/main.yaml to ensure this will work properly with your setup. | True
**lpar.storage_group_2.type** | <b>(Optional)</b> Storage type. FCP is the only tested type as of now. | fcp
**lpar.storage_group_2.storage_wwpn** | <b>(Optional)</b> World-wide port numbers for storage group. Use provided list formatting. | 500708680235c3f0<br />500708680235c3f1<br />500708680235c3f2<br />500708680235c3f3
**lpar.storage_group_2.dev_num** | <b>(Optional)</b> The logical device number of the Host Bus Adapter (HBA) for the storage group. | C001
**lpar.storage_group_2.lun_name** | <b>(Optional)</b> The Logical Unit Numbers (LUN) that points to a specific virtual disk behind the WWPN. | 4200569309ahhd240000000000000c001

## 7 - (Optional) Livedisk info
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**lpar.livedisk.livedisktype** | <b>(Optional)</b> Storage type. DASD and SCSI are tested types as of now. | dasd/scsi
**lpar.livedisk.lun** | <b>(Required if livedisktype is scsi)</b> The Lunid of the disk when the livedisktype is SCSI. | 4003402b00000000
**lpar.livedisk.wwpn** | <b>(Required if livedisktype is scsi)</b> World-wide port number when livedisktype is SCSI. | 500507630a1b50a4
**lpar.livedisk.devicenr** | <b>(Optional)</b> the device no of the live disk | c6h1
**lpar.livedisk.livediskuuid** | <b>(Required if `lpar.dpm_enabled` is `'True'`)</b> UUID of the SCSI live disk device. Used by the HMC load on DPM-enabled CPCs only. | 6005076308ffc2200000000000001000
**lpar.livedisk.livedisk_root_pass** | <b>(Optional)</b> root password for the livedisk. Reference it from the vault: `"{{ vault_livedisk_root_pass }}"`. | p@ssword
**lpar.dpm_enabled** | Type of CPC: `'True'` if the CPC is DPM enabled, `'False'` for classic PR/SM. Allowed values `'True'` and `'False'` (quoted strings). It controls how the LPAR is loaded (`boot_LPAR`, `boot_LPAR_abi`): for DPM the live disk UUID and the install device by-path are used. | 'False'

## 8 - LPAR ABI: vm_name, hostname, and mac explained

This section explains three variables that are **distinct but easily confused** when deploying an Agent-Based Installer (ABI) cluster directly on bare-metal LPARs.

### vm_name vs hostname

| Variable | Where set | Purpose |
|:---|:---|:---|
| `env.cluster.nodes.*.vm_name[n]` | `group_vars/all.yaml` Sections 8 & 9 | Filename stem of `host_vars/<vm_name>.yaml`. Used by `boot_LPAR_abi` to load HMC/LPAR credentials and livedisk settings, and by `agent-config.yaml.j2` to look up FCP `rootDeviceHints`. |
| `env.cluster.nodes.*.hostname[n]` | `group_vars/all.yaml` Sections 8 & 9 | Short OCP node hostname. Combined with `metadata_name` and `base_domain` to form the FQDN written as the `hostname:` field in `agent-config.yaml` (e.g. `control-01.ocpz.example.com`). Also used for DNS A/PTR records and HAProxy server lines by the `setup_bastion_services` role. |

**On KVM deployments** `vm_name` and `hostname` are typically the same value because the libvirt VM name and the OCP hostname are set identically by convention.

**On LPAR ABI deployments** they are independent:
- `vm_name` identifies the LPAR's host_vars file (e.g. `lpar-node-1` → `host_vars/lpar-node-1.yaml`). It is the HMC/CPC identity.
- `hostname` is the OCP node short name (e.g. `control-01`). It is combined with `metadata_name` and `base_domain` to produce the FQDN written into `agent-config.yaml` (e.g. `control-01.<metadata_name>.<base_domain>`). This FQDN is what OpenShift registers as the node name, so it must be DNS-resolvable.

Example (`group_vars/all.yaml`):
```yaml
env:
  cluster:
    nodes:
      control:
        vm_name:   # host_vars filenames — match your LPAR names in HMC
          - lpar-cpc1-01
          - lpar-cpc1-02
          - lpar-cpc1-03
        hostname:  # OCP node hostnames — used for DNS and HAProxy
          - control-01
          - control-02
          - control-03
```

With the above, you must have `host_vars/lpar-cpc1-01.yaml`, `host_vars/lpar-cpc1-02.yaml`, `host_vars/lpar-cpc1-03.yaml`. DNS will be configured for `control-01.<metadata_name>.<base_domain>`, and `agent-config.yaml` will contain `hostname: control-01.<metadata_name>.<base_domain>` — the FQDN that OpenShift registers as the node name (visible in `oc get nodes`).

### mac is required for LPAR ABI

The `env.cluster.nodes.*.mac[n]` variable is **required** for LPAR ABI deployments. It is used in `agent-config.yaml.j2` for two purposes:
1. The `interfaces[].macAddress:` field — tells the agent which NIC to configure with the static IP.
2. The `networkConfig.interfaces[].mac-address:` NMState field — configures the interface for static IP assignment.

Without this value the agent cannot match the correct network interface and the node will not join the cluster.

#### MAC Address Determination by Environment and Adapter Type

- **RoCE Adapters:** Use the actual physical MAC address assigned to the RoCE card.
- **DPM Mode:** Use the MAC address configured/assigned to the network adapter in DPM.
- **Non-DPM Mode with Non-RoCE Adapters (e.g., OSA-Express / HiperSockets):** Non-DPM LPARs using OSA or HiperSockets in Layer 2 mode do not have a fixed permanent MAC address and the Linux kernel generates a random MAC address on every boot by default. For these environments, specify a **randomly generated MAC address** (e.g., `52:54:00:xx:yy:zz` or `02:xx:yy:zz:aa:bb` using valid unicast hex bytes) in `env.cluster.nodes.*.mac` in `group_vars/all.yaml`. During LPAR boot, the `boot_LPAR_abi` role writes this MAC into the boot parameter file (`genericdvd.prm`) via dracut's `ip=...::<mac>` parameter, which forces the kernel to assign this specified MAC to the LPAR interface so that it matches what `agent-config.yaml` expects.

### LPAR Load Status Timeout (Optional)

By default, the HMC status wait timeout when loading DASD or SCSI live disks is set to **300 seconds** (overriding the upstream `zhmcclient` default of 60 seconds). You can customize this timeout per node or globally:
- Per node in `host_vars/<node>.yaml`: `lpar.load_status_timeout: 300`
- Globally in `group_vars/all.yaml`: `env.lpar_load_status_timeout: 300`
