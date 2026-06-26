# AGENTS.md

## Plan Mode Guidance

Use this mode to produce implementation plans before editing code.

### Planning expectations
- Identify the exact files likely to change.
- Separate repository changes from runtime/environment work.
- Note compatibility risks across KVM, LPAR, z/VM, SNO, ABI, and disconnected paths.
- Prefer phased plans with validation after each phase.

### Plan structure
1. Goal
2. Constraints and non-goals
3. Files to inspect
4. Proposed changes
5. Validation steps
6. Rollback or safe fallback

### Good plan characteristics
- Minimal and testable
- Explicit about assumptions
- Focused on user-requested scope
- Avoids unrelated cleanup

### Example validation block

```bash
ansible-lint <changed-file>
ansible-playbook -i inventories/default <playbook> --syntax-check
ansible-playbook -i inventories/default playbooks/create_abi_cluster.yaml --tags prepare_configs
```

### Notes
- For HA/DPM/LPAR work, explicitly confirm node topology, bastion placement, networking mode, and whether existing non-HA flows must remain unchanged.
- For boot failures, distinguish generated-config issues from HMC/Tessia/runtime infrastructure issues before proposing code changes.