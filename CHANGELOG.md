# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.0.1] - 2021-08-24

### Added
- Added a changelog

[unreleased]: https://github.com/IBM/Ansible-OpenShift-Provisioning/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/IBM/Ansible-OpenShift-Provisioning/compare/v0.0.1

## [Automated Bastion Update]

## [1.0.0] - 2021-11-24

### Summary
- Fully automated bastion installation and configuration using cloud-init

### Added
- Added options in env.yaml for creating a DNS server on the bastion or not, and for automatically attaching Red Hat subscriptions
- Added variables for bootstrap, bastion, control and compute nodes' specifications in env.yaml
- Added node name variables in env.yaml
- Added variable for network interface name in env.yaml
- Added variable for DNS forwarder in env.yaml
- Added templating of DNS configuration files so they don't have to be pre-provided
- Added expect script to ssh_copy_id role so that the user doesn't have to type in ssh password when copying ssh key
- Added templating of haproxy config file
- Added a boot_teardown tag in teardown.yaml to automate the teardown of bootstrap node
### Modified
- Reworked create_bastion role to use cloud-init to fully automate configuration and installation of the bastion node
- Reworked teardown.yaml script to decrease complexity and work faster.
- Changed some tags to match their corresponding role names
- Lots of small improvements and tweaks
### Removed
- Removed encryption of env.yaml as it was unnecessary and increased complexity


[Automated Bastion Update]: https://github.com/IBM/Ansible-OpenShift-Provisioning/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/IBM/Ansible-OpenShift-Provisioning/compare/v1.0.0

## [Roadmap]

- Make ssh-copy-id role idempotent.
- Add role to check if DNS is working properly before continuing
- Add picture of finished infrastructure to README
- Add README’s for each role
- Create inventories and playbooks folders
- Integrate setup.yaml into main.yaml - no longer need to be separate because encryption role removed
- Automate verification steps. This is difficult because Ansible has to use bastion as a jumphost.
- Add option in env.yaml to create HAProxy on bastion or not (on different server)
- Further down the line, air-gapped install of OpenShift option
- Further down the line, add functionality to provision more than 3 control and 2 compute nodes
