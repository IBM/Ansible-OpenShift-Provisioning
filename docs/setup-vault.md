# Step 3: Setup Ansible Vault
* Ansible Vault helps to protect sensitive variables by encrypting them.
* In order to properly leverage Ansible Vault for the playbooks, follow these steps:

###### 1. Find the Vault template at [inventories/default/group_vars/all/vault.yaml.template](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/inventories/default/group_vars/all/vault.yaml.template).
###### 2. Create a copy of 'vault.yaml.template' in the same folder and rename it 'vault.yaml'
###### 3. Fill out the variables, following the table below's descriptions.
###### 4. Set the Vault password by running the following command from the project's root directory (top-level folder where 'ansible.cfg' file is): 
<b>Note:</b> Make sure to change '`vault-password`'
```
echo 'vault-password' > .password.txt && chmod 600 .password.txt
```
###### 5. Encrypt the Ansible Vault by running the following command:
```
ansible-vault encrypt group_vars/db_servers/vault.yaml
```

* For more on working with Ansible Vault, please see [Ansible's documentation](https://docs.ansible.com/ansible/latest/vault_guide/index.html).

**Variable Name** | **Description** | **Example**
:--- | :---
**vault_redhat_pass** | Password to Red Hat above user's account. Used to</br > auto-attach necessary subscriptions to hypervisor(s),</br > bastion, and pull live images for OpenShift. | Pa$sw0rd!
**vault_controller_pass** | The password to the machine running Ansible (localhost).</br > This will only be used for two things: to ensure you've installed</br > the pre-requisite packages if you're on Linux, and to add the</br > cluster login URL to your /etc/hosts file. | Pa$sw0rd!
**vault_redhat_pull_secret** | Pull secret for OpenShift, comes from Red Hat's [Hybrid Cloud Console](https://console.redhat.com/openshift/install/ibmz/user-provisioned). | {"auths":[...]@gmail.com"}}}
**vault_bastion_pass** | The password to the bastion's admin user. | Pa$sw0rd!
**vault_bastion_root_pass** | Only required if bastion's 'create' is 'True' - Bastion root password. | Pa$sw0rd!
**vault_file_server_pass** | Password to authenticate to the file server. | Pa$sw0rd!
**vault_jumphost_pass** | Only required if 'network_mode' is set to 'nat' - </br >password to jumphost server. | Pa$sw0rd!
**vault_hypervisor_1_pass** | The password for the first hypervisor's admin user. | Pa$sw0rd!
**vault_hypervisor_1_root_pass** | Only required if creating a hypervisor - the root password</br > for the</br > first hypervisor. | Pa$sw0rd!
**vault_hypervisor_2_pass** | The password for the second hypervisor's admin user. | Pa$sw0rd!
**vault_hypervisor_2_root_pass** | Only required if creating two hypervisors - the root password</br > for the second hypervisor. | Pa$sw0rd!
**vault_hypervisor_3_pass** | The password for the third hypervisor's admin user. | Pa$sw0rd!
**vault_hypervisor_3_root_pass** | Only required if creating three hypervisors - the root password</br > for the third hypervisor. | Pa$sw0rd!
**vault_hmc_1_pass** | The password that the HMC API call will use to authenticate</br > for the first LPAR. | Pa$sw0rd!
**vault_hmc_2_pass** | Only required if creating two LPARs. The password that the</br > HMC API call will use to authenticate for the second LPAR. | Pa$sw0rd!
**vault_hmc_3_pass** | Only required if creating three LPARs. The password that</br > the HMC API call will use to authenticate for the third LPAR. | Pa$sw0rd!
**vault_hcp_pull_secret** | Only required if configuring HyperShift. Pull secret for Managed Cluster. | {"auths":[...]@gmail.com"}}}
**vault_hcp_password** | Only required if configuring HyperShift. Password to authenticate to the Managed Cluster. | Pa$sw0rd!