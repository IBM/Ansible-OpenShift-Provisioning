# Step 3: Set Variables
* In a text editor of your choice, open the [environment variables file](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/inventories/default/group_vars/all.yaml).
* This is the master variables file and you will likely reference it many times throughout the process. The default inventory can be found at [inventories/default/group_vars/all.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/inventories/default/group_vars/all.yaml).
* Fill out the variables marked with `X` to match your specific installation. 
* This is the most important step in the process. Take the time to make sure everything here is correct.
* <u>Note on YAML syntax</u>: Only the lowest value in each hierarchicy needs to be filled in. For example, at the top of the variables file env and z don't need to be filled in, but the cpc_name does. There are X's where input is required to help you with this.
* Scroll table to the right to see examples for each variable.

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**<u>Section 1 - IBM zSystems</u>** 
**env.z.cpc_name** | The name of the IBM zSystems / LinuxONE mainframe that you are creating a Red Hat OpenShift Container<br /> Platform cluster on. Can be found under the "Systems Management" tab of the Hardware Management<br /> Console (HMC). | SYS1
**env.z.hmc.host** | The IPv4 address of the HMC you will be connecting to in order to create a Logical Partition (LPAR)<br /> on which will act as the Kernel-based Virtual Machine (KVM) host aftering installing and setting up<br /> Red Hat Enterprise Linux (RHEL). | 192.168.10.1
**env.z.hmc.user** | The username that the HMC API call will use to connect to the HMC. Must have access to create<br /> LPARs, attach storage groups and networking cards. | hmc-user
**env.z.hmc.pass** | The password that the HMC API call will use to connect to the HMC. Must have access to create<br /> LPARs, attach storage groups and networking cards. | hmcPas$w0rd!
**env.z.lpar.name** | The name of the Logical Partition (LPAR) that you would like to create/target for the creation of<br /> your cluster. This LPAR will act as the KVM host, with RHEL installed natively. | OCPKVM1
**env.z.lpar.description** | A short description of what this LPAR will be used for, will only be displayed in the HMC next to<br /> the LPAR name for identification purposes. | KVM host LPAR for RHOCP cluster.
**env.z.lpar.access.user** | The username that will be created in RHEL when it is installed on the LPAR (the KVM host). | kvm-admin
**env.z.lpar.access.pass** | The password for the user that will be created in RHEL when it is installed on the LPAR (the KVM host). | ch4ngeMe!
**env.z.lpar.root_pass** | The root password for RHEL installed on the LPAR (the KVM host). | $ecureP4ass!
**env.z.lpar.ifl.count** | Number of Integrated Facilities for Linux (IFL) processors will be assigned to this LPAR.<br /> 6 or more recommended. | 6
**env.z.lpar.ifl.initial memory** | Initial memory allocation for LPAR to have at start-up (in megabytes). | 55000
**env.z.lpar.ifl.max_memory** | The most amount of memory this LPAR can be using at any one time (in megabytes). | 99000
**env.z.lpar.ifl.initial_weight** | For LPAR load balancing purposes, the processing weight this LPAR will have at start-up (1-999). | 100
**env.z.lpar.ifl.min_weight** | For LPAR load balancing purposes, the minimum weight that this LPAR can have at any one time (1-999). | 50
**env.z.lpar.ifl.max_weight** | For LPAR load balancing purposes, the maximum weight that this LPAR can have at any one time (1-999). | 500
**env.z.lpar.networking.hostname** | The hostname of the LPAR with RHEL installed natively (the KVM host). | kvm-host-01
**env.z.lpar.networking.ip** | The IPv4 address of the LPAR with RHEL installed natively (the KVM host). | 192.168.10.2
**env.z.lpar.networking.subnetmask** | The subnet that the LPAR resides in within your network. | 255.255.255.0
**env.z.lpar.networking.subnet** | The same value as the above variable but in Classless Inter-Domain Routing (CIDR) notation. | 23
**env.z.lpar.networking.gateway** | The IPv4 address of the gateway to the network where the KVM host resides. | 192.168.10.0
**env.z.lpar.networking.nameserver1** | The IPv4 address from which the KVM host gets its hostname resolved. | 192.168.10.200
**env.z.lpar.networking.nameserver2** | (Optional) A second IPv4 address from which the KVM host can get its hostname resolved. Used for high availability. | 192.168.10.200
**env.z.lpar.networking.device1** | The network interface card from Linux's perspective. Usually enc and then a number that comes<br /> from the dev_num of the network adapter. | enc100
**env.z.lpar.networking.device2** | (Optional) Another Linux network interface card. Usually enc and then a number that comes<br /> from the dev_num of the second network adapter. | enc1
**env.z.lpar.networking.nic.card1.name** | The logical name of the Network Interface Card (NIC) within the HMC. An arbitrary value<br /> that is human-readable<br /> that points to the NIC. | SYS-NIC-01
**env.z.lpar.networking.nic.card1.adapter** | The physical adapter name reference to the logical adapter for the LPAR. | 10Gb-A
**env.z.lpar.networking.nic.card1.port** | The port number for the NIC. | 0
**env.z.lpar.networking.nic.card1.dev_num** | The logical device number for the NIC. In hex format. | 0x0100
**env.z.lpar.networking.nic.card2.name** | (Optional, uncomment and fill-in if you want to attach a second storage group) The logical name of a<br /> second Network Interface Card (NIC) within the HMC. An arbitrary value that is human-readable<br /> that points to the NIC. | SYS-NIC-02
**env.z.lpar.networking.nic.card2.adapter** | (Optional, uncomment and fill-in if you want to attach a second storage group) The physical adapter<br /> name of a second NIC. | 10Gb-B
**env.z.lpar.networking.nic.card2.port** | (Optional, uncomment and fill-in if you want to attach a second storage group) The port<br /> number for a second NIC. | 1
**env.z.lpar.networking.nic.card2.dev_num** | (Optional, uncomment and fill-in if you want to attach a second storage group) The logical device<br /> number for a second NIC. In hex format. | 0x0001
**env.z.lpar.storage_group.name** | The name of the storage group that will be attached to the LPAR. | OCP-storage-01
**env.z.lpar.storage_group.type** | Storage type. FCP is the only tested type as of now. | fcp
**env.z.lpar.storage_group.pool_path** | Set the absolute path to the storage pool within Linux. Recommended /var/lib/libvirt/images | /var/lib/libvirt/images
**env.z.lpar.storage_group.storage_wwpn** | World-wide port numbers for storage group. Use provided list formatting. | 500708680235c3f0<br />500708680235c3f1<br />500708680235c3f2<br />500708680235c3f3
**env.z.lpar.storage_group.dev_num** | The logical device number of the Host Bus Adapter (HBA) for the storage group. | C001
**env.z.lpar.storage_group.lun_name** | A list of Logical Unit Numbers (LUN) that point to specific virtual disk behind the WWPN. First in<br /> list will be used for boot. | mpatha<br />mpathb<br />mpathc<br />mpathd
**<u>Section 2 - FTP</u>**
**env.ftp.ip** | IP address for the FTP server that will be used to pass config files and iso to KVM host LPAR and bastion<br /> VM during their first boot. | 192.168.10.201
**env.ftp.user** | Username to connect to the FTP server. | ftp-user
**env.ftp.pass** | Password to connect to the FTP server as above user. | FTPpa$s!
**env.ftp.iso_mount_dir** | Directory path relative to FTP root where RHEL ISO is mounted. If FTP root is /var/ftp/pub<br /> and the ISO is mounted at /var/ftp/pub/RHEL/8.5 then this variable would be RHEL/8.5. No slash before or after. | RHEL/8.5
**env.ftp.iso_mount_dir** | Directory path relative to FTP root where configuration files can be stored. If FTP root is /var/ftp/pub<br /> and you would like to store the configs at /var/ftp/pub/ocpz-config then this variable would be<br /> ocpz-config. No slash before or after. | ocpz-config
**<u>Section 3 - RedHat</u>**
**env.redhat.username** | Red Hat username with a valid license or free trial to Red Hat OpenShift Container Platform (RHOCP),<br /> which comes with necessary licenses for Red Hat Enterprise Linux (RHEL) and Red Hat CoreOS (RHCOS). | redhat.user
**env.redhat.password** | Password to Red Hat above user's account. Used to auto-attach necessary subscriptions to KVM Host,<br /> bastion VM, and pull live images for OpenShift. | rEdHatPa$s!
**env.redhat.pull_secret** | Pull secret for OpenShift, comes from Red Hat's [Hybrid Cloud Console](https://console.redhat.com/openshift/install/ibmz/user-provisioned). Make sure to enclose in 'single quotes'.<br />  | '{"auths":{"cloud.openshift<br />.com":{"auth":"b3Blb<br />...<br />4yQQ==","email":"redhat.<br />user@gmail.com"}}}' 
**<u>Section 4 - Bastion</u>**
**env.bastion.create** | Would you like to create a bastion KVM guest to host essential infrastructure services like DNS,<br /> load balancer, firewall, etc? Highly recommended. Can de-select certain services with the env.bastion.options<br /> variables below. True or False (boolean). | True
**env.bastion.name** | Name of the bastion KVM guest. Arbitrary value, not the hostname. | bastion
**env.bastion.resources.disk_size** | How much of the storage pool would you like to allocate to the bastion (in<br /> Gigabytes)? Recommended 30 or more. | 30
**env.bastion.resources.ram** | How much memory would you like to allocate the bastion (in<br /> megabytes)? Recommended 4096 or more | 4096
**env.bastion.resources.swap** | How much swap storage would you like to allocate the bastion (in<br /> megabytes)? Recommended 4096 or more. | 4096
**env.bastion.resources.vcpu** | How many virtual CPUs would you like to allocate to the bastion? Recommended 4 or more. | 4
**env.bastion.resources.os_variant** | Version of Red Hat Enterprise Linux to use for the bastion's operating system.<br /> Recommended 8.4 and above. Must match version of mounted ISO on the FTP server. | 8.5
**env.bastion.networking.ip** | IPv4 address for the bastion. | 192.168.10.3
**env.bastion.networking.hostname** | Hostname of the bastion. Will be combined with<br /> env.bastion.networking.base_domain to create a Fully Qualified Domain Name (FQDN). | ocpz-bastion
**env.bastion.networking.subnetmask** | Subnet of the bastion. | 255.255.255.0
**env.bastion.networking.gateway** | What will be the IPv4 address of the bastion's gateway server? | 192.168.10.0
**env.bastion.networking.nameserver1** | IPv4 address of the server that resolves the bastion's hostname. | 192.168.10.200
**env.bastion.networking.nameserver2** | (Optional) A second IPv4 address that resolves the bastion's hostname. | 192.168.10.201
**env.bastion.networking.interface** | Name of the networking interface on the bastion from Linux's perspective. Most likely enc1. | enc1
**env.bastion.networking.base_domain** | Base domain that, when combined with the hostname, creates a fully-qualified<br /> domain name (FQDN) for the bastion? | ihost.com
**env.bastion.access.user** | What would you like the admin's username to be on the bastion? | admin
**env.bastion.access.pass** | The password to the bastion's admin user. | cH4ngeM3!
**env.bastion.access.root_pass** | The root password for the bastion. | R0OtPa$s!
**env.bastion.access.ocp_ssh_key_comment** | Comment to describe the SSH key used for OCP. Arbitrary value. | OCPZ-01 key
**env.bastion.options.dns** | Would you like the bastion to host the DNS information for the cluster? True or False (boolean).<br /> If false, resolution must come from elsewhere in your environment. Make sure to add IP addresses for<br /> KVM hosts, bastion, bootstrap, control, compute nodes, AND api, api-int and *.apps as described [here](https://docs.openshift.com/container-platform/4.8/installing/installing_bare_metal/installing-bare-metal-network-customizations.html)<br /> in section "User-provisioned DNS Requirements" Table 5. If True this will be done for<br /> you in the dns and check_dns roles. | True
**env.bastion.options.loadbalancer.on_bastion** | Would you like the bastion to host the load balancer (HAProxy) for the cluster?<br /> True or False (boolean).<br /> If false, this service must be provided elsewhere in your environment, and public and<br /> private IP of the load balancer must be<br /> provided in the following two variables. | True
**env.bastion.options.loadbalancer.public_ip** | (Only required if env.bastion.options.loadbalancer.on_bastion is True). The public IPv4<br /> address for your environment's loadbalancer. api, apps, *.apps must use this. | 192.168.10.50
**env.bastion.options.loadbalancer.private_ip** | (Only required if env.bastion.options.loadbalancer.on_bastion is True). The private IPv4 address<br /> for your environment's loadbalancer. api-int must use this. | 10.24.17.12
**<u>Section 5 - Cluster</u>**
**env.cluster.networking.metadata_name** | Name to describe the cluster as a whole, can be anything if DNS will be hosted on the bastion. If<br /> DNS is not on the bastion, must match your DNS configuration. Will be combined with the base_domain<br /> and hostnames to create Fully Qualified Domain Names (FQDN). | ocpz
**env.cluster.networking.base_domain** | The site name, where is the cluster being hosted? This will be combined with the metadata_name<br /> and hostnames to create FQDNs.  | ihost.com
**env.cluster.networking.nameserver1** | IPv4 address that the cluster get its hostname resolution from. If env.bastion.options.dns<br /> is True, this should be the IP address of the bastion. | 192.168.10.200
**env.cluster.networking.nameserver2** | (Optional) A second IPv4 address will the cluster get its hostname resolution from? If env.bastion.options.dns<br /> is True, this should be left commented out. | 192.168.10.201
**env.cluster.networking.forwarder** | What IPv4 address will be used to make external DNS calls? Can use 1.1.1.1 or 8.8.8.8 as defaults. | 8.8.8.8
**env.cluster.nodes.bootstrap.disk_size** | How much disk space do you want to allocate to the bootstrap node (in Gigabytes)? Bootstrap node<br /> is temporary and will be brought down automatically when its job completes. 120 or more recommended. | 120
**env.cluster.nodes.bootstrap.ram** | How much memory would you like to allocate to the temporary bootstrap node (in<br /> megabytes)? Recommended 16384 or more. | 16384
**env.cluster.nodes.bootstrap.vcpu** | How many virtual CPUs would you like to allocate to the temporary bootstrap node?<br /> Recommended 4 or more. | 4
**env.cluster.nodes.bootstrap.ip** | IPv4 address of the temporary bootstrap node. | 192.168.10.4
**env.cluster.nodes.bootstrap.hostname** | Hostname of the temporary boostrap node. If DNS is hosted on the bastion, this can be anything.<br /> If DNS is hosted elsewhere, this must match DNS definition. This will be combined with the<br /> metadata_name and base_domain to create a Fully Qualififed Domain Name (FQDN). | bootstrap
**env.cluster.nodes.control.disk_size** | How much disk space do you want to allocate to each control node (in Gigabytes)? 120 or more recommended. | 120
**env.cluster.nodes.control.ram** | How much memory would you like to allocate to the each control<br /> node (in megabytes)? Recommended 16384 or more. | 16384
**env.cluster.nodes.control.vcpu** | How many virtual CPUs would you like to allocate to each control node? Recommended 4 or more. | 4
**env.cluster.nodes.control.ip** | IPv4 address of the control nodes. Usually no more or less than 3 are used. Use provided<br /> list formatting. | 192.168.10.5<br />192.168.10.6<br />192.168.10.7
**env.cluster.nodes.control.hostname** | Hostnames for control nodes. Must match the total number of IP addresses for control nodes<br /> (usually 3). If DNS is hosted on the bastion, this can be anything. If DNS is hosted elsewhere,<br /> this must match DNS definition. This will be combined with the metadata_name and<br /> base_domain to create a Fully Qualififed Domain Name (FQDN). | control-01<br />control-02<br />control-03
**env.cluster.nodes.compute.disk_size** | How much disk space do you want to allocate to each compute<br /> node (in Gigabytes)? 120 or more recommended. | 120
**env.cluster.nodes.compute.ram** | How much memory would you like to allocate to the each compute<br /> node (in megabytes)? Recommended 16384 or more. | 16384
**env.cluster.nodes.compute.vcpu** | How many virtual CPUs would you like to allocate to each compute node? Recommended 2 or more. | 2
**env.cluster.nodes.compute.ip** | IPv4 address of the compute nodes. This list can be expanded to any number of nodes,<br /> minimum 2. Use provided list formatting. | 192.168.10.8<br />192.168.10.9
**env.cluster.nodes.compute.hostname** | Hostnames for compute nodes. Must match the total number of IP addresses for compute nodes.<br /> If DNS is hosted on the bastion, this can be anything. If DNS is hosted elsewhere, this must match<br /> DNS definition. This will be combined with the metadata_name and base_domain to create<br /> a Fully Qualififed Domain Name (FQDN). | compute-01<br />compute-02
**env.cluster.nodes.infra.disk_size** | (Optional) Set up compute nodes that are made for infrastructure workloads (ingress,<br /> monitoring, logging)? How much disk space do you want to allocate to each infra node (in Gigabytes)?<br /> 120 or more recommended. | 120
**env.cluster.nodes.infra.ram** | (Optional) How much memory would you like to allocate to the each infra node (in<br /> megabytes)? Recommended 16384 or more. | 16384
**env.cluster.nodes.infra.vcpu** | (Optional) How many virtual CPUs would you like to allocate to each infra node?<br /> Recommended 2 or more. | 2
**env.cluster.nodes.infra.ip** | (Optional) IPv4 address of the infra nodes. This list can be expanded to any number of nodes,<br /> minimum 2. Use provided list formatting. | 192.168.10.8<br />192.168.10.9
**env.cluster.nodes.infra.hostname** | (Optional) Hostnames for infra nodes. Must match the total number of IP addresses for infra nodes.<br /> If DNS is hosted on the bastion, this can be anything. If DNS is hosted elsewhere, this must match<br /> DNS definition. This will be combined with the metadata_name and base_domain<br /> to create a Fully Qualififed Domain Name (FQDN). | infra-01<br />infra-02
**<u>Section 6 - Misc Optional Settings</u>**
**env.language** | What language would you like Red Hat Enterprise Linux to use? In UTF-8 language code.<br /> Available languages and their corresponding codes can be found [here](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/5/html-single/international_language_support_guide/index), in the "Locale" column of Table 2.1. | en_US.UTF-8
**env.timezone** | Which timezone would you like Red Hat Enterprise Linux to use? A list of available timezone<br /> options can be found [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). | America/New_York
**env.ansible_key_name** | (Optional) Name of the SSH key that Ansible will use to connect to hosts. | ansible-ocpz
**env.bridge_name** | (Optional) Name of the macvtap bridge that will be created on the KVM host. | macvtap-net
**env.pkgs.galaxy** | A list of Ansible Galaxy collections that will be installed during the setup playbook. The<br /> collections listed are required. Feel free to add more as needed, just make sure to follow the same list format. | community.general
**env.pkgs.workstation** | A list of packages that will be installed on the workstation running Ansible during the setup<br /> playbook. Feel free to add more as needed, just make sure to follow the same list format. | openssh
**env.pkgs.kvm** | A list of packages that will be installed on the KVM Host during the setup_kvm_host playbook.<br /> Feel free to add more as needed, just make sure to follow the same list format. | qemu-kvm
**env.pkgs.bastion** | A list of packages that will be installed on the bastion during the setup_bastion playbook.<br /> Feel free to add more as needed, just make sure to follow the same list format. | haproxy
**env.openshift.client** | Link to the mirror for the OpenShift client from Red Hat. Feel free to change to a different version, but <br /> make sure it is for s390x architecture.<br /> Also make sure the client, installer and CoreOS versions (below) match. | https://mirror.openshift.com<br />/pub/openshift-v4/s390x/clients<br />/ocp/stable/openshift-<br />client-linux.tar.gz
**env.openshift.installer** | Link to the mirror for the OpenShift installer from Red Hat.<br /> Feel free to change to a different version, but make sure it is for s390x architecture.<br /> Also make sure the client, installer and CoreOS versions (below) match.  | https://mirror.openshift.com<br />/pub/openshift-v4/s390x<br />/clients/ocp/stable/openshift-<br />install-linux.tar.gz
**env.coreos.kernel** | Link to the mirror of the CoreOS kernel to be used for the bootstrap, control and compute nodes.<br /> Feel free to change to a different version, but make sure it is for s390x architecture.<br /> Also make sure the OCP client and installer (above) and other CoreOS components versions match. | https://mirror.openshift.com<br />/pub/openshift-v4/s390x<br />/dependencies/rhcos<br />/4.9/latest/rhcos-4.9.0-s390x-<br />live-kernel-s390x
**env.coreos.initramfs** | Link to the mirror of the CoreOS initramfs to be used for the bootstrap, control and compute nodes.<br /> Feel free to change to a different version, but make sure it is for s390x architecture.<br /> Also make sure the OCP client and installer (above) and other CoreOS components versions match. | https://mirror.openshift.com<br />/pub/openshift-v4<br />/s390x/dependencies/rhcos<br />/4.9/latest/rhcos-4.9.0-s390x-<br />live-initramfs.s390x.img
**env.coreos.rootfs** | Link to the mirror of the CoreOS rootfs to be used for the bootstrap, control and compute nodes.<br /> Feel free to change to a different version, but make sure it is for s390x architecture.<br /> Also make sure the OCP client and installer (above) and other CoreOS components versions match. | https://mirror.openshift.com<br />/pub/openshift-v4<br />/s390x/dependencies/rhcos<br />/4.9/latest/rhcos-4.9.0-<br />s390x-live-rootfs.s390x.img 
**env.install_config.api_version** | Kubernetes API version for the cluster. These install_config variables will be passed to the OCP<br /> install_config file. This file is templated in the get_ocp role during the setup_bastion playbook.<br /> To make more fine-tuned adjustments to the install_config, you can find it at<br /> roles/get_ocp/templates/install-config.yaml.j2 | v1
**env.install_config.compute.architecture** | Computing architecture for the compute nodes. Must be s390x for clusters on IBM zSystems. | s390x
**env.install_config.compute.hyperthreading** | Enable or disable hyperthreading on compute nodes. Recommended enabled. | Enabled
**env.install_config.control.architecture** | Computing architecture for the control nodes. Must be s390x for clusters on IBM zSystems. | s390x
**env.install_config.control.hyperthreading** | Enable or disable hyperthreading on control nodes. Recommended enabled. | Enabled
**env.install_config.cluster_network.cidr** | IPv4 block in Internal cluster networking in Classless Inter-Domain<br /> Routing (CIDR) notation. Recommended to keep as is. | 10.128.0.0/14
**env.install_config.cluster_network.host_prefix** | The subnet prefix length to assign to each individual node. For example, if<br /> hostPrefix is set to 23 then each node is assigned a /23 subnet out of the given cidr. A hostPrefix<br /> value of 23 provides 510 (2^(32 - 23) - 2) pod IP addresses. | 23
**env.install_config.cluster_network.type** | The cluster network provider Container Network Interface (CNI) plug-in to install.<br /> Either OpenShiftSDN (recommended) or OVNKubernetes. | OpenShiftSDN
**env.install_config.service_network** | The IP address block for services. The default value is 172.30.0.0/16. The OpenShift SDN<br /> and OVN-Kubernetes network providers support only a single IP address block for the service<br /> network. An array with an IP address block in CIDR format. | 172.30.0.0/16
**env.install_config.fips** | True or False (boolean) for whether or not to use the United States' Federal Information Processing<br /> Standards (FIPS). Not yet certified on IBM zSystems. Enclosed in 'single quotes'. | 'false'
**proxy_env.http_proxy** | (Optional) A proxy URL to use for creating HTTP connections outside the cluster. Will be<br /> used in the install-config and applied to other Ansible hosts unless set otherwise in<br /> no_proxy below. Must follow this pattern: http://usernamepswd>@ip:port | http://ocp-admin:Pa$sw0rd@9.72.10.1:80
**proxy_env.https_proxy** | (Optional) A proxy URL to use for creating HTTPS connections outside the cluster. Will be<br /> used in the install-config and applied to other Ansible hosts unless set otherwise in<br /> no_proxy below. Must follow this pattern: https://username:pswd@ip:port | https://ocp-admin:Pa$sw0rd@9.72.10.1:80  
**proxy_env.no_proxy** | (Optional) A comma-separated list of destination domain names, IP addresses, or other<br /> network CIDRs to exclude from proxying. Preface a domain with . to match subdomains only.<br /> For example, .y.com matches x.y.com, but not y.com. Use * to bypass the proxy for all listed destinations. | example.com, 192.168.10.1