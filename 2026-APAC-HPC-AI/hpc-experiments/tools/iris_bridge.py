"""Run a small Python script through the interactive Iris login and return JSON.

This bridge owns only the local SSH child it starts. It does not inspect local
or remote environments, retain terminal output, or manage SSH control sockets.
"""

import base64
import hashlib
import json
import re
import secrets
import time
from pathlib import Path

import pexpect


DEFAULT_HELPER = Path(__file__).with_name("iris-interactive.sh")
MAX_BODY_BYTES = 1024 * 1024
MAX_REPLY_BYTES = 2 * 1024 * 1024
INPUT_CHUNK_CHARS = 900
OUTPUT_CHUNK_CHARS = 1000
MAX_BANNER_BYTES = 64 * 1024
MAX_TRAILER_BYTES = 64 * 1024
READ_SIZE = 4096

_CSI = rb"(?:\x1b\[[0-?]*[ -/]*[@-~])*"
_IRIS_PROMPT = re.compile(
    _CSI + rb"rdmaworkshop30" + _CSI + rb"@" + _CSI
    + rb"login[0-9]+" + _CSI + rb"[^\r\n]{0,256}[#$>] ?" + _CSI
)
_BEGIN_PREFIX = b"__IRIS_JSON_BEGIN__"
_CHUNK_PREFIX = b"__IRIS_JSON_CHUNK__"
_END_PREFIX = b"__IRIS_JSON_END__"


class IrisBridgeError(RuntimeError):
    """A bounded, non-sensitive bridge protocol or session failure."""


def _json_constant(value):
    raise ValueError("non-standard JSON constant: " + value)


def _wire_lines(body, nonce):
    """Build a small heredoc driver; the submitted body travels in short base64 lines."""
    if not isinstance(body, str):
        raise TypeError("body must be Python source text")
    source = body.encode("utf-8")
    if len(source) > MAX_BODY_BYTES:
        raise IrisBridgeError("Python input exceeds the 1 MiB limit")
    encoded = base64.b64encode(source).decode("ascii")
    parts = [encoded[i:i + INPUT_CHUNK_CHARS]
             for i in range(0, len(encoded), INPUT_CHUNK_CHARS)] or [""]
    lines = [
        "python3 - <<'__IRIS_BRIDGE_SCRIPT__'",
        "import base64, hashlib, json",
        "_nonce = " + repr(nonce),
        "_parts = (",
    ]
    lines.extend("    " + repr(part) + "," for part in parts)
    lines.extend([
        ")",
        "_source = base64.b64decode(''.join(_parts), validate=True)",
        "_scope = {'__name__': '__iris_bridge_body__'}",
        "exec(compile(_source.decode('utf-8'), '<iris-bridge-body>', 'exec'), _scope, _scope)",
        "if 'result' not in _scope:",
        "    raise RuntimeError('bridge body must define result')",
        "_value = _scope['result']",
        "if not isinstance(_value, (dict, list)):",
        "    raise TypeError('result must be a JSON object or array')",
        "_payload = json.dumps(_value, ensure_ascii=False, allow_nan=False,",
        "                      separators=(',', ':')).encode('utf-8')",
        "if len(_payload) > " + str(MAX_REPLY_BYTES) + ":",
        "    raise ValueError('JSON reply exceeds the 2 MiB limit')",
        "_digest = hashlib.sha256(_payload).hexdigest()",
        "_encoded = base64.b64encode(_payload).decode('ascii')",
        "_chunk_size = " + str(OUTPUT_CHUNK_CHARS),
        "_chunks = [_encoded[i:i + _chunk_size] for i in range(0, len(_encoded), _chunk_size)]",
        "print('__IRIS_JSON_BEGIN__ nonce=%s bytes=%d chunks=%d sha256=%s' %",
        "      (_nonce, len(_payload), len(_chunks), _digest), flush=True)",
        "for _index, _chunk in enumerate(_chunks):",
        "    print('__IRIS_JSON_CHUNK__ nonce=%s index=%d data=%s' %",
        "          (_nonce, _index, _chunk), flush=True)",
        "print('__IRIS_JSON_END__ nonce=%s' % _nonce, flush=True)",
        "__IRIS_BRIDGE_SCRIPT__",
    ])
    if any(len(line) > 1000 for line in lines):
        raise AssertionError("heredoc line exceeds the PTY-safe 1000 character bound")
    return lines


def _parse_frame(lines, nonce):
    """Validate one complete nonce-bound frame and decode its JSON payload."""
    begin_re = re.compile(
        rb"^__IRIS_JSON_BEGIN__ nonce=" + nonce.encode("ascii")
        + rb" bytes=([0-9]+) chunks=([0-9]+) sha256=([0-9a-f]{64})$"
    )
    chunk_re = re.compile(
        rb"^__IRIS_JSON_CHUNK__ nonce=" + nonce.encode("ascii")
        + rb" index=([0-9]+) data=([A-Za-z0-9+/=]*)$"
    )
    end_line = (_END_PREFIX + b" nonce=" + nonce.encode("ascii"))

    normalized = [line.rstrip(b"\r") for line in lines]
    nonce_bytes = nonce.encode("ascii")
    saw_begin = False
    for line in normalized:
        if line.startswith(_BEGIN_PREFIX):
            saw_begin = True
        elif (line.startswith((_CHUNK_PREFIX, _END_PREFIX))
              and b"nonce=" + nonce_bytes in line and not saw_begin):
            raise IrisBridgeError("out-of-order JSON frame marker")
    begins = [i for i, line in enumerate(normalized) if line.startswith(_BEGIN_PREFIX)]
    if len(begins) != 1:
        raise IrisBridgeError("missing or duplicate JSON frame header")
    start = begins[0]
    header = begin_re.fullmatch(normalized[start])
    if not header:
        raise IrisBridgeError("malformed JSON frame header")
    byte_count, chunk_count, digest = (int(header.group(1)), int(header.group(2)),
                                       header.group(3).decode("ascii"))
    if not 0 < byte_count <= MAX_REPLY_BYTES:
        raise IrisBridgeError("JSON frame byte count is outside the limit")
    expected_chunks = (4 * ((byte_count + 2) // 3) + OUTPUT_CHUNK_CHARS - 1) // OUTPUT_CHUNK_CHARS
    if chunk_count != expected_chunks or chunk_count < 1:
        raise IrisBridgeError("JSON frame chunk count is inconsistent")

    encoded = []
    cursor = start + 1
    for index in range(chunk_count):
        if cursor >= len(normalized):
            raise IrisBridgeError("truncated JSON frame")
        match = chunk_re.fullmatch(normalized[cursor])
        if not match:
            raise IrisBridgeError("malformed or out-of-order JSON frame chunk")
        if int(match.group(1)) != index:
            raise IrisBridgeError("duplicate or out-of-order JSON frame chunk")
        chunk = match.group(2)
        if len(chunk) > OUTPUT_CHUNK_CHARS:
            raise IrisBridgeError("JSON frame chunk exceeds the limit")
        encoded.append(chunk)
        cursor += 1
    if cursor >= len(normalized) or normalized[cursor] != end_line:
        raise IrisBridgeError("missing or malformed JSON frame terminator")
    cursor += 1
    if any(line.startswith((_BEGIN_PREFIX, _CHUNK_PREFIX, _END_PREFIX)) for line in normalized[cursor:]):
        raise IrisBridgeError("duplicate or unexpected JSON frame marker")

    try:
        payload = base64.b64decode(b"".join(encoded), validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise IrisBridgeError("invalid base64 JSON frame") from exc
    if len(payload) != byte_count:
        raise IrisBridgeError("JSON frame byte count mismatch")
    if hashlib.sha256(payload).hexdigest() != digest:
        raise IrisBridgeError("JSON frame SHA-256 mismatch")
    try:
        value = json.loads(payload.decode("utf-8"), parse_constant=_json_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise IrisBridgeError("framed reply is not valid JSON") from exc
    if not isinstance(value, (dict, list)):
        raise IrisBridgeError("framed reply is not a JSON object or array")
    return value


def _read_frame_and_prompt(child, nonce, deadline):
    """Read bounded protocol lines through the next Iris prompt; never persist output."""
    pending = bytearray()
    lines = []
    frame_started = False
    frame_ended = False
    before_bytes = 0
    frame_bytes = 0
    after_end = bytearray()

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise IrisBridgeError("timed out waiting for the framed JSON reply")
        try:
            data = child.read_nonblocking(READ_SIZE, timeout=remaining)
        except pexpect.TIMEOUT:
            raise IrisBridgeError("timed out waiting for the framed JSON reply") from None
        except pexpect.EOF:
            raise IrisBridgeError("Iris session closed before returning framed JSON") from None
        pending.extend(data)
        if not frame_started and len(pending) > MAX_BANNER_BYTES:
            raise IrisBridgeError("pre-frame terminal output exceeded the limit")
        if frame_started and len(pending) > MAX_REPLY_BYTES * 2 + MAX_BANNER_BYTES:
            raise IrisBridgeError("framed terminal output exceeded the transport limit")
        if frame_ended:
            after_end.extend(data)
            if len(after_end) > MAX_TRAILER_BYTES:
                raise IrisBridgeError("unexpected output after JSON frame exceeded the limit")
            if _IRIS_PROMPT.search(bytes(after_end)):
                if any(marker in after_end for marker in (_BEGIN_PREFIX, _CHUNK_PREFIX, _END_PREFIX)):
                    raise IrisBridgeError("duplicate JSON frame output")
                return _parse_frame(lines, nonce)

        while b"\n" in pending:
            raw, _, rest = pending.partition(b"\n")
            pending = bytearray(rest)
            line = bytes(raw).rstrip(b"\r")
            if not frame_started:
                before_bytes += len(raw) + 1
                if before_bytes > MAX_BANNER_BYTES:
                    raise IrisBridgeError("pre-frame terminal output exceeded the limit")
                if line.startswith(_BEGIN_PREFIX):
                    frame_started = True
            else:
                if frame_ended:
                    if line.startswith((_BEGIN_PREFIX, _CHUNK_PREFIX, _END_PREFIX)):
                        raise IrisBridgeError("duplicate JSON frame output")
                else:
                    if line.startswith(_END_PREFIX):
                        frame_ended = True
                    elif line.startswith((_BEGIN_PREFIX, _CHUNK_PREFIX)):
                        pass
                    else:
                        raise IrisBridgeError("unexpected line inside JSON frame")
            lines.append(line)
            frame_bytes += len(line) + 1
            if frame_started and frame_bytes > MAX_REPLY_BYTES * 2 + MAX_BANNER_BYTES:
                raise IrisBridgeError("framed terminal output exceeded the transport limit")
            if frame_ended and pending:
                after_end.extend(pending)
                if len(after_end) > MAX_TRAILER_BYTES:
                    raise IrisBridgeError("unexpected output after JSON frame exceeded the limit")
                if any(marker in after_end for marker in (_BEGIN_PREFIX, _CHUNK_PREFIX, _END_PREFIX)):
                    raise IrisBridgeError("duplicate JSON frame output")
                if _IRIS_PROMPT.search(bytes(after_end)):
                    return _parse_frame(lines, nonce)


def _close_child(child, deadline):
    """Exit the current Iris shell and then only this bridge's local SSH process."""
    if child.isalive():
        try:
            child.sendline(b"exit")
            child.expect(pexpect.EOF, timeout=max(0.2, min(5.0, deadline - time.monotonic())))
        except (pexpect.TIMEOUT, pexpect.EOF, OSError):
            if child.isalive():
                try:
                    child.sendline(b"exit")
                    child.expect(pexpect.EOF, timeout=2.0)
                except (pexpect.TIMEOUT, pexpect.EOF, OSError):
                    pass
    if child.isalive():
        child.close(force=True)


def run_json(body, timeout=120, helper=DEFAULT_HELPER):
    """Run Python source remotely after the real Iris prompt and return its JSON result.

    The source must assign a JSON object or array to `result`. The SSH helper is
    launched without a remote command; no terminal banners or command output are
    returned or written to disk.
    """
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    helper = Path(helper).resolve(strict=True)
    nonce = secrets.token_hex(16)
    lines = _wire_lines(body, nonce)
    deadline = time.monotonic() + timeout
    child = pexpect.spawn("bash", [str(helper)], echo=False, timeout=timeout,
                          encoding=None, maxread=READ_SIZE)
    try:
        try:
            child.expect(_IRIS_PROMPT, timeout=max(0.2, deadline - time.monotonic()))
        except pexpect.TIMEOUT:
            raise IrisBridgeError("timed out before the Iris login prompt") from None
        except pexpect.EOF:
            raise IrisBridgeError("SSH helper exited before the Iris login prompt") from None
        if len(child.before or b"") > MAX_BANNER_BYTES:
            raise IrisBridgeError("login banner exceeded the limit")

        # Disable remote PTY echo before transferring the source line by line.
        child.sendline(b"stty -echo")
        try:
            child.expect(_IRIS_PROMPT, timeout=max(0.2, deadline - time.monotonic()))
        except pexpect.TIMEOUT:
            raise IrisBridgeError("timed out preparing the Iris terminal") from None
        except pexpect.EOF:
            raise IrisBridgeError("Iris session closed while preparing the terminal") from None
        if b"stty:" in (child.before or b""):
            raise IrisBridgeError("could not disable terminal echo")

        for line in lines:
            if len(line) > 1000:
                raise IrisBridgeError("input line exceeds the 1000 character PTY limit")
            if time.monotonic() >= deadline:
                raise IrisBridgeError("timed out transferring the Python source")
            child.sendline(line.encode("ascii"))
        result = _read_frame_and_prompt(child, nonce, deadline)
        return result
    finally:
        _close_child(child, deadline)

