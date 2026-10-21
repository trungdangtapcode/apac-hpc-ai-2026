"""Request the bounded pre-score captures and label incomplete evidence honestly."""
import datetime
import json
from pathlib import Path
import sys
import time

artifact, placement = map(Path, sys.argv[1:])
folder = artifact / 'worker-locality'
folder.mkdir(exist_ok=True)
expected = {row.split()[0]: int(row.split()[2]) for row in placement.read_text().splitlines() if row.strip()}
(folder / 'request.json').write_text(json.dumps(dict(
    requested_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    phase='After pair warmup, before official client warmup/scoring')) + '\n')
deadline = time.monotonic() + 25
while time.monotonic() < deadline and not all((folder / (role + '.ready.json')).exists() for role in expected):
    time.sleep(1)
results = {}
for role, count in expected.items():
    path = folder / (role + '.ready.json')
    try:
        data = json.loads(path.read_text())
        snapshot = data.get('snapshot', {})
        uuids = {x['gpu_uuid'] for x in snapshot.get('matched_gpu_processes', [])}
        fields_present = all(x['allowed_local_cpu_intersection'] is not None
                             and x['gpu_numa_node'] not in (None, '-1')
                             for process in snapshot.get('processes', [])
                             for x in process['gpu_locality'])
        results[role] = dict(state=data['state'], expected_gpu_count=count,
                             matched_gpu_uuids=sorted(uuids), fields_present=fields_present,
                             thread_capture_truncated=snapshot.get('thread_capture_truncated', True),
                             ambiguous_gpu_pid_matches=snapshot.get('ambiguous_gpu_pid_matches', 0))
        results[role]['mapping_complete'] = (data['state'] == 'CAPTURE_COMPLETE' and len(uuids) == count
            and fields_present and not results[role]['thread_capture_truncated']
            and results[role]['ambiguous_gpu_pid_matches'] == 0)
    except (OSError, ValueError, KeyError) as error:
        results[role] = dict(state='CAPTURE_INCOMPLETE', mapping_complete=False, error_type=type(error).__name__)
summary = dict(phase='Before official client', roles=results,
               all_roles_mapping_complete=all(x['mapping_complete'] for x in results.values()),
               affinity_changed=False, scored_cpu_demand_collected=False,
               interpretation='Mapping evidence only, not CPU saturation, memory placement or performance causality.')
(folder / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary), flush=True)
