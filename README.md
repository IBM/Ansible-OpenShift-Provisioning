# Ansible-OpenShift-Provisioning

## Table of Contents
* [Scope](#Scope)
* [Supported Operating Systems](#Supported-Operating-Systems)
* [Installation Instructions](#Installation-Instructions)
* [Pre-Requisites](#Pre-Requisites)
* [Troubleshooting](#Troubleshooting)
* [Teardown](#Teardown)
* [Tags](#Tags)
* [Vault](#Vault)

## Scope
* The goal of this playbook is to automate the setup and deployment of a Red Hat OpenShift Container Platform (RHOCP) cluster on IBM Z / LinuxONE with Kernel Virtual Machine (KVM) as the hypervisor. This is a user-provisioned infrastructure (UPI) installation of RHOCP.
* These playbooks assume a basic understanding of the command-line. Using them requires near-zero experience with Ansible, unless you want to customize them.

## Supported Operating Systems 
(for local workstation running Ansible)
* Linux (RedHat and Debian)
* MacOS X

## Installation Instructions
A step-by-step guide can be found [here](#installation_instructions.md) in the installation_instructions.md file.

## Pre-Requisites
* A Red Hat account ([Sign Up](https://www.redhat.com/wapps/ugc/register.html?_flowId=register-flow&_flowExecutionKey=e1s1))
* A [license](https://access.redhat.com/products/red-hat-openshift-container-platform/) or [free trial](https://www.redhat.com/en/technologies/cloud-computing/openshift/try-it) of Red Hat OpenShift Container Platform for IBM Z systems - s390x architecture (OCP license comes with licenses for RHEL and CoreOS)
* Hardware Management Console (HMC) access on IBM Z or LinuxONE (390x)
* Must be Dynamic Partition Manager (DPM) enabled
* An FTP server with RHEL iso mounted
* For a minimum installation, at least:
  * 6 Integrated Facilities for Linux (IFLs) with SMT2 enabled
  * 85 GB of RAM
  * A storage group created with 1 TB of disk space
  * 8 IPv4 addresses
* If you are using MacOS for your workstation running Ansible, you also need to have: 
    * [Homebrew](https://brew.sh/) package manager installed:
      ~~~
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      ~~~
    * Updated software for command line tools:
      ~~~
      softwareupdate --all --install
      ~~~
      ~~~
      xcode-select --install
      ~~~
* [Python3](https://realpython.com/installing-python/) and [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) intalled on your local workstation \
  * <u>Mac</u>:
    ~~~
    brew install python3
    ~~~
    ~~~
    brew install ansible
    ~~~
  * <u>Linux</u>:
    ~~~
    sudo apt install python3
    ~~~
    ~~~
    sudo apt install ansible
    ~~~
    * or (depending on your distribution),
    ~~~
    sudo yum install python3
    ~~~
    ~~~
    sudo yum install ansible
    ~~~

## Tags
* To be more selective with what parts of playbooks run, use tags. 
* To determine what part of a playbook you would like to run, open the playbook you'd like to run and find the roles parameter. Each [role](roles) has a corresponding tag.
* This is especially helpful for troubleshooting. 

## Vault
* The setup.yaml playbook encrypts passwords entered into the [master variables file](inventories/default/group_vars/all.yaml) for security. 
* The sensitive data is transferred to the [vault](vault.yaml) and the variables are redacted from the original variables file.
* To encrypt/decrypt the vault to view its contents, run either of the following commnds:
  ~~~
  ansible-playbook playbooks/vault.yaml --tags decrypt --ask-vault-pass
  ansible-playbook playbooks/vault.yaml --tags encrypt --ask-vault-pass
  ~~~