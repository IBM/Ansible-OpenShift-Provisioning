# Step 4: Run the Playbooks
## 3 Setup Hypervisors Playbook
<img src="../../images/3-setup-hypervisors.png" width="100%"/>

* Run this shell command to run the [3_setup_hypervisors.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/3_setup_hypervisors.yaml) playbook:
```
ansible-playbook playbooks/3_setup_hypervisors.yaml
```
### Overview
Configures the RHEL server(s) installed natively on the LPAR(s) to act as virtualization hypervisor(s) to host the virtual machines that make up the eventual cluster.
### Outcomes
* Ansible SSH key is copied to all hypervisors for passwordless authentication
* RHEL subscription is auto-attached to all hypervisors
* Software packages specified in inventory have been installed
* Cockpit console enabled for Graphical User Interface via web browser. Go to http://kvm-ip-here:9090 to view it
* Libvirt is started and enabled
* A macvtap or NAT virtual network has been created