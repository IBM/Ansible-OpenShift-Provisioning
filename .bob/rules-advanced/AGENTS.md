# AGENTS.md

## Advanced Mode Guidance

Use this mode only when the task requires deeper multi-step reasoning, wider repository analysis, or coordination across several subsystems.

### When to use
- Cross-cutting changes affecting multiple playbooks or roles
- Designing a new workflow such as HA support for DPM LPARs
- Debugging failures that span inventory, generated configs, boot logic, and runtime infrastructure
- Producing structured implementation or migration plans

### Expectations
- Break work into explicit phases.
- Keep a TODO list updated for non-trivial tasks.
- Read all directly related files before proposing edits.
- Prefer repo-safe diagnosis before risky code changes.
- Call out assumptions, unknowns, and environment dependencies clearly.

### Analysis checklist
1. Identify impacted installation paths: KVM, LPAR, z/VM, SNO, ABI, disconnected.
2. Verify where secrets live versus non-secret defaults.
3. Trace playbook entrypoints to roles and templates.
4. Distinguish repository bugs from environment/runtime issues.
5. Propose the smallest validation that proves or disproves the hypothesis.

### Output guidance
- Summaries should separate:
  - confirmed facts
  - likely causes
  - repo-side changes
  - external/environment blockers
  - next validation steps
- Avoid speculative refactors.
- Preserve backward compatibility unless the task explicitly authorizes broader behavior changes.

### Useful validation examples

```bash
ansible-lint playbooks/create_abi_cluster.yaml
ansible-playbook -i inventories/default playbooks/create_abi_cluster.yaml --syntax-check
ansible-playbook -i inventories/default playbooks/create_abi_cluster.yaml --tags prepare_configs