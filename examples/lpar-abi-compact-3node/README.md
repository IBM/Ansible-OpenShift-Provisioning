# Example: 3-Node Compact OpenShift Cluster on Bare-Metal LPARs (Non-DPM / ABI)

This example inventory demonstrates how to configure an Agent-Based Installer (ABI) deployment for a 3-node compact OpenShift cluster running directly on bare-metal IBM Z / LinuxONE LPARs (non-DPM / Classic PR/SM mode).

---

## Directory Structure

```text
examples/lpar-abi-compact-3node/
├── group_vars/
│   └── all.yaml              # Main cluster and environment configuration
├── host_vars/
│   ├── lpar-node-1.yaml      # LPAR parameters for Control Node 1
│   ├── lpar-node-2.yaml      # LPAR parameters for Control Node 2
│   └── lpar-node-3.yaml      # LPAR parameters for Control Node 3
├── hosts                     # Ansible inventory mapping bastion and file server
└── README.md
```

---

## Key Configuration Concepts

### 1. 3-Node Compact Cluster (No Separate Compute Nodes or Bootstrap VM)
- **No Bootstrap Node:** The Agent-Based Installer runs the bootstrap service internally in-memory. Section 7 (`bootstrap`) is omitted from `all.yaml`.
- **No Compute Nodes:** In a compact 3-node cluster, control nodes act as both control plane and worker nodes. Section 9 (`compute`) is omitted from `all.yaml`.

### 2. Matching `vm_name` to `host_vars/<vm_name>.yaml`
In `group_vars/all.yaml`:
```yaml
env:
  cluster:
    nodes:
      control:
        vm_name:
          - lpar-node-1
          - lpar-node-2
          - lpar-node-3
```
Each entry in `vm_name` must have a corresponding file `host_vars/<vm_name>.yaml`.

### 3. MAC Address Generation for Non-DPM Environments
For non-DPM LPARs with OSA-Express or HiperSockets in Layer 2 mode, the Linux kernel generates a transient random MAC address on each boot. To ensure the OpenShift Agent can match network interfaces consistently and apply static IP settings:
- Provide a **randomly generated locally administered unicast MAC address** in `env.cluster.nodes.control.mac` in `all.yaml`.
- The `boot_LPAR_abi` playbook writes this MAC into the kernel command line parameters (`genericdvd.prm`) via dracut `ip=...::<mac>`, assigning it to the interface at boot time.

#### Generating a Random MAC Address
Run any of the following:

**Python:**
```bash
python3 -c "import random; print(':'.join(['52', '54', '00'] + [f'{random.randint(0,255):02x}' for _ in range(3)]))"
```

**Bash:**
```bash
printf '52:54:00:%02x:%02x:%02x\n' $((RANDOM%256)) $((RANDOM%256)) $((RANDOM%256))
```

---

## Running the Deployment

Copy this example inventory into `inventories/default/` (or pass `-i examples/lpar-abi-compact-3node/hosts`):

```bash
# 1. Setup inventory & bastion SSH keys
ansible-playbook -i examples/lpar-abi-compact-3node/hosts playbooks/0_setup.yaml

# 2. Configure bastion DNS and HAProxy
ansible-playbook -i examples/lpar-abi-compact-3node/hosts playbooks/5_setup_bastion.yaml

# 3. Create the ABI ISO/PXE artifacts and boot LPARs
ansible-playbook -i examples/lpar-abi-compact-3node/hosts playbooks/create_abi_cluster.yaml

# 4. Monitor installation until complete
ansible-playbook -i examples/lpar-abi-compact-3node/hosts playbooks/monitor_create_abi_cluster.yaml
```
