"""Freeze a reviewable submission from completed Qwen evidence; never submit jobs."""
import csv
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE=Path('/home/apacsc42/workspace')
SOURCE=Path('/home/apacsc42/2026-APAC-HPC-AI')
EXP=SOURCE/'qwen-experiments'
DEST=WORKSPACE/'VNUHCM - TripleU'
AI=DEST/'AI_Task'
SCRIPTS=AI/'job_scripts'
LOGS=AI/'logs'
NOW=datetime.now(timezone.utc).isoformat()

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()

def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding='utf-8')

def js(path,obj):write(path,json.dumps(obj,indent=2,ensure_ascii=False)+'\n')

copied=[]
def cp(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,dst)
    copied.append({'source':str(src),'destination':str(dst.relative_to(DEST)),
                   'bytes':dst.stat().st_size,'sha256':sha(dst)})

def main():
    for sub in ('Presentation','HPC_Task/job_scripts','HPC_Task/logs','AI_Task/logs/slurm','AI_Task/logs/reruns'):
        (DEST/sub).mkdir(parents=True,exist_ok=True)
    original=json.loads((EXP/'topology-sweep/registry.json').read_text())
    recovery=json.loads((EXP/'topology-repair/recovery.json').read_text())
    js(LOGS/'snapshots/recovery.json',recovery)
    js(LOGS/'snapshots/topology-registry.json',original)
    status=subprocess.run(['sacct','-u','apacsc42','-S','2026-10-09T00:00:00','-X','-P',
                           '--format=JobID,State%30,ExitCode,Elapsed,Start,End,AllocTRES'],
                          capture_output=True,text=True,check=True).stdout
    write(LOGS/'snapshots/slurm-accounting.txt',status)
    status_rows={r['JobID']:r for r in csv.DictReader(status.splitlines(),delimiter='|')}
    queue=subprocess.run(['squeue','-u','apacsc42','-o','%.18i %.30j %.2t %.10M %.25R'],capture_output=True,text=True,check=True).stdout
    write(LOGS/'snapshots/queue.txt',queue)

    final='22219'
    bundle=EXP/'runs'/final/'submitted'
    # Keep verified worker/pair initialization behavior, with only paths made portable.
    for filename in ('worker.sh','warm-topology.py','placement.tsv','summarize.py'):
        cp(bundle/filename,SCRIPTS/filename)
    config=json.loads((bundle/'config.json').read_text())
    config.update(concurrency=[40],prefill_ep=1,declared_concurrency=40,
                  tier='Basic',speculative_decoding=False,transport_patch=None,
                  measured_evidence_job='22219',benchmark_warmup_s=60,
                  benchmark_measure_s=120,benchmark_grace_s=30,
                  packaging_note='Portable one-point replay derived from the measured job; not yet GPU-run as a packaged script.')
    js(SCRIPTS/'config.json',config)
    cache=EXP/'hf-cache/models--Qwen--Qwen3-235B-A22B-Instruct-2507'
    for src in sorted(cache.rglob('*')):
        if src.is_file():cp(src,SCRIPTS/'hf-cache'/cache.name/src.relative_to(cache))
    cp(EXP/'tokenizer-cache.json',SCRIPTS/'tokenizer-provenance.json')
    model=Path(config['model'])
    cp(model/'config.json',LOGS/'environment/model-config.json')
    cp(model/'model.safetensors.index.json',LOGS/'environment/model.safetensors.index.json')
    metadata_root=Path('/tmp/apac42-submission-image-meta/usr/local/lib/python3.12/dist-packages')
    for package in ('sglang-0.5.17','nixl-1.3.2','sglang_router-0.3.2'):
        cp(metadata_root/(package+'.dist-info')/'METADATA',LOGS/'environment'/(package+'-METADATA.txt'))
    image_specs=[]
    for name,digest,variable in (
        ('sglang-harbor.sqsh','b74ae77446bfedd6c5d72820b45be255cc513cf7c7c039d1bf63679c8178bfe5','TRIPLEU_SGLANG_IMAGE'),
        ('aiperf.sqsh','58fc1cbc2aec897fe39bf74d8f38f055b63c3690429162134f818d9597d22c0a','TRIPLEU_AIPERF_IMAGE')):
        p=Path('/scratch/enroot-images')/name
        image_specs.append({'path':str(p),'bytes':p.stat().st_size,'sha256':digest,'override_environment_variable':variable})
    env={'method':'Reuse the exact organiser-provided enroot/Pyxis images on shared storage; no custom image build and no serving-code patch in the declared Basic stack.',
         'container_images':image_specs,
         'model':{'id':'Qwen/Qwen3-235B-A22B-Instruct-2507-FP8','path':str(model),
                  'metadata_sha256':{name:sha(model/name) for name in ('config.json','model.safetensors.index.json')},
                  'precision':'Published FP8 weights; BF16 KV (kv_cache_dtype=auto, dtype torch.bfloat16 evidenced in worker logs)',
                  'weight_shards_not_included':True},
         'versions':{'sglang':'0.5.17','sglang_router':'0.3.2','nixl':'1.3.2','aiperf':'0.12.0',
                     'transformers_client':'5.14.1','tokenizers_client':'0.22.2'},
         'tokenizer':{'id':'Qwen/Qwen3-235B-A22B-Instruct-2507','revision':'ac9c66cc9b46af7306746a9250f23d47083d689e',
                      'included_cache':'hf-cache','tokenizer_json_sha256':sha(model/'tokenizer.json')},
         'rules_snapshot_commit':subprocess.run(['git','rev-parse','HEAD'],cwd=SOURCE,capture_output=True,text=True,check=True).stdout.strip(),
         'accuracy_check':'NOT_RUN; no reference quality score or organiser verification result available'}
    js(SCRIPTS/'environment.json',env)
    for name in ('README.md','1. Qwen3 AI Task Rules.md','2. OpenFOAM HPC Task Rules.md','3.1 Qwen3 Application Notes - Firmus AI Cloud.md'):
        cp(SOURCE/name,LOGS/'rules'/name)

    # Archive immutable job payloads, including failed deployments. No mutable
    # container-home trees or credentials are traversed or copied.
    jobs={e['job']:e['bundle'] for e in original['experiments']}
    for e in recovery['entries']:
        for a in e['attempts']:jobs[a['job']]=a['bundle']
    for job in ('22197','22200','22131'):
        p=EXP/'runs'/job/'submitted'
        jobs[job]=str(p if p.exists() else EXP/'runs'/job)
    for job,bundle_path in sorted(jobs.items(),key=lambda kv:int(kv[0])):
        src_bundle=Path(bundle_path)
        for f in sorted(src_bundle.iterdir()):
            if f.is_file() and (f.suffix in ('.sh','.py','.sbatch','.patch','.json') or f.name in ('placement.tsv','SHA256SUMS')):
                cp(f,SCRIPTS/'archive'/job/f.name)
    terminal={'COMPLETED','FAILED','TIMEOUT','CANCELLED','NODE_FAIL','OUT_OF_MEMORY','PREEMPTED'}
    results=[]
    included_jobs=[]
    for job in sorted(jobs,key=int):
        st=status_rows.get(job,{})
        if st.get('State','').split()[0].rstrip('+') not in terminal:continue
        run=EXP/'runs'/job
        included_jobs.append(job)
        for suffix in ('.out','.err'):
            f=EXP/'runs'/(job+suffix)
            if f.is_file():cp(f,LOGS/'runs'/job/('slurm'+suffix))
        if not run.exists():continue
        for f in sorted(run.iterdir()):
            if f.is_file() and (f.suffix in ('.log','.txt','.tsv') or f.name in ('config.json','summary.json','artifact-manifest.json')):
                cp(f,LOGS/'runs'/job/f.name)
        if (run/'pair-warmup').exists():
            for f in sorted((run/'pair-warmup').glob('*.log')):cp(f,LOGS/'runs'/job/'pair-warmup'/f.name)
        for export in sorted(run.glob('*/n*/artifacts/profile_export_aiperf.json')):
            point=export.parent.parent
            for name in ('client.log','artifacts/profile_export_aiperf.json','artifacts/profile_export_aiperf.csv',
                         'artifacts/profile_export.jsonl','artifacts/profile_export_console.txt',
                         'artifacts/phase_manifest.json','artifacts/logs/aiperf.log'):
                f=point/name
                if f.is_file():cp(f,LOGS/'runs'/job/f.relative_to(run))
        if (run/'summary.json').exists():
            c=json.loads((run/'config.json').read_text()) if (run/'config.json').exists() else {}
            for m in json.loads((run/'summary.json').read_text()):
                source_export=Path(m['export'])
                if not source_export.is_file():continue
                rel=source_export.relative_to(run)
                record={'job':job,'topology':c.get('id',c.get('topology','baseline07' if job=='22197' else 'candidate09')),
                        'transport_patch':c.get('transport_patch'),**m}
                record['export']=str((LOGS/'runs'/job/rel).relative_to(DEST))
                record['is_long_confirmation']=m['phase']=='confirm'
                results.append(record)
    # Keep the complete selected input corpus once, rather than 228 MB per point.
    dataset=EXP/'runs/22219/confirm/n40/artifacts/inputs.json'
    cp(dataset,LOGS/'dataset/job-22219-confirm-n40-inputs.json')
    js(LOGS/'dataset/provenance.json',{'source_job':'22219','point':'confirm/n40','file':'job-22219-confirm-n40-inputs.json',
       'sha256':sha(dataset),'bytes':dataset.stat().st_size,'entries':12800,'seed':2026,
       'note':'Original AIPerf-generated synthetic inputs, unmodified. Other points retain metrics and client configuration; repeated inputs.json and duplicate phase exports are omitted from this package, preserved in source workspace.'})
    js(LOGS/'results.json',results)
    fields=['job','topology','transport_patch','phase','concurrency','good_output_tokens_s','raw_output_tokens_s',
            'good_request_fraction','sla_pass','requests','errors','cancelled_requests','ttft_avg_ms','itl_avg_ms',
            'ttft_p95_ms','itl_p95_ms','is_long_confirmation','export']
    with (LOGS/'results.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(results)
    exact=8+sum(e['benchmark_complete'] and not e['variant'] for e in recovery['entries'])
    variants=sum(e['benchmark_complete'] and e['variant'] for e in recovery['entries'])
    best=next(m for m in results if m['job']=='22219' and m['phase']=='confirm')
    latest_best=max((m for m in results if m['phase']=='confirm' and m['sla_pass']
                    and (m['requests'] or 0)>0 and m['cancelled_requests']==0),
                    key=lambda m:m['good_output_tokens_s'])
    equal_patch=next(m for m in results if m['job']=='22809' and m['phase']=='confirm')
    baseline=next(m for m in results if m['job']=='22197' and m['phase']=='confirm')
    patch=next(m for m in results if m['job']=='22294' and m['phase']=='confirm')
    coverage=[]
    for e in original['experiments']:
        repair=next((r for r in recovery['entries'] if r['index']==e['index']),None)
        original_rows=[m for m in results if m['job']==e['job']]
        exact_complete={m['concurrency'] for m in original_rows if m['phase']=='sweep' and (m['requests'] or 0)>0 and m['cancelled_requests']==0}=={16,32,40,48}
        if repair and not repair['variant']:exact_complete=repair['benchmark_complete']
        coverage.append({'index':e['index'],'original_topology':e['config']['id'],'original_job':e['job'],
                         'original_measured':exact_complete,
                         'variant_topology':repair['config']['id'] if repair and repair['variant'] else None,
                         'variant_measured':bool(repair and repair['variant'] and repair['benchmark_complete']),
                         'status':'Measured' if exact_complete else 'FP8 block incompatible' if repair and repair['variant'] else 'Awaiting measurements'})
    js(LOGS/'coverage.json',coverage)
    context={'snapshot_utc':NOW,'best':latest_best,'declared_basic':best,'baseline':baseline,'patch':patch,
             'equal_patch':equal_patch,'results':results,'coverage':coverage,
             'measured_originals':exact,'measured_variants':variants,
             'relative_gain_pct':100*(latest_best['good_output_tokens_s']/baseline['good_output_tokens_s']-1),
             'gain_over_declared_pct':100*(latest_best['good_output_tokens_s']/best['good_output_tokens_s']-1),
             'included_jobs':included_jobs,'environment':env}
    js(DEST/'Presentation/presentation-data.json',context)
    for f in sorted((EXP/'nixl-ondemand').iterdir()):
        if f.is_file():cp(f,SCRIPTS/'supplementary/nixl-ondemand'/f.name)
    for name in ('build-nixl-ondemand.py','test-nixl-ondemand.py'):
        cp(EXP/name,SCRIPTS/'supplementary'/name)
    for f in sorted((EXP/'nixl-equal-ondemand').iterdir()):
        if f.is_file():cp(f,SCRIPTS/'supplementary/nixl-equal-ondemand'/f.name)
    for name in ('build-nixl-equal-ondemand.py','test-nixl-equal-ondemand.py'):
        cp(EXP/name,SCRIPTS/'supplementary'/name)

    run_lines=['# Measured results and evidence','',f'Snapshot UTC: {NOW}','',
               f'Original configurations measured: **{exact}/17**. EP2 variants measured: **{variants}/3**, counted separately.',
               'Only actual exports count as measurements. Failed deployments and pending jobs are not performance results.','',
               '| Job | Topology | Phase / N | Good tokens/s | SLA fraction | Errors | Cancelled | Raw export |',
               '|---|---|---|---:|---:|---:|---:|---|']
    for m in results:
        rate=m['good_output_tokens_s']; fraction=m['good_request_fraction']
        link=Path(m['export']).relative_to('AI_Task/logs')
        run_lines.append(f"| {m['job']} | {m['topology']} | {m['phase']}/{m['concurrency']} | {rate:.2f} | {fraction:.2%} | {m['errors']} | {m['cancelled_requests']} | [JSON]({link}) |")
    write(LOGS/'RESULTS.md','\n'.join(run_lines)+'\n')
    coverage_lines=['# Coverage of the 17 original configurations','',f'Snapshot UTC: {NOW}','',
                    '| # | Original topology | Status | EP2 replacement | Replacement measured |',
                    '|---:|---|---|---|---|']
    for c in coverage:
        coverage_lines.append(f"| {c['index']} | {c['original_topology']} | {c['status']} | {c['variant_topology'] or '—'} | {c['variant_measured']} |")
    write(LOGS/'COVERAGE.md','\n'.join(coverage_lines)+'\n')
    write(SCRIPTS/'BUILD_AND_RUN.md',f'''# Reconstruct and run the declared Basic stack

This package uses the exact organiser-provided SGLang and AIPerf enroot images on Firmus shared storage. No custom serving source or image build is needed for the declared result. `environment.json` records image SHA256, image sizes, image package versions, model metadata hashes and the pinned tokenizer revision. Obtain those exact images and the published FP8 checkpoint from the organisers if the shared files are not already staged. A replacement image built from package version numbers alone is not claimed to be identical.

## Prerequisites

Slurm with enroot/Pyxis, the Firmus H200 nodes, active InfiniBand, shared `/scratch`, `curl`, Python 3 and standard shell tools. Container images and model remain external to this archive. No weights are copied, trained or requantised. The offline tokenizer cache is included, so the replay does not depend on the team's account or Hugging Face credentials.

## Prepare and submit

From an extracted package, go to `AI_Task/job_scripts`:

```bash
cd 'VNUHCM - TripleU/AI_Task/job_scripts'
bash setup.sh --check
# Optional full verification of the two external image files (~25 GiB + 779 MiB):
bash setup.sh --verify-images
sbatch submit.sbatch
```

If submitting from another directory, pass the absolute `AI_Task/job_scripts` directory using `sbatch --chdir=...`; this is required because Slurm executes a spooled script. `setup.sh` creates the Slurm output directory before submission.

The single submitted job allocates two nodes / 16 H200, starts 2 prefill workers (TP4/EP1) on node 0 and 2 decode workers (TP4/EP4) on node 1, starts the gateway on port 8000, initializes all four P/D paths through temporary gateways, shuts the temporary gateways down, then invokes the exact official AIPerf command once at N40. The official command still performs 60s warmup + 120s measurement + 30s grace. The temporary setup prompts are separate from the official dataset and seed, as allowed by Q1.

Results are written under `AI_Task/logs/reruns/<job>/official/n40/`; Slurm output is under `AI_Task/logs/slurm/`. AIPerf uses its default artifact directory because no extra flags are appended to the locked official command. Only the main `/v1/chat/completions` gateway is targeted by the official client. Per-worker logs record UCX device selection and GPU visibility.

All environment paths can be changed via `TRIPLEU_SGLANG_IMAGE`, `TRIPLEU_AIPERF_IMAGE`, and `TRIPLEU_MODEL_PATH`, exported before submission. They must still resolve to the exact staged files recorded in `environment.json`. The declared concurrency remains 40. These path overrides do not change model or benchmark settings.

## Provenance and validation status

The worker script, pair-initialization script, placement and metric parser come byte-for-byte from measured job 22219. The new wrapper makes paths relative to this package, removes exploratory sweeps and invokes the literal official command. A text diff against the measured wrapper is included. Static shell checks, protocol argument checks, topology checks and metric reproduction are recorded in `../logs/package-validation.json`. **The portable packaged wrapper has not yet been executed on GPU.** Existing job 22219 is performance evidence for the underlying configuration, not a claimed run of the new wrapper.

`archive/` holds original frozen payloads, including old absolute paths, for audit only. Run `submit.sbatch`, not archived scripts. The supplementary NIXL patch is not enabled by this Basic entry point.

## Accuracy

No full-set accuracy run or reference quality score is available in this workspace. We do not claim the 99% reference accuracy gate is passed. Organiser reconstruction, accuracy testing and official performance re-verification remain outstanding.
''')
    write(SCRIPTS/'supplementary/README.md','''# Supplementary transport work

The packaged Basic entry point remains the unpatched job-22219 configuration. These patches are included as separately labelled serving research and are not mounted by `submit.sbatch`.

Job 22415, P8-TP4_D8-TP8-EP8 / N48 with `hetero-tp-request-descriptors-v1`, is the current best local long run: 1912.30 good output tokens/s, 97.44% SLA, zero errors/cancellations. That is an observed 14.78% above job 22219 (1666.01); topology, concurrency and transport differ, so the gain is not isolated to the patch. The patch passed 720 CPU byte-range cases and real GPU benchmarks.

The separate `equal-tp8-request-descriptors-v1` passed 936 CPU range cases and 5 fallback guards. Job 22809 completed all four sweeps and long N32: 1507.96 good tokens/s, 95.38% SLA, zero errors/cancellations. N40/N48 sweeps miss the 90% gate. Source metadata with `gpu_validated: false` describes the pre-submission snapshot; later evidence is in `gpu-validation.json` and the immutable job logs. Prefill EP2 is a separate layout change.

Full-set accuracy and official organiser acceptance remain unverified for both stacks. Original frozen payloads, including source hashes, are under `archive/22415` and `archive/22809`; those historical scripts contain the team's paths and are audit evidence, not portable entry points.

To reproduce the CPU check independently, use Python with NumPy, then `python3 test-nixl-ondemand.py` from this directory. The patch, original/patched module and exact geometry helper are in `nixl-ondemand/`. Do not confuse this descriptor test with the competition's accuracy gate.

For the equal-TP patch, run `python3 test-nixl-equal-ondemand.py` here; the exact image helper sources are included under `nixl-equal-ondemand/`.
''')
    write(LOGS/'README.md','''# Evidence included

`RESULTS.md`, `results.json` and `results.csv` point to original canonical AIPerf exports. `runs/<job>/` preserves completed/failed worker logs, Slurm output, canonical metrics, per-request JSONL, client logs, configuration and provenance. `snapshots/` is a frozen view of the queue and recovery registry at packaging time. Its pending states do not update automatically after packaging.

Per-request JSONL contains warmup and profiling records; filter `metadata.benchmark_phase == "profiling"` for scored-window request statistics. Read canonical `profile_export_aiperf.json` for AIPerf goodput; multiply by 200. Short sweep measurements are labelled separately from long confirmation runs. Per-request SLA is not inferred from aggregate TTFT/ITL averages.

The selected input dataset is included once in `dataset/`, unmodified. Repeated `inputs.json`, duplicate phase exports, writable container homes, checkpoints and container binaries are omitted from the archive. Originals remain in the workspace. `artifact-manifest.json` files copied from source enumerate those original run trees and may refer to files omitted here; root `FILE_MANIFEST.json` and `SHA256SUMS` describe the delivered package.

Quality benchmark results and full generated response texts are not claimed to be archived. No official organiser score has been received.
''')
    write(DEST/'HPC_Task/job_scripts/README.md','''# HPC task status: no submission evidence available

The work in this workspace was explicitly scoped to Qwen. No OpenFOAM job script, contest-case preparation chain, decomposition dictionaries or solver run has been produced here. This directory preserves the requested package structure; it contains no executable or fabricated HPC submission.

The published general rules require a Basic result for both tasks. If HPC is required for TripleU's entry, obtain the actual HPC team's scripts/dictionaries and include the full preparation chain, official v2512 environment, and 1/2/4-node results before treating this as a complete two-task submission.
''')
    write(DEST/'HPC_Task/logs/README.md','''# No HPC measurements supplied

There are no 1/2/4-node simpleFoam logs, 4-node average wall-clock-per-step result, coefficient.dat or Cd correctness evidence in this workspace. No performance number or correctness claim is made for OpenFOAM.
''')
    write(DEST/'README.md',f'''# VNUHCM - TripleU — APAC HPC-AI 2026 submission snapshot

Prepared UTC: **{NOW}**. Team label follows the requested directory name. This is a **Qwen evidence package with an explicit incomplete HPC section**, prepared for review/upload. Nothing has been sent to the organisers.

## Current best measured result

**{latest_best['topology']}, N{latest_best['concurrency']}, job {latest_best['job']}, transport patch `{latest_best['transport_patch']}`:** **{latest_best['good_output_tokens_s']:.2f} good tokens/s**, **{latest_best['good_request_fraction']:.2%} SLA**, 0 errors/cancellations, long 60/120/30 measurement. The slides and raw evidence now include this result. It is a local measurement, not an organiser score. Full-set accuracy remains untested.

The portable `submit.sbatch` below retains the earlier unpatched Basic replay (job 22219). The new winning stack is supplied as raw evidence and a reviewable patch with its historical payload, and is not silently enabled in that portable wrapper.

## Declared AI configuration

**Basic: P8-TP4_D8-TP4-EP4, N40, 16 H200, official published FP8 checkpoint, unpatched provided serving image.** Two prefill workers (TP4/EP1) on one node; two decode workers (TP4/EP4) on the other. All official requests use PD through the OpenAI-compatible gateway. No draft model/speculative decoding, approximation, expert/layer skipping or additional quantization is used.

Job **22219**, long internal confirmation (60/120/30), achieved **{best['good_output_tokens_s']:.2f} good output tokens/s**, **{best['good_request_fraction']:.2%}** SLA fraction, **1034/1057** good requests, 0 errors and 0 cancelled requests. This is **local evidence, not an official organiser score**. The mean TTFT was {best['ttft_avg_ms']:.2f} ms and mean ITL {best['itl_avg_ms']:.2f} ms. The full accuracy gate remains untested.

## Files to review

- [Presentation](Presentation/TripleU_APAC2026_Presentation.pptx): English slides with Vietnamese speaker notes; matching PDF and Markdown guide included.
- [Build and replay instructions](AI_Task/job_scripts/BUILD_AND_RUN.md), [single Slurm entry point](AI_Task/job_scripts/submit.sbatch), [environment](AI_Task/job_scripts/environment.json).
- [Results and raw evidence](AI_Task/logs/RESULTS.md), [coverage of the 17 topologies](AI_Task/logs/COVERAGE.md).
- [NIXL research and current best stack](AI_Task/job_scripts/supplementary/README.md): not enabled by the declared entry point; local speed evidence is included, accuracy remains unverified.
- [HPC status](HPC_Task/job_scripts/README.md): no OpenFOAM results or scripts available.

## What remains outstanding

1. Full-set accuracy check: at least 99% of the organisers' FP8 reference score. No such pass is claimed.
2. Organiser reconstruction and official re-run; the portable packaged wrapper has only CPU/static validation so far.
3. All 17 usable layouts have been measured: {exact}/17 original configurations and {variants}/3 EP2 replacements. Three incompatible EP1 originals remain explicitly blocked; failed runs are not counted as measurements. Promote and GPU-validate a portable replay of the new winning stack before using it as the primary entry point.
4. HPC deliverables if the organisers require both tasks for this entry. The general published rules require Basic for each task; the user's active work scope here was Qwen only.

The organiser-provided .sqsh images and checkpoint are deliberately external; use the exact recorded shared-storage files. No private credentials or writable container-home directory is packaged. The root checksum and file manifest support integrity checks after extraction.

## Archive/upload

The sibling ZIP contains this directory as its top-level folder. Upload through the organiser's designated channel. This workspace does not contain a confirmed upload address or submission receipt; archive creation is not submission acceptance.
''')
    js(DEST/'submission-status.json',{'team':'VNUHCM - TripleU','snapshot_utc':NOW,'officially_submitted':False,
       'declared_basic':{'topology':config['id'],'concurrency':40,'evidence_job':'22219'},
       'best_local':{'topology':latest_best['topology'],'concurrency':latest_best['concurrency'],
                     'evidence_job':latest_best['job'],'transport_patch':latest_best['transport_patch'],
                     'good_output_tokens_s':latest_best['good_output_tokens_s'],
                     'good_request_fraction':latest_best['good_request_fraction']},
       'accuracy_verified':False,'hpc_evidence_available':False,'portable_replay_gpu_validated':False,
       'originals_measured':exact,'ep2_variants_measured':variants})
    js(LOGS/'copy-provenance.json',copied)
    # Human-reviewable wrapper change; original immutable source stays intact.
    import difflib
    diff=''.join(difflib.unified_diff((bundle/'topology-job.sh').read_text().splitlines(True),
             (SCRIPTS/'deploy-and-benchmark.sh').read_text().splitlines(True),
             fromfile='job-22219/topology-job.sh',tofile='submission/deploy-and-benchmark.sh'))
    write(SCRIPTS/'PORTABILITY.patch',diff)
    for f in SCRIPTS.glob('*.sh'):f.chmod(0o755)
    (SCRIPTS/'submit.sbatch').chmod(0o755)
    digest_paths=[f for f in sorted(SCRIPTS.iterdir()) if f.is_file() and f.name!='SHA256SUMS']
    digest_paths += [f for f in sorted((SCRIPTS/'hf-cache').rglob('*')) if f.is_file()]
    write(SCRIPTS/'SHA256SUMS',''.join(f'{sha(f)}  {f.relative_to(SCRIPTS)}\n' for f in digest_paths))
    print(json.dumps({'destination':str(DEST),'snapshot_utc':NOW,'copied_files':len(copied),
                     'originals_measured':exact,'ep2_variants_measured':variants,
                     'results':len(results),'best_good_tokens_s':latest_best['good_output_tokens_s'],
                     'portable_entry_good_tokens_s':best['good_output_tokens_s']},indent=2),flush=True)

if __name__=='__main__':main()
