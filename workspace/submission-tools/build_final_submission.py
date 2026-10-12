"""Stage an English-only submission using the measured winning serving stack."""
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE=Path('/home/apacsc42/workspace')
OLD=WORKSPACE/'VNUHCM - TripleU'
STAGE=WORKSPACE/'submission-staging'/'VNUHCM - TripleU'
EXP=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
SOURCE=EXP/'runs/22415/submitted'
SCRIPTS=STAGE/'AI_Task/job_scripts'
LOGS=STAGE/'AI_Task/logs'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def write(p,text):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def js(p,obj):write(p,json.dumps(obj,indent=2)+'\n')
def cp(a,b):b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a,b)

assert not STAGE.exists(),'Refuse to overwrite an existing stage'
for name in ('Presentation','AI_Task/job_scripts','AI_Task/logs','HPC_Task/job_scripts','HPC_Task/logs'):
    (STAGE/name).mkdir(parents=True)

for name in ('worker.sh','warm-topology.py','summarize.py','placement.tsv','nixl-conn.py'):
    cp(SOURCE/name,SCRIPTS/name)
cp(SOURCE/'nixl-ondemand.patch',SCRIPTS/'nixl.patch')
cp(SOURCE/'nixl-patch-metadata.json',SCRIPTS/'patch-metadata.json')
cp(SOURCE/'nixl-geometry-test.json',SCRIPTS/'patch-geometry-test.json')
for name in ('setup.sh','official-benchmark.sh'):
    cp(OLD/'AI_Task/job_scripts'/name,SCRIPTS/name)
shutil.copytree(OLD/'AI_Task/job_scripts/hf-cache',SCRIPTS/'hf-cache')
cp(OLD/'AI_Task/job_scripts/tokenizer-provenance.json',SCRIPTS/'tokenizer-provenance.json')

config=json.loads((SOURCE/'config.json').read_text())
config.update(concurrency=[48],declared_concurrency=48,tier='Basic',speculative_decoding=False,
    measured_evidence_job='22415',benchmark_warmup_s=60,benchmark_measure_s=120,benchmark_grace_s=30,
    packaging_note='Package-relative one-point replay of the measured winning stack; official client command unchanged.')
for key in ('sweep_warmup_s','sweep_measure_s','phase','original_job','is_prefill_ep_variant','required_measurement_transport'):
    config.pop(key,None)
js(SCRIPTS/'config.json',config)
env=json.loads((OLD/'AI_Task/job_scripts/environment.json').read_text())
env.update(method='Reuse the recorded organiser images and published checkpoint; mount the included patched NIXL conn.py read-only in each serving worker. No image rebuild or model changes.',
           rules_snapshot_commit='3d050964d1008b97fb6d0d7ec5160087cd6883d9',
           transport_patch=json.loads((SCRIPTS/'patch-metadata.json').read_text()))
js(SCRIPTS/'environment.json',env)

deployment=(OLD/'AI_Task/job_scripts/deploy-and-benchmark.sh').read_text()
deployment=deployment.replace('  printf \'%s\' "/scratch:/scratch,$local_home:$HOME,$TASK_ROOT:$TASK_ROOT"',
'''  local patch_mount=""
  case "$1" in
    prefill-*|decode-*)
      patch_mount=",$TASK_SCRIPTS/nixl-conn.py:/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py:ro"
      ;;
  esac
  printf '%s' "/scratch:/scratch,$local_home:$HOME,$TASK_ROOT:$TASK_ROOT$patch_mount"''')
assert 'patch_mount=' in deployment
deployment=deployment.replace('  role=${name%%-*}\n','  role=${name%%-*}\n  nccl_port=$((20000+port-30100))\n')
deployment=deployment.replace('"$MODEL" "$tp" "${extra[@]}"','"$MODEL" "$tp" --nccl-port "$nccl_port" "${extra[@]}"')
deployment=deployment.replace('env QWEN_PAIR_TIMEOUT=360 python3', 'env QWEN_PAIR_TIMEOUT=480 QWEN_PAIR_PARALLELISM=8 python3')
deployment=deployment.replace('run N40 once','run N48 once')
write(SCRIPTS/'deploy-and-benchmark.sh',deployment)
command=(SCRIPTS/'official-benchmark.sh').read_text().replace('TRIPLEU_CONCURRENCY:-40','TRIPLEU_CONCURRENCY:-48')
write(SCRIPTS/'official-benchmark.sh',command)
write(SCRIPTS/'submit.sbatch','''#!/bin/bash
#SBATCH --job-name=TripleU-Qwen-Basic
#SBATCH --partition=hpcai
#SBATCH --nodes=2
#SBATCH --time=00:17:00
#SBATCH --gres=gpu:8
#SBATCH --exclusive
#SBATCH --propagate=NONE
#SBATCH --output=../logs/slurm/%j.out
#SBATCH --error=../logs/slurm/%j.err
set -euo pipefail
# Run setup.sh first, then submit from AI_Task/job_scripts (or use --chdir).
TASK_SCRIPTS=${SLURM_SUBMIT_DIR:?Submit this script through Slurm}
cd "$TASK_SCRIPTS"
sha256sum --check SHA256SUMS
export TRIPLEU_CONCURRENCY=48
export QWEN_NIXL_PATCH_SHA256=912b7edb95b03604354cc0137f111756ed5bb0eaa91345b5bf5024f
exec bash "$TASK_SCRIPTS/deploy-and-benchmark.sh"
'''.replace('912b7edb95b03604354cc0137f111756ed5bb0eaa91345b5bf5024f',env['transport_patch']['patched_sha256']))

write(SCRIPTS/'README.md','''# TripleU — APAC HPC-AI 2026 Qwen Basic submission

## Declared configuration

**P8-TP4_D8-TP8-EP8, concurrency 48, 16 H200 GPUs.** Node 0 has two prefill
workers (4 GPUs each, TP4/EP1). Node 1 has one decode worker (8 GPUs,
TP8/EP8). Every benchmark request uses the PD gateway. Published FP8 weights,
BF16 KV, no speculative decoding, no model or expert/layer changes.

The NIXL patch is enabled in the primary script. It changes heterogeneous-TP
KV descriptor preparation to operate on request pages instead of the whole
pool; byte geometry, head mapping and notifications are retained. The text
diff is `nixl.patch`, the mounted source is `nixl-conn.py`, and both original
and patched hashes are in `patch-metadata.json`. The worker verifies the
mounted source hash before launching SGLang. The patch passed 720 CPU
byte-range comparisons and served the measured GPU run.

## Rebuild the serving environment

Use the exact organiser-provided SGLang/Pyxis image and AIPerf image recorded
in `environment.json`, and the official published
`Qwen3-235B-A22B-Instruct-2507-FP8` checkpoint. The defaults use the organiser
shared `/scratch` paths. No model weights or image binaries are bundled.
No image rebuild is necessary: the script mounts the included `nixl-conn.py`
read-only at the image's SGLang NIXL module path for prefill/decode workers.
The original image and checkpoint stay unchanged. The pinned offline
tokenizer cache is included.

Required host tools: Slurm, Pyxis/enroot, Python 3, curl and sha256sum.
Worker containers use SGLang 0.5.17, router 0.3.2 and NIXL 1.3.2;
the client image uses AIPerf 0.12.0. External image/model paths can be
overridden using `TRIPLEU_SGLANG_IMAGE`, `TRIPLEU_AIPERF_IMAGE` and
`TRIPLEU_MODEL_PATH`; the staged files must match the recorded environment.

```bash
cd 'VNUHCM - TripleU/AI_Task/job_scripts'
bash setup.sh --check
# Optional full SHA256 check of the two external images:
bash setup.sh --verify-images
sbatch submit.sbatch
```

Submit from this directory, or pass its absolute path with `sbatch --chdir`.
No team account or home directory is hardcoded. The single 17-minute job
allocates two nodes and 16 GPUs, deploys the three workers and gateway,
initializes the two P/D paths using separate setup prompts, then invokes
the exact official closed-loop AIPerf command **once at N48**. There is no
sweep in this entry point. Official timings remain 60/120/30; input/output
lengths remain 4000/200, seed 2026 and both original SLA thresholds.

Slurm output is in `../logs/slurm/`; replay outputs are in
`../logs/reruns/<job>/official/n48/`. Source worker/placement/setup geometry
match measured job 22415; only submission paths and one-point client
orchestration are made portable.

## Evidence and status

Job **22415**, N48 long run: **1912.299955 good output tokens/s**,
**97.440132% SLA**, **1180/1211** good requests, zero errors/cancellations.
This is local evidence, not an official organiser score. The packaged
portable orchestration has static and mock validation; its own GPU replay
status is recorded in `../logs/replay-status.json`.
The organiser full-set accuracy check and official re-verification are
not yet available. No quality pass is claimed.

Rule source (verified at commit 3d050964d1008b97fb6d0d7ec5160087cd6883d9):
https://github.com/hpcac/2026-APAC-HPC-AI/blob/3d050964d1008b97fb6d0d7ec5160087cd6883d9/1.%20Qwen3%20AI%20Task%20Rules.md
Submission Guidelines require build instructions, one deploy-and-benchmark
Slurm/PBS script, and slides. Q1 permits serving patches that preserve
the model computation; the text patch is supplied for judge review.
''')

# Preserve the local measured records, without translating or editing raw data.
for job,n in (('22197',32),('22219',40),('22415',48),('22809',32)):
    run=EXP/'runs'/job;target=LOGS/'measured'/job
    for suffix in ('.out','.err'):
        p=EXP/'runs'/(job+suffix)
        if p.exists():cp(p,target/('slurm'+suffix))
    for p in run.iterdir():
        if p.is_file() and (p.suffix=='.log' or p.name in ('config.json','summary.json','endpoints.tsv')):
            cp(p,target/p.name)
    for point in run.glob('*/n*/artifacts/profile_export_aiperf.json'):
        if point.parent.parent.parent.name!='confirm' and job!='22415':continue
        for name in ('client.log','artifacts/profile_export_aiperf.json','artifacts/profile_export_aiperf.csv',
                     'artifacts/profile_export.jsonl','artifacts/profile_export_console.txt','artifacts/logs/aiperf.log'):
            p=point.parent.parent/name
            if p.exists():cp(p,target/p.relative_to(run))

data=json.loads((OLD/'Presentation/presentation-data.json').read_text())
data['previous_best']=data['declared_basic'];data['declared_basic']=data['best']
data['snapshot_utc']=datetime.now(timezone.utc).isoformat()
for key in ('best','previous_best','declared_basic','baseline','patch','equal_patch'):
    if key in data:data[key]['export']=data[key]['export'].replace('logs/runs/','logs/measured/')
for m in data['results']:m['export']=m['export'].replace('logs/runs/','logs/measured/')
js(STAGE/'Presentation/presentation-data.json',data)
js(LOGS/'results.json',data['results'])
cp(OLD/'AI_Task/logs/results.csv',LOGS/'results.csv')
with (LOGS/'results.csv').open() as f:entries=list(csv.DictReader(f));fields=list(entries[0])
for row in entries:row['export']=row['export'].replace('logs/runs/','logs/measured/')
with (LOGS/'results.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(entries)
js(LOGS/'coverage.json',data['coverage'])
js(LOGS/'replay-status.json',{'declared_config':config['id'],'concurrency':48,
    'measured_source_job':'22415','portable_gpu_replay_job':None,
    'portable_gpu_replay_state':'NOT_SUBMITTED','accuracy_verified':False,'officially_submitted':False})
write(LOGS/'README.md','''# Qwen measured evidence

`measured/22415` contains the winning worker/router/client logs, all four
short sweeps and the long N48 export. Its long-run goodput × 200 is
1912.2999551030798 good tokens/s, with 1180/1211 passing both SLAs.
`measured/22219` is the previous best (1666.0095960803812 at N40);
`measured/22197` is the measured starting baseline (1297.0178084383886 at N32).
`measured/22809` records the final repaired TP8/EP2 layout (1507.960592 at N32).
The observed 14.78% improvement over 22219 includes topology, concurrency
and transport changes; it is not an isolated patch speedup measurement.

`coverage.json` distinguishes 14 measured original layouts and three
measured EP2 replacements from the three FP8-block-incompatible EP1 originals.
`results.json`/CSV retain the 89 recorded points for the search; detailed
logs for the selected comparison runs are bundled. Other raw search logs
remain in the team's experiment workspace. All bundled raw exports and
per-request records are byte-identical to their measured sources. Inputs
are generated by the unchanged official client and are not bundled here.

`replay-status.json` distinguishes the new portable replay from original
job 22415 evidence. Full-set accuracy and organiser acceptance are pending.
''')
for where in ('job_scripts','logs'):
    write(STAGE/'HPC_Task'/where/'STATUS.txt','No HPC task scripts or measurements were supplied for this Qwen-scoped package. No HPC result is claimed.\n')

for p in SCRIPTS.iterdir():
    if p.suffix in ('.sh','.sbatch'):p.chmod(0o755)
files=[p for p in sorted(SCRIPTS.rglob('*')) if p.is_file() and p.name!='SHA256SUMS']
write(SCRIPTS/'SHA256SUMS',''.join(f'{sha(p)}  {p.relative_to(SCRIPTS)}\n' for p in files))
print(json.dumps({'stage':str(STAGE),'declared':config['id'],'concurrency':48,'patch':config['transport_patch']},indent=2))
