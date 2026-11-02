#!/usr/bin/env python3
"""Check completion and service integrity; the paired quality ratio is a separate gate."""
from pathlib import Path
import hashlib
import json
import sys

root = Path(sys.argv[1])
run = json.loads((root / 'run.json').read_text())
summary = json.loads((root / 'summary.json').read_text())
records = [json.loads(line) for line in (root / 'responses.jsonl').read_text().splitlines() if line.strip()]
ids = run['selected_question_ids']
actual = [int(r['question_id']) for r in records]
checks = {
    'run_complete': run['status'] == summary['status'] == 'COMPLETE',
    'exact_coverage': len(actual) == len(ids) == len(set(actual)) and set(actual) == set(ids),
    'all_requests_successful': all(r['status'] == 'OK' and r['http_status'] == 200 for r in records),
    'responses_retained': all(isinstance(r['raw_response_body'], str) and r['completion_text'] is not None for r in records),
    'no_service_errors': summary['service_errors_in_denominator'] == 0,
    'no_deadline_skips': summary['not_started_deadline_records'] == 0,
}
result = {'passed': all(checks.values()), 'checks': checks,
          'question_count': len(ids), 'accuracy': summary['accuracy'],
          'correct': summary['correct'],
          'raw_responses_sha256': hashlib.sha256((root / 'responses.jsonl').read_bytes()).hexdigest(),
          'scope': 'complete error-free local measurement; no paired 99% ratio or official certification implied'}
print(json.dumps(result, indent=2))
raise SystemExit(0 if result['passed'] else 1)
