"""Seal the failed native H200 reference and retain the first concrete failure."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,subprocess
O=Path(__file__).resolve().parent;R=O.parent;job='25495';run=R/'runs'/job
assert job not in subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True).split()
raw=subprocess.check_output(['sacct','-X','-j',job,'-P','--format=JobID,State%30,ExitCode,Elapsed,Start,End'],text=True)
(O/'accounting.psv').write_text(raw);status=list(csv.DictReader(raw.splitlines(),delimiter='|'))[0]
assert status['State']=='FAILED' and status['ExitCode']=='1:0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
seal=run/'artifact-manifest.json'
if not seal.exists():
 files=[p for p in run.rglob('*') if p.is_file() and p.name not in {'summary.json','artifact-manifest.json'} and '__pycache__' not in p.parts]+[R/'runs'/f'{job}.out',R/'runs'/f'{job}.err']
 for p in files:assert not p.is_symlink(),p
 seal.write_text(json.dumps(dict(job=job,sealed_utc=datetime.now(timezone.utc).isoformat(),status_at_seal=status,scope='Terminal failed diagnostic after allocation cleanup; includes original submitted payload and no output reference',files=[dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)]),indent=2)+'\n')
manifest=json.loads(seal.read_text());assert all(sha(R/row['path'])==row['sha256'] for row in manifest['files'])
source=R/'serving-tuning-10/s37-h200-target-reference';submitted=run/'submitted-payload'
for row in (source/'SHA256SUMS').read_text().splitlines():
 digest,name=row.split('  ',1);assert sha(source/name)==digest and sha(submitted/name)==digest,name
text=(run/'token-client.log').read_text();needle='--container-mounts: source path does not exist:'
assert needle in text and '/home/25495/token-client' in text
assert not (run/'target-reference.json').exists()
head=(run/'head-result-check.log').read_text();assert 'FileNotFoundError' in head
batch=(R/'runs'/f'{job}.out').read_text();assert 'ALL_WORKERS_READY' in batch and 'ALL_PAIRS_WARM' in batch
for role in ['prefill-0','prefill-1','decode-0']:
 subprocess.run(['python3',str(source/'check-kv-ranks.py'),str(run/(role+'.log')),role],check=True,capture_output=True)
# Recheck warmup response/receipt semantics, never rely on the printed marker.
import importlib.util
spec=importlib.util.spec_from_file_location('warmup_semantic',source/'warmup_semantic.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
context=json.loads((run/'pair-warmup-context.json').read_text());exp=context['experiment_id'];token=hashlib.sha256(exp.encode()).hexdigest()[:32]
warm=m.check(run/'pair-warmup-receipts',run/'endpoints.tsv',token)
assert warm['pair_count']==2
result=dict(job=job,reviewed_utc=datetime.now(timezone.utc).isoformat(),state='FAILED_CLIENT_CONTAINER_HOME_MOUNT',scheduler_state=status,payload_and_sealed_evidence_verified=True,seal_sha256=sha(seal),all_workers_and_router_ready=True,bf16_kv_rank_counts=[4,4,8],semantic_warmup=warm,client_process_started=False,actual_model_responses=0,actual_output_token_ids=0,accepted_reference=False,ranked_performance_measured=False,official_accuracy_verified=False,earliest_concrete_failure='Pyxis refused token-client container because mounts() names a role HOME directory that topology-job.sh never created',downstream_error='Independent head checker rejects missing target-reference.json; this is downstream of container launch failure',correction='Prior CPU launcher fixture mocked srun without checking mount source prerequisites; it therefore missed this real launcher bug',next_decision='Derive a fresh bundle adding token-client HOME mkdir before its srun, with actual-launcher mount-prerequisite regression; preserve source and failed evidence. Do not launch EAGLE3 before a passing reference.')
(O/'REVIEW.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
