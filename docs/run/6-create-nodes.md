# Step 4: Run the Playbooks
## 6 Create Nodes Playbook
<img src="../../images/6-create-nodes.png" width="100%"/>

* Run this shell command to run the [6_create_nodes.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/6_create_nodes.yaml) playbook:
```
ansible-playbook playbooks/6_create_nodes.yaml
```
### Overview
* OCP cluster's nodes are created and the control plane is bootstrapped
* Nodes are allocated to hypervisor hosts by placing the nodes' inventory hostnames into the respective hypervisors' 'guests' list.
### Outcomes
* CoreOS initramfs and kernel are pulled down
* Control nodes are created and bootstrapped
* Bootstrap has been created, done its job connecting the control plane, and is then destroyed
* Compute nodes are created, as many as is specified in inventory
### Notes
* To watch the bootstrap do its job connecting the control plane: first, SSH to the bastion, then change to root (sudo -i), from there SSH to the bootstrap node as user 'core' (e.g. ssh core@bootstrap-ip). 
* Once you're in the bootstrap run the following command:
```
journalctl -b -f -u release-image.service -u bootkube.service 
```
* Expect many errors as the control planes come up. You're waiting for the message 'bootkube.service complete'