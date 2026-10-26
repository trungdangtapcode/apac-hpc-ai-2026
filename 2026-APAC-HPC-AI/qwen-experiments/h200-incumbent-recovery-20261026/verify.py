#!/usr/bin/env python3
"""Preflight recovery study against frozen operational bytes and actual exports."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,tempfile
S=Path(__file__).resolve().parent;Q=S.parent
names=['s69-h200-legacy-n64-replay','s70-h200-full-pgraph-disabled-cap64','s71-h200-full-pgraph-breakable-cap64','s72-h200-full-pgraph-breakable-capnative']
legacy=Q/'serving-tuning-10/s35-h200-observed-n64-full-control';copy=Q/'serving-tuning-11'/names[0]
identical=[]
for p in legacy.iterdir():
 if not p.is_file() or p.name in ('job.sbatch','config.json','SHA256SUMS'):continue
 assert p.read_bytes()==(copy/p.name).read_bytes(),p.name;identical.append(p.name)
records=[]
for name in names:
 b=Q/'serving-tuning-11'/name;subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=b,check=True,stdout=subprocess.DEVNULL)
 if name==names[0]:continue
 cfg=json.loads((b/'config.json').read_text());enabled=cfg['prefill_cuda_graph']=='breakable'
 spec=importlib.util.spec_from_file_location('gates',b/'performance_gates.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
 with tempfile.TemporaryDirectory(prefix='h200-full-replay-') as temp:
  a=Path(temp);(a/'config.json').write_text(json.dumps(cfg));(a/'summary.json').symlink_to(Q/'runs/25487/summary.json');(a/'confirm').symlink_to(Q/'runs/25487/confirm')
  profile=g.check_aiperf(a,json.loads((b/'expected-input-config.json').read_text()));assert profile['completed']==1901
  bad=json.loads((b/'expected-input-config.json').read_text());bad['phases'][0]['duration']=20.0
  try:g.check_aiperf(a,bad)
  except AssertionError:pass
  else:raise AssertionError('Wrong warmup accepted')
  for role in ('prefill-0','prefill-1','decode-0'):
   text=(Q/f'runs/26083/{role}.log').read_text()
   if role.startswith('prefill') and enabled:
    assert text.count("prefill=PhaseConfig(backend='disabled'")==1
    text=text.replace("prefill=PhaseConfig(backend='disabled'","prefill=PhaseConfig(backend='breakable'")
    text='\n'.join(line for line in text.splitlines() if 'Disable prefill CUDA graph because' not in line)+'\n'
    capture=[line for line in (Q/f'runs/25487/{role}.log').read_text().splitlines() if 'Capture target prefill CUDA graph begin.' in line or 'Capture target prefill CUDA graph end.' in line]
    text+='\n'.join(capture)+'\n'
   if role.startswith('prefill') and cfg['prefill_max_running_requests'] is None:
    assert text.count('mem_fraction_static=0.9, max_running_requests=64,')==1
    text=text.replace('max_running_requests=64,','max_running_requests=None,')
   (a/f'{role}.log').write_text(text)
  result=subprocess.run(['python3','-B',str(b/'check-fast-runtime.py'),str(a),'control','64'],capture_output=True,text=True);assert result.returncode==0,result.stderr
  if enabled:
   p=a/'prefill-0.log';t=p.read_text();p.write_text(t.replace('Capture target prefill CUDA graph end.','REMOVED_CAPTURE_END'))
   rejected=subprocess.run(['python3','-B',str(b/'check-fast-runtime.py'),str(a),'control','64'],capture_output=True,text=True);assert rejected.returncode!=0 and 'capture incomplete' in rejected.stderr
  records.append({'bundle':name,'actual_old_full_profile_replay_good_output_tokens_s':profile['good_output_tokens_per_second'],'wrong_warmup_rejected':True,'synthetic_resolved_runtime_fixture':'PASS','missing_graph_end_rejected':True if enabled else 'NOT_APPLICABLE','fixture_scope':'Real26083 logs with explicitly synthetic graph/cap edits and retained25487 capture markers; no GPU evidence of candidate.'})
report={'state':'PASS_CPU_PREFLIGHT_ONLY','legacy_operational_files_byte_identical':identical,'legacy_original_job':25487,'modern_arms':records,'limits':'No new GPU measurements or recovery claimed. Historical raw profile replay is not candidate execution. Internal server random seeds differ by deployment while client seed2026 is fixed.'}
(S/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
