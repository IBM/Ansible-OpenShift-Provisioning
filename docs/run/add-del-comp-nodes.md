# Step 4: Run the Playbooks
## Add Compute Nodes Playbook
* Run this shell command to run the [add_compute_nodes.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/add_compute_nodes.yaml) playbook:
```
ansible-playbook playbooks/add_compute_nodes.yaml
```
### Overview
* After the cluster is installed, use this playbook to add compute nodes to the cluster.
* First, add sections for the new compute nodes in inventory.yaml
* Then, allocate them to hypervisors by placing their Ansible inventory hostnames in the hypervisors' 'guests' lists. 
* Finally, run the playbook.
### Outcomes
* Update ignition files
* Add new nodes to DNS configuration, if hosted on bastion
* Add new nodes to loadbalancer configuration, if hosted on bastion
* Create new virtual machines on hypervisors
* Admit new nodes into the cluster by approving CSRs and waiting until 'Ready'

## Delete Compute Nodes Playbook
* Run this shell command to run the [del_compute_nodes.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/del_compute_nodes.yaml) playbook:
```
ansible-playbook playbooks/del_compute_nodes.yaml
```
### Overview
* After the cluster is installed, use this playbook to delete compute nodes to the cluster.
* First, remove the inventory hostnames associated with the compute nodes to be deleted from hypervisors 'guests' lists. 
* Then, run the playbook.
* Note: Do not delete / comment-out the compute nodes to-be-deleted's hostvars section until after the playbook is complete. These variables are still needed to full remove them.
* Once the playbook is complete, you can delete / comment-out the compute nodes' section(s).
### Outcomes
* Mark nodes as 'Unschedulable'
* Safely evict pods from nodes
* Create backup of nodes
* Set nodes to 'power off' status
* Remove nodes from DNS configuration, if hosted on bastion
* Remove nodes from loadbalancer configuration, if hosted on bastion
* Delete virtual machines on hypervisors