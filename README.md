# Ansible-Automated OpenShift Provisioning on IBM zSystems / LinuxONE
The documentation for this project can be found [here](https://ibm.github.io/Ansible-OpenShift-Provisioning/).

**Supported Hypervisors:** KVM, LPAR, z/VM  
**Installation Methods:** User-Provisioned Infrastructure (UPI), Agent-Based Installer (ABI), Hosted Control Plane (HCP)

Release v2.5.0:
This README contains the information for the current release only.
The whole history of the releases can be found [here](https://github.com/IBM/Ansible-OpenShift-Provisioning/releases).
This release was tested with OpenShift v4.22 and below.

## What's new:
* **OpenShift Virtualization day-2 operator playbook** — new `playbooks/operators/install_ocp_virt.yaml`
  installs Node Feature Discovery, cert-manager, and OpenShift Virtualization in sequence on a
  running OCP 4.19+ cluster on IBM Z / LinuxONE (s390x). Creates the `HyperConverged` CR to
  activate the full KVM-based virtualization stack alongside containers in the same OCP cluster.
  Includes 14 preflight checks, fully configurable `HyperConverged` spec, and an optional
  end-to-end test VM. See [`docs/run-the-playbooks.md`](docs/run-the-playbooks.md) and
  [`inventories/default/group_vars/operators.yaml.template`](inventories/default/group_vars/operators.yaml.template)
  for usage and configuration.
* Enable CEX based LUKS encryption
* Updated hcp.yaml with CatalogSource image parameter for MCE installation
* Added workflows to integrate github actions for PR validations
* New [`download_kubeconfig`](roles/download_kubeconfig/README.md) role for downloading kubeconfig and kubepassw files from bastion host

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

### Deprecated section:

#### Support for openvpn is being deprecated due to issues with RHEL9. It will be removed in one of the upcoming releases. For the time being this feature is disabled by setting setup_openvpn variable to False.
#### Support for RHEL8. RHEL8 support will be removed in one of the upcoming releases.
