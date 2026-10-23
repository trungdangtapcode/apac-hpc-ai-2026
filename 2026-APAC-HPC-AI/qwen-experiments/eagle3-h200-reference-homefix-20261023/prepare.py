"""Derive a reference HOME prerequisite repair; never modify a submitted bundle."""
from datetime import datetime,timezone
from pathlib import Path
import ast,hashlib,importlib.util,json,shutil,subprocess
O=Path(__file__).resolve().parent;R=O.parent
SOURCE=R/'serving-tuning-10/s37-h200-target-reference'
BID='s38-h200-target-reference-homefix';B=R/'serving-tuning-10'/BID
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not B.exists() and not (O/'prepared.json').exists(),'Inspect existing preparation; never rebuild a freeze'
proof=R/'research-review-25495-20261023/REVIEW.json';failure=json.loads(proof.read_text())
assert failure['state']=='FAILED_CLIENT_CONTAINER_HOME_MOUNT' and failure['accepted_reference'] is False
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=SOURCE,check=True,capture_output=True)
subprocess.run(['python3','-B',str(SOURCE/'preflight-assets.py')],check=True,capture_output=True)
TEMP=B.with_name('.'+BID+'.preparing');assert not TEMP.exists();TEMP.mkdir()
for p in SOURCE.iterdir():
 if p.is_file():shutil.copyfile(p,TEMP/p.name)
(TEMP/'SHA256SUMS').rename(TEMP/'PARENT_SHA256SUMS')
(TEMP/'FROZEN_PROVENANCE.json').rename(TEMP/'PARENT_FROZEN_PROVENANCE.json')
p=TEMP/'topology-job.sh';text=p.read_text()
needle='python3 "$BUNDLE/phase-marker.py" "$ART" target_reference_start "$(date +%s)"\nset +e'
assert text.count(needle)==1
text=text.replace(needle,'mkdir -p "$ROOT/home/$SLURM_JOB_ID/token-client"\n'+needle)
p.write_text(text)
p=TEMP/'job.sbatch';text=p.read_text();assert text.count(str(SOURCE))==1
text=text.replace(str(SOURCE),str(B)).replace('ap42-s37-h200-target-reference','ap42-'+BID)
p.write_text(text)
p=TEMP/'config.json';config=json.loads(p.read_text());config.update(experiment=BID,repair_for_job='25495',repair='Create token-client role HOME before container mount',parent_bundle=str(SOURCE));p.write_text(json.dumps(config,indent=2)+'\n')
unchanged=[]
for p in SOURCE.iterdir():
 if not p.is_file() or p.name in {'topology-job.sh','job.sbatch','config.json','SHA256SUMS','FROZEN_PROVENANCE.json'}:continue
 assert p.read_bytes()==(TEMP/p.name).read_bytes(),p.name;unchanged.append(p.name)
for p in TEMP.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in [*TEMP.glob('*.sh'),TEMP/'job.sbatch']:subprocess.run(['bash','-n',str(p)],check=True)
provenance=dict(frozen_utc=datetime.now(timezone.utc).isoformat(),source_bundle=str(SOURCE),source_job='25495',source_seal_sha256=sha(SOURCE/'SHA256SUMS'),failure_review_sha256=sha(proof),execution_change='mkdir -p token-client role HOME before native Slurm client srun',other_changes=['New canonical job identity/path','Repair provenance in diagnostic config'],unchanged_files=unchanged,no_target_transport_precision_protocol_or_deadline_change=True,diagnostic_only=True)
(TEMP/'FROZEN_PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n')
files=sorted(p for p in TEMP.iterdir() if p.is_file())
(TEMP/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in files))
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=TEMP,check=True,capture_output=True)
TEMP.rename(B)
prepared=dict(id=BID,bundle=str(B),state='FROZEN_NOT_SUBMITTED',gpus=16,nodes=2,minutes=17,pbs_su_reserved=0,diagnostic_only=True,asset_manifest_sha256=config['asset_manifest_sha256'],repair_for_job='25495',payload_sha256={p.name:sha(p) for p in B.iterdir() if p.is_file()})
(O/'prepared.json').write_text(json.dumps(prepared,indent=2)+'\n')
print(BID,'frozen; not submitted')
