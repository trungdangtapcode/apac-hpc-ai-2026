#!/usr/bin/env python3
"""Derive a bounded three-point KV completion-poll study from the native full control."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess
D=Path(__file__).resolve().parent;Q=D.parent;P=Q/'serving-tuning-11/s93-h200-tokenizer-off-warmfix'
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=P,check=True,stdout=subprocess.DEVNULL)
source=json.loads((Q/'h200-transfer-poll-source-20261029/evidence/SOURCE_MANIFEST.json').read_text())
for f in source['files']:
 p=Q/'h200-transfer-poll-source-20261029'/f['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']
unchanged=['topology-job.sh','benchmark.sh','performance_gates.py','native-container.sh','nixl-conn.py','kv_geometry.py','validate_kv_geometry.py','warm-topology.py','warmup_semantic.py','resource-sampler.py','expected-input-config.json','reference-output-smoke.json']
records=[]
for prefix,k in [('s101',1),('s99',2),('s100',4)]:
 B=Q/f'serving-tuning-11/{prefix}-h200-transfer-poll{k}'
 shutil.copytree(P,B)
 cfg=json.loads((P/'config.json').read_text());cfg.update(experiment=B.name,label=f'Decode transfer completion polling interval {k}',source_parent=P.name,matched_control_job=26949,study_arm=f'decode_transfer_poll_interval_{k}',decode_transfer_polling_interval=k,prefill_transfer_polling_interval=1,matched_pair='Prospective full N64 polling intervals 1/2/4, target-only in all arms; new interval1 control must be reviewed before claiming improvement.',performance_or_GPU_acceptance='UNKNOWN')
 # Legacy arm=control means target-only, not the role in this new three-point study.
 assert cfg['arm']=='control' and cfg['speculation'] is None
 (B/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
 s=(P/'worker.sh').read_text();needle='extra=(--cuda-graph-backend-prefill disabled '
 assert s.count(needle)==1;s=s.replace(needle,f'extra=(--disaggregation-decode-polling-interval {k} --cuda-graph-backend-prefill disabled ')
 needle="print('NIXL_PATCH_VERIFIED',actual,flush=True)"
 assert s.count(needle)==1
 proof="\n".join(f"assert hashlib.sha256(Path('/{f['image_path']}').read_bytes()).hexdigest()=='{f['sha256']}', 'Pinned polling source mismatch'" for f in source['files'])
 s=s.replace(needle,needle+'\n'+proof+"\nprint('TRANSFER_POLL_SOURCE_VERIFIED',flush=True)")
 (B/'worker.sh').write_text(s)
 s=(P/'check-fast-runtime.py').read_text();needle="    for key,wanted in common.items():";assert s.count(needle)==1
 s=s.replace(needle,"    common['disaggregation_decode_polling_interval']=cfg['decode_transfer_polling_interval'] if role=='decode-0' else cfg['prefill_transfer_polling_interval']\n"+needle)
 needle="'server_args_records':1}";assert s.count(needle)==1;s=s.replace(needle,"'server_args_records':1,'decode_transfer_polling_interval':common['disaggregation_decode_polling_interval']}")
 (B/'check-fast-runtime.py').write_text(s)
 s=(P/'check-performance.py').read_text().replace('import ast, hashlib, importlib.util, json, re, sys','import ast, hashlib, importlib.util, json, re, sys, subprocess')
 needle="needed={'max_running_requests',";assert s.count(needle)==1;s=s.replace(needle,"needed={'disaggregation_decode_polling_interval','max_running_requests',")
 needle="        assert a['max_running_requests']==cap and a['dtype']=='bfloat16'";assert s.count(needle)==1
 s=s.replace(needle,needle+"\n        assert a['disaggregation_decode_polling_interval']==(cfg['decode_transfer_polling_interval'] if role=='decode-0' else cfg['prefill_transfer_polling_interval']), f'{role}: actual transfer polling interval differs'")
 needle="    assert runtime.get('state')=='PASS_FAST_RUNTIME' and runtime.get('arm')==cfg['arm']";assert s.count(needle)==1
 s=s.replace(needle,needle+"\n    replay=subprocess.run([sys.executable,'-B',str(HERE/'check-fast-runtime.py'),str(art),'control','64'],capture_output=True,text=True)\n    assert replay.returncode==0,replay.stdout+replay.stderr\n    assert json.loads(replay.stdout)==runtime, 'runtime receipt differs from independently replayed raw logs'")
 (B/'check-performance.py').write_text(s)
 s=(P/'job.sbatch').read_text().replace(P.name,B.name).replace('#SBATCH -J ap42-s93-warm',f'#SBATCH -J ap42-{prefix}-poll{k}')
 (B/'job.sbatch').write_text(s)
 (B/'README.md').write_bytes((D/'PLAN.md').read_bytes())
 for name in unchanged:assert (B/name).read_bytes()==(P/name).read_bytes(),name
 for p in B.rglob('*'):
  if p.suffix=='.py':ast.parse(p.read_text())
  if p.suffix in ('.sh','.sbatch'):subprocess.run(['bash','-n',str(p)],check=True)
 files=sorted(p for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='SHA256SUMS')
 (B/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(B))+'\n' for p in files))
 subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=B,check=True,stdout=subprocess.DEVNULL)
 records.append({'bundle':str(B.relative_to(Q)),'interval':k,'manifest_sha256':hashlib.sha256((B/'SHA256SUMS').read_bytes()).hexdigest()})
(D/'preparation.json').write_text(json.dumps({'state':'PREPARED_NOT_SUBMITTED','parent':str(P.relative_to(Q)),'parent_manifest_sha256':hashlib.sha256((P/'SHA256SUMS').read_bytes()).hexdigest(),'source_evidence':source,'unchanged_files':unchanged,'bundles':records,'gate_scope':'Legacy arm=control means target-only; study_arm identifies actual polling intervention. All three arms independently replay exact runtime logs including the interval.'},indent=2)+'\n')
print(json.dumps(records,indent=2))
