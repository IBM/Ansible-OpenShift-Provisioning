# Multi-Architecture Compute Node Addition

## Overview

This document explains how to add compute nodes to an OpenShift cluster, including:
- Single node addition using `create_compute_node.yaml`
- Multiple nodes addition using `create_multiple_compute_nodes.yaml`
- Multi-architecture scenarios (e.g., adding x86_64 nodes to an s390x cluster)

## Scenario Analysis

### Your Setup
- **Primary Cluster**: 3 KVM servers running s390x architecture
- **Additional Node**: x86_64 compute node on a separate x86 KVM server
- **Infrastructure**: Bastion with DNS and HAProxy services

## Automated Components

The [`create_compute_node.yaml`](../playbooks/create_compute_node.yaml) playbook **automatically handles**:

### 1. DNS Configuration ✅ AUTOMATED

**What happens:**
- Line 92-96: Calls [`dns_update`](../roles/dns_update/tasks/main.yaml) role with `add` command
- Adds forward DNS entry to `/var/named/<cluster>.db`
- Adds reverse DNS entry to `/var/named/<cluster>.rev`
- Restarts named service to apply changes

**DNS entries added:**
```
# Forward DNS
worker-x86.cluster.example.com. IN A 192.168.122.50

# Reverse DNS
50     IN      PTR     worker-x86.cluster.example.com.
```

**Condition:** Only runs if `env.bastion.options.dns = true`

### 2. HAProxy Configuration ✅ AUTOMATED

**What happens:**
- Line 110-113: Calls [`haproxy_update`](../roles/haproxy_update/tasks/main.yaml) role with `add` command
- Adds node to port 80 backend in `/etc/haproxy/haproxy.cfg`
- Adds node to port 443 backend in `/etc/haproxy/haproxy.cfg`
- Restarts haproxy service to apply changes

**HAProxy entries added:**
```
# Port 80 backend
  server worker-x86 worker-x86.cluster.example.com:80 check inter 1s

# Port 443 backend
  server worker-x86 worker-x86.cluster.example.com:443 check inter 1s
```

**Condition:** Only runs if `env.bastion.options.loadbalancer.on_bastion = true`

### 3. Architecture-Specific RHCOS Images ✅ AUTOMATED

**What happens:**
- Line 40-70: Queries OpenShift machine-config-operator for correct RHCOS images
- Automatically detects architecture from `day2_compute_node.host_arch`
- Downloads architecture-specific images:
  - RHCOS kernel
  - RHCOS initrd
  - RHCOS rootfs
  - RHCOS ISO

**Example for x86_64:**
```bash
# Automatically fetches from machine-config-operator
rhcos_live_kernel: rhcos-4.21.0-x86_64-live-kernel-x86_64
rhcos_live_initrd: rhcos-4.21.0-x86_64-live-initramfs.x86_64.img
rhcos_live_rootfs: rhcos-4.21.0-x86_64-live-rootfs.x86_64.img
```

### 4. VM Creation on Target KVM Host ✅ AUTOMATED

**What happens:**
- Line 98-101: Delegates VM creation to specified KVM host
- Uses `param_compute_node.hostname` to target correct KVM server
- Creates VM with architecture-specific settings
- Configures network with DNS servers from `env.cluster.networking.nameserver1/2`

**Network configuration in VM:**
```bash
# Line 83 in create_compute_node/tasks/main.yaml
--extra-args "nameserver={{ env.cluster.networking.nameserver1 }},{{ env.cluster.networking.nameserver2 }}"
```

### 5. Certificate Approval ✅ AUTOMATED

**What happens:**
- Line 103-107: Automatically approves CSRs for the new node
- Waits for node to join cluster
- Approves final certificates
- Cleans up after approval

## X86 KVM Host DNS Configuration

### Question: Does the x86 KVM host have correct resolv.conf?

**Answer: It depends on how the x86 KVM host was configured.**

The `create_compute_node.yaml` playbook does **NOT** configure `/etc/resolv.conf` on the x86 KVM host itself. It only configures DNS for the **VM being created**.

### Manual Configuration Required for X86 KVM Host

If your x86 KVM host needs to resolve cluster hostnames, you must manually configure it:

```bash
# SSH to x86 KVM host
ssh user@x86-kvm-host

# Configure DNS to point to bastion
sudo cat > /etc/resolv.conf << EOF
search cluster.example.com
nameserver 192.168.122.2  # Bastion IP
nameserver 8.8.8.8        # External DNS as backup
EOF

# Disable NetworkManager DNS management (if needed)
sudo cat > /etc/NetworkManager/conf.d/90-dns-none.conf << EOF
[main]
dns=none
EOF

sudo systemctl restart NetworkManager
```

## Adding Multiple Nodes

### Why Add Multiple Nodes at Once?

**Benefits:**
- **Efficiency**: Add 5-10 nodes in one operation instead of running playbook multiple times
- **Consistency**: All nodes configured with same settings
- **Time-saving**: Parallel certificate approval and validation
- **Easier tracking**: Single operation to monitor

### Using create_multiple_compute_nodes.yaml

**1. Create configuration file with multiple nodes:**

```yaml
# extra-multiple-nodes.yml
day2_compute_nodes:
  # X86 nodes on x86 KVM host
  - vm_name: worker-x86-1
    vm_hostname: worker-x86-1
    vm_ip: 192.168.122.50
    vm_ipv6: "fd00::50"
    vm_mac: "52:54:00:ab:cd:50"
    vm_interface: enp1s0
    hostname: x86-kvm-host.example.com
    host_user: root
    host_arch: x86_64
    
  - vm_name: worker-x86-2
    vm_hostname: worker-x86-2
    vm_ip: 192.168.122.51
    vm_ipv6: "fd00::51"
    vm_mac: "52:54:00:ab:cd:51"
    vm_interface: enp1s0
    hostname: x86-kvm-host.example.com
    host_user: root
    host_arch: x86_64
  
  # S390X nodes on s390x KVM hosts
  - vm_name: worker-s390x-4
    vm_hostname: worker-s390x-4
    vm_ip: 192.168.122.52
    vm_interface: enc1
    hostname: s390x-kvm-host1.example.com
    host_user: root
    host_arch: s390x
    
  - vm_name: worker-s390x-5
    vm_hostname: worker-s390x-5
    vm_ip: 192.168.122.53
    vm_interface: enc1
    hostname: s390x-kvm-host2.example.com
    host_user: root
    host_arch: s390x
```

**2. Run the playbook:**

```bash
ansible-playbook -i inventories/default \
  playbooks/create_multiple_compute_nodes.yaml \
  --extra-vars "@extra-multiple-nodes.yml"
```

**3. What happens:**
- Displays list of nodes to be added
- Prompts for confirmation (if more than 1 node)
- Processes each node sequentially:
  - Downloads architecture-specific RHCOS images
  - Updates DNS
  - Creates VM
  - Approves certificates
  - Updates HAProxy
- Displays summary of all added nodes

**4. Monitor progress:**
```bash
# In another terminal, watch nodes joining
watch oc get nodes

# Watch CSRs being approved
watch oc get csr
```

### Single vs Multiple Node Addition

| Feature | Single Node | Multiple Nodes |
|---------|-------------|----------------|
| Playbook | `create_compute_node.yaml` | `create_multiple_compute_nodes.yaml` |
| Configuration | `day2_compute_node: {...}` | `day2_compute_nodes: [...]` |
| Execution | One node per run | Multiple nodes per run |
| Confirmation | No prompt | Prompts if >1 node |
| Best for | Testing, single additions | Bulk additions, scaling |

### Example Scenarios

**Scenario 1: Add 3 x86 nodes to s390x cluster**
```yaml
day2_compute_nodes:
  - {vm_name: worker-x86-1, vm_hostname: worker-x86-1, vm_ip: 192.168.122.50, hostname: x86-kvm.example.com, host_user: root, host_arch: x86_64, vm_interface: enp1s0}
  - {vm_name: worker-x86-2, vm_hostname: worker-x86-2, vm_ip: 192.168.122.51, hostname: x86-kvm.example.com, host_user: root, host_arch: x86_64, vm_interface: enp1s0}
  - {vm_name: worker-x86-3, vm_hostname: worker-x86-3, vm_ip: 192.168.122.52, hostname: x86-kvm.example.com, host_user: root, host_arch: x86_64, vm_interface: enp1s0}
```

**Scenario 2: Add mixed architecture nodes**
```yaml
day2_compute_nodes:
  - {vm_name: worker-x86-1, vm_hostname: worker-x86-1, vm_ip: 192.168.122.50, hostname: x86-kvm.example.com, host_user: root, host_arch: x86_64, vm_interface: enp1s0}
  - {vm_name: worker-arm-1, vm_hostname: worker-arm-1, vm_ip: 192.168.122.51, hostname: arm-kvm.example.com, host_user: root, host_arch: aarch64, vm_interface: enp1s0}
  - {vm_name: worker-s390x-1, vm_hostname: worker-s390x-1, vm_ip: 192.168.122.52, hostname: s390x-kvm.example.com, host_user: root, host_arch: s390x, vm_interface: enc1}
```

**Scenario 3: Scale existing architecture**
```yaml
day2_compute_nodes:
  - {vm_name: worker-4, vm_hostname: worker-4, vm_ip: 192.168.122.54, hostname: kvm-host1.example.com, host_user: root, host_arch: s390x, vm_interface: enc1}
  - {vm_name: worker-5, vm_hostname: worker-5, vm_ip: 192.168.122.55, hostname: kvm-host2.example.com, host_user: root, host_arch: s390x, vm_interface: enc1}
  - {vm_name: worker-6, vm_hostname: worker-6, vm_ip: 192.168.122.56, hostname: kvm-host3.example.com, host_user: root, host_arch: s390x, vm_interface: enc1}
```

## Complete Workflow

### Prerequisites

1. **X86 KVM Host Setup:**
   ```bash
   # Ensure x86 KVM host can reach bastion
   ping 192.168.122.2
   
   # Ensure x86 KVM host has libvirt configured
   virsh list --all
   
   # Ensure storage pool exists
   virsh pool-list
   ```

2. **Network Connectivity:**
   - X86 KVM host must be on same network as bastion
   - X86 KVM host must be able to reach file server for RHCOS images
   - VMs created on x86 KVM host must be able to reach bastion

3. **Create Node Configuration File:**
   ```yaml
   # extra-worker-x86.yml
   day2_compute_node:
     vm_name: worker-x86-1
     vm_hostname: worker-x86-1
     vm_ip: 192.168.122.50
     vm_ipv6: "fd00::50"  # If using IPv6
     vm_mac: "52:54:00:ab:cd:50"  # If using DHCP
     vm_interface: enp1s0
     hostname: x86-kvm-host.example.com  # X86 KVM host FQDN
     host_user: root  # User on x86 KVM host
     host_arch: x86_64  # Architecture
   ```

### Execution Steps

1. **Run the playbook:**
   ```bash
   ansible-playbook -i inventories/default \
     playbooks/create_compute_node.yaml \
     --extra-vars "@extra-worker-x86.yml"
   ```

2. **What happens automatically:**
   - ✅ Queries OpenShift for x86_64 RHCOS images
   - ✅ Downloads x86_64 RHCOS images to bastion
   - ✅ Adds DNS entries for new node
   - ✅ Creates VM on x86 KVM host
   - ✅ VM boots with correct DNS configuration
   - ✅ VM joins cluster
   - ✅ Certificates approved
   - ✅ HAProxy updated with new node

3. **Verify:**
   ```bash
   # Check node joined cluster
   oc get nodes
   
   # Check node architecture
   oc get node worker-x86-1 -o jsonpath='{.status.nodeInfo.architecture}'
   # Should output: amd64
   
   # Check DNS resolution
   nslookup worker-x86-1.cluster.example.com
   
   # Check HAProxy configuration
   ssh root@bastion
   grep worker-x86-1 /etc/haproxy/haproxy.cfg
   ```

## Manual Steps Required

### 1. X86 KVM Host DNS Configuration (If Needed)

**When needed:**
- If x86 KVM host needs to resolve cluster hostnames
- If x86 KVM host needs to access cluster services

**How to configure:**
See "Manual Configuration Required for X86 KVM Host" section above.

### 2. Firewall Rules (If Needed)

**When needed:**
- If firewall blocks traffic between x86 KVM host and bastion
- If firewall blocks traffic between VMs on different KVM hosts

**How to configure:**
```bash
# On x86 KVM host
sudo firewall-cmd --permanent --add-service=libvirt
sudo firewall-cmd --permanent --add-port=16509/tcp  # libvirt TLS
sudo firewall-cmd --reload

# Allow VM traffic
sudo firewall-cmd --permanent --zone=libvirt --add-service=dns
sudo firewall-cmd --permanent --zone=libvirt --add-service=dhcp
sudo firewall-cmd --reload
```

### 3. SSH Key Distribution (If Needed)

**When needed:**
- If Ansible controller cannot SSH to x86 KVM host

**How to configure:**
```bash
# From Ansible controller
ssh-copy-id user@x86-kvm-host.example.com
```

## Architecture-Specific Considerations

### S390X to X86_64 Addition

**Supported:** ✅ Yes, fully automated

**Requirements:**
- OpenShift 4.14+ (multi-arch support)
- Correct `host_arch: x86_64` in node configuration
- X86 KVM host accessible from Ansible controller

**Automatic handling:**
- Different RHCOS images downloaded
- Different CPU model flags used (`--cpu host` disabled for aarch64)
- Architecture-specific variables loaded from `roles/common/vars/<arch>/vars.yaml`

### Other Architecture Combinations

| Primary Cluster | Additional Node | Supported | Notes |
|----------------|-----------------|-----------|-------|
| s390x | x86_64 | ✅ Yes | Fully automated |
| s390x | aarch64 | ✅ Yes | Fully automated |
| x86_64 | s390x | ✅ Yes | Fully automated |
| x86_64 | aarch64 | ✅ Yes | Fully automated |
| aarch64 | x86_64 | ✅ Yes | Fully automated |
| aarch64 | s390x | ✅ Yes | Fully automated |

## Troubleshooting

### Issue: VM Cannot Resolve Cluster Hostnames

**Symptom:**
```
Failed to fetch ignition config: could not resolve bastion.cluster.example.com
```

**Cause:** VM's DNS not configured correctly

**Solution:**
Check `env.cluster.networking.nameserver1` in `all.yaml` points to bastion:
```yaml
env:
  cluster:
    networking:
      nameserver1: 192.168.122.2  # Must be bastion IP
      nameserver2: 8.8.8.8         # External DNS as backup
```

### Issue: Cannot Create VM on X86 KVM Host

**Symptom:**
```
Failed to connect to x86-kvm-host.example.com
```

**Cause:** SSH connectivity issue

**Solution:**
```bash
# Test SSH connectivity
ssh user@x86-kvm-host.example.com

# Check SSH key
ssh-copy-id user@x86-kvm-host.example.com

# Verify in node config
day2_compute_node:
  hostname: x86-kvm-host.example.com  # Must be reachable
  host_user: root  # Must have libvirt permissions
```

### Issue: Wrong Architecture RHCOS Images

**Symptom:**
```
VM fails to boot or boots with wrong architecture
```

**Cause:** Incorrect `host_arch` in node configuration

**Solution:**
```yaml
day2_compute_node:
  host_arch: x86_64  # Must match target KVM host architecture
  # Options: x86_64, s390x, aarch64, ppc64le
```

### Issue: DNS Not Updated

**Symptom:**
```
nslookup worker-x86-1.cluster.example.com
# Returns: NXDOMAIN
```

**Cause:** DNS role not executed or failed

**Solution:**
```bash
# Check if DNS is enabled
grep "dns:" inventories/default/group_vars/all.yaml
# Should show: dns: true

# Manually add DNS entry
ssh root@bastion
vi /var/named/cluster.db
# Add: worker-x86-1.cluster.example.com. IN A 192.168.122.50
systemctl restart named
```

### Issue: HAProxy Not Updated

**Symptom:**
```
curl http://worker-x86-1.cluster.example.com
# Connection refused or timeout
```

**Cause:** HAProxy role not executed or failed

**Solution:**
```bash
# Check if HAProxy is enabled
grep "loadbalancer:" inventories/default/group_vars/all.yaml
# Should show: on_bastion: true

# Manually add HAProxy entry
ssh root@bastion
vi /etc/haproxy/haproxy.cfg
# Add under #80 section:
#   server worker-x86-1 worker-x86-1.cluster.example.com:80 check inter 1s
# Add under #443 section:
#   server worker-x86-1 worker-x86-1.cluster.example.com:443 check inter 1s
systemctl restart haproxy
```

## Summary

### Fully Automated ✅
1. DNS configuration (forward and reverse)
2. HAProxy configuration (ports 80 and 443)
3. Architecture-specific RHCOS image download
4. VM creation on target KVM host
5. Network configuration in VM
6. Certificate approval
7. Node joining cluster

### Manual Configuration Required ⚠️
1. X86 KVM host `/etc/resolv.conf` (if host needs cluster DNS resolution)
2. Firewall rules (if blocking traffic)
3. SSH key distribution (if not already configured)
4. Network connectivity between KVM hosts

### Not Automated ❌
- X86 KVM host DNS configuration
- X86 KVM host firewall configuration
- Initial SSH access setup to x86 KVM host

## Best Practices

1. **Test connectivity first:**
   ```bash
   ansible x86-kvm-host -m ping
   ```

2. **Verify DNS before adding nodes:**
   ```bash
   ssh root@bastion
   nslookup cluster-api.cluster.example.com
   ```

3. **Check available resources on target KVM host:**
   ```bash
   ssh user@x86-kvm-host
   virsh nodeinfo
   df -h
   ```

4. **Use consistent naming:**
   - VM names: `worker-<arch>-<number>`
   - Hostnames: `worker-<arch>-<number>`

5. **Document your multi-arch setup:**
   - Keep track of which nodes are on which KVM hosts
   - Document architecture distribution
   - Note any special configurations

## Related Documentation

- [Main Playbook Documentation](run-the-playbooks.md)
- [DNS Configuration](disconnected-dns-configuration.md)
- [Troubleshooting Guide](troubleshooting.md)