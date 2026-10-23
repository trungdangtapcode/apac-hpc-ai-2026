#!/usr/bin/env python3
"""Read bounded, existing ASCII processor boundaries; launch no MPI or jobs."""
from pathlib import Path
import hashlib
import io
import json
import shlex
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parent
HELPER = ROOT.parent / 'tools/nscc-cpu-ssh.sh'
REMOTE = r'''
from pathlib import Path
import datetime,hashlib,io,json,sys,tarfile
r=Path('/scratch/users/industry/ai-hpc/apacsc42/apac2026/hpc/runs/4n-scotch-25921488')
paths=[r/('processor'+str(i))/'constant/polyMesh/boundary' for i in range(512)]
assert len(list(r.glob('processor*/constant/polyMesh/boundary')))==512
members={}; rows=[]
for rank,p in enumerate(paths):
 assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(r.resolve())
 assert 0<p.stat().st_size<131072
 before=p.stat(); b=p.read_bytes(); after=p.stat()
 assert before.st_size==after.st_size==len(b) and before.st_mtime_ns==after.st_mtime_ns
 # polyBoundaryMesh dictionaries are text even when global writeFormat is binary.
 assert b'\0' not in b
 b.decode('ascii')
 name='boundaries/processor'+str(rank)+'/boundary';members[name]=b
 rows.append({'rank':rank,'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'source_mtime_ns':before.st_mtime_ns})
assert sum(len(b) for b in members.values())<8000000
log=r/'logFiles/10_decomposePar.log'; b=log.read_bytes();assert len(b)<600000 and b'\0' not in b
members['10_decomposePar.log']=b
meta={'collected_utc':datetime.datetime.utcnow().isoformat()+'Z','source_directory':str(r),'originating_native_job':'25921488.pbs101','ranks':512,'members':rows,'decompose_log_sha256':hashlib.sha256(b).hexdigest(),'scope':'Current existing ASCII boundary artifacts only. These files were not sealed at original job submission. No mesh binaries, processor fields, MPI, qsub or scheduler mutation. A graph is not measured communication.'}
members['collection.json']=(json.dumps(meta,indent=2)+'\n').encode()
out=io.BytesIO()
with tarfile.open(fileobj=out,mode='w:gz') as t:
 for n,b in sorted(members.items()):
  info=tarfile.TarInfo(n);info.size=len(b);info.mode=0o644;info.mtime=0;t.addfile(info,io.BytesIO(b))
sys.stdout.buffer.write(out.getvalue())
'''
# ASPIRE's system Python is 3.6; avoid newer pathlib interfaces remotely.
REMOTE = REMOTE.replace("p.resolve().is_relative_to(r.resolve())",
                        "str(p.resolve()).startswith(str(r.resolve())+'/')")


def main():
    target = ROOT / 'collected'
    assert not target.exists(), 'Preserve previous collection; never overwrite raw evidence'
    result = subprocess.run(['bash', str(HELPER), 'python3 -c ' + shlex.quote(REMOTE)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
    if result.returncode:
        raise RuntimeError('Read-only intake failed: ' + result.stderr.decode(errors='replace')[-1000:])
    with tarfile.open(fileobj=io.BytesIO(result.stdout), mode='r:gz') as archive:
        members = archive.getmembers()
        assert len(members) == 514 and len({m.name for m in members}) == 514
        assert all(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
                   for m in members)
        assert sum(m.size for m in members) < 8_500_000
        data = {m.name: archive.extractfile(m).read() for m in members}
    metadata = json.loads(data['collection.json'])
    assert len(metadata['members']) == 512
    for row in metadata['members']:
        assert hashlib.sha256(data[row['path']]).hexdigest() == row['sha256']
    reference = ROOT.parent / 'four-node-review-20261023/collected/runs/4n-scotch-25921488/logFiles/10_decomposePar.log'
    assert reference.read_bytes() == data['10_decomposePar.log'], 'Current decomposition log differs from sealed native intake'
    target.mkdir()
    for name, payload in data.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    (ROOT / 'boundaries.tar.gz').write_bytes(result.stdout)
    (ROOT / 'intake-validation.json').write_text(json.dumps(dict(
        passed=True, ascii_boundaries=512, bytes=sum(len(v) for v in data.values()),
        archive_sha256=hashlib.sha256(result.stdout).hexdigest(),
        decompose_log_matches_sealed_native_intake=True,
        original_boundary_submission_seal_available=False,
        mesh_or_field_identity_established=False,
        local_member_hashes_verified=True), indent=2) + '\n')
    print(json.dumps(dict(passed=True, files=len(data), collected_utc=metadata['collected_utc'])))


if __name__ == '__main__':
    main()
