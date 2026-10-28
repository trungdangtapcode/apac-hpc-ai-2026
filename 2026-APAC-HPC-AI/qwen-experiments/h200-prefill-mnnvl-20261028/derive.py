#!/usr/bin/env python3
"""Derive a matched prefill collective-backend study without changing attention."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess
D=Path(__file__).resolve().parent;Q=D.parent;src=Q/'serving-tuning-11/s93-h200-tokenizer-off-warmfix';b=Q/'serving-tuning-11/s97-h200-prefill-mnnvl'
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=src,check=True,stdout=subprocess.DEVNULL);shutil.copytree(src,b)
cfg=json.loads((src/'config.json').read_text());cfg.update(experiment=b.name,label='Prefill explicit MNNVL collective; FA3 attention retained',source_parent=src.name,matched_control_job=26949,study_arm='prefill_collective_backend',prefill_allreduce_fusion_backend='mnnvl',flashinfer_allreduce_fusion_backend='decode=mnnvl, prefill=mnnvl; explicit actual per-rank startup evidence required',matched_pair='Actual S93 control prefill auto resolves to trtllm; this arm requests mnnvl on both prefills, with all other settings unchanged.',performance_or_GPU_acceptance='UNKNOWN')
(b/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
s=(src/'worker.sh').read_text();old='extra=(--chunked-prefill-size 8192 --moe-runner-backend deep_gemm --cuda-graph-backend-prefill breakable)';assert s.count(old)==1;s=s.replace(old,old[:-1]+' --flashinfer-allreduce-fusion-backend mnnvl)');(b/'worker.sh').write_text(s)
s=(src/'check-fast-runtime.py').read_text();old="moe_runner_backend='deep_gemm',flashinfer_allreduce_fusion_backend='auto'";assert s.count(old)==1;s=s.replace(old,"moe_runner_backend='deep_gemm',flashinfer_allreduce_fusion_backend='mnnvl'")
needle="    expected_kv=1 if arm=='control' else 2";assert s.count(needle)==1
s=s.replace(needle,"""    if role.startswith('prefill'):
        selected=set(re.findall(r'FlashInfer AllReduce Fusion enabled and workspace initialized: backend=mnnvl, rank=(\\d+), world_size=4',text))
        if selected!=set(map(str,range(4))): raise ValueError(f'{role}: all four native MNNVL startup ranks required')
        if re.search(r'workspace initialized: backend=trtllm, rank=\\d+, world_size=4',text): raise ValueError(f'{role}: TRTLLM fallback forbidden')
"""+needle)
s=s.replace("'mnnvl_fusion':'mnnvl' if role=='decode-0' else 'auto'", "'mnnvl_fusion':'mnnvl'")
(b/'check-fast-runtime.py').write_text(s)
s=(src/'check-performance.py').read_text();old="('auto' if role.startswith('prefill') else 'mnnvl')";assert s.count(old)==1;s=s.replace(old,"'mnnvl'");(b/'check-performance.py').write_text(s)
s=(src/'job.sbatch').read_text().replace(src.name,b.name).replace('#SBATCH -J ap42-s93-warm','#SBATCH -J ap42-s97-p-mnnvl');(b/'job.sbatch').write_text(s)
unchanged=['nixl-conn.py','kv_geometry.py','validate_kv_geometry.py','warmup_semantic.py','warm-topology.py','native-container.sh','topology-job.sh','benchmark.sh','performance_gates.py']
for name in unchanged:assert (src/name).read_bytes()==(b/name).read_bytes(),name
for p in b.iterdir():
 if p.suffix=='.py':ast.parse(p.read_text())
 if p.suffix in ['.sh','.sbatch']:subprocess.run(['bash','-n',str(p)],check=True)
source=Q/'fp8-kv-source-preflight-20261023/source-image/sgl-workspace/sglang/python/sglang/srt/server_args.py'
(D/'provenance.json').write_text(json.dumps({'parent':str(src.relative_to(Q)),'parent_manifest_SHA256':hashlib.sha256((src/'SHA256SUMS').read_bytes()).hexdigest(),'server_args_source':str(source.relative_to(Q)),'server_args_SHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_lines':[1974,1991],'actual_control':26949,'unchanged_files':unchanged},indent=2)+'\n')
lines=[x for x in (Q/'runs/26949/prefill-0.log').read_text().splitlines() if 'FlashInfer AllReduce Fusion enabled and workspace initialized:' in x]
assert lines and all('backend=trtllm' in x and 'world_size=4' in x for x in lines);(D/'actual-control-prefill-collective.log').write_text('\n'.join(lines)+'\n')
plan='''# Prefill MNNVL collective backend, attention held at FA3

Recorded 29 October 2026, Vietnam time. Actual full control 26949 logs reveal that its prefill `auto` collective resolves to **TRT-LLM**, four ranks per worker, whereas decode uses MNNVL. The control's resolved ServerArgs alone only said auto; the startup lines identify the selected backend. This distinction motivates a separate communication-kernel hypothesis. It is unrelated to the losing FlashInfer attention trial27077: FA3 prefill attention stays unchanged here.

Hypothesis: explicitly using MNNVL fusion on each TP4 prefill could reduce collective/norm/dispatch cost and improve time to first token or useful request rate. Decode has already executed MNNVL on eight H200 ranks; this does not prove TP4 prefill performance, kernel selection or a bottleneck. Source server_args.py lines1974-1991 lists MNNVL support on SM90 single-node systems. Actual per-rank MNNVL initialization must be observed on all four ranks of each prefill; a fallback to TRT-LLM is rejected before scoring. Source/runtime/KV/semantic/output checks remain, and no numerical, model, KV or transport patch is changed.

Only the prefill collective selection changes from auto to explicitmnnvl. Keep P4+P4/D8EP8, DeepGEMM chunk8192, breakable prefill graphs, full decode graphs1..64, FA3 prefill/FlashInfer decode attention, target-only FP8 weights/BF16 activation and KV, native page1, tokenizer batching off and full N64 cold4000/200 seed2026 60/120/30. Same image, model, sampler and transport wrapper. Compare primarily against full fresh26949 (3034.761104 good output tokens/s), with separate26766 (3045.501509) as variation context. No automatic promotion or claim that differences between separate launches are caused by this flag.

Bounded one-job admission:16 H200/two nodes/17 minutes, maximum4.533334GPU-hours, no PBS SU, own active/pending cap5. Retain raw joint success >=90% at TTFT<=3000ms/request-mean ITL<=20ms including errors, zero errors/cancellations, smoke7/8 without regression and retrieval12/12. Official full-set99%-reference accuracy remains UNKNOWN. Require a gain above1% and acceptable tails before independent matched confirmation. Otherwise close this unchanged collective intervention. Inspect actual selected startup ranks, queues/KV, errors, tail latency, sparse CPU/GPU/VRAM and cleanup; no heavy profile in scoring. A source-supported flag is not GPU acceptance.

Parent is frozen S93. Job27136 portable submission replay is independent and retains its queue position. The prior tokenizer arms were full valid but below1%; they are closed unchanged. Published AI/HPC payloads remain untouched. No VPN prompts, H100 charge, background Codex or schedules.
'''
for a,z in {'trial27077':'trial 27077','lines1974':'lines 1974','explicitmnnvl':'explicit mnnvl','chunk8192':'chunk 8192','graphs1..64':'graphs 1..64','cold4000':'cold 4000','seed2026':'seed 2026','fresh26949':'fresh 26949','separate26766':'separate 26766','admission:16':'admission: 16','maximum4.533334GPU-hours':'maximum 4.533334 GPU-hours','cap5':'cap 5','TTFT<=3000ms':'TTFT <= 3000 ms','ITL<=20ms':'ITL <= 20 ms','smoke7/8':'smoke 7/8','retrieval12/12':'retrieval 12/12','full-set99%':'full-set 99%','above1%':'above 1%','Job27136':'Job 27136','below1%':'below 1%'}.items():plan=plan.replace(a,z)
(D/'PLAN.md').write_text(plan);(b/'README.md').write_text(plan)
files=sorted(p for p in b.iterdir() if p.is_file() and p.name!='SHA256SUMS');(b/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))
print(b)
