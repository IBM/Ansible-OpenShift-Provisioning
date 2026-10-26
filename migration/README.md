# Migration

This folder contains playbooks for migrating inventory configuration files
between major schema versions.

---

## v1 → v2: `migrate_to_v2.yaml`

### What changed in v2

| Area | v1 | v2 |
|---|---|---|
| Bastion config location | `env.bastion` block inside `all.yaml` | Per-bastion `host_vars/<name>.yaml` file |
| Bastion list | Single implicit bastion in `env.bastion` | `bastion_nodes:` list in `all.yaml` |
| Schema marker | None | `schema_version: 2` at top of `all.yaml` |

### What the playbook does

1. Reads `all.yaml` and aborts if already at `schema_version: 2`.
2. Extracts the `env.bastion` block into a new host_vars file:
   `inventories/default/host_vars/<vm_name>.yaml`
3. Adds `bastion_nodes:` and `schema_version: 2` to `all.yaml`.
4. Removes `env.bastion` from `all.yaml`.
5. Writes a backup of the original `all.yaml` as `all.yaml.v1.bak`.

### Usage

Run from the repository root:

```bash
ansible-playbook migration/migrate_to_v2.yaml \
  -e "inventory_dir=inventories/default"
```

The `inventory_dir` variable defaults to `inventories/default`.
Override it if your inventory lives elsewhere.

### After migration

1. Review the generated `host_vars/<name>.yaml` and verify all values.
2. Ensure `<name>` appears in `inventories/default/hosts` under `[bastion]`.
3. Continue with the normal playbook flow from `0_setup.yaml`.
