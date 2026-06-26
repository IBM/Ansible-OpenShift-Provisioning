# AGENTS.md

## Code Mode Guidance

Use this mode when making or reviewing concrete repository changes.

### Primary expectations
- Prefer minimal, targeted diffs.
- Read related files before editing.
- Preserve existing behavior for KVM, LPAR, z/VM, SNO, ABI, and disconnected flows unless the task explicitly changes one of them.
- Treat `roles/robertdebock.*` as vendored upstream content unless explicitly asked to modify them.

### Validation
Prefer the smallest relevant validation after a change:

```bash
ansible-lint <changed-file>
ansible-playbook -i inventories/default <playbook> --syntax-check
ansible-playbook -i inventories/default playbooks/create_abi_cluster.yaml --tags prepare_configs
```

Examples:

```bash
ansible-lint playbooks/create_abi_cluster.yaml
ansible-lint roles/boot_LPAR_abi/tasks/main.yaml
ansible-playbook -i inventories/default playbooks/create_abi_cluster.yaml --syntax-check
```

### Editing guidelines
- Keep YAML indentation at 2 spaces.
- Keep Python indentation at 4 spaces.
- Use `ansible.builtin.*` module names where already used.
- Preserve inventory structure and variable naming conventions.
- Avoid unrelated refactors.
- Be careful with Jinja whitespace in YAML templates.
- Keep secrets in `inventories/default/group_vars/secrets.yaml`, not in non-secret defaults.

### Risk areas
Use extra caution when changing:
- boot logic
- DNS
- storage / root device hints
- HMC / Tessia integrations
- bastion networking
- installer artifacts and generated configs

### Runtime commands often relevant in this mode

```bash
ansible-playbook playbooks/4_create_bastion.yaml
ansible-playbook playbooks/5_setup_bastion.yaml
ansible-playbook playbooks/create_abi_cluster.yaml
ansible-playbook playbooks/master_playbook_for_abi.yaml -e "inventory_dir=${PWD}/inventories/default"
```

### Contribution requirements
- Include `Signed-off-by:` in commits.
- Add `Made by AI:` or `Assisted by AI:` comments where applicable.