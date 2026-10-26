#!/usr/bin/env python3
"""Record launcher identity, then exec the probe (strace only for PMI rank 0)."""
from __future__ import print_function
import json
import os
import socket
import sys

def main(argv):
    if len(argv) != 6:
        sys.stderr.write("usage: rank-exec.py MODE RECORD_DIR PROBE STRACE NATIVE_DIR\n")
        return 2
    mode, record_dir, probe, strace, native_dir = argv[1:]
    if mode not in ("control", "rank0-straced"):
        sys.stderr.write("invalid arm mode\n")
        return 2
    value = os.environ.get("PMI_RANK", "")
    if not value.isdigit():
        sys.stderr.write("missing or nonnumeric PMI_RANK\n")
        return 2
    rank = int(value)
    trace_this_rank = mode == "rank0-straced" and rank == 0
    row = {
        "pmi_rank": rank,
        "host": socket.gethostname(),
        "pid": os.getpid(),
        "mode": "strace" if trace_this_rank else "native",
        "arm": mode,
    }
    path = os.path.join(record_dir, "rank-%04d.json" % rank)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except OSError as exc:
        sys.stderr.write("cannot create unique rank identity %s: %s\n" % (path, exc))
        return 3
    try:
        data = (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        written = os.write(fd, data)
        if written != len(data):
            sys.stderr.write("short identity record write\n")
            return 3
    finally:
        os.close(fd)
    if trace_this_rank:
        trace_path = os.path.join(record_dir, "rank-0000-affinity.strace")
        args = [strace, "-f", "-k", "-ttt",
                "-e", "trace=sched_setaffinity,sched_getaffinity",
                "-e", "signal=none", "-o", trace_path, "--", probe, native_dir]
    else:
        args = [probe, native_dir]
    os.execv(args[0], args)
    return 127

if __name__ == "__main__":
    sys.exit(main(sys.argv))
