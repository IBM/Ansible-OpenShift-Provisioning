# Step 5: Run the Playbooks
* Navigate to the [root folder of the cloned Git repository](https://github.com/IBM/Ansible-OpenShift-Provisioning) in your terminal (`ls` should show [ansible.cfg](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/ansible.cfg)).
* To run all the playbooks at once, start the master playbook by running this shell command: 
```
ansible-playbook playbooks/site.yaml 
```
* Alternatively, run each part step-by-step by running one playbook at a time. Here's the list of playbooks to be run in order, also found in [playbooks/site.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/site.yaml):
    * [create_kvm_host](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/create_kvm_host.yaml)
    * [setup_kvm_host](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/setup_kvm_host.yaml)
    * [create_bastion](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/create_bastion.yaml)
    * [setup_bastion](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/setup_bastion.yaml)
    * [create_nodes](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/create_nodes.yaml)
    * [ocp_verification](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/ocp_verification.yaml)
* Watch Ansible as it completes the installation, correcting errors if they arise. 
* To look at what tasks are running in detail, open the playbook or roles/role-name/tasks/main.yaml
* If the process fails in error, go through the steps in the [troubleshooting](troubleshooting.md) page. 
```
ansible-playbook playbooks/setup_bastion.yaml --tags 'httpd,get_ocp' 
```