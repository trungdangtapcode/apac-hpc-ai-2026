#!/usr/bin/env python3
"""Freeze a page-1 prefill attention backend control derived from valid S93."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess
D=Path(__file__).resolve().parent;Q=D.parent
src=Q/'serving-tuning-11/s93-h200-tokenizer-off-warmfix';dst=Q/'serving-tuning-11/s96-h200-prefill-flashinfer-page1'
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=src,check=True,stdout=subprocess.DEVNULL)
shutil.copytree(src,dst)
cfg=json.loads((src/'config.json').read_text());cfg.update(experiment=dst.name,label='Page-1 FlashInfer prefill attention compatibility/control',source_parent=src.name,study_arm='prefill_attention_backend_page1',matched_control_job=26949,prefill_attention_backend='flashinfer',page_size=1,matched_pair='S93 full N64 tokenizer-off control; only both prefill workers explicitly select FlashInfer attention instead of automatic FA3. Decode unchanged.',performance_or_GPU_acceptance='UNKNOWN',purpose='Separate attention backend effect before any future page-size change; not a page-16 trial or predicted improvement.')
(dst/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
s=(src/'worker.sh').read_text();old='extra=(--chunked-prefill-size 8192 --moe-runner-backend deep_gemm --cuda-graph-backend-prefill breakable)';assert s.count(old)==1
s=s.replace(old,old[:-1]+' --attention-backend flashinfer --page-size 1)');(dst/'worker.sh').write_text(s)
s=(src/'check-fast-runtime.py').read_text();old="'attention_backend':'fa3'}";assert s.count(old)==1
s=s.replace(old,"'attention_backend':'flashinfer' if role.startswith('prefill') else 'fa3', 'page_size':1}")
(dst/'check-fast-runtime.py').write_text(s)
s=(src/'job.sbatch').read_text().replace(src.name,dst.name).replace('#SBATCH -J ap42-s93-warm','#SBATCH -J ap42-s96-fi-p1')
s=s.replace("import json\nfrom pathlib", "import json\nfrom pathlib")
needle="assert r.get('state')=='AIPERF_ENTRYPOINT_AND_TERMINAL_ROOT_CLEANUP_PASS', 'Actual R3 entrypoint/cleanup prerequisite missing; no model may start'"
assert needle in s;s=s.replace(needle,needle+"\naudit=json.loads(Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-full-load-review-20261026/review-26949.json').read_text())\nassert audit['state']=='LOCAL_FULL_GATE_PASS_NOT_OFFICIAL_ACCURACY' and audit['scheduler']['State']=='COMPLETED'")
(dst/'job.sbatch').write_text(s)
(src/'SHA256SUMS').read_text()
unchanged=['native-container.sh','nixl-conn.py','kv_geometry.py','validate_kv_geometry.py','warm-topology.py','warmup_semantic.py','benchmark.sh','performance_gates.py','check-performance.py','topology-job.sh','exec.rc']
for name in unchanged:assert (src/name).read_bytes()==(dst/name).read_bytes(),name
plan='''# Page-1 prefill FlashInfer control before page-size work

Recorded 28 October 2026, Vietnam time. This is a distinct backend/control question, not a claim that FlashInfer beats FA3. Full fresh control 26949 is valid at 3034.761104 good output tokens/s with 98.627968% joint SLA; separate 26766 is 3045.501509. Page sizes above1 are documented by the pinned selector as changing automatic prefill attention. A future page16 trial must not attribute that coupled backend change solely to paging.

The only serving intervention is that both TP4 prefill workers explicitly request `--attention-backend flashinfer --page-size 1`, holding native page size1. Decode remains TP8/EP8 HPC-Ops/FlashInfer/MNNVL, all other target flags unchanged. P4+P4/D8, DeepGEMM chunk8192, breakable prefill graphs, full decode graphs1..64, target-only FP8 weights/BF16 activation and KV, native runtime/transport patches, N64 and full60/120/30 cold4000/200 seed2026 remain. Tokenizer batching is off. No future page16 production exception is enabled. Explicit page1 must match actual resolved arguments and the existing strict188-region geometry; no fallback is accepted.

Pinned source server_args.py declares FlashInfer as a supported attention choice and exposes explicit phase/worker selection; get_attention_backends uses explicit overrides. The same source explains that its Hopper default is FA3 because FlashInfer0.6.1 had a regression. This is counterevidence to a speedup hypothesis, preserved rather than hidden. This control is useful even if slower: it measures the isolated backend cost and real whole-prefill compatibility before any page/backend combined candidate. It does not depend on the failed BF16 primitive or bypass that branch's remaining correctness prerequisites. No heavy profile is added.

Admit at most one16-H200/two-node/17-minute job, maximum4.533334GPU-hours, under cap5 and the Slurm admission lock. Preserve current positions. The frozen semantic/runtime/BF16/KV/two-route and raw request/error/SLA/output gates all remain. Require joint TTFT<=3000ms and request-mean ITL<=20ms >=90% including errors, zero profiling errors/cancellations, smoke7/8 without regression and retrieval12/12. Full official99%-reference accuracy remains UNKNOWN. Startup/runtime evidence is not a kernel trace. If incompatible with breakable graphs or local gates, retain failure and do not silently disable graphs or relax checks. If valid, compare against fresh26949 and retained repeats; a >1% candidate gain plus nonregressing tails warrants a separately matched independent confirmation, not automatic promotion. A smaller/lower result closes this unchanged backend as a speed optimization but remains a usable page-study control.

Source: ../fp8-kv-source-preflight-20261023/source-image/sgl-workspace/sglang/python/sglang/srt/server_args.py lines1644-1670,5655-5690,8607-8622. Source SHA256 is recorded in provenance.json. Other full tokenizer arms remain independent. Published AI/HPC submission is unchanged; no H100 spending, VPN prompt or background schedule.
'''
(dst/'README.md').write_text(plan);(D/'PLAN.md').write_text(plan)
source=Q/'fp8-kv-source-preflight-20261023/source-image/sgl-workspace/sglang/python/sglang/srt/server_args.py'
(D/'provenance.json').write_text(json.dumps({'parent':str(src.relative_to(Q)),'parent_manifest_sha256':hashlib.sha256((src/'SHA256SUMS').read_bytes()).hexdigest(),'source_path':str(source.relative_to(Q)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'matched_control_job':26949,'unchanged_protocol_files':unchanged,'changed':['worker.sh','check-fast-runtime.py','config.json','job.sbatch','README.md'],'old_fusion_branch':'S66/S67 already measured26089/26091 and closed below3%; explicitly not repeated'},indent=2)+'\n')
for f in dst.iterdir():
 if f.suffix=='.py':ast.parse(f.read_text())
 if f.suffix in ('.sh','.sbatch'):subprocess.run(['bash','-n',str(f)],check=True)
files=sorted(p for p in dst.iterdir() if p.is_file() and p.name!='SHA256SUMS');(dst/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))
print(dst)
