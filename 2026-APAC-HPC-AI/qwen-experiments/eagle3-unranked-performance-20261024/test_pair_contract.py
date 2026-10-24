#!/usr/bin/env python3
"""CPU fixtures: validate matched source and fail-closed report behavior."""
import copy, json, subprocess, sys, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
S55=ROOT/'serving-tuning-10/s55-h200-eagle3-perf-control'
S56=ROOT/'serving-tuning-10/s56-h200-eagle3-perf-candidate'

a=json.loads((S55/'config.json').read_text()); b=json.loads((S56/'config.json').read_text())
metadata={'experiment','label','source_bundle','arm','speculation'}
normalize=lambda x:{k:v for k,v in x.items() if k not in metadata}
assert normalize(a)==normalize(b)
assert normalize(a)==normalize(copy.deepcopy(b))
bad=copy.deepcopy(b); bad['prefill_max_running_requests']=49
assert normalize(a)!=normalize(bad), 'CPU fixture failed to detect a changed common control'
assert (S55/'worker.sh').read_bytes()==(S56/'worker.sh').read_bytes()
assert (S55/'check-client-image.py').read_bytes()==(S56/'check-client-image.py').read_bytes()
assert 'st_mtime_ns' in (S55/'check-client-image.py').read_text() and 'st_ctime_ns' in (S55/'check-client-image.py').read_text()
assert (S55/'topology-job.sh').read_bytes()==(S56/'topology-job.sh').read_bytes()
review=json.loads((ROOT/'research-review-25862-20261024/REVIEW.json').read_text())
assert review['exact_output_gate']['state']=='FAIL'
# Empty output artifacts must fail the independent checker; this fixture is not GPU evidence.
with tempfile.TemporaryDirectory() as temp:
    p=subprocess.run([sys.executable,str(S55/'check-performance.py'),temp],capture_output=True,text=True)
    assert p.returncode!=0
    result=json.loads(p.stdout)
    assert result['state']=='FAIL'
replay=subprocess.run([sys.executable,str(HERE/'replay_actual_gate_fixtures.py')],capture_output=True,text=True)
assert replay.returncode==0, replay.stdout+'\n'+replay.stderr
replay_state=json.loads(replay.stdout)
assert replay_state['state']=='ACTUAL_GATE_FIXTURE_REPLAY_PASS' and replay_state['single_run_evidence'] is False
print('ACTUAL_CROSS_JOB_GATE_REPLAY_PASS (25862 + 25920 remain separate; no performance claim)')
print('CPU_PAIR_FIXTURES_PASS (no GPU evidence fabricated)')
