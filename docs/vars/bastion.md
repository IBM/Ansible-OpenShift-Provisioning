# Step 2: Set Variables - Bastion
- These variables apply to the cluster's bastion host, which is the server that acts as the connection point to the cluster's nodes, and optionally hosts essential services. 
- Can be created as a guest on a hypervisor or connected to elsewhere.
- If using these playbooks to create the bastion ('create' variable below is 'True'), then you must follow the instruction below this first table.

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**bastion_ip** | IPv4 address of the bastion host. | 192.168.1.4
**bastion_user** | Admin user on the bastion host, not necessarily the one used </br >to connect to via SSH. | admin
**ansible_host** | IP or hostname Ansible will use to connect to via SSH. Leave</br > as is to use same value as bastion_ip var. | "{{ bastion_ip }}"
**ansible_user** | Username for Ansible to connect as via SSH. Leave as is to</br > use same value as bastion_user var. | "{{ bastion_user }}"
**ansible_become_password** | Do not change. Set in Ansible Vault (next step) - Bastion</br > user's SSH password. | "{{ vault_bastion_pass }}"
**pkgs** | Packages to be installed on host. | [ haproxy, httpd, bind, bind-utils, expect, firewalld, mod_ssl, python3-policycoreutils, rsync ]
**fqdn** | Fully-qualified domain name of the bastion. | bastion123.ocp_na_east.ihost.com
**nameservers** | List of DNS nameservers for this host. If 'setup_dns'</br > is True (below) this should be set to "{{ bastion_ip }}" | - 192.168.1.254<br />- 192.168.1.253
**forwarder** | IPv4 address of DNS forwarder for external name resolution. | 1.1.1.1
**setup_dns** | True or False - setup bastion host as the DNS nameserver</br > for the cluster. | True
**setup_lb** | True or False - setup bastion host as the loadbalancer</br > for the cluster. If 'False' must fill in next two vars. | True
**lb_public_ip** | Only required if 'setup_lb' is 'False', public IPv4</br > address of the cluster's loadbalancer. | 123.45.67.89
**lb_private_ip** | Only required if 'setup_lb' is 'False', private IPv4</br > address of the cluster's loadbalancer. | 192.168.1.230
**ssh_cluster_private_key_file**: | Absolute path to a private SSH key on the bastion</br > (will be created if it doesn't already exist) to be used</br > as the SSH key for the cluster. | /root/.ssh/id_rsa
**create** | True or False - create the bastion host or not. If 'True' </br >must follow the directions below. | True

## <b>OPTIONAL</b> 'Create' Variables
- The variables below are only required if you will be using Ansible to create the bastion (the 'create' variable just above is 'True').
1) Go to [inventories/default/host_vars/](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/inventories/default/host_vars/) and copy bastion.yaml.template into the same folder.
2) Rename the copied template to 'bastion.yaml'
3) Fill in the following variables.

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**vm_name** | Name of the guest virtual machine from the perspective of the hypervisor. | bastion
**disk_size** | Amount of virtual storage capacity allocated to this VM, in gigabytes. | 30
**ram** | Amount of virtual memory allocated to this VM, in megabytes. | 4096
**swap** | Amount of virtual storage capacity allocated to swap for this VM, </br >in megabytes. | 4096
**vcpu** | Number of virtual CPUs allocated to this VM. | 4
**netmask** | Subnet size for the VMs IP in dotted decimal notation. | 255.255.255.0
**gateway** | IP address that acts as the exit point for the VM to reach other networks. | 192.168.1.1
**interface** | Name of the network device (from Linux perspective) used for connecting</br > the VM to the network. | enc100
**root_pass** | Do not change. Set in Ansible Vault (next step) - Bastion's root SSH password. | "{{ vault_bastion_root_pass }}"