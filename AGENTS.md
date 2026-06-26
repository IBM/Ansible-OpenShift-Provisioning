# AGENTS.md

## Repository Overview
This repository automates OpenShift provisioning on IBM zSystems / LinuxONE using Ansible across KVM, LPAR, z/VM, ABI, and related bastion-based workflows.

## Build / Lint / Test Commands

### Primary validation commands
Run from repository root unless noted otherwise.

```bash
ansible-lint
```

Lint a specific changed file:

```bash
ansible-lint playbooks/create_abi_cluster.yaml
ansible-lint roles/boot_LPAR_abi/tasks/main.yaml
```

Run a specific playbook with the default inventory from `ansible.cfg`:

```bash
ansible-playbook playbooks/create_abi_cluster.yaml
ansible-playbook playbooks/4_create_bastion.yaml
ansible-playbook playbooks/5_setup_bastion.yaml
ansible-playbook playbooks/master_playbook_for_abi.yaml -e "inventory_dir=${PWD}/inventories/default"
```

Run a playbook with explicit inventory:

```bash
ansible-playbook -i inventories/default playbooks/create_abi_cluster.yaml
```

Run a specific tagged portion of a playbook:

```bash
ansible-playbook -i inventories/default playbooks/create_abi_cluster.yaml --tags prepare_configs
ansible-playbook -i inventories/default playbooks/create_abi_cluster.yaml --tags ssh_to_nodes
```

Run a focused syntax check before execution:

```bash
ansible-playbook -i inventories/default playbooks/create_abi_cluster.yaml --syntax-check
```

### Commands used by the project at runtime
These are not unit tests, but they are key execution paths used by roles and docs:

```bash
openshift-install agent create pxe-files --log-level=debug
openshift-install agent create image --log-level=debug
openshift-install agent wait-for install-complete --dir=/root/ansible_workdir
openshift-install wait-for bootstrap-complete --dir=/root/ocpinst
```

### Single-test guidance
There is no top-level pytest-based test suite in this repository. “Single test” usually means one of:

1. Lint one file:
   ```bash
   ansible-lint roles/dns/tasks/main.yaml
   ```

2. Syntax-check one playbook:
   ```bash
   ansible-playbook -i inventories/default playbooks/create_abi_cluster.yaml --syntax-check
   ```

3. Execute one workflow slice by tags:
   ```bash
   ansible-playbook -i inventories/default playbooks/create_abi_cluster.yaml --tags prepare_configs
   ```

4. Execute one playbook only:
   ```bash
   ansible-playbook playbooks/4_create_bastion.yaml
   ```

### Documentation commands
The docs site uses MkDocs.

Install and serve locally:

```bash
python3 -m pip install mkdocs
python3 -m mkdocs serve
```

Deploy command used in CI:

```bash
python3 -m mkdocs gh-deploy
```

### Vendored role test commands
The vendored `roles/robertdebock.epel` and `roles/robertdebock.openvpn` directories contain their own Molecule/Tox workflows. Treat them as upstream third-party content unless explicitly modifying those roles.

Examples:

```bash
cd roles/robertdebock.epel && molecule test
cd roles/robertdebock.epel && tox
cd roles/robertdebock.openvpn && molecule test
cd roles/robertdebock.openvpn && tox
```

## Code Style Guidelines

### General
- Follow `.editorconfig`.
- Use UTF-8, LF line endings, and ensure a final newline.
- YAML, YML, and most repository text files use 2-space indentation.
- Python uses 4-space indentation.
- Shell scripts use 4-space indentation.
- Avoid trailing whitespace, except Markdown where trimming is disabled.

### Ansible / YAML
- Prefer clear task names beginning with verbs.
- Keep YAML indentation at 2 spaces.
- Use fully qualified collection names where already established, e.g. `ansible.builtin.*`.
- Match the repository’s existing style before refactoring.
- Prefer targeted changes over broad restructuring in playbooks and roles.
- Preserve backward compatibility across KVM, LPAR, z/VM, SNO, and ABI flows unless the task explicitly changes behavior.
- Keep inventory variable naming and nesting aligned with existing structures such as:
  - `env.cluster.*`
  - `env.bastion.*`
  - `node.lpar.*`
  - `node.networking.*`

### Jinja / Templates
- Be careful with whitespace control in YAML-producing templates.
- When editing generated YAML templates, validate final rendered indentation and list structure.
- Avoid introducing template changes that alter existing non-target installation paths.

### Python
- Follow existing repository Python style when touching helper scripts.
- Keep imports simple and grouped at the top.
- Use descriptive argument names matching CLI flags and existing playbook variables.
- Favor small, minimal-risk changes in boot/helper scripts because they interact with HMC/Tessia and runtime infrastructure.
- Prefer public/stable APIs over private methods of external libraries.

### Shell
- Use `#!/bin/bash` when the script already targets bash.
- Prefer straightforward commands over complex shell abstractions.
- Keep scripts readable and environment assumptions explicit.

### Naming
- Use descriptive names that match infrastructure concepts: `bastion`, `control`, `compute`, `lpar`, `kvm_host`, `inventory_dir`, etc.
- For new HA-specific assets, use names that clearly reflect HA/DPM/LPAR purpose without renaming established generic paths unless necessary.

### Error handling and safety
- Prefer explicit guards with `when:` in Ansible for optional resources.
- Use defaults carefully for optional variables.
- Do not silently change behavior for unrelated install types.
- Preserve existing secrets boundaries:
  - non-secret defaults in `group_vars/all.yaml`
  - secrets in `group_vars/secrets.yaml`
- Be cautious with destructive operations, boot logic, storage settings, and network parameters.
- For shell execution in Ansible, use `set -o pipefail` when piping commands and where shell is required.

### Validation expectations
Before finishing a change, prefer the smallest relevant validation:
- `ansible-lint <changed-file-or-playbook>`
- `ansible-playbook --syntax-check ...`
- targeted tagged run where practical

## Contribution Requirements
- Add a `Signed-off-by:` trailer to commit messages.
- If AI was involved, add a matching file comment beginning with `Made by AI:` or `Assisted by AI:` where applicable.
- PRs should answer: “If and how AI was involved?”

## Notes for Agents
- Read related files together before editing.
- Prefer minimal diffs.
- Do not “clean up” unrelated formatting or naming.
- Treat vendor roles under `roles/robertdebock.*` as external unless the task explicitly targets them.