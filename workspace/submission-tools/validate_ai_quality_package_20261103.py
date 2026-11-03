#!/usr/bin/env python3
"""Verify complete staged accuracy replay and lossless evidence identities."""
from pathlib import Path
import hashlib
import json
from ai_release_context import review_path

W = Path(__file__).resolve().parents[1]
O = review_path(W)
E = O / 'package-files/AI_Task/logs/quality-20261103'
checks = []
def check(name, passed):
    assert passed, name
    checks.append(name)

replay = json.loads((O/'PACKAGED_QUALITY_REPLAY.json').read_text())
source = json.loads((O/'inputs/FULL_COMPARISON.json').read_text())
check('full_paired_replay_matches_source', replay['comparison'] == source['comparison'] and replay['reference']['correct'] == 9460 and replay['candidate']['correct'] == 9452)
check('all_questions_and_no_errors', all(replay[role]['n'] == 12032 and replay[role]['service_errors'] == 0 for role in ['reference','candidate']))
check('replay_is_local_pass', replay['status'] == 'LOCAL_FULLSET_GATE_PASS')
for line in (E/'SHA256SUMS').read_text().splitlines():
    digest, name = line.split('  ', 1)
    check('quality_checksum:' + name, hashlib.sha256((E/name).read_bytes()).hexdigest() == digest)
check('16_source_runs', len(json.loads((E/'RUNS.json').read_text())) == 16)
for path in [O/'package-files/AI_Task/logs/README.md', O/'package-files/AI_Task/job_scripts/README.md', O/'package-files/AI_Task/logs/FINAL_REPORT.md']:
    check('current_quality_claim:' + str(path.relative_to(O)), '99.915433%' in path.read_text())
report = dict(passed=True, checks=len(checks), checks_run=checks, full_quality_result=replay['comparison'], official_certification=False, question_count_per_role=12032, packed_response_records=24064, scoring_runtime='Python standard library; no GPU', no_serving_runtime_change=True)
(O/'QUALITY_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
print('Quality package validation passed:', len(checks), 'checks')
