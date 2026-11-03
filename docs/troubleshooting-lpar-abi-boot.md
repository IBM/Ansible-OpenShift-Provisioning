# Troubleshooting: ABI LPAR Boot via HMC / tessia-baselib

This document covers issues specific to the Agent-Based Installer (ABI) LPAR boot path,
where `boot_lpar_abi.py` uses `tessia-baselib` to load a live disk (Ubuntu debirf-rescue),
set up networking, and `kexec` into the RHCOS agent image.

---

## Architecture Overview

```
Ansible controller
  └─ boot_LPAR_abi role
       └─ boot_lpar_abi.py (on bastion)
            ├─ zhmcclient  → HMC REST API  (deactivate, DASD load)
            └─ tessia-baselib HypervisorHmc
                 ├─ DASD load  → Ubuntu debirf-rescue boots on LPAR
                 ├─ HMC REST list-os-messages  → read console output
                 ├─ HMC REST send-os-command   → type login/password/cmds
                 └─ kexec  → RHCOS agent boots on LPAR
```

The playbook runs `patch_tessia_baselib` **before** `boot_LPAR_abi` on every run,
ensuring all patches are applied even after a fresh `pip install tessia-baselib`.

---

## Known Issues and Fixes

### 1. STOMP notification channel broken (HMC 2.16.0 + Ubuntu debirf-rescue)

**Symptom**: `stomp.exception.ConnectFailedException` in boot log.

```
File ".../tessia/baselib/hypervisors/hmc/hmc.py", line 246, in _do_netsetup
    with Messages.connect(...) as receiver:
...
stomp.exception.ConnectFailedException
```

**Cause**: The HMC STOMP notification broker (port 61612) accepts the TCP/TLS connection
but never responds to the STOMP CONNECT frame on this HMC version + live disk combination.

**Fix (patch 8 — `rest_os_messages`)**: The entire `with Messages.connect(...)` block
is replaced with HMC REST polling via the `list-os-messages` endpoint. Applied automatically
by `roles/patch_tessia_baselib/files/apply_patch.py`.

---

### 2. Login fails — password sent as username (blank reprompt)

**Symptom** on HMC console:
```
debirf-rescue login:
 
Password:
<your-password>         ← password echoed as plain text
Login incorrect
```

**Cause**: An empty `send_os_command('')` was sent before the login sequence to
"reprompt" the login. Ubuntu interprets the blank as an empty username, immediately
asks for `Password:`, and then the real username `root` is sent as the password
(rejected), followed by the actual password sent as a shell command (echoed).

**Fix**: The reprompt `send_os_command('')` call was removed from `hmc.py`.
The `_send_commands` sequence now waits directly for `login:\s*$` without sending
anything first.

---

### 3. DASD load job timeout (not a real error)

**Symptom** in boot log:
```
WARNING - DASD load job timed out (operation_timeout=300 s) - LPAR may still have booted. Proceeding with netsetup.
```

**Cause**: The HMC async job for DASD load completes asynchronously. The LPAR boots
successfully but the HMC job object reports timeout before the LPAR reaches `operating`
status within `operation_timeout` seconds.

**Fix (patch 3 — `dasd_load_timeout`)**: `operation_timeout=_status_timeout` is passed
to `guest_obj.load()` and the resulting `zhmcclient.OperationTimeout` exception is
caught and converted to a warning. Boot continues normally.

---

### 4. Deactivate fails with HTTP 500,263

**Symptom** in boot log:
```
zhmcclient._exceptions.HTTPError: 500,263: The deactivate did not take place because
the target is currently in the operating state and the force flag was not set.
```

**Cause**: `lpar.deactivate()` requires `force=True` when the LPAR is in `operating`
state (e.g., running RHCOS from a previous install).

**Fix**: `boot_lpar_abi.py` now calls `_lpar.deactivate(wait_for_completion=True, force=True)`.

---

### 5. HMC session pool exhaustion

**Symptom**: `zhmcclient.Session.logon()` hangs indefinitely (no timeout, no error).
Standalone `logon()` test works fine initially but after several failed/killed runs
all new logons also block.

**Cause**: Each killed or crashed `boot_lpar_abi.py` process leaves an orphaned
`zhmcclient.Session` open on the HMC. After multiple attempts the HMC session limit
for the configured HMC user is reached.

**Fix**:
1. The `--deactivate_first` block in `boot_lpar_abi.py` now uses `try/finally` to
   guarantee `_session.logoff()` even if an exception occurs.
2. To recover immediately: log into the HMC GUI → **User Management** → your HMC user
   → **Active Sessions** → delete all sessions.
3. Alternatively wait 10–30 minutes for the HMC to expire idle sessions automatically.

---

### 6. Live disk password case sensitivity

**Symptom**: `Login incorrect` on every attempt despite using the value from
`vault_livedisk_root_pass`.

**Cause**: The password is case-sensitive. A single character case difference
(e.g., lowercase `i` vs uppercase `I`) causes all logins to fail.

**Fix**: Verify the exact password character-by-character. The correct value for the
Ubuntu debirf-rescue image used in this environment is stored in `secrets.yaml` as
`vault_livedisk_root_pass`. Use the HMC REST API to test manually:

```python
# Quick manual login test via HMC REST
import zhmcclient, urllib3, warnings, time
warnings.filterwarnings('ignore'); urllib3.disable_warnings()
s = zhmcclient.Session('hmc.example.com', 'HMC_USER', 'HMC_PASS', verify_cert=False)
s.logon()
c = zhmcclient.Client(s)
lp = c.cpcs.find(name='CPC').lpars.find(name='LPARNAME')
# Send username
lp.send_os_command('root')
time.sleep(3)
# Send candidate password
lp.send_os_command('CANDIDATE_PASSWORD')
time.sleep(6)
# Check response
resp = s.get(lp.uri + '/operations/list-os-messages')
for m in resp.get('os-messages', [])[-5:]:
    print(m.get('sequence-number'), repr(m.get('message-text', '').strip()))
s.logoff()
```

A successful login shows `Welcome to Ubuntu` and `debirf-rescue:~#`.
A failed login shows `Login incorrect`.

---

### 7. Node hostnames are short names instead of FQDNs

**Symptom**: `oc get nodes` shows `master-0` instead of `master-0.mycluster.example.com`.

**Cause**: The original `agent-config.yaml.j2` template emitted only
`env.cluster.nodes.control.hostname[item]` without appending the domain.

**Fix**: The template now emits the full FQDN:
```jinja2
hostname: "{{ env.cluster.nodes.control.hostname[item] }}.{{ env.cluster.networking.metadata_name }}.{{ env.cluster.networking.base_domain }}"
```

**Verification**: After running `prepare_configs`, check:
```bash
grep hostname ~/ansible_workdir/agent-config-backup.yaml
# Should show: master-0.mycluster.example.com
```

---

### 8. DASD rootDeviceHints missing (DASD storage type)

**Symptom**: OpenShift installer cannot find the installation disk on DASD-based LPARs.

**Cause**: The original `agent-config.yaml.j2` only generated `rootDeviceHints` for FCP
storage. DASD storage (used in non-DPM environments) was not handled.

**Fix**: The template now generates DASD `rootDeviceHints`:
```yaml
rootDeviceHints:
  deviceName: /dev/disk/by-path/ccw-0.0.{{ dev_num }}
```

Where `dev_num` is taken from `lpar.storage_group_1.dev_num` in the node's host_vars
(format: `4401`, without `0.0.` prefix — the template adds it).

---

### 9. `rd.dasd=` missing from kexec kernel command line

**Symptom**: RHCOS agent boots but cannot find the installation DASD (`/dev/dasda` absent).

**Cause**: The `genericdvd.prm.j2` template did not include `rd.dasd=` for DASD storage.
Without it, dracut does not activate the DASD channel.

**Fix**: `genericdvd.prm.j2` now appends `rd.dasd=0.0.{{ node.lpar.storage_group_1.dev_num }}`
when `storage_group_1.type == 'dasd'`.

---

### 10. HMC hostname not resolving from bastion

**Symptom**: `zhmcclient.Session` logon fails with connection timeout or DNS error
for the HMC hostname (e.g., `hmc.example.com`).

**Cause**: The bastion's BIND instance does not have a forwarder for the HMC's DNS
domain (e.g., `example.com`).

**Fix**: Set `env.bastion.networking.hmc_domain: example.com` in `all.yaml`,
replacing `example.com` with the actual DNS domain of your HMC hostname.
The `setup_bastion_services` role adds a forward-only BIND zone for that domain
pointing to `nameserver2` (the site DNS).

---

### 11. stomp.py version incompatibility

**Symptom**: ImportError or AttributeError in `zhmcclient/_notification.py`.

**Cause**: stomp.py 6.x broke the API used by `zhmcclient` for the STOMP notification
channel.

**Fix (patch — `install_tessia_baselib`)**: stomp.py is pinned to `4.1.24` in
`roles/install_tessia_baselib/tasks/main.yaml`. This is now a moot point since
STOMP is replaced entirely by REST polling (see issue 1), but the pin remains to
prevent future accidental upgrades.

---

## Configuration Reference

### `secrets.yaml` variables for LPAR boot

| Variable | Description |
|---|---|
| `vault_hmc_pass` | HMC user password (set in `hmc.auth.pass`) |
| `vault_livedisk_root_pass` | Root password of the Ubuntu debirf-rescue live disk |

### `host_vars/{node}.yaml` for DASD boot

```yaml
lpar:
  livedisk:
    livedisktype: dasd
    devicenr: "1a00"          # DASD address of the live (Ubuntu) disk
    livedisk_root_pass: "{{ vault_livedisk_root_pass }}"

  storage_group_1:
    type: dasd
    dev_num: "1b00"           # DASD address of the installation disk (NO 0.0. prefix)
```

### `all.yaml` for DASD + HMC DNS

```yaml
env:
  bastion:
    networking:
      hmc_domain: example.com   # Forward zone for HMC hostname resolution (domain of your HMC hostname)
```

---

## Patch Summary

All patches are applied by `roles/patch_tessia_baselib` on every playbook run.

| Patch name | What it fixes |
|---|---|
| `login_prompt` | Waits for `login:\s*$` instead of literal `debirf-rescue login:` |
| `shell_prompt` | Shell prompt pattern `[#$]\s*$` instead of `debirf-rescue:~#\s*$` |
| `dasd_load_timeout` | Passes `operation_timeout` to `guest_obj.load()`, catches `OperationTimeout` |
| `send_os_cmd_retry` | Retries `send_os_command` on HTTP 409,332 (LPAR not yet in operating state) |
| `rest_os_messages` | Replaces entire STOMP channel with HMC REST `list-os-messages` polling |
| `operating_wait` | Waits for LPAR to reach `operating` status before sending OS commands |
