"""Record wrapper start/end status, not terminal PBS accounting."""
from pathlib import Path
import datetime
import json
import sys
import time

mode, runarg = sys.argv[1:3]
run = Path(runarg)
status_file = run / 'batch-lifecycle.json'
if mode == 'start':
    status_file.write_text(json.dumps({'utc_start': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                       'monotonic_start': time.monotonic(),
                                       'requested_nodes': 4, 'requested_ranks': 512,
                                       'requested_walltime_seconds': 5400,
                                       'maximum_requested_SU': 512 * 5400 / 3600,
                                       'internal_deadline_seconds': 5220,
                                       'scope': 'Wrapper status and elapsed time only; not final PBS state or billed SU.'}, indent=2) + '\n')
elif mode == 'finish':
    data = json.loads(status_file.read_text())
    data.update({'utc_wrapper_end': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'wrapper_exit_status': int(sys.argv[3]),
                 'post_run_source_hash_status': int(sys.argv[4]),
                 'wrapper_elapsed_seconds': time.monotonic() - data['monotonic_start']})
    data.pop('monotonic_start', None)
    data['limits'] = 'Review terminal PBS state and accounting separately; this wrapper snapshot is diagnostic only.'
    status_file.write_text(json.dumps(data, indent=2) + '\n')
else:
    raise SystemExit('mode must be start or finish')
