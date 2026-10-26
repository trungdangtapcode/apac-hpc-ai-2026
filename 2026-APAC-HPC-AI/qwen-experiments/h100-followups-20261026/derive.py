#!/usr/bin/env python3
"""Prepare one H100 incumbent refresh and an equal-TP observer prerequisite correction."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess,tarfile
S=Path(__file__).resolve().parent;Q=S.parent

def copy(parent,name):
 b=Q/name;b.mkdir(exist_ok=False)
 for line in (parent/'SHA256SUMS').read_text().splitlines():
  digest,rel=line.split(None,1);rel=rel.lstrip('*');p=Path(rel);assert not p.is_absolute() and '..' not in p.parts
  src=parent/p;assert src.is_file() and not src.is_symlink() and hashlib.sha256(src.read_bytes()).hexdigest()==digest
  dst=b/p;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 # Parent submitter is historical and not used to admit these new jobs.
 if (b/'submit-pbs.py').exists():(b/'submit-pbs.py').rename(b/'PARENT_SUBMITTER.py')
 (b/'PARENT_BUNDLE.json').write_text(json.dumps({'parent':str(parent.relative_to(Q)),'parent_manifest_sha256':hashlib.sha256((parent/'SHA256SUMS').read_bytes()).hexdigest(),'derivation':str(Path(__file__).relative_to(Q))},indent=2)+'\n')
 return b

def seal(b):
 for p in b.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
 for p in list(b.glob('*.sh'))+list(b.glob('*.pbs')):subprocess.run(['bash','-n',str(p)],check=True)
 files=sorted(p for p in b.rglob('*') if p.is_file() and p.name not in ('SHA256SUMS','payload.tar.gz') and '__pycache__' not in p.parts)
 (b/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(b))+'\n' for p in files))
 with tarfile.open(b/'payload.tar.gz','w:gz') as tar:
  for p in files+[b/'SHA256SUMS']:tar.add(p,arcname=str(p.relative_to(b)),recursive=False)
 subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=b,check=True,stdout=subprocess.DEVNULL)

parent=Q/'nscc-pbs/h100-cpu-envelope-legacy-n54-79';b=copy(parent,'h100-incumbent-n54-refresh-20261026')
c=json.loads((b/'config.json').read_text());c.update(experiment=b.name,source_experiment=parent.name,source_job='222551.pbs111',purpose='Fresh full H100 incumbent control after access restoration and observed H200 repeat drift; no new tuning treatment or peak claim.');(b/'config.json').write_text(json.dumps(c,indent=2)+'\n')
p=b/'benchmark.pbs';text=p.read_text().replace('/'+parent.name,'/'+b.name).replace('ap42-h100-cpu-envelope-legacy-n54-79','ap42-h100-n54-refresh');p.write_text(text)
(b/'PLAN.md').write_text('''# Refresh the accepted full H100 control after restoring access

H100 has no live ranked-control observation during the recent access outage. Retained222551 full N54 scored2407.544052 good output tokens/s,98.347654% joint SLA, zero errors/cancellations and output7/8/retrieval12/12. Its balanced-envelope treatment lost the declared gain gate; this run retains the accepted legacy control. H200's actual same-runtime replay dropped7.012% from its historical cluster, so old scores must not be assumed current on either cluster.

Reproduce the H100 control once to establish today's baseline before new tuning. All source worker/client/topology/transport/output/profiler files are byte-identical; only metadata/scheduler name/path differ. Full60/120/30, N54, fixed4000/200/client seed2026, official FP8 target, native BF16 KV, both-phase HPC-Ops/chunk4096, FA3 prefill/FlashInfer+MNNVL decode, round-robin and CPU-envelope mode legacy remain. This is not a repeat of the losing balanced policy or a guaranteed2433 peak.

Require actual terminal/workload/runtime/source/raw denominator/latency/output audit before accepting any score. >=90% joint TTFT<=3000ms and mean request ITL<=20ms, zero errors/cancellations, no smoke regression below7/8, retrieval12/12. Official full-set99% accuracy stays UNKNOWN. Inspect tails, role CPU/GPU/VRAM/queue/KV/transport evidence and keep separate post-score stop-profile errors. One lower replay remains evidence; do not repeat until a favorable number appears. No promotion without distinct justified improvements and independent confirmation.

One16-H100/two-node/30-minute maximum,1024SU bound at128SU/GPU-hour. Admission needs fresh selected AI and CPU queues, CPU-before-AI locks, conservative retained old maxima, combined cap3 and one running AI allocation. Then the separate8-GPU equal-TP observer correction may run afterany. No PBS budget increase, model weights upload, automatic retry, HPC payload change or background Codex.
''')
for p in parent.iterdir():
 if p.is_file() and p.name not in ('config.json','benchmark.pbs','SHA256SUMS') and (b/p.name).is_file():assert p.read_bytes()==(b/p.name).read_bytes(),p.name
seal(b)
parent=Q/'eagle3-h100-single-node-equal-tp-20261024';b=copy(parent,'eagle3-h100-equal-tp-observer-r2-20261026')
c=json.loads((b/'config.json').read_text());c.update(experiment_id=b.name,status='PREPARED_NOT_SUBMITTED',question='Actual equal-TP native KV and auxiliary invocation under a successful semantic request; repairs a wrong heterogeneous-method observer gate.',parent_failed_job='224560.pbs111');(b/'config.json').write_text(json.dumps(c,indent=2)+'\n')
p=b/'benchmark.pbs';p.write_text(p.read_text().replace(parent.name,b.name).replace('ap42-eagle3-h100-equal-tp','ap42-equal-tp-observer-r2'))
p=b/'pd-observer/observer.py';s=p.read_text();s=s.replace('if kind == "send_kvcache_slice":','if kind in {"send_kvcache_slice", "send_kvcache"}:').replace('dst_pages = _arg_count(args, kwargs, "dst_kv_indices", 2)','dst_pages = _arg_count(args, kwargs, "dst_kv_indices", 3 if kind == "send_kvcache" else 2)').replace('for name in ("send_kvcache_slice", "send_aux"):','for name in ("send_kvcache", "send_kvcache_slice", "send_aux"):');p.write_text(s)
p=b/'metadata-gate.py';s=p.read_text().replace('for kind in ("send_kvcache_slice", "send_aux"):','for kind in ("send_kvcache", "send_aux"):')
needle='        observed[kind] = {"start_markers": outcomes.count("start"),';assert needle in s
s=s.replace(needle,'''        if outcomes.count("exception"):
            raise ValueError(f"native observer exception in successful semantic interval: {kind}")
        starts = {int(e["tp_rank"]) for e in events if e.get("marker") == "start"}
        returns = {int(e["tp_rank"]) for e in events if e.get("marker") == "returned_handle"}
        if starts != {0,1,2,3} or returns != starts:
            raise ValueError(f"incomplete actual prefill rank method coverage for {kind}")
        observed[kind] = {"start_markers": outcomes.count("start"),''');p.write_text(s)
(b/'ROOT_REVIEW.json').write_text(json.dumps({'ready_for_bounded_probe':True,'scope':'Derived observer-only prerequisite correction; actual new markers unverified.','parent_failed_job':'224560.pbs111','gpus':8,'minutes':20,'max_su':8*128*20/60,'native_arithmetic_or_source_changed':False,'no_gate_bypass':'Semantic response,8 physical unique devices, source pins and metadata remain required. Adds actual equal-TP KV observer and requires all4 sender-rank return markers with no exception; returned handles are not completion.'},indent=2)+'\n')
(b/'PLAN.md').write_text('''# Repair equal-TP native observation without inventing old KV markers

Actual224560 returned one independently replayable semantic response across same-node P4/D4 EAGLE, but final checker wrongly required heterogeneous send_kvcache_slice. Exact native transfer_worker dispatch chooses send_kvcache when decode_tp_size==attn_tp_size. Old observer wrapped only slice/send_aux, so equal-TP KV invocation was not collected. Original scheduler FAILED and missing observation remain; do not manufacture a past pass.

This derivative wraps native send_kvcache in addition to the existing methods and indexes its dst_kv_indices at positional argument3, unlike slice argument2. The final checker requires send_kvcache and send_aux start/return markers on each actual prefill rank0–3 in the semantic interval, no observed exceptions, plus the original independently replayed semantic response,8 disjoint H100 UUIDs, native module pins and eight role metadata receipts. Native function return/exception/arguments remain unchanged; no arithmetic, model weights, draft, precision, NIXL source or transfer behavior is patched. Returned handles are not proof of completion; the actual semantic response remains independently required.

One8-H100/one-node/20-minute maximum,341.333333SU bound. Same P4/D4EP4 EAGLEsteps2/topk1/draft3 and one semantic request. This is no full16-GPU ranked score, exact-target-ID pass, official accuracy or throughput improvement. If the correct-path gate fails, stop and inspect; no unchanged retry. Fresh queue/credit/combined cap3/one running AI mandatory; run afterany the independent full N54 reference. Existing HPC CPU job stays untouched.

The old run is used for source/metadata/semantic replay only. CPU synthetic method-event fixtures validate rejection and wrapper transparency; they do not prove the newly instrumented GPU invocation. Actual new observations require this bounded allocation.
''')
seal(b)
for b in (Q/'h100-incumbent-n54-refresh-20261026',Q/'eagle3-h100-equal-tp-observer-r2-20261026'):
 for p in (b/'PLAN.md',):
  t=p.read_text()
  for a,c in [('Retained222551','Retained 222551'),('scored2407','scored 2407'),('s,98','s, 98'),('output7','output 7'),('retrieval12','retrieval 12'),('dropped7','dropped 7'),('Full60','Full 60'),('fixed4000','fixed 4000'),('seed2026','seed 2026'),('chunk4096','chunk 4096'),('guaranteed2433','guaranteed 2433'),('below7','below 7'),('full-set99','full-set 99'),('One16','One 16'),('maximum,1024SU','maximum, 1024 SU'),('at128SU','at 128 SU'),('cap3','cap 3'),('separate8','separate 8'),('Actual224560','Actual 224560'),('argument3','argument 3'),('argument2','argument 2'),('rank0','rank 0'),('response,8','response, 8'),('One8','One 8'),('maximum,341.333333SU','maximum, 341.333333 SU'),('EAGLEsteps2','EAGLE steps 2'),('draft3','draft 3'),('full16','full 16')]:t=t.replace(a,c)
  p.write_text(t)
 seal(b)
print('Prepared full H100 incumbent refresh and native equal-TP observer correction')
