"""Read-only final evidence review for existing job23906; no job submission."""
import datetime
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
OUT = Path(__file__).resolve().parent
api = runpy.run_path(str(ROOT / 'serving-tuning/review-n54.py'))
result = dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              job='23906', state='INCOMPLETE', accuracy_verified=False,
              new_jobs_submitted=False)
status = subprocess.check_output(['sacct', '-X', '-n', '-P', '-j',
    '23778,23839,23906', '--format=JobID,State,ExitCode,Start,End'], text=True)
(OUT / 'terminal-accounting.txt').write_text(status)
statuses = {f[0]: dict(zip(['job', 'state', 'exit', 'start', 'end'], f))
            for row in status.splitlines() if (f := row.split('|')) and f[0]}
result['scheduler'] = statuses
seal = ROOT / 'runs/23906/artifact-manifest.json'
if statuses.get('23906', {}).get('state') == 'COMPLETED' and seal.exists():
    assert statuses['23906']['exit'] == '0:0'
    # Recheck sealed metric/raw request evidence and both independently run controls.
    points = {job: api['point'](ROOT, job, 52) for job in ('23778', '23839', '23906')}
    actual = points['23906']
    assert all(actual['normalized_protocol'] == points[j]['normalized_protocol']
               for j in ('23778', '23839'))
    # Recheck submitted/frozen payloads, stored script and actual derived graphs.
    runpy.run_path(str(OUT / 'audit-runtime.py'))
    runtime = json.loads((OUT / 'runtime-review.json').read_text())
    assert runtime['mnnvl_ranks'] == runtime['nixl_ucx_ranks'] == list(range(8))
    assert runtime['pair_warmup_complete_at_snapshot'] is True
    means = {key: sum(points[j]['metrics'][key] for j in ('23778', '23839')) / 2
             for key in ('good_tokens_s', 'ttft_ms', 'itl_ms')}
    result.update(state='MEASURED_PASS_SLA' if actual['metrics']['sla_pass'] else 'MEASURED_FAIL_SLA',
                  runs={j: {k: v for k, v in p.items() if k not in (
                      'server_args', 'normalized_protocol', 'payload_files')}
                        for j, p in points.items()},
                  baseline_mean=means,
                  vs_each_baseline={j: api['metric_delta'](actual['metrics'], points[j]['metrics'])
                                    for j in ('23778', '23839')},
                  vs_baseline_mean=api['metric_delta'](actual['metrics'], means),
                  runtime_review='runtime-review.json',
                  interpretation='Single chunk CLI change also changes prefill graph4096->8192; '
                                 'engine seed unpinned. No isolated scheduling claim or promotion.')
else:
    result['reason'] = 'Waiting for terminal scheduler status and watcher artifact seal.'
(OUT / 'chunk8192-final-review.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
