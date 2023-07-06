# Step 2: Set Variables - Cluster
- These variables apply to the nodes that make up the OpenShift cluster guests. 
- The three types of nodes are the bootstrap node, control nodes, and compute nodes. Each have their own sets of variables, but they also share a set of cluster-wide variables.
- Can create as many compute nodes as needed, just add more to the list and follow the structure and naming convention of the section.

## Cluster-wide variables
These variables are for the cluster in general, all types of nodes can access them.

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**gateway** | IP address that acts as the exit point for the cluster's VMs to reach</br > other networks. | 192.168.1.1
**netmask** | Subnet size for the cluster's VMs in dotted decimal notation. | 255.255.255.0
**nameservers** | IP address that acts as the exit point for the VMs to reach other</br > networks. If bastion's 'setup_dns' is True, this should be the bastion's</br > IP address. | "{{ hostvars['bastion'].bastion_ip }}"
**fips** | True or False - use the United States' Federal Information</br > Processing Standards (FIPS). | False
**hyperthreading** | 'Enabled' or 'Disabled' hyperthreading on compute nodes.</br > Recommend Enabled. | Enabled
**forwarder** | IPv4 address of DNS forwarder for external name resolution. | 1.1.1.1
**cidr** | IPv4 block in Internal cluster networking in Classless Inter-Domain</br > Routing (CIDR) notation. Recommended to keep as is. | 10.128.0.0/14
**host_prefix** | The subnet prefix length to assign to each individual node.</br > For example, if hostPrefix is set to 23 then each node is</br > assigned a /23 subnet out of the given cidr. A hostPrefix</br > value of 23 provides 510 (2^(32 - 23) - 2) pod IP addresses. | 23
**net_type** | The cluster network provider Container Network Interface (CNI)</br > plug-in to install. Either OpenShiftSDN or OVNKubernetes (default). | OVNKubernetes
**service_network** | The IP address block for services. The default value is 172.30.0.0/16.</br > The OpenShift SDN and OVN-Kubernetes network providers support</br > only a single IP address block for the service network. An array with an</br > IP address block in CIDR format. Recommended to keep as is. | 172.30.0.0/16
**api_version** | Kubernetes API version for the cluster. | v1
**architecture** | CPU architecture of the cluster. Can be set at the level of</br > control/compute nodes so they are different, but that will only</br > determine what goes in the install-config.yaml file. Where they</br > are assigned in hypervisors 'guests' list and that hypervisors's</br > architecture will ultimately determine a node's architecture. | s390x

## Node Variables
- These variables are for the individual types of nodes. 
- Each type (bootstrap, control, compute) have their own section. 
- The variables controlling resource allocation (like disk_size) can be set at the group-level, as they are now, or at the host-level. For more on variable precedence, see [Ansible's documentation](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html) on using variables.

<u>Bootstrap:</u>
- The playbooks automatically tear the bootstrap down once it is finished.
- If you would like to repurpose the information and resourdces from the bootstrap node to add another compute node after the cluster is up, consider using the add_compute_nodes.yaml playbook. 

<u>Control:</U>
- There are almost always exactly three control nodes. 
- Form the control plane and help coordinate the cluster.

<U>Compute:</U>
- Can add as many compute nodes as desired. Two minumum. 
- If you would like to add more compute nodes after the cluster is already created, consider using the add_compute_nodes.yaml playbook. 

**Variable Name** | **Description** | **Example**
:--- | :--- | :---
**disk_size** | Amount of virtual storage capacity allocated to this VM, in gigabytes. | 120
**ram** | Amount of virtual memory allocated to this VM, in megabytes. | 16384
**vcpu** | Number of virtual CPUs allocated to this VM. | 4
**node_ip** | IPv4 address of the VM. | 192.168.1.6
**vm_name** | Name of the guest virtual machine from the perspective of the hypervisor. | control-1
**hostname** | DNS short hostname of the VM. | ocp-ct-1