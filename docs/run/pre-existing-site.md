# Step 4: Run the Playbooks
## Additional - Pre-Existing Site Master Playbook
* Run this shell command to run the [pre_existing_site.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/pre_existing_site.yaml) playbook:
```
ansible-playbook playbooks/pre_existing_site.yaml
```
### Overview
* Use this version of the master playbook if you are using a pre-existing LPAR(s) with RHEL already installed.
### Outcomes
* Same outcome as running playbooks 0-7 or site.yaml, excluding changes from 1 & 2. 
* This will not create LPAR(s) nor boot your RHEL hypervisor(s).
* At the end you will have an OpenShift cluster deployed and first-time login credentials.