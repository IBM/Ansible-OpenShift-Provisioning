# Step 4: Run the Playbooks
## 7 OCP Verification Playbook
<img src="../../images/7-ocp-verification.png" width="100%"/>

* Run this shell command to run the [7_ocp_verification.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/7_ocp_verification.yaml) playbook:
```
ansible-playbook playbooks/7_ocp_verification.yaml
```
### Overview
Final steps of waiting for and verifying the OpenShift cluster to complete its installation.
### Outcomes
* Certificate Signing Requests (CSRs) have been approved
* All nodes are in ready state
* All cluster operators are available
* OpenShift installation is verified to be complete
* Temporary credentials and URL are printed to allow easy first-time login to the cluster
<img src="../../images/install-complete.png" width="100%"/>

### Notes
* These steps may take a long time and the tasks are very repetitive because of that
* If your cluster has a very large number of compute nodes or insufficient resources, more rounds of approvals and time may be needed for these tasks.
* If you made it this far, congratulations!
* To install a new cluster, copy your inventory directory, change the 'inventory' variable in the ansible.cfg to the new path, change the variables, and start again. With all the customizations to the playbooks you made along the way still intact.