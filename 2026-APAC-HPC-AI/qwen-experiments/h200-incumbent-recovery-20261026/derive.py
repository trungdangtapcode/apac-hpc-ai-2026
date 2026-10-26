#!/usr/bin/env python3
"""Recover incumbent with one legacy replay and three controlled full modern arms."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess
S=Path(__file__).resolve().parent;Q=S.parent
LEGACY=Q/'serving-tuning-10/s35-h200-observed-n64-full-control'
MODERN=Q/'serving-tuning-11/s65-h200-router-rr-control'
def copy(parent,name):
 b=Q/'serving-tuning-11'/name
 shutil.copytree(parent,b,copy_function=shutil.copyfile,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 (b/'PARENT_RECOVERY.json').write_text(json.dumps({'parent':str(parent.relative_to(Q)),'parent_sha256sums_sha256':hashlib.sha256((parent/'SHA256SUMS').read_bytes()).hexdigest(),'derivation':str(Path(__file__).relative_to(Q)),'derivation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
 return b,json.loads((b/'config.json').read_text())
def edit(p,old,new):
 t=p.read_text();assert old in t,(p,old);p.write_text(t.replace(old,new))
def seal(b,c):
 (b/'config.json').write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
 for p in b.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 for p in list(b.glob('*.sh'))+[b/'job.sbatch']:subprocess.run(['bash','-n',str(p)],check=True)
 (b/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in sorted(b.iterdir()) if p.is_file() and p.name!='SHA256SUMS'))

b,c=copy(LEGACY,'s69-h200-legacy-n64-replay');c.update(experiment=b.name,source_experiment=LEGACY.name,source_job='25487',purpose='Incumbent reproducibility/regression checkpoint; unchanged legacy operational scripts and full workload; metadata/job path only differ.')
edit(b/'job.sbatch',str(LEGACY),str(b));edit(b/'job.sbatch','ap42-s35-h200-observed-n64-full-control','ap42-s69-legacy-n64')
(b/'README.md').write_text('# S69 legacy N64 replay\n\nRecover the retained 3k configuration before attributing later lower scores to a dead end. All legacy operational scripts/placement/transport are byte-identical to accepted25487; only metadata and scheduler label/bundle path differ. Same image, model, full60/120/30, N64 and post-score profiling. Actual new outputs, source identity and acceptance must be reviewed; exit0 alone is insufficient. Run sbatch from qwen-experiments.16 H200/two nodes/17-minute cap/no PBS SU.\n'.replace('accepted25487','accepted 25487').replace('full60','full 60').replace('exit0','exit 0').replace('experiments.16','experiments. 16'))
seal(b,c)
for sid,graph,cap in [(70,'disabled',64),(71,'breakable',64),(72,'breakable',None)]:
 name=f's{sid}-h200-full-pgraph-{graph}-cap'+('native' if cap is None else str(cap))
 b,c=copy(MODERN,name)
 c.update(experiment=name,label=name,source_bundle=str(MODERN.relative_to(Q)),schema='full-incumbent-regression-isolation-v1',benchmark_phase='confirm',warmup_seconds=60,measure_seconds=120,prefill_cuda_graph=graph,prefill_max_running_requests=cap,study_arm='modern_full_control' if sid==70 else 'graph_admission_intervention',matched_pair='S70/S71 isolate prefill graph, S71/S72 isolate prefill admission, same full workload and modern harness.',client_protocol='N64 full60/120/30 then smoke/retrieval; local quality unknown',performance_gate='Full60/120/30, N64, exact4000/200 seed2026; joint>=90%; zero errors/cancellations; smoke>=7/8 no regression; retrieval12/12.')
 edit(b/'job.sbatch',str(MODERN),str(b));edit(b/'job.sbatch',MODERN.name+'-${SLURM_JOB_ID}',name+'-${SLURM_JOB_ID}');edit(b/'job.sbatch','ap42-s65-rr',f'ap42-s{sid}-full-'+graph[:3])
 edit(b/'benchmark.sh','110s aiperf profile','250s aiperf profile');edit(b/'benchmark.sh','+200 >','+350 >');edit(b/'benchmark.sh','run_benchmark "$N" screen 20 40','run_benchmark "$N" confirm 60 120');edit(b/'benchmark.sh',"r['phase']=='screen'","r['phase']=='confirm'")
 edit(b/'benchmark.sh','walltime_limit_s=135','walltime_limit_s=250')
 ex=json.loads((b/'expected-input-config.json').read_text());ex['phases'][0]['duration']=60.0;ex['phases'][1]['duration']=120.0;(b/'expected-input-config.json').write_text(json.dumps(ex,indent=2)+'\n')
 edit(b/'performance_gates.py',"rows=[r for r in summary if r.get('phase')=='screen' and r.get('concurrency')==n]", "phase=json.loads((art/'config.json').read_text())['benchmark_phase']\n    assert phase=='confirm'\n    rows=[r for r in summary if r.get('phase')==phase and r.get('concurrency')==n]")
 edit(b/'performance_gates.py',"art/f'screen/n{n}/", "art/f'{phase}/n{n}/")
 edit(b/'check-performance.py',"cap=64 if role.startswith('prefill') else 256", "cap=cfg['prefill_max_running_requests'] if role.startswith('prefill') else 256")
 edit(b/'check-fast-runtime.py',"roles={'prefill-0':4,'prefill-1':4,'decode-0':8}; evidence={}", "roles={'prefill-0':4,'prefill-1':4,'decode-0':8}; evidence={}\ncfg=json.loads((Path(__file__).resolve().parent/'config.json').read_text())\nprefill_cap=cfg['prefill_max_running_requests']")
 edit(b/'check-fast-runtime.py',"    if lit(pg,'backend',role)!='disabled': raise ValueError(f'{role}: prefill CUDA graphs must be disabled')", "    expected_pg=cfg['prefill_cuda_graph'] if role.startswith('prefill') else 'disabled'\n    if lit(pg,'backend',role)!=expected_pg: raise ValueError(f'{role}: actual prefill graph differs from arm')\n    if expected_pg=='breakable':\n        starts=set(re.findall(r'TP(\\d+)\\] Capture target prefill CUDA graph begin\\. backend=breakable',text))\n        ends=set(re.findall(r'TP(\\d+)\\] Capture target prefill CUDA graph end\\.',text))\n        if starts!=set(map(str,range(nranks))) or ends!=starts: raise ValueError(f'{role}: breakable prefill capture incomplete')")
 edit(b/'check-fast-runtime.py',"    if prefill_disabled!=collections.Counter({str(i):expected_kv for i in range(nranks)}): raise ValueError(f'{role}: native target/draft prefill graph-disabled markers incomplete')", "    if expected_pg=='disabled':\n        if prefill_disabled!=collections.Counter({str(i):expected_kv for i in range(nranks)}): raise ValueError(f'{role}: native target/draft prefill graph-disabled markers incomplete')\n    elif prefill_disabled: raise ValueError(f'{role}: graph arm unexpectedly disabled capture')")
 edit(b/'check-fast-runtime.py',"'prefill_graph':'disabled'", "'prefill_graph':expected_pg")
 if graph=='breakable':
  edit(b/'worker.sh','--moe-runner-backend deep_gemm --cuda-graph-backend-prefill disabled','--moe-runner-backend deep_gemm --cuda-graph-backend-prefill breakable')
 if cap is None:
  edit(b/'topology-job.sh','--disaggregation-bootstrap-port "$bootstrap" --max-running-requests 64','--disaggregation-bootstrap-port "$bootstrap"')
 (b/'README.md').write_text(f'# S{sid} full N64 regression isolation\n\nPrefill graph={graph}; prefill max_running_requests={cap}. Full60/120/30, same modern S65 runtime/transport/output gates except declared graph/admission treatment. No fusion or speculative decoding. Retain strict per-rank graph/runtime/KV/semantic and raw denominator acceptance. Read shared PLAN.md in h200-incumbent-recovery-20261026. Run sbatch from qwen-experiments.16 H200/two nodes/17-minute maximum/no PBS SU.\n'.replace('Full60','Full 60').replace('experiments.16','experiments. 16'))
 (b/'PLAN.md').write_text('''# Controlled full-protocol regression study

S70 disabled prefill graph/cap64 is the full-duration counterpart of the recent short S65 control. S71 enables breakable prefill graphs only. S72 retains S71 graphs and removes the explicit prefill64 cap, recovering native admission. All use N64/full60/120/30/fixed4000:200/client seed2026/cold-prefix setting and the same modern target-only runtime, explicit BF16 activation/KV, geometry-instrumented NIXL, round-robin,16 H200 and local checks. S69 independently replays the legacy3k operational payload; cross-harness differences remain, so S69/S72 is not a one-factor attribution.

Need every full workload/runtime/geometry/semantic/output gate, >=90% joint TTFT<=3000ms and mean request ITL<=20ms, zero errors/cancellations, smoke>=7/8 with no regression, retrieval12/12. Actual breakable graph capture must begin and end on every intended prefill rank. Missing capture/fallback is a failed prerequisite, not accepted graph performance. No target precision/weights/dataset/sampling threshold is changed.

Question: did shorter protocol and graph/admission drift explain lower recent controls? No cause is assumed. Review full profiles, actual native arguments and output plus outer-client phase-bounded CPU/GPU/queue/KV samples. These sampling windows include warmup/grace and are not profiling-only; missing telemetry is explicit. Heavy profiling is disabled for modern arms; S69 retains the original separately post-score profile. No scored profile contamination.

Require >1% paired good output throughput with useful tails and all local gates to propose independent confirmation. A single peak is not a reproduced new winner. If legacy reproduces but modern arms fail, preserve incumbent and isolate remaining wrapper/dtype/harness drift before broader architecture search. If no useful graph/admission improvement appears, close that treatment; no blind duplicates. Official full-set99% accuracy stays UNKNOWN. None of these jobs updates submission materials automatically.

Each job16 H200/two nodes/at most17 minutes/no PBS SU. Fresh queue cap5 includes already submitted S68. Use afterany chain to preserve experiment order; control failure invalidates a paired comparison but does not prevent independent recovery evidence. Save definite IDs before another submission and preserve all failed attempts. No background Codex or schedules.
'''.replace('cap64','cap 64').replace('prefill64','prefill 64').replace('full60','full 60').replace('fixed4000','fixed 4000').replace('seed2026','seed 2026').replace('round-robin,16','round-robin, 16').replace('legacy3k','legacy 3k').replace('retrieval12','retrieval 12').replace('full-set99','full-set 99').replace('job16','job 16').replace('most17','most 17').replace('cap5','cap 5'))
 seal(b,c)
print('Prepared legacy replay and three modern full isolation arms')
