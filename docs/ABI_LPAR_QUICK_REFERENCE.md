# ABI LPAR Quick Reference Card

## 🚀 Quick Start

### Step 1: Set Installation Type
**File**: `inventories/default/group_vars/all.yaml`
```yaml
installation_type: lpar

abi:
  flag: True
  boot_method: pxe
```

### Step 2: Configure Storage for Each Node
**File**: `inventories/default/host_vars/{node-name}.yaml`
```yaml
lpar:
  storage_group_1:
    type: fcp
    dev_num: "1a00"
    storage_wwpn:
      - "0x500507680b2a5f7e"
    lun_name: "0x4000000000000000"
```

### Step 3: Run Playbook
```bash
ansible-playbook playbooks/master_playbook_for_abi.yaml
```

---

## 📋 Configuration Checklist

- [ ] Set `installation_type: lpar` in all.yaml
- [ ] Set `abi.flag: True` in all.yaml
- [ ] Configure `env.cluster.nodes.control.mac` (and compute `.mac`) in all.yaml
  - **RoCE / DPM:** Use physical or DPM assigned MAC address
  - **Non-DPM with OSA/HiperSockets:** Use a **randomly generated MAC address** (e.g., `52:54:00:xx:yy:zz`)
- [ ] Configure `lpar.storage_group_1` in each node's host_vars
  - **FCP**: set `type: fcp`, `dev_num`, `storage_wwpn`, `lun_name`
  - **DASD**: set `type: dasd`, `dev_num` (bare hex, e.g. `"4401"` — no `0.0.` prefix)
- [ ] Configure `lpar.livedisk` in each node's host_vars
  - `livedisktype: dasd` or `scsi`
  - `devicenr`: DASD address of the Ubuntu live disk (e.g. `"4400"`)
  - `livedisk_root_pass: "{{ vault_livedisk_root_pass }}"` — verify this value is correct
- [ ] Set `vault_livedisk_root_pass` in `secrets.yaml` (case-sensitive)
- [ ] Set `vault_hmc_pass` in `secrets.yaml`
- [ ] Set `env.bastion.networking.hmc_domain` in all.yaml if HMC hostname is in a subdomain
- [ ] Node names in all.yaml match host_vars filenames
- [ ] `env.cluster.nodes.control.hostname` values are short names (domain appended automatically)

---

## 🔧 Storage Configuration Format

### Required Fields
| Field | Format | Example |
|-------|--------|---------|
| `dev_num` | 4-digit hex (no prefix) | `"1a00"` |
| `storage_wwpn[0]` | Hex with 0x prefix | `"0x500507680b2a5f7e"` |
| `lun_name` | Hex with 0x prefix | `"0x4000000000000000"` |

### Generated Device Path
```
/dev/disk/by-path/ccw-0.0.{dev_num}-fc-{wwpn}-lun-{lun_name}
```

**Example Output**:
```
/dev/disk/by-path/ccw-0.0.1a00-fc-0x500507680b2a5f7e-lun-0x4000000000000000
```

---

## 📝 Example Configurations

### Control Node
**File**: `host_vars/control-1.yaml`
```yaml
lpar:
  storage_group_1:
    name: storage_group_1
    type: fcp
    storage_wwpn:
      - "0x500507680b2a5f7e"
      - "0x500507680b2a5f7f"
    dev_num: "1a00"
    lun_name: "0x4000000000000000"
```

### Compute Node
**File**: `host_vars/compute-1.yaml`
```yaml
lpar:
  storage_group_1:
    name: storage_group_1
    type: fcp
    storage_wwpn:
      - "0x500507680b2a5f7e"
      - "0x500507680b2a5f7f"
    dev_num: "1a00"
    lun_name: "0x4002000000000000"  # Different LUN
```

---

## 🔍 Verification

### Check Generated agent-config.yaml
**Location**: `~/ansible_workdir/agent-config.yaml` on bastion

**Expected for LPAR**:
```yaml
hosts:
  - hostname: "control-1"
    role: master
    rootDeviceHints:
      deviceName: /dev/disk/by-path/ccw-0.0.1a00-fc-...
```

**Expected for KVM**:
```yaml
hosts:
  - hostname: "control-1"
    role: master
    # No rootDeviceHints
```

---

## ⚠️ Common Issues

### Issue: No rootDeviceHints in agent-config.yaml
**Solution**:
- ✅ Verify `installation_type: lpar`
- ✅ Check `lpar.storage_group_1.type: fcp` or `dasd`
- ✅ Ensure host_vars file exists for each node

### Issue: Wrong device path
**Solution**:
- ✅ FCP dev_num: Use `"1a00"` NOT `"0.0.1a00"`
- ✅ DASD dev_num: Use `"4401"` NOT `"0.0.4401"` — template adds `0.0.` prefix
- ✅ wwpn (FCP): Include `"0x"` prefix
- ✅ lun_name (FCP): Include `"0x"` prefix

### Issue: Login incorrect on live disk
**Solution**:
- ✅ Verify `vault_livedisk_root_pass` exactly — it is **case-sensitive**
- ✅ Test manually via HMC REST `list-os-messages` / `send-os-command`
- ✅ See `docs/troubleshooting-lpar-abi-boot.md` §6

### Issue: boot_lpar_abi.py hangs at HMC login
**Solution**:
- ✅ Previous failed runs may have exhausted HMC session slots
- ✅ Log into HMC GUI → User Management → user → Active Sessions → delete all
- ✅ See `docs/troubleshooting-lpar-abi-boot.md` §5

### Issue: stomp.exception.ConnectFailedException
**Solution**:
- ✅ This is fixed automatically by `patch_tessia_baselib` (patch `rest_os_messages`)
- ✅ If it recurs, run `5_setup_bastion.yaml` to re-apply all patches
- ✅ See `docs/troubleshooting-lpar-abi-boot.md` §1

### Issue: Template error loading host_vars
**Solution**:
- ✅ Node name in `env.cluster.nodes.control.vm_name` must match host_vars filename
- ✅ Example: `vm_name: control-1` → file: `host_vars/control-1.yaml`

---

## 🎯 Key Differences: KVM vs LPAR

| Feature | KVM | LPAR |
|---------|-----|------|
| rootDeviceHints | ❌ Not needed | ✅ Required |
| Storage Config | Virtual disks | FCP/DASD |
| Device Path | Auto-detected | Must specify |
| host_vars Required | Optional | **Required** |

---

## 📚 Related Documentation

- **Full Guide**: `docs/abi-lpar-configuration.md`
- **Implementation Details**: `docs/IMPLEMENTATION_SUMMARY_ABI_LPAR.md`
- **Boot Troubleshooting**: `docs/troubleshooting-lpar-abi-boot.md`
- **Main Docs**: https://ibm.github.io/Ansible-OpenShift-Provisioning/

---

## 🔗 Playbook Flow

```
master_playbook_for_abi.yaml
  ├─ 0_setup.yaml (Setup environment)
  ├─ 4_create_bastion.yaml (Create bastion)
  ├─ 5_setup_bastion.yaml (Setup bastion)
  ├─ create_abi_cluster.yaml
  │   ├─ prepare_configs (Generate agent-config.yaml with rootDeviceHints)
  │   ├─ create_agent (Generate installation images)
  │   └─ boot_abi_agents (Boot nodes)
  └─ monitor_create_abi_cluster.yaml (Monitor installation)
```

---

## 💡 Pro Tips

1. **Reuse Configuration**: The same `lpar.storage_group_1` is used for both booting and ABI installation
2. **Multiple Nodes**: Each node can have different storage configuration
3. **Multipath**: List all WWPNs in `storage_wwpn` array, but only first is used for rootDeviceHints
4. **Validation**: Check generated agent-config.yaml before running create_agent role

---

## 🆘 Need Help?

- **Troubleshooting**: See `docs/abi-lpar-configuration.md` → Troubleshooting section
- **GitHub Issues**: https://github.com/IBM/Ansible-OpenShift-Provisioning/issues
- **Documentation**: https://ibm.github.io/Ansible-OpenShift-Provisioning/

---

**Version**: 2.3.0+  
**Last Updated**: 2026-04-05
