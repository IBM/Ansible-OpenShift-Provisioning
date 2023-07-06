# Step 2: Set Variables - Overview
* In a text editor of your choice, open the template of the [inventory file](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/inventories/default/inventory.yaml.template). Make a copy of it called inventory.yaml and paste it into the same directory as its template.
* inventory.yaml is your master variables file and you will likely reference it many times throughout the process. 
* The default inventory can be found at [inventories/default](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/inventories/default). To easily switch which inventory you are managing, change the 'inventory=' path in [ansible.cfg](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/ansible.cfg).
* The variables marked with an `X` are required to be filled in. Many values are pre-filled with sesible defaults or are optional. Optional values are commented out; in order to use them, remove the `#` and fill them in.
* This is the most important step in the process. Take the time to make sure everything here is correct.
* <u>Note on YAML syntax</u>: Only the lowest value in each hierarchicy needs to be filled in. For example, at the top of the inventory, 'all' and 'vars' need a value, they are just headers, but the key 'absible_ssh_private_key_file' does need a value. There are X's where input is required to help you with this.
* Scroll the table to the right to see examples for each variable.
* Variables with values that look like this: "{{ vault_controller_pass }}" with 'vault_' in them are set in Ansible Vault, which is the [next step](../setup-vault.md). Skip for now.

* To learn more about how variables work, see [Ansible's documentation](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html).