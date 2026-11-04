from pathlib import Path

import datetime,hashlib,json,math,os,re,shutil,statistics,subprocess,time,socket

from case_checks import source_check

from native_checks import field_snapshot

from native_output import review_native_output

def save(path,data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')

def remaining():
    return int(DEADLINE-time.monotonic())

def phase(label,state,extra=None):
    row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':label,'state':state}
    if extra: row.update(extra)
    with (RUN/'phases.jsonl').open('a') as f:f.write(json.dumps(row,sort_keys=True)+'\n')

def bounded(label,args,cwd,cap):
    left=remaining()-60
    assert left>0,('shared internal deadline before '+label,left)
    limit=min(cap,left)
    started=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
    phase(label,'start',{'cap_seconds':limit})
    with (RUN/(label+'.log')).open('w') as f:
        try:
            p=subprocess.run(['timeout','--signal=TERM','--kill-after=10s',str(limit)+'s',*map(str,args)],cwd=str(cwd),stdout=f,stderr=subprocess.STDOUT,timeout=limit+20)
            rc=p.returncode
        except subprocess.TimeoutExpired:
            rc=124
    result={'returncode':rc,'cap_seconds':limit,'elapsed_seconds':time.monotonic()-started,'utc_start':utc,'command':list(map(str,args))}
    save(RUN/(label+'.status.json'),result);phase(label,'exit',{'returncode':rc,'elapsed_seconds':result['elapsed_seconds']})
    assert rc==0,(label,rc)
    return result

def node_snapshot(label,dest):
    started=time.monotonic_ns()
    snap={'label':label,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'time_ns':time.time_ns(),
          'scope':'Whole-node procfs counters; not per-process hardware bandwidth or attribution.'}
    for name in ('meminfo','vmstat','pressure/memory','cpuinfo'):
        p=Path('/proc')/name
        try:snap[name]=p.read_text()
        except Exception as exc:snap[name+'_error']={'type':type(exc).__name__,'message':str(exc)}
    snap['collection_elapsed_ms']=(time.monotonic_ns()-started)/1e6
    save(Path(dest)/(label+'-node-snapshot.json'),snap)

def runtime_snapshot(label):
    tools={}
    for name in ('simpleFoam','mpirun'):
        found=shutil.which(name)
        assert found,(name,'not present on PATH')
        real=Path(found).resolve();tools[name]={'path':found,'resolved_path':str(real),'sha256':hashlib.sha256(real.read_bytes()).hexdigest()}
    ldd=subprocess.run(['ldd',tools['simpleFoam']['resolved_path']],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True)
    libraries={}
    for line in ldd.stdout.splitlines():
        m=re.search(r'=>\s+(/\S+)',line)
        if not m: m=re.match(r'\s*(/\S+)\s+\(',line)
        if m:
            path=Path(m.group(1)).resolve()
            if path.is_file():libraries[str(path)]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
    assert libraries,'ldd produced no resolved library identities'
    assert 'not found' not in ldd.stdout,'unresolved OpenFOAM runtime library'
    snapshot={'label':label,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ldd_simpleFoam':ldd.stdout,'tools':tools,'libraries':libraries}
    save(RUN/(label+'.json'),snapshot)
    return snapshot

def runtime_identity_equal(before,after):
    return before['tools']==after['tools'] and before['libraries']==after['libraries']

KIT=Path(__file__).resolve().parent
DEADLINE=0.0
RUN=None
