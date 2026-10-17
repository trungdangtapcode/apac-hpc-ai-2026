"""Prepare a frozen candidate without arming or submitting any scheduler job."""
from pathlib import Path
import hashlib,json,shutil,subprocess,datetime
R=Path.cwd();O=R/'research-followup-20261017-1830';src=R/'serving-tuning-10/s10-prefill-deepgemm-n56';name='s10-prefill-deepgemm-chunk8192-n56';dst=src.parent/name
assert not dst.exists();shutil.copytree(src,dst)
f=dst/'worker.sh';s=f.read_text();old='extra=(--chunked-prefill-size 4096 --moe-runner-backend deep_gemm)';assert s.count(old)==1;f.write_text(s.replace(old,'extra=(--chunked-prefill-size 8192 --moe-runner-backend deep_gemm)'))
f=dst/'job.sbatch';f.write_text(f.read_text().replace(src.name,name))
f=dst/'config.json';c=json.loads(f.read_text());c.update(experiment=name,source_job='24291',prefill_chunk_size=8192,prefill_extra_flags=['--chunked-prefill-size','8192','--moe-runner-backend','deep_gemm'],purpose='Conditional prefill chunk/backend interaction: new DeepGEMM runner with chunk8192 versus DeepGEMM chunk4096 at identical N56; not an unchanged repeat of old auto-runner chunk8192');f.write_text(json.dumps(c,indent=2)+'\n')
allowed={'config.json','worker.sh','job.sbatch','SHA256SUMS'}
for f in src.iterdir():
 if f.is_file() and f.name not in allowed:assert f.read_bytes()==(dst/f.name).read_bytes(),f.name
for f in list(dst.glob('*.sh'))+[dst/'job.sbatch']:subprocess.run(['bash','-n',str(f)],check=True)
h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()))
plan=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),id=name,bundle=str(dst),state='PREPARED_NOT_ARMED_OR_SUBMITTED',payload_sha256=h,planned_ns=[56],max_gpus=16,max_minutes=17,control='24291 and independent repeat 24327',prior_negative='Auto-runner chunk8192 job 23906 lost versus chunk4096. A runner interaction is a new hypothesis, not demonstrated improvement.',preconditions=['Review independent DeepGEMM N56 repeat 24327; reject this branch if its existing gain does not hold.','Review graph ablation 24376 and avoid combining unresolved changes.','Check all own Slurm jobs; queue must have room under the five-job cap before arming.'],stop_rules=['Require full 60/120/30, 4000/200 protocol, intended runtime, SLA >=90%, no request errors/cancellations, short nonregression and 12/12 long retrieval.','Keep all initial burst requests in the official metric; no benchmark-phase-specific scheduling or score changes.','Close on startup failure, failed SLA, output regression or no useful goodput gain.','A promising single point requires independent confirmation, not automatic promotion.'],memory_caveat='Larger chunk and graph capture shapes can change scratch memory and startup. Do not increase resources or retry blindly on an OOM.')
(O/'conditional-candidate.json').write_text(json.dumps(plan,indent=2)+'\n')
# This file is intentionally not added to prepared-pilots.json: the watcher must not submit it yet.
print('Prepared but not armed:',name)
