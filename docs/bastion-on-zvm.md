# Bastion Node Configuration

## Overview

Each bastion is defined in its own `host_vars` file. The `bastion.type` key in that file
(`kvm` or `zvm`) determines which hypervisor is used and which role `4_create_bastion.yaml`
calls. Multiple bastions, on different hypervisors, can coexist.

---

## 1 — `all.yaml` — `bastion_nodes` list

Add a top-level `bastion_nodes` list. Each entry is the name of a bastion `host_vars` file
(without the `.yaml` extension):

```yaml
# Section 5 - Bastion nodes
bastion_nodes:
  - bastion-lp59          # KVM bastion: inventories/default/host_vars/bastion-lp59.yaml
# - a3e06001              # zVM bastion: inventories/default/host_vars/a3e06001.yaml
```

Each name must match:

1. A file `inventories/default/host_vars/<name>.yaml`.
2. An entry in the `[bastion]` group in the `hosts` inventory.

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**bastion_nodes** | List of bastion node names. Each entry points to a `host_vars` file. | `- bastion-lp59`

---

## 2 — `hosts` inventory

### `[bastion]` group

Each bastion listed in `bastion_nodes` needs a matching entry. `ansible_become_password` and
`ansible_password` must **not** be set here — they reference vault variables and must live in
the bastion's `host_vars` file (Jinja2 is not evaluated in static inventory files).

**KVM bastion** — SSH via ProxyJump through the KVM host:

```ini
[bastion]
bastion-lp59  ansible_host=192.168.122.2  ansible_user=root \
  ansible_ssh_common_args='-o StrictHostKeyChecking=no -o ProxyCommand="ssh -i ~/.ssh/ansible-ocpz -o StrictHostKeyChecking=no -W %h:%p root@<kvm-host-ip>"'
```

**z/VM bastion** — direct SSH after kickstart installation:

```ini
[bastion]
a3e06001  ansible_host=10.10.10.201  ansible_user=root \
  ansible_ssh_common_args='-o StrictHostKeyChecking=no'
```

### `[zvm_host]` group

Not required for bastion creation. `tessia-baselib` runs on the Ansible controller and
connects to the z/VM hypervisor over the network — no SSH connection to a z/VM host is used.
Leave the group empty or commented out:

```ini
[zvm_host]
# reserved for future use
```

---

## 3 — Bastion `host_vars` files

### 3.1 — KVM bastion

Copy `inventories/default/host_vars/bastion-kvm-example.yaml.template` to
`inventories/default/host_vars/<your-bastion-hostname>.yaml` and fill in the values marked `#X`.

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**ansible_become_password** | Sudo password for Ansible on the bastion. References a vault variable. | `"{{ vault_bastion_pass }}"`
**ansible_password** | SSH password for Ansible on the bastion. References a vault variable. | `"{{ vault_bastion_pass }}"`
**bastion.type** | Dispatcher key. `kvm` for a KVM-hosted bastion. | `kvm`
**bastion.create** | Set `false` to skip creation and use a pre-existing bastion. | `true`
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
**bastion.networking.hostname** | Short hostname. Combined with `base_domain` to form the FQDN. | `bastion-lp59`
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
**bastion.access.pass** | Admin password. References a vault variable. | `"{{ vault_bastion_pass }}"`
**bastion.access.root_pass** | Root password. References a vault variable. | `"{{ vault_bastion_root_pass }}"`
**bastion.options.dns** | Run DNS for the cluster on this bastion. | `true`
**bastion.options.loadbalancer.on_bastion** | Run HAProxy load balancer on this bastion. | `true`
**bastion.options.loadbalancer.public_ip** | **(Optional)** External LB IP when `on_bastion: false`. | `192.168.10.50`
**bastion.options.loadbalancer.private_ip** | **(Optional)** Internal LB IP when `on_bastion: false`. | `10.24.17.12`

### 3.2 — z/VM bastion

Copy `inventories/default/host_vars/bastion-zvm-example.yaml.template` to
`inventories/default/host_vars/<zvm-guest-name-lowercase>.yaml` (e.g. `a3e06001.yaml`).

All common variables from the KVM table above apply. The z/VM-specific variables are:

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**bastion.type** | Dispatcher key. `zvm` for a z/VM-hosted bastion. | `zvm`
**bastion.hypervisor_host** | Label identifying the z/VM hypervisor (informational, not an inventory host). | `zvm-host1`
**bastion.zvm_name** | z/VM guest user ID (uppercase, max 8 characters). Must equal `zvm_user` — tessia-baselib enforces this. | `A3E06001`
**bastion.zvm_host** | Hostname or IP of the z/VM LPAR that hosts the guest. tessia-baselib connects here. | `boea3e17`
**bastion.zvm_user** | Same value as `zvm_name`. tessia-baselib logs in **as the guest's own user ID** to IPL it — not as a separate admin account. | `A3E06001`
**bastion.zvm_pass** | Password for the guest's z/VM user ID. References a vault variable. | `"{{ vault_zvm_pass }}"`
**bastion.resources.vcpu** | Virtual CPUs. | `4`
**bastion.resources.ram** | RAM in MB. | `8192`
**bastion.resources.swap** | Swap in MB. | `4096`
**bastion.networking.interface.ifname** | Linux interface name inside the guest. | `enc1000`
**bastion.networking.interface.nettype** | z/VM network type. | `qeth`
**bastion.networking.interface.subchannels** | Three OSA subchannel addresses (comma-separated). | `0.0.1000,0.0.1001,0.0.1002`
**bastion.networking.interface.options** | QETH options. | `layer2=1`
**bastion.disk_type** | Disk type: `dasd` or `fcp`. | `dasd`
**bastion.dasd.disk_id** | DASD device number *(when `disk_type: dasd`)*. | `0B00`
**bastion.fcp.lun[].id** | FCP LUN ID *(when `disk_type: fcp`)*. | `0x4000000000000000`
**bastion.fcp.lun[].paths[].wwpn** | FCP WWPN for a path. | `0x500507680b2a5f7e`
**bastion.fcp.lun[].paths[].fcp** | FCP device number for a path. | `0x1a00`

---

## 4 — `4_create_bastion.yaml` Playbook

### Overview

Creates bastion nodes listed in `bastion_nodes`. The playbook runs two passes in sequence.
The first pass targets each `kvm_host` and creates any KVM bastions assigned to it. The
second pass runs on `localhost` and creates any z/VM bastions by connecting to the z/VM
hypervisor over the network via `tessia-baselib`. Each pass inspects every entry in
`bastion_nodes` and skips bastions whose type or `hypervisor_host` do not match.

### Dispatch logic

```
bastion.type == 'kvm'  →  role: create_bastion       (runs on designated kvm_host)
bastion.type == 'zvm'  →  role: create_bastion_zvm   (runs on localhost via tessia-baselib)
```

### Outcomes

* **KVM bastions**: kickstart configuration files are uploaded to the file server;
  `virt-install` creates and boots the VM on the designated KVM host; SSH is verified.
* **z/VM bastions**: a kickstart file is uploaded to the file server; a Python boot script
  is generated and executed on the Ansible controller; `tessia-baselib` boots the guest
  into the kickstart installer; SSH is verified once installation completes.
* In both cases the bastion is left running and ready for `5_setup_bastion.yaml`.

### Notes

* Set `bastion.create: false` in a bastion's `host_vars` file to skip creation and use a
  pre-existing server.
* For KVM bastions, Cockpit on the KVM host (`http://<kvm-ip>:9090`) is useful for watching
  the VM come up.
* `tessia-baselib` must be installed on the Ansible controller for z/VM bastion creation
  (`pip install tessia-baselib`).

---

## 5 — `power_bastion.yaml` Playbook

### Overview

Starts, stops, or restarts bastion VMs. The action is passed via the `bastion_action` extra
variable. All bastions listed in `bastion_nodes` are acted on.

### Usage

```bash
ansible-playbook playbooks/power_bastion.yaml --ask-vault-pass \
  --extra-vars "bastion_action=start"

ansible-playbook playbooks/power_bastion.yaml --ask-vault-pass \
  --extra-vars "bastion_action=stop"

ansible-playbook playbooks/power_bastion.yaml --ask-vault-pass \
  --extra-vars "bastion_action=restart"
```

`bastion_action` must be one of `start`, `stop`, or `restart`. The default is `start`.

### Dispatch logic

```
bastion.type == 'kvm'           →  role: power_bastion_kvm   (runs on designated kvm_host)
bastion.type in ['zvm','lpar']  →  role: power_bastion_zvm   (runs on localhost)
```

### Outcomes

**start**
* KVM: `virsh start <vm_name>` on the KVM host; waits for SSH to become available.
* z/VM: boots the guest from disk via `tessia-baselib` (`boot_method: disk`).

**stop**
* KVM: graceful `virsh shutdown`; falls back to `virsh destroy` after timeout.
* z/VM: SSH `systemctl poweroff` on the guest; falls back to `vmcp force logoff <zvm_name>`.

**restart**
* Both types: stop then start as above.

### Notes

* Idempotent — starting an already-running VM or stopping an already-stopped VM is handled
  gracefully.
* For z/VM guests, `vmcp query user <zvm_name>` checks whether the guest is logged on before
  issuing a `force logoff`.
