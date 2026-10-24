"""Fail-closed CPU log gate for H200 prefill graph policy capacity initialization.

This validates resolved SGLang ServerArgs and initialized scheduler receipts for
prefill-0, prefill-1, and decode-0. It does not prove benchmark readiness,
output correctness, performance, or current scheduler state before logs exist.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
from typing import Any

ROLES = {
    "prefill-0": {"tp_size": 4, "ep_size": 1, "max_running_requests": 64,
                  "moe_runner_backend": "deep_gemm"},
    "prefill-1": {"tp_size": 4, "ep_size": 1, "max_running_requests": 64,
                  "moe_runner_backend": "deep_gemm"},
    "decode-0": {"tp_size": 8, "ep_size": 8, "max_running_requests": 256,
                 "moe_runner_backend": "hpc_ops"},
}
SERVER_FIELDS = (
    "dtype", "max_running_requests", "tp_size", "ep_size", "chunked_prefill_size",
    "moe_runner_backend", "disaggregation_mode", "cuda_graph_backend_prefill", "disable_prefill_cuda_graph",
    "speculative_algorithm", "speculative_draft_model_path", "speculative_num_steps",
    "speculative_eagle_topk", "speculative_num_draft_tokens", "enable_multi_layer_eagle",
)


class AuditError(ValueError):
    pass


def _value_for(line: str, field: str) -> Any:
    """Read one top-level ServerArgs field without matching nested field names."""
    matches = list(re.finditer(r"(?<![\w.])" + re.escape(field) + r"=", line))
    if len(matches) != 1:
        raise AuditError(f"missing or ambiguous ServerArgs field {field} ({len(matches)} matches)")
    start = matches[0].end()
    # Values required here are scalar or a flat integer list.
    if line.startswith("[", start):
        end = line.find("]", start)
        if end < 0:
            raise AuditError(f"malformed list value for ServerArgs field {field}")
        raw = line[start:end + 1]
    elif line.startswith(("'", '"'), start):
        quote = line[start]
        end = start + 1
        escaped = False
        while end < len(line):
            char = line[end]
            if char == quote and not escaped:
                end += 1
                break
            escaped = (char == "\\" and not escaped)
            if char != "\\":
                escaped = False
            end += 1
        if end > len(line) or line[end - 1] != quote:
            raise AuditError(f"unterminated string value for ServerArgs field {field}")
        raw = line[start:end]
    else:
        end = start
        while end < len(line) and line[end] not in ",)":
            end += 1
        raw = line[start:end].strip()
    try:
        return ast.literal_eval(raw)
    except (SyntaxError, ValueError) as error:
        if raw == "None":
            return None
        raise AuditError(f"malformed ServerArgs value for {field}: {raw[:80]!r}") from error


def _phase_config(line: str, phase: str) -> dict[str, Any]:
    marker = phase + "=PhaseConfig("
    positions = [m.start() for m in re.finditer(re.escape(marker), line)]
    if len(positions) != 1:
        raise AuditError(f"missing or ambiguous cuda_graph_config {phase} PhaseConfig")
    start = positions[0] + len(phase) + len("=PhaseConfig(")
    depth = 1
    quote = None
    escaped = False
    end = start
    while end < len(line) and depth:
        char = line[end]
        if quote:
            if char == quote and not escaped:
                quote = None
            escaped = char == "\\" and not escaped
            if char != "\\":
                escaped = False
        elif char in ("'", '"'):
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        end += 1
    if depth:
        raise AuditError(f"unterminated cuda_graph_config {phase} PhaseConfig")
    content = line[start:end - 1]
    result = {}
    for field in ("backend", "max_bs", "bs"):
        matches = list(re.finditer(r"(?<![\w.])" + field + r"=", content))
        if len(matches) != 1:
            raise AuditError(f"missing or ambiguous {phase} graph config {field}")
        result[field] = _value_for(content, field)
    return result


def _parse_server_args(line: str) -> dict[str, Any]:
    if "server_args=ServerArgs(" not in line:
        raise AuditError("not a resolved ServerArgs record")
    result = {field: _value_for(line, field) for field in SERVER_FIELDS}
    result["graph_config"] = {"prefill": _phase_config(line, "prefill")}
    return result


def _role_logs(artdir: Path, role: str) -> list[Path]:
    paths = {p for p in artdir.rglob(f"{role}.log") if p.is_file()}
    paths.update(p for p in artdir.rglob(f"task-{role}-*.log") if p.is_file())
    return sorted(paths)


def audit(artdir: Path, prefill_policy: str) -> dict[str, Any]:
    if prefill_policy not in ("auto", "disabled"):
        raise AuditError("prefill policy must be auto or disabled")
    if not artdir.is_dir():
        raise AuditError(f"artifact directory does not exist or is not a directory: {artdir}")

    errors: list[str] = []
    observations: dict[str, Any] = {}
    for role, expected in ROLES.items():
        logs = _role_logs(artdir, role)
        if not logs:
            errors.append(f"{role}: missing role log")
            continue
        args_records = []
        scheduler_records = []
        for path in logs:
            try:
                lines = path.read_text(errors="replace").splitlines()
            except OSError as error:
                errors.append(f"{role}: cannot read {path}: {error}")
                continue
            for number, line in enumerate(lines, 1):
                if "server_args=ServerArgs(" in line:
                    try:
                        args_records.append({"path": str(path), "line": number,
                                            "values": _parse_server_args(line)})
                    except AuditError as error:
                        errors.append(f"{role}: {path}:{number}: {error}")
                # In observed SGLang logs, this is emitted while initializing the scheduler.
                # Requiring the same line's positive token pool distinguishes an initialized
                # scheduler receipt from a requested/default ServerArgs capacity.
                if "max_total_num_tokens=" in line:
                    token_match = re.search(r"(?<![\w.])max_total_num_tokens=(\d+)(?=[,\s])", line)
                    cap_match = re.search(r"(?<![\w.])max_running_requests=(\d+)(?=[,\s])", line)
                    if token_match and cap_match:
                        scheduler_records.append({"path": str(path), "line": number,
                                                  "max_total_num_tokens": int(token_match[1]),
                                                  "max_running_requests": int(cap_match[1])})
        if not args_records:
            errors.append(f"{role}: no resolved ServerArgs record")
            continue
        unique_args = {json.dumps(item["values"], sort_keys=True) for item in args_records}
        if len(unique_args) != 1:
            errors.append(f"{role}: contradictory resolved ServerArgs records")
            continue
        values = args_records[0]["values"]
        observations[role] = {"server_args": args_records, "initialized_scheduler": scheduler_records}

        if not scheduler_records:
            errors.append(f"{role}: no initialized scheduler capacity receipt")
        elif any(item["max_total_num_tokens"] <= 0 for item in scheduler_records):
            errors.append(f"{role}: scheduler receipt has non-positive max_total_num_tokens")
        elif {item["max_running_requests"] for item in scheduler_records} != {expected["max_running_requests"]}:
            errors.append(f"{role}: initialized scheduler max_running_requests does not uniquely equal {expected['max_running_requests']}")

        checks = {
            "dtype": "bfloat16",
            "max_running_requests": expected["max_running_requests"],
            "tp_size": expected["tp_size"],
            "ep_size": expected["ep_size"],
            "chunked_prefill_size": 8192,
            "moe_runner_backend": expected["moe_runner_backend"],
            "disaggregation_mode": "decode" if role == "decode-0" else "prefill",
            "cuda_graph_backend_prefill": None if prefill_policy == "auto" else "disabled",
            "speculative_algorithm": None,
            "speculative_draft_model_path": None,
            "speculative_num_steps": None,
            "speculative_eagle_topk": None,
            "speculative_num_draft_tokens": None,
            "enable_multi_layer_eagle": False,
        }
        for field, wanted in checks.items():
            if values[field] != wanted:
                errors.append(f"{role}: ServerArgs {field}={values[field]!r}, expected {wanted!r}")

        expected_prefill_backend = (
            "disabled" if prefill_policy == "disabled" or role == "decode-0" else "breakable"
        )
        prefill_phase = values["graph_config"]["prefill"]
        if prefill_phase["backend"] != expected_prefill_backend:
            errors.append(f"{role}: initialized prefill graph config backend={prefill_phase['backend']!r}, expected {expected_prefill_backend!r}")
        if values["disable_prefill_cuda_graph"] is not False:
            errors.append(f"{role}: disable_prefill_cuda_graph must remain False; prefill policy is selected with cuda_graph_backend_prefill")

    return {
        "passed": not errors,
        "prefill_policy": prefill_policy,
        "roles": observations,
        "errors": errors,
        "scope": "CPU log gate for explicit resolved ServerArgs and initialized scheduler capacity across all roles; not current live scheduler state, full execution correctness, or performance.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artdir", type=Path, required=True)
    parser.add_argument("--prefill-policy", choices=("auto", "disabled"), required=True)
    args = parser.parse_args()
    try:
        result = audit(args.artdir, args.prefill_policy)
    except (AuditError, OSError, ValueError) as error:
        result = {"passed": False, "prefill_policy": args.prefill_policy,
                  "roles": {}, "errors": [str(error)],
                  "scope": "CPU log gate; no current live scheduler claim."}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
