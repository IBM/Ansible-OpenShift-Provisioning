# Step 2: Set Variables (group_vars)
## Overview
* In a text editor of your choice, open the template of the [environment variables file](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/inventories/default/group_vars/all.yaml.template). Make a copy of it called all.yaml and paste it into the same directory with its template.
* all.yaml is your master variables file and you will likely reference it many times throughout the process. The default inventory can be found at [inventories/default](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/inventories/default).
* The variables marked with an `X` are required to be filled in. Many values are pre-filled or are optional. Optional values are commented out; in order to use them, remove the `#` and fill them in.
* This is the most important step in the process. Take the time to make sure everything here is correct.
* <u>Note on YAML syntax</u>: Only the lowest value in each hierarchicy needs to be filled in. For example, at the top of the variables file env and z don't need to be filled in, but the cpc_name does. There are X's where input is required to help you with this.
* Scroll the table to the right to see examples for each variable.

## 1 - Controller
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**installation_type** | Can be of type kvm or lpar. Some packages will be ignored for installation in case of non lpar based installation. | kvm 
**controller_sudo_pass** | The password to the machine running Ansible (localhost). This will only be used for two things. To ensure you've installed the pre-requisite packages if you're on Linux, and to add the login URL to your /etc/hosts file. | Pas$w0rd!

## 2 - LPAR(s)
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**env.z.high_availability** | Is this cluster spread across three LPARs? If yes, mark True. If not (just in one LPAR), mark False | True
**env.z.ip_forward** | This variable specifies if ip forwarding is enabled or not if NAT network is selected. If ip_forwarding is set to 0, the installed OCP cluster will not be able to access external services because using NAT keep the nodes isolated. This parameter will be set via sysctl on the KVM host. The change of the value is instantly active. This setting will be configured during 3_setup_kvm playbook. If NAT will be configured after 3_setup_kvm playbook, the setup needs to be done manually before bastion is being created, configured or reconfigured by running the 3_setup_kvm playbook with parameter: --tags cfg_ip_forward | 1
**env.z.lpar1.create** | To have Ansible create an LPAR and install RHEL on it for the KVM host, mark True. If using a pre-existing LPAR with RHEL already installed, mark False. | True
**env.z.lpar1.hostname** | The hostname of the KVM host. | kvm-host-01
**env.z.lpar1.ip** | The IPv4 address of the KVM host. | 192.168.10.1
**env.z.lpar1.user** | Username for Linux admin on KVM host 1. Recommended to run as a non-root user with sudo access. | admin
**env.z.lpar1.pass** | The password for the user that will be created or exists on the KVM host.  | ch4ngeMe!
**env.z.lpar2.create** | To create a second LPAR and install RHEL on it to act as another KVM host, mark True. If using pre-existing LPAR(s) with RHEL already installed, mark False. | True
**env.z.lpar2.hostname** | <b>(Optional)</b> The hostname of the second KVM host. | kvm-host-02
**env.z.lpar2.ip** | <b>(Optional)</b> The IPv4 address of the second KVM host. | 192.168.10.2
**env.z.lpar2.user** | Username for Linux admin on KVM host 2. Recommended to run as a non-root user with sudo access. | admin
**env.z.lpar2.pass** | <b>(Optional)</b> The password for the admin user on the second KVM host. | ch4ngeMe!
**env.z.lpar3.create** | To create a third LPAR and install RHEL on it to act as another KVM host, mark True. If using pre-existing LPAR(s) with RHEL already installed, mark False. | True
**env.z.lpar3.hostname** | <b>(Optional)</b> The hostname of the third KVM host. | kvm-host-03
**env.z.lpar3.ip** | <b>(Optional)</b> The IPv4 address of the third KVM host. | 192.168.10.3
**env.z.lpar3.user** | Username for Linux admin on KVM host 3. Recommended to run as a non-root user with sudo access. | admin
**env.z.lpar3.pass** | <b>(Optional)</b> The password for the admin user on the third KVM host. | ch4ngeMe!

## 3 - File Server
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**env.file_server.ip** | IPv4 address for the file server that will be used to pass config files and iso to KVM host LPAR(s) and bastion VM during their first boot. | 192.168.10.201
**env.file_server.port** | The port on which the file server is listening. Will be embedded into all download urls. Defaults to protocol default port. Keep empty `''` to use  default port | 10000
**env.file_server.user** | Username to connect to the file server. Must have sudo and SSH access. | user1
**env.file_server.pass** | Password to connect to the file server as above user. | user1pa$s!
**env.file_server.protocol** | Protocol used to serve the files, either 'ftp' or 'http' | http
**env.file_server.iso_os_variant** | The os variant for the bastion kvm to be created | rhel8.8
**env.file_server.iso_mount_dir** | Directory path relative to the HTTP/FTP accessible directory where RHEL ISO is mounted. For example, if the FTP root is at /home/user1 and the ISO is mounted at /home/user1/RHEL/8.7 then this variable would be RHEL/8.7 - no slash before or after. | RHEL/8.7
**env.file_server.cfgs_dir** | Directory path relative to to the HTTP/FTP accessible directory where configuration files can be stored. For example, if FTP root is /home/user1 and you would like to store the configs at /home/user1/ocpz-config then this variable would be ocpz-config. No slash before or after. | ocpz-config

## 4 - Red Hat Info
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**env.redhat.username** | Red Hat username with a valid license or free trial to Red Hat OpenShift Container Platform (RHOCP), which comes with necessary licenses for Red Hat Enterprise Linux (RHEL) and Red Hat CoreOS (RHCOS). | redhat.user
**env.redhat.password** | Password to Red Hat above user's account. Used to auto-attach necessary subscriptions to KVM Host, bastion VM, and pull live images for OpenShift. | rEdHatPa$s!
**env.redhat.manage_subscription** | True or False. Would you like to subscribe the server with Red Hat? | True 
**env.redhat.pull_secret** | Pull secret for OpenShift, comes from Red Hat's [Hybrid Cloud Console](https://console.redhat.com/openshift/install/ibmz/user-provisioned). Make sure to enclose in 'single quotes'.  | '{"auths":{"cloud.openshift.com":{"auth":"b3Blb...4yQQ==","email":"redhat.user@gmail.com"}}}'

## 5 - Bastion
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**env.bastion.create** | True or False. Would you like to create a bastion KVM guest to host essential infrastructure services like DNS, load balancer, firewall, etc? Can de-select certain services with the env.bastion.options variables below. | True
**env.bastion.vm_name** | Name of the bastion VM. Arbitrary value. | bastion
**env.bastion.resources.disk_size** | How much of the storage pool would you like to allocate to the bastion (in Gigabytes)? Recommended 30 or more. | 30
**env.bastion.resources.ram** | How much memory would you like to allocate the bastion (in megabytes)? Recommended 4096 or more | 4096
**env.bastion.resources.swap** | How much swap storage would you like to allocate the bastion (in megabytes)? Recommended 4096 or more. | 4096
**env.bastion.resources.vcpu** | How many virtual CPUs would you like to allocate to the bastion? Recommended 4 or more. | 4
**env.bastion.resources.vcpu_model_option** | Configure the CPU model and CPU features exposed to the guest | --cpu host
**env.bastion.networking.ip** | IPv4 address for the bastion. | 192.168.10.3
**env.bastion.networking.ipv6** | IPv6 address for the bastion if use_ipv6 variable is 'True'. | fd00::3
**env.bastion.networking.mac** | MAC address for the bastion if use_dhcp variable is 'True'. | 52:54:00:18:1A:2B
**env.bastion.networking.hostname** | Hostname of the bastion. Will be combined with env.bastion.networking.base_domain to create a Fully Qualified Domain Name (FQDN). | ocpz-bastion
**env.bastion.networking.base_domain** | Base domain that, when combined with the hostname, creates a fully-qualified domain name (FQDN) for the bastion? | ihost.com
**env.bastion.networking.subnetmask** | Subnet of the bastion. | 255.255.255.0
**env.bastion.networking.gateway** | IPv4 of he bastion's gateway server. | 192.168.10.0
**env.bastion.networking.ipv6_gateway** | IPv6 of he bastion's gateway server. | fd00::1
**env.bastion.networking.ipv6_prefix** | IPv6 prefix. | 64
**env.bastion.networking.nameserver1** | IPv4 address of the server that resolves the bastion's hostname. | 192.168.10.200
**env.bastion.networking.nameserver2** | <b>(Optional)</b> A second IPv4 address that resolves the bastion's hostname. | 192.168.10.201
**env.bastion.networking.forwarder** | What IPv4 address will be used to make external DNS calls for the bastion? Can use 1.1.1.1 or 8.8.8.8 as defaults. | 8.8.8.8
**env.bastion.networking.interface** | Name of the networking interface on the bastion from Linux's perspective. Most likely enc1. | enc1
**env.bastion.access.user** | What would you like the admin's username to be on the bastion? If root, make pass and root_pass vars the same. | admin
**env.bastion.access.pass** | The password to the bastion's admin user. If using root, make pass and root_pass vars the same. | cH4ngeM3!
**env.bastion.access.root_pass** | The root password for the bastion. If using root, make pass and root_pass vars the same. | R0OtPa$s!
**env.bastion.options.dns** | Would you like the bastion to host the DNS information for the cluster? True or False. If false, resolution must come from elsewhere in your environment. Make sure to add IP addresses for KVM hosts, bastion, bootstrap, control, compute nodes, AND api, api-int and *.apps as described [here](https://docs.openshift.com/container-platform/4.8/installing/installing_bare_metal/installing-bare-metal-network-customizations.html) in section "User-provisioned DNS Requirements" Table 5. If True this will be done for you in the dns and check_dns roles. | True
**env.bastion.options.loadbalancer.on_bastion** | Would you like the bastion to host the load balancer (HAProxy) for the cluster? True or False (boolean). If false, this service must be provided elsewhere in your environment, and public and private IP of the load balancer must be provided in the following two variables. | True
**env.bastion.options.loadbalancer.public_ip** | (Only required if env.bastion.options.loadbalancer.on_bastion is True). The public IPv4 address for your environment's loadbalancer. api, apps, *.apps must use this. | 192.168.10.50
**env.bastion.options.loadbalancer.private_ip** | (Only required if env.bastion.options.loadbalancer.on_bastion is True). The private IPv4 address for your environment's loadbalancer. api-int must use this. | 10.24.17.12

## 6 - Cluster Networking
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**env.cluster.networking.metadata_name** | Name to describe the cluster as a whole, can be anything if DNS will be hosted on the bastion. If DNS is not on the bastion, must match your DNS configuration. Will be combined with the base_domain and hostnames to create Fully Qualified Domain Names (FQDN). | ocpz
**env.cluster.networking.base_domain** | The site name, where is the cluster being hosted? This will be combined with the metadata_name and hostnames to create FQDNs.  | host.com
**env.bastion.networking.ipv6_gateway** | IPv6 of he bastion's gateway server. | fd00::1
**env.bastion.networking.ipv6_prefix** | IPv6 prefix. | 64
**env.cluster.networking.nameserver1** | IPv4 address that the cluster get its hostname resolution from. If env.bastion.options.dns is True, this should be the IP address of the bastion. | 192.168.10.200
**env.cluster.networking.nameserver2** | <b>(Optional)</b> A second IPv4 address will the cluster get its hostname resolution from? If env.bastion.options.dns is True, this should be left commented out. | 192.168.10.201
**env.cluster.networking.forwarder** | What IPv4 address will be used to make external DNS calls for the cluster? Can use 1.1.1.1 or 8.8.8.8 as defaults. | 8.8.8.8
**env.cluster.networking.interface** | Name of the networking interface on the bastion from Linux's perspective. Most likely enc1. | enc1

## 7 - Bootstrap Node
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**env.cluster.nodes.bootstrap.disk_size** | How much disk space do you want to allocate to the bootstrap node (in Gigabytes)? Bootstrap node is temporary and will be brought down automatically when its job completes. 120 or more recommended. | 120
**env.cluster.nodes.bootstrap.ram** | How much memory would you like to allocate to the temporary bootstrap node (in megabytes)? Recommended 16384 or more. | 16384
**env.cluster.nodes.bootstrap.vcpu** | How many virtual CPUs would you like to allocate to the temporary bootstrap node? Recommended 4 or more. | 4
**env.cluster.nodes.bootstrap.vcpu_model_option** | Configure the CPU model and CPU features exposed to the guest | --cpu host
**env.cluster.nodes.bootstrap.vm_name** | Name of the temporary bootstrap node VM. Arbitrary value. | bootstrap
**env.cluster.nodes.bootstrap.ip** | IPv4 address of the temporary bootstrap node. | 192.168.10.4
**env.cluster.nodes.bootstrap.ipv6** | IPv6 address for the bootstrap if use_ipv6 variable is 'True'. | fd00::4
**env.cluster.nodes.bootstrap.mac** | MAC address for the bootstrap node if use_dhcp variable is 'True'. | 52:54:00:18:1A:2B
**env.cluster.nodes.bootstrap.hostname** | Hostname of the temporary boostrap node. If DNS is hosted on the bastion, this can be anything. If DNS is hosted elsewhere, this must match DNS definition. This will be combined with the metadata_name and base_domain to create a Fully Qualififed Domain Name (FQDN). | bootstrap-ocpz

## 8 - Control Nodes
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**env.cluster.nodes.control.disk_size** | How much disk space do you want to allocate to each control node (in Gigabytes)? 120 or more recommended. | 120
**env.cluster.nodes.control.ram** | How much memory would you like to allocate to the each control node (in megabytes)? Recommended 16384 or more. | 16384
**env.cluster.nodes.control.vcpu** | How many virtual CPUs would you like to allocate to each control node? Recommended 4 or more. | 4
**env.cluster.nodes.control.vcpu_model_option** | Configure the CPU model and CPU features exposed to the guest | --cpu host
**env.cluster.nodes.control.vm_name** | Name of the control node VMs. Arbitrary values. Usually no more or less than 3 are used. Must match the total number of IP addresses and hostnames for control nodes. Use provided list format. | control-1control-2control-3
**env.cluster.nodes.control.ip** | IPv4 address of the control nodes. Use provided list formatting. | 192.168.10.5192.168.10.6192.168.10.7
**env.cluster.nodes.control.ipv6** | IPv6 address for the control nodes. Use iprovided list formatting (if use_ipv6 variable is 'True'). | fd00::5fd00::6fd00::7
**env.cluster.nodes.control.mac** | MAC address for the control node if use_dhcp variable is 'True'. | 52:54:00:18:1A:2B
**env.cluster.nodes.control.hostname** | Hostnames for control nodes. Must match the total number of IP addresses for control nodes (usually 3). If DNS is hosted on the bastion, this can be anything. If DNS is hosted elsewhere, this must match DNS definition. This will be combined with the metadata_name and base_domain to create a Fully Qualififed Domain Name (FQDN). | control-01control-02control-03

## 9 - Compute Nodes
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**env.cluster.nodes.compute.disk_size** | How much disk space do you want to allocate to each compute node (in Gigabytes)? 120 or more recommended. | 120
**env.cluster.nodes.compute.ram** | How much memory would you like to allocate to the each compute node (in megabytes)? Recommended 16384 or more. | 16384
**env.cluster.nodes.compute.vcpu** | How many virtual CPUs would you like to allocate to each compute node? Recommended 2 or more. | 2
**env.cluster.nodes.compute.vcpu_model_option** | Configure the CPU model and CPU features exposed to the guest | --cpu host
**env.cluster.nodes.compute.vm_name** | Name of the compute node VMs. Arbitrary values. This list can be expanded to any number of nodes, minimum 2. Must match the total number of IP addresses and hostnames for compute nodes. Use provided list format. | compute-1compute-2
**env.cluster.nodes.compute.ip** | IPv4 address of the compute nodes. Must match the total number of VM names and hostnames for compute nodes. Use provided list formatting. | 192.168.10.8192.168.10.9
**env.cluster.nodes.control.ipv6** | IPv6 address for the compute nodes. Use iprovided list formatting (if use_ipv6 variable is 'True'). | fd00::8fd00::9
**env.cluster.nodes.compute.mac** | MAC address for the compute node if use_dhcp variable is 'True'. | 52:54:00:18:1A:2B
**env.cluster.nodes.compute.hostname** | Hostnames for compute nodes. Must match the total number of IP addresses and VM names for compute nodes. If DNS is hosted on the bastion, this can be anything. If DNS is hosted elsewhere, this must match DNS definition. This will be combined with the metadata_name and base_domain to create a Fully Qualififed Domain Name (FQDN). | compute-01compute-02

## 10 - Infra Nodes
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**env.cluster.nodes.infra.disk_size** | <b>(Optional)</b> Set up compute nodes that are made for infrastructure workloads (ingress, monitoring, logging)? How much disk space do you want to allocate to each infra node (in Gigabytes)? 120 or more recommended. | 120
**env.cluster.nodes.infra.ram** | <b>(Optional)</b> How much memory would you like to allocate to the each infra node (in megabytes)? Recommended 16384 or more. | 16384
**env.cluster.nodes.infra.vcpu** | <b>(Optional)</b> How many virtual CPUs would you like to allocate to each infra node? Recommended 2 or more. | 2
**env.cluster.nodes.infra.vcpu_model_option** | <b>(Optional)</b> Configure the CPU model and CPU features exposed to the guest | --cpu host
**env.cluster.nodes.infra.vm_name** | <b>(Optional)</b> Name of additional infra node VMs. Arbitrary values. This list can be expanded to any number of nodes, minimum 2. Must match the total number of IP addresses and hostnames for infra nodes. Use provided list format. | infra-1infra-2
**env.cluster.nodes.infra.ip** | <b>(Optional)</b> IPv4 address of the infra nodes. This list can be expanded to any number of nodes, minimum 2. Use provided list formatting. | 192.168.10.10192.168.10.11
**env.cluster.nodes.infra.ipv6** | <b>(Optional)</b> IPv6 address of the infra nodes. iThis list can be expanded to any number of nodes, minimum 2. Use provided list formatting (if use_ipv6 variable is 'True'). | fd00::10fd00::11
**env.cluster.nodes.infra.hostname** | <b>(Optional)</b> Hostnames for infra nodes. Must match the total number of IP addresses for infra nodes. If DNS is hosted on the bastion, this can be anything. If DNS is hosted elsewhere, this must match DNS definition. This will be combined with the metadata_name and base_domain to create a Fully Qualififed Domain Name (FQDN). | infra-01infra-02

## 11 - (Optional) Misc
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**env.language** | What language would you like Red Hat Enterprise Linux to use? In UTF-8 language code. Available languages and their corresponding codes can be found [here](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/5/html-single/international_language_support_guide/index), in the "Locale" column of Table 2.1. | en_US.UTF-8
**env.timezone** | Which timezone would you like Red Hat Enterprise Linux to use? A list of available timezone options can be found [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). | America/New_York
**env.keyboard** | Which keyboard layout would you like Red Hat Enterprise Linux to use?  | us
**env.ansible_key_name** | (Optional) Name of the SSH key that Ansible will use to connect to hosts. | ansible-ocpz
**env.ocp_key_name** | Comment to describe the SSH key used for OCP. Arbitrary value. | OCPZ-01 key
**env.vnet_name** | (Optional) Name of the bridged virtual network that will be created on the KVM host if network mode is not set to NAT. In case of NAT network mode the name of the NAT network definition used to create the nodes(usually it is 'default'). If NAT is being used and a jumphost is needed, the parameters network_mode, jumphost.name, jumphost.user and jumphost.pass must be specified, too. For default (NAT) network verify that the configured IP ranges does not interfere with the IPs defined for the controle and compute nodes. Modify the default network (dhcp range setting) to prevent issues with VMs using dhcp and OCP nodes having fixed IPs. Default is create a bridge network.| macvtap-net
**env.network_mode** | (Optional) In case the network mode will be NAT and the installation will be executed from remote (e.g. your laptop), a jumphost needs to be defined to let the installation access the bastion host. If macvtap for networking is being used this variable should be empty. | NAT
**env.use_ipv6** | If ipv6 addresses should be assigned to the controle and compute nodes, this variable should be true (default) and the matching ipv6 settings should be specified. | True
**env.use_dhcp** | If dhcp service should be used to get an IP address, this variable should be true and the matching mac address must be specified. | False
**env.jumphost.name** | (Optional) If env.network.mode is set to 'NAT' the name of the jumphost (e.g. the name of KVM host if used as jumphost) should be specified. | kvm-host-01
**env.jumphost.ip** | (Optional) The ip of the jumphost. | 192.168.10.1
**env.jumphost.user** | (Optional) The user name to login to the jumphost. | admin
**env.jumphost.pass** | (Optional) The password for user to login to the jumphost. | ch4ngeMe!
**env.jumphost.path_to_keypair** | (Optional) The absolute path to the public key file on the jumphost to be copied to the bastion. | /home/admin/.ssh/id_rsa.pub

## 12 - OCP and RHCOS (CoreOS)

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**ocp_download_url** | Link to the mirror for the OpenShift client and installer from Red Hat. | https://mirror.openshift.com/pub/openshift-v4/multi/clients/ocp/4.13.1/s390x/
**ocp_client_tgz** | OpenShift client filename (tar.gz). | openshift-client-linux.tar.gz
**ocp_install_tgz** | OpenShift installer filename (tar.gz). | openshift-install-linux.tar.gz
**rhcos_download_url** | Link to the CoreOS files to be used for the bootstrap, control and compute nodes. Feel free to change to a different version. | https://mirror.openshift.com/pub/openshift-v4/s390x/dependencies/rhcos/4.12/4.12.3/
**rhcos_os_variant** | CoreOS base OS. Use the OS string as defined in 'osinfo-query os -f short-id' | rhel8.6
**rhcos_live_kernel** | CoreOS kernel filename to be used for the bootstrap, control and compute nodes. | rhcos-4.12.3-s390x-live-kernel-s390x
**rhcos_live_initrd** | CoreOS initramfs to be used for the bootstrap, control and compute nodes. | rhcos-4.12.3-s390x-live-initramfs.s390x.img
**rhcos_live_rootfs** | CoreOS rootfs to be used for the bootstrap, control and compute nodes. | rhcos-4.12.3-s390x-live-rootfs.s390x.img

## 13 - (Optional) Create compute node in a day-2 operation

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**day2_compute_node.vm_name** | Name of the compute node VM.  | compute-4
**day2_compute_node.vm_hostname** | Hostnames for compute node. | compute-4
**day2_compute_node.vm_vm_ip** | IPv4 address of the compute node. | 192.168.10.99
**day2_compute_node.vm_vm_ipv6** | IPv6 address of the compute node. | fd00::99
**day2_compute_node.vm_mac** | MAC address of the compute node if use_dhcp variable is 'True'. | 52:54:00:18:1A:2B
**day2_compute_node.vm_interface** | The network interface used for given IP addresses of the compute node. | enc1
**day2_compute_node.hostname** | The hostname of the KVM host | kvm-host-01
**day2_compute_node.host_user** | KVM host user which is used to create the VM | root
**day2_compute_node.host_arch** | KVM host architecture.  | s390x

## 14 - (Optional) Agent Based Installer
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**abi.flag** | This is the flag, Will be used to identify during execution. Few checks in the playbook will be depend on this (default value will be False)  | True
**abi.ansible_workdir** | This will be work directory name, it will keep required data that need to be present during or after execution | ansible_workdir
**abi.ocp_installer_version** | Version will contain value of openshift-installer binary version user desired to be used | '4.15.0-rc.8'
**abi.ocp_installer_url** | This is the base url of openshift installer binary it will remain same as static value, User Do not need to give value until user wants to change the mirror | 'https://mirror.openshift.com/pub/openshift-v4/s390x/clients/ocp/'

## OpenShift Settings
* The parameters bellow have a hierachical structure and need to be added to all.yaml in given format. For example if you want to change the hyperthreading (disable) than you need to specify the following value in all.yaml file:
  install_config:
    compute:
      hyperthreading: Disabled

**Variable Name** | **Description** | **Example/Default**
:--- | :--- | :---
**install_config.api_version** | Kubernetes API version for the cluster. These install_config variables will be passed to the OCP install_config file. This file is templated in the get_ocp role during the setup_bastion playbook. To make more fine-tuned adjustments to the install_config, you can find it at roles/get_ocp/templates/install-config.yaml.j2 | v1
**install_config.compute.architecture** | Computing architecture for the compute nodes. Must be s390x for clusters on IBM zSystems. | s390x
**install_config.compute.hyperthreading** | Enable or disable hyperthreading on compute nodes. Recommended enabled. | Enabled
**install_config.control.architecture** | Computing architecture for the control nodes. Must be s390x for clusters on IBM zSystems, amd64 for Intel or AMD systems, and arm64 for ARM servers. | s390x
**install_config.control.hyperthreading** | Enable or disable hyperthreading on control nodes. Recommended enabled. | Enabled
**install_config.cluster_network.cidr** | IPv4 block in Internal cluster networking in Classless Inter-Domain Routing (CIDR) notation. Recommended to keep as is. | 10.128.0.0/14
**install_config.cluster_network.host_prefix** | The subnet prefix length to assign to each individual node. For example, if hostPrefix is set to 23 then each node is assigned a /23 subnet out of the given cidr. A hostPrefix value of 23 provides 510 (2^(32 - 23) - 2) pod IP addresses. | 23
**install_config.cluster_network.type** | The cluster network provider Container Network Interface (CNI) plug-in to install. Either OpenShiftSDN or OVNKubernetes (default). | OVNKubernetes
**install_config.service_network** | The IP address block for services. The default value is 172.30.0.0/16. The OpenShift SDN and OVN-Kubernetes network providers support only a single IP address block for the service network. An array with an IP address block in CIDR format. | 172.30.0.0/16
**install_config.machine_network** | The IP address block for Nodes IP Pool. The default value is 192.168.122.0/24 For NAT Network Mode. In case of MacvTap it will be depend on Inteface IP assignment. An array with an IP address block in CIDR format. | 192.168.122.0/24
**install_config.fips** | True or False (boolean) for whether or not to use the United States' Federal Information Processing Standards (FIPS). Not yet certified on IBM zSystems. Enclosed in 'single quotes'. | 'false'

## Packages (Optional)
* Packages are installed based on the executed playbooks based on the given requirements. This means that these variables have default values which can be overwritten in all.yaml file.
* The following table describe the current installed packages and their default values.
* In general is to say that the default values are all required. Feel free to add more if needed but it is required to specify the whole list (include default values).
* Within the all.yaml.template file you find an example of the parameter including the format. 

**Variable Name** | **Description** | **Default values**
:--- | :--- | :---
**pkgs_galaxy** | A list of Ansible Galaxy collections that will be installed during the setup playbook. The collections listed are required. | [ ibm.ibm_zhmc, community.general, community.crypto, ansible.posix, community.libvirt ]
**pkgs_controller** | A list of packages that will be installed on the machine running Ansible during the setup playbook. | [ openssh, expect, sshuttle ]
**pkgs_kvm** | A list of packages that will be installed on the KVM Host during the setup_kvm_host playbook. | [ libguestfs, libvirt-client, libvirt-daemon-config-network, libvirt-daemon-kvm, cockpit-machines, libvirt-devel, virt-top, qemu-kvm, python3-lxml, cockpit, lvm2 ]
**pkgs_bastion** | A list of packages that will be installed on the bastion during the setup_bastion playbook. Feel free to add more as needed, just make sure to follow the same list format. | [ haproxy, httpd, bind, bind-utils, expect, firewalld, mod_ssl, python3-policycoreutils, rsync ]
**pkgs_zvm** | A list of packages that will be installed in case of HCP (zVM nodes) or LPAR installation. | [ git, python3-pip, python3-devel, openssl-devel, rust, cargo, libffi-devel, wget, tar, jq, gcc, make, x3270, python39 ]

## Proxy (Optional)
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**use_proxy** | (Optional) Use proxyx . Default value is 'False'. Possible values are 'True' or 'False'. | False
**proxy_http** | (Optional) A proxy URL to use for creating HTTP connections outside the cluster. Will be used in the install-config and applied to other Ansible hosts unless set otherwise in no_proxy below. Must follow this pattern: http://username:pswd>@ip:port | http://ocp-admin:Pa$sw0rd@9.72.10.1:80
**proxy_https** | (Optional) A proxy URL to use for creating HTTPS connections outside the cluster. Will be used in the install-config and applied to other Ansible hosts unless set otherwise in no_proxy below. Must follow this pattern: https://username:pswd@ip:port | https://ocp-admin:Pa$sw0rd@9.72.10.1:80
**proxy_no** | (Optional) A comma-separated list (no spaces) of destination domain names, IP addresses, or other network CIDRs to exclude from proxying. When using a proxy, all necessary IPs and domains for your cluster will be added automatically. See roles/get_ocp/templates/install-config.yaml.j2 for more details on the template. Preface a domain with . to match subdomains only. For example, .y.com matches x.y.com, but not y.com. Use * to bypass the proxy for all listed destinations. | example.com,192.168.10.1

## Disconnected cluster setup (Optional)
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**disconnected.enabled** | True or False, to enable disconnected mode | False
**disconnected.registry.url** | String containing url of disconnected registry with or without port and without protocol | registry.tt.testing:5000
**disconnected.registry.pull_secret** | String containing pull secret of the disconnected registry to be applied on the *cluster*.  Make sure to enclose pull_secret in 'single quotes' and it has appropriate pull access. | '{"auths":{"registry.tt..testing:5000":{"auth":"b3Blb...4yQQ==","email":"test.user@example.com"}}}'
**disconnected.registry.mirror_pull_ecret** | String containing pull secret to use for mirroring. Contains Red Hat secret and registry pull  secret. Make sure to enclose pull_secret in 'single quotes' and must be able to push to mirror registry. | '{"auths":{"cloud.openshift.com":{"auth":"b3Blb...4yQQ==","email":"redhat.user@gmail.com", "registry.tt..testing:5000":...user@example.com"}}}'
**disconnected.registry.ca_trusted** | True or False to indicate that mirror registry CA is implicitly trusted or needs to be made trusted on mirror host and cluster. | False
**disconnected.registry.ca_cert** | Multiline string containing the mirror registry CA bundle | -----BEGIN CERTIFICATE-----MIIDqDCCApCgAwIBAgIULL+d1HTYsiP+8jeWnqBis3N4BskwDQYJKoZIhvcNAQEF...-----END CERTIFICATE-----
**disconnected.mirroring.host.name** | String containing the hostname of the host, which will be used for mirroring | mirror-host-1
**disconnected.mirroring.host.ip** | String containing ip of the host, which will be used for mirroring | 192.168.10.99
**disconnected.mirroring.host.user** | String containing the username of the host, which will be used for mirroring | mirroruser
**disconnected.mirroring.host.pass** | String containing the password of the host, which will be used for mirroring | mirrorpassword
**disconnected.mirroring.file_server.clients_dir** | Directory path relative to the HTTP/FTP accessible directory on **env.file_server** where client binary tarballs are kept | clients
**disconnected.mirroring.file_server.oc_mirror_tgz** | Name of oc-mirror tarball on **env.file_server** in **disconnected.mirroring.file_server.clients_dir** | oc-mirror.tar.gz
**disconnected.mirroring.legacy.platform** | True or False if the platform should be mirrored using `oc adm release mirror`. | False
**disconnected.mirroring.legacy.ocp_quay_release_image_tag** | The tag of the release image *quay.io/openshift-release-dev/ocp-release* to mirror and use | 4.13.1-s390x
**disconnected.mirroring.legacy.ocp_org** | The org part of the repo on the mirror registry where the release image will be pushed | ocp4
**disconnected.mirroring.legacy.ocp_repo** | The repo part of the repo on the mirror registry where the release image will be pushed | openshift4
**disconnected.mirroring.legacy.ocp_tag** | The tag part of the repo on the mirror registry where the release image will be pushed. Full image would be as below.: disconnected.registry.url/disconnected.mirroring.legacy.ocp_org/disconnected...ocp_repo:disconnected..ocp_tag | v4.13.1
**disconnected.mirroring.oc_mirror.release_image_tag** | The ocp release image tag you want to install the cluster with. Used when legacy platform  mirroring is disabled and **disconnected.mirroring.oc_mirror.image_set** contains platform  entries. |  4.13.1-multi
**disconnected.mirroring.oc_mirror.oc_mirror_args.continue_on_error** | True or False to give `--continue-on-error` flag to `oc-mirror` | False
**disconnected.mirroring.oc_mirror.oc_mirror_args.source_skip_tls** | True or False to give `--source-skip-tls` flag to `oc-mirror` | False
**disconnected.mirroring.oc_mirror.post_mirror.mapping.replace.enabled** | True or False to replace values in `mapping.txt` generated by oc-mirror.  This also does a manual repush of the images in `mapping.txt`. | False
**disconnected.mirroring.oc_mirror.post_mirror.mapping.replace.list** | List of **regexp** and **replace** where every string/regular expression  gets replaced by corresponding *replace* value. | regexp: interal-url.com replace: external-url.com
**disconnected.mirroring.oc_mirror.image_set** | YAML fields containing a standard `oc-mirror` [image set](https://docs.openshift.com/container-platform/latest/installing/disconnected_install/installing-mirroring-disconnected.html#oc-mirror-creating-image-set-config_installing-mirroring-disconnected) with some minor changes to schema.  Differences are documented as needed. Used to generate final image set. | see template
**disconnected.mirroring.oc_mirror.image_set.storageConfig.registry.enabled** | True or False to use registry storage backend for pushing mirrored content directly to the registry.  Currently only this backend is supported.| True
**disconnected.mirroring.oc_mirror.image_set.storageConfig.registry.imageURL.org** | The org part of registry imageURL from standard image set. | mirror
**disconnected.mirroring.oc_mirror.image_set.storageConfig.registry.imageURL.repo** | The repo part of registry imageURL from standard image set.  Final imageURL will be as below:  disconnected.registry.url/disconnected.mirroring.oc_mirror.image_set.storageConfig .registry.imageURL.org/disconnected...imageURL.repo | oc-mirror-metadata
**disconnected.mirroring.oc_mirror.image_set.storageConfig.registry.skipTLS** | True of False same purpose served as in standard image set i.e. skip the tls for the registry   during mirroring.| false
**disconnected.mirrroing.oc_mirror.image_set.mirror** | YAML containing a list of what needs to be mirrored. See the oc mirror image set documentation. | see oc-mirror [image set](https://docs.openshift.com/container-platform/latest/installing/disconnected_install/installing-mirroring-disconnected.html#oc-mirror-creating-image-set-config_installing-mirroring-disconnected)   documentation

## Hosted Control Plane ( Optional )
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**hcp.compute_node_type** | Select the compute node type for HCP , either zKVM or zVM | zvm
**hcp.mgmt_cluster_nameserver** | IP Address of Nameserver of Management Cluster | 192.168.10.1
**hcp.oc_url** | URL for OC Client that you want to install on the host | https://... ..openshift-client-linux-4.13.0-ec.4.tar.gz
**hcp.ansible_key_name** | ssh key name | ansible-ocpz
**hcp.pkgs** | list of packages for different hosts | 
**hcp.mce.version** | version for multicluster-engine Operator | 2.4
**hcp.mce.instance_name** | name of the MultiClusterEngine instance | engine
**hcp.mce.delete** | true or false - deletes mce and related resources while running deletion playbook | true
**hcp.asc.url_for_ocp_release_file** | Add URL for OCP release.txt File | https://...  ..../release.txt
**hcp.asc.db_volume_size** | DatabaseStorage Volume Size | 10Gi
**hcp.asc.fs_volume_size** | FileSystem Storage Volume Size | 10Gi
**hcp.asc.ocp_version** | OCP Version for AgentServiceConfig | 4.13.0-ec.4
**hcp.asc.iso_url** | Give URL for ISO image | https://...  ...s390x-live.s390x.iso
**hcp.asc.root_fs_url** | Give URL for rootfs image | https://...  ... live-rootfs.s390x.img
**hcp.asc.mce_namespace** | Namespace where your Multicluster Engine Operator is installed.  Recommended Namespace for MCE is 'multicluster-engine'.  Change this only if MCE is installed in other namespace. | multicluster-engine
**hcp.control_plane.high_availabiliy** | Availability for Control Plane | true
**hcp.control_plane.clusters_namespace** | Namespace for Creating Hosted Control Plane | clusters
**hcp.control_plane.hosted_cluster_name** | Name for the Hosted Cluster  | hosted0
**hcp.control_plane.basedomain** | Base domain for Hosted Cluster | example.com
**hcp.control_plane.pull_secret_file** | Path for the pull secret  No need to change this as we are copying the pullsecret to same file  /root/ansible_workdir/auth_file | /root/ansible_workdir/auth_file
**hcp.control_plane.ocp_release_image** | OCP Release version for Hosted Control Cluster and Nodepool | 4.13.0-rc.4-multi
**hcp.control_plane.arch** | Architecture for InfraEnv and AgentServiceConfig" | s390x
**hcp.control_plane.additional_flags** | Any additional flags for creating hcp ( In hcp create cluster agent command ) | --fips
**hcp.control_plane.pull_secret** | Pull Secret of Management Cluster  Make sure to enclose pull_secret in 'single quotes' | '{"auths":{"cloud.openshift.com":{"auth":"b3Blb...4yQQ==","email":"redhat.user@gmail.com"}}}'
**hcp.bastion_params.create** | true or false - create bastion with the provided IP | true
**hcp.bastion_params.ip** | IPv4 address for bastion of Hosted Cluster | 192.168.10.1
**hcp.bastion_params.user** | User for bastion of Hosted Cluster | root
**hcp.bastion_params.host** | IPv4 address of KVM host  (kvm host where you want to run all oc commands and create VMs)| 192.168.10.1
**hcp.bastion_params.host_user** | User for KVM host | root
**hcp.bastion_params.hostname** | Hostname for bastion | bastion
**hcp.bastion_params.base_domain** | DNS base domain for the bastion. | ihost.com
**hcp.bastion_params.nameserver** | Nameserver for creating bastion | 192.168.10.1
**hhcp.bastion_params.gateway** | Gateway IP for creating bastion  This is how it well be used ip=<ipv4 address>::<nameserver>:<subnet mask> | 192.168.10.1
**hcp.bastion_params.subnet_mask** |  IPv4 address of subnetmask | 255.255.255.0
**hcp.bastion_params.interface** | Interface for bastion | enc1
**hcp.bastion_params.file_server.ip** | IPv4 address for the file server that will be used to pass config files and iso to KVM host LPAR(s) and bastion VM during their first boot. | 192.168.10.201
**hcp.bastion_params.file_server.protocol** | Protocol used to serve the files, either 'ftp' or 'http' | http
**hcp.bastion_params.file_server.iso_mount_dir** | Directory path relative to the HTTP/FTP accessible directory where RHEL ISO is mounted. For example, if the FTP root is at /home/user1 and the ISO is mounted at /home/user1/RHEL/8.7 then this variable would be RHEL/8.7 - no slash before or after. | RHEL/8.7
**hcp.bastion_params.os_variant** | rhel os variant for creating bastion | 8.7
**hcp.bastion_params.disk** | rhel os variant for creating bastion | 8.7
**hcp.bastion_params.network_name** | rhel os variant for creating bastion | 8.7
**hcp.bastion_params.networking_device** | The network interface card from Linux's perspective.  Usually enc and then a number that comes from the dev_num of the network adapter. | enc1100
**hcp.bastion_params.language** | What language would you like Red Hat Enterprise Linux to use? In UTF-8 language code. Available languages and their corresponding codes can be found here, in the "Locale" column of Table 2.1. | en_US.UTF-8
**hcp.bastion_params.timezone** | Which timezone would you like Red Hat Enterprise Linux to use? A list of available timezone options can be found here. | America/New_York
**hcp.bastion_params.keyboard** | Which keyboard layout would you like Red Hat Enterprise Linux to use? | us
**hcp.data_plane.compute_count** | Number of agents for the hosted cluster  The same number of compute nodes will be attached to Hosted Cotrol Plane | 2
**hcp.data_plane.vcpus** | vCPUs for compute nodes | 4
**hcp.data_plane.memory** | RAM for compute nodes | 16384
**hcp.data_plane.nameserver** | Nameserver for compute nodes | 192.168.10.1
**hcp.data_plane.storage.type** | Storage type for KVM guests  qcow/dasd | qcow
**hcp.data_plane.storage.qcow.disk_size** | Disk size for kvm guests | 100G
**hcp.data_plane.storage.qcow.pool_path** | Storage pool path for creating disks | /home/images/
**hcp.data_plane.storage.dasd** | dasd disks for kvm guests | /disk
**hcp.data_plane.kvm.ip_params.static_ip.enabled** | true or false - use static IPs for agents using NMState | true
**hcp.data_plane.kvm.ip_params.static_ip.ip** | List of IP addresses for agents | 192.168.10.1
**hcp.data_plane.kvm.ip_params.static_ip.interface** | Interface for agents for configuring NMStateConfig | eth0
**hcp.data_plane.kvm.ip_params.mac** | List of macaddresses for the agents.  Configure in DHCP if you are using dynamic IPs for Agents. | - 52:54:00:ba:d3:f7 
**hcp.data_plane.zvm.network_mode** | Network mode for zvm nodes  Supported modes: vswitch,osa, RoCE  |  vswitch
**hcp.data_plane.zvm.disk_type** | Disk type for zvm nodes  Supported disk types: fcp, dasd | dasd
**hcp.data_plane.zvm.subnetmask** | Subnet mask for compute nodes | 255.255.255.0
**hcp.data_plane.zvm.gateway** | Gateway for compute nodes | 192.168.10.1
**hcp.data_plane.zvm.nodes** | Set of parameters for zvm nodes  Give the details of each zvm node here | 
**hcp.data_plane.zvm.name** | Name of the zVM guest | m1317002
**hcp.data_plane.zvm.nodes.host** | Host name of the zVM guests  which we use to login 3270 console | boem1317
**hcp.data_plane.zvmnodes.user** | Username for zVM guests to login | m1317002
**hcp.data_plane.zvm.nodes.password** | password for the zVM guests to login | password
**hcp.data_plane.zvm.nodes.interface.ifname** | Network interface name for zVM guests | encbdf0
**hcp.data_plane.zvm.nodes.interface.nettype** | Network type for zVM guests for network connectivity | qeth
**hcp.data_plane.zvm.nodes.interface.subchannels** | subchannels for zVM guests interfaces | 0.0.bdf0,0.0.bdf1,0.0.bdf2
**hcp.data_plane.zvm.nodes.interface.options** | Configurations options  | layer2=1
**hcp.data_plane.zvm.interface.ip** | IP addresses for to be used for zVM nodes | 192.168.10.1
**hcp.data_plane.zvm.nodes.dasd.disk_id** | Disk id for dasd disk to be used for zVM node | 4404 
**hcp.data_plane.zvm.nodes.lun** | Disk details of fcp disk to be used for zVM node | 4404
