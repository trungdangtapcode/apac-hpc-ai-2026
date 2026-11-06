#!/usr/bin/env python3
"""Clone, seal, and strictly verify one native Scotch40/48 solver arm."""
import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path
from native_checks import field_snapshot
from seal_tree import inventory
from source_checks import verify_exact_tree, verify_inputs

def main():
    p=argparse.ArgumentParser()
    for n in ('source','destination','manifest','supplementary','template','pins','probe-writer','proof-reader','result'):
        p.add_argument('--'+n,required=True,type=Path)
    p.add_argument('--rank-count',required=True,type=int,choices=(40,48))
    p.add_argument('--mpirun',required=True)
    p.add_argument('--recipe',required=True,choices=('candidate40','control48'))
    a=p.parse_args();started=time.monotonic();ranks=a.rank_count
    if (a.recipe,ranks) not in (('candidate40',40),('control48',48)):
        raise ValueError('recipe and rank count must identify the corresponding source')
    source=a.source.resolve(strict=True);dest=a.destination
    core=json.loads(a.manifest.read_text());extra=json.loads(a.supplementary.read_text())
    verify_inputs(source,a.template,a.pins,ranks)
    if dest.exists() or dest.is_symlink():raise ValueError('arm destination must be new')
    def phase(name):
        print(json.dumps({"stage":name,"elapsed_seconds":time.monotonic()-started}),flush=True)
    phase("clone-start")
    shutil.copytree(source,dest,symlinks=True)
    phase("clone-complete")
    if inventory(dest)!=core:raise ValueError('clone core inventory differs from accepted source')
    phase('clone-core-hashes-verified')
    files,dirs=verify_exact_tree(dest,core,extra,core_already_verified=True)
    phase("clone-complete-tree-verified")
    before=field_snapshot(source,ranks)
    if field_snapshot(dest,ranks)!=before:raise ValueError('cloned initial fields differ byte-for-byte')
    core_names=set(core['files'])|set(core.get('symlinks',{}))
    extra_names=set(extra['files'])|set(extra.get('symlinks',{}))
    source_names=core_names|extra_names
    src={(os.stat(source/n).st_dev,os.stat(source/n).st_ino) for n in source_names if not (source/n).is_symlink()}
    reused=[n for n in source_names if not (dest/n).is_symlink() and (os.stat(dest/n).st_dev,os.stat(dest/n).st_ino) in src]
    if reused:raise ValueError('clone reuses source inodes: '+repr(reused[:4]))
    import re
    ctrl=dest/'system/controlDict';original=ctrl.read_text()
    changed,count=re.subn(r'(?m)^endTime[ \t]+[^;\n]+;[^\n]*$','endTime 40;',original)
    if count!=1:raise ValueError('expected exactly one endTime directive change')
    ctrl.write_text(changed)
    if (dest/'system/fvSolution').read_bytes()!=(dest/'system/fvSolution.fixedIter').read_bytes():
        raise ValueError('solver source is not fixed-iteration')
    phase("fields-and-inodes-verified")
    proofdir=dest/'rank-probe-proofs';proofdir.mkdir();proofout=dest/'rank-proofs.json'
    prober=dest/'rank-probe-launch.log'
    flags=['--map-by','socket','--bind-to','core'] if ranks==40 else []
    cmd=[a.mpirun,'--report-bindings','--display-map',*flags,'-np',str(ranks),'--',sys.executable,str(a.probe_writer),'--proof-dir',str(proofdir)]
    with prober.open('w') as f:q=subprocess.run(cmd,cwd=dest,stdout=f,stderr=subprocess.STDOUT,timeout=45)
    if q.returncode:raise RuntimeError('per-rank proof writer failed: %d'%q.returncode)
    verifier=[sys.executable,str(a.proof_reader),'--proof-dir',str(proofdir),'--expected-ranks',str(ranks),'--output',str(proofout)]
    with (dest/'rank-proof-verifier.log').open('w') as f:q=subprocess.run(verifier,cwd=dest,stdout=f,stderr=subprocess.STDOUT,timeout=45)
    if q.returncode:raise RuntimeError('strict per-rank verifier failed: %d'%q.returncode)
    phase("rank-files-verified")
    proofs=json.loads(proofout.read_text())
    if not proofs.get('passed') or proofs.get('rank_count')!=ranks:raise ValueError('incomplete affinity proof records')
    bind=[]
    for line in prober.read_text(errors='replace').splitlines():
        m=re.search(r'(?:MCW\s+)?rank\s+(\d+)\s+bound to\b',line,re.I)
        if m:bind.append(int(m[1]))
    if sorted(set(bind))!=list(range(ranks)):raise ValueError('Open MPI binding report omitted one or more ranks')
    result={'passed':True,'recipe':a.recipe,'rank_count':ranks,'source':str(source),'destination':str(dest),
        'core_files':len(core['files']),'complete_files':files,'directories':dirs,
        'no_source_inode_reuse':True,'initial_time_zero_fields':before['field_count'],
        'endTime_change':'40','fixed_iteration_source':True,'rank_count_complete':True,
        'rank_binding_reports_complete':True,'rank_proof_verifier':str(proofout),
        'proof_files':len(proofs['proof_files']),'hostnames':proofs['hostnames'],
        'affinity_phase':proofs['scope'],'elapsed_seconds':time.monotonic()-started}
    a.result.parent.mkdir(parents=True,exist_ok=True);a.result.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('passed','recipe','rank_count','proof_files','elapsed_seconds')}))
if __name__=='__main__':main()
