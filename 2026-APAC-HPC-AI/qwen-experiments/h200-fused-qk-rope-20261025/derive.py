#!/usr/bin/env python3
"""Prepare phase-isolated native QK norm/RoPE fusion screens from frozen S65."""
from pathlib import Path
import hashlib,json,shutil,ast,subprocess
STUDY=Path(__file__).resolve().parent;ROOT=STUDY.parent
PARENT=ROOT/'serving-tuning-11/s65-h200-router-rr-control'
BASE=STUDY/'source/sgl-workspace/sglang/python/sglang/srt/models/qwen3_moe.py'
base=BASE.read_text();needle='        self._used_fused_qk_norm_rope_last_call = False\n'
assert needle in base
observed=base.replace(needle,needle+'''        if layer_id == 0:
            logger.info("FUSED_QK_ROPE_SELECTION selected=%s head_dim=%s", self.use_fused_qk_norm_rope, self.head_dim)
''',1)
ast.parse(observed)

def edit(p,a,b):
 t=p.read_text();assert a in t,(p,a);p.write_text(t.replace(a,b))

for stage,sid in [('prefill',66),('decode',67)]:
 name=f's{sid}-h200-{stage}-fused-qk-rope';dst=ROOT/'serving-tuning-11'/name
 shutil.copytree(PARENT,dst,copy_function=shutil.copyfile,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 cfg=json.loads((dst/'config.json').read_text());cfg.update(experiment=name,label=f'S{sid} native QK/RoPE fusion on {stage} only',study_arm='candidate',schema='h200-phase-isolated-qk-rope-fusion-v1',fused_qk_norm_rope_roles=['prefill-0','prefill-1'] if stage=='prefill' else ['decode-0'],matched_control_job=26083,source_bundle=str(PARENT.relative_to(ROOT)),matched_pair='S65 current round-robin control; only the selected phase requests native QK norm/RoPE fusion; all other settings unchanged.',native_fusion_source_sha256=hashlib.sha256(observed.encode()).hexdigest())
 (dst/'config.json').write_text(json.dumps(cfg,indent=2,sort_keys=True)+'\n')
 (dst/'qwen3_moe-observed.py').write_text(observed)
 (dst/'FUSION_SOURCE.json').write_text(json.dumps({'image':cfg['image'],'image_sha256':cfg['image_sha256'],'native_model_source_sha256':hashlib.sha256(base.encode()).hexdigest(),'observed_source_sha256':hashlib.sha256(observed.encode()).hexdigest(),'change':'Two startup-only observer lines after native fusion selection; no arithmetic or control-flow changes. Actual kernel invocation/timing is not traced.'},indent=2)+'\n')
 (dst/'PARENT_CHAIN.json').write_bytes((dst/'PARENT_BUNDLE.json').read_bytes())
 (dst/'PARENT_BUNDLE.json').write_text(json.dumps({'parent_bundle':str(PARENT.relative_to(ROOT)),'parent_sha256sums_sha256':hashlib.sha256((PARENT/'SHA256SUMS').read_bytes()).hexdigest(),'derivation_script':str(Path(__file__).relative_to(ROOT)),'derivation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
 edit(dst/'job.sbatch',str(PARENT),str(dst));edit(dst/'job.sbatch',PARENT.name+'-${SLURM_JOB_ID}',name+'-${SLURM_JOB_ID}');edit(dst/'job.sbatch','ap42-s65-rr',f'ap42-s{sid}-{stage}-qkr')
 edit(dst/'worker.sh','telemetry_flags=()',f'''if [[ $role == {stage} ]]; then
  extra+=(--enable-fused-qk-norm-rope)
fi
python3 - "$QWEN_BUNDLE/config.json" <<'PYFUSION'
import hashlib,json,sys
from pathlib import Path
cfg=json.loads(Path(sys.argv[1]).read_text())
p=Path('/sgl-workspace/sglang/python/sglang/srt/models/qwen3_moe.py')
assert hashlib.sha256(p.read_bytes()).hexdigest()==cfg['native_fusion_source_sha256'], 'fusion observer source hash mismatch'
PYFUSION
telemetry_flags=()''')
 edit(dst/'topology-job.sh','$BUNDLE/kv_geometry.py:/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/kv_geometry.py:ro', '$BUNDLE/kv_geometry.py:/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/kv_geometry.py:ro,$BUNDLE/qwen3_moe-observed.py:/sgl-workspace/sglang/python/sglang/srt/models/qwen3_moe.py:ro')
 edit(dst/'check-fast-runtime.py',"roles={'prefill-0':4,'prefill-1':4,'decode-0':8}; evidence={}","roles={'prefill-0':4,'prefill-1':4,'decode-0':8}; evidence={}\nfusion_cfg=json.loads((Path(__file__).resolve().parent/'config.json').read_text())")
 edit(dst/'check-fast-runtime.py',"    spec={'speculative_algorithm'",'''    fused_expected=role in fusion_cfg['fused_qk_norm_rope_roles']
    if lit(args,'enable_fused_qk_norm_rope',role) is not fused_expected:
        raise ValueError(f'{role}: actual native fusion flag differs')
    selection=re.findall(r'TP(\\d+)(?: EP\\d+)?\\] FUSED_QK_ROPE_SELECTION selected=(True|False) head_dim=(\\d+)',text)
    if collections.Counter(x[0] for x in selection)!=collections.Counter(map(str,range(nranks))):
        raise ValueError(f'{role}: native fusion-selection ranks missing or duplicated')
    if {(x[1],x[2]) for x in selection}!={(str(fused_expected),'128')}:
        raise ValueError(f'{role}: native fusion selection fell back or geometry differs')
    spec={'speculative_algorithm' ''')
 # Reparse the actual resolved flag independently in the final head check as well.
 edit(dst/'check-performance.py',"needed={'max_running_requests'", "needed={'enable_fused_qk_norm_rope','max_running_requests'")
 edit(dst/'check-performance.py',"        assert a['max_running_requests']==cap", "        assert a['enable_fused_qk_norm_rope'] is (role in cfg['fused_qk_norm_rope_roles'])\n        assert a['max_running_requests']==cap")
 (dst/'README.md').write_text(f'# S{sid}: native fusion on {stage} only\n\nDerived from frozen S65, compared with actual control 26083. Read PLAN.md. Submit from qwen-experiments; 16 H200/two nodes/17-minute cap/no PBS SU. Native selected-versus-fallback flags must pass on every rank before scoring. Official quality remains UNKNOWN.\n')
 (dst/'PLAN.md').write_text(f'''# Phase-isolated native QK norm/RoPE fusion: {stage}

Question: can combining per-head Q/K RMS normalization and rotary position embedding reduce launches/intermediate memory traffic on {stage}, without changing target weights, precision or the workload? This is a hypothesis, not an established bottleneck. Recent S63 telemetry shows incomplete sampled GPU-active time and TTFT-sensitive goodput; neither establishes where fusion will help.

The exact deployed image's Qwen3MoeAttention selects native fused QK norm/RoPE when explicitly enabled, CUDA, supported head_dim (64/128/256), compatible rotary embedding and successful BF16 JIT build. Current model head_dim is128. S65 actual baseline native flags are false. A bounded scan of130 serving configs found no explicit fusion study; this is not proof of complete historic coverage. S66 enables it on both prefill workers only; S67 enables it on decode only. Arithmetic/target weights are not patched. Two startup-only observer lines expose the native per-rank selection. A fallback or wrong flag fails before scoring; selected configuration is not a kernel-time trace.

Match actual fresh S65 control26083: P8-TP4/D8-TP8-EP8,16 H200, target-only FP8 checkpoint with BF16 activation/KV, identical image/kernel defaults/graph batches/NIXL, round-robin, N64,4000/200, seed2026, cold prefixes,20/40/30 short screen, all source/runtime/KV/semantic/output checks. The image's can_use helper may fail to build a JIT kernel; this is an unresolved GPU prerequisite. Accuracy drift remains possible from changed operation fusion; smoke/retrieval checks do not establish the official99% full-set requirement.

Need >=90% joint TTFT<=3000ms / request-mean ITL<=20ms, zero profiling errors/cancellations, complete raw denominator, no smoke regression below7/8, retrieval12/12. Advance an arm only if all gates pass and good output tokens/s is at least3% above actual fresh control26083. If control fails, no historical substitution or gain claim. Otherwise close the losing arm. Independently confirm useful short results with full matched scoring before adoption; current full H200 frontier3044.400475 remains.

Admission:16 H200/two nodes/17minutes maximum per job, cap5 total including existing jobs. Scheduler afterany:26083 preserves matching control order without an unsatisfiable afterok chain; control failure still disqualifies comparison. No PBS SU. Frozen parents stay unchanged. Inspect phase-bounded GPU/CPU/VRAM/queues/KV and all errors/tails beyond score, mark missing data explicitly. No heavy profile or background Codex.
'''.replace('is128','is 128').replace('of130','of 130').replace('control26083','control 26083').replace(',16',', 16').replace('N64,4000','N64, 4000').replace('seed2026','seed 2026').replace('prefixes,20','prefixes, 20').replace('official99','official 99').replace('below7','below 7').replace('retrieval12','retrieval 12').replace('least3','least 3').replace('frontier3044','frontier 3044').replace('Admission:16','Admission: 16').replace('17minutes','17 minutes').replace('cap5','cap 5'))
 for p in dst.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 for p in list(dst.glob('*.sh'))+[dst/'job.sbatch']:subprocess.run(['bash','-n',str(p)],check=True)
 (dst/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in sorted(dst.iterdir()) if p.is_file() and p.name!='SHA256SUMS'))
 subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=dst,check=True,stdout=subprocess.DEVNULL)
 print(name,'CPU syntax and hashes PASS')
