# Run the Playbooks for HCP KubeVirt

## Prerequisites
* Running OCP Cluster (Management Cluster) with sufficient resources
* For FIPS validation: Management cluster must be FIPS-enabled
* Bastion host with root user access
* Network connectivity between management cluster and bastion host

## Step-1: Setup Secrets File

Copy the secrets template and add your credentials:

```bash
cp inventories/default/group_vars/secrets.yaml.template inventories/default/group_vars/secrets.yaml
```

Edit `inventories/default/group_vars/secrets.yaml` and provide values for:

```yaml
# Section 5 - Bastion
vault_bastion_root_pass: <password_for_bastion_root_user>

# Section 6 - Management cluster login credentials
vault_ocp_user: <username>
vault_ocp_password: <password>
```

Encrypt the secrets file:

```bash
ansible-vault encrypt inventories/default/group_vars/secrets.yaml
```

To edit the encrypted file later:

```bash
ansible-vault edit inventories/default/group_vars/secrets.yaml
```

## Step-2: Configure HCP KubeVirt Parameters

Copy and edit the configuration template:

```bash
cp inventories/default/group_vars/hcp-kubevirt.yaml.template inventories/default/group_vars/hcp-kubevirt.yaml
```

Edit `inventories/default/group_vars/hcp-kubevirt.yaml` and update the parameters according to your environment.

**Important Parameters:**
- `mgmt_cluster_nameserver`: Nameserver IP for the management cluster
- `oc_url`: API server URL of the management cluster
- `mgmt_cluster_bastion.ip`: IP address of the bastion host
- `mce.catalogsource_image`: (Optional) Custom MCE catalog source image. If provided, a custom CatalogSource will be created and used for MCE installation. If empty, the default Red Hat Operators catalog will be used.
- `metallb.ip_pool`: IP range for MetalLB LoadBalancer services
- `storage.type`: Choose between `odf` or `hpp`
- `control_plane.hosted_cluster_name`: Name for your hosted cluster
- `control_plane.basedomain`: Base domain for the cluster
- `control_plane.pull_secret`: Pull secret (enclose in single quotes)
- `data_plane.compute_count`: Number of compute nodes

## Step-3: Run the Complete Workflow

Navigate to the root directory of the repository and run:

```bash
ansible-playbook playbooks/hcpvirt.yaml --ask-vault-pass
```

This master playbook will:
1. Setup inventory and passwordless SSH to bastion
2. Login to the management cluster
3. Check node resources
4. Install required operators (MCE, MetalLB, OpenShift Virtualization, Storage)
   - If `mce.catalogsource_image` is provided, a custom CatalogSource will be created
5. Create the hosted control plane cluster on KubeVirt
6. Configure networking and LoadBalancer
7. Wait for cluster to be ready

### Alternative: Run Step-by-Step

If you prefer to run the playbooks separately:

```bash
# Step 1: Setup inventory and SSH keys
ansible-playbook playbooks/setup_inventory_hcp_kubevirt.yaml --ask-vault-pass

# Step 2: Setup prerequisites and install operators
ansible-playbook playbooks/hcp_kubevirt_prereqs_setup.yaml --ask-vault-pass

# Step 3: Create HCP KubeVirt cluster
ansible-playbook playbooks/create_hcpvirt.yaml --ask-vault-pass
```

## Step-4: Access the Hosted Cluster

After successful deployment, access the hosted cluster from the bastion:

```bash
# SSH to bastion
ssh root@<bastion_ip>

# Export kubeconfig
export KUBECONFIG=/root/ansible_workdir/<hosted_cluster_name>-kubeconfig

# Verify cluster
oc get nodes
oc get co
```

## Destroy the HCP KubeVirt Cluster

To destroy the hosted cluster and all associated resources:

```bash
ansible-playbook playbooks/destroy_hcpvirt.yaml --ask-vault-pass
```

This will delete:
- Hosted cluster control plane
- Virtual machine compute nodes
- LoadBalancer services
- DNS configurations
- Associated resources

**Note**: Management cluster operators (MCE, MetalLB, OpenShift Virtualization, Storage) will remain installed.

## Playbook Descriptions

### setup_inventory_hcp_kubevirt.yaml
- Creates inventory file for HCP KubeVirt
- Generates SSH keys for passwordless authentication
- Copies SSH keys to the bastion host

### hcp_kubevirt_prereqs_setup.yaml
- Adds bastion host to dynamic inventory
- Logs in to the management cluster
- Checks node resources
- Installs required operators:
  - MultiClusterEngine (MCE) - with optional custom catalog source
  - MetalLB
  - OpenShift Virtualization
  - Storage operators (LSO/ODF or HPP based on configuration)
- Monitors operator installation

### create_hcpvirt.yaml
- Adds bastion host to dynamic inventory
- Logs in to the management cluster
- Enables wildcard DNS routes
- Creates the hosted control plane cluster
- Extracts kubeconfig
- Configures LoadBalancer and DNS
- Waits for cluster operators to be ready

### hcpvirt.yaml (Master Playbook)
- Runs `setup_inventory_hcp_kubevirt.yaml`
- Runs `hcp_kubevirt_prereqs_setup.yaml`
- Runs `create_hcpvirt.yaml`
- Complete end-to-end workflow

## Notes

### MCE Custom Catalog Source
The `mce.catalogsource_image` parameter in `hcp-kubevirt.yaml` is optional:
- **If provided**: A custom CatalogSource named `custom-redhat-operators` will be created in the `openshift-marketplace` namespace, and the MCE operator will be installed from this custom catalog
- **If empty or not provided**: The MCE operator will be installed from the default Red Hat Operators catalog


### FIPS Validation
For FIPS-validated deployments:
- The management cluster must be installed with FIPS mode enabled
- In the `hcp-kubevirt.yaml` file, set the `additional_flags` parameter to enable FIPS for the hosted cluster:
  ```yaml
  control_plane:
    additional_flags: "--fips"
  ```
- The hosted cluster will be created with FIPS mode enabled
