# Ansible Role: download_kubeconfig

This role downloads the kubeconfig and kubepassw files from the bastion host.

## Description

The `download_kubeconfig` role enables downloading OpenShift authentication files from the bastion host to the local controller. The files are downloaded from the `~/ocpinst/auth/` directory on the bastion host and stored in a configurable destination directory.

## Requirements

- Ansible 2.9 or higher
- SSH access to the bastion host
- The `kubeconfig` and `kubepassw` files must exist on the bastion host under `~/ocpinst/auth/`

## Role Variables

### Default Variables (defaults/main.yaml)

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `kubeconfig_dest_dir` | `/tmp` | Destination directory on the local controller where downloaded files will be stored |
| `kubeconfig_source_dir` | `~/ocpinst/auth` | Source directory on the bastion host from which files will be downloaded |
| `kubeconfig_files` | `['kubeconfig', 'kubepassw']` | List of files to download |

### Overriding Variables

Variables can be overridden in several ways:

1. **In the playbook file:**
```yaml
- hosts: bastion
  roles:
    - role: download_kubeconfig
      vars:
        kubeconfig_dest_dir: /custom/path
```

2. **Via command line:**
```bash
ansible-playbook download_kubeconfig.yaml -e "kubeconfig_dest_dir=/custom/path" --ask-vault-password
```

3. **In group_vars or host_vars:**
```yaml
# group_vars/all.yaml
kubeconfig_dest_dir: /custom/path
```

## Dependencies

No external role dependencies.

## Example Playbook

### Simple usage with default values

```yaml
---
- name: Download kubeconfig files from bastion
  hosts: bastion
  gather_facts: false
  roles:
    - download_kubeconfig
```

### Usage with custom destination directory

```yaml
---
- name: Download kubeconfig files to custom location
  hosts: bastion
  gather_facts: false
  vars:
    kubeconfig_dest_dir: /home/user/openshift-configs
  roles:
    - download_kubeconfig
```

### Usage with additional variables

```yaml
---
- name: Download kubeconfig files with custom settings
  hosts: bastion
  gather_facts: false
  vars_files:
    - "{{ inventory_dir }}/group_vars/all.yaml"
    - "{{ inventory_dir }}/group_vars/secrets.yaml"
  vars:
    kubeconfig_dest_dir: /opt/openshift/configs
  roles:
    - download_kubeconfig
```

## Output Structure

The downloaded files are stored in the following structure:

```
<kubeconfig_dest_dir>/
└── kubeconfig/
    ├── kubeconfig
    └── kubepassw
```

**Note:** Files are stored directly in the `kubeconfig/` subdirectory, **not** in `auth/kubeconfig/`. This meets the requirement that the destination file structure should be `kubeconfig` instead of `auth`.

### Example with default values

When using default values (`kubeconfig_dest_dir: /tmp`):

```
/tmp/
└── kubeconfig/
    ├── kubeconfig
    └── kubepassw
```

## Tags

The role supports the following tags:

- `download_kubeconfig`: Executes only the download tasks

Usage:
```bash
ansible-playbook download_kubeconfig.yaml --tags download_kubeconfig --ask-vault-password
```

## License

See main project license

## Author

Ansible OpenShift Provisioning Team