# Vault and Tags
A quick note explaining how to use tags and Ansible Vault.
## Tags
* To be more selective with what parts of a playbook are run, use tags. 
* To determine what part of a playbook you would like to run, open the playbook you'd like to run and find the roles parameter. Each [role](https://github.com/IBM/Ansible-OpenShift-Provisioning/tree/main/roles) has a corresponding tag.
* There are also occasionally tags for sections of a playbook or within the role themselves.
* This is especially helpful for troubleshooting. You can add in tags under the `name` parameter for individual tasks you'd like to run. 
* Here's an example of using a tag:
```
ansible-playbook playbooks/setup_kvm_host.yaml --tags "section_2,section_3"
```
* This runs only the parts of the [setup_kvm_host playbook](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/setup_kvm_host.yaml) marked with tags section_2 and section_3. To use more than one tag, they must be quoted (single or double) and comma-separated (with or without spaces between).

## Vault
* For security purposes, the [setup playbook](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/setup.yaml) transfers passwords and sensitive information entered into the [environment variables file](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/inventories/default/group_vars/all.yaml) to the [Ansible Vault](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/vault.yaml) and then encrypts them.
* To decrypt the Ansible Vault to view its contents, run the following command:
```
ansible-playbook playbooks/vault.yaml --tags decrypt --ask-vault-pass
```
* To encrypt the Ansible Vault to re-secure its contents, run the following command:
```
ansible-playbook playbooks/vault.yaml --tags encrypt --ask-vault-pass
```