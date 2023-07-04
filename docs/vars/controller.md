# Step 2: Set Variables - Controller
These variables apply to the Ansible controller, which is the server where the Ansible Playbooks will be executed from, i.e. your laptop or Ansible Automation Controller (Tower).

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**ansible_connection** | Do not change - Tells Ansible this is localhost. | local
**ansible_become_password** | Do not change. Set in Ansible Vault (next step) <br > Controller user's SSH password. | "{{ vault_controller_pass }}"
**pkgs** | Packages to be installed on host. | [ openssh, expect, sshuttle ]