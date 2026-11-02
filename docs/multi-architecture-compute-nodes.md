# Multi-Architecture Compute Node Addition

## Overview

This document explains the current day-2 workflow for adding compute nodes to an existing OpenShift cluster, including:
- adding a single node with [`playbooks/create_compute_node.yaml`](../playbooks/create_compute_node.yaml)
- adding multiple nodes with [`playbooks/create_multiple_compute_nodes.yaml`](../playbooks/create_multiple_compute_nodes.yaml)
- multi-architecture scenarios such as adding [`x86_64`](../inventories/default/host_vars/example-day2-node.yaml) compute nodes to an [`s390x`](../inventories/default/host_vars/example-day2-node.yaml) cluster

The current implementation is **host_vars-based**. A day-2 node is no longer described inline as a nested object in [`all.yaml`](../inventories/default/group_vars/all.yaml). Instead:

1. create one host_vars file per day-2 node in [`inventories/default/host_vars`](../inventories/default/host_vars)
2. list the host_vars entry name in [`day2_compute_node`](../inventories/default/group_vars/all.yaml) for single-node operations
3. pass a list of host_vars entry names as [`day2_compute_nodes`](../playbooks/create_multiple_compute_nodes.yaml) for multi-node operations

## Current Day-2 Data Model

### Single-node flow

For [`playbooks/create_compute_node.yaml`](../playbooks/create_compute_node.yaml), define [`day2_compute_node`](../inventories/default/group_vars/all.yaml) as a list containing exactly one host_vars entry name:

```yaml
day2_compute_node:
  - example-day2-node
```

The playbook loads the node definition from:

- [`inventories/default/host_vars/example-day2-node.yaml`](../inventories/default/host_vars/example-day2-node.yaml) for a real example
- [`inventories/default/host_vars/compute-day2.yaml.template`](../inventories/default/host_vars/compute-day2.yaml.template) as the template structure

### Multi-node flow

For [`playbooks/create_multiple_compute_nodes.yaml`](../playbooks/create_multiple_compute_nodes.yaml), provide a list of host_vars entry names through extra vars:

```yaml
day2_compute_nodes:
  - example-day2-node
  - another-day2-node
```

Each list item must match a file in [`inventories/default/host_vars`](../inventories/default/host_vars).

### Host_vars structure

A day-2 host_vars file contains both:
- the compute node definition
- the hypervisor connection details used to create that node

Example structure:

```yaml
hypervisor_name: example-kvm-host
hypervisor_host_ip: 192.168.100.10
hypervisor_user: root
hypervisor_user_pwd: "{{ vault_host_user_pass }}"
hypervisor_arch: x86_64
setup_host: true

node_vm_name: worker-x64-example
node_vm_hostname: worker-x64-example

vcpu: 4
memory: 16384
disk_size: 120
vcpu_model_option: "--cpu host"

networking:
  ip: 192.168.100.64
  ipv6:
  gateway: 192.168.100.1
  ipv6_gateway:
  subnetmask: 255.255.255.0
  ipv6_prefix:
  mac_address: "52:54:00:00:01:41"
  device1: enp1s0
  dhcp: false

storage:
  pool_path: /var/lib/libvirt/images/
  pool_name: examplecluster-vdisk

node_role: compute
ignition_type: worker
```

## How Nodes Are Added Now

## 1. Define the day-2 node in host_vars

Create a host_vars file for each additional compute node you want to add. Use [`inventories/default/host_vars/compute-day2.yaml.template`](../inventories/default/host_vars/compute-day2.yaml.template) as the starting point.

Important fields:
- `hypervisor_name`: inventory name of the target hypervisor
- `hypervisor_host_ip`: IP address of the target hypervisor
- `hypervisor_user`: SSH user for the hypervisor
- `hypervisor_user_pwd`: password used for privilege escalation and setup
- `hypervisor_arch`: architecture of the hypervisor and node image lookup
- `setup_host`: whether [`playbooks/3_setup_kvm_host.yaml`](../playbooks/3_setup_kvm_host.yaml) should configure this hypervisor as a day-2 host
- `node_vm_name`: VM name to create
- `node_vm_hostname`: hostname of the new OpenShift node
- `vcpu`, `memory`, `disk_size`, `vcpu_model_option`: VM sizing
- `networking.*`: DHCP/static selection, IP, gateway, subnet, MAC, and interface settings
- `storage.pool_path`: libvirt storage pool path
- `storage.pool_name`: optional libvirt storage pool name used for VM disk creation
- `node_role` and `ignition_type`: node role metadata

If `disk_size` is not set, the day-2 VM creation flow falls back to [`env.cluster.nodes.compute.disk_size`](../inventories/default/group_vars/all.yaml).
If `storage.pool_name` is not set, the day-2 VM creation flow falls back to `{{ env.cluster.networking.metadata_name }}-vdisk`.
If `networking.dhcp: true`, the day-2 VM boots with DHCP and uses `networking.mac_address` for the guest NIC definition.
If `networking.dhcp: false`, the day-2 VM boots with the static IPv4 settings from `networking.ip`, `networking.gateway`, `networking.subnetmask`, and `networking.device1`.

## 2. Register the node in [`day2_compute_node`](../inventories/default/group_vars/all.yaml)

For the single-node workflow, add the host_vars entry name to [`day2_compute_node`](../inventories/default/group_vars/all.yaml):

```yaml
day2_compute_node:
  - example-day2-node
```

This variable is used by:
- [`playbooks/0_setup.yaml`](../playbooks/0_setup.yaml) to evaluate day-2 hypervisors for inventory generation
- [`playbooks/3_setup_kvm_host.yaml`](../playbooks/3_setup_kvm_host.yaml) to configure eligible day-2 hypervisors
- [`playbooks/create_compute_node.yaml`](../playbooks/create_compute_node.yaml) to load the node definition and create the VM

## 3. Re-run [`playbooks/0_setup.yaml`](../playbooks/0_setup.yaml)

When [`day2_compute_node`](../inventories/default/group_vars/all.yaml) is defined, [`playbooks/0_setup.yaml`](../playbooks/0_setup.yaml) regenerates [`inventories/default/hosts`](../inventories/default/hosts).

If a referenced host_vars file has `setup_host: true`, the hypervisor is added to the dedicated inventory group:

```ini
[day2_hosts]
example-kvm-host ansible_host=192.168.100.10 ansible_user=root ansible_become_password='...' ansible_python_interpreter=/usr/bin/python3
```

If no eligible day-2 nodes exist, the [`day2_hosts`](../inventories/default/hosts) section is omitted.

This inventory-based approach is important because it avoids the delegation and interpreter-discovery problems that occur when trying to configure day-2 hypervisors only through ad-hoc delegated tasks.

## 4. Configure day-2 hypervisors with [`playbooks/3_setup_kvm_host.yaml`](../playbooks/3_setup_kvm_host.yaml)

If `setup_host: true` is set in the day-2 node host_vars file, rerun [`playbooks/3_setup_kvm_host.yaml`](../playbooks/3_setup_kvm_host.yaml).

The playbook now uses the [`day2_hosts`](../inventories/default/hosts) inventory group and configures those hosts in the same way as the primary KVM hosts, including:
- SSH key distribution
- package installation
- libvirt preparation
- storage configuration
- macvtap configuration where applicable

If `setup_host: false`, the hypervisor is not added to [`day2_hosts`](../inventories/default/hosts) and is not configured by [`playbooks/3_setup_kvm_host.yaml`](../playbooks/3_setup_kvm_host.yaml).

## 5. Prepare bastion services with [`playbooks/5_setup_bastion.yaml`](../playbooks/5_setup_bastion.yaml)

After inventory or cluster topology changes, rerun [`playbooks/5_setup_bastion.yaml`](../playbooks/5_setup_bastion.yaml) so bastion-side configuration is refreshed.

This is especially relevant when:
- DNS is hosted on the bastion
- HAProxy is hosted on the bastion
- ignition files need to be refreshed before adding nodes

The bastion playbook prepares the services that the day-2 node creation flow depends on.

## 6. Add the node

### Single node

Run:

```bash
ansible-playbook playbooks/create_compute_node.yaml
```

[`playbooks/create_compute_node.yaml`](../playbooks/create_compute_node.yaml) performs the following high-level steps:
- loads the host_vars file referenced by [`day2_compute_node`](../inventories/default/group_vars/all.yaml)
- queries the machine-config-operator for architecture-specific RHCOS artifacts using `hypervisor_arch`
- refreshes ignition content
- optionally updates DNS when `env.bastion.options.dns: true`
- creates the VM on the target hypervisor
- uses `disk_size` when defined, otherwise falls back to [`env.cluster.nodes.compute.disk_size`](../inventories/default/group_vars/all.yaml)
- uses `storage.pool_name` when defined, otherwise falls back to `{{ env.cluster.networking.metadata_name }}-vdisk`
- uses `networking.dhcp: true` to boot with DHCP and attach the configured MAC address
- uses `networking.dhcp: false` to boot with static network arguments from the host_vars file
- waits for the node to join
- approves CSRs
- optionally updates HAProxy when `env.bastion.options.loadbalancer.on_bastion: true`

### Multiple nodes

Create an extra vars file such as:

```yaml
day2_compute_nodes:
  - example-day2-node
  - another-day2-node
```

Then run:

```bash
ansible-playbook playbooks/create_multiple_compute_nodes.yaml --extra-vars "@extra-nodes.yml"
```

[`playbooks/create_multiple_compute_nodes.yaml`](../playbooks/create_multiple_compute_nodes.yaml) processes each host_vars entry sequentially by including [`roles/create_compute_node/tasks/add_single_node.yaml`](../roles/create_compute_node/tasks/add_single_node.yaml).

## Automated Components

The day-2 node creation flow automatically handles the following tasks.

### 1. Architecture-specific RHCOS image lookup

[`playbooks/create_compute_node.yaml`](../playbooks/create_compute_node.yaml) queries the OpenShift machine-config-operator and selects the correct RHCOS artifacts based on `hypervisor_arch` from the loaded host_vars file.

This supports mixed-architecture day-2 additions as long as the target architecture is available in the cluster's boot image metadata.

### 2. DNS updates

When `env.bastion.options.dns: true`, [`playbooks/create_compute_node.yaml`](../playbooks/create_compute_node.yaml) calls the [`dns_update`](../roles/dns_update/tasks/add.yaml) role to add the new node's DNS records.

The node IP used for DNS comes from `networking.ip` in the host_vars file.

### 3. HAProxy updates

When `env.bastion.options.loadbalancer.on_bastion: true`, [`playbooks/create_compute_node.yaml`](../playbooks/create_compute_node.yaml) calls the [`haproxy_update`](../roles/haproxy_update/tasks/add.yaml) role to add the node to the bastion HAProxy configuration.

### 4. VM creation on the target hypervisor

[`roles/create_compute_node/tasks/main.yaml`](../roles/create_compute_node/tasks/main.yaml) uses the loaded host_vars structure to create the VM with:
- `node_vm_name`
- `node_vm_hostname`
- `vcpu`
- `memory`
- `vcpu_model_option`
- `networking.*`
- `storage.pool_path`
- `storage.pool_name` or the default `{{ env.cluster.networking.metadata_name }}-vdisk`

### 5. Certificate approval and readiness checks

The workflow automatically:
- waits for the node to appear
- approves CSRs
- waits for the node to become ready

## Adding Multiple Nodes

### Why add multiple nodes at once?

Benefits:
- more efficient than running the single-node playbook repeatedly
- consistent use of the same host_vars-based schema
- easier tracking of a larger scale-out operation
- supports mixed architectures by loading each node definition independently

### Example multi-node extra vars file

```yaml
day2_compute_nodes:
  - worker-x86-1
  - worker-x86-2
  - worker-s390x-4
```

Each of these names must correspond to:
- [`inventories/default/host_vars/worker-x86-1.yaml`](../inventories/default/host_vars/worker-x86-1.yaml)
- [`inventories/default/host_vars/worker-x86-2.yaml`](../inventories/default/host_vars/worker-x86-2.yaml)
- [`inventories/default/host_vars/worker-s390x-4.yaml`](../inventories/default/host_vars/worker-s390x-4.yaml)

### What happens during the multi-node run

[`playbooks/create_multiple_compute_nodes.yaml`](../playbooks/create_multiple_compute_nodes.yaml) will:
- display the list of nodes to be added
- prompt for confirmation when more than one node is requested
- process each node sequentially
- display a summary at the end

## Single vs Multiple Node Addition

| Feature | Single Node | Multiple Nodes |
|---------|-------------|----------------|
| Playbook | `create_compute_node.yaml` | `create_multiple_compute_nodes.yaml` |
| Input variable | `day2_compute_node` | `day2_compute_nodes` |
| Input format | list with one host_vars entry name | list of host_vars entry names |
| Node definition source | `inventories/default/host_vars/<name>.yaml` | `inventories/default/host_vars/<name>.yaml` |
| Execution | one node per run | multiple nodes per run |
| Confirmation | no prompt | prompts if more than one node |
| Best for | single additions, testing | bulk additions, scaling |

## Recommended Execution Order

For a new day-2 node on a new hypervisor:
1. create the host_vars file
2. add the host_vars entry name to [`day2_compute_node`](../inventories/default/group_vars/all.yaml)
3. run [`playbooks/0_setup.yaml`](../playbooks/0_setup.yaml)
4. if `setup_host: true`, run [`playbooks/3_setup_kvm_host.yaml`](../playbooks/3_setup_kvm_host.yaml)
5. run [`playbooks/5_setup_bastion.yaml`](../playbooks/5_setup_bastion.yaml)
6. run [`playbooks/create_compute_node.yaml`](../playbooks/create_compute_node.yaml)

For multiple nodes:
1. create one host_vars file per node
2. if new hypervisors must be configured, temporarily list the relevant node names in [`day2_compute_node`](../inventories/default/group_vars/all.yaml)
3. run [`playbooks/0_setup.yaml`](../playbooks/0_setup.yaml)
4. if needed, run [`playbooks/3_setup_kvm_host.yaml`](../playbooks/3_setup_kvm_host.yaml)
5. run [`playbooks/5_setup_bastion.yaml`](../playbooks/5_setup_bastion.yaml)
6. run [`playbooks/create_multiple_compute_nodes.yaml`](../playbooks/create_multiple_compute_nodes.yaml) with `day2_compute_nodes`

## Notes

- The day-2 workflow currently supports `macvtap` networking for compute-node creation.
- The host_vars-based model is the authoritative source for day-2 node definitions.
- If a day-2 hypervisor should no longer be configured through the inventory-based flow, remove the corresponding node from [`day2_compute_node`](../inventories/default/group_vars/all.yaml) or set `setup_host: false` in its host_vars file and rerun [`playbooks/0_setup.yaml`](../playbooks/0_setup.yaml).