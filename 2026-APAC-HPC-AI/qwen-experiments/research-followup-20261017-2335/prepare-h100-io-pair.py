"""Prepare a reversed-order H100 prefetch/control pair with identical startup bounds."""
from pathlib import Path
import json,shutil,subprocess,hashlib,tarfile,datetime
R=Path.cwd();P=R/'nscc-pbs';O=R/'research-followup-20261017-2335';report={}
for source,name in [('h100-prefill-prefetch-18','h100-prefetch-repeat-21'),('h100-combo-control-16','h100-io-control-22')]:
 src=P/source;dst=P/name;assert not dst.exists();shutil.copytree(src,dst)
 f=dst/'benchmark.pbs';f.write_text(f.read_text().replace(source,name))
 f=dst/'topology-job.sh';s=f.read_text();assert s.count('deadline=${2:-1200}')==1;f.write_text(s.replace('deadline=${2:-1200}','deadline=${2:-1800}'))
 f=dst/'config.json';c=json.loads(f.read_text());c.update(experiment=name,source_job='221153.pbs111' if 'prefetch' in name else '221151.pbs111',worker_readiness_deadline_s=1800,purpose='Reversed-order N50 prefetch/control confirmation; separate startup I/O timing from ranked throughput and record cache/node confounds');f.write_text(json.dumps(c,indent=2)+'\n')
 for f in src.iterdir():
  if f.is_file() and f.name not in ['config.json','benchmark.pbs','topology-job.sh','SHA256SUMS']:assert f.read_bytes()==(dst/f.name).read_bytes(),f.name
 for f in list(dst.glob('*.sh'))+[dst/'benchmark.pbs']:subprocess.run(['bash','-n',str(f)],check=True)
 h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()));report[name]=h
control=(P/'h100-io-control-22/worker.sh').read_text();pref=(P/'h100-prefetch-repeat-21/worker.sh').read_text();assert control.replace('extra=(--chunked-prefill-size 4096)','extra=(--chunked-prefill-size 4096 --weight-loader-prefetch-checkpoints)')==pref
with tarfile.open(O/'io-pair.tar.gz','w:gz') as t:
 for name in report:t.add(P/name,arcname=name)
(O/'io-pair-validation.json').write_text(json.dumps(dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),order=list(report),payloads=report,worker_difference='Prefill weight-loader prefetch flag only',shared_worker_readiness_s=1800,max_charge_su_per_job=1536),indent=2)+'\n');print('Prepared reversed-order prefetch then control, 3072 SU maximum total')
