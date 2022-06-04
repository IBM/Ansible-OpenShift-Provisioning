# Step 4: Run Setup Playbook
* Navigate to the [root folder of the cloned Git repository](https://github.com/IBM/Ansible-OpenShift-Provisioning) in your terminal (`ls` should show [ansible.cfg](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/ansible.cfg)).
* Run this shell command:
```
ansible-playbook playbooks/setup.yaml --ask-vault-pass
```