# Troubleshooting Internet Access for Disconnected Setup

## Problem
When running the `disconnected_setup_oc_mirror.yaml` playbook, downloads fail with errors like:
```
Could not find or access '/tmp/oc-mirror-downloads/openshift-client-linux.tar.gz'
```

This happens because the bastion cannot reach the internet to download required files.

## Root Cause
Even though the KVM host has IP forwarding enabled, the bastion VM may lack:
- Proper DNS configuration
- Correct default gateway
- Required firewall rules

## Solution Steps

### 1. Verify DNS Configuration on Bastion

SSH to the bastion and check DNS:
```bash
cat /etc/resolv.conf
```

Should contain valid nameservers, for example:
```
nameserver 8.8.8.8
nameserver 8.8.4.4
```

If missing or incorrect, add DNS servers:
```bash
echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf
echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf
```

For persistent DNS configuration on RHEL/CentOS:
```bash
sudo nmcli con mod "System eth0" ipv4.dns "8.8.8.8 8.8.4.4"
sudo nmcli con up "System eth0"
```

### 2. Test DNS Resolution

```bash
nslookup mirror.openshift.com
# or
dig mirror.openshift.com
```

Should return IP addresses. If it fails, DNS is not working.

### 3. Verify Default Gateway

Check routing table:
```bash
ip route show
```

Should show a default route, for example:
```
default via 192.168.122.1 dev eth0
```

If missing, add default gateway (replace with your KVM host IP):
```bash
sudo ip route add default via 192.168.122.1
```

For persistent configuration:
```bash
sudo nmcli con mod "System eth0" ipv4.gateway "192.168.122.1"
sudo nmcli con up "System eth0"
```

### 4. Verify KVM Host IP Forwarding

On the KVM host, check if IP forwarding is enabled:
```bash
sysctl net.ipv4.ip_forward
```

Should return `net.ipv4.ip_forward = 1`. If not:
```bash
sudo sysctl -w net.ipv4.ip_forward=1
# Make it persistent
echo "net.ipv4.ip_forward = 1" | sudo tee -a /etc/sysctl.conf
```

### 5. Configure NAT/Masquerading on KVM Host

The KVM host needs to masquerade traffic from the bastion:
```bash
# Check current iptables rules
sudo iptables -t nat -L -n -v

# Add masquerading rule (replace virbr0 with your bridge interface)
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i virbr0 -o eth0 -j ACCEPT
sudo iptables -A FORWARD -i eth0 -o virbr0 -m state --state RELATED,ESTABLISHED -j ACCEPT

# Save rules (RHEL/CentOS)
sudo iptables-save | sudo tee /etc/sysconfig/iptables

# Or use firewalld
sudo firewall-cmd --permanent --add-masquerade
sudo firewall-cmd --reload
```

### 6. Test Internet Connectivity from Bastion

```bash
# Test DNS and connectivity
curl -I https://mirror.openshift.com

# Test with verbose output
curl -v https://mirror.openshift.com

# Test specific download URL
curl -I https://mirror.openshift.com/pub/openshift-v4/s390x/clients/ocp/stable/oc-mirror.tar.gz
```

### 7. Check Firewall on Bastion

Ensure the bastion firewall allows outbound connections:
```bash
# Check firewall status
sudo firewall-cmd --state

# If needed, allow outbound HTTPS
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 8. Verify Network Configuration

Check the bastion's network interface configuration:
```bash
ip addr show
ip route show
nmcli con show
```

Ensure:
- IP address is assigned
- Subnet mask is correct
- Gateway is reachable: `ping 192.168.122.1`

## Updated Playbook Behavior

The updated `disconnected_download_oc_mirror` role now includes:

1. **Pre-flight connectivity check**: Tests connection to mirror.openshift.com before attempting downloads
2. **Detailed error messages**: Provides troubleshooting steps if connectivity fails
3. **File verification**: Confirms files exist before attempting to copy them
4. **Better error handling**: Fails fast with clear messages instead of continuing with missing files

## Running the Playbook Again

After fixing connectivity issues, run the playbook:
```bash
ansible-playbook -i inventories/default playbooks/disconnected_setup_oc_mirror.yaml
```

The playbook will now:
1. Test internet connectivity first
2. Show clear error messages if connectivity fails
3. Provide troubleshooting guidance
4. Only proceed with downloads if connectivity is confirmed

## Alternative: Manual Download

If internet access cannot be configured on the bastion, you can manually download files:

1. Download on a machine with internet access:
```bash
# Create download directory
mkdir -p /tmp/oc-mirror-downloads

# Download files
cd /tmp/oc-mirror-downloads
curl -LO https://mirror.openshift.com/pub/openshift-v4/s390x/clients/ocp/stable/oc-mirror.tar.gz
curl -LO https://mirror.openshift.com/pub/openshift-v4/s390x/clients/ocp/stable-4.21/openshift-client-linux.tar.gz
curl -LO https://mirror.openshift.com/pub/openshift-v4/s390x/clients/ocp/stable-4.21/openshift-install-linux.tar.gz
curl -LO https://mirror.openshift.com/pub/openshift-v4/s390x/dependencies/rhcos/4.21/latest/rhcos-live-rootfs.s390x.img
```

2. Transfer to bastion:
```bash
scp /tmp/oc-mirror-downloads/* root@bastion-ip:/tmp/oc-mirror-downloads/
```

3. Skip the download tasks and run only the copy/setup tasks:
```bash
ansible-playbook -i inventories/default playbooks/disconnected_setup_oc_mirror.yaml --skip-tags download
```

## Common Issues

### Issue: "Temporary failure in name resolution"
**Cause**: DNS not configured
**Fix**: Add nameservers to /etc/resolv.conf (see step 1)

### Issue: "No route to host"
**Cause**: Missing default gateway
**Fix**: Add default route (see step 3)

### Issue: "Connection timed out"
**Cause**: KVM host not forwarding packets or firewall blocking
**Fix**: Enable IP forwarding and NAT on KVM host (see steps 4-5)

### Issue: Downloads succeed but files not found
**Cause**: Files downloaded to wrong location or permissions issue
**Fix**: Check `disconnected.yaml` download_dir setting and file permissions

## Support

For additional help, check:
- [Main troubleshooting guide](troubleshooting.md)
- [Disconnected installation documentation](run-the-playbooks-for-disconnected-install.md)
- OpenShift documentation: https://docs.openshift.com/container-platform/latest/installing/disconnected_install/index.html