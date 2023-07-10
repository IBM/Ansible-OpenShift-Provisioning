# Step 2: Set Variables - Hypervisors
- These variables apply to the hypervisor(s) used to host the cluster's virtual machine (VM) guests. 
- Kernel-based Virtual Machine (KVM) hypervisors are the only type possible with these playbooks as of now.
- Can use/create as many hypervisors as needed, but usually either one or three of them are used for hosting a kubernetes cluster. Using three makes the cluster 'highly available' as the three control nodes can be hosted 1:1 on each hypervisor.
- Each hypervisor has their own set of hostvars and groupvars.
    - <b>groupvars</b>
        - Set in the 'vars' section at the bottom of the 'hypervisors' group section and apply to all hypervisors defined in the group.
        - If you'd like to set these variables differently for one or more hosts, just add the variable to the hostvars section for the hypervisor and set it differently. For more on variable precedence, see [Ansible's documentation](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html) on using variables.
    - <b>hostvars</b> 
        - Set directly under each hypervisor's inventory hostname (i.e. 'hypervisor_1').
        - <b>Note</b>: If using Ansible to create LPARs and install hypervisors' OS ('create' is 'True' for any hypervisors), must follow the directions below this first table.

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**hypervisor_ip** | IPv4 address of the hypervisor. | 192.168.1.1
**hypervisor_user** | Admin user on the hypervisor, not necessarily the</br > one used to connect to via SSH. | admin
**ansible_become_password** | Do not change. Set in Ansible Vault (next step) -</br > Hypervisor user's SSH password. | "{{ vault_hypervisor_1_pass }}"
**guests** | The Ansible inventory hostname(s) associated with</br > the VMs that this hypervisor will host. i.e. the name</br > of the section for each node's variables in this inventory file. | - bastion</br >- control_1</br >- compute_1
**ansible_host** | IP or hostname Ansible will use to connect to via SSH.</br > Leave as is to use same value as hypervisor_ip var. | "{{ hypervisor_ip }}"
**ansible_user** | Username for Ansible to connect as via SSH.</br > Leave as is to use same value as hypervisor_user var. | "{{ hypervisor_user }}"
**virt_type** | Virtualization type, at this point must be 'kvm' as it</br > is the only type possible with these playbooks. | kvm
**cfgs_dir** | Absolute path to the directory where important</br > configuration files (like qcow2 files) will be stored. |  "/home/{{ hypervisor_user }}/ocp"
**pkgs** | Packages to be installed on host. | [ libguestfs, libvirt-client, ..., lvm2 ]
**network_name** | Name of virtual network to be defined</br > that the VM guests will use. | macvtap-net
**network_mode** | Either 'nat' or leave blank to use default MacVTap. | 
**network_interface** | Which network interface to connect</br > the virtual network to. | "{{ ansible_default_ipv4.interface }}"
**ip_forward** | If 'network_mode' above is 'nat', it is highly</br > recommended to set this to '1' to enable IP forwarding, </br >which is required for NAT-based networking, but can</br > be setup in a variety of ways important to network security.</br > This will change sysctl at the kernel level. | 0
**pool_name** | Name of virtual storage pool to be created/managed</br > that the VM guests will use. | "{{ metadata_name }}_vdisk"
**pool_path** | Absolute path to the storage pool used by VM guests. | "/home/{{ hypervisor_user }}/VirtualMachines/{{ metadata_name }}"
**create** | True or False - create this hypervisor via Ansible</br > Playbooks. If 'True' must follow additional steps below. | True


## <b>OPTIONAL</b> 'Create' Variables
- The variables below are only required if you will be using Ansible to create hypervisor(s) (the 'create' variable just above is 'True'). 
- Follow the steps below for <i>each</i> hypervisor to be created.
- <b>Note</b>: The Central Processing Complex (CPC) must be in Dynamic Parition Manager (DPM) mode, as Ansible leverages the Hardware Management Console's (HMC) Application Programming Interface (API) to manage Logical Paritions (LPARs)
1) Go to [inventories/default/host_vars/](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/inventories/default/host_vars/) and copy hypervisor_X.yaml.template into the same folder.
2) Rename the copied template to 'hypervisor_1.yaml' (or hypervisors_2.yaml, etc. to match the section name in inventory.yaml)
3) Fill in the following variables.


**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**hostname** | DNS short hostname of the hypervisor. | hv-1
**netmask** | Subnet size for the hypervisor's IP in dotted decimal notation. | 255.255.255.0
**gateway** | IP address that acts as the exit point for the hypervisor to</br > reach other networks. | 192.168.1.1
**nameservers** | List of DNS nameserver(s) for this hypervisor. | - 192.168.1.254<br />- 192.168.1.253
**device1** | Name of the network device (from Linux perspective) used</br > for connecting the hypervisor to the network. | enc1
**device2** | A second, optional name of a network device (from Linux</br > perspective) used for connecting the hypervisor to the network. | enc2
**root_pass** | Change the 'X' to match the hypervisor's inventory hostname</br > number. Set in Ansible Vault (next step) - Hypervisor's root SSH password. | "{{ vault_hypervisor_X_root_pass }}"
**cpc_name** | Name of the Central Processing Complex to be managed. | ZSYSTEM1
**hmc_host** | IP or hostname of the Hardware Management Console (HMC)</br > to connect to via API. | 192.168.1.200
**hmc_user** | Username to connect as via HMC API. | admin
**hmc_pass** | Change the 'X' to match the hypervisor's inventory hostname</br > number. Set in Ansible Vault (next step) - Password</br > to authenticate with HMC API. | "{{ vault_hmc1_pass }}"
**lpar_name** | Name of the Logical Parition (LPAR) to be created/managed. | OCP1
**lpar_desc** | Description of the Logical Parition (LPAR) to be created/managed. | Hypervisor 1 for RHOCP cluster.
**ifl_count** | Number of Integrated Facilities for Linux (IFLs) to be allocated to this LPAR. | 6
**mem_init** | Amount of initial memory allocated to this LPAR upon startup, in megabytes. | 50000
**mem_max** | Maximum amount of memory usable by this LPAR, in megabytes. | 96000
**weight_init** | Weight to give this LPAR upon startup. | 100
**weight_min** | Minimum weight this LPAR could have at any time. | 50
**weight_max** | Maximum weight this LPAR could have at any time. | 100
**nics** | Section for Network Interface Cards (NICs) to be attached to the</br > LPAR. Add as many as needed, just make sure to follow the</br > provided list format.
**name** | Name of Network Interface Card (NIC) to attach to the LPAR. | OCP-Access1
**adapter** | The physical adapter name reference to the logical adapter for the LPAR. | 10Gb-E
**port** | The port number for the NIC. | 0
**dev_num** | The logical device number for the NIC. In hex format. | 0x0001
**storage_groups** | Section for Storage Groups to attach to the LPAR. Add as many as</br > needed, just make sure to follow the provided list format.
**name** | Name of the storage group to be attached to the LPAR. | OCP-storage-01
**boot_parms** | Boot parameters of disk to be passed via the .prm file to the FTP server </br >for installation of hypervisor's operating system (OS). | rd.zfcp=0.0.F200,0xC05076CD908000FA,0x0000000000000000</br >rd.zfcp=0.0.F200,0xC05076CD908000F6,0x0000000000000000</br >rd.zfcp=0.0.F200,0xC05076CD908000F9,0x0000000000000000</br >rd.zfcp=0.0.F200,0xC05076CD908000F7,0x0000000000000000</br >OR</br >rd.dasd=0123</br >rd.dasd=0456