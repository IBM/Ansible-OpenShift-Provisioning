# Step 4: Run the Playbooks
## Additional - Reinstall Cluster Playbook
* Run this shell command to run the [reinstall_cluster.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/reinstall_cluster.yaml) playbook:
```
ansible-playbook playbooks/reinstall_cluster.yaml
```
### Overview
* In case the cluster needs to be completely reinstalled, run this playbook. 
* It will refresh the ingitions that expire after 24 hours, teardown all the nodes and re-create them, and then verify the installation.
* It will not reinstall the bastion or hypervisors.
### Outcomes
* get_ocp role runs.
    * Delete the folders /var/www/html/bin and /var/www/html/ignition
    * CoreOS roofts is pulled to the bastion
    * OCP client and installer are pulled down
    * oc, kubectl and openshift-install binaries are installed
    * OCP install-config is created from scratch, templated and backed up
    * Manfifests are created
    * OCP install directory found at /root/ocpinst/ is deleted, re-created and populated with necessary files.
    * Ignition files for the bootstrap, control, and compute nodes are transferred to HTTP or FTP accessible directory for booting nodes.
* 6 Create Nodes playbook runs, tearing down and recreating cluster nodes
* 7 OCP Verification playbook runs, verifying new deployment
