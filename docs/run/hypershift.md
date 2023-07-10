# Step 4: Run the Playbooks

## HyperShift - Create Hosted Cluster Playbook
* Run this shell command to run the [create_hosted_cluster.yaml](https://github.com/IBM/Ansible-OpenShift-Provisioning/blob/main/playbooks/create_hosted_cluster.yaml) playbook:
```
ansible-playbook playbooks/create_hosted_cluster.yaml
```
### Prerequisites
* Running OCP Cluster (Management Cluster)
* Multi Cluster Engine (MCE) Operator installed on Management Cluster.
* MCE instance created and hypershift-preview component enabled.
* Hypervisor with root user access
### Overview
* Creates Hosted Cluster with Hypershift
### Outcomes
* Creating AgentServiceConfig, HostedControlPlane, InfraEnv Resources
* Log in to Management Cluster
* Creates AgentServiceConfig resource and required configmaps
* Deploys HostedControlPlane
* Creates InfraEnv resource and wait till ISO generation