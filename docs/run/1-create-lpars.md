# Step 4: Run the Playbooks
## 1 Create LPARs Playbook
<img src="../../images/1-create-lpars.png" width="100%"/>

* This playbook can be skipped if you are using pre-existing LPARs/hypervisors. Skip to [playbook 3](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/3_setup_hypervisors.yaml).
* Run this shell command to run the [1_create_lpars.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/1_create_lpars.yaml) playbook:
```
ansible-playbook playbooks/1_create_lpars.yaml
```
### Pre-Requisites
* Each LPAR/hypervisor that is to be created has to have a corresponding hostvars file filled out, using [inventories/default/hostvars/hypervisor_X.yaml.template]((https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/inventories/default/host_vars/)).
* Create a copy of the template, name it hypevisor_X.yaml, replacing the X with the hypervisor's number from inventory.yaml
* Fill out the variables there.
* Uses the Hardware Management Console (HMC) API, so your Central Processing Complex (CPC, aka the whole IBM zSystems box) must be in Dynamic Partition Manager (DPM) mode.
### Overview
* Creation of as many Logical Partitions (LPARs) are defined in inventory
### Outcomes
* Create as many LPARs as are defined in inventory
* Attach any number of Networking Interface Cards (NICs) to LPARs
* Attach any number of storage groups to LPARs
* LPARs are in 'Stopped' state
### Notes
* Recommend opening the HMC via web-browser to watch the LPARs come up