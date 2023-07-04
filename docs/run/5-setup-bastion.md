# Step 4: Run the Playbooks
## 5 Setup Bastion Playbook
<img src="../../images/5-setup-bastion.png" width="100%"/>

* Run this shell command to run the [5_setup_bastion_bastion.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/5_setup_bastion_bastion.yaml) playbook:
```
ansible-playbook playbooks/5_setup_bastion_bastion.yaml
```
### Overview
* Configuration of the bastion to host essential infrastructure services for the cluster. 
* Can be first-time setup or use an existing server.
### Outcomes
* Ansible SSH key copied to bastion for passwordless authentication
* Software packages set by 'pkgs' in inventory have been installed
* An OCP-specific SSH key is generated for passing into the install-config (then passed to the nodes)
* Firewall is configured to permit traffic through the necessary ports
* Domain Name Server (DNS) configured to resolve cluster's IP addresses and APIs. Only done if 'setup_dns' is 'True'.
* DNS is checked to make sure all the necessary Fully Qualified Domain Names, including APIs resolve properly. Also ensures outside access is working.
* High Availability Proxy (HAProxy) loadbalancer is configured. Only done if 'setup_lb' is 'True'
* If the the cluster is to be highly available (meaning spread across more than one LPAR), an OpenVPN server is setup on the bastion to allow for the KVM hosts to communicate between eachother. OpenVPN clients are configured on the KVM hosts.
* CoreOS roofts is pulled to the bastion if not already there
* OCP client and installer are pulled down if not there already
* oc, kubectl and openshift-install binaries are installed
* OCP install-config is templated and backed up
* Manfifests are created
* OCP install directory found at /root/ocpinst/ is created and populated with necessary files
* Ignition files for the bootstrap, control, and compute nodes are transferred to HTTP or FTP accessible directory for booting nodes
### Notes
* The stickiest part is DNS setup and get_ocp role at the end