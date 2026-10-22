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
    args = parser.parse_args()
    base = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    assert base in output.parents and not output.exists(), "Use a fresh evidence directory"
    assert all(re.fullmatch(r"\d+\.pbs\d+", job) for job in args.jobs)
    remote = r'''
from pathlib import Path
import datetime,hashlib,io,json,subprocess,sys,tarfile
base=Path('/scratch/users/industry/ai-hpc/apacsc42/apac2026/hpc')
jobs=JOBS
raw=json.loads(subprocess.check_output(['qstat','-xf','-F','json']+jobs).decode())['Jobs']
data={};metadata={}
for job in jobs:
 j=raw[job]
 assert j['job_state']=='F' and j['project']=='59000042'
 assert j['Job_Owner'].startswith('apacsc42@')
 assert j['Variable_List']['PBS_O_WORKDIR']==str(base/'job_scripts')
 assert int(j['Resource_List'].get('ngpus',0))==0
 metadata[job]={k:j[k] for k in ['Job_Name','job_state','Exit_status','queue','project','Resource_List','resources_used','exec_host','ctime','stime','obittime','Submit_arguments'] if k in j}
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
 script=Path(j.get('Submit_arguments','').split()[0]).name
 assert script.endswith('.pbs')
 for name in [script,'run_occ_common.sh',j['Job_Name']+'.o'+number]:
  path=base/'job_scripts'/name
  if not path.is_file() or path.is_symlink():continue
  b=path.read_bytes();assert len(b)<=100000 and b'\0' not in b
  data[str(path.relative_to(base))]=b
collection={'utc':datetime.datetime.utcnow().isoformat()+'Z','scope':'Completed shared CPU jobs, read-only intake; ownership and frozen input provenance unverified. No queue or budget mutation.','jobs':metadata,'limits':['Current script bytes need not equal submitted bytes','Environment excluded','No processor fields, mesh binaries, final zero-field seals or physical mapping collected','PBS exit zero alone is not acceptance of numerical results']}
data['collection.json']=json.dumps(collection,indent=2).encode()
assert sum(map(len,data.values()))<8000000
data['remote-file-sha256.json']=json.dumps({p:hashlib.sha256(b).hexdigest() for p,b in data.items()},indent=2).encode()
b=io.BytesIO()
with tarfile.open(fileobj=b,mode='w:gz') as t:
 for name,content in sorted(data.items()):
  item=tarfile.TarInfo(name);item.size=len(content);t.addfile(item,io.BytesIO(content))
sys.stdout.buffer.write(b.getvalue())
'''.replace("JOBS", repr(args.jobs))
    result = subprocess.run(
        [str(base / "tools/nscc-cpu-ssh.sh"), "bash -lc " + shlex.quote("python3 -c " + shlex.quote(remote))],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120, check=True,
    )
    with tarfile.open(fileobj=io.BytesIO(result.stdout)) as archive:
        members = archive.getmembers()
        assert all(m.isfile() and not m.name.startswith("/") and ".." not in Path(m.name).parts for m in members)
        assert sum(m.size for m in members) < 8000000
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
                      "scope": "Read-only sealed intake; not accepted results or owned reservations"}))


if __name__ == "__main__":
    main()
