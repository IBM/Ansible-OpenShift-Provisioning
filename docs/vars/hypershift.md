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

## HyperShift Bastion
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**bastion_ip** | IPv4 address of the HyperShift bastion. | 192.168.1.1
**bastion_user** | Admin user on the HyperShift bastion, not necessarily</br > the one used to connect to via SSH. | admin
**ansible_become_password** | Do not change. Set in Ansible Vault (next step) - HyperShift</br > bastion user's SSH password. | "{{ vault_bastion_hypershift_pass }}"
**ansible_host** | IP or hostname Ansible will use to connect to via SSH. Leave as</br > is to use same value as bastion_ip var. | "{{ bastion_ip }}"
**ansible_user** | Username for Ansible to connect as via SSH. Leave as is to use</br > same value as bastion_user var. | "{{ bastion_user }}"

## HyperShift General
**Variable Name** | **Description** | **Example**
:--- | :--- | :---
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
**hcp.pull_secret** | Do not change. Set in Ansible Vault (next step) - Pull Secret of Management Cluster. | "{{ vault_hypershift_pull_secret }}"
**hcp.api_server** | Do not change. Set in Ansible Vault (next step) - API server URL of the Management Cluster. | "{{ vault_hcp_api_server }}"
**hcp.user_name** | Username to authenticate to the Management Cluster. | kubeadmin
**hcp.password** | Do not change. Set in Ansible Vault (next step) - Password to authenticate to Management Cluster. | "{{ vault_hcp_pass }}
**asc.url_for_ocp_release_file** | Add URL for OCP release.txt File | https://.../release.txt
**asc.db_volume_size** | DatabaseStorage Volume Size | 10Gi
**asc.fs_volume_size** | FileSystem Storage Volume Size | 10Gi
**asc.ocp_version** | OCP Version for AgentServiceConfig | 4.13.0-ec.4
**asc.iso_url** | Give URL for ISO image | https://[...]s390x-live.s390x.iso
**asc.root_fs_url** | Give URL for rootfs image | https://[...]live-rootfs.s390x.img
**asc.mce_namespace** | Namespace where your Multicluster Engine Operator</br > is installed. Recommended Namespace for MCE is</br > 'multicluster-engine' Change this only if MCE is installed</br > in other namespace | multicluster-engine