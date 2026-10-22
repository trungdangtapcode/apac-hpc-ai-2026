"""Freeze one asset-bound native H200 exact-token reference, without submission."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import importlib.util
import json
import shutil
import subprocess

O = Path(__file__).resolve().parent
R = O.parent
P = O / 'proposal'
DRAFT = R / 'eagle3-h200-reference-20261022'
BID = 's37-h200-target-reference'
B = R / 'serving-tuning-10' / BID
ASSETS = R / 'eagle3-h200-reference-assets-20261022/VERIFICATION.json'
MODEL = '/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8'
IMAGE = '/scratch/enroot-images/sglang-harbor.sqsh'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

assert not B.exists(), 'Never rewrite an existing frozen bundle'
assert not (O / 'prepared.json').exists(), 'Inspect an existing preparation'
proof = json.loads(ASSETS.read_text())
assert proof['state'] == 'PASS' and len(proof['files']) == 34 and not proof['errors']
assert (P / 'asset-verification.json').read_bytes() == ASSETS.read_bytes()
subprocess.run(['python3', str(DRAFT / 'prepare.py')], check=True, capture_output=True)
root_proof = json.loads((DRAFT / 'ROOT_REVIEW.json').read_text())
assert root_proof['state'] == 'CPU_VALIDATED_REFERENCE_DRAFT'
source = DRAFT / 'mutable-proposal/payload'
for name in ['worker.sh','nixl-conn.py','placement.tsv','prepared-corpus.json','warmup_semantic.py','warm-topology.py','check-kv-ranks.py','token_observation.py']:
    assert (P / name).read_bytes() == (source / name).read_bytes(), name
spec = importlib.util.spec_from_file_location('asset_identity', P / 'asset_identity.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
identity = module.verify_asset_identity(ASSETS, MODEL, IMAGE)
assert identity['verified_file_count'] == 34
assert not any('EAGLE3' in str(v) for v in json.loads((source/'config.json').read_text())['prefill_extra_flags'])
for p in P.glob('*.py'): ast.parse(p.read_text(), filename=str(p))
for p in list(P.glob('*.sh')) + [P/'job.sbatch']:
    subprocess.run(['bash','-n',str(p)],check=True)
TEMP = B.with_name('.' + BID + '.preparing')
assert not TEMP.exists(), 'Inspect interrupted preparation first'
TEMP.mkdir()
for p in P.iterdir():
    if p.is_file(): shutil.copyfile(p,TEMP/p.name)
# These are original source inventories, not current bundle seals.
(TEMP/'SOURCE_PROVENANCE.json').rename(TEMP/'SOURCE_DRAFT_PROVENANCE.json')
job = (TEMP/'job.sbatch').read_text()
assert job.count('export QWEN_BUNDLE="$SLURM_SUBMIT_DIR/mutable-proposal/payload"') == 1
job = job.replace('ap42-eagle3-h200-target-reference','ap42-'+BID)
job = job.replace('export QWEN_BUNDLE="$SLURM_SUBMIT_DIR/mutable-proposal/payload"','export QWEN_BUNDLE='+str(B))
job = job.replace('sha256sum --check SOURCE_SHA256SUMS','sha256sum --check SHA256SUMS')
job = job.replace('# Draft only. Root review and fresh target/image identity checks required before freeze.', '# Frozen target-only reference; identity, CPU and native source gates reviewed.')
needle='exec bash topology-job.sh'
assert job.count(needle)==1
job=job.replace(needle,'mkdir -p "$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID"\npython3 -B "$QWEN_BUNDLE/preflight-assets.py" >"$SLURM_SUBMIT_DIR/runs/$SLURM_JOB_ID/asset-preflight.json"\n'+needle)
(TEMP/'job.sbatch').write_text(job)
(TEMP/'preflight-assets.py').write_text('''"""Reject changed assets before starting a GPU model worker."""
from pathlib import Path
import json
from asset_identity import verify_asset_identity
print(json.dumps(verify_asset_identity(Path(__file__).parent/'asset-verification.json', '/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8', '/scratch/enroot-images/sglang-harbor.sqsh'),indent=2))
''')
c=json.loads((TEMP/'config.json').read_text())
keep=['id','prefill_gpus','decode_gpus','prefill_tp','decode_tp','decode_ep','prefill_workers','decode_workers','image','model','memory_fraction','decode_max_running_requests','context_length','kv_dtype','transfer','prefill_ep','nccl_port_policy','nixl_on_demand','transport_patch','transport_patch_metadata','decode_extra_flags','prefill_extra_flags','prefill_chunk_size','router_extra_flags','scheduler_recv_interval_decode','graph_maximum_decode','transport_patch_sha256']
c={k:c[k] for k in keep}
c.update(experiment=BID,source_experiment='s30-h200-observed-n64-full-candidate',source_job='25366',validated_startup_source_job='25373',platform='H200',phase='target_reference',scored_benchmark=False,aiperf=False,diagnostic_profile=False,concurrency=1,requests=8,output_tokens_per_request=200,expected_output_token_ids=1600,sampling_seed=2026,ignore_eos=True,walltime_minutes=17,gpus=16,pbs_su_reserved=0,resource_monitor=True,asset_manifest_sha256=sha(ASSETS),asset_identity_state='FULL_PRE_FREEZE_HASH_PASS_RUNTIME_FINGERPRINT_AND_METADATA_RECHECK',protocol='Two greedy native /generate passes over four frozen cases; no AIPerf score',startup_deadline_s=600,semantic_pair_warmup_deadline_s=120,client_deadline_s=210,result_check_deadline_s=20,teardown_budget_s=40,hard_stop_s=1020,kv_geometry='not collected',official_accuracy_verified=False)
(TEMP/'config.json').write_text(json.dumps(c,indent=2)+'\n')
provenance=dict(frozen_utc=datetime.now(timezone.utc).isoformat(),source_proposal=str(P),source_proposal_sha256={p.name:sha(p) for p in P.iterdir() if p.is_file()},asset_manifest_sha256=sha(ASSETS),unchanged_native_files=['worker.sh','nixl-conn.py','placement.tsv'],changes=['Asset manifest binding in client and independent head result','Canonical job name/path and pre-worker asset preflight','Diagnostic-only configuration metadata; no AIPerf protocol claim'],no_model_or_image_bytes_bundled=True)
(TEMP/'FROZEN_PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n')
for p in TEMP.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in list(TEMP.glob('*.sh'))+[TEMP/'job.sbatch']:subprocess.run(['bash','-n',str(p)],check=True)
files=sorted(p for p in TEMP.iterdir() if p.is_file())
(TEMP/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in files))
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=TEMP,check=True,capture_output=True)
TEMP.rename(B)
(O/'prepared.json').write_text(json.dumps(dict(id=BID,bundle=str(B),state='FROZEN_NOT_SUBMITTED',gpus=16,nodes=2,minutes=17,pbs_su_reserved=0,diagnostic_only=True,asset_manifest_sha256=sha(ASSETS),files=len(files),payload_sha256={p.name:sha(p) for p in B.iterdir() if p.is_file()}),indent=2)+'\n')
print('Frozen',BID,'asset-bound target-only reference; no submission')
