# Step 2: Set Variables - HyperShift (OPTIONAL)
- These variables control the installation of HyperShift.
- They are <b><i>optional</i></b>, as HyperShift is not required to install OpenShift.
- For more on what HyperShift is, see Red Hat's [blog](https://cloud.redhat.com/blog/a-guide-to-red-hat-hypershift-on-bare-metal).

## HyperShift Hypervisor
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**hypervisor_ip** | IPv4 address of the HyperShift hypervisor. | 192.168.1.1
**hypervisor_user** | Admin user on the HyperShift hypervisor, not necessarily</br > the one used to connect to via SSH. | admin
**ansible_become_password** | Do not change. Set in Ansible Vault (next step) -</br > HyperShift hypervisor user's SSH password. | "{{ vault_hypervisor_hypershift_pass }}"
**ansible_host** | IP or hostname Ansible will use to connect to via SSH.</br > Leave as is to use same value as hypervisor_ip var. | "{{ hypervisor_ip }}"
**ansible_user** | Username for Ansible to connect as via SSH. Leave</br > as is to use same value as hypervisor_user var. | "{{ hypervisor_user }}"
**pkgs** | Packages to be installed on host. | [ make, jq, ..., lvm2 ]
**network_interface** | The interface to be used for the virtual network bridge. | "{{ ansible_default_ipv4.interface }}"
**bridge_name** | Name of virtual network to be defined</br > that the VM guests will use. | macvtap-net
**gateway** | IP address that acts as the exit point</br > to reach other networks.  | "{{ ansible_default_ipv4.gateway }}"

## HyperShift Bastion
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**bastion_ip** | IPv4 address of the HyperShift bastion. | 192.168.1.1
**bastion_user** | Admin user on the HyperShift bastion, not necessarily</br > the one used to connect to via SSH. | admin
**ansible_become_password** | Do not change. Set in Ansible Vault (next step) - HyperShift</br > bastion user's SSH password. | "{{ vault_bastion_hypershift_pass }}"
**ansible_host** | IP or hostname Ansible will use to connect to via SSH. Leave as</br > is to use same value as bastion_ip var. | "{{ bastion_ip }}"
**ansible_user** | Username for Ansible to connect as via SSH. Leave as is to use</br > same value as bastion_user var. | "{{ bastion_user }}"
**pkgs** | Packages to be installed on host. | [ make, jq, ..., rsync ]
**create** | True or False - create the hypervisor bastion or not. If 'True' </br >must fill in variables below. | True
**vm_name** | Name of the guest virtual machine from the perspective of the hypervisor. | bastion
**disk_size** | Amount of virtual storage capacity allocated to this VM, in gigabytes. | 100
**vcpu** | Number of virtual CPUs allocated to this VM. | 4
**ram** | Amount of virtual memory allocated to this VM, in megabytes. | 4096
**interface** | Name of the network device (from Linux perspective) used for connecting</br > the VM to the network. | enc1
**hostname** | DNS short hostname of the bastion. | bastion-hs
**base_domain** | Base domain for the bastion, will be combined with base domain to create cluster URL. | ihost.com
**os_variant** | RHEL version closest to ISO file used to install bastion. | rhel8.7
**nameservers** | List of DNS nameserver(s) for this host. | - 192.168.1.254<br />- 192.168.1.253
**gateway** | IP address that acts as the exit point for the bastion to reach other networks. | 192.168.1.1
**subnet_mask** | Subnet size for the bastion's IP in dotted decimal notation. | 255.255.255.0
**root_pass** | Do not change. Set in Ansible Vault (next step) - Bastion's root SSH password. | "{{ vault_bastion_hypershift_root_pass }}"

## HyperShift General
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**branch_for_cli** | Git branch for latest release of hypershift | release-4.13
**mgmt_cluster_nameserver** | IP Address of Nameserver of Management Cluster | 192.168.10.1
**go_version** | Version of go you want to install on hypervisor.</br > (It will replace existing go with this version ) | 1.19.5
**oc_url** | URL for OC Client that you want to install on the host | https://[...]openshift-client-linux-4.13.0-ec.4.tar.gz
**hcp.clusters_namespace** | Namespace for Creating Hosted Control Plane | clusters
**hcp.hosted_cluster_name** | Name for the Hosted Cluster  | hosted0
**hcp.basedomain** | Base domain for Hosted Cluster | example.com
**hcp.pull_secret_file** | Path for the pull secret. No need to change this as we</br > are copying the pull secret to same file </br >/root/ansible_workdir/auth_file | /root/ansible_workdir/auth_file
**hcp.ocp_release** | OCP Release version for Hosted Control Cluster and Nodepool | 4.13.0-rc.4-multi
**hcp.machine_cidr** | Machines CIDR for Hosted Cluster | 192.168.122.0/24
**hcp.arch** | Architecture for InfraEnv and AgentServiceConfig" | s390x
**hcp.pull_secret** | Do not change. Set in Ansible Vault (next step) - Pull Secret of Management Cluster. | "{{ vault_hcp_pull_secret }}"
**hcp.api_server** | API server URL of the Management Cluster. | https://my-k8s.example.com:6443
**hcp.user_name** | Username to authenticate to the Management Cluster. | kubeadmin
**hcp.password** | Do not change. Set in Ansible Vault (next step) - Password to authenticate to Management Cluster. | "{{ vault_hcp_pass }}
**asc.url_for_ocp_release_file** | Add URL for OCP release.txt file | https://.../release.txt
**asc.db_volume_size** | DatabaseStorage Volume Size | 10Gi
**asc.fs_volume_size** | FileSystem Storage Volume Size | 10Gi
**asc.ocp_version** | OCP Version for AgentServiceConfig | 4.13.0-ec.4
**asc.iso_url** | URL for ISO image | https://[...]s390x-live.s390x.iso
**asc.root_fs_url** | URL for rootfs image | https://[...]live-rootfs.s390x.img
**asc.mce_namespace** | Namespace where your Multicluster Engine Operator</br > is installed. Recommended Namespace for MCE is</br > 'multicluster-engine' Change this only if MCE is installed</br > in other namespace | multicluster-engine