# Step 4: Run the Playbooks
## 2 Create Hypervisors Playbook
<img src="../../images/2-create-hypervisors.png" width="100%"/>

* This playbook can be skipped if you are using pre-existing LPARs/hypervisors. Skip to [playbook 3](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/3_setup_hypervisors.yaml).
* Run this shell command to run the [2_create_hypervisors.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/2_create_hypervisors.yaml) playbook:
```
ansible-playbook playbooks/2_create_hypervisors.yaml
```
### Pre-Requisites
* Each LPAR/hypervisor that is to be created has to have a corresponding hostvars file filled out, using [inventories/default/hostvars/hypervisor_X.yaml.template]((https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/inventories/default/host_vars/)).
* Create a copy of the template, name it hypevisor_X.yaml, replacing the X with the hypervisor's number from inventory.yaml
* Fill out the variables there.
* Uses the Hardware Management Console (HMC) API, so your Central Processing Complex (CPC, aka the whole IBM zSystems box) must be in Dynamic Partition Manager (DPM) mode.
## 2 Create Hypervisors Playbook
### Overview
* First-time installation of Red Hat Enterprise Linux (RHEL) installed natively on the Logical Partition(s). 
* Uses the Hardware Management Console (HMC) API, so your system must be in Dynamic Partition Manager (DPM) mode. 
* Configuration files are passed to the file server and RHEL is booted and then kickstarted for fully automated setup.
### Outcomes
* LPAR(s) started up in 'Active' state.
* Configuration files (cfg, ins, prm) for the hypervisors(s) are on the file server in the provided configs directory.
### Notes
* Recommended to open the HMC via web-browser to watch the Operating System Messages for each LPAR as they boot in order to debug any potential problems.