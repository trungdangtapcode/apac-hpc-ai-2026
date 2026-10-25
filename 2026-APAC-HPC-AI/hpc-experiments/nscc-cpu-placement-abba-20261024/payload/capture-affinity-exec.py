#!/usr/bin/env python3
"""Capture a launcher's singleton CPU mask, then exec one MPI application rank."""


import argparse
import glob
import json
import os
from pathlib import Path
import shutil
import stat
import sys


def diagnostic(**fields):
    record = {"event": "apac_affinity_exec", "pid": os.getpid(),
              "pmi_rank": os.environ.get("PMI_RANK"), **fields}
    payload = ("APAC_AFFINITY_EXEC_JSON " +
               json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n").encode()
    if len(payload) > 2048:
        payload = b'APAC_AFFINITY_EXEC_JSON {"success":false,"error":"diagnostic_overflow"}\n'
    written = os.write(2, payload)
    if written != len(payload):
        raise OSError("short write while emitting launch-affinity diagnostic")


def topology(cpu):
    root = Path(f"/sys/devices/system/cpu/cpu{cpu}/topology")
    result = {"package": None, "core": None, "numa_nodes": []}
    for key, filename in (("package", "physical_package_id"), ("core", "core_id")):
        try:
            result[key] = int((root / filename).read_text(encoding="ascii").strip())
        except (OSError, ValueError):
            pass
    try:
        result["numa_nodes"] = sorted(
            int(Path(path).name[4:])
            for path in glob.glob(f"/sys/devices/system/cpu/cpu{cpu}/node[0-9]*")
            if Path(path).name[4:].isdigit())
    except (OSError, ValueError):
        result["numa_nodes"] = []
    return result


def resolve_application(command):
    original = command[0]
    if os.sep in original:
        path = Path(original)
        if not path.is_absolute():
            path = Path.cwd() / path
    else:
        found = shutil.which(original)
        if not found:
            raise ValueError(f"application executable not found on PATH: {original}")
        path = Path(found)
    path = path.resolve(strict=True)
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or not os.access(path, os.X_OK):
        raise ValueError(f"application is not an executable regular file: {path}")
    return str(path), command


def main(argv):
    if "--" not in argv:
        print("usage: capture-affinity-exec.py --library /absolute/lib.so -- APP [ARG ...]",
              file=sys.stderr)
        return 2
    divider = argv.index("--")
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--library", required=True)
    options = parser.parse_args(argv[:divider])
    command = argv[divider + 1:]
    if not command:
        parser.error("missing application after --")

    inherited_preload = os.environ.get("LD_PRELOAD", "")
    if inherited_preload:
        diagnostic(success=False, error="refusing_nonempty_inherited_LD_PRELOAD")
        return 125

    supplied_library = Path(options.library)
    if not supplied_library.is_absolute():
        diagnostic(success=False, error="library_path_must_be_absolute")
        return 125
    try:
        library = supplied_library.resolve(strict=True)
        library_info = library.stat()
        if not stat.S_ISREG(library_info.st_mode) or not os.access(library, os.R_OK):
            raise ValueError("library is not a readable regular file")
        app_path, app_argv = resolve_application(command)
    except (OSError, ValueError) as error:
        diagnostic(success=False, error=str(error))
        return 125

    try:
        cpus = sorted(os.sched_getaffinity(0))
    except (AttributeError, OSError) as error:
        diagnostic(success=False, error=f"cannot_capture_affinity:{error}")
        return 125
    if len(cpus) != 1:
        diagnostic(success=False, launch_cpus=cpus, error="launcher_mask_not_single_cpu")
        return 125

    cpu = cpus[0]
    record = {"success": True, "launch_cpus": cpus, "launch_cpu": cpu,
              "topology": topology(cpu), "library": str(library),
              "application": app_path}
    diagnostic(**record)

    child_env = os.environ.copy()
    child_env["APAC_LAUNCH_CPU"] = str(cpu)
    child_env["APAC_PRESERVE_AFFINITY"] = "1"
    child_env["LD_PRELOAD"] = str(library)
    try:
        os.execve(app_path, app_argv, child_env)
    except OSError as error:
        diagnostic(success=False, error=f"execve_failed:{error}",
                   launch_cpus=cpus, launch_cpu=cpu)
        return 127


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
