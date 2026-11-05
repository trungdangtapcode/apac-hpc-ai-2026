#!/usr/bin/env python3
"""Read only MPI rank/host/OS-affinity probe; no memory-policy manipulation."""
import json
import os
import socket

rank = int(os.environ['OMPI_COMM_WORLD_RANK'])
print('RANK_DENSITY_PROBE\t' + json.dumps({
    'rank': rank,
    'hostname': socket.gethostname(),
    'affinity_cpu_ids': sorted(os.sched_getaffinity(0))
}, sort_keys=True), flush=True)
