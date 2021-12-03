# Changelog

All notable changes to this project will be documented in this file.

###Jump-To:
* [Latest](#1.1.0 - Automated OCP Verification Update - 2021-12-03)
* [1.0.0](#1.0.0 - Automated Bastion Update - 2021-11-24)
* [0.0.1](#0.0.1 - Unreleased - 2021-08-24)
* [Roadmap](#Roadmap)


## 1.1.0 - Automated OCP Verification Update - 2021-12-03

### Summary
- Fully automated all OCP verification steps. Cutting the number of steps nearly in half. The main playbook can now run completely hands-off from kicking it off all the way to an operational cluster. The last step provides the first-time login credentials.

### Added
- 5 roles related to automating OCP verification steps: wait_for_bootstrap, approve_certs, check_nodes, wait_for_cluster_operators, and wait_for_install_complete.
- role to check internal and external DNS configuration before continuing. Including checking to make sure the name resolves to the correct IP address.
### Modified
- The mirrors for CoreOS versions to update to 4.9 and tested them.
- The acquisition method of RHEL qcow2 from downloading via ephemeral link to having the user download the file to their local machine as a pre-req. This was changed to avoid having to re-copy the link every time it expires.
- teardown.yaml and reset_files role to be fully idempotent when running the main playbook from the point where each type of teardown sets the user back to.
- Lots of small tweaks.
### Removed
- Instructions in README for doing OCP verification steps manually

## 1.0.0 - Automated Bastion Update - 2021-11-24

### Summary
- Fully automated bastion installation and configuration using cloud-init

### Added
- Options in env.yaml for creating a DNS server on the bastion or not, and for automatically attaching Red Hat subscriptions
- Variables for bootstrap, bastion, control and compute nodes' specifications in env.yaml
- Node name variables in env.yaml
- Variable for network interface name in env.yaml
- Variable for DNS forwarder in env.yaml
- Templating of DNS configuration files so they don't have to be pre-provided
- Expect script to ssh_copy_id role so that the user doesn't have to type in ssh password when copying ssh key
- Templating of haproxy config file
- A boot_teardown tag in teardown.yaml to automate the teardown of bootstrap node
### Modified
- create_bastion role to use cloud-init to fully automate configuration and installation of the bastion node
- teardown.yaml script to decrease complexity and work faster.
- Some tags to match their corresponding role names
- Lots of small improvements and tweaks
### Removed
- Encryption of env.yaml as it was unnecessary and increased complexity

## 0.0.1 - Unreleased - 2021-08-24

## Roadmap
* Add option in env.yaml to create HAProxy on bastion or not
* Add option for using a proxy server for OpenShift in install-config via env.yaml
* Add functionality to provision more than 3 control and 2 compute nodes
* Make ssh-copy-id role idempotent.
* Add picture of finished infrastructure to README
* Add README’s for each role
* Air-gapped (disconnected) install of OpenShift option