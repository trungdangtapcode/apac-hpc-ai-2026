"""Derive a portable N62 submission from reviewed job 24915, not its diagnostics."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil

W = Path('/home/apacsc42/workspace')
R = Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
O = W / 'submission-review/full-update-2026-10-21'
T = O / 'VNUHCM - TripleU'
OLD = W / 'VNUHCM - TripleU'
SOURCE = R / 'runs/24915/submitted'
assert not T.exists(), 'Do not overwrite an existing review stage'
shutil.copytree(OLD, T)
S = T / 'AI_Task/job_scripts'
L = T / 'AI_Task/logs'
assert not any(p.is_file() for p in (T / 'HPC_Task').rglob('*'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
write = lambda p, d: p.write_text(json.dumps(d, indent=2) + '\n')
for name in ['worker.sh', 'warm-topology.py', 'placement.tsv', 'nixl-conn.py']:
    shutil.copyfile(SOURCE / name, S / name)
shutil.copyfile(W / 'submission-tools/score-gate.py', S / 'score-gate.py')
deployment = (S / 'deploy-and-benchmark.sh').read_text()
deployment = deployment.replace('--pd-disaggregation "${router_args[@]}"', '--pd-disaggregation --prefill-policy round_robin "${router_args[@]}"')
deployment = deployment.replace('run N48 once', 'run N62 once')
deployment += '\npython3 "$TASK_SCRIPTS/score-gate.py" "$ART" "$TRIPLEU_CONCURRENCY" >"$ART/performance-gate.json"\n'
(S / 'deploy-and-benchmark.sh').write_text(deployment)
(S / 'submit.sbatch').write_text((S / 'submit.sbatch').read_text().replace('TRIPLEU_CONCURRENCY=48', 'TRIPLEU_CONCURRENCY=62'))
(S / 'official-benchmark.sh').write_text((S / 'official-benchmark.sh').read_text().replace('TRIPLEU_CONCURRENCY:-48', 'TRIPLEU_CONCURRENCY:-62'))
config = json.loads((SOURCE / 'config.json').read_text())
config.update(declared_concurrency=62, diagnostic_profile=False, long_context_diagnostic=False,
              tier='Basic', speculative_decoding=False, measured_evidence_job='24915',
              benchmark_warmup_s=60, benchmark_measure_s=120, benchmark_grace_s=30,
              packaging_note='One-point portable replay. No research sweep, output suite or post-score profiler in the primary job.')
write(S / 'config.json', config)
environment = json.loads((S / 'environment.json').read_text())
environment['rules_snapshot_commit'] = 'b4df52907f5bbb9152ef6ae902c925fc79d54417'
environment['serving_source_job'] = '24915'
write(S / 'environment.json', environment)
(S / 'README.md').write_text('''# TripleU Qwen Basic deployment

The declared point is **N62 on two 8-GPU H200 nodes**. Two TP4/EP1 prefill
workers on the first node feed one TP8/EP8 decode worker on the second.
Prefill uses DeepGEMM and chunk8192. Decode uses HPC-Ops, FlashInfer attention,
MNNVL collectives and dense CUDA graph sizes 1–64. Routing is round-robin.
The official published FP8 target, BF16 KV and request-scoped NIXL patch are
retained. There is no speculative decoding in this submission.

## Reconstruct and run

Reuse the organiser images and official FP8 checkpoint specified, with hashes
and versions, in environment.json. No image rebuild is required. setup.sh
checks image sizes and model metadata; --verify-images also hashes the images.
The included text nixl.patch and full nixl-conn.py are mounted read-only into
each worker. Its hash is checked before serving. The patch preserves KV byte
geometry and computation while preparing only the request's transfer pages.
The pinned public tokenizer cache is included; model weights are not included.

Required host tools: Slurm with Pyxis/enroot, Python 3, curl and sha256sum.
The organiser SGLang image must include the recorded HPC-Ops kernels.
TRIPLEU_SGLANG_IMAGE, TRIPLEU_AIPERF_IMAGE and TRIPLEU_MODEL_PATH can relocate
the exact same external objects. Paths and scripts do not depend on a team
account. Place the package on storage shared by both allocated nodes.

```bash
cd 'VNUHCM - TripleU/AI_Task/job_scripts'
bash setup.sh --check
# Optional full image digest check:
bash setup.sh --verify-images
sbatch submit.sbatch
```

Submit from this directory, or use sbatch --chdir with its absolute path.
The single job allocates all 16 GPUs for at most 17 minutes, deploys all workers
and the gateway, warms each transfer path with separate setup prompts, and
runs the official AIPerf command once at N62. It retains closed-loop 4000/200,
seed2026, cold-prefix cache busting, 60s warmup / 120s scoring / 30s grace,
and the original TTFT3000ms / request-mean ITL20ms goodput thresholds.
The exported goodput in requests/s multiplied by200 is the score in good
output tokens/s; the joint good fraction must be at least0.90.

Output: ../logs/slurm/<job>.out/.err and ../logs/reruns/<job>/official/n62/.
performance-gate.json independently rejects missing/incomplete/error/SLA-failed
artifacts even when a client or scheduler reports exit0. It reads existing
exports and requests after the unchanged client command; it does not modify
benchmark traffic or recalculate goodput from a guessed window duration.

## Evidence and limits

Reviewed source job24915: 3022.034919 good output tokens/s, 1860/1884 good
requests (98.726115%), zero errors/cancellations. This is one local N62
observation. Its independent repeat24962 was still pending at packaging.
N60 independently repeated at2990.150791 and2989.174711; see the retained raw
exports and results table for exact values. All platform comparisons remain
separate. The portable entry point is statically checked and exercised with
mock orchestration and replayed artifacts; it has no separate GPU replay yet.

The organiser full-set accuracy check (at least99% of reference) remains
unverified. Small output checks and SLA acceptance do not certify it.
See ../logs/README.md for measured evidence, review scope and reproduction status.

Rules: https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/1.%20Qwen3%20AI%20Task%20Rules.md
'''.replace('seed2026','seed 2026').replace('by200','by 200').replace('least0.90','least 0.90').replace('exit0','exit 0').replace('job24915','job 24915').replace('repeat24962','repeat 24962').replace('at2990','at 2990').replace('and2989','and 2989').replace('least99%','least 99%').replace('TTFT3000ms / request-mean ITL20ms','TTFT 3000 ms / request-mean ITL 20 ms'))
files = [p for p in sorted(S.rglob('*')) if p.is_file() and p.name != 'SHA256SUMS']
(S / 'SHA256SUMS').write_text(''.join('{}  {}\n'.format(sha(p), p.relative_to(S)) for p in files))
write(O / 'script-provenance.json', dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), source_job='24915',
    exact_components={name: sha(S/name) for name in ['worker.sh','warm-topology.py','placement.tsv','nixl-conn.py']},
    derived_components=['submit.sbatch','deploy-and-benchmark.sh','official-benchmark.sh','config.json'],
    added_gate='score-gate.py', gpu_replayed=False, official_accuracy_verified=False))
print(T)
