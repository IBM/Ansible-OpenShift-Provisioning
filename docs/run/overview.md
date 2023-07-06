# Step 4: Run the Playbooks
## Overview
<img src="../../images/overview.png" width="100%"/>

* Navigate to the [root folder of the cloned Git repository](https://github.com/IBM/Ansible-OpenShift-Provisioning) in your terminal (`ls` should show [ansible.cfg](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/ansible.cfg)).
* Run one of the setup shell scripts, based on whether you are using Mac or Linux (Red Hat based distribtions) as your Ansible Controller:
```
./setup_mac.sh
```
OR
```
./setup_rhel.sh
```
* These scripts install software dependencies, install Ansible itself, install Ansible Galaxy collections, and kick off the first Ansible playbook.
* These are very simple shell scripts, if they throw an error, open them up and see what commands are being used and run them manually if needed.
* The last command of the setup script runs an Ansible Playbook, 0_setup.yaml, which installs additional software, runs pre-flight checks and connects to the file server in preparation for the next playbook.
* Then, run the playbooks in order 1-7 playbook-by-playbook.
* For first-time users of these playbooks, it is recommended to follow the docuemtation along as you execute each playbook.
* Choose whether to start with playbook 1 or 3, based on whether you have an existing LPAR with RHEL pre-installed.
```
ansible-playbook playbooks/1_create_lpars.yaml
```
OR
```
ansible-playbook playbooks/3_setup_hypervisors.yaml
```
* Here's the full list of playbooks to be run in order, full descriptions can be found in the next pages of this section of the documentation:
    * [0_setup.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/0_setup.yaml)
    * [1_create_lpars.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/1_create_lpars.yaml)
    * [2_create_hypervisors.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/2_create_hypervisors.yaml)
    * [3_setup_hypervisors.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/3_setup_hypervisors.yaml)
    * [4_create_bastion.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/4_create_bastion.yaml)
    * [5_setup_bastion.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/5_setup_bastion.yaml)
    * [6_create_nodes.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/6_create_nodes.yaml)
    * [7_ocp_verification.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/7_ocp_verification.yaml)
* Watch Ansible as it completes the installation, correcting errors if they arise. 
* To look at what tasks are running in detail, open the playbook or roles/role-name/tasks/main.yaml
* Alternatively, to run all the playbooks at once, start the master playbook by running this shell command: 
```
ansible-playbook playbooks/site.yaml 
```
* If the process fails in error, go through the steps in the [troubleshooting](../troubleshooting.md) page. 
* At the end of the the last playbook, follow the printed instructions for first-time login to the cluster.