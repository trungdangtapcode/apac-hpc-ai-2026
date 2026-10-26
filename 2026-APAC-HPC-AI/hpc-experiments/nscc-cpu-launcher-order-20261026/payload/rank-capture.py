#!/usr/bin/env python3
"""Write one plain-Python launcher-entry observation per PMI rank."""
from __future__ import print_function
import json
import os
import socket
import sys

def main():
    output = sys.argv[1]
    value = os.environ.get("PMI_RANK")
    if value is None or not value.isdigit():
        sys.stderr.write("missing or nonnumeric PMI_RANK\n")
        return 2
    rank = int(value)
    try:
        cpus = sorted(os.sched_getaffinity(0))
        status = 0
        error = None
    except Exception as exc:
        cpus = None
        status = -1
        error = "%s: %s" % (type(exc).__name__, str(exc))
    row = {"phase": "python_entry", "pmi_rank": rank,
           "host": socket.gethostname(), "affinity_status": status,
           "affinity_error": error, "cpus": cpus}
    path = os.path.join(output, "rank-%04d.json" % rank)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, 0o600)
    try:
        data = (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        os.write(fd, data)
    finally:
        os.close(fd)
    return 0

if __name__ == "__main__":
    sys.exit(main())
