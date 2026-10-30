#!/usr/bin/env python3
"""
apply_patch.py <path_to_hmc.py> <patch_name>

Applies a single named patch to the tessia-baselib hmc.py file.
Each patch is idempotent: prints "PATCHED" if the change was made,
"ALREADY_APPLIED" if the new string was already present,
"NOT_FOUND" if neither old nor new string was found (upstream changed).

Exit codes:
  0 — success (patched, already applied, or not found — all non-fatal)
  1 — file could not be read/written
"""
import sys

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <hmc.py path> <patch_name>", file=sys.stderr)
    sys.exit(1)

path = sys.argv[1]
patch_name = sys.argv[2]

# ---------------------------------------------------------------------------
# Patch definitions: each entry is (old_string, new_string)
# The old_string is what the unpatched library contains.
# The new_string is the replacement.
# ---------------------------------------------------------------------------
PATCHES = {

    # -------------------------------------------------------------------------
    # Patch 1: LOGIN PROMPT
    # tessia waits for the literal "debirf-rescue login:" console message before
    # sending credentials. RHEL shows "<hostname> login:" instead.
    # The tuple format is (pattern_to_wait_for, command_to_send).
    # -------------------------------------------------------------------------
    "login_prompt": (
        "[('debirf-rescue login:', 'root'), ('Password:', os_passwd)]",
        "[(r'login:\\s*$', 'root'), ('Password:', os_passwd)]",
    ),

    # -------------------------------------------------------------------------
    # Patch 2: SHELL PROMPT PATTERN
    # After login, every command waits for MESSAGES_DEFAULT_PATTERN before
    # sending the next one. The debirf-specific pattern never matches RHEL.
    # -------------------------------------------------------------------------
    "shell_prompt": (
        "MESSAGES_DEFAULT_PATTERN = r'debirf-rescue:~#\\s*$'",
        "MESSAGES_DEFAULT_PATTERN = r'[#$]\\s*$'",
    ),

    # -------------------------------------------------------------------------
    # Patch 3: DASD LOAD STATUS TIMEOUT & 500,263
    # The default zhmcclient status_timeout (60 s) is too short for a live
    # disk to reach "operating" on s390x DASD. Raise timeout to configurable
    # (default 300 s), allow exceptions status, and catch HTTP 500,263 race.
    # -------------------------------------------------------------------------
    "dasd_load_timeout": (
        [
            """\
            guest_obj.load(
                load_address=self._normalize_address(boot_params['devicenr']),
                wait_for_completion=True,
                force=True)""",
            """\
            _status_timeout = boot_params.get('status_timeout', int(__import__('os').environ.get('TESSIA_LOAD_STATUS_TIMEOUT', 300)))
            try:
                guest_obj.load(
                    load_address=self._normalize_address(boot_params['devicenr']),
                    wait_for_completion=True,
                    force=True,
                    allow_status_exceptions=True,
                    status_timeout=_status_timeout
                )
            except zhmcclient.HTTPError as exc:
                # 500,263: HMC reports load failed but LPAR often boots
                # successfully anyway (race in HMC status reporting).
                if exc.http_status == 500 and exc.reason == 263:
                    self._logger.warning(
                        'HMC returned 500,263 for load - LPAR may still '
                        'have booted. Proceeding with netsetup.')
                else:
                    raise""",
        ],
        """\
            _status_timeout = boot_params.get('status_timeout', int(__import__('os').environ.get('TESSIA_LOAD_STATUS_TIMEOUT', 300)))
            try:
                guest_obj.load(
                    load_address=self._normalize_address(boot_params['devicenr']),
                    wait_for_completion=True,
                    force=True,
                    allow_status_exceptions=True,
                    operation_timeout=_status_timeout,
                    status_timeout=_status_timeout
                )
            except zhmcclient.OperationTimeout:
                # HMC job never reported completion but the LPAR may have
                # booted successfully (HMC async job tracking bug on some
                # CPC/HMC combinations). Proceed with netsetup.
                self._logger.warning(
                    'DASD load job timed out (operation_timeout=%s s) - '
                    'LPAR may still have booted. Proceeding with netsetup.',
                    _status_timeout)
            except zhmcclient.HTTPError as exc:
                # 500,263: HMC reports load failed but LPAR often boots
                # successfully anyway (race in HMC status reporting).
                if exc.http_status == 500 and exc.reason == 263:
                    self._logger.warning(
                        'HMC returned 500,263 for load - LPAR may still '
                        'have booted. Proceeding with netsetup.')
                else:
                    raise""",
    ),

    # -------------------------------------------------------------------------
    # Patch 4: SCSI LOAD STATUS TIMEOUT
    # The default zhmcclient status_timeout (60 s) is too short for a RHEL
    # live disk to reach "operating" on s390x. Raise it to 300 s and accept
    # "exceptions" as a valid interim status.
    # -------------------------------------------------------------------------
    "scsi_load_timeout": (
        """\
            guest_obj.scsi_load(
                load_address=self._normalize_address(boot_params['devicenr']),
                wwpn=boot_params['wwpn'],
                lun=boot_params['lun'],
                wait_for_completion=True,
                force=True
            )""",
        """\
            guest_obj.scsi_load(
                load_address=self._normalize_address(boot_params['devicenr']),
                wwpn=boot_params['wwpn'],
                lun=boot_params['lun'],
                wait_for_completion=True,
                force=True,
                allow_status_exceptions=True,
                status_timeout=300
            )""",
    ),

    # -------------------------------------------------------------------------
    # Patch 5: HMC 500,263 RACE CONDITION ON SCSI LOAD & CONFIGURABLE TIMEOUT
    # The HMC sometimes returns HTTP 500 reason 263 ("The load failed") even
    # when the LPAR booted successfully. Catch it and log a warning so
    # _do_netsetup / kexec can still proceed. Supports configurable status_timeout.
    # -------------------------------------------------------------------------
    "scsi_load_500_263": (
        [
            """\
            guest_obj.scsi_load(
                load_address=self._normalize_address(boot_params['devicenr']),
                wwpn=boot_params['wwpn'],
                lun=boot_params['lun'],
                wait_for_completion=True,
                force=True,
                allow_status_exceptions=True,
                status_timeout=300
            )""",
            """\
            try:
                guest_obj.scsi_load(
                    load_address=self._normalize_address(boot_params['devicenr']),
                    wwpn=boot_params['wwpn'],
                    lun=boot_params['lun'],
                    wait_for_completion=True,
                    force=True,
                    allow_status_exceptions=True,
                    status_timeout=300
                )
            except zhmcclient.HTTPError as exc:
                # 500,263: HMC reports load failed but LPAR often boots
                # successfully anyway (race in HMC status reporting).
                if exc.http_status == 500 and exc.reason == 263:
                    self._logger.warning(
                        'HMC returned 500,263 for scsi_load - LPAR may still '
                        'have booted. Proceeding with netsetup.')
                else:
                    raise""",
            """\
            guest_obj.scsi_load(
                load_address=self._normalize_address(boot_params['devicenr']),
                wwpn=boot_params['wwpn'],
                lun=boot_params['lun'],
                wait_for_completion=True,
                force=True
            )""",
        ],
        """\
            _status_timeout = boot_params.get('status_timeout', int(__import__('os').environ.get('TESSIA_LOAD_STATUS_TIMEOUT', 300)))
            try:
                guest_obj.scsi_load(
                    load_address=self._normalize_address(boot_params['devicenr']),
                    wwpn=boot_params['wwpn'],
                    lun=boot_params['lun'],
                    wait_for_completion=True,
                    force=True,
                    allow_status_exceptions=True,
                    status_timeout=_status_timeout
                )
            except zhmcclient.HTTPError as exc:
                # 500,263: HMC reports load failed but LPAR often boots
                # successfully anyway (race in HMC status reporting).
                if exc.http_status == 500 and exc.reason == 263:
                    self._logger.warning(
                        'HMC returned 500,263 for scsi_load - LPAR may still '
                        'have booted. Proceeding with netsetup.')
                else:
                    raise""",
    ),

    # -------------------------------------------------------------------------
    # Patch 6: WAIT FOR LPAR OPERATING STATUS BEFORE SENDING OS COMMANDS
    # After load completes, the HMC briefly leaves the LPAR in a
    # transitional status before it reaches "operating" or "exceptions".
    # Calling send_os_command during that window fails with HTTP 409,332
    # "The image is not in the operating or exceptions state."
    # This patch adds a polling loop in _do_netsetup that waits for
    # the LPAR to reach one of those states before opening the OS messages channel.
    # -------------------------------------------------------------------------
    "wait_for_operating": (
        [
            """\
        with Messages.connect(_get_guest_os_channel, self.host_name,
                              self.user, self.passwd) as receiver:
            self._logger.debug("Waiting for live image login prompt")
            self._send_commands(
                guest_obj,
                [(r'login:\\s*$', 'root'), ('Password:', os_passwd)],
                receiver)""",
            """\
        # Wait for LPAR to reach 'operating' or 'exceptions' before trying
        # to send OS commands (HTTP 409,332 if we call too early).
        _wait_deadline = time.monotonic() + 120
        while time.monotonic() < _wait_deadline:
            _lpar_status = guest_obj.get_property('status')
            if _lpar_status in ('operating', 'exceptions'):
                break
            self._logger.debug(
                "LPAR status is '%s', waiting for operating/exceptions ...",
                _lpar_status)
            time.sleep(5)
        else:
            self._logger.warning(
                "LPAR did not reach operating/exceptions within 120 s "
                "(status=%s); proceeding anyway", _lpar_status)
        with Messages.connect(_get_guest_os_channel, self.host_name,
                              self.user, self.passwd) as receiver:
            self._logger.debug("Waiting for live image login prompt")
            self._send_commands(
                guest_obj,
                [(r'login:\\s*$', 'root'), ('Password:', os_passwd)],
                receiver)""",
            # broken intermediate version: boot_params not in scope of _do_netsetup
            """\
        # Wait for LPAR to reach 'operating' or 'exceptions' before trying
        # to send OS commands (HTTP 409,332 if we call too early).
        _wait_timeout = boot_params.get('operating_timeout', boot_params.get('status_timeout', int(__import__('os').environ.get('TESSIA_OPERATING_TIMEOUT', 180))))
        _wait_deadline = time.monotonic() + _wait_timeout
        while time.monotonic() < _wait_deadline:
            _lpar_status = guest_obj.get_property('status')
            if _lpar_status in ('operating', 'exceptions'):
                break
            self._logger.debug(
                "LPAR status is '%s', waiting for operating/exceptions ...",
                _lpar_status)
            time.sleep(5)
        else:
            self._logger.warning(
                "LPAR did not reach operating/exceptions within %s s "
                "(status=%s); proceeding anyway", _wait_timeout, _lpar_status)
        with Messages.connect(_get_guest_os_channel, self.host_name, self.user, self.passwd) as receiver:
            self._logger.debug("Waiting for live image login prompt")
            self._send_commands(
                guest_obj,
                [(r'login:\\s*$', 'root'), ('Password:', os_passwd)],
                receiver)""",
        ],
        """\
        # Wait for LPAR to reach 'operating' or 'exceptions' before trying
        # to send OS commands (HTTP 409,332 if we call too early).
        _wait_timeout = int(__import__('os').environ.get('TESSIA_OPERATING_TIMEOUT', 180))
        _wait_deadline = time.monotonic() + _wait_timeout
        while time.monotonic() < _wait_deadline:
            _lpar_status = guest_obj.get_property('status')
            if _lpar_status in ('operating', 'exceptions'):
                break
            self._logger.debug(
                "LPAR status is '%s', waiting for operating/exceptions ...",
                _lpar_status)
            time.sleep(5)
        else:
            self._logger.warning(
                "LPAR did not reach operating/exceptions within %s s "
                "(status=%s); proceeding anyway", _wait_timeout, _lpar_status)
        with Messages.connect(_get_guest_os_channel, self.host_name, self.user, self.passwd) as receiver:
            self._logger.debug("Waiting for live image login prompt")
            self._send_commands(
                guest_obj,
                [(r'login:\\s*$', 'root'), ('Password:', os_passwd)],
                receiver)""",
    ),

    # -------------------------------------------------------------------------
    # Patch 8: REPLACE STOMP OS-MESSAGES CHANNEL WITH HMC REST POLLING
    # On some HMC/live-disk combinations (e.g. HMC 2.16.0 + Ubuntu debirf-rescue)
    # the STOMP notification broker accepts the TCP/TLS connection but never
    # responds to the STOMP CONNECT frame, causing ConnectFailedException.
    # The HMC REST API (list-os-messages + send_os_command) works reliably in
    # all cases and is used as a drop-in replacement for the STOMP channel.
    # This patch replaces the entire Messages.connect block with a REST-polling
    # receiver that has the same interface as the STOMP-based one.
    # -------------------------------------------------------------------------
    "rest_os_messages": (
        # old_string: the entire 'with Messages.connect(...)' block from tessia-baselib 1.4.6
        # including login, net-setup, netboot/kexec and post-kexec loop — all 8-space indented
        # under the 'with' (i.e. 12-space body lines).  Patch 1 (login_prompt) may already have
        # changed the login tuple, so we list both variants as candidates.
        [
            """\
        with Messages.connect(_get_guest_os_channel, self.host_name,
                              self.user, self.passwd) as receiver:
            self._logger.debug("Waiting for live image login prompt")
            self._send_commands(
                guest_obj,
                [('debirf-rescue login:', 'root'), ('Password:', os_passwd)],
                receiver)

            self._logger.debug("Setting up network on live image")
            self._send_commands(guest_obj, net_cmds, receiver)

            if net_boot:
                self._logger.debug("Performing netboot")
                self._execute_kexec(guest_obj, receiver,
                                    net_setup, net_boot)

                kexec_stime = time.monotonic()
                # wait a little to collect reboot logs and
                # check whether kexec is successful
                timeout = time.monotonic() + MSG_POST_LOAD_DURATION
                while timeout - time.monotonic() > 0:
                    for msg in receiver.get_messages(
                            timeout=max(1.0, min(MSG_POST_LOAD_DURATION,
                                                 timeout-time.monotonic()))):
                        self._logger.debug("%s: %s", msg['type'], msg['text'])
                        if time.monotonic() - kexec_stime <= KEXEC_WAIT_TIME :
                            if re.search(KEXEC_ERROR_PATTERN, msg['text']):
                                raise RuntimeError(
                                    "Cannot read /tmp/kernel or /tmp/initrd")
                        # check if we have a notification event in parameters
                        elif notify_boot and not notify_boot.is_set() :
                            self._logger.debug("Notify initial boot complete")
                            notify_boot.set()""",
            # variant after patch 1 (login_prompt) has already been applied
            """\
        with Messages.connect(_get_guest_os_channel, self.host_name,
                              self.user, self.passwd) as receiver:
            self._logger.debug("Waiting for live image login prompt")
            self._send_commands(
                guest_obj,
                [(r'login:\\s*$', 'root'), ('Password:', os_passwd)],
                receiver)

            self._logger.debug("Setting up network on live image")
            self._send_commands(guest_obj, net_cmds, receiver)

            if net_boot:
                self._logger.debug("Performing netboot")
                self._execute_kexec(guest_obj, receiver,
                                    net_setup, net_boot)

                kexec_stime = time.monotonic()
                # wait a little to collect reboot logs and
                # check whether kexec is successful
                timeout = time.monotonic() + MSG_POST_LOAD_DURATION
                while timeout - time.monotonic() > 0:
                    for msg in receiver.get_messages(
                            timeout=max(1.0, min(MSG_POST_LOAD_DURATION,
                                                 timeout-time.monotonic()))):
                        self._logger.debug("%s: %s", msg['type'], msg['text'])
                        if time.monotonic() - kexec_stime <= KEXEC_WAIT_TIME :
                            if re.search(KEXEC_ERROR_PATTERN, msg['text']):
                                raise RuntimeError(
                                    "Cannot read /tmp/kernel or /tmp/initrd")
                        # check if we have a notification event in parameters
                        elif notify_boot and not notify_boot.is_set() :
                            self._logger.debug("Notify initial boot complete")
                            notify_boot.set()""",
        ],
        """\
        # Use HMC REST polling for OS messages instead of the STOMP channel.
        # stomp.py / HMC STOMP broker compatibility issues make STOMP unreliable;
        # the REST API works on all tested HMC versions.
        class _RestOsMessages:
            \"\"\"Minimal Messages-compatible receiver backed by HMC REST polling.\"\"\"
            def __init__(self, lpar_obj):
                self._lpar = lpar_obj
                self._seen_seq = -1
            def get_messages(self, timeout=60.0):
                import time as _time
                deadline = _time.monotonic() + timeout
                while _time.monotonic() < deadline:
                    try:
                        resp = self._lpar.manager.session.get(
                            self._lpar.uri + '/operations/list-os-messages')
                        msgs = resp.get('os-messages', [])
                    except Exception:
                        msgs = []
                    new = [m for m in msgs
                           if m.get('sequence-number', 0) > self._seen_seq]
                    if new:
                        self._seen_seq = max(
                            m.get('sequence-number', 0) for m in new)
                        return [{'type': 'OS message',
                                 'text': m.get('message-text', '')}
                                for m in new]
                    _time.sleep(1)
                return []
        _rest_recv = _RestOsMessages(guest_obj)
        self._logger.debug("Waiting for live image login prompt (REST polling)")
        self._send_commands(
            guest_obj,
            [(r'login:\\s*$', 'root'), ('Password:', os_passwd)],
            _rest_recv)

        self._logger.debug("Setting up network on live image")
        self._send_commands(guest_obj, net_cmds, _rest_recv)

        if net_boot:
            self._logger.debug("Performing netboot")
            self._execute_kexec(guest_obj, _rest_recv,
                                net_setup, net_boot)

            kexec_stime = time.monotonic()
            # wait a little to collect reboot logs and
            # check whether kexec is successful
            timeout = time.monotonic() + MSG_POST_LOAD_DURATION
            while timeout - time.monotonic() > 0:
                for msg in _rest_recv.get_messages(
                        timeout=max(1.0, min(MSG_POST_LOAD_DURATION,
                                             timeout-time.monotonic()))):
                    self._logger.debug("%s: %s", msg['type'], msg['text'])
                    if time.monotonic() - kexec_stime <= KEXEC_WAIT_TIME :
                        if re.search(KEXEC_ERROR_PATTERN, msg['text']):
                            raise RuntimeError(
                                "Cannot read /tmp/kernel or /tmp/initrd")
                    # check if we have a notification event in parameters
                    elif notify_boot and not notify_boot.is_set() :
                        self._logger.debug("Notify initial boot complete")
                        notify_boot.set()""",
    ),

    # -------------------------------------------------------------------------
    # Patch 7: RETRY SEND_OS_COMMAND ON HTTP 409,332
    # Right after the live OS displays the login prompt, the HMC status monitor
    # may briefly report that the LPAR is not yet in 'operating' or 'exceptions'
    # state, causing send_os_command to fail with HTTP 409,332.
    # Retrying allows the HMC to update its status and accept the command.
    # -------------------------------------------------------------------------
    "send_os_cmd_retry": (
        [
            """\
                for chunk in _string_to_chunks(cmd):
                    guest_obj.send_os_command(chunk)""",
        ],
        """\
                _send_deadline = time.monotonic() + int(__import__('os').environ.get('TESSIA_SEND_CMD_TIMEOUT', 180))
                for chunk in _string_to_chunks(cmd):
                    while True:
                        try:
                            guest_obj.send_os_command(chunk)
                            break
                        except zhmcclient.HTTPError as exc:
                            if exc.http_status == 409 and exc.reason == 332 and time.monotonic() < _send_deadline:
                                self._logger.debug("LPAR not in operating state yet (HTTP 409,332); retrying send_os_command in 3s ...")
                                time.sleep(3)
                                continue
                            raise""",
    ),
}

if patch_name not in PATCHES:
    print(f"Unknown patch name: {patch_name}", file=sys.stderr)
    print(f"Available patches: {', '.join(PATCHES)}", file=sys.stderr)
    sys.exit(1)

old, new = PATCHES[patch_name]
old_candidates = [old] if isinstance(old, str) else list(old)

try:
    with open(path) as f:
        content = f.read()
except OSError as exc:
    print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
    sys.exit(1)

if new in content or (patch_name == "scsi_load_timeout" and PATCHES["scsi_load_500_263"][1] in content):
    print(f"ALREADY_APPLIED: {patch_name}")
    sys.exit(0)

matched_old = None
for candidate in old_candidates:
    if candidate in content:
        matched_old = candidate
        break

if not matched_old:
    print(f"NOT_FOUND: {patch_name} — old string not present; library may have changed upstream")
    sys.exit(0)

try:
    with open(path, "w") as f:
        f.write(content.replace(matched_old, new, 1))
except OSError as exc:
    print(f"ERROR: cannot write {path}: {exc}", file=sys.stderr)
    sys.exit(1)

print(f"PATCHED: {patch_name}")
