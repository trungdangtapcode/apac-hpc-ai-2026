#!/usr/bin/env python3
"""Fail closed until root reviews the derived R4 controller and runtime plan."""
import json,sys,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent
review=json.loads((B/"R5_ROOT_REVIEW.json").read_text())
if review.get("status")!="PASS" or review.get("state")!="ROOT_REVIEWED_READY":
 print("R5_PREPARE_CHECK=FAIL_CLOSED: root review required");sys.exit(2)
import hashlib
proof=json.loads((B/'R3_PARENT_PROOF.json').read_text())
assert proof['state']=='ACTUAL_PARENT_R3_PASS_BOUND'
parent={}
for name,item in proof['files'].items():
 path=B/item['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'], 'Parent proof changed'
 parent[name]=json.loads(path.read_text())
assert parent['receipt.json']['job']==proof['job_id']
assert parent['result.json']['state']=='D5_STARTUP_READINESS_PASS'
assert parent['review.json']['job_id']==proof['job_id']
terminal=parent['review.json']['terminal']
assert terminal.get('exit_status', terminal.get('exit_code')) in (0,'0:0')
source=(B/"pinned-source/sgl-workspace/sglang/python/sglang/srt/server_args.py").read_text()
needle='Literal["null", "prefill", "decode"]'
start=source.find('disaggregation_mode:')
if needle not in source or start < 0 or '= "null"' not in source[start:start+700]: print("R4_PREPARE_CHECK=FAIL_CLOSED: pinned null default proof missing");sys.exit(2)
if "h100" in B.name:
 dep=json.loads((B/"H100_DEPENDENCY_BINDING.json").read_text())
 job=dep.get("parent_job_id")
 if dep.get("state")!="ROOT_BOUND_AFTEROK" or not isinstance(job,str) or not job.endswith(".pbs111") or not job.split(".",1)[0].isdigit():
  print("R5_PREPARE_CHECK=FAIL_CLOSED: H100 afterok parent binding is unresolved");sys.exit(2)
chunk=subprocess.run([sys.executable,str(B/"prefill_chunk_preflight.py")],capture_output=True,text=True)
if chunk.returncode:
 print("R5_PREPARE_CHECK=FAIL_CLOSED: source-backed CPU chunk preflight failed")
 print(chunk.stdout,chunk.stderr);sys.exit(2)
print(chunk.stdout.strip())
print("R5_PREPARE_CHECK=PASS: reviewed payload, actual R3 parent, and source-backed unified chunk verified")
