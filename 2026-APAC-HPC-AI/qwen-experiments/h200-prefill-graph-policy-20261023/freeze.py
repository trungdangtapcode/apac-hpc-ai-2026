from pathlib import Path
import json,hashlib,shutil,subprocess,datetime
o=Path(__file__).resolve().parent;r=o.parent;t=r/'serving-tuning-10';made=[]
assert json.loads((o/'validation.json').read_text())['passed']
for draft in sorted((o/'proposals').iterdir()):
 name=draft.name;out=t/name;assert not out.exists(),out
 shutil.copyfile(o/'client-image-identity.json',draft/'client-image-identity.json')
 f=draft/'preflight-assets.py';f.write_text('''"""Bound target, serving and client image identities before worker startup."""
from pathlib import Path
import json
from asset_identity import verify_asset_identity
root=Path(__file__).resolve().parent
result=verify_asset_identity(root/'asset-verification.json','/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8','/scratch/enroot-images/sglang-harbor.sqsh')
client=json.loads((root/'client-image-identity.json').read_text());stat=Path(client['path']).stat()
assert stat.st_size==client['bytes'] and stat.st_mtime_ns==client['mtime_ns'] and stat.st_ctime_ns==client['ctime_ns'], 'Client image changed after full byte verification'
print(json.dumps(dict(target_and_serving=result,client_image_prechecked_sha256=client['sha256'],client_image_runtime_fingerprint_match=True),indent=2))
''')
 compile(f.read_bytes(),str(f),'exec')
 c=json.loads((draft/'config.json').read_text());c['canonical_bundle']=str(out);c['client_image_sha256']=json.loads((o/'client-image-identity.json').read_text())['sha256'];c['submission_kind']='short_policy_screen';(draft/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 provenance=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),canonical_bundle=str(out),target_only=True,source_bundles=[dict(path=str(s),manifest_sha256=hashlib.sha256((s/'SHA256SUMS').read_bytes()).hexdigest()) for s in [t/'s35-h200-observed-n64-full-control',t/'s38-h200-target-reference-homefix']],change='Uniform native prefill graph policy at common explicit BF16 and64/256request caps; only policy differs between two derived jobs',cpu_only_before_submission=True,official_accuracy_verified=False)
 (draft/'FROZEN_PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n')
 shutil.copytree(draft,out,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 files=sorted(p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
 (out/'SHA256SUMS').write_text(''.join(hashlib.sha256((out/f).read_bytes()).hexdigest()+'  '+f+'\n' for f in files))
 subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=out,check=True,stdout=subprocess.DEVNULL)
 made.append(out)
a,b=made;different=[]
for f in a.iterdir():
 if f.is_file() and f.name!='SHA256SUMS' and f.read_bytes()!=(b/f.name).read_bytes():different.append(f.name)
assert set(different)=={'config.json','job.sbatch','worker.sh','topology-job.sh','FROZEN_PROVENANCE.json'},different
(o/'frozen.json').write_text(json.dumps(dict(ready_for_slurm=True,prepared_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),bundles=[str(p) for p in made],pair_different_files=different,source_reference='25487 full H200 N64;25585 bounded target reference',cpu_validation=str(o/'validation.json'),asset_checks='Target and serving image fingerprint checks pass; client image fullSHA prechecked and fingerprint bound at runtime',pbs_su=0,submitted=False),indent=2)+'\n')
print('Frozen',*[str(p) for p in made],sep='\n')
