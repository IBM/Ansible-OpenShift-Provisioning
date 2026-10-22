# Ansible-Automated OpenShift Provisioning on IBM zSystems / LinuxONE
The documentation for this project can be found [here](https://ibm.github.io/Ansible-OpenShift-Provisioning/).

**Supported Hypervisors:** KVM, LPAR, z/VM  
**Installation Methods:** User-Provisioned Infrastructure (UPI), Agent-Based Installer (ABI), Hosted Control Plane (HCP)

Release v2.4.0:
This README contains the information for the current release only.
The whole history of the releases can be found [here](https://github.com/IBM/Ansible-OpenShift-Provisioning/releases).
This release was tested with OpenShift v4.21 and below.

## What's new:
* Enable CEX based LUKS encryption
* Updated hcp.yaml with CatalogSource image parameter for MCE installation
* Added workflows to integrate github actions for PR validations
* New [`download_kubeconfig`](roles/download_kubeconfig/README.md) role for downloading kubeconfig and kubepassw files from bastion host
* New [`setup_bastion_services`](roles/setup_bastion_services/) role that consolidates DNS and HAProxy configuration into a single, idempotent role — replaces the four separate roles `dns`, `dns_update`, `haproxy`, and `haproxy_update`

### Bug Fixes
* Add EC build support logic in OCP installer download task
* Added RoCE interface to the parm file of LPAR while booting
* DNS entries fix to enabling correct forwarding
* Issue 433 - UPI installion not working
* Jenkins pipeline failure at the mce creation steps
* This fix solves the UPI installation for HA
* resolved bug for ocmirrorv2 from 4.19
* Update to get the by-path value of fcp disk and the pod count of hcp to greater than 20
* Updated InfraEnv template and updated timeouts for image downloads
* Updated mirror information for HCP templates
* Updated the nameserver of kvm, zvm & LPAR agents - hcp
* Updated the nameserver of lpar hipersockets agents

### Variables renamed:

#### Only new variables introduced but no renamed.

## `setup_bastion_services` Role

The new [`setup_bastion_services`](roles/setup_bastion_services/) role replaces and consolidates the four previous roles `dns`, `dns_update`, `haproxy`, and `haproxy_update` into a single, idempotent role.

### Motivation

Previously, running playbook `5_setup_bastion.yaml` against a bastion that already had named and HAProxy configured (for example on a re-run or when `env.bastion.create: false`) would blindly re-template the configuration files, potentially clobbering entries from a previous run or producing duplicate entries. The new role handles both the fresh-install and the existing-bastion case correctly.

> **HAProxy limitation — single cluster per bastion:** Because all listener ports (6443, 22623, 443, 80) bind to `*`, only one OCP cluster can be served per bastion at a time. `haproxy.cfg` is therefore always fully re-templated on every run (after a dated backup). The cluster's `listen` blocks are wrapped in `# BEGIN <cluster>` / `# END <cluster>` markers so the file structure is self-documenting and the template output is idempotent. Multi-cluster port assignment is planned for a future release.

### How it works

The role is invoked with a `bastion_services_mode` variable that selects which sub-task to execute:

| `bastion_services_mode` | When to use | What it does |
|---|---|---|
| `dns` | Full DNS setup (fresh or existing bastion) | Auto-detects whether `/var/named/<cluster>.db` already exists. **Fresh bastion**: templates out `named.conf`, the forward zone file (`.db`) and reverse zone file (`.rev`), then adds all node entries. **Existing bastion**: leaves the existing `named.conf` intact and only appends the two cluster zones (forward and reverse) using `blockinfile` if they are not already present — all pre-existing zones and options are preserved. Stale cluster node entries are removed from the live `.db` and `.rev` files before being re-added. |
| `haproxy` | Full HAProxy setup | Always backs up any existing `/etc/haproxy/haproxy.cfg` to a dated file, then re-templates the full config (global, defaults, stats frontend, and the cluster's `listen` blocks wrapped in `# BEGIN <cluster>` / `# END <cluster>` markers). Because all ports bind to `*`, only one OCP cluster can be served per bastion — see the limitation note above. |
| `node_dns` | Day-2 single-node DNS add/delete | Adds or removes the forward and reverse DNS entries for one node. Controlled by `param_dns_cmd` (`add`/`delete`), `param_dns_hostname`, and `param_dns_ip`. Restarts named after the change. |
| `node_haproxy` | Day-2 single-node HAProxy add/delete | Adds or removes the port-80 and port-443 backend entries for one node. Controlled by `param_haproxy_cmd` (`add`/`delete`) and `param_haproxy_hostname`. Restarts haproxy after the change. |
| `all` (default) | Run both `dns` and `haproxy` together | Convenience shorthand that runs the full DNS and HAProxy configuration in sequence. |

The `initial_resolv` task file is available for use in `pre_tasks` via `tasks_from: initial_resolv.yaml`, exactly as the old `dns` role provided `initial-resolv.yaml`.

### Configuration file backups

Before making any changes to an existing bastion, the role creates a dated backup of each configuration file it modifies. The backup is placed alongside the original file and named with a `YYYY-MM-DD` suffix:

| Original file | Backup created |
|---|---|
| `/etc/named.conf` | `/etc/named.conf.<YYYY-MM-DD>` |
| `/etc/haproxy/haproxy.cfg` | `/etc/haproxy/haproxy.cfg.<YYYY-MM-DD>` |

**Important notes:**
- Backups are only created when the file already exists on the bastion (i.e. on an existing bastion, not on a fresh one).
- A new backup is written on every playbook run. If the role is run more than once on the same day, the backup from the first run of that day is overwritten.
- **Backup files are never removed automatically.** They must be deleted manually when they are no longer needed. To clean them up on the bastion, run:

```bash
# Remove named.conf backups
rm -f /etc/named.conf.[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]

# Remove haproxy.cfg backups
rm -f /etc/haproxy/haproxy.cfg.[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]
```

### Example usage in a playbook

```yaml
# Full DNS + HAProxy configuration (idempotent — safe on fresh or existing bastion)
- role: setup_bastion_services
  bastion_services_mode: dns
  when: env.bastion.options.dns

- role: setup_bastion_services
  bastion_services_mode: haproxy
  when: env.bastion.options.loadbalancer.on_bastion

# Day-2: add a compute node to DNS and HAProxy
- role: setup_bastion_services
  bastion_services_mode: node_dns
  param_dns_cmd: add
  param_dns_hostname: "{{ day2_compute_node.vm_hostname }}"
  param_dns_ip: "{{ day2_compute_node.vm_ip }}"
  when: env.bastion.options.dns

- role: setup_bastion_services
  bastion_services_mode: node_haproxy
  param_haproxy_cmd: add
  param_haproxy_hostname: "{{ day2_compute_node.vm_hostname }}"
  when: env.bastion.options.loadbalancer.on_bastion

# Day-2: remove a compute node from DNS and HAProxy
- role: setup_bastion_services
  bastion_services_mode: node_haproxy
  param_haproxy_cmd: delete
  param_haproxy_hostname: "{{ day2_compute_node.vm_hostname }}"
  when: env.bastion.options.loadbalancer.on_bastion

- role: setup_bastion_services
  bastion_services_mode: node_dns
  param_dns_cmd: delete
  param_dns_hostname: "{{ day2_compute_node.vm_hostname }}"
  param_dns_ip: "{{ day2_compute_node.vm_ip }}"
  when: env.bastion.options.dns
```

### Deprecated section:

#### The `dns`, `dns_update`, `haproxy`, and `haproxy_update` roles are deprecated and will be removed in an upcoming release. They have been replaced by the consolidated [`setup_bastion_services`](roles/setup_bastion_services/) role. No playbooks in this project call them any longer. If you have custom playbooks that reference these roles directly, migrate them to `setup_bastion_services` using the `bastion_services_mode` variable as described above.

#### Support for openvpn is being deprecated due to issues with RHEL9. It will be removed in one of the upcoming releases. For the time being this feature is disabled by setting setup_openvpn variable to False.
#### Support for RHEL8. RHEL8 support will be removed in one of the upcoming releases.
