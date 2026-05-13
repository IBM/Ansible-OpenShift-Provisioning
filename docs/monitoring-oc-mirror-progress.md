# Monitoring OC-Mirror Progress in Real-Time

## Overview

When running the `disconnected_setup_oc_mirror.yaml` playbook, the mirroring operation can take several hours. This guide explains how to monitor the progress in real-time to see which images are being pulled.

## What Changed

The `disconnected_mirror_ocp_bastion` role now includes:

1. **Progress Logging**: All oc-mirror output is logged to a file
2. **Periodic Updates**: Ansible displays progress updates every poll interval
3. **Monitoring Script**: A helper script for real-time monitoring with color-coded output
4. **Summary Display**: Shows the last 50 lines of output when complete

## Monitoring Methods

### Method 1: Ansible Playbook Output (Automatic)

When you run the playbook, you'll see:

```
TASK [disconnected_mirror_ocp_bastion : Display mirroring progress information]
ok: [bastion] => {
    "msg": [
        "==========================================",
        "OC-Mirror is running in the background",
        "==========================================",
        "Progress log: /opt/oc-mirror/oc-mirror-progress.log",
        "Job ID: 123456.78910",
        "",
        "To monitor progress in real-time, SSH to bastion and run:",
        "  tail -f /opt/oc-mirror/oc-mirror-progress.log",
        "",
        "Or use this command to see only image pulls:",
        "  tail -f /opt/oc-mirror/oc-mirror-progress.log | grep -E 'mirroring|copying|Pulling|sha256'",
        "",
        "Ansible will check progress every 30 seconds..."
    ]
}
```

Ansible will then check progress periodically and display updates.

### Method 2: SSH to Bastion and Tail the Log

**Basic monitoring:**
```bash
# SSH to bastion
ssh root@bastion-ip

# Watch all output
tail -f /opt/oc-mirror/oc-mirror-progress.log
```

**Filter for image pulls only:**
```bash
# See only image-related messages
tail -f /opt/oc-mirror/oc-mirror-progress.log | grep -E 'mirroring|copying|sha256'
```

**Filter for errors and warnings:**
```bash
# See only errors and warnings
tail -f /opt/oc-mirror/oc-mirror-progress.log | grep -E 'ERROR|WARN'
```

### Method 3: Use the Monitoring Script (Recommended)

The playbook copies a monitoring script to the bastion that provides color-coded, filtered output:

```bash
# SSH to bastion
ssh root@bastion-ip

# Run the monitoring script
cd /opt/oc-mirror
./monitor-oc-mirror.sh
```

**Output example:**
```
==========================================
OC-Mirror Progress Monitor
==========================================
Log file: /opt/oc-mirror/oc-mirror-progress.log
Press Ctrl+C to exit
==========================================

==========================================
Statistics (2026-05-22 10:15:30)
==========================================
Images processed: 127
Errors: 0
Warnings: 2
==========================================

[INFO] collecting release images...
[MIRROR] mirroring platform images
[IMAGE] quay.io/openshift-release-dev/ocp-release@sha256:abc123...
[IMAGE] quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:def456...
[MIRROR] copying image sha256:abc123... to 192.168.122.2:5000/...
```

**Features:**
- Color-coded output (errors in red, warnings in yellow, etc.)
- Periodic statistics display
- Filters out noise, shows only relevant information
- Real-time updates

### Method 4: Monitor from Ansible Controller

While the playbook is running, open another terminal and SSH to bastion:

```bash
# Terminal 1: Running playbook
ansible-playbook playbooks/disconnected_setup_oc_mirror.yaml

# Terminal 2: Monitor progress
ssh root@bastion-ip "tail -f /opt/oc-mirror/oc-mirror-progress.log | grep -E 'mirroring|copying|sha256'"
```

## Understanding the Output

### Key Messages to Look For

**1. Collection Phase:**
```
[INFO] collecting release images...
[INFO] found 150 release images
[INFO] collecting operator images...
```

**2. Mirroring Phase:**
```
mirroring platform images
copying image sha256:abc123... to 192.168.122.2:5000/ocp4/openshift4
```

**3. Image Processing:**
```
sha256:abc123def456... -> 192.168.122.2:5000/ocp4/openshift4@sha256:abc123def456...
```

**4. Completion:**
```
[INFO] mirroring completed successfully
[INFO] mirror time: 2h 15m 30s
```

### Progress Indicators

**Images being processed:**
- Each `sha256:...` line represents one image layer being copied
- Multiple layers per image is normal
- Hundreds or thousands of sha256 lines is expected

**Operator catalogs:**
```
mirroring operator catalog: registry.redhat.io/redhat/redhat-operator-index:v4.21
```

**Additional images:**
```
mirroring additional image: registry.redhat.io/ubi9/ubi:latest
```

## Troubleshooting

### Issue: No Progress Updates

**Symptom:**
```
Ansible shows "TASK [Monitor oc-mirror progress]" but no updates
```

**Cause:** Log file not being created or written to

**Solution:**
```bash
# SSH to bastion
ssh root@bastion-ip

# Check if oc-mirror is running
ps aux | grep oc-mirror

# Check if log file exists
ls -lh /opt/oc-mirror/oc-mirror-progress.log

# Check if log file is being written to
tail -f /opt/oc-mirror/oc-mirror-progress.log
```

### Issue: Mirroring Appears Stuck

**Symptom:**
```
Same image sha256 shown for several minutes
```

**Cause:** Large image layer being downloaded

**Solution:**
- This is normal for large images (500MB-2GB layers)
- Check network activity: `iftop -i eth0` on bastion
- Be patient - large layers take time

### Issue: Many Errors in Log

**Symptom:**
```
[ERROR] failed to copy image sha256:...
[ERROR] connection timeout
```

**Cause:** Network issues or source registry problems

**Solution:**
```bash
# Check if continue-on-error is enabled
grep continue_on_error inventories/default/group_vars/disconnected.yaml

# If not enabled, consider enabling it for large mirrors
# Edit disconnected.yaml:
oc_mirror_args:
  continue_on_error: true
```

### Issue: Want to Stop Mirroring

**To stop gracefully:**
```bash
# SSH to bastion
ssh root@bastion-ip

# Find oc-mirror process
ps aux | grep "oc mirror"

# Send SIGTERM (graceful shutdown)
kill -TERM <pid>

# Wait a few minutes for cleanup
# If it doesn't stop, use SIGKILL
kill -9 <pid>
```

**To resume later:**
- oc-mirror v2 supports resuming from workspace
- Re-run the playbook - it will continue from where it stopped

## Performance Tips

### Monitor Network Usage

```bash
# On bastion
iftop -i eth0

# Or use nload
nload eth0
```

### Monitor Disk Space

```bash
# Check registry storage
df -h /opt/registry/data

# Check workspace
df -h /opt/oc-mirror
```

### Monitor System Resources

```bash
# CPU and memory
htop

# Or use top
top
```

## Log File Location

**Default location:**
```
/opt/oc-mirror/oc-mirror-progress.log
```

**Configured in:**
```yaml
# disconnected.yaml
mirroring:
  bastion:
    working_dir: '/opt/oc-mirror'  # Log will be: <working_dir>/oc-mirror-progress.log
```

## After Mirroring Completes

The playbook will automatically:

1. Display the last 50 lines of output
2. Show completion message
3. Provide next steps

**Manual review:**
```bash
# SSH to bastion
ssh root@bastion-ip

# View full log
less /opt/oc-mirror/oc-mirror-progress.log

# Search for errors
grep ERROR /opt/oc-mirror/oc-mirror-progress.log

# Count images mirrored
grep -c "sha256" /opt/oc-mirror/oc-mirror-progress.log

# View summary
tail -100 /opt/oc-mirror/oc-mirror-progress.log
```

## Example Session

**Terminal 1 - Run playbook:**
```bash
$ ansible-playbook playbooks/disconnected_setup_oc_mirror.yaml

TASK [disconnected_mirror_ocp_bastion : Run oc-mirror v2 to mirror images (async)]
changed: [bastion]

TASK [disconnected_mirror_ocp_bastion : Display mirroring progress information]
ok: [bastion] => {
    "msg": [
        "OC-Mirror is running in the background",
        "Progress log: /opt/oc-mirror/oc-mirror-progress.log",
        "Ansible will check progress every 30 seconds..."
    ]
}

TASK [disconnected_mirror_ocp_bastion : Monitor oc-mirror progress with periodic updates]
FAILED - RETRYING: [bastion]: Monitor oc-mirror progress (240 retries left)
FAILED - RETRYING: [bastion]: Monitor oc-mirror progress (239 retries left)
...
```

**Terminal 2 - Monitor progress:**
```bash
$ ssh root@192.168.122.2
# cd /opt/oc-mirror
# ./monitor-oc-mirror.sh

==========================================
Statistics (2026-05-22 10:30:15)
==========================================
Images processed: 245
Errors: 0
Warnings: 3
==========================================

[MIRROR] mirroring platform images
[IMAGE] quay.io/openshift-release-dev/ocp-release@sha256:abc123...
[IMAGE] quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:def456...
...
```

## Related Documentation

- [Disconnected Installation Guide](run-the-playbooks-for-disconnected-install.md)
- [OC-Mirror Timeout Configuration](troubleshooting-oc-mirror-timeout.md)
- [DNS Configuration](disconnected-dns-configuration.md)
- [Troubleshooting Guide](troubleshooting.md)