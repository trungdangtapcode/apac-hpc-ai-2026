#!/usr/bin/env python3
"""Finish the interrupted derived bundle, preserving all full-workload gates."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess
D=Path(__file__).resolve().parent;Q=D.parent;B=Q/'serving-tuning-11/s98-h200-shallow-eagle12';P=Q/'serving-tuning-11/s93-h200-tokenizer-off-warmfix';S=Q/'runs/25998/submitted-payload'
for name in ['verify-draft.py','draft-fingerprint.py']:shutil.copy2(S/name,B/name)
shutil.copytree(S/'draft-evidence',B/'draft-evidence',dirs_exist_ok=True)
p=B/'worker.sh';s=p.read_text();s=s.replace('if [[ ${QWEN_HAS_DRAFT:-0} == 1 ]]; then\n  [[ $role == decode ]] || { echo \'FATAL: shallow EAGLE3 draft is decode-only\'; exit 1; }','if [[ ${QWEN_HAS_DRAFT:-0} == 1 && $role == decode ]]; then');s=s.replace('--speculative-draft-attention-backend flashinfer)','--speculative-draft-attention-backend flashinfer --speculative-draft-model-quantization unquant)');p.write_text(s)
p=B/'headcheck-worker-drafts.py';s=p.read_text().replace('Require three role-local full-verification receipts with one parent identity.','Require the decode-only full-verification receipt with its pinned parent identity.');p.write_text(s)
p=B/'check-performance.py';s=(P/'check-performance.py').read_text();s=s.replace('import ast, hashlib, importlib.util, json, re, sys','import ast, hashlib, importlib.util, json, re, sys, subprocess')
s=s.replace('        if candidate:\n            required=',"        if candidate and role=='decode-0':\n            required=")
s=s.replace("'speculative_num_steps':2", "'speculative_num_steps':1").replace("'speculative_num_draft_tokens':3", "'speculative_num_draft_tokens':2")
s=s.replace("assert bound.get('state')=='PASS_ACTUAL_S59_CONTROL' and bound.get('control_job'), 'root-bound actual control verification missing'", "assert bound.get('state')=='PASS_ACTUAL_26949_CONTROL_RAW_REVIEW' and bound.get('control_job')=='26949', 'root-bound actual full control verification missing'\n        assert bound.get('control_payload_manifest_sha256')==json.loads((HERE/'matched-control.json').read_text())['control_payload_manifest_sha256']\n        assert geometry.get('decode_draft_regions',{}).get('enabled') is True and geometry['decode_draft_regions']['observed_regions_per_rank']==190\n        replay=subprocess.run([sys.executable,'-B',str(HERE/'check-fast-runtime.py'),str(art),'candidate','64'],capture_output=True,text=True)\n        assert replay.returncode==0,replay.stdout+replay.stderr\n        assert json.loads(replay.stdout)==runtime, 'runtime receipt differs from independently replayed raw logs'")
p.write_text(s)
p=B/'topology-job.sh';s=(P/'topology-job.sh').read_text();needle='mkdir -p "$ART"\n';assert s.count(needle)==1;s=s.replace(needle,needle+'python3 -B "$BUNDLE/verify-control.py" "$ART/matched-control-verification.json"\n')
s=s.replace('--expected-role prefill-0=4 --expected-role prefill-1=4 --expected-role decode-0=8 >', '--expected-role prefill-0=4 --expected-role prefill-1=4 --expected-role decode-0=8 --decode-draft 1 >');p.write_text(s)
p=B/'job.sbatch';s=(P/'job.sbatch').read_text().replace(P.name,B.name).replace('#SBATCH -J ap42-s93-warm','#SBATCH -J ap42-s98-eagle12').replace('export QWEN_HAS_DRAFT=0','export QWEN_HAS_DRAFT=1')
needle='mkdir -p "$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID"';assert s.count(needle)==1
cfg=json.loads((B/'config.json').read_text());proof=cfg['native_argument_prerequisite']
s=s.replace(needle,needle+'\npython3 -B "$QWEN_BUNDLE/check-native-arg-prereq.py" "'+proof['evidence']+'" "'+proof['evidence_sha256']+'" >"$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID/native-argument-prerequisite.json"')
p.write_text(s)
for name in ['performance_gates.py','benchmark.sh','native-container.sh','nixl-conn.py','kv_geometry.py','warm-topology.py','warmup_semantic.py','resource-sampler.py','expected-input-config.json','reference-output-smoke.json']:
 assert (B/name).read_bytes()==(P/name).read_bytes(),name
assert (B/'validate_kv_geometry.py').read_bytes()==(S/'validate_kv_geometry.py').read_bytes(),'Do not broaden the proven decode-only whitelist'
for p in B.rglob('*'):
 if p.suffix=='.py':ast.parse(p.read_text())
 if p.suffix in ('.sh','.sbatch'):subprocess.run(['bash','-n',str(p)],check=True)
(D/'preparation.json').write_text(json.dumps({'native_full_parent':str(P),'decode_only_semantic_parent':str(S),'unchanged': ['performance_gates.py','benchmark.sh','native-container.sh','nixl-conn.py','kv_geometry.py','warm-topology.py','warmup_semantic.py','resource-sampler.py','expected-input-config.json','reference-output-smoke.json'],'geometry_validator_identity':'Byte-identical to actual 25998; 188 P / 190 D predeclared, fresh actual receipts still required.','syntax':'PASS','state':'PREPARED_NOT_SUBMITTED'},indent=2)+'\n')
print('Finished missing worker, controller, prerequisite and independent performance wiring')
