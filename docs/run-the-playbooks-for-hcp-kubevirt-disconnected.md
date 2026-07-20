# Disconnected HCP KubeVirt Installation

This guide covers the end-to-end steps to install a Hosted Control Plane (HCP) on KubeVirt in a disconnected (air-gapped) environment using the `hcpvirt.yaml` master playbook.

---

## Prerequisites

- An OpenShift management cluster is up and reachable from the bastion.
- A mirror registry (e.g. Quay) is running and accessible from the bastion and the management cluster.
- The bastion host is reachable via SSH from the Ansible controller.
- `oc` CLI is installed on the bastion.
- `oc-mirror` v2 plugin is installed on the mirror host (bastion).

---

## Configuration Files

### `inventories/default/group_vars/disconnected.yaml`

Set `enabled: true` and fill in all registry fields:

```yaml
disconnected:
  enabled: true
  registry:
    url: '<registry-host>:<port>'          # e.g. sno-bastion.sno.com:8443
    ip: '<registry-ip>'
    pull_secret: '<pull-secret-json>'      # auth for the mirror registry only
    mirror_pull_secret: '<pull-secret-json>' # auth for all source registries + mirror
    ca_trusted: false
    ca_cert: |
      -----BEGIN CERTIFICATE-----
      <mirror registry CA certificate>
      -----END CERTIFICATE-----
  mirroring:
    host:
      name: <mirror-host-name>
      ip: <mirror-host-ip>
      user: root
    cluster_resources_dir: /root/ocpinst_disconnected/working-dir/cluster-resources
    oc_mirror:
      image_set:
        apiVersion: mirror.openshift.io/v2alpha1
        mirror:
          platform:
            channels:
              - name: stable-4.21
                minVersion: 4.21.0
                maxVersion: 4.21.0
          operators:
            - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.21
              packages:
                - name: multicluster-engine
                - name: metallb-operator
                - name: kubevirt-hyperconverged
```

> **Note:** `cluster_resources_dir` is where `oc-mirror v2` writes the cluster manifests
> (`idms-*.yaml`, `itms-*.yaml`, `cs-*.yaml`) after mirroring. Default:
> `/root/ocpinst_disconnected/working-dir/cluster-resources`

---

### `inventories/default/group_vars/hcp-kubevirt.yaml`

Key fields for disconnected installation:

```yaml
hcp:
  oc_url: https://api.<mgmt-cluster-domain>:6443
  mgmt_cluster_bastion:
    ip: <bastion-ip>
  ansible_key_name: ansible-ocpz    # SSH key generated on the bastion if absent

  mce:
    version: 2.11
    mce_namespace: multicluster-engine
    catalogsource_image: ""         # Leave empty — disconnected CatalogSource is used

  metallb:
    version: stable
    ip_pool:
      - <ip-range>                  # e.g. 172.23.232.232-172.23.232.234
    catalogsource_image: ""         # Leave empty — disconnected CatalogSource is used

  ocpvirt:
    version: stable

  storage:
    type: hpp                       # hpp or odf

  hpp:
    name: hostpath-provisioner
    storageclass_name: hostpath-csi
    storage_size: 50Gi
    storage_path: /var/hpvolumes

  control_plane:
    high_availability: false
    clusters_namespace: <namespace>
    hosted_cluster_name: <cluster-name>
    basedomain: <base-domain>
    ocp_release_image: 4.21.0-multi  # Must match the version mirrored
    arch: s390x
    pull_secret: '<mirror-registry-pull-secret-json>'

  data_plane:
    compute_count: 1
    cores: 4
    memory: 16Gi
    root_volume_size: 60
```

> **Important:** `catalogsource_image` fields for all operators must be left empty (`""`).
> In disconnected mode the CatalogSource applied from `oc-mirror` output is used automatically.

---

### `inventories/default/group_vars/secrets.yaml`

```yaml
vault_ocp_user: <oc-login-username>
vault_ocp_password: <oc-login-password>
vault_bastion_root_pass: <bastion-root-password>
```

---

## Playbook Flow

Run the master playbook:

```bash
cd Ansible-OpenShift-Provisioning
ansible-playbook playbooks/hcpvirt.yaml
```

The master playbook executes the following sub-playbooks in order:

```
hcpvirt.yaml
├── 1. setup_inventory_hcp_kubevirt.yaml      (always)
├── 2. disconnected_mirror_hcp_artifacts.yaml (disconnected.enabled == true)
├── 3. disconnected_hcp_kubevirt_setup.yaml   (disconnected.enabled == true)
├── 4. hcp_kubevirt_prereqs_setup.yaml        (always)
└── 5. create_hcpvirt.yaml                    (always)
```

---

## What Each Playbook Does

### 1. `setup_inventory_hcp_kubevirt.yaml`
Sets up the Ansible inventory and SSH key configuration for the bastion.

---

### 2. `disconnected_mirror_hcp_artifacts.yaml`
Runs `oc-mirror v2` on the mirror host to mirror all required images to the local registry.

After mirroring completes, the following cluster manifests are written to
`/root/ocpinst_disconnected/working-dir/cluster-resources/` on the bastion:

| File | Purpose |
|---|---|
| `idms-oc-mirror.yaml` | ImageDigestMirrorSet for release images |
| `itms-oc-mirror.yaml` | ImageTagMirrorSet for operator images |
| `cs-redhat-operator-index-v4-21.yaml` | CatalogSource for disconnected operators |
| `cc-redhat-operator-index-v4-21.yaml` | CatalogSource config |

---

### 3. `disconnected_hcp_kubevirt_setup.yaml`
Applies the disconnected configuration to the management cluster. Executes the
`disconnected_apply_hcp_manifests` role which performs the following steps in order:

**Step 1 — Registry CA ConfigMap**
Creates the `registry-config` ConfigMap in `openshift-config` with the mirror
registry CA certificate. The ConfigMap key uses `..` in place of `:` for the
port separator (e.g. `sno-bastion.sno.com..8443`):

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: registry-config
  namespace: openshift-config
data:
  sno-bastion.sno.com..8443: |
    -----BEGIN CERTIFICATE-----
    ...
    -----END CERTIFICATE-----
```

**Step 2 — Patch image.config**
Patches the cluster image config to trust the mirror registry CA:

```bash
oc patch image.config.openshift.io/cluster --type=merge \
  -p '{"spec":{"additionalTrustedCA":{"name":"registry-config"}}}'
```

**Step 3 — Wait for MCP and ClusterOperators**
- Pauses 2 minutes for the MCO to begin reconciling.
- Waits for `master` and `worker` MachineConfigPools to reach `Updated=True`.
- Polls until no ClusterOperator has `Degraded=True`.

**Step 4 — Apply mirror manifests**
Applies all manifests from the `cluster-resources` directory in this order:

1. `idms-*.yaml` — ImageDigestMirrorSets from oc-mirror
2. `idms-capi.yaml` — Additional IDMS for CAPI/importer pod images:
   ```yaml
   # mirrors quay.io/openshift-release-dev/ocp-v4.0-art-dev
   # → <registry>/<registry-org>/ocp-v4.0-art-dev
   ```
3. `itms-*.yaml` — ImageTagMirrorSets from oc-mirror
4. Patches `OperatorHub` to disable all default sources
5. `cs-*.yaml` — CatalogSources from oc-mirror
6. Waits for all CatalogSources to reach `READY` state

---

### 4. `hcp_kubevirt_prereqs_setup.yaml`
Installs the required operators on the management cluster.

Before installing operators, a pre-task reads the CatalogSource name from the
`cluster-resources` directory and sets it as the source for all Subscriptions:

```
/root/ocpinst_disconnected/working-dir/cluster-resources/cs-*.yaml
  → disconnected_catalogsource_name = cs-redhat-operator-index-v4-21
```

Operators installed (each Subscription points to the disconnected CatalogSource):

| Operator | Namespace |
|---|---|
| MultiClusterEngine (MCE) | `multicluster-engine` |
| MetalLB | `metallb-system` |
| OpenShift Virtualization | `openshift-cnv` |
| HostPath Provisioner (HPP) | cluster-scoped *(when `storage.type: hpp`)* |
| LSO + ODF | `openshift-local-storage` / `openshift-storage` *(when `storage.type: odf`)* |

---

### 5. `create_hcpvirt.yaml`
Creates the Hosted Control Plane cluster. Key steps in the `create_hcp_kubevirt` role:

**ICSP file** rendered from the disconnected registry mirrors:
```yaml
- mirrors:
  - <registry-url>/openshift/release
  source: quay.io/openshift-release-dev/ocp-v4.0-art-dev
- mirrors:
  - <registry-url>/openshift/release-images
  source: quay.io/openshift-release-dev/ocp-release
```

**`hcp create cluster kubevirt` command** with disconnected flags:
```bash
hcp create cluster kubevirt \
  --name=<cluster-name> \
  --namespace=<namespace> \
  --arch=s390x \
  --pull-secret=/root/ansible_workdir/auth_file \
  --base-domain=<base-domain> \
  --image-content-sources /root/ansible_workdir/icsp.yaml \
  --release-image=<registry-url>/openshift/release-images:<ocp-release-image> \
  --additional-trust-bundle /root/ansible_workdir/mirror-registry-ca.crt \
  --olm-disable-default-sources \
  --control-plane-availability-policy SingleReplica \
  --infra-availability-policy SingleReplica \
  --node-pool-replicas=<compute-count> \
  --memory=<memory> \
  --cores=<cores> \
  --root-volume-size=<root-volume-size>
```

---

## Running Individual Playbooks

You can also run each playbook independently if needed:

```bash
# Step 1 – Mirror images to local registry
ansible-playbook playbooks/disconnected_mirror_hcp_artifacts.yaml

# Step 2 – Apply mirror manifests to management cluster
ansible-playbook playbooks/disconnected_hcp_kubevirt_setup.yaml

# Step 3 – Install prerequisite operators
ansible-playbook playbooks/hcp_kubevirt_prereqs_setup.yaml

# Step 4 – Create the HCP cluster
ansible-playbook playbooks/create_hcpvirt.yaml
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `cluster-resources directory not found` | Mirroring step not completed | Run `disconnected_mirror_hcp_artifacts.yaml` first |
| `ConfigMap invalid: data key contains ':'` | Registry URL used as-is | Ensure `disconnected.registry.url` does not have extra colons; the role replaces `:` with `..` automatically |
| CatalogSource not READY | Registry unreachable from cluster nodes | Verify `disconnected.registry.ca_cert` is correct and nodes can reach the mirror registry |
| Operator CSV stuck in `Pending` | Wrong CatalogSource name in Subscription | Check the `cs-*.yaml` filename in `cluster-resources`; the name is auto-discovered |
| `hcp` binary not found | MCE pod layout differs between versions | The role tries `hcp-linux-s390x.tar.gz` first, then falls back to the `linux/s390x/` directory |
| `cat ~/.ssh/ansible-ocpz.pub: No such file` | Key not yet generated | The role auto-generates the key with `ssh-keygen` if absent |
