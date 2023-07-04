# Step 4: Run the Playbooks
## 4 Create Bastion Playbook
<img src="../../images/4-create-bastion.png" width="100%"/>

* This playbook can be skipped if you are using pre-existing bastion. Skip to [playbook 5](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/5_setup_bastion.yaml).
* Run this shell command to run the [4_create_bastion.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/4_create_bastion.yaml) playbook:
```
ansible-playbook playbooks/4_create_bastion.yaml
```
### Overview
* Creates the bastion guest VM on whichever hypervisor has 'bastion' in its 'guests' list in inventory
* The bastion hosts essential services for the cluster
* If you already have a bastion server, that can be used instead of running this playbook.
### Outcomes
* Bastion configs are templated out to the file server
* Bastion is booted using virt-install
* Bastion is kickstarted for fully automated setup of the operating system
### Notes
* This can be a particularly sticky part of the process
* If any of the variables used in the virt-install or kickstart are off, the bastion won't be able to boot.
* Recommend watching it come up from the hypervisor's cockpit. Go to http://hypervisor-ip-here:9090 via web-browser to view it. You'll have to sign in, enable administrative access (top right), and then click on the virtual machines tab on the left-hand toolbar.