# Running Playbooks for Disconnected Installation

This guide explains how to set up and run OpenShift Container Platform (OCP) in disconnected or air-gapped environments using the `disconnected_setup_oc_mirror.yaml` playbook.

## Table of Contents

- [Overview](#overview)
- [Correct Playbook Execution Order](#correct-playbook-execution-order)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Running the Playbook](#running-the-playbook)
- [Roles Overview](#roles-overview)
- [Troubleshooting](#troubleshooting)
- [Advanced Topics](#advanced-topics)

## Overview

In disconnected environments, OpenShift clusters cannot directly access Red Hat's container registries. This solution automates:

1. Setting up a container registry on the bastion host
2. Downloading oc-mirror plugin and OCP client tools
3. Mirroring OCP platform images, operators, and additional images
4. Generating necessary manifests for cluster installation

## Correct Playbook Execution Order

### Standard Installation (UPI - User Provisioned Infrastructure)

For a complete disconnected OpenShift installation from scratch, execute playbooks in this **exact order**:

1. **[`0_setup.yaml`](../playbooks/0_setup.yaml)** - Setup inventory, install Galaxy collections, check disconnected variables
   ```bash
   ansible-playbook -i inventories/default playbooks/0_setup.yaml
   ```

2. **[`1_create_lpar.yaml`](../playbooks/1_create_lpar.yaml)** - Create LPARs (if using HMC/DPM mode)
   ```bash
   ansible-playbook -i inventories/default playbooks/1_create_lpar.yaml
   ```

3. **[`2_create_kvm_host.yaml`](../playbooks/2_create_kvm_host.yaml)** - Boot RHEL on LPARs
   ```bash
   ansible-playbook -i inventories/default playbooks/2_create_kvm_host.yaml
   ```

4. **[`3_setup_kvm_host.yaml`](../playbooks/3_setup_kvm_host.yaml)** - Configure KVM hosts with libvirt, networking, storage
   ```bash
   ansible-playbook -i inventories/default playbooks/3_setup_kvm_host.yaml
   ```

5. **[`4_create_bastion.yaml`](../playbooks/4_create_bastion.yaml)** - Create bastion VM
   ```bash
   ansible-playbook -i inventories/default playbooks/4_create_bastion.yaml
   ```

6. **🆕 [`disconnected_setup_oc_mirror.yaml`](../playbooks/disconnected_setup_oc_mirror.yaml)** - **CRITICAL: Setup registry and mirror images**
   ```bash
   ansible-playbook -i inventories/default playbooks/disconnected_setup_oc_mirror.yaml --ask-vault-pass
   ```
   
   **This playbook MUST run after bastion creation but BEFORE bastion setup because:**
   - ✅ Bastion must exist to host the registry
   - ✅ Registry and mirrored images must be ready before OCP installation files are created
   - ✅ Pull secret is automatically updated in `all.yaml` for use by subsequent playbooks
   - ✅ Generates manifests needed for disconnected cluster installation

7. **[`5_setup_bastion.yaml`](../playbooks/5_setup_bastion.yaml)** - Configure bastion services (DNS, HAProxy, get OCP binaries)
   ```bash
   ansible-playbook -i inventories/default playbooks/5_setup_bastion.yaml
   ```

8. **[`6_create_nodes.yaml`](../playbooks/6_create_nodes.yaml)** - Create and bootstrap cluster nodes
   ```bash
   ansible-playbook -i inventories/default playbooks/6_create_nodes.yaml
   ```

9. **[`7_ocp_verification.yaml`](../playbooks/7_ocp_verification.yaml)** - Verify cluster installation
   ```bash
   ansible-playbook -i inventories/default playbooks/7_ocp_verification.yaml
   ```

10. **[`disconnected_apply_operator_manifests.yaml`](../playbooks/disconnected_apply_operator_manifests.yaml)** - Apply operator manifests to cluster
    ```bash
    ansible-playbook -i inventories/default playbooks/disconnected_apply_operator_manifests.yaml
    ```

### ABI Installation (Agent-Based Installer)

For ABI disconnected installation, execute in this order:

1. **[`0_setup.yaml`](../playbooks/0_setup.yaml)** - Setup inventory and check variables
   ```bash
   ansible-playbook -i inventories/default playbooks/0_setup.yaml
   ```

2. **[`3_setup_kvm_host.yaml`](../playbooks/3_setup_kvm_host.yaml)** - Configure KVM hosts (if using KVM)
   ```bash
   ansible-playbook -i inventories/default playbooks/3_setup_kvm_host.yaml
   ```

3. **[`4_create_bastion.yaml`](../playbooks/4_create_bastion.yaml)** - Create bastion VM
   ```bash
   ansible-playbook -i inventories/default playbooks/4_create_bastion.yaml
   ```

4. **🆕 [`disconnected_setup_oc_mirror.yaml`](../playbooks/disconnected_setup_oc_mirror.yaml)** - Setup registry and mirror images
   ```bash
   ansible-playbook -i inventories/default playbooks/disconnected_setup_oc_mirror.yaml --ask-vault-pass
   ```

5. **[`5_setup_bastion.yaml`](../playbooks/5_setup_bastion.yaml)** - Configure bastion services
   ```bash
   ansible-playbook -i inventories/default playbooks/5_setup_bastion.yaml
   ```

6. **[`create_abi_cluster.yaml`](../playbooks/create_abi_cluster.yaml)** - Create ABI cluster
   ```bash
   ansible-playbook -i inventories/default playbooks/create_abi_cluster.yaml
   ```

7. **[`monitor_create_abi_cluster.yaml`](../playbooks/monitor_create_abi_cluster.yaml)** - Monitor ABI installation
   ```bash
   ansible-playbook -i inventories/default playbooks/monitor_create_abi_cluster.yaml
   ```

### Pre-existing LPAR Installation

If you have pre-existing LPARs with RHEL already installed, skip steps 1-3 and start from step 4:

```bash
# Start from KVM host setup
ansible-playbook -i inventories/default playbooks/3_setup_kvm_host.yaml
# Then continue with steps 5-10 as shown above
```

### Using Master Playbooks

**⚠️ Important**: The current [`site.yaml`](../playbooks/site.yaml) master playbook calls the OLD `disconnected_mirror_artifacts.yaml` playbook. You should update it to use the new `disconnected_setup_oc_mirror.yaml` playbook instead.

**Option 1: Run all standard playbooks at once** (after updating site.yaml):
```bash
ansible-playbook -i inventories/default playbooks/site.yaml --ask-vault-pass
```

**Option 2: Run ABI master playbook** (after updating master_playbook_for_abi.yaml):
```bash
ansible-playbook -i inventories/default playbooks/master_playbook_for_abi.yaml --ask-vault-pass
```

### Critical Timing Notes

**The insertion point for `disconnected_setup_oc_mirror.yaml` is critical:**

```
✅ CORRECT ORDER:
4_create_bastion.yaml → disconnected_setup_oc_mirror.yaml → 5_setup_bastion.yaml

❌ WRONG ORDER:
5_setup_bastion.yaml → disconnected_setup_oc_mirror.yaml (TOO LATE - install-config already created)
disconnected_setup_oc_mirror.yaml → 4_create_bastion.yaml (TOO EARLY - bastion doesn't exist)
```

**Why this order matters:**
1. Bastion must exist to host the container registry
2. Registry must be running before mirroring images
3. Images must be mirrored before creating OCP installation files
4. Pull secret must be updated before `5_setup_bastion.yaml` creates install-config.yaml

### Installation Methods Comparison

This mirroring solution supports both standard and Agent-Based Installer (ABI) installation methods:

| Aspect | Standard Installation | Agent-Based Installer (ABI) |
|--------|----------------------|----------------------------|
| **Playbook** | `6_create_nodes.yaml` | `create_abi_cluster.yaml` |
| **Bootstrap Node** | Required | Not required |
| **Installation Method** | Ignition files | Agent ISO/PXE |
| **Configuration** | Multiple files (install-config, ignition) | Single install-config + agent-config |
| **Disconnected Support** | ✅ Full support | ✅ Full support |
| **Registry Integration** | Via ignition files | Via agent artifacts |
| **Node Discovery** | Manual configuration | Automated discovery |
| **Complexity** | Higher | Lower |
| **Best For** | Traditional deployments | Simplified deployments, edge locations |

Both methods use the same mirrored registry and are fully compatible with `disconnected_setup_oc_mirror.yaml`.

## Architecture

```
Internet → File Server → Bastion → Disconnected Registry → OCP Cluster
           (Download)    (Mirror)   (Local Storage)
```

### Components

- **File Server**: Downloads binaries from the internet (can be same as bastion)
- **Bastion**: Runs oc-mirror to perform the actual mirroring
- **Disconnected Registry**: Container registry on bastion for mirrored images
- **OCP Cluster**: Target OpenShift cluster using mirrored images

## Prerequisites

### System Requirements

#### Bastion Host

**Note**: If you don't have a bastion host yet, you can create one using the project's playbooks:
```bash
# Create the bastion VM
ansible-playbook -i inventories/default playbooks/4_create_bastion.yaml

# Setup the bastion with required packages and configuration
ansible-playbook -i inventories/default playbooks/5_setup_bastion.yaml
```

**Requirements**:
- RHEL 8/9 or compatible Linux distribution
- **Disk Space**:
  - Minimum: 100 GB (single OCP version + limited operators)
  - Recommended: 200 GB (multiple versions + operators)
  - Production: 500 GB+ (full catalog mirroring)
- 4GB RAM minimum (8GB+ recommended for large mirrors)
- Root/sudo access
- s390x architecture support

**Disk Space Breakdown**:
- Registry data (`/opt/registry/data`): 100-150 GB
- oc-mirror workspace (`/opt/oc-mirror`): 50-100 GB
- System and logs: 20-50 GB

#### Network Requirements
- File server must have internet access (or pre-downloaded binaries)
- Bastion must have access to:
  - File server (HTTP/FTP)
  - Source registries (Red Hat registries) during mirroring
  - Target disconnected registry (localhost if on bastion)

### Required Files

Ensure you have:
- Valid Red Hat pull secret
- Ansible inventory configured
- Vault password (if using Ansible Vault)

## Configuration

### Step 1: Enable Disconnected Mode in all.yaml

Edit `inventories/default/group_vars/all.yaml` and set the disconnected mode flag:

```yaml
# Section 1 - Ansible Controller
installation_type: kvm
controller_sudo_pass: "{{ vault_ctl_host_sudo_pass }}"
disconnected_enabled: true  # ⚠️ REQUIRED: Set to true for disconnected installations
```

**Important**: This parameter was moved from `disconnected.yaml` to `all.yaml` under Section 1 - Ansible Controller. The default value is `false`.

### Step 2: Configure secrets.yaml

Add the registry password to `inventories/default/group_vars/secrets.yaml`:

```yaml
vault_registry_password: 'your-secure-password-here'
```

**Security Note**: Use Ansible Vault to encrypt this file:
```bash
ansible-vault encrypt inventories/default/group_vars/secrets.yaml
```

### Step 3: Configure disconnected.yaml

#### Create disconnected.yaml from Template

Copy the template file to create your configuration:

```bash
cp inventories/default/group_vars/disconnected.yaml.template \
   inventories/default/group_vars/disconnected.yaml
```

#### Mandatory Configuration Changes

Edit `inventories/default/group_vars/disconnected.yaml` and update these **required** values:

**1. Mirror Host Configuration** (lines 49-52):
```yaml
mirroring:
  host:
    name: your-mirror-host-name  # ⚠️ REQUIRED: Hostname of mirror host with internet access
    ip: 192.168.1.100            # ⚠️ REQUIRED: IP address of mirror host
    user: root                   # User with sudo access
    pass: your-secure-password   # ⚠️ REQUIRED: Password for mirror host user
```

**2. Registry Certificate** (lines 11-21):
- If `ca_trusted: false` (default): Certificate will be **auto-generated** - no action needed
- If `ca_trusted: true`: Paste your existing certificate in the `ca_cert` field

**3. Registry Password** (line 52):
- Already references `{{ vault_registry_password }}` from `secrets.yaml`
- Ensure you've set this in Step 1

#### Optional Configuration Changes

These values have sensible defaults but can be customized:

**Registry Configuration:**
```yaml
bastion:
  port: 5000                    # Registry port (default: 5000)
  username: 'admin'             # Registry username (default: admin)
  email: 'registry@example.com' # Email for pull secret
```

**OCP Version and Operators:**
```yaml
oc_mirror:
  image_set:
    mirror:
      platform:
        channels:
          - name: stable-4.21
            minVersion: 4.21.14  # Customize OCP version
            maxVersion: 4.21.14
      operators:
        - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.21
          packages:
            - name: serverless-operator  # Add/remove operators as needed
```

#### Complete Configuration Example

Here's a complete example with all mandatory values filled:

```yaml
disconnected:
  enabled: true
  
  registry:
    ca_trusted: false  # Auto-generates self-signed certificate
    
    bastion:
      enabled: true
      port: 5000
      username: 'admin'
      password: "{{ vault_registry_password }}"
      email: 'registry@example.com'
      use_local_repo: true
  
  mirroring:
    host:
      name: mirror-host-01        # ⚠️ YOUR MIRROR HOST NAME
      ip: 192.168.100.50          # ⚠️ YOUR MIRROR HOST IP
      user: root
      pass: SecurePassword123!    # ⚠️ YOUR MIRROR HOST PASSWORD
    
    oc_mirror:
      image_set:
        apiVersion: mirror.openshift.io/v2alpha1
        mirror:
          platform:
            architectures:
              - multi
            channels:
              - name: stable-4.21
                full: false
                minVersion: 4.21.14
                maxVersion: 4.21.14
          operators:
            - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.21
              full: false
              packages:
                - name: serverless-operator
                  channels:
                    - name: stable
```

#### Configuration Validation Checklist

Before running the playbook, verify:

- ✅ `disconnected_enabled: true` set in `all.yaml` (Section 1 - Ansible Controller)
- ✅ `disconnected.yaml` created from template
- ✅ Mirror host `name`, `ip`, and `pass` updated with your values
- ✅ `vault_registry_password` set in `secrets.yaml`
- ✅ `secrets.yaml` encrypted with `ansible-vault encrypt`
- ✅ OCP version matches your target version
- ✅ Required operators listed in `packages` section

### Step 4: Verify all.yaml Configuration (Original Content Below)

The original configuration example:

```yaml
disconnected:
  enabled: true  # REQUIRED: Change from false to true (if not already done)
  
  registry:
    # Auto-configured when using bastion registry
    ca_trusted: false  # Auto-generates self-signed certificate
    
    bastion:
      enabled: true  # Creates registry on bastion
      port: 5000
      username: 'admin'
      password: "{{ vault_registry_password }}"  # From secrets.yaml
      email: 'registry@example.com'  # For pull secret
      
      # Package installation mode
      use_local_repo: true  # Set to false for fully disconnected (downloads RPMs)
      
      # Storage directories
      data_dir: '/opt/registry/data'
      auth_dir: '/opt/registry/auth'
      certs_dir: '/opt/registry/certs'
  
  mirroring:
    file_server:
      document_root: '/var/www/html'  # HTTP server document root
      clients_dir: 'clients'  # Subdirectory under document_root (accessible at http://<ip>:<port>/clients/)
      oc_mirror_tgz: 'oc-mirror.tar.gz'
      download_dir: '/tmp/oc-mirror-downloads'  # Temporary download directory
    
    bastion:
      working_dir: '/opt/oc-mirror'
      mirror_output_dir: '/opt/oc-mirror/mirror-output'
    
    # Download URLs (s390x architecture)
    oc_mirror_download:
      base_url: "https://mirror.openshift.com/pub/openshift-v4/s390x/clients/ocp/stable/"
      oc_mirror_tgz: 'oc-mirror.tar.gz'
    
    client_download:
      ocp_download_url: "https://mirror.openshift.com/pub/openshift-v4/multi/clients/ocp/stable-4.21/s390x/"
      ocp_client_tgz: 'openshift-client-linux.tar.gz'
    
    # oc-mirror configuration
    oc_mirror:
      oc_mirror_args:
        continue_on_error: false  # Continue mirroring even if some images fail
        source_skip_tls: false  # Skip TLS verification for source registries
        async_timeout: 7200  # Timeout in seconds (default: 7200 = 2 hours)
        async_poll: 30  # Check status every N seconds (default: 30)
      oc_mirror_args:
        continue_on_error: false
        source_skip_tls: false
      
      image_set:
        apiVersion: mirror.openshift.io/v2alpha1  # v2alpha1 for oc-mirror v2
        
        mirror:
          platform:
            architectures:
              - multi  # Includes s390x in multi-arch images
            channels:
              - name: stable-4.21
                full: false
                minVersion: 4.21.14
                maxVersion: 4.21.14
          
          operators:
            - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.13
              full: false
              packages:
                - name: serverless-operator
                  channels:
                    - name: stable
          
          additionalImages:
            - name: registry.redhat.io/ubi8/ubi:latest
          
          helm: {}
```

### Step 3: Verify all.yaml Configuration

Ensure these values are set in `inventories/default/group_vars/all.yaml`:

```yaml
env:
  file_server:
    ip: 192.168.1.10
    protocol: http
    cfgs_dir: /pub
  
  bastion:
    networking:
      ip: 192.168.1.20
      hostname: bastion
      base_domain: example.com
  
  redhat:
    pull_secret: '{"auths":{...}}'  # Your Red Hat pull secret
```

### Step 4: Update Pull Secret (After First Run)

After the playbook runs, it will create a backup file with updated pull secret:

```bash
# Review the updated pull secret
cat inventories/default/group_vars/pull_secret_with_registry.json

# Copy the content and update env.redhat.pull_secret in all.yaml
```

Or manually add the bastion registry entry:
```json
{
  "auths": {
    "cloud.openshift.com": {...},
    "quay.io": {...},
    "registry.redhat.io": {...},
    "192.168.1.20:5000": {
      "auth": "base64-encoded-username:password",
      "email": "registry@example.com"
    }
  }
}
```

## Running the Playbook

### Basic Usage

Run the complete playbook:

```bash
ansible-playbook -i inventories/default playbooks/disconnected_setup_oc_mirror.yaml
```

With Ansible Vault (interactive password prompt):
```bash
ansible-playbook -i inventories/default playbooks/disconnected_setup_oc_mirror.yaml --ask-vault-pass
```

With Ansible Vault (password file):
```bash
# Create a vault password file (protect it with appropriate permissions)
echo 'your-vault-password' > ~/.vault_pass
chmod 600 ~/.vault_pass

# Run playbook with vault password file
ansible-playbook -i inventories/default playbooks/disconnected_setup_oc_mirror.yaml --vault-password-file ~/.vault_pass
```

### Run Specific Stages

The playbook has multiple stages that can be run independently:

#### 1. Download Registry RPMs Only (for fully disconnected)
```bash
ansible-playbook -i inventories/default playbooks/disconnected_setup_oc_mirror.yaml --tags download_rpms
```

#### 2. Setup Registry Only
```bash
ansible-playbook -i inventories/default playbooks/disconnected_setup_oc_mirror.yaml --tags registry
```

#### 3. Download oc-mirror Only
```bash
ansible-playbook -i inventories/default playbooks/disconnected_setup_oc_mirror.yaml --tags download
```

#### 4. Setup oc-mirror Only
```bash
ansible-playbook -i inventories/default playbooks/disconnected_setup_oc_mirror.yaml --tags setup
```

#### 5. Mirror Images Only
```bash
ansible-playbook -i inventories/default playbooks/disconnected_setup_oc_mirror.yaml --tags mirror
```

### Skip Registry Setup (Use External Registry)

If you have an external registry:

```bash
ansible-playbook -i inventories/default playbooks/disconnected_setup_oc_mirror.yaml --skip-tags registry
```

Then configure `disconnected.registry.url` and `disconnected.registry.ip` in disconnected.yaml.

## Roles Overview

The playbook uses six roles in sequence:

### 1. disconnected_download_registry_rpms

**Purpose**: Downloads RPM packages for offline installation  
**Runs on**: File server (or bastion if same)  
**When**: Only if `use_local_repo: false`

Downloads:
- podman
- httpd-tools
- openssl
- container-selinux
- conmon, crun, fuse-overlayfs, slirp4netns

**Architecture**: Uses `--archlist=s390x,noarch` for correct architecture

### 2. disconnected_setup_registry_bastion

**Purpose**: Creates container registry on bastion  
**Runs on**: Bastion

Actions:
- Installs podman and dependencies
- Generates self-signed certificate (or uses provided)
- Creates htpasswd authentication
- Starts registry as systemd service
- Adds certificate to system trust

**Service**: `container-registry.service`  
**Port**: 5000 (configurable)  
**Storage**: `/opt/registry/data`

### 3. disconnected_update_pull_secret

**Purpose**: Updates pull secret with registry credentials  
**Runs on**: localhost (Ansible controller)

Actions:
- Parses existing pull secret
- Adds bastion registry credentials
- Updates in-memory for current run
- Creates backup file
- Displays instructions for permanent update

**Output**: `inventories/default/group_vars/pull_secret_with_registry.json`

### 4. disconnected_download_oc_mirror

**Purpose**: Downloads oc-mirror, client tools, and RHCOS rootfs
**Runs on**: File server (or bastion if same)

Downloads:
- oc-mirror plugin (s390x)
- openshift-client-linux.tar.gz (s390x)
- openshift-install-linux.tar.gz (s390x)
- rhcos-live-rootfs.s390x.img (RHCOS rootfs for node installation)

**Destinations**:
- Client tools: `{{ env.file_server.document_root }}/clients/`
- RHCOS rootfs: `{{ env.file_server.document_root }}/bin/`

**Note**: The RHCOS rootfs file is required for node installation and will be served via HTTP during the bootstrap process.

### 5. disconnected_setup_oc_mirror_bastion

**Purpose**: Installs oc-mirror on bastion  
**Runs on**: Bastion

Actions:
- Downloads binaries from file server
- Extracts and installs to `/usr/local/bin/`
- Configures pull secret
- Adds registry CA certificate
- Verifies installation

**Binaries**: oc-mirror, oc, kubectl

### 6. disconnected_mirror_ocp_bastion

**Purpose**: Performs OCP image mirroring  
**Runs on**: Bastion

Actions:
- Creates ImageSet configuration
- Runs oc-mirror (v1 or v2)
- Generates cluster manifests
- Copies results to output directory

**Duration**: 30 minutes to several hours depending on content

**Output Files**:
- ImageContentSourcePolicy or ImageDigestMirrorSet
- CatalogSource manifests
- Release signatures

## Playbook Execution Flow

```
1. Download Registry RPMs (if use_local_repo=false)
   ↓
2. Setup Container Registry on Bastion
   ↓
3. Update Pull Secret with Registry Credentials
   ↓
4. Download oc-mirror to File Server
   ↓
5. Setup oc-mirror on Bastion
   ↓
6. Mirror OCP Images
   ↓
7. Display Next Steps
```

## Post-Mirroring Steps

After successful mirroring:

### 1. Review Output Files

```bash
ssh bastion
ls -la /opt/oc-mirror/mirror-output/
```

### 2. For New Cluster Installation

Update `install-config.yaml`:

```yaml
imageContentSources:
  - mirrors:
      - 192.168.1.20:5000/openshift/release-images
    source: quay.io/openshift-release-dev/ocp-release
  - mirrors:
      - 192.168.1.20:5000/openshift/release
    source: quay.io/openshift-release-dev/ocp-v4.0-art-dev

additionalTrustBundle: |
  -----BEGIN CERTIFICATE-----
  <content from /opt/registry/certs/registry.crt>
  -----END CERTIFICATE-----
```

### 3. For Existing Cluster

Apply the generated manifests:

```bash
# Apply ImageContentSourcePolicy or ImageDigestMirrorSet
oc apply -f /opt/oc-mirror/mirror-output/imageContentSourcePolicy.yaml

# Apply CatalogSource for operators
oc apply -f /opt/oc-mirror/mirror-output/catalogSource.yaml

# Wait for nodes to restart and apply configuration
oc get nodes
oc get mcp
```

## Troubleshooting

### Self-Signed Certificate Challenges in Disconnected Environments

When using a self-signed certificate for your disconnected registry (not from a globally trusted Certificate Authority), several certificate trust issues can arise during OpenShift installation. This section explains the challenges and the solutions implemented in this playbook.

#### The Problem: Certificate Trust in Container Environments

**Why Self-Signed Certificates Are Challenging:**

1. **Multiple Trust Stores**: Different components use different certificate trust mechanisms:
   - System trust store: `/etc/pki/ca-trust/source/anchors/`
   - Container-specific: `/etc/containers/certs.d/<registry>/`
   - Application-specific: Some tools have their own trust stores

2. **Ephemeral Containers**: The OpenShift bootstrap process runs `oc` commands inside temporary containers that:
   - Don't inherit environment variables from the host
   - Don't have access to host certificate files
   - Use Go's HTTP client which strictly validates certificates
   - Cannot be easily configured with custom certificates

3. **Bootstrap Isolation**: The bootstrap node runs critical installation scripts (`bootkube.sh`) that:
   - Execute `oc adm release info` commands to query release images
   - Run inside podman containers with isolated filesystems
   - Fail with "x509: certificate signed by unknown authority" errors
   - Cannot proceed without trusting the registry certificate

#### The Solution: Multi-Layer Certificate Trust

This playbook implements a comprehensive solution that addresses certificate trust at multiple levels:

**1. System-Level Trust** (Lines 315-356 in [`roles/get_ocp/tasks/main.yaml`](roles/get_ocp/tasks/main.yaml:315-356))
```yaml
# Certificate added to system trust store
/etc/pki/ca-trust/source/anchors/registry-ca.crt

# Certificate added for container runtime
/etc/containers/certs.d/172.23.238.65:5000/ca.crt
```

**2. Insecure Registry Configuration** (Lines 361-390 in [`roles/get_ocp/tasks/main.yaml`](roles/get_ocp/tasks/main.yaml:361-390))
```yaml
# Allows podman to skip TLS verification
/etc/containers/registries.conf.d/999-insecure-registry.conf
```
This enables podman to pull images without certificate validation, which is acceptable in a controlled disconnected environment.

**3. Bootstrap Script Patching** (Lines 412-430 in [`roles/get_ocp/tasks/main.yaml`](roles/get_ocp/tasks/main.yaml:412-430))

The most critical fix: A systemd service (`patch-bootkube-insecure.service`) that runs early in the bootstrap process to modify the `bootkube.sh` script:

```bash
# Adds --insecure flag to all oc adm release info commands
sed -i -e "s|oc adm release info|oc adm release info --insecure|g" \
       -e "1a# insecure-added" /usr/local/bin/bootkube.sh
```

**Why This Is Necessary:**
- The `bootkube.sh` script runs `oc` commands inside ephemeral containers
- These containers cannot access the host's certificate trust store
- The `--insecure` flag tells `oc` to skip TLS verification
- This is the only way to make bootstrap work with self-signed certificates

#### Final Bootstrap Configuration

The bootstrap ignition now includes:

✅ **Certificate in system trust store**: `/etc/pki/ca-trust/source/anchors/registry-ca.crt`
✅ **Certificate for container runtime**: `/etc/containers/certs.d/172.23.238.65:5000/ca.crt`
✅ **Insecure registry configuration**: `/etc/containers/registries.conf.d/999-insecure-registry.conf`
✅ **Bootstrap script patcher**: `patch-bootkube-insecure.service` systemd unit

**Security Considerations:**

Using `--insecure` and `insecure = true` is acceptable in disconnected environments because:
- The registry is on a trusted internal network
- No external/untrusted registries are involved
- The alternative (bootstrap failure) is worse
- Production clusters can use proper certificates from internal CAs

**For Production Environments:**

Consider using certificates from an internal Certificate Authority (CA) that:
- Is trusted by your organization
- Can be pre-installed in RHCOS images
- Eliminates the need for insecure flags
- Provides proper certificate chain validation

Set `disconnected.registry.ca_trusted: true` and provide your CA certificate in `disconnected.registry.ca_cert` to use this approach.

### Registry Issues

#### Registry service fails to start

**Check logs**:
```bash
journalctl -u container-registry -f
```

**Common causes**:
- Port 5000 already in use: `ss -tlnp | grep 5000`
- Podman not installed: `podman --version`
- Permissions on directories

**Solution**:
```bash
# Check service status
systemctl status container-registry

# Restart service
systemctl restart container-registry

# Check podman directly
podman ps -a
```

#### Certificate errors

**Symptoms**: "x509: certificate signed by unknown authority"

**Solution**:
```bash
# Verify certificate in trust anchors
ls /etc/pki/ca-trust/source/anchors/

# Update trust
update-ca-trust

# Check certificate
openssl x509 -in /opt/registry/certs/registry.crt -text -noout
```

### Mirroring Issues

#### Authentication failures

**Symptoms**: "unauthorized" or "authentication required"

**Solution**:
- Verify pull secret includes all registries
- Check registry credentials are correct
- Ensure pull secret is valid JSON:
  ```bash
  echo '{"auths":{...}}' | python -m json.tool
  ```

#### Out of disk space

**Symptoms**: "no space left on device"

**Solution**:
```bash
# Check disk usage
df -h /opt/oc-mirror
df -h /opt/registry/data

# Clean up if needed
podman system prune -a

# Consider using different mount point with more space
```

#### Network timeouts

**Symptoms**: Connection timeouts during mirroring

**Solution**:
- Enable `continue_on_error: true` in disconnected.yaml
- Check network connectivity to Red Hat registries
- Consider mirroring in smaller batches

### Download Issues

#### RPM download fails

**Symptoms**: yumdownloader errors

**Solution**:
```bash
# Verify yum-utils is installed
yum install yum-utils

# Check repository configuration
yum repolist

# Test download manually
yumdownloader --archlist=s390x,noarch podman
```

#### oc-mirror download fails

**Symptoms**: HTTP 404 or connection errors

**Solution**:
- Verify URL is correct for your architecture
- Check internet connectivity
- Try alternative mirror URLs
- Verify OCP version exists at specified URL

## Advanced Topics

### Using External Registry

If you have an existing registry:

1. Set `disconnected.registry.bastion.enabled: false`
2. Configure registry URL and IP:
   ```yaml
   disconnected:
     registry:
       url: 'registry.example.com:5000'
       ip: '192.168.1.50'
   ```
3. Skip registry setup:
   ```bash
   ansible-playbook ... --skip-tags registry
   ```

### Mirroring Multiple OCP Versions

Update the image_set configuration:

```yaml
mirror:
  platform:
    channels:
      - name: stable-4.21
        minVersion: 4.21.14
        maxVersion: 4.21.20
      - name: stable-4.22
        minVersion: 4.22.0
        maxVersion: 4.22.5
```

### Mirroring Specific Operators

```yaml
operators:
  - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.13
    packages:
      - name: serverless-operator
        channels:
          - name: stable
            minVersion: '1.30.0'
            maxVersion: '1.32.0'
      - name: elasticsearch-operator
        channels:
          - name: stable
```

### Using oc-mirror v1 vs v2

**oc-mirror v1** (apiVersion: mirror.openshift.io/v1alpha2):
- Requires storageConfig
- Uses oc-mirror-workspace directory
- Generates mapping.txt

**oc-mirror v2** (apiVersion: mirror.openshift.io/v2alpha1):
- No storageConfig needed
- Uses working-dir structure
- Generates cluster-resources directory

Configure in disconnected.yaml:
```yaml
oc_mirror:
  image_set:
    apiVersion: mirror.openshift.io/v2alpha1  # or v1alpha2
```

### Fully Disconnected Installation (No Repository Access)

For environments without any repository access:

1. Set `use_local_repo: false` in disconnected.yaml
2. Run on a host with internet access:
   ```bash
   ansible-playbook ... --tags download_rpms
   ```
3. Transfer downloaded RPMs to file server
4. Run full playbook on disconnected bastion

### Performance Tuning

#### Disk Space Requirements
- **Minimal** (single OCP version): 50-100 GB
- **Standard** (OCP + operators): 200-300 GB
- **Full** (complete catalog): 500GB-1TB

#### Network Bandwidth
- Recommended: 100 Mbps or higher
- Consider running during off-peak hours
- Use `continue_on_error: true` for unreliable connections

#### Time Estimates
- Single OCP version: 30-60 minutes
- OCP + 5-10 operators: 1-3 hours
- Full operator catalog: 4-8 hours

### Security Best Practices

1. **Use Ansible Vault** for sensitive data:
   ```bash
   ansible-vault encrypt inventories/default/group_vars/secrets.yaml
   ```

2. **Change default passwords**:
   - Registry password in secrets.yaml
   - Use strong, unique passwords

3. **Certificate management**:
   - Use proper certificates in production
   - Don't use `source_skip_tls` in production

4. **Limit access**:
   - Restrict bastion access to authorized users
   - Use firewall rules for registry port

5. **Regular backups**:
   - Backup registry data directory
   - Backup mirrored content
   - Document configuration

## Storage Management

### Registry Storage

Monitor disk usage:
```bash
# Check registry data directory
du -sh /opt/registry/data

# Check for old images
podman images

# Clean up if needed
podman system prune -a
```

### Mirror Output Storage

```bash
# Check mirror output
du -sh /opt/oc-mirror/mirror-output

# Archive old mirroring results
tar -czf mirror-backup-$(date +%Y%m%d).tar.gz /opt/oc-mirror/mirror-output
```

## References

- [Red Hat OpenShift Disconnected Installation](https://docs.redhat.com/en/documentation/openshift_container_platform/4.14/html/disconnected_installation_mirroring/)
- [oc-mirror Plugin Documentation](https://docs.redhat.com/en/documentation/openshift_container_platform/4.14/html/disconnected_installation_mirroring/installing-mirroring-disconnected#installation-oc-mirror-installing-plugin_installing-mirroring-disconnected)
- [ImageSet Configuration Reference](https://docs.redhat.com/en/documentation/openshift_container_platform/4.14/html/disconnected_installation_mirroring/installing-mirroring-disconnected#oc-mirror-imageset-config-params_installing-mirroring-disconnected)
- [Podman Documentation](https://docs.podman.io/)
- [Container Registry Documentation](https://docs.docker.com/registry/)

## Support

For issues specific to this playbook:
- Check the troubleshooting section above
- Review Ansible logs for detailed error messages
- Verify all prerequisites are met

For oc-mirror or OpenShift issues:
- Consult Red Hat support
- Review Red Hat documentation
- Check OpenShift community forums

## Summary

This playbook provides a complete solution for disconnected OpenShift installations:

✅ Automated registry setup with self-signed certificates  
✅ Automatic pull secret management  
✅ s390x architecture support throughout  
✅ Flexible package installation (repo or offline RPMs)  
✅ Support for both oc-mirror v1 and v2  
✅ Comprehensive error handling and logging  
✅ Secure password management via Ansible Vault  

Follow this guide to successfully mirror OCP images and prepare for disconnected cluster installation.