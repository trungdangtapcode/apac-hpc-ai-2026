#!/usr/bin/env python3
"""Per-MPI-rank anonymous first-touch and NUMA policy diagnostic."""
import ctypes
import json
import mmap
import os
import pathlib
import re
import subprocess
import sys
import tempfile


BYTES = 8 * 1024 * 1024


def atomic_json(path, data):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(data, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def fail(message):
    print("RANK_PROBE_ERROR: " + message, file=sys.stderr, flush=True)
    raise SystemExit(2)


def main():
    rank_text = os.environ.get("OMPI_COMM_WORLD_RANK")
    if rank_text is None:
        fail("OMPI_COMM_WORLD_RANK is missing; refusing to infer MPI rank")
    rank = int(rank_text)
    arm = os.environ.get("RANK_PROBE_ARM")
    root = os.environ.get("RANK_PROBE_ROOT")
    if arm not in ("inherited", "interleave") or not root:
        fail("RANK_PROBE_ARM/ROOT is unset or invalid")

    policy = subprocess.run(["numactl", "--show"], text=True, capture_output=True)
    if policy.returncode:
        fail("numactl --show failed: " + policy.stderr.strip())
    page_size = os.sysconf("SC_PAGE_SIZE")
    if BYTES % page_size:
        fail("8 MiB mapping is not a whole number of system pages")
    mapping = mmap.mmap(-1, BYTES+2*page_size, flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS,
                        prot=mmap.PROT_READ | mmap.PROT_WRITE)
    base = ctypes.addressof(ctypes.c_char.from_buffer(mapping))
    libc = ctypes.CDLL(None, use_errno=True)
    libc.mprotect.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
    libc.mprotect.restype = ctypes.c_int
    for guard in (base, base+page_size+BYTES):
        if libc.mprotect(guard, page_size, 0) != 0:
            fail("mprotect guard failed with errno %d" % ctypes.get_errno())
    address = base+page_size
    for offset in range(0, BYTES, page_size):
        mapping[page_size+offset] = (rank + offset // page_size) & 0xff

    target = "/proc/self/numa_maps"
    start_hex = format(address, "x")
    matches = []
    with open(target, "r") as stream:
        for line in stream:
            first = line.split(None, 1)[0]
            if first.lower() == start_hex.lower():
                matches.append(line.rstrip())
    if len(matches) != 1:
        fail("expected one exact /proc/self/numa_maps start-address line for "
             + start_hex + "; found " + str(len(matches)))
    fields = dict(re.findall(r"([A-Za-z0-9_]+)=([^ ]+)", matches[0]))
    node_pages = {key: int(value) for key, value in fields.items()
                  if re.fullmatch(r"N\d+", key)}
    page_count = sum(node_pages.values())
    if page_count != BYTES//page_size:
        fail("NUMA mapping accounting differs from exact touched-page count")
    allowed = sorted(os.sched_getaffinity(0))
    status = {}
    with open("/proc/self/status", "r") as stream:
        for line in stream:
            if line.startswith(("Cpus_allowed_list:", "Mems_allowed_list:")):
                key, value = line.split(":", 1)
                status[key] = value.strip()
    result = {
        "arm": arm, "mpi_rank": rank, "pid": os.getpid(),
        "numactl_show": policy.stdout.strip(),
        "allowed_cpu_affinity_list": allowed,
        "proc_status_allowed_masks": status,
        "mapping": {"address_hex": "0x" + start_hex, "requested_bytes": BYTES,
                    "page_size_bytes": page_size, "touched_pages": BYTES // page_size,
                    "numa_maps_line": matches[0], "numa_node_pages": node_pages,
                    "reported_node_page_total": page_count,
                    "reported_bytes_from_node_pages": page_count * page_size,
                    "exact_mapping_accounting": page_count == BYTES // page_size},
    }
    atomic_json(pathlib.Path(root) / arm / ("rank-%02d.json" % rank), result)
    print("RANK_PROBE_OK arm=%s rank=%d address=0x%s pages=%d mapped_bytes=%d" %
          (arm, rank, start_hex, page_count, page_count * page_size), flush=True)
    mapping.close()


if __name__ == "__main__":
    main()
