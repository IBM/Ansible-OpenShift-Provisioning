# AGENTS.md

## Ask Mode Guidance

Use this mode when user clarification is required before making a safe repository change.

### Ask only when necessary
Do not ask for information that can be obtained from repository files, playbooks, templates, docs, or configuration already present in the workspace.

### Good reasons to ask
- The requested behavior is ambiguous across supported install types.
- A change could break KVM, LPAR, z/VM, SNO, or disconnected flows without clarification.
- Required environment values are external and not present in inventory or docs.
- There are multiple valid implementation choices with materially different outcomes.

### Preferred question style
- Be specific and technical.
- Offer concrete options where possible.
- Ask for the minimum missing information needed to proceed safely.

### Examples
- Which installation path should this change affect: KVM, LPAR, z/VM, SNO, ABI, or all?
- Should HA support be limited to DPM-enabled LPARs, or should classic LPAR logic change too?
- Do you want a repo-only change, or should I also add validation commands and operator notes?

### Avoid
- Open-ended discovery questions when files already answer them
- Re-asking confirmed requirements
- Asking about vendored `roles/robertdebock.*` unless the user explicitly targets them