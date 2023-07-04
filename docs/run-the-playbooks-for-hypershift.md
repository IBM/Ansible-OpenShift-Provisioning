# Run the Playbooks
## Prerequisites
* Running OCP Cluster ( Management Cluster ) 
* Multi Cluster Engine (MCE) Operator installed on Management Cluster.
* MCE instance created and hypershift-preview component enabled.
* KVM host with root user access

## Initial Setup for Hypershift
* Navigate to the [root folder of the cloned Git repository](https://github.com/IBM/Ansible-OpenShift-Provisioning) in your terminal (`ls` should show [ansible.cfg](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/ansible.cfg)).

* First playbook to be run is setup_for_hypershift.yaml which will create inventory file for hypershift and will add ssh key to the kvm host.
###### Note:
* If you are running this first time, it will prompt for the password for kvm host for the selected user.
* Enter password of kvm host to establish SSH key-based authentication.
* Run this shell command:
```
ansible-playbook playbooks/setup_for_hypershift.yaml
```

## Setup Ansible Vault for Management Cluster Credentials
### Overview
* Creating an encrypted file for storing Management Cluster Credentials.
### Steps:
* The ansible-vault create command is used to create the encrypted file.
* Create an encrypted file in playbooks directory and set the Vault password ( Below command will prompt for setting Vault password).
```
ansible-vault create playbooks/secrets.yaml
``` 

* Give the credentials of Management Cluster in the encrypted file (created above) in following format.
```
api_server: '<api-server-url>:<port>'
user_name: '<username>'
password: '<password>'
```

* You can edit the encrypted file using below command
```
ansible-vault edit playbooks/secrets.yaml
``` 
* Make sure you entered Manamegement cluster credenitails properly ,incorrect credentails will cause problem while logging in to the cluster in further steps.

## Create Hosted Cluster 
* Here is the playbook which handle the creation of Hosted Cluster using Hypershift , full descriptions of each can be found further down the page.
    * create_hosted_cluster.yaml ([code](https://github.com/veera-damisetti/Ansible-OpenShift-Provisioning/blob/main/playbooks/create_hosted_cluster.yaml))
* Run this shell command to run the create_hosted_cluster.yaml playbook:
```
ansible-playbook playbooks/create_hosted_cluster.yaml --ask-vault-pass
```


* Watch Ansible as it completes the installation, correcting errors if they arise.
* To look at what tasks are running in detail, open the playbook or roles/role-name/tasks/main.yaml

# Description for Playbooks

## setup_for_hypershift Playbook
### Overview
* First-time setup of the Ansible Controller,the machine running Ansible.
### Outcomes
* Inventory file for hypershift to be created.
* SSH key generated for Ansible passwordless authentication.
* Ansible SSH key is copied to kvm host.
### Notes
* You can use an existing SSH key as your Ansible key, or have Ansible create one for you.

## create_hosted_cluster Playbook
### Overview
* Creating AgentServiceConfig, HostedControlPlane , InfraEnv Resources
### Outcomes
* Log in to Management Cluster
* Creates AgentServiceConfig resource and required configmaps.
* Deploys HostedControlPlane and .
* Creates InfraEnv resource and wait till ISO generation.

