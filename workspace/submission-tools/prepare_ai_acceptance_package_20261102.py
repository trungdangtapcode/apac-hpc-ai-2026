#!/usr/bin/env python3
"""Stage a compact, explicitly mapped AI acceptance package. Never publishes or edits HPC."""
from pathlib import Path
import hashlib, json, shutil, gzip

W=Path('/home/apacsc42/workspace')
O=W/'submission-review/ai-acceptance-update-20261102'
B=O/'package-files'
OLD=W/'submission-review/ai-final-update-20261101/package-files'
R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-r2-20261102/delivery/VNUHCM - TripleU/AI_Task')
LOG=R/'logs'; TEAM=W/'VNUHCM - TripleU'
O.mkdir(parents=True,exist_ok=True); B.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
# Preserve the prior compact evidence set as provenance, then overlay reviewed R2 deliverables.
oldmap=json.loads((OLD/'package-file-map.json').read_text())
files={}
for target,src in oldmap.items():
    if target.startswith('AI_Task/logs/') and Path(src).is_file(): files[target]=Path(src)
# Replace the active code with exactly the R2 frozen 26-file payload; retain only the requested edits.
code_src=R/'job_scripts'; code_target='AI_Task/job_scripts/'
source_sums=(code_src/'SHA256SUMS').read_text().splitlines()
code_files={}
for line in source_sums:
    expected, rel=line.split('  ',1)
    p=code_src/rel
    assert p.is_file() and not p.is_symlink(), f'Frozen payload path missing/unsafe: {rel}'
    data=p.read_bytes()
    assert sha(data)==expected, f'Frozen payload checksum mismatch: {rel}'
    if rel=='README.md':
        body='''# Acceptance status update (2 November 2026)\n\nA new portable acceptance run completed on job 28197 (16 H200, N64). The measured full-run gate was 3051.518173 tokens/s, 1881/1907 requests within joint latency SLA (98.636602%), with zero timeouts, errors, or cancellations. Both semantic routes, exact run-bound receipts, summary, and gate cleanup passed. This is an accepted portability/operational result, not a new matched optimization or a claim of state-of-the-art performance. Official model quality remains UNKNOWN.\n\nRun 28194 is historical and failed before AIPerf: HTTP health returned 200 while model readiness returned 503 during asynchronous initialization (curl exit 22). The deployment-readiness gate was corrected; the frozen official worker, semantic warmup, and readers were unchanged. See `logs/historical-28194/README.md` and `logs/reruns/28197/README.md`.\n\n'''+data.decode()
        data=body.encode()
    dst=B/'code'/rel; dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes(data)
    if rel!='README.md': shutil.copystat(p,dst)
    code_files[rel]=data
    files[code_target+rel]=dst
sumfile=B/'code-SHA256SUMS'
sumfile.write_text(''.join(f"{sha(data)}  {name}\n" for name,data in sorted(code_files.items())))
files[code_target+'SHA256SUMS']=sumfile
# Add exact root worker evidence and selected run artifacts. Avoid large request input and private runtime home.
def add(src,target):
    if not src.is_file(): return
    dst=B/'evidence'/target
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)
    files['AI_Task/logs/'+target]=dst
# Use actual submitted worker payloads (source delivery already contains exact code); selected run 28197.
base='reruns/28197/'
run=LOG/'reruns/28197'
for p in sorted(run.rglob('*')):
    if not p.is_file(): continue
    rel=p.relative_to(LOG)
    if 'inputs.json' in p.name or '/submitted/' in str(rel) or '.runtime-home' in str(rel): continue
    if p.suffix=='.jsonl':
        dest=B/'evidence'/(str(rel)+'.gz')
        dest.parent.mkdir(parents=True,exist_ok=True)
        with p.open('rb') as src, gzip.open(dest,'wb',compresslevel=6) as out: shutil.copyfileobj(src,out)
        files['AI_Task/logs/'+str(rel)+'.gz']=dest
    else: add(p,'acceptance-20261102/'+str(rel))
for name in ['28197.out','28197.err']:
    add(LOG/'slurm'/name,'acceptance-20261102/slurm/'+name)
# Failure context from R1, minimal and explicit.
r1=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-20261102/delivery/VNUHCM - TripleU/AI_Task/logs')
for candidate in [r1/'reruns/28194/README.md', r1/'reruns/28194/health-check.json', r1/'reruns/28194/deploy.log',r1/'slurm/28194.out',r1/'slurm/28194.err']:
    if candidate.is_file(): add(candidate,'historical-28194/'+candidate.name)
failure_root=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-20261102')
for source,target in [
    (failure_root/'FAILURE_28194.json','historical-28194/FAILURE_28194.json'),
    (failure_root/'FAILURE_28194.md','historical-28194/FAILURE_28194.md'),
    (failure_root/'accounting-28194.txt','historical-28194/accounting-28194.txt'),
]: add(source,target)
reader_root=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/portable-artifact-path-fix-20261029')
for job in (27136,27145):
    for prefix in ('recovered-gate','recovered-summary'):
        add(reader_root/f'{prefix}-{job}.json',f'historical-reader-replays/{prefix}-{job}.json')
for name in ('REPLAY_REVIEW.md','ALIAS_CORRECTION.md'):
    add(reader_root/name,'historical-reader-replays/'+name)
failreadme=B/'evidence/historical-28194/README.md'
failreadme.parent.mkdir(parents=True,exist_ok=True)
failreadme.write_text('''# Historical deployment failure: job 28194\n\nThis run is not a scored result. Curl exited 22 after the basic health endpoint returned HTTP 200 while model readiness returned HTTP 503 during asynchronous initialization. No AIPerf run or score was produced. The R2 correction adds a model-readiness deployment gate; official worker, semantic warmup and readers were unchanged.\n''')
files['AI_Task/logs/historical-28194/README.md']=failreadme
# Updated paper/report docs from the reviewed report source; compact English-only set.
reports=W/'reports/ai-final-report-20261030'
docmap={'FINAL_REPORT.md':'REPORT.md','PRESENTATION_PLAN.md':'PRESENTATION_PLAN.md','EVIDENCE_CARDS.md':'EVIDENCE_CARDS.md','PANEL_QA.md':'PANEL_QA.md','TALK_SCRIPT_EN.md':'TALK_SCRIPT_EN.md','TEACHER_FEEDBACK_RESPONSE.md':'FEEDBACK_RESPONSE.md','MOCK_QA_EVIDENCE.md':'MOCK_QA_EVIDENCE.md','RESEARCH_JOURNEY.md':'JOURNEY_COVERAGE.md'}
for target,srcname in docmap.items():
    src=reports/srcname
    if src.exists():
        dst=B/target; shutil.copy2(src,dst); files['AI_Task/logs/'+target]=dst
# Include the independent job-specific review and machine-readable verdict.
study=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-r2-20261102')
for srcname,target in [
    ('RESULTS_REVIEW.md','acceptance-20261102/RESULTS_REVIEW.md'),
    ('RESULTS.md','acceptance-20261102/RESULTS.md'),
    ('STATUS.md','acceptance-20261102/STATUS.md'),
    ('accounting-28197.txt','acceptance-20261102/accounting-28197.txt'),
    ('result-28197.json','acceptance-20261102/result-28197.json'),
    ('recomputed-performance-gate.json','acceptance-20261102/recomputed-performance-gate.json'),
    ('recomputed-summary.json','acceptance-20261102/recomputed-summary.json'),
    ('FROZEN_PAYLOAD.json','acceptance-20261102/FROZEN_PAYLOAD.json'),
    ('ARTIFACT_MANIFEST.json','acceptance-20261102/ARTIFACT_MANIFEST.json'),
]:
    src=study/srcname
    if src.is_file(): add(src,target)
receipt=study/'admission/submission-receipt.json'
if receipt.is_file(): add(receipt,'acceptance-20261102/submission-receipt.json')
# New readable acceptance report, grounded in scheduler/run evidence.
latest=B/'latest-results.md'
latest.write_text('''# Latest AI results and acceptance status\n\n## Accepted portable N64 run: job 28197\n\nThe frozen R2 package completed on 16 H200 GPUs in 611 seconds (Slurm state COMPLETED, exit 0:0). The official AIPerf run measured 3,051.518173 good output tokens/s. Of 1,907 requests, 1,881 met the joint latency service-level objective (98.636602%); there were 26 TTFT and 0 ITL violations, with zero errors and cancellations. Both independently validated semantic P/D routes passed, as did summary generation, score gate, and cleanup. This acceptance confirms deployment and benchmark reproducibility for this portable bundle. It is not a matched optimization claim or a new state-of-the-art claim. Official organiser accuracy is UNKNOWN.\n\n## Prior deployment failure: job 28194\n\nJob 28194 ended before AIPerf with curl exit 22. Basic health returned HTTP 200 while model readiness returned 503 during asynchronous initialization. R2 changes only the deployment-readiness gate among runtime files; worker, semantic warmup, readers, and model/environment configuration match the frozen R1 payload. README and checksum files are documentary metadata.\n\n## Interpretation\n\nJob 27378 remains the previously highest completed score in the older research set; that phrasing is now historical because accepted portable job 28197 measured 3,051.518173 tokens/s. Earlier job 27145 reported a higher raw point (3,055.330517 good output tokens/s). Its original allocation failed result postprocessing because of a canonical-path alias; the recovered raw performance export passes the local performance gate, but that allocation was not fully successful. Neither comparison makes 28197 a matched improvement: this is an acceptance replay, not an optimization experiment. H100 results remain a separate platform. The archived job data preserve raw profile exports and losslessly compressed request records; the 228 MB inputs file, model weights, runtime home, and private authentication/cache state are excluded. Hardware telemetry was not collected for job 28197; runtime log sampling is not GPU utilization evidence.\n''')
files['AI_Task/logs/measured/latest-results.md']=latest
# Add fresh R2 compact evidence manifest and job README.
readme=B/'acceptance-28197-README.md'; readme.write_text('''# Job 28197 evidence\n\nAccepted portable N64 run on 16 H200 GPUs; COMPLETED 0:0 after 611 seconds. Score gate: 3051.518173 tokens/s; 1881/1907 good (98.636602%), 26 TTFT violations, 0 ITL violations, zero errors/cancellations. Both semantic warmup routes and run-bound receipts validated. Official model quality is UNKNOWN. Raw profile export is included and raw JSONL requests are gzip compressed losslessly; the 228 MB inputs file and runtime-home/private state are excluded.\n''')
files['AI_Task/logs/reruns/28197/README.md']=readme
# Compose normalized mapping with unique team-relative paths, copy all source payloads under owned stage.
mapping={}
for target,src in sorted(files.items()):
    assert target.startswith('AI_Task/') and '..' not in Path(target).parts, target
    if isinstance(src,Path) and (B not in src.parents):
        dst=B/'evidence'/target.removeprefix('AI_Task/logs/')
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dst); src=dst
    mapping[target]=str(src)
assert len(mapping)==len(set(mapping))
# Rewrite source-report links to included team-relative evidence or explicit archive notes.
import os, re, urllib.parse
doc_origins={}
for target,srcname in docmap.items():
    if (reports/srcname).is_file(): doc_origins['AI_Task/logs/'+target]=(reports/srcname).resolve()
hash_targets={}
for target,src in mapping.items():
    hash_targets.setdefault(sha(Path(src).read_bytes()),target)
source_targets={str(Path(src).resolve()):target for target,src in mapping.items()}
for target,origin in doc_origins.items():
    staged=Path(mapping[target]); body=staged.read_text()
    def rewrite(match):
        label,raw=match.groups()
        if raw.startswith(('http://','https://','#')): return match.group(0)
        local,sep,fragment=raw.strip('<>').partition('#')
        resolved=(origin.parent/urllib.parse.unquote(local)).resolve()
        dest=source_targets.get(str(resolved))
        if dest is None and resolved.is_file(): dest=hash_targets.get(sha(resolved.read_bytes()))
        if dest:
            rel=os.path.relpath(dest,str(Path(target).parent))
            return f'[{label}](<{rel}{sep+fragment if sep else ""}>)'
        return f'{label} (source: `{resolved.name}`, retained outside this compact package)'
    staged.write_text(re.sub(r'\[([^\]]+)\]\(([^)]+)\)',rewrite,body))
# File inventory + checksums cover only staged package assets.
(B/'package-file-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
(O/'package-file-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
# The release helper may replace only these three job-script metadata files plus AI logs.
publish_map={path:source for path,source in mapping.items()
             if path.startswith('AI_Task/logs/') or path in {
                 'AI_Task/job_scripts/README.md',
                 'AI_Task/job_scripts/deploy-and-benchmark.sh',
                 'AI_Task/job_scripts/SHA256SUMS'}}
(O/'publish-file-map.json').write_text(json.dumps(publish_map,indent=2)+'\n')
manifest=[]
for target,src in mapping.items():
    data=Path(src).read_bytes(); manifest.append({'path':target,'bytes':len(data),'sha256':sha(data)})
(B/'evidence-manifest.json').write_text(json.dumps({'created_utc':'2026-11-02','files':manifest,'accuracy':'UNKNOWN','scope':'AI-only staged evidence'},indent=2)+'\n')
# Source provenance for this package; payload hashes reflect accepted frozen code.
(O/'PREPARATION.json').write_text(json.dumps({'stage_only':True,'publication_performed':False,'job_id':28197,'result_class':'accepted portable acceptance; not optimization/SOTA','gpu':'16 H200','n64':True,'official_accuracy':'UNKNOWN','mapped_files':len(mapping),'excluded':['228 MB inputs.json','model weights','runtime-home','private authentication/cache state'],'hpc_files_modified':False},indent=2)+'\n')
print(json.dumps({'mapped_files':len(mapping),'staged_bytes':sum(Path(x).stat().st_size for x in mapping.values()),'stage':str(O)}))
