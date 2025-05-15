# Ansible-Automated OpenShift Provisioning on KVM on IBM zSystems / LinuxONE
The documentation for this project can be found [here](https://ibm.github.io/Ansible-OpenShift-Provisioning/).

Release v2.3.0:
This README contains the information for the current release only.
The whole history of the releases can be found [here](https://github.com/IBM/Ansible-OpenShift-Provisioning/releases).
This release was tested with OpenShift v4.19 and below.

## What's new:
* Add support for fips and some minor code allignments
* Added support for zVM Converged Hipersockets for HCP
* HCP - Support for booting DPM LPAR ans attaching as compute node
* Support for LPAR as compute nodes for HCP

### Bug Fixes
* Added installation_disk_id to agents for LPAR HCP
* Boot-artifacts has been renamed as required to boot the agents.
* Creating ABI cluster with ISO boot not working
* Fips support for abi
* HCP - Segregating InfraEnv and Agents into a separate namespace
* Updated agent patch command for HCP kvm

### Variables renamed:
* abi.ocp_installer_url to abi.ocp_installer_base_url

#### Only new variables introduced but no renamed.
* abi.architecture: The installer binary supports two architecture options: multi and s390x. Users are required to specify the appropriate architecture value based on their deployment environment. Values: multi/s390x

### Deprecated section:

#### Support for openvpn is being deprecated due to issues with RHEL9. It will be removed in one of the upcoming releases. For the time being this feature is disabled by setting setup_openvpn variable to False.
#### Support for RHEL8. RHEL8 support will be removed in one of the upcoming releases.
