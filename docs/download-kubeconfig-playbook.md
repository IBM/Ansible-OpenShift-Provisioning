# Download Kubeconfig Playbook

## Overview

The `download_kubeconfig.yaml` playbook downloads the OpenShift authentication files (`kubeconfig` and `kubepassw`) from the bastion host to the local Ansible controller.

## Playbook File

**Path:** `playbooks/download_kubeconfig.yaml`

## Purpose

This playbook is used to download authentication files from the bastion host after a successful OpenShift installation. These files are needed to:

- Interact with the OpenShift cluster via `oc` or `kubectl`
- Access the OpenShift web console
- Perform administrative tasks

## Prerequisites

1. **Bastion host must be configured:**
   - SSH access to the bastion host must be working
   - The bastion host must be defined in the Ansible inventory under the `bastion` group
   - The 0_setup.yaml playbook must have been executed successfully

2. **OpenShift installation must be complete:**
   - The files `~/ocpinst/auth/kubeconfig` and `~/ocpinst/auth/kubepassw` must exist on the bastion host

3. **Ansible configuration:**
   - Inventory file must be correctly configured
   - `group_vars/all.yaml` must be present
   - `group_vars/secrets.yaml` must be present

## Usage

### Basic Usage

```bash
ansible-playbook playbooks/download_kubeconfig.yaml --ask-vault-pass
```

### With Custom Destination Directory

```bash
ansible-playbook playbooks/download_kubeconfig.yaml \
  --ask-vault-pass \
  -e "kubeconfig_dest_dir=/home/user/openshift-configs"
```

### With Specific Inventory

```bash
ansible-playbook playbooks/download_kubeconfig.yaml \
  -i inventories/production/hosts \
  --ask-vault-pass \
  -e "kubeconfig_dest_dir=/opt/openshift/production"
```

### Execute Only Download Tasks (with Tags)

```bash
ansible-playbook playbooks/download_kubeconfig.yaml \
  --ask-vault-pass \
  --tags download_kubeconfig
```

## Configurable Variables

### Main Variables

| Variable | Default Value | Description | Overridable |
|----------|---------------|-------------|-------------|
| `kubeconfig_dest_dir` | `/tmp` | Destination directory on the local controller | Yes |
| `kubeconfig_source_dir` | `~/ocpinst/auth` | Source directory on the bastion host | Yes |
| `kubeconfig_files` | `['kubeconfig', 'kubeadmin-password']` | List of files to download | Yes |

### Overriding Variables

#### Method 1: Command Line (recommended for one-time changes)

```bash
ansible-playbook playbooks/download_kubeconfig.yaml \
  --ask-vault-pass \
  -e "kubeconfig_dest_dir=/custom/path"
```

#### Method 2: In group_vars/all.yaml (recommended for permanent changes)

```yaml
# inventories/default/group_vars/all.yaml
kubeconfig_dest_dir: /opt/openshift/configs
```

#### Method 3: In a separate variables file

```bash
# Create a file vars/kubeconfig_vars.yaml
cat > vars/kubeconfig_vars.yaml <<EOF
kubeconfig_dest_dir: /opt/openshift/configs
kubeconfig_source_dir: ~/ocpinst/auth
EOF

# Use the file when executing
ansible-playbook playbooks/download_kubeconfig.yaml \
  --ask-vault-pass \
  -e @vars/kubeconfig_vars.yaml
```

## Output

### File Structure

The downloaded files are stored in the following structure:

```
<kubeconfig_dest_dir>/
└── kubeconfig/
    ├── kubeconfig
    └── kubeadmin-password
```

**Important:** Files are stored in the `kubeconfig/` subdirectory, **not** in `auth/kubeconfig/`.

### Example with Default Values

```
/tmp/
└── kubeconfig/
    ├── kubeconfig
    └── kubeadmin-password
```

### Example with Custom Path

```bash
ansible-playbook playbooks/download_kubeconfig.yaml \
  --ask-vault-pass \
  -e "kubeconfig_dest_dir=/home/user/ocp-cluster1"
```

Result:
```
/home/user/ocp-cluster1/
└── kubeconfig/
    ├── kubeconfig
    └── kubeadmin-password
```

## Using the Downloaded Files

### Using Kubeconfig

```bash
# Export the kubeconfig file
export KUBECONFIG=/tmp/kubeconfig/kubeconfig

# Test the connection
oc whoami
oc get nodes

# Or use it directly
oc --kubeconfig=/tmp/kubeconfig/kubeconfig get nodes
```

### Display Kubeadmin Password

```bash
cat /tmp/kubeconfig/kubeadmin-password
```

## Integration in Workflows

### After OpenShift Installation

```bash
# 1. Install OpenShift
ansible-playbook playbooks/<0_xxx to 7_xxx>.yaml --ask-vault-password
or
ansible-playbook playbooks/reinstall_cluster.yaml --ask-vault-password


# 2. Download kubeconfig
ansible-playbook playbooks/download_kubeconfig.yaml --ask-vault-password

# 3. Use cluster
export KUBECONFIG=/tmp/kubeconfig/kubeconfig
oc get nodes
```

### In a Master Playbook if bastion already exists and 0_setup.yaml was executed successfully

```yaml
---
- name: Complete OpenShift Setup
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Install OpenShift
      ansible.builtin.import_playbook: reinstall_cluster.yaml --ask-vault-password

    - name: Download kubeconfig
      ansible.builtin.import_playbook: download_kubeconfig.yaml --ask-vault-password

```

## Troubleshooting

### Problem: Files Not Found

**Error:**
```
fatal: [bastion]: FAILED! => {"msg": "file not found: ~/ocpinst/auth/kubeconfig"}
```

**Solution:**
- Verify that the OpenShift installation is complete
- Ensure the files exist on the bastion host:
  ```bash
  ssh bastion "ls -la ~/ocpinst/auth/"
  ```

### Problem: SSH Connection Failed

**Error:**
```
fatal: [bastion]: UNREACHABLE! => {"msg": "Failed to connect to the host via ssh"}
```

**Solution:**
- Check SSH configuration
- Ensure the SSH key is correct
- Test the connection manually:
  ```bash
  ssh bastion "echo 'Connection successful'"
  ```

## Best Practices

1. **Secure Storage:**
   - Store kubeconfig files in a secure location
   - Set restrictive file permissions:
     ```bash
     chmod 600 /tmp/kubeconfig/kubeconfig
     chmod 600 /tmp/kubeconfig/kubepassw
     ```

2. **Backup:**
   - Create backups of authentication files
   - Store them in multiple secure locations

3. **Versioning:**
   - Use different directories for different clusters:
     ```bash
     ansible-playbook playbooks/download_kubeconfig.yaml \
       -e "kubeconfig_dest_dir=/opt/openshift/cluster-prod"
     ```

4. **Automation:**
   - Integrate the playbook into CI/CD pipelines

## See Also

- [Role Documentation](../roles/download_kubeconfig/README.md)
- [OpenShift Documentation](https://docs.openshift.com/)
- [Ansible Documentation](https://docs.ansible.com/)

## Support

For problems or questions:
1. Check the logs
2. Consult the documentation
3. Create an issue in the project repository