#!/usr/bin/env python3
"""Gate S44 on actual two-pass repeat stability; report old-reference identity without gating."""
import hashlib,json,sys
from pathlib import Path
actual_path=Path(sys.argv[1]); old_path=Path(sys.argv[2]); binding_path=Path(__file__).with_name('accepted-reference-binding.json')
binding=json.loads(binding_path.read_text()); old_hash=hashlib.sha256(old_path.read_bytes()).hexdigest()
if old_hash!=binding.get('reference_file_sha256') or old_hash!=binding.get('accepted_reference_sha256'):
 raise SystemExit('informational parent reference file/hash binding mismatch')
actual=json.loads(actual_path.read_text()); old=json.loads(old_path.read_text())
if not actual.get('passed'): raise SystemExit('new target result is not passed')
if set(actual.get('stages',{}))!={'target-a','target-b'}: raise SystemExit('expected target-a and target-b')
if len(actual.get('cases',[]))!=4: raise SystemExit('expected four exact cases')
count=0; repeats=True
for idx,case in enumerate(actual['cases']):
 a=actual['stages']['target-a'][idx]; b=actual['stages']['target-b'][idx]
 if a.get('name')!=case.get('name') or b.get('name')!=case.get('name') or a.get('request')!=b.get('request'):
  raise SystemExit(f'exact request/case mismatch: {case.get("name")}')
 if a.get('observed')!=b.get('observed'):
  repeats=False
  raise SystemExit(f'target-a/target-b output IDs or finish reason differ: {case.get("name")}')
 obs=a['observed']; ids=obs.get('output_ids')
 if not isinstance(ids,list) or len(ids)!=200 or (obs.get('finish_reason') or {}).get('type')!='length' or obs.get('finish_reason',{}).get('length')!=200:
  raise SystemExit(f'exactly 200 actual IDs and length finish required: {case.get("name")}')
 count+=len(ids)*2
if count!=1600: raise SystemExit(f'exactly 1600 actual IDs required across both passes; got {count}')
old_matches=True
try:
 for stage in ('target-a','target-b'):
  for a,b in zip(actual['stages'][stage],old['stages'][stage]):
   if a.get('request')!=b.get('request') or a.get('observed')!=b.get('observed'): old_matches=False
except (KeyError,TypeError): old_matches=False
print(json.dumps({'state':'PASS','exact_repeat_stability':True,'actual_output_ids_checked':count,'cases':4,'passes':2,
 'historical_25585_identity_match':old_matches,'historical_25585_identity_is_acceptance_gate':False},indent=2))
