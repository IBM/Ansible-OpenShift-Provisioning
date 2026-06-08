# Role: disconnected_setup_registry_bastion

## Description

This role sets up a container registry on the bastion host for disconnected OpenShift installations. It installs podman, creates a self-signed certificate (or uses a provided one), configures authentication, and runs a container registry as a systemd service.

## Requirements

- RHEL 8/9 or compatible Linux distribution
- Root/sudo access
- Sufficient disk space for container images (100GB+ recommended)
- Podman, httpd-tools, and openssl packages (either from repo or pre-downloaded RPMs)

## Role Variables

All variables are defined in `inventories/default/group_vars/disconnected.yaml`:

### Required Variables

```yaml
disconnected:
  enabled: true
  registry:
    ca_trusted: false  # Set to true if using provided certificate for the bastion host
    ca_cert: |
      -----BEGIN CERTIFICATE-----
      ...
      -----END CERTIFICATE-----
    bastion:
      enabled: true  # Enable registry on bastion
      port: 5000  # Registry port
      username: 'admin'  # Registry username
      password: 'redhat123'  # Registry password (CHANGE THIS!)
      data_dir: '/opt/registry/data'  # Registry data storage
      auth_dir: '/opt/registry/auth'  # Registry authentication files
      certs_dir: '/opt/registry/certs'  # Registry certificates
      # Package installation options
      use_local_repo: true  # Set to false for fully disconnected (use downloaded RPMs)
      rpm_dir: '/tmp/registry-rpms'  # Directory for RPMs (if use_local_repo=false)
      rpm_path: 'rpms/registry'  # Path on file server (if use_local_repo=false)
      required_rpms:  # RPM files on file server (if use_local_repo=false)
        - 'podman-*.rpm'
        - 'httpd-tools-*.rpm'
        - 'openssl-*.rpm'

env:
  bastion:
    networking:
      hostname: 'bastion'
      base_domain: 'example.com'
      ip: '192.168.1.100'
```

## Dependencies

- `community.crypto` collection (for certificate generation)
- `community.general` collection (for htpasswd module)

Install with:
```bash
ansible-galaxy collection install community.crypto community.general
```

## Example Playbook

```yaml
- name: Setup container registry on bastion
  hosts: bastion
  gather_facts: true
  vars_files:
    - "{{ inventory_dir }}/group_vars/all.yaml"
    - "{{ inventory_dir }}/group_vars/disconnected.yaml"
  tasks:
    - name: Setup container registry
      ansible.builtin.include_role:
        name: disconnected_setup_registry_bastion
      when:
        - disconnected.enabled
        - disconnected.registry.bastion.enabled
```

## Package Installation Modes

### Mode 1: Using Local Repository (use_local_repo: true)
- Installs packages from configured yum/dnf repositories
- Requires bastion to have access to RHEL repositories or local mirror
- Simplest method if repositories are available

### Mode 2: Using Downloaded RPMs (use_local_repo: false)
- Downloads RPMs from file server
- For fully disconnected environments
- Requires RPMs to be pre-downloaded to file server using `disconnected_download_registry_rpms` role

## Tasks Overview

1. Checks package installation mode
2. Installs required packages (podman, httpd-tools, openssl) from repo OR downloaded RPMs
2. Creates registry directories for data, auth, and certificates
3. Generates self-signed certificate (if ca_trusted=false) or uses provided certificate
4. Adds certificate to system trust anchors
5. Creates htpasswd file for registry authentication
6. Creates systemd service for container registry
7. Starts and enables the registry service
8. Verifies registry is accessible

## Files Created

### Directories
- `{{ disconnected.registry.bastion.data_dir }}` - Registry image storage
- `{{ disconnected.registry.bastion.auth_dir }}` - Authentication files
- `{{ disconnected.registry.bastion.certs_dir }}` - TLS certificates

### Files
- `{{ disconnected.registry.bastion.certs_dir }}/registry.crt` - Registry certificate
- `{{ disconnected.registry.bastion.certs_dir }}/registry.key` - Registry private key
- `{{ disconnected.registry.bastion.auth_dir }}/htpasswd` - Authentication credentials
- `/etc/systemd/system/container-registry.service` - Systemd service file
- `/etc/pki/ca-trust/source/anchors/registry.crt` - System-trusted certificate

## Registry Service

The registry runs as a systemd service named `container-registry`:

```bash
# Check status
systemctl status container-registry

# View logs
journalctl -u container-registry -f

# Restart registry
systemctl restart container-registry

# Stop registry
systemctl stop container-registry
```

## Registry Configuration

The registry is configured with:
- **TLS**: Enabled with self-signed or provided certificate
- **Authentication**: Basic auth using htpasswd
- **Storage**: Local filesystem storage
- **Delete**: Image deletion enabled
- **Port**: Configurable (default: 5000)

## Testing the Registry

After installation, test the registry:

```bash
# Login to registry
podman login {{ env.bastion.networking.ip }}:{{ disconnected.registry.bastion.port }} \
  -u {{ disconnected.registry.bastion.username }} \
  -p {{ disconnected.registry.bastion.password }}

# Pull a test image
podman pull docker.io/library/hello-world:latest

# Tag for local registry
podman tag docker.io/library/hello-world:latest \
  {{ env.bastion.networking.ip }}:{{ disconnected.registry.bastion.port }}/hello-world:latest

# Push to local registry
podman push {{ env.bastion.networking.ip }}:{{ disconnected.registry.bastion.port }}/hello-world:latest

# Verify
curl -u {{ disconnected.registry.bastion.username }}:{{ disconnected.registry.bastion.password }} \
  https://{{ env.bastion.networking.ip }}:{{ disconnected.registry.bastion.port }}/v2/_catalog
```

## Pull Secret Configuration

After the registry is created, you need to add its credentials to your pull secret. The role displays the required authentication string in base64 format.

Add to `env.redhat.pull_secret` in all.yaml:

```json
{
  "auths": {
    "cloud.openshift.com": {...},
    "quay.io": {...},
    "registry.redhat.io": {...},
    "192.168.1.100:5000": {
      "auth": "base64-encoded-username:password",
      "email": "registry@example.com"
    }
  }
}
```

To generate the auth string:
```bash
echo -n "admin:redhat123" | base64
```

## Security Considerations

1. **Change Default Password**: Always change the default registry password
2. **Certificate Management**: Use proper certificates in production
3. **Firewall Rules**: Ensure port 5000 (or configured port) is accessible
4. **Disk Space**: Monitor disk usage in data_dir
5. **Backup**: Regularly backup registry data directory

## Storage Requirements

Plan for adequate storage based on your needs:
- **Minimal** (single OCP version): 50-100 GB
- **Standard** (OCP + operators): 200-300 GB
- **Full** (complete catalog): 500GB-1TB

## Troubleshooting

### Issue: Registry service fails to start
**Solution**: Check logs with `journalctl -u container-registry -f`
- Verify port is not in use: `ss -tlnp | grep 5000`
- Check podman is installed: `podman --version`
- Verify directories exist and have correct permissions

### Issue: Certificate errors when accessing registry
**Solution**: 
- Verify certificate is in trust anchors: `ls /etc/pki/ca-trust/source/anchors/`
- Update trust: `update-ca-trust`
- Check certificate validity: `openssl x509 -in /opt/registry/certs/registry.crt -text -noout`

### Issue: Authentication failures
**Solution**:
- Verify htpasswd file exists: `cat /opt/registry/auth/htpasswd`
- Test credentials: `htpasswd -v /opt/registry/auth/htpasswd admin`
- Check service environment variables in systemd file

### Issue: Out of disk space
**Solution**:
- Check disk usage: `df -h /opt/registry/data`
- Clean up old images if needed
- Consider using different mount point with more space

## Tags

- `setup_registry_bastion`
- `registry`

## References

- [Podman Documentation](https://docs.podman.io/)
- [Docker Registry Documentation](https://docs.docker.com/registry/)
- [Red Hat Container Registry](https://access.redhat.com/documentation/en-us/red_hat_quay/)

## Author

Generated for Ansible-OpenShift-Provisioning project