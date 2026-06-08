# Troubleshooting: oc-mirror Timeout Issues

## Problem
When running the `disconnected_setup_oc_mirror.yaml` playbook, the mirroring operation times out with an error like:
```
async task did not complete within the requested time
```

Or the playbook appears to hang during the mirroring phase.

## Root Cause
The mirroring operation takes longer than the configured `async_timeout` value. Large mirroring operations (multiple OpenShift versions, full operator catalogs, or many additional images) can take several hours to complete.

## Solution

### 1. Adjust the Timeout Value

Edit your `disconnected.yaml` configuration and increase the `async_timeout` value:

```yaml
disconnected:
  mirroring:
    oc_mirror:
      oc_mirror_args:
        async_timeout: 28800  # Increase based on your needs
        async_poll: 30
```

### 2. Recommended Timeout Values

Choose a timeout based on what you're mirroring:

#### Small Mirroring Operation (2 hours = 7200 seconds)
**Use when mirroring:**
- Single OpenShift version
- Few operators (1-3)
- Minimal additional images

```yaml
async_timeout: 7200
```

#### Medium Mirroring Operation (4 hours = 14400 seconds) - **DEFAULT**
**Use when mirroring:**
- 2-3 OpenShift versions
- Several operators (4-10)
- Some additional images

```yaml
async_timeout: 14400
```

#### Large Mirroring Operation (8 hours = 28800 seconds)
**Use when mirroring:**
- Full channel (many versions)
- Many operators (10-20)
- Multiple additional images
- Full operator catalogs

```yaml
async_timeout: 28800
```

#### Very Large Mirroring Operation (12 hours = 43200 seconds)
**Use when mirroring:**
- Multiple channels
- Full operator catalogs with `full: true`
- Extensive additional images
- Multiple architectures

```yaml
async_timeout: 43200
```

### 3. Estimating Your Timeout Needs

Consider these factors when setting your timeout:

**OpenShift Platform Images:**
- Each version: ~5-10 GB
- Time per version: 15-30 minutes (depending on network speed)

**Operator Catalogs:**
- Single operator: 100 MB - 2 GB
- Full catalog (`full: true`): 50-100 GB
- Time for full catalog: 2-4 hours

**Additional Images:**
- Varies widely based on image size
- Add 10-20 minutes per additional image

**Network Speed Impact:**
- Fast connection (100+ Mbps): Use lower timeout values
- Moderate connection (10-100 Mbps): Use recommended values
- Slow connection (<10 Mbps): Double the recommended values

### 4. Configuration Examples

#### Example 1: Minimal Setup (Single Version, No Operators)
```yaml
disconnected:
  mirroring:
    oc_mirror:
      oc_mirror_args:
        async_timeout: 7200  # 2 hours
        async_poll: 30
      image_set:
        mirror:
          platform:
            architectures:
              - s390x
            channels:
              - name: stable-4.21
                minVersion: 4.21.14
                maxVersion: 4.21.14
          operators: []  # No operators
          additionalImages: []
```

#### Example 2: Production Setup (Multiple Versions, Several Operators)
```yaml
disconnected:
  mirroring:
    oc_mirror:
      oc_mirror_args:
        async_timeout: 28800  # 8 hours
        async_poll: 30
      image_set:
        mirror:
          platform:
            architectures:
              - s390x
            channels:
              - name: stable-4.21
                minVersion: 4.21.0
                maxVersion: 4.21.14
          operators:
            - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.21
              packages:
                - name: serverless-operator
                - name: openshift-gitops-operator
                - name: odf-operator
          additionalImages:
            - name: registry.redhat.io/ubi9/ubi:latest
```

#### Example 3: Full Mirror (Everything)
```yaml
disconnected:
  mirroring:
    oc_mirror:
      oc_mirror_args:
        async_timeout: 43200  # 12 hours
        async_poll: 30
      image_set:
        mirror:
          platform:
            architectures:
              - s390x
            channels:
              - name: stable-4.21
                full: true  # All versions in channel
          operators:
            - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.21
              full: true  # All operators
```

### 5. Monitoring Progress

While the mirroring is running, you can monitor progress on the bastion:

```bash
# SSH to bastion
ssh root@bastion-ip

# Watch oc-mirror logs
tail -f /opt/oc-mirror/oc-mirror.log

# Check disk space (mirroring requires significant space)
df -h /opt/registry/data

# Monitor network activity
iftop -i eth0
```

### 6. If Timeout Still Occurs

If you've increased the timeout but still experience issues:

#### Check Available Disk Space
```bash
# On bastion
df -h /opt/registry/data
df -h /opt/oc-mirror
```

Mirroring requires:
- Registry storage: 100-500 GB depending on content
- Workspace: 50-100 GB for temporary files

#### Check Network Stability
```bash
# Test sustained connectivity
ping -c 100 quay.io
curl -I https://registry.redhat.io
```

#### Review oc-mirror Logs
```bash
# On bastion
cd /opt/oc-mirror
cat oc-mirror-workspace/logs/oc-mirror.log
```

Look for:
- Network errors
- Authentication failures
- Disk space issues

#### Use Continue on Error (Carefully)
For very large mirrors, you can enable continue-on-error:

```yaml
oc_mirror_args:
  continue_on_error: true  # Continue even if some images fail
  async_timeout: 43200
```

**Warning**: This may result in incomplete mirroring. Review logs carefully.

### 7. Alternative: Split the Mirroring

For extremely large mirrors, consider splitting into multiple runs:

**Run 1: Platform Images Only**
```yaml
mirror:
  platform:
    channels:
      - name: stable-4.21
        minVersion: 4.21.14
        maxVersion: 4.21.14
  operators: []
```

**Run 2: Operators**
```yaml
mirror:
  platform:
    channels: []  # Skip platform
  operators:
    - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.21
      packages:
        - name: serverless-operator
```

### 8. Best Practices

1. **Start Small**: Begin with a single version and few operators
2. **Test First**: Use `--dry-run` to estimate size and time
3. **Monitor Resources**: Watch disk space and network during mirroring
4. **Plan Timing**: Run large mirrors during off-hours
5. **Document**: Keep notes on how long different configurations take
6. **Incremental Updates**: After initial mirror, updates are much faster

### 9. Timeout Calculation Formula

Use this formula to estimate your timeout:

```
timeout = (platform_versions × 1800) + (operators × 600) + (additional_images × 300) + 3600

Where:
- platform_versions: Number of OpenShift versions to mirror
- operators: Number of operator packages (or 100 if full: true)
- additional_images: Number of additional images
- 3600: Base overhead (1 hour)
```

**Example Calculation:**
- 5 OpenShift versions
- 10 operators
- 5 additional images

```
timeout = (5 × 1800) + (10 × 600) + (5 × 300) + 3600
        = 9000 + 6000 + 1500 + 3600
        = 20100 seconds (≈ 5.6 hours)

Recommended: 28800 seconds (8 hours) for safety margin
```

## Quick Reference

| Content Size | Timeout (seconds) | Timeout (hours) | Use Case |
|--------------|-------------------|-----------------|----------|
| Small | 7200 | 2 | Single version, few operators |
| Medium | 14400 | 4 | Multiple versions, several operators |
| Large | 28800 | 8 | Full channel, many operators |
| Very Large | 43200 | 12 | Multiple channels, full catalogs |
| Extreme | 86400 | 24 | Everything, multiple architectures |

## Related Documentation

- [DNS Configuration for Disconnected Mirroring](disconnected-dns-configuration.md)
- [oc-mirror "No Release Images Found" Error](troubleshooting-oc-mirror-no-release-images.md)
- [Disconnected Installation Guide](run-the-playbooks-for-disconnected-install.md)