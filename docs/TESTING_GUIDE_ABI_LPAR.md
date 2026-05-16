# Testing Guide: ABI LPAR Implementation

## Overview

This guide helps you test the ABI LPAR implementation up to image generation to verify that `rootDeviceHints` are correctly added to the agent-config.yaml file.

## Test Scope

We'll test up to and including image generation:
1. ✅ Bastion setup (no changes, should work as before)
2. ✅ agent-config.yaml generation with rootDeviceHints
3. ✅ Image generation (PXE or ISO)
4. ⏸️ LPAR booting (test later after validation)

## Prerequisites

Before testing, ensure you have:
- [ ] Bastion node created and accessible
- [ ] LPAR nodes defined in inventory
- [ ] FCP storage configuration available for each LPAR node
- [ ] OpenShift pull secret configured

## Test Setup

### 1. Configure Installation Type

**File**: `inventories/default/group_vars/all.yaml`

```yaml
installation_type: lpar  # Critical: Must be 'lpar' not 'kvm'

abi:
  flag: True
  ansible_workdir: 'ansible_workdir'
  ocp_installer_version: '4.18.8'
  ocp_installer_base_url: 'https://mirror.openshift.com/pub/openshift-v4'
  architecture: multi  # or s390x based on your environment
  boot_method: pxe     # or iso
```

### 2. Configure LPAR Storage for Each Node

Create/update host_vars for each control and compute node.

**Example**: `inventories/default/host_vars/control-1.yaml`

```yaml
# ... other configuration ...

lpar:
  name: control-1-lpar
  storage_group_1:
    name: storage_group_1
    type: fcp  # Must be 'fcp' for rootDeviceHints
    storage_wwpn:
      - "0x500507680b2a5f7e"  # Replace with your actual WWPN
      - "0x500507680b2a5f7f"  # Additional paths for multipath
    dev_num: "1a00"  # Replace with your FCP device number
    lun_name: "0x4000000000000000"  # Replace with your LUN ID
```

**Important**: Repeat for all control and compute nodes with their respective storage configurations.

### 3. Verify Node Names Match

Ensure node names in all.yaml match host_vars filenames:

```yaml
# In all.yaml
env:
  cluster:
    nodes:
      control:
        vm_name:
          - control-1  # Must match: host_vars/control-1.yaml
          - control-2  # Must match: host_vars/control-2.yaml
          - control-3  # Must match: host_vars/control-3.yaml
```

## Testing Steps

### Step 1: Setup Bastion (If Not Already Done)

```bash
# Run bastion setup playbooks
ansible-playbook playbooks/4_create_bastion.yaml
ansible-playbook playbooks/5_setup_bastion.yaml
```

**Expected Result**: Bastion created and configured successfully (no changes from existing behavior)

### Step 2: Generate agent-config.yaml

```bash
# Run only the ABI cluster creation playbook
ansible-playbook playbooks/create_abi_cluster.yaml
```

This will:
1. Run `prepare_configs` role → Generate agent-config.yaml
2. Run `create_agent` role → Generate installation images
3. Attempt to boot agents (you can stop here for testing)

**Alternative**: Run only the prepare_configs role:

```bash
# SSH to bastion
ssh <bastion-user>@<bastion-ip>

# Run prepare_configs tasks manually
cd /path/to/ansible
ansible-playbook -i inventories/default playbooks/create_abi_cluster.yaml --tags prepare_configs
```

### Step 3: Verify agent-config.yaml

**On Bastion**, check the generated file:

```bash
ssh <bastion-user>@<bastion-ip>
cat ~/ansible_workdir/agent-config.yaml
```

### Expected Output for LPAR

```yaml
apiVersion: v1alpha1
kind: AgentConfig
metadata:
  name: <your-cluster-name>
rendezvousIP: <first-control-node-ip>

hosts:
  - hostname: "control-1"
    role: master
    rootDeviceHints:
      deviceName: /dev/disk/by-path/ccw-0.0.1a00-fc-0x500507680b2a5f7e-lun-0x4000000000000000
    interfaces:
      - name: eth0
        macAddress: "02:00:00:00:00:01"
    networkConfig:
      # ... network configuration ...

  - hostname: "control-2"
    role: master
    rootDeviceHints:
      deviceName: /dev/disk/by-path/ccw-0.0.1a00-fc-0x500507680b2a5f7e-lun-0x4001000000000000
    interfaces:
      - name: eth0
        macAddress: "02:00:00:00:00:02"
    networkConfig:
      # ... network configuration ...

  # ... more nodes ...
```

### Step 4: Verify Image Generation

Check that images were created successfully:

```bash
# On bastion
ls -lh ~/ansible_workdir/boot-artifacts/
```

**Expected files for PXE**:
- `agent.s390x-initrd.img`
- `agent.s390x-vmlinuz` (or `agent.s390x-kernel.img`)
- `agent.s390x-rootfs.img`

**Expected files for ISO**:
- `agent.s390x.iso`

Also verify files were copied to web server:

```bash
ls -lh /var/www/html/
```

## Validation Checklist

### ✅ Configuration Validation

- [ ] `installation_type: lpar` is set in all.yaml
- [ ] `abi.flag: True` is set
- [ ] Each node has host_vars file with `lpar.storage_group_1` configured
- [ ] `storage_group_1.type: fcp` is set for each node
- [ ] `dev_num`, `storage_wwpn`, and `lun_name` are properly formatted
- [ ] Node names in all.yaml match host_vars filenames

### ✅ Generated agent-config.yaml Validation

- [ ] File exists at `~/ansible_workdir/agent-config.yaml` on bastion
- [ ] Each host entry has `rootDeviceHints` section
- [ ] `deviceName` follows format: `/dev/disk/by-path/ccw-0.0.{dev_num}-fc-{wwpn}-lun-{lun}`
- [ ] Device paths are unique for each node (different LUNs)
- [ ] All control nodes have `role: master`
- [ ] All compute nodes have `role: worker`

### ✅ Image Generation Validation

- [ ] Images created in `~/ansible_workdir/boot-artifacts/`
- [ ] Images copied to `/var/www/html/`
- [ ] No errors in playbook output
- [ ] File sizes are reasonable (initrd ~100MB, rootfs ~1GB+)

## Test Cases

### Test Case 1: Single Control Node

**Configuration**:
```yaml
# all.yaml
installation_type: lpar
env:
  cluster:
    nodes:
      control:
        vm_name: [control-1]
        ip: [192.168.1.10]
        mac: [02:00:00:00:00:01]
        hostname: [control-1]

# host_vars/control-1.yaml
lpar:
  storage_group_1:
    type: fcp
    dev_num: "1a00"
    storage_wwpn: ["0x500507680b2a5f7e"]
    lun_name: "0x4000000000000000"
```

**Expected agent-config.yaml**:
```yaml
hosts:
  - hostname: "control-1"
    role: master
    rootDeviceHints:
      deviceName: /dev/disk/by-path/ccw-0.0.1a00-fc-0x500507680b2a5f7e-lun-0x4000000000000000
```

### Test Case 2: Three Control Nodes with Different LUNs

**Configuration**:
```yaml
# host_vars/control-1.yaml
lpar:
  storage_group_1:
    lun_name: "0x4000000000000000"

# host_vars/control-2.yaml
lpar:
  storage_group_1:
    lun_name: "0x4001000000000000"

# host_vars/control-3.yaml
lpar:
  storage_group_1:
    lun_name: "0x4002000000000000"
```

**Expected**: Each node gets unique rootDeviceHints with different LUN IDs

### Test Case 3: Control + Compute Nodes

**Expected**: Both control and compute nodes have rootDeviceHints with their respective storage configurations

## Troubleshooting

### Issue: Template Error - Cannot Load host_vars

**Error Message**:
```
fatal: [bastion]: FAILED! => {"msg": "An unhandled exception occurred..."}
```

**Solution**:
1. Check that host_vars file exists for each node
2. Verify filename matches exactly: `host_vars/control-1.yaml` (not `control-1.yml`)
3. Ensure YAML syntax is valid in host_vars files

**Debug Command**:
```bash
# Check if file exists
ls -la inventories/default/host_vars/control-1.yaml

# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('inventories/default/host_vars/control-1.yaml'))"
```

### Issue: No rootDeviceHints in agent-config.yaml

**Possible Causes**:
1. `installation_type` is not set to `lpar`
2. `lpar.storage_group_1.type` is not `fcp`
3. host_vars file missing or incorrectly named

**Debug Steps**:
```bash
# On bastion, check what variables are being used
ansible-playbook playbooks/create_abi_cluster.yaml -vvv | grep -A 10 "installation_type"
```

### Issue: Wrong Device Path Format

**Problem**: Device path doesn't match expected format

**Check**:
- dev_num should be "1a00" NOT "0.0.1a00"
- wwpn should include "0x" prefix: "0x500507680b2a5f7e"
- lun_name should include "0x" prefix: "0x4000000000000000"

### Issue: Image Generation Fails

**Check**:
1. OpenShift installer binary is downloaded
2. Pull secret is valid
3. Network connectivity from bastion
4. Sufficient disk space in ~/ansible_workdir

**Debug**:
```bash
# Check installer
which openshift-install

# Check disk space
df -h ~/ansible_workdir

# Check pull secret
cat ~/.docker/config.json
```

## Comparison Test: KVM vs LPAR

To verify backward compatibility, you can test both:

### KVM Test (Should NOT have rootDeviceHints)

```yaml
installation_type: kvm
abi:
  flag: True
```

**Expected**: agent-config.yaml WITHOUT rootDeviceHints

### LPAR Test (Should have rootDeviceHints)

```yaml
installation_type: lpar
abi:
  flag: True
```

**Expected**: agent-config.yaml WITH rootDeviceHints

## Next Steps After Successful Testing

Once you've verified:
1. ✅ agent-config.yaml has correct rootDeviceHints
2. ✅ Images generated successfully
3. ✅ No errors in playbook execution

You can proceed to:
- Boot LPAR nodes with generated images
- Monitor installation progress
- Complete the full ABI installation

## Reporting Issues

If you encounter issues during testing:

1. **Collect Information**:
   - agent-config.yaml content
   - Playbook output (with -vvv for verbose)
   - host_vars configuration
   - Error messages

2. **Check Documentation**:
   - `docs/abi-lpar-configuration.md` - Full guide
   - `docs/ABI_LPAR_QUICK_REFERENCE.md` - Quick reference

3. **Create GitHub Issue**:
   - Include all collected information
   - Specify OpenShift version
   - Describe expected vs actual behavior

## Success Criteria

✅ **Test is successful if**:
1. Playbook runs without errors
2. agent-config.yaml contains rootDeviceHints for each LPAR node
3. Device paths are correctly formatted
4. Images are generated and copied to web server
5. KVM installations still work without rootDeviceHints (if tested)

---

**Good luck with testing!** 🚀

Feel free to provide feedback on the implementation after testing.