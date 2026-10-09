# Agent-Based Installer (ABI) for LPAR Installations

## Overview

> **⚠️ Important Note**: This guide focuses specifically on the LPAR-specific `rootDeviceHints` configuration. For a complete setup, you must also configure all other required variables. See:
> - **Complete Variable Reference**: [set-variables-group-vars.md](set-variables-group-vars.md) and [set-variables-host-vars.md](set-variables-host-vars.md)
> - **Quick Start Guide**: [ABI_LPAR_QUICK_REFERENCE.md](ABI_LPAR_QUICK_REFERENCE.md)
> - **Full Setup Instructions**: [run-the-playbooks-for-abi.md](run-the-playbooks-for-abi.md)


This guide explains how to use Agent-Based Installer (ABI) for LPAR-based OpenShift installations on IBM Z/LinuxONE. The key difference between KVM and LPAR installations is the requirement for `rootDeviceHints` in the agent-config.yaml file.

## Key Differences: KVM vs LPAR

| Feature | KVM Installation | LPAR Installation |
|---------|------------------|-------------------|
| `rootDeviceHints` | Not required | **Required** for FCP storage |
| Storage Configuration | Virtual disks | Physical FCP/DASD storage |
| Device Path | Automatic | Must specify exact device path |

## How It Works

### Automatic rootDeviceHints Generation

When `installation_type: lpar` is set, the automation will:

1. Read each node's host_vars file (e.g., `host_vars/control-1.yaml`)
2. Extract FCP storage configuration from `lpar.storage_group_1`
3. Automatically generate `rootDeviceHints` in agent-config.yaml
4. Use the format: `/dev/disk/by-path/ccw-0.0.{dev_num}-fc-{wwpn}-lun-{lun_name}`

### Configuration Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Configure host_vars for each LPAR node             │
│ File: inventories/default/host_vars/control-1.yaml         │
│                                                             │
│ lpar:                                                       │
│   storage_group_1:                                          │
│     type: fcp                                               │
│     dev_num: "1a00"                                         │
│     storage_wwpn:                                           │
│       - "0x500507680b2a5f7e"                                │
│     lun_name: "0x4000000000000000"                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Set installation_type in all.yaml                  │
│ File: inventories/default/group_vars/all.yaml              │
│                                                             │
│ installation_type: lpar                                     │
│ abi:                                                        │
│   flag: True                                                │
│   boot_method: pxe                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Template generates agent-config.yaml               │
│ Role: prepare_configs                                       │
│                                                             │
│ hosts:                                                      │
│   - hostname: "control-1"                                   │
│     role: master                                            │
│     rootDeviceHints:                                        │
│       deviceName: /dev/disk/by-path/ccw-0.0.1a00-fc-       │
│                   0x500507680b2a5f7e-lun-0x4000000000000000│
└─────────────────────────────────────────────────────────────┘
```

## Configuration Requirements

### 1. Set Installation Type

In `inventories/default/group_vars/all.yaml`:

```yaml
installation_type: lpar

abi:
  flag: True
  ansible_workdir: 'ansible_workdir'
  ocp_installer_version: '4.18.8'
  ocp_installer_base_url: 'https://mirror.openshift.com/pub/openshift-v4'
  architecture: multi  # or s390x
  boot_method: pxe
```

### 2. Configure LPAR Storage in Host Vars

For **each** LPAR node (control and compute), create/update the host_vars file:

**File**: `inventories/default/host_vars/control-1.yaml`

```yaml
# ... other configuration ...

lpar:
  storage_group_1:
    name: storage_group_1
    type: fcp  # FCP storage (Fibre Channel Protocol)
    storage_wwpn:
      - "0x500507680b2a5f7e"  # Primary WWPN
      - "0x500507680b2a5f7f"  # Additional WWPNs for multipath
      - "0x500507680b2a5f80"
      - "0x500507680b2a5f81"
    dev_num: "1a00"              # FCP device number
    lun_name: "0x4000000000000000"  # LUN ID
```

**Important Notes**:
- Only the **first WWPN** (`storage_wwpn[0]`) is used for rootDeviceHints
- All WWPNs are used for multipath configuration during boot
- The `dev_num` should be the FCP adapter device number (without "0.0." prefix)
- The `lun_name` is the LUN identifier in hexadecimal format

### 3. Example for Multiple Nodes

**Control Node 1**: `host_vars/control-1.yaml`
```yaml
lpar:
  storage_group_1:
    type: fcp
    dev_num: "1a00"
    storage_wwpn:
      - "0x500507680b2a5f7e"
    lun_name: "0x4000000000000000"
```

**Control Node 2**: `host_vars/control-2.yaml`
```yaml
lpar:
  storage_group_1:
    type: fcp
    dev_num: "1a00"
    storage_wwpn:
      - "0x500507680b2a5f7e"
    lun_name: "0x4001000000000000"  # Different LUN
```

**Compute Node 1**: `host_vars/compute-1.yaml`
```yaml
lpar:
  storage_group_1:
    type: fcp
    dev_num: "1a00"
    storage_wwpn:
      - "0x500507680b2a5f7e"
    lun_name: "0x4002000000000000"  # Different LUN
```

### 3. Configure MAC Addresses in Group Vars

For LPAR ABI deployments, `env.cluster.nodes.*.mac` is **mandatory** in `inventories/default/group_vars/all.yaml`.

#### MAC Address Rules by Environment and Adapter Type

- **RoCE Adapters:** Use the actual physical MAC address assigned to the RoCE card.
- **DPM Mode:** Use the MAC address configured/assigned to the network adapter in DPM.
- **Non-DPM Mode with Non-RoCE Adapters (e.g., OSA-Express / HiperSockets):** Non-DPM LPARs using OSA or HiperSockets in Layer 2 mode do not have a fixed permanent MAC address; the Linux kernel generates a random MAC address on every boot by default. For these environments, specify a **randomly generated locally administered MAC address** (e.g. `52:54:00:xx:yy:zz` or `02:xx:yy:zz:aa:bb`) in `env.cluster.nodes.*.mac`.

#### How the Parm File and Boot Process Handle the MAC Address

During LPAR boot, the `boot_LPAR_abi` role generates the boot parameter file (`genericdvd.prm`) and appends the specified MAC address as the last field of dracut's `ip=` parameter:
```text
ip=<node_ip>::<gateway>:<subnetmask>::<device_name>:none::<node_mac>
```
This forces the Linux kernel / dracut to assign this specific MAC address to the network interface at boot time. Consequently:
1. The LPAR boots with the exact MAC address specified in `all.yaml`.
2. The Agent-Based Installer's `agent-config.yaml` matches this MAC address under `interfaces[].macAddress` and NMState `mac-address`.
3. The Agent installer correctly identifies the host and assigns the static IP configuration.

## Generated agent-config.yaml Example

### For LPAR Installation

```yaml
apiVersion: v1alpha1
kind: AgentConfig
metadata:
  name: ocp-cluster
rendezvousIP: 192.168.1.10

hosts:
  - hostname: "control-1"
    role: master
    rootDeviceHints:
      deviceName: /dev/disk/by-path/ccw-0.0.1a00-fc-0x500507680b2a5f7e-lun-0x4000000000000000
    interfaces:
      - name: eth0
        macAddress: "52:54:00:11:22:31"
    networkConfig:
      # ... network configuration ...

  - hostname: "control-2"
    role: master
    rootDeviceHints:
      deviceName: /dev/disk/by-path/ccw-0.0.1a00-fc-0x500507680b2a5f7e-lun-0x4001000000000000
    interfaces:
      - name: eth0
        macAddress: "52:54:00:11:22:32"
    networkConfig:
      # ... network configuration ...

  - hostname: "compute-1"
    role: worker
    rootDeviceHints:
      deviceName: /dev/disk/by-path/ccw-0.0.1a00-fc-0x500507680b2a5f7e-lun-0x4002000000000000
    interfaces:
      - name: eth0
        macAddress: "52:54:00:11:22:33"
    networkConfig:
      # ... network configuration ...
```

### For KVM Installation (No rootDeviceHints)

```yaml
apiVersion: v1alpha1
kind: AgentConfig
metadata:
  name: ocp-cluster
rendezvousIP: 

hosts:
  - hostname: "control-1"
    role: master
    # No rootDeviceHints for KVM
    interfaces:
      - name: eth0
        macAddress: ""
    networkConfig:
      # ... network configuration ...
```

## Running the Playbooks

### Complete LPAR ABI Installation

```bash
# Run the master playbook for ABI
ansible-playbook playbooks/master_playbook_for_abi.yaml
```

This will:
1. Setup the environment (playbook 0)
2. Skip KVM host setup (only for installation_type: kvm)
3. Create bastion (playbook 4)
4. Setup bastion (playbook 5)
5. Create ABI cluster with rootDeviceHints for LPAR (create_abi_cluster.yaml)
6. Monitor installation (monitor_create_abi_cluster.yaml)

### Individual Playbooks

```bash
# 1. Setup bastion (same for KVM and LPAR)
ansible-playbook playbooks/4_create_bastion.yaml
ansible-playbook playbooks/5_setup_bastion.yaml

# 2. Create ABI cluster (generates agent-config.yaml with rootDeviceHints for LPAR)
ansible-playbook playbooks/create_abi_cluster.yaml

# 3. Monitor installation
ansible-playbook playbooks/monitor_create_abi_cluster.yaml
```

## Troubleshooting

### Issue: rootDeviceHints not appearing in agent-config.yaml

**Check**:
1. Verify `installation_type: lpar` is set in `all.yaml`
2. Ensure each node's host_vars file exists and has `lpar.storage_group_1` configured
3. Verify `lpar.storage_group_1.type: fcp` is set
4. Check that node names in `env.cluster.nodes.control.vm_name` match host_vars filenames

### Issue: Wrong device path in rootDeviceHints

**Verify**:
- `dev_num` format: Should be without "0.0." prefix (e.g., "1a00" not "0.0.1a00")
- `storage_wwpn[0]` format: Should include "0x" prefix (e.g., "0x500507680b2a5f7e")
- `lun_name` format: Should include "0x" prefix (e.g., "0x4000000000000000")

### Issue: Template fails to load host_vars

**Solution**:
Ensure host_vars files are named exactly as specified in `env.cluster.nodes.control.vm_name` and `env.cluster.nodes.compute.vm_name` arrays.

Example:
```yaml
# In all.yaml
env:
  cluster:
    nodes:
      control:
        vm_name:
          - control-1  # Must match: host_vars/control-1.yaml
          - control-2  # Must match: host_vars/control-2.yaml
```

## DASD Storage Support

Currently, the implementation focuses on FCP storage. For DASD storage:

```yaml
lpar:
  storage_group_1:
    type: dasd
    dev_num: "0190"
```

The rootDeviceHints for DASD would be:
```yaml
rootDeviceHints:
  deviceName: /dev/dasda
```

**Note**: DASD support for ABI rootDeviceHints can be added if needed. Contact the maintainers for implementation.

## Summary

✅ **For KVM**: No changes needed, rootDeviceHints are automatically excluded  
✅ **For LPAR**: Set `installation_type: lpar` and configure `lpar.storage_group_1` in each node's host_vars  
✅ **Automatic**: Template generates correct rootDeviceHints based on FCP storage configuration  
✅ **Reusable**: Same storage configuration used for both booting and ABI installation  

## References

- [OpenShift Agent-Based Installer Documentation](https://docs.openshift.com/container-platform/latest/installing/installing_with_agent_based_installer/preparing-to-install-with-agent-based-installer.html)
- [IBM Z Storage Configuration](https://www.ibm.com/docs/en/linux-on-systems?topic=devices-fibre-channel-protocol)
- [Main Project Documentation](https://ibm.github.io/Ansible-OpenShift-Provisioning/)
