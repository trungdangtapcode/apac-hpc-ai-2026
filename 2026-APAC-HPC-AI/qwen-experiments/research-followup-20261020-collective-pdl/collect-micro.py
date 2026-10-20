"""Preserve a terminal own microbenchmark without applying a model-score reader."""
from pathlib import Path
import argparse,datetime,hashlib,json,re,shlex,subprocess,tarfile
ROOT=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
REMOTE='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015'
HELPER='/home/apacsc42/workspace/vpn-rootless/vpn.sh'
parser=argparse.ArgumentParser();parser.add_argument('job');args=parser.parse_args();assert re.fullmatch(r'\d+\.pbs\d+',args.job)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');dest=ROOT/'nscc-pbs/micro-collected'/args.job/stamp;dest.mkdir(parents=True)
def remote(command,path):
 with path.open('wb') as handle:
  result=subprocess.run(['bash',HELPER,'ssh-batch','bash -lc '+shlex.quote(command)],stdout=handle,stderr=subprocess.PIPE,timeout=300)
 path.with_suffix(path.suffix+'.stderr').write_bytes(result.stderr);assert result.returncode==0
remote('qstat -xf '+args.job,dest/'pbs-accounting.txt');raw=(dest/'pbs-accounting.txt').read_text();assert re.search(r'Job_Owner\s*=\s*apacsc42@',raw);assert re.search(r'job_state\s*=\s*F\b',raw),'Do not seal a live pilot'
remote('cd '+REMOTE+' && tar -czf - runs/'+args.job,dest/'raw-artifacts.tar.gz')
with tarfile.open(dest/'raw-artifacts.tar.gz') as archive:
 for member in archive.getmembers():
  path=Path(member.name);assert not path.is_absolute() and '..' not in path.parts and (member.isfile() or member.isdir())
 archive.extractall(dest,filter='data')
run=dest/'runs'/args.job;result=subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=run/'submitted',capture_output=True);(dest/'payload-checksums.txt').write_bytes(result.stdout+result.stderr);assert result.returncode==0
seal={str(f.relative_to(dest)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dest.rglob('*')) if f.is_file()};(dest/'evidence-sha256.json').write_text(json.dumps(seal,indent=2)+'\n')
print(json.dumps(dict(job=args.job,destination=str(dest),kind='isolated_microbenchmark_not_model_score',terminal=True,exit_status=int(re.search(r'Exit_status\s*=\s*(-?\d+)',raw).group(1)),payload_hashes_passed=True,sealed_files=len(seal)),indent=2))
