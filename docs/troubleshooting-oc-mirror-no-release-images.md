# Troubleshooting: oc-mirror "no release images found" Error

## Problem
When running `oc-mirror`, you get the error:
```
[ERROR] : [Executor] collection error: [GetReleaseReferenceImages] no release images found
```

## Root Cause
This error occurs when oc-mirror cannot find any release images matching your version specification in the imageset-config.yaml. Common causes:

1. **Version doesn't exist**: The minVersion/maxVersion specified doesn't exist in the channel
2. **Wrong channel name**: The channel name doesn't match available channels
3. **Architecture mismatch**: The specified architecture doesn't have releases in that version
4. **Network issues**: Cannot reach the source registry to query available versions

## Solution Steps

### 1. Find Available Versions

First, determine what versions are actually available for your architecture and channel:

```bash
# SSH to bastion
ssh root@bastion-ip

# List available versions in stable-4.21 channel for s390x
oc adm release info quay.io/openshift-release-dev/ocp-release:4.21-s390x

# Or check what's available in the channel
curl -s https://mirror.openshift.com/pub/openshift-v4/s390x/clients/ocp/stable-4.21/ | grep -oP '4\.21\.\d+' | sort -V | uniq

# For multi-arch
curl -s https://mirror.openshift.com/pub/openshift-v4/multi/clients/ocp/stable-4.21/ | grep -oP '4\.21\.\d+' | sort -V | uniq
```

### 2. Check Your Current Configuration

Review your `disconnected.yaml` configuration:

```yaml
mirror:
  platform:
    architectures:
      - s390x  # or 'multi' for multi-arch
    channels:
      - name: stable-4.21
        full: false
        minVersion: 4.21.21  # ← This version must exist!
        maxVersion: 4.21.21
```

### 3. Common Version Issues

#### Issue: Version Too New
**Problem**: You specified `4.21.21` but only `4.21.0` through `4.21.14` exist.

**Solution**: Use an existing version:
```yaml
channels:
  - name: stable-4.21
    full: false
    minVersion: 4.21.0
    maxVersion: 4.21.14
```

#### Issue: Using Latest/Newest
**Problem**: You want the latest version but don't know the exact number.

**Solution**: Either use `full: true` to get all versions, or omit min/maxVersion:
```yaml
channels:
  - name: stable-4.21
    # Option 1: Get all versions (large download)
    full: true

    # Option 2: Get latest only (omit min/max)
    # (This gets the latest in the channel)
```

#### Issue: Architecture Mismatch
**Problem**: Using `s390x` architecture but the version only exists for `multi`.

**Solution**: Check which architecture tag exists:
```bash
# Check if s390x-specific tag exists
skopeo inspect docker://quay.io/openshift-release-dev/ocp-release:4.21.14-s390x

# Check if multi-arch tag exists
skopeo inspect docker://quay.io/openshift-release-dev/ocp-release:4.21.14-multi
```

Then update your configuration:
```yaml
mirror:
  platform:
    architectures:
      - multi  # Use 'multi' instead of 's390x' if that's what's available
```

### 4. Recommended Configuration for s390x

For s390x systems, use this proven configuration:

```yaml
disconnected:
  mirroring:
    oc_mirror:
      image_set:
        apiVersion: mirror.openshift.io/v2alpha1
        mirror:
          platform:
            architectures:
              - s390x
            channels:
              - name: stable-4.21
                full: false
                minVersion: 4.21.0  # Use first available version
                maxVersion: 4.21.14  # Use last known good version
```

### 5. Test Your Configuration

Before running the full mirror, test with a dry-run:

```bash
# SSH to bastion
cd /opt/oc-mirror

# Run dry-run to validate configuration
oc mirror --v2 --config imageset-config.yaml \
  --workspace file:///opt/oc-mirror/oc-mirror-workspace \
  docker://192.168.122.2:5000 \
  --dest-tls-verify=false \
  --dry-run
```

If successful, you'll see:
```
[INFO] : 🔍 collecting release images...
[INFO] : found X release images
```

If it fails with "no release images found", the version doesn't exist.

### 6. Alternative: Use Specific Release Image

Instead of using channels, you can specify an exact release image:

```yaml
mirror:
  platform:
    architectures:
      - s390x
    channels:
      - name: stable-4.21
        type: ocp
        full: false
    # Or use graph to specify exact release
    graph: true
```

### 7. Check oc-mirror Version Compatibility

Ensure your oc-mirror version supports the OpenShift version you're trying to mirror:

```bash
# Check oc-mirror version
oc mirror version

# Check if it supports v2 API
oc mirror --help | grep -i v2
```

For OpenShift 4.21, you need oc-mirror v2 (which you're using based on the error).

## Quick Fix for Your Current Error

Based on your error, try this immediate fix:

1. **Option A: Use a range of versions** (recommended)
```yaml
channels:
  - name: stable-4.21
    full: false
    minVersion: 4.21.0
    maxVersion: 4.21.14
```

2. **Option B: Get all versions in channel**
```yaml
channels:
  - name: stable-4.21
    full: true
```

3. **Option C: Omit version constraints** (gets latest)
```yaml
channels:
  - name: stable-4.21
```

## Verify Available Versions Online

Check Red Hat's official mirror to see what's available:

- s390x: https://mirror.openshift.com/pub/openshift-v4/s390x/clients/ocp/stable-4.21/
- multi-arch: https://mirror.openshift.com/pub/openshift-v4/multi/clients/ocp/stable-4.21/

Look for directories with version numbers like `4.21.0`, `4.21.1`, etc.

## After Fixing Configuration

1. Update your `disconnected.yaml` with correct versions
2. Re-run the playbook:
```bash
ansible-playbook -i inventories/default playbooks/disconnected_setup_oc_mirror.yaml
```

3. The imageset-config.yaml will be regenerated with correct versions
4. oc-mirror should now find and mirror the release images

## Additional Resources

- [OpenShift Mirror Documentation](https://docs.openshift.com/container-platform/latest/installing/disconnected_install/installing-mirroring-disconnected.html)
- [oc-mirror Plugin Documentation](https://docs.openshift.com/container-platform/latest/installing/disconnected_install/installing-mirroring-creating-registry.html)
- [Available OpenShift Releases](https://mirror.openshift.com/pub/openshift-v4/)