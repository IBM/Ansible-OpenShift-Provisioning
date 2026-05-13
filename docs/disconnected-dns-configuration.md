# DNS Configuration for Disconnected Mirroring

## Overview

When running disconnected installations with the bastion acting as both the DNS server and the mirroring host, proper DNS configuration is critical:

1. The bastion needs internet access to download OCP images during mirroring
2. The bastion's DNS service (named) is configured in `5_setup_bastion.yaml`
3. The `disconnected_setup_oc_mirror.yaml` playbook runs **before** `5_setup_bastion.yaml`
4. The bastion must have working DNS from the moment it's created

## The Problem

### Scenario
- KVM host has IP forwarding enabled for NAT
- Bastion can reach the internet through the KVM host
- If `/etc/resolv.conf` points to the bastion itself before named is configured, DNS resolution fails
- DNS queries fail, preventing downloads from mirror.openshift.com

### Error Symptoms
```
Could not find or access '/tmp/oc-mirror-downloads/openshift-client-linux.tar.gz'
```

Or:

```
Failed to connect to mirror.openshift.com: Temporary failure in name resolution
```

## The Solution

The solution is implemented at bastion creation time in the kickstart configuration, ensuring DNS works from the first boot:

### 1. During Bastion Creation (`4_create_bastion.yaml`)
The kickstart configuration automatically sets up the correct nameserver:

**If `env.bastion.options.dns = true` AND `nameserver2` is defined:**
- Uses `nameserver2` (external DNS) as the primary nameserver
- This allows internet access for mirroring before the local DNS service is configured

**If `env.bastion.options.dns = false` OR `nameserver2` is not defined:**
- Uses `nameserver1` as the primary nameserver
- Adds `nameserver2` as secondary if defined

### 2. During Mirroring (`disconnected_setup_oc_mirror.yaml`)
- DNS is already working from bastion creation
- Downloads proceed successfully using the configured nameserver
- No DNS reconfiguration needed

### 3. Final DNS Setup (`5_setup_bastion.yaml`)
- Configures the named service on the bastion
- Updates `/etc/resolv.conf` to use the bastion as primary DNS
- Sets up DNS forwarding to external nameservers

## Configuration Requirements

### In your `all.yaml`, configure nameservers properly:

```yaml
env:
  bastion:
    networking:
      nameserver1: 192.168.122.2  # Bastion IP (will be DNS server after setup)
      nameserver2: 8.8.8.8         # External DNS - REQUIRED for disconnected with DNS on bastion
      forwarder: 8.8.8.8           # External DNS forwarder
      base_domain: example.com
    options:
      dns: true                     # Enable DNS service on bastion
  
  cluster:
    networking:
      nameserver1: 192.168.122.2  # Bastion IP (DNS server)
      nameserver2: 8.8.8.8         # External DNS (optional, for redundancy)
      base_domain: example.com
```

### Critical Configuration Rules:

**For Disconnected Installations with DNS on Bastion:**
- **`env.bastion.options.dns`**: Must be `true`
- **`env.bastion.networking.nameserver2`**: **REQUIRED** - Must be an external DNS server (e.g., 8.8.8.8, 1.1.1.1, or corporate DNS)
- **`env.bastion.networking.nameserver1`**: Should be the bastion IP
- **`env.bastion.networking.forwarder`**: Should match nameserver2

**For Installations without DNS on Bastion:**
- **`env.bastion.options.dns`**: Set to `false`
- **`env.bastion.networking.nameserver1`**: Use your external DNS server
- **`env.bastion.networking.nameserver2`**: Optional secondary DNS

### Why nameserver2 is Required:

When `env.bastion.options.dns = true`, the kickstart configuration uses `nameserver2` as the initial DNS server because:
1. The bastion's named service isn't configured yet
2. Internet access is needed for mirroring operations
3. Using the bastion IP (nameserver1) would fail since named isn't running

## How It Works

### Playbook Execution Order

The correct order for disconnected installations:

1. **`4_create_bastion.yaml`** - Creates the bastion VM
   - Kickstart configures `/etc/resolv.conf` with external DNS (nameserver2)
   - Bastion boots with working DNS resolution
   
2. **`disconnected_setup_oc_mirror.yaml`** - Downloads and mirrors OCP content
   - DNS already works from bastion creation
   - Downloads proceed without DNS issues
   
3. **`5_setup_bastion.yaml`** - Configures bastion services including DNS
   - Sets up named service
   - Updates `/etc/resolv.conf` to use bastion as primary DNS
   - Configures DNS forwarding to external nameservers

### DNS Configuration Timeline

```
Bastion Creation (4_create_bastion.yaml)
├─ Kickstart sets: nameserver 8.8.8.8
└─ Bastion boots with working external DNS

Mirroring (disconnected_setup_oc_mirror.yaml)
├─ DNS works (using 8.8.8.8)
├─ Downloads succeed
└─ No DNS reconfiguration needed

Final Setup (5_setup_bastion.yaml)
├─ named service configured
├─ /etc/resolv.conf updated to: nameserver 192.168.122.2
└─ DNS forwarding to 8.8.8.8 configured
```

## Implementation Details

### Files Modified:

1. **`roles/create_bastion/templates/bastion-ks.cfg.j2`** (RHEL 8)
   - Kickstart now checks `env.bastion.options.dns` setting
   - Uses `nameserver2` if DNS will be enabled on bastion
   - Uses `nameserver1` if DNS will not be enabled on bastion

2. **`roles/create_bastion/templates/rhel9-bastion-ks.cfg.j2`** (RHEL 9)
   - Same logic as RHEL 8 kickstart
   - Ensures consistent behavior across RHEL versions

### Kickstart Logic:

```jinja2
{% if env.bastion.options.dns and env.bastion.networking.nameserver2 is defined %}
  # Use external DNS (nameserver2) for initial boot
  --nameserver={{ env.bastion.networking.nameserver2 }}
{% else %}
  # Use primary DNS (nameserver1) and optional secondary
  --nameserver={{ env.bastion.networking.nameserver1 }}{{ (',' + nameserver2) if nameserver2 is defined }}
{% endif %}
```

## Manual DNS Verification

If you need to verify DNS configuration on the bastion after creation:

```bash
# SSH to bastion
ssh root@bastion-ip

# Check current DNS configuration
cat /etc/resolv.conf

# Should show external DNS if env.bastion.options.dns = true
# Expected: nameserver 8.8.8.8 (or your nameserver2 value)

# Test DNS resolution
nslookup mirror.openshift.com
dig mirror.openshift.com

# Verify internet connectivity
curl -I https://mirror.openshift.com
```

If DNS is not working correctly, check:
1. Bastion was created with correct `env.bastion.networking.nameserver2` value
2. `env.bastion.options.dns` is set to `true` in `all.yaml`
3. KVM host has IP forwarding enabled
4. Network routing is configured correctly

## Troubleshooting

### Issue: DNS still not working after configuration

**Check NetworkManager status:**
```bash
systemctl status NetworkManager
```

**Verify resolv.conf:**
```bash
cat /etc/resolv.conf
```

**Test DNS resolution:**
```bash
nslookup mirror.openshift.com
dig mirror.openshift.com
```

### Issue: NetworkManager keeps overwriting resolv.conf

**Ensure the config file exists:**
```bash
cat /etc/NetworkManager/conf.d/90-dns-none.conf
```

Should contain:
```
[main]
dns=none
```

**Restart NetworkManager:**
```bash
systemctl restart NetworkManager
```

### Issue: Can't reach internet even with correct DNS

**Check routing:**
```bash
ip route show
ping 8.8.8.8
```

**Verify KVM host IP forwarding:**
```bash
# On KVM host
sysctl net.ipv4.ip_forward
# Should return: net.ipv4.ip_forward = 1
```

**Check NAT/masquerading on KVM host:**
```bash
# On KVM host
iptables -t nat -L -n -v | grep MASQUERADE
```

## Best Practices

1. **Always define nameserver2** in your configuration for disconnected scenarios
2. **Use reliable external DNS** servers (Google DNS, Cloudflare, or corporate DNS)
3. **Test DNS resolution** before running mirroring operations
4. **Keep the playbook execution order** as documented
5. **Don't skip the DNS configuration steps** - they're critical for success

## Related Documentation

- [Troubleshooting Internet Access](troubleshooting-disconnected-internet-access.md)
- [Troubleshooting oc-mirror](troubleshooting-oc-mirror-no-release-images.md)
- [Disconnected Installation Guide](run-the-playbooks-for-disconnected-install.md)