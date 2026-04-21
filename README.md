# Ansible-Automated OpenShift Provisioning on KVM on IBM zSystems / LinuxONE
The documentation for this project can be found [here](https://ibm.github.io/Ansible-OpenShift-Provisioning/).

Release v2.4.0:
This README contains the information for the current release only.
The whole history of the releases can be found [here](https://github.com/IBM/Ansible-OpenShift-Provisioning/releases).
This release was tested with OpenShift v4.21 and below.

## What's new:
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
