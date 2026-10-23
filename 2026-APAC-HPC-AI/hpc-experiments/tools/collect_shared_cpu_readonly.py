"""Seal bounded text from completed shared CPU jobs without adopting their ownership.

The remote operation only reads PBS metadata and whitelisted research files.
Current scripts are evidence at collection time, not frozen submission receipts.
"""
import argparse
import datetime
import hashlib
import io
import json
from pathlib import Path
import re
import shlex
import subprocess
import tarfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("jobs", nargs="+")
    parser.add_argument("--history-free-metadata", type=Path,
                        help="Retained own-account queue snapshot; requested resources only, never terminal proof")
    parser.add_argument("--max-text-bytes", type=int, default=8_000_000,
                        help="Bounded text intake size, at most 24 MB for longer endpoint batches")
    args = parser.parse_args()
    base = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    assert base in output.parents and not output.exists(), "Use a fresh evidence directory"
    assert all(re.fullmatch(r"\d+\.pbs\d+", job) for job in args.jobs)
    assert 0 < args.max_text_bytes <= 24_000_000
    historical = None
    if args.history_free_metadata:
        snapshot_path = args.history_free_metadata.resolve()
        assert base in snapshot_path.parents
        snapshot_bytes = snapshot_path.read_bytes()
        snapshot = json.loads(snapshot_bytes)
        historical = {
            "snapshot_utc": snapshot["utc"],
            "snapshot_sha256": hashlib.sha256(snapshot_bytes).hexdigest(),
            "snapshot_source": str(snapshot_path.relative_to(base)),
            "jobs": {job: snapshot["jobs"][job] for job in args.jobs},
        }
        assert all(str(job["project"]) == "59000042" for job in historical["jobs"].values())
    remote = r'''
from pathlib import Path
import datetime,hashlib,io,json,subprocess,sys,tarfile
base=Path('/scratch/users/industry/ai-hpc/apacsc42/apac2026/hpc')
jobs=JOBS
historical=HISTORICAL
p=subprocess.run(['qstat','-xf','-F','json']+jobs,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
raw=json.loads(p.stdout).get('Jobs',{}) if p.stdout.strip().startswith('{') else {}
if historical is None:
 assert p.returncode==0
else:
 assert not raw and p.returncode!=0 and 'Unknown Job Id' in p.stderr, 'History returned; collect terminal proof instead'
data={};metadata={}
for job in jobs:
 if historical is None:
  j=raw[job]
  assert j['job_state']=='F' and j['project']=='59000042'
  assert j['Job_Owner'].startswith('apacsc42@')
  assert j['Variable_List']['PBS_O_WORKDIR']==str(base/'job_scripts')
  metadata[job]={k:j[k] for k in ['Job_Name','job_state','Exit_status','queue','project','Resource_List','resources_used','exec_host','ctime','stime','obittime','Submit_arguments'] if k in j}
 else:
  j=historical['jobs'][job]
  assert str(j['project'])=='59000042'
  metadata[job]={k:j[k] for k in ['Job_Name','queue','project','Resource_List','Submit_arguments'] if k in j}
  metadata[job].update({'scheduler_history_unavailable':True,'final_scheduler_state':None,'final_exit_status':None,'terminal_resources':None,'historical_job_state_at_snapshot':j['job_state'],'request_snapshot_utc':historical['snapshot_utc'],'request_snapshot_sha256':historical['snapshot_sha256']})
 assert int(j['Resource_List'].get('ngpus',0))==0
 metadata[job]['work_directory']=str(base/'job_scripts')
 number=job.split('.')[0]
 runs=list((base/'runs').glob('*-'+number));assert len(runs)==1
 run=runs[0];metadata[job]['run_directory']=str(run)
 selected=[]
 for root in ['logFiles','system','0.orig','postProcessing']:
  parent=run/root
  if parent.is_dir():
   selected.extend(p for p in parent.rglob('*') if p.is_file() and not p.is_symlink())
 selected.extend(p for p in (run/'constant').glob('*') if p.is_file() and not p.is_symlink())
 for path in selected:
  rel=path.relative_to(base)
  if any(part.startswith('processor') or part in ['polyMesh','dynamicCode'] for part in rel.parts):continue
  if path.name=='00_environment.log':continue
  assert path.stat().st_size<=600000, str(path)
  b=path.read_bytes();assert b'\0' not in b
  data[str(rel)]=b
 environment=run/'logFiles/00_environment.log'
 if environment.is_file() and not environment.is_symlink():
  b=environment.read_bytes();assert len(b)<10000
  allowed={'timestamp','nodes','ranks','end_time','decomposition','hierarchical_shape','host','FI_OFI_RXM_USE_SRX','FI_VERBS_PREFER_XRC','OMP_NUM_THREADS','WM_PROJECT_VERSION','WM_PRECISION_OPTION','WM_LABEL_SIZE','WM_MPLIB','WM_OPTIONS'}
  selected_lines=[line for line in b.decode().splitlines() if line.split('=',1)[0] in allowed and '=' in line]
  data[str((run/'logFiles/00_environment.selected.txt').relative_to(base))]=('\n'.join(selected_lines)+'\n').encode()
  metadata[job]['environment_original_sha256']=hashlib.sha256(b).hexdigest()
 script=Path(j.get('Submit_arguments','').split()[0]).name
 assert script.endswith('.pbs')
 for name in [script,'run_occ_common.sh',j['Job_Name']+'.o'+number]:
  path=base/'job_scripts'/name
  if not path.is_file() or path.is_symlink():continue
  b=path.read_bytes();assert len(b)<=100000 and b'\0' not in b
  data[str(path.relative_to(base))]=b
collection={'utc':datetime.datetime.utcnow().isoformat()+'Z','scope':'Completed shared CPU jobs, read-only intake; ownership and frozen input provenance unverified. No queue or budget mutation.','jobs':metadata,'limits':['Current script bytes need not equal submitted bytes','Environment excluded','No processor fields, mesh binaries, final zero-field seals or physical mapping collected','PBS exit zero alone is not acceptance of numerical results']}
collection['limits'][1]='Only whitelisted research environment lines retained; full environment excluded'
if historical is not None:
 collection['scope']='Native scratch evidence only; scheduler history unavailable. No final exit, whole-allocation elapsed, cost or terminal claim.'
 collection['historical_request_snapshot']={k:v for k,v in historical.items() if k!='jobs'}
 collection['limits'].append('Historical requested resources are not actual terminal usage; retain prior maximums')
data['collection.json']=json.dumps(collection,indent=2).encode()
assert sum(map(len,data.values()))<MAX_TEXT_BYTES, ('text intake bytes',sum(map(len,data.values())))
data['remote-file-sha256.json']=json.dumps({p:hashlib.sha256(b).hexdigest() for p,b in data.items()},indent=2).encode()
b=io.BytesIO()
with tarfile.open(fileobj=b,mode='w:gz') as t:
 for name,content in sorted(data.items()):
  item=tarfile.TarInfo(name);item.size=len(content);t.addfile(item,io.BytesIO(content))
sys.stdout.buffer.write(b.getvalue())
'''.replace("JOBS", repr(args.jobs)).replace("HISTORICAL", repr(historical)).replace("MAX_TEXT_BYTES", str(args.max_text_bytes))
    result = subprocess.run(
        [str(base / "tools/nscc-cpu-ssh.sh"), "bash -lc " + shlex.quote("python3 -c " + shlex.quote(remote))],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120, check=False,
    )
    if result.returncode:
        raise SystemExit("Remote read-only collection failed (status %s):\n%s" % (
            result.returncode, result.stderr.decode("utf8", "replace")[-3000:]))
    with tarfile.open(fileobj=io.BytesIO(result.stdout)) as archive:
        members = archive.getmembers()
        assert all(m.isfile() and not m.name.startswith("/") and ".." not in Path(m.name).parts for m in members)
        assert sum(m.size for m in members) < args.max_text_bytes
        output.mkdir(parents=True)
        (output / "raw-text-evidence.tar.gz").write_bytes(result.stdout)
        for member in members:
            path = output / member.name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(archive.extractfile(member).read())
    remote_hashes = json.loads((output / "remote-file-sha256.json").read_text())
    assert all(hashlib.sha256((output / path).read_bytes()).hexdigest() == digest for path, digest in remote_hashes.items())
    hashes = {str(path.relative_to(output)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in output.rglob("*") if path.is_file()}
    (output / "evidence-sha256.json").write_text(json.dumps(hashes, indent=2) + "\n")
    print(json.dumps({"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      "files": len(members), "jobs": args.jobs, "output": str(output),
                      "scope": "Read-only sealed intake; not accepted results or owned reservations",
                      "scheduler_history_unavailable": historical is not None}))


if __name__ == "__main__":
    main()
