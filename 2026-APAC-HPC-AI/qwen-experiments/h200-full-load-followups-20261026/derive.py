#!/usr/bin/env python3
"""Bracket full-workload N64 after closing the graph/admission factorial."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess
S=Path(__file__).resolve().parent;Q=S.parent;P=Q/'serving-tuning-11/s72-h200-full-pgraph-breakable-capnative'
for sid,n in [(74,62),(75,66)]:
 B=Q/'serving-tuning-11'/f's{sid}-h200-full-native-n{n}'
 assert not B.exists();shutil.copytree(P,B,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 c=json.loads((B/'config.json').read_text());c.update(experiment=B.name,label=B.name,concurrency=n,source_bundle=str(P.relative_to(Q)),source_job='26319',schema='full-native-load-bracket-v1',study_arm='lower_load' if n<64 else 'higher_load',matched_pair='Compare to full native N64 26319; short graph-disabled/cap64 sweeps are different runtime controls.',client_protocol=f'N{n}, full 60/120/30, fixed 4000/200, seed 2026',performance_gate=f'Configured N{n}; full 60/120/30; joint SLA >=90%; zero errors/cancellations; no smoke regression and retrieval12/12.')
 (B/'config.json').write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
 p=B/'job.sbatch';s=p.read_text().replace(str(P),str(B)).replace(P.name,B.name).replace('ap42-s72-full-bre',f'ap42-s{sid}-full-n{n}');p.write_text(s)
 p=B/'topology-job.sh';s=p.read_text();assert 'env QWEN_TUNE_NS=64 ' in s;s=s.replace('env QWEN_TUNE_NS=64 ',f'env QWEN_TUNE_NS={n} ').replace('no N64 performance-client budget',f'no N{n} performance-client budget');p.write_text(s)
 ex=json.loads((B/'expected-input-config.json').read_text())
 for phase in ex['phases']:
  if 'concurrency' in phase:phase['concurrency']=n
 assert ex['workers']['workers']==64 if isinstance(ex.get('workers'),dict) else True
 # Change only client concurrency/worker count; server graph captures remain dense1..64.
 def workers(value):
  if isinstance(value,dict):
   for key,v in value.items():
    if key=='workers' and type(v) is int and v==64:value[key]=n
    else:workers(v)
  elif isinstance(value,list):
   for v in value:workers(v)
 workers(ex)
 (B/'expected-input-config.json').write_text(json.dumps(ex,indent=2)+'\n')
 (B/'PARENT_RECOVERY.json').write_text(json.dumps({'parent':str(P.relative_to(Q)),'manifest_sha256':hashlib.sha256((P/'SHA256SUMS').read_bytes()).hexdigest(),'control_job':26319,'only_treatment':'client closed-loop concurrency and matching client workers','derivation':str(Path(__file__).relative_to(Q))},indent=2)+'\n')
 (B/'PLAN.md').write_text(f'''# Full native-runtime load bracket: N{n}

All four full graph/admission observations pass local gates. Graph gains0.79–0.91%, below the declared >1% useful-gain gate; admission changes are near zero. Close that tuning branch without confirming a subthreshold peak. Full native N64 job26319 scores2827.996286 good output tokens/s,98.424311% joint SLA, no errors/cancellations, smoke7/8 and retrieval12/12. Its mean ITL14.659ms leaves headroom but28 TTFT failures prevent assuming unlimited concurrency.

Hypothesis: a small closed-loop load change can trade prefill queueing against decoder batch utilization under the recovered full native runtime. This arm uses N{n}, compared with fixed N64 control26319 and the other bracket arm. Prior N66–N70 losses used short graph-disabled/cap64 controls, so they do not answer this exact full breakable/native question. This is one bounded protocol correction, not a retry of unchanged losing settings. Keep the original losses visible. No future widening beyond this bracket without reviewing these actual results.

Only client N and corresponding worker count change. Keep full60/120/30,4000/200,seed2026, cold prefix, target FP8 weights/BF16 activation and native BF16 KV, P4+P4/D8EP8, round robin, prefill breakable graphs/native admission, same image/transport/geometry and local output gates. The server decode graph list remains1..64: N66 client concurrency is not a demand to capture server batch66, because requests occupy different serving stages. The actual runtime checker remains unchanged.

Require independently replayed configured-N input/raw denominator, joint TTFT<=3000ms and mean request ITL<=20ms for >=90%, zero errors/cancellations, smoke>=7/8 without regression and retrieval12/12. Inspect tails, role queue/running/KV gauges, CPU/GPU/VRAM and transport evidence. Need >1% useful gain versus contemporary N64 before proposing an independent matched confirmation; a single deployment does not prove a winner. Official full-set99%-reference accuracy stays UNKNOWN. No submitted package promotion.

One16-H200/two-node/17-minute bound, no PBS SU. Fresh Slurm cap5 and unambiguous receipts required. Two bracket jobs may be admitted sequentially with afterany; scheduling success never substitutes for acceptance. Frozen parents unchanged. No background Codex or automatic retry.
'''.replace('gains0','gains 0').replace('job26319','job 26319').replace('scores2827','scores 2827').replace('s,98','s, 98').replace('smoke7','smoke 7').replace('retrieval12','retrieval 12').replace('ITL14','ITL 14').replace('but28','but 28').replace('control26319','control 26319').replace('full60','full 60').replace('30,4000','30, 4000').replace('/200,seed','/200, seed').replace('remains1','remains 1').replace('batch66','batch 66').replace('full-set99','full-set 99').replace('One16','One 16').replace('cap5','cap 5'))
 (B/'README.md').write_text(f'# S{sid} full native load N{n}\n\nRead PLAN.md. Exactly one client-load treatment versus accepted full N64 26319. No new score or official accuracy claim.\n')
 for p in B.glob('*.py'):ast.parse(p.read_text())
 for p in list(B.glob('*.sh'))+[B/'job.sbatch']:subprocess.run(['bash','-n',str(p)],check=True)
 unchanged=[p.name for p in P.glob('*.py') if p.read_bytes()==(B/p.name).read_bytes()];assert len(unchanged)==len(list(P.glob('*.py')))
 assert (B/'worker.sh').read_bytes()==(P/'worker.sh').read_bytes()
 (B/'PREPARATION.json').write_text(json.dumps({'state':'CPU_SYNTAX_CONFIG_PARITY_PASS_NOT_GPU_ACCEPTANCE','configured_concurrency':n,'unchanged_python_gates':unchanged,'worker_byte_identical':True,'all_phase_concurrency':[x.get('concurrency') for x in ex['phases']]},indent=2)+'\n')
 (B/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in sorted(B.iterdir()) if p.is_file() and p.name!='SHA256SUMS'))
 subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=B,check=True,stdout=subprocess.DEVNULL)
 print('Prepared',B.name)
