# Changelog
All notable changes to this project will be documented in this file.  

## Roadmap
* Add option to use a VPN to reduce # of IPs needed
* Add the ability to provision multiple LPARs for high availability
* Tag infrastructure nodes for specific operators
* Add air-gapped (disconnected) install option
* Add option for OpenShift to use a proxy server
* Add README’s for each role
* Make ssh-copy-id role idempotent

## Documentation Overhaul
Version 0.3.1  
Released: 2022-06-03
### Summary 
* Moved documentation to GitHub Pages to be more reader-friendly.

## Automated KVM Host Provisioning
Version 0.3.0  
Released: 2022-03-26  
### Summary
* Now able to provision the KVM host via Ansible.
* Changed the structure of playbooks, variables, and inventories to use Ansible best practices.
### Added
* Support for using IBM's zHMC Ansible modules to automate the creation of a logical partition (LPAR) profile, connect storage group and network card, boot from an FTP server, and then kickstart the installation of RHEL to serve as the KVM hypervisor for the cluster.
* Usage of Ansible vault to encrypt sensitive data. Playbooks must now be run with --ask-vault-pass, e.g. 'ansible-playbook playbooks/site.yaml --ask-vault-pass'
### Modified 
* Bastion boot method from cloud-init to FTP and kickstart.
* The structure of playbooks. The setup.yaml playbook still must be run before anything else, but now there is a master playbook - site.yaml which imports all other playbooks. This was done to be more user-friendly and in-line with best practices. Previously, everything was all in one playbook and relied on tags to start back from a given point. Relying solely on tags proved tedious.
* The structure for inventories, which allows for more flexibility with deployments and is more in-line with best practices. Now you can have multiple inventories and specify which you would like to use for a given run in the ansible.cfg file.
* The structure of variables, to allow for the separation of the bastion node from the rest of the cluster. This opens up many more possibilities for more complex deployments where, for example, the bastion node is already created.

## Infrastructure Nodes, Extra Apps, Security
Version: 0.2.1  
Released: 2022-01-06  
### Summary 
* Now able to designate compute nodes as infrastructure nodes, and create optional RHEL VMs for additional non-cluster applications running on the KVM host.
* Made changes to SSH and SELinux tasks to be more secure.
### Added
* Support for creating infrastructure nodes and extra apps.
* Added tcp port 53 to firewall.
* Setting of permissions and ownership of important configuration files to bastion admin user instead of root.
* Wheel to groups that bastion admin user is added to on boot.
* More rounds of checking cluster operators and CSRs in verification steps to ensure the playbook doesn't fail if it takes a long time for those steps to complete.
* Task to httpd to allow port 4443 because SELinux is no longer set to permissive (see '[Removed](###Removed)' below).
### Modified
* Formatting of README file to be prettier and more useful.
* env.yaml to have two sections separated by a comment block: one for variables that need to be filled out, the other for pre-filled variables that can be modified if desired.
* Ansible user from running as root to an admin user with sudo privileges.
### Removed
* The need to run anything as root user for security reasons.
* set_selinux_permissive mode role for security reasons.

## Scaling
Version: 0.2.0  
Released: 2021-12-09  
### Summary
* Now supports any number of control and compute nodes to be provisioned in the cluster.
* This update heavily modifies the variable structure in env.yaml in order to make scaling work.
### Added
* Support for scaling of control and compute nodes.
### Modified
* Variable structure in env.yaml in order to support scaling.
* Tags to match their corresponding role.
* Every reference to a variable from env.yaml to match the new structure.

## Automated OCP Verification
Version: 0.1.1  
Released: 2021-12-03  
### Summary
* Fully automated all OCP verification steps. Cutting the number of steps nearly in half. The main playbook can now run completely hands-off from kicking it off all the way to an operational cluster. The last step provides the first-time login credentials.
### Added
* 5 roles related to automating OCP verification steps: wait_for_bootstrap, approve_certs, check_nodes, wait_for_cluster_operators, and wait_for_install_complete.
* Role to check internal and external DNS configuration before continuing. Including checking to make sure the name resolves to the correct IP address.
### Modified
* The mirrors for CoreOS versions to update to 4.9 and tested them.
* The acquisition method of RHEL qcow2 from downloading via ephemeral link to having the user download the file to their local machine as a pre-req. This was changed to avoid having to re-copy the link every time it expires.
* teardown.yaml and reset_files role to be fully idempotent when running the main playbook from the point where each type of teardown sets the user back to.
* Lots of small tweaks.
### Removed
* Instructions in README for doing OCP verification steps manually

## Automated Bastion Install
Version: 0.1.0  
Released: 2021-11-24  
### Summary
* Fully automated bastion installation and configuration using cloud-init
### Added
* Options in env.yaml for creating a DNS server on the bastion or not, and for automatically attaching Red Hat subscriptions
* Variables for bootstrap, bastion, control and compute nodes' specifications in env.yaml
* Node name variables in env.yaml
* Variable for network interface name in env.yaml
* Variable for DNS forwarder in env.yaml
* Templating of DNS configuration files so they don't have to be pre-provided
* Expect script to ssh_copy_id role so that the user doesn't have to type in ssh password when copying ssh key
* Templating of haproxy config file
* A boot_teardown tag in teardown.yaml to automate the teardown of bootstrap node
### Modified
* create_bastion role to use cloud-init to fully automate configuration and installation of the bastion node
* teardown.yaml script to decrease complexity and work faster.
* Some tags to match their corresponding role names
* Lots of small improvements and tweaks
### Removed
* Encryption of env.yaml as it was unnecessary and increased complexity

## First Working Build
Version: 0.0.1
Released: 2021-08-24  

## Initial Commit
Version: 0.0.0  
Released: 2021-06-11  