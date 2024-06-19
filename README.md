# Ansible-Automated OpenShift Provisioning on KVM on IBM zSystems / LinuxONE
The documentation for this project can be found [here](https://ibm.github.io/Ansible-OpenShift-Provisioning/).

Release v2.1.0:
This README contains the information for the current release only.
The whole history of the releases can be found [here](https://github.com/IBM/Ansible-OpenShift-Provisioning/releases).

## What's new:
* Added RHEL9 support. RHEL8 still supported (two sets of kickstart files for bastion).
* 3 node cluster. You can specify a 3 node cluster without the need of compute nodes.
* Several bug fixes and improvements.

### Variables renamed:

#### Only new variables introduced but no renamed.

### Deprecated section:

#### Support for openvpn is being deprecated due to issues with RHEL9. It will be removed in one of the upcoming releases. For the time being this feature is disabled by setting setup_openvpn variable to False.
#### Support for RHEL8. RHEL8 support will be removed in one of the upcoming releases.
