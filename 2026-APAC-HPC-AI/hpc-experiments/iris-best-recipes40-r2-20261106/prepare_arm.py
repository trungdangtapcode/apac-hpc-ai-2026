#!/usr/bin/env python3
"""Bounded clone, hash, time-window, and rank-map preparation for one arm."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from native_checks import field_snapshot
from seal_tree import inventory
from source_checks import verify_exact_tree

def main():
    ap=argparse.ArgumentParser()
    for name in ('source','destination','manifest','supplementary','probe-writer','proof-reader','result'):
        ap.add_argument('--'+name,required=True,type=Path)
    ap.add_argument('--rank-count',required=True,type=int,choices=(48,56))
    ap.add_argument('--mpirun',required=True)
    ap.add_argument('--recipe',required=True,choices=('original48','teammate56','io48'))
    a=ap.parse_args(); start=time.monotonic()
    expected_ranks=56 if a.recipe=='teammate56' else 48
    if a.rank_count!=expected_ranks: raise ValueError('recipe/rank-count mismatch')
    source=a.source; dest=a.destination
    core=json.loads(a.manifest.read_text()); extra=json.loads(a.supplementary.read_text())
    if dest.exists() or dest.is_symlink(): raise ValueError('arm destination must be new')
    shutil.copytree(source,dest,symlinks=True)
    cloned=inventory(dest)
    if cloned != core: raise ValueError('arm clone core hashes differ from accepted source')
    file_count,dir_count=verify_exact_tree(dest,core,extra,core_already_verified=True)
    source_fields=field_snapshot(source,a.rank_count)
    if field_snapshot(dest,a.rank_count)!=source_fields: raise ValueError('arm copy time-zero fields differ from accepted source')
    src_files=set(core['files'])|set(extra['files'])
    source_inodes={(os.stat(source/name).st_dev,os.stat(source/name).st_ino) for name in src_files}
    reused=[name for name in src_files if (os.stat(dest/name).st_dev,os.stat(dest/name).st_ino) in source_inodes]
    if reused: raise ValueError('arm copy reuses a source inode: '+repr(reused[:5]))
    ctrl=dest/'system/controlDict'; original=ctrl.read_text()
    import re
    changed,count=re.subn(r'(?m)^endTime[ \t]+[^;\n]+;[^\n]*$', 'endTime 40;', original)
    if count!=1: raise ValueError('expected exactly one controlDict endTime change')
    ctrl.write_text(changed)
    if (dest/'system/fvSolution').read_bytes() != (dest/'system/fvSolution.fixedIter').read_bytes():
        raise ValueError('source fvSolution is not fixedIter')
    proof_dir=dest/'rank-probe-proofs'
    proof_dir.mkdir()
    proof_result=dest/'rank-proofs.json'
    probe_log=dest/'rank-probe-launch.log'
    recipe_flags=['--map-by','socket','--bind-to','core'] if a.recipe=='teammate56' else []
    cmd=[a.mpirun,'--report-bindings','--display-map',*recipe_flags,'-np',str(a.rank_count),'--',sys.executable,str(a.probe_writer),'--proof-dir',str(proof_dir)]
    with probe_log.open('w') as out:
        p=subprocess.run(cmd,cwd=str(dest),stdout=out,stderr=subprocess.STDOUT,timeout=45)
    if p.returncode: raise RuntimeError('file-based MPI rank probe failed: %d'%p.returncode)
    verifier=[sys.executable,str(a.proof_reader),'--proof-dir',str(proof_dir),'--expected-ranks',str(a.rank_count),'--output',str(proof_result)]
    with (dest/'rank-proof-verifier.log').open('w') as out:
        v=subprocess.run(verifier,cwd=str(dest),stdout=out,stderr=subprocess.STDOUT,timeout=45)
    if v.returncode: raise RuntimeError('rank proof verifier failed: %d'%v.returncode)
    proof_report=json.loads(proof_result.read_text())
    if not proof_report.get('passed') or proof_report.get('rank_count')!=a.rank_count:
        raise ValueError('rank proof verifier did not pass expected complete count')
    records=proof_report['proofs']; binding_ranks=[]
    import re
    for line in probe_log.read_text(errors='replace').splitlines():
        bind=re.search(r'(?:MCW\s+)?rank\s+(\d+)\s+bound to\b',line,re.I)
        if bind: binding_ranks.append(int(bind.group(1)))
    if sorted(set(binding_ranks))!=list(range(a.rank_count)):
        raise ValueError('Open MPI --report-bindings did not report every rank')
    hosts=set(proof_report['hostnames'])
    masks=[set(x['affinity_cpu_ids']) for x in records]
    result={'passed':True,'rank_count':a.rank_count,'source':str(source),'destination':str(dest),
            'clone_core_files':len(cloned['files']),'full_files':file_count,'directories':dir_count,
            'no_source_inode_reuse':True,'source_field_count':source_fields['field_count'],
            'control_change':'only endTime=40','recipe':a.recipe,'mpirun_rank_probe_command':cmd,'rank_proof_verifier_command':verifier,
            'rank_probe_log':str(probe_log),'rank_proof_files':str(proof_dir),'rank_proof_verifier_result':str(proof_result),
            'rank_count_complete':True,'hostnames':sorted(hosts),
            'rank_binding_reports_complete':True,'cpu_affinity_masks':{str(x['rank']):x['affinity_cpu_ids'] for x in records},
            'cpu_affinity_nonoverlap':True,
            'affinity_phase':'Pre-MPI_Init launcher-process OS-affinity observation from one-file-per-rank proof artifacts under the matching mpirun launch; not post-MPI/native solver affinity.',
            'placement_limit':'Observed OS CPU masks and binding reports are retained. No per-socket rank layout is assumed; unequal socket counts are possible.',
            'elapsed_seconds':time.monotonic()-start}
    a.result.parent.mkdir(parents=True,exist_ok=True);a.result.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'passed':True,'rank_count':a.rank_count,'elapsed_seconds':result['elapsed_seconds']}))
if __name__=='__main__': main()
