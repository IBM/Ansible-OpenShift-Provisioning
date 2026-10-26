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
* **Bastion node support for z/VM**: bastions can now be created on a z/VM hypervisor in addition to KVM. Each bastion is defined in its own `host_vars` file (`bastion.type: kvm` or `bastion.type: zvm`). The `bastion_nodes` list in `all.yaml` replaces the old `env.bastion` block. Multiple bastions on different hypervisors can coexist. A new `power_bastion.yaml` playbook starts, stops, or restarts bastion VMs. See [Bastion Node Configuration](docs/bastion-on-zvm.md) for details.
* **Inventory schema v2**: `all.yaml` now requires `schema_version: 2`. If you have an existing `all.yaml` from a previous release, run the migration playbook before using this version — see [`migration/README.md`](migration/README.md).

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

#### `env.bastion` removed — replaced by per-bastion `host_vars` files and the `bastion_nodes` list. Use the migration playbook in [`migration/`](migration/) to convert existing `all.yaml` files automatically.

### Deprecated section:

#### Support for openvpn is being deprecated due to issues with RHEL9. It will be removed in one of the upcoming releases. For the time being this feature is disabled by setting setup_openvpn variable to False.
#### Support for RHEL8. RHEL8 support will be removed in one of the upcoming releases.
