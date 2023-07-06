# Step 2: Set Variables - Jumphost
- <b>OPTIONAL</b> - only required if hypervisor's 'network_mode' variable is set to 'nat' for NAT-based networking.
- These variables apply to the jumphost, which is the server that acts as an SSH tunnel to the hypervisors' guest VMs when using NAT-based networking.
- Can be the same host as the hypervisor itself, but not necessarily.

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**ansible_host** | Hostname or IPv4 address for Ansible to connect to via SSH. | 192.168.1.1
**ansible_user** | Username for Ansible to connect as via SSH. | admin
**ansible_password** | Do not change. Set in Ansible Vault (next step) - File server </br >user's SSH password. Jumphost user's password. | "{{ vault_jumphost_pass }}"
**ssh_jumphost_private_key_file** | Absolute path to a private SSH key on the jumphost</br > to create a tunnel to the hypervisor's private network. | "/home/{{ ansible_user }}/.ssh/id_rsa"
