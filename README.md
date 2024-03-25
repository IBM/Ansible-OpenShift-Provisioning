# Ansible-Automated OpenShift Provisioning on KVM on IBM zSystems / LinuxONE
The documentation for this project can be found [here](https://ibm.github.io/Ansible-OpenShift-Provisioning/).

## What's new:

### Variables renamed:

#### Rename the variable defining the name of the virtual network for clarity. **env.bridge_name** is renamed to **env.vnet_name**. 

### Deprecated section:

#### Support for openvpn is being deprecated due to issues with RHEL9. It will be removed in one of the upcoming releases. For the time being this feature is disabled by setting setup_openvpn variable to False. 
