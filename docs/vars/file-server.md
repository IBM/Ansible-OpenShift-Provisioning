# Step 2: Set Variables - File Server
- These variables apply to the file server, which provides necessary configuration and installation files for installation of hypervisors and the bastion. 
- Must have SSH access.
- <b>Note:</b> If using these playbooks to create LPARs and install hypervisors, FTP is mandatory as HTTP is not allowed by the HMC. However, you can still set 'protocol' variable to 'http' because FTP is hardcoded in when mandatory. Setting 'protocol' to 'ftp' will just ensure that 'ftp' is always used.
- Can be the same server as the hypervisor if:
  - not creating LPARs and installing hypervisors and 
  - using NAT-based networking (hypervisor's 'netowrk_mode' var is set to 'nat')

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**fs_ip** | IPv4 address of the file server. | 192.168.1.220
**fs_user** | User to fetch files as. | ftp-user
**fs_pass** | Do not change. Set in Ansible Vault (next step) - Password to</br > authenticate as fs_user. | "{{ vault_file_server_pass }}"
**ansible_host** | IP or hostname for Ansible to connect to via SSH, keep as is to</br > use fs_ip. | "{{ fs_ip }}"
**ansible_user** | Username for Ansible to connect as via SSH. Leave as is to </br >use same value as fs_user. | "{{ fs_user }}"
**ansible_become_password** | Password for Ansible to authenticate via SSH.</br > Leave as is to use same value as fs_user. | "{{ fs_pass }}"
**protocol** | 'http' or 'ftp' - Which transfer protocol would you like to use? | http
**iso_os_variant** | RHEL version closest to ISO file used to install hypervisors</br > and/or bastion. | rhel8.7
**doc_root** | Absolute path of document root for file server. | /var/www/html
**iso_mount_dir** | Relative path from 'doc_root' to the directory where the</br > ISO is mounted. | rhel/8.7
**cfgs_dir** | Relative path from 'doc_root' to the directory where</br > configuration files (like kickstart) will be stored. | rhel/cfg_files