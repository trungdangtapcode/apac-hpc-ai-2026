"""Record local wrapper lifecycle; this is not terminal PBS accounting."""
from pathlib import Path
import datetime
import json
import sys
import time

mode, runarg = sys.argv[1:3]
run = Path(runarg)
status_path = run / 'batch-lifecycle.json'
if mode == 'start':
    status_path.write_text(json.dumps({'utc_start': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                       'monotonic_start': time.monotonic(),
                                       'requested_nodes': 1, 'requested_ranks': 4,
                                       'requested_walltime_seconds': 180,
                                       'internal_deadline_seconds': 135,
                                       'nominal_requested_SU': 4 * 180 / 3600,
                                       'scope': 'Wrapper lifecycle only; not final PBS state or billed SU.'}, indent=2) + '\n')
elif mode == 'finish':
    data = json.loads(status_path.read_text())
    data.update({'utc_wrapper_end': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'wrapper_exit_status': int(sys.argv[3]),
                 'post_run_source_hash_status': int(sys.argv[4]),
                 'wrapper_elapsed_seconds': time.monotonic() - data['monotonic_start']})
    data.pop('monotonic_start', None)
    data['limits'] = 'A wrapper exit and elapsed time are diagnostic only; terminal PBS accounting must be reviewed separately.'
    status_path.write_text(json.dumps(data, indent=2) + '\n')
else:
    raise SystemExit('mode must be start or finish')
