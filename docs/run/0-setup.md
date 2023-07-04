# Step 4: Run the Playbooks
## 0 Setup Playbook
<img src="../../images/0-setup.png" width="100%"/>

* Run this shell command to run the [0_setup.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/0_setup.yaml) playbook:
```
ansible-playbook playbooks/0_setup.yaml
```
### Overview
First-time setup of the Ansible Controller, the machine running Ansible
### Outcomes
* Packages and Ansible Galaxy collections are confirmed to be installed properly
* host_vars files are confirmed to match KVM host(s) hostnames
* Ansible inventory is templated out and working properly
* SSH key generated for Ansible passwordless authentication
* SSH agent is setup on the Ansible Controller
* Ansible SSH key is copied to the file server
### Notes
* You can use an existing SSH key as your Ansible key, or have Ansible create one for you. It is highly recommended to use one without a passphrase.