# Issue: `storage_group_2` (and beyond) not activated during boot

## Summary

`storage_group_2` (and any additional storage groups) are attached to the LPAR
partition via HMC during LPAR creation, but their FCP LUNs are **never activated
by the kernel** during the live-disk boot or installation phase, and are **not
referenced** in the ABI `rootDeviceHints`. This means the disks are physically
presented to the LPAR but not visible as block devices during RHCOS installation.

## Affected files

| File | Problem |
|:---|:---|
| `roles/boot_LPAR_abi/templates/genericdvd.prm.j2` | Only emits `rd.zfcp=` for `storage_group_1`; `storage_group_2`/`3` never activated |
| `roles/boot_LPAR/templates/genericdvd.prm.j2` | Same — only `storage_group_1` activated |
| `roles/prepare_configs/templates/agent-config.yaml.j2` | `rootDeviceHints` hardcoded to `storage_group_1` only |
| `roles/create_lpar/tasks/main.yaml` | Correctly attaches `storage_group_2` at HMC level (good), but that is insufficient on its own |

## Missing role

The documentation in `docs/run-the-playbooks.md` and `docs/run-the-playbooks-for-abi.md`
references a `roles/configure_storage` role that was supposed to use
`lpar.storage_group_2.auto_config: True` to extend the OS logical volume with
the second storage group after installation. **This role does not exist in the
repository.** It was either never implemented or was removed.

## Required fix

### 1. Activate additional FCP LUNs in the parm file templates

Both `roles/boot_LPAR_abi/templates/genericdvd.prm.j2` and
`roles/boot_LPAR/templates/genericdvd.prm.j2` should loop over all defined
storage groups (not just `storage_group_1`) and emit an `rd.zfcp=` entry for
each FCP-type group. Example approach:

```jinja2
{%- set sg_keys = ['storage_group_1', 'storage_group_2', 'storage_group_3'] -%}
{%- for sg_key in sg_keys -%}
{%-   if node.lpar[sg_key] is defined and node.lpar[sg_key].type | lower == "fcp" -%}
 rd.zfcp=0.0.{{ node.lpar[sg_key].dev_num }},{{ node.lpar[sg_key].storage_wwpn[0] }},{{ node.lpar[sg_key].lun_name }}
{%-   endif -%}
{%- endfor -%}
```

Or, if the host_vars schema is refactored to use a list instead of numbered keys,
loop over `node.lpar.storage_groups`.

### 2. Optionally extend `rootDeviceHints` selection

`agent-config.yaml.j2` currently always points `rootDeviceHints` at
`storage_group_1`. This is correct for the OS disk and should remain the default.
No change needed here unless there is a use case for installing on a non-first
storage group.

### 3. Implement or remove `configure_storage`

Either:
- Implement `roles/configure_storage` to extend the LVM logical volume using
  `storage_group_2` when `auto_config: True`, and wire it into the playbooks; or
- Remove all references to `configure_storage` and `auto_config` from the
  documentation to avoid misleading users.

## Impact

- Users who define `storage_group_2` (e.g. for ODF/Ceph data disks) on a
  non-DPM LPAR will find those LUNs not visible during installation. Post-install
  they will typically become available once the OS activates the FCP subsystem,
  but this is not guaranteed and depends on the system's zfcp configuration.
- The `auto_config: True` flag documented in `set-variables-host-vars.md` has
  no effect because the backing role does not exist.

## References

- `inventories/default/host_vars/KVMhostname1-here.yaml.template` — shows
  `storage_group_2` commented out as optional
- `docs/set-variables-host-vars.md` lines 89–94 — documents `storage_group_2`
  variables including `auto_config`
- `roles/create_lpar/tasks/main.yaml` lines 50–70 — only place `storage_group_2`
  is used in roles
