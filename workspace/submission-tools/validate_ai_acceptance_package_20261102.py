#!/usr/bin/env python3
"""Validate the staged 28197 AI acceptance package without publishing it."""
from pathlib import Path
import ast, gzip, hashlib, json, math, re, subprocess, tempfile, zipfile
import xml.etree.ElementTree as ET

W=Path(__file__).resolve().parents[1]
O=W/'submission-review/ai-acceptance-update-20261102'; B=O/'package-files'
R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-r2-20261102')
TEAM=W/'VNUHCM - TripleU'
sha=lambda b:hashlib.sha256(b).hexdigest()
checks=[]
def ok(name,condition):
    assert condition,name
    checks.append(name)

pmap=json.loads((O/'package-file-map.json').read_text())
publish=json.loads((O/'publish-file-map.json').read_text())
seen=set()
for target,source in pmap.items():
    p=Path(target)
    ok('normalized_target:'+target, target.startswith('AI_Task/') and '..' not in p.parts and target not in seen)
    seen.add(target)
    s=Path(source).resolve()
    ok('staged_source:'+target, s.is_file() and B.resolve() in s.parents)
allowed={'AI_Task/job_scripts/README.md','AI_Task/job_scripts/deploy-and-benchmark.sh','AI_Task/job_scripts/SHA256SUMS'}
for target in publish:
    ok('publish_scope:'+target,target.startswith('AI_Task/logs/') or target in allowed)
ok('publish_map_subset',set(publish).issubset(pmap))
ok('no_internal_map_artifact',not any(Path(x).name=='package-file-map.json' for x in publish))

# Verify the newly frozen 26-file payload. Only README differs as content; deployment readiness is the only runtime delta from R1.
code=R/'delivery/VNUHCM - TripleU/AI_Task/job_scripts'
source_sum={}
for line in (code/'SHA256SUMS').read_text().splitlines():
    digest,name=line.split('  ',1); source_sum[name]=digest
ok('frozen_26_file_manifest',len(source_sum)==25 and len([x for x in pmap if x.startswith('AI_Task/job_scripts/')])==26)
for name,digest in source_sum.items():
    target='AI_Task/job_scripts/'+name
    staged=Path(pmap[target]).read_bytes()
    if name=='README.md':
        ok('README_acceptance_status',b'job 28197' in staged.lower() and b'UNKNOWN' in staged)
    else:
        ok('frozen_code_byte_identity:'+name,sha(staged)==digest)
# Check generated code checksum file matches the staged files (README updated only).
lines=(Path(pmap['AI_Task/job_scripts/SHA256SUMS']).read_text().splitlines())
parsed={n:h for h,n in (line.split('  ',1) for line in lines)}
ok('staged_code_checksums',set(parsed)==set(source_sum) and all(parsed[n]==sha(Path(pmap['AI_Task/job_scripts/'+n]).read_bytes()) for n in parsed))

# Result review and raw exports agree exactly on accepted score, counts, semantic routes, and unknown quality.
result=json.loads(Path(pmap['AI_Task/logs/acceptance-20261102/result-28197.json']).read_text())
gate=json.loads(Path(pmap['AI_Task/logs/acceptance-20261102/reruns/28197/performance-gate.json']).read_text())
summary=json.loads(Path(pmap['AI_Task/logs/acceptance-20261102/reruns/28197/summary.json']).read_text())[0]
score=result['score']; status=result['status']; checks_record=result['independent_checks']
ok('job_terminal_success',status['slurm']=='COMPLETED' and status['exit_code']=='0:0' and status['elapsed_seconds']==611)
ok('N64_16_H200',status['gpus']==16 and status['gpu_model']=='H200' and result['configuration']['concurrency']==64)
ok('score_gate_exact',gate['passed'] is True and gate['good_requests']==1881 and gate['requests']==1907 and math.isclose(gate['good_output_tokens_s'],3051.518173303673,abs_tol=1e-10))
ok('review_summary_gate_concordance',math.isclose(summary['good_output_tokens_s'],gate['good_output_tokens_s'],abs_tol=1e-10) and summary['errors']==0 and summary['cancelled_requests']==0)
ok('no_official_quality_claim',result['quality']['official_accuracy_verified'] is False and result['quality']['result']=='unknown')
ok('raw_gate_recomputed',checks_record['raw_gate_recomputed'] is True and checks_record['raw_phase_rows']=={'warmup':949,'profiling':1907})
ok('semantic_two_pair_pass',checks_record['semantic_receipts_valid'] is True and checks_record['semantic_pair_count']==2)
ok('frozen_payload_review',checks_record['submitted_payload_manifest_files']==26 and checks_record['submitted_payload_hash_mismatches']==0)
ok('telemetry_not_collected',result['runtime_observations']['hardware_telemetry'].startswith('not collected'))
official=Path(pmap['AI_Task/job_scripts/official-benchmark.sh']).read_text()
for flag in ['--warmup-duration 60','--benchmark-duration 120','--benchmark-grace-period 30',
             '--synthetic-input-tokens-mean 4000','--output-tokens-mean 200','--random-seed 2026',
             '--cache-bust first_turn_prefix','--goodput "time_to_first_token:3000 inter_token_latency:20"']:
    ok('official_aiperf_flag:'+flag,flag in official)
profile_target=next(t for t in publish if t.endswith('/profile_export_aiperf.json'))
profile=json.loads(Path(publish[profile_target]).read_text())
ok('AIPerf_profile_score',math.isclose(profile['goodput']['avg']*200,3051.518173303673,abs_tol=1e-9))
raw_target=next(t for t in publish if t.endswith('/profile_export.jsonl.gz'))
raw=Path(publish[raw_target]).read_bytes()
rows=[json.loads(line) for line in gzip.decompress(raw).splitlines()]
ok('lossless_raw_jsonl_gzip',len(rows)==2856)
phases={}
scored=good=miss_ttft=miss_itl=0
for row in rows:
    phase=row.get('metadata',{}).get('phase_kind',row.get('metadata',{}).get('benchmark_phase'))
    phases[phase]=phases.get(phase,0)+1
    if phase!='profiling': continue
    scored+=1
    metadata=row.get('metadata',{}); metrics=row.get('metrics',{})
    failed=bool(metadata.get('was_cancelled') or metadata.get('context_overflow_skip') or row.get('error') or row.get('errors'))
    ttft=metrics.get('time_to_first_token',{}).get('value')
    itl=metrics.get('inter_token_latency',{}).get('value')
    assert not failed and isinstance(ttft,(float,int)) and isinstance(itl,(float,int))
    miss_ttft+=ttft>3000; miss_itl+=itl>20
    good+=(ttft<=3000 and itl<=20)
ok('raw_phase_counts',phases.get('warmup')==949 and phases.get('profiling')==1907)
ok('raw_request_gate_replay',scored==1907 and good==1881 and miss_ttft==26 and miss_itl==0)

# The deployment edit is the sole runtime file changed from R1; no weights or disposable caches are staged.
r1=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-portable-acceptance-20261102/delivery/VNUHCM - TripleU/AI_Task/job_scripts')
changed=[]
for name in source_sum:
    q=r1/name
    if q.is_file() and q.read_bytes()!= (code/name).read_bytes(): changed.append(name)
ok('R1_R2_runtime_change_scoped',set(changed)=={'deploy-and-benchmark.sh'})
ok('no_large_inputs_or_model_weights',not any(Path(x).name=='inputs.json' or Path(x).suffix in {'.safetensors','.bin','.pt','.pth'} for x in pmap))
ok('no_runtime_home_or_private_cache',not any('.runtime-home' in x or '/blobs/' in x or 'credentials' in x.lower() for x in pmap))
latest=Path(pmap['AI_Task/logs/measured/latest-results.md']).read_text()
ok('latest_historical_wording', '27378' in latest and '27145' in latest and 'matched improvement' in latest and 'UNKNOWN' in latest)
talk=Path(pmap['AI_Task/logs/TALK_SCRIPT_EN.md']).read_text()
ok('spoken_script_closes_replay_gap', '28197' in talk and '3,051.52' in talk and
   'we have not completed a fresh full GPU replay' not in talk)

# Syntax validation for staged runnable entrypoints.
for target,source in pmap.items():
    path=Path(source)
    if target.endswith('.py'):
        ast.parse(path.read_text(),filename=target)
    elif target.endswith(('.sh','.sbatch')):
        subprocess.run(['bash','-n',str(path)],check=True,capture_output=True,text=True)
ok('python_and_bash_syntax',True)

# Validate the fresh deck/HPC snapshot when the root slide build is present.
pptx=O/'TripleU_APAC2026_Presentation.pptx'
if pptx.exists():
    merge=json.loads((O/'merge-validation.json').read_text())
    before=json.loads((O/'HPC_BEFORE.json').read_text())
    ok('merged_deck_42_slides',merge['passed'] and merge['slides']==42 and merge['updated_ai_slides']==34 and merge['preserved_hpc_slides']==8 and len(ET.fromstring(zipfile.ZipFile(pptx).read('ppt/presentation.xml')).findall('.//{http://schemas.openxmlformats.org/presentationml/2006/main}sldId'))==42)
    with zipfile.ZipFile(pptx) as z:
        ok('PPTX_HPC_closure_68_parts',all(sha(z.read(path))==digest for path,digest in before['presentation']['hpc_dependency_closure_parts'].items()) and len(before['presentation']['hpc_dependency_closure_parts'])==68)
else:
    ok('deck_pending_root_merge',not (O/'merge-validation.json').exists())

out={'passed':True,'checks':len(checks),'job_id':28197,'package_entries':len(pmap),'publish_entries':len(publish),'staged_bytes':sum(Path(x).stat().st_size for x in pmap.values()),'official_accuracy':'UNKNOWN','publication_performed':False,'deck_ready':pptx.exists(),'hpc_changed':False,'checks_run':checks}
(O/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='checks_run'},indent=2))
