# Ansible-Automated OpenShift Provisioning on KVM on IBM zSystems / LinuxONE
The documentation for this project can be found [here](https://ibm.github.io/Ansible-OpenShift-Provisioning/).

## What's new:
* Added support for LPAR based installation. The process for installing based on LPAR will largely use the same playbooks with some modifications to the configuration which can be found in the updated docs.
* Infra nodes on LPAR is currently unsupported, will be added in a later patch.
* Installation with bastion and bootstrap as KVM nodes and also extra worker or compute nodes as KVM along with lpar nodes is supported.

### Variables renamed:

#### Rename the variable defining the name of the virtual network for clarity. **env.bridge_name** is renamed to **env.vnet_name**. 

### Deprecated section:

#### Support for openvpn is being deprecated due to issues with RHEL9. It will be removed in one of the upcoming releases. For the time being this feature is disabled by setting setup_openvpn variable to False. 
