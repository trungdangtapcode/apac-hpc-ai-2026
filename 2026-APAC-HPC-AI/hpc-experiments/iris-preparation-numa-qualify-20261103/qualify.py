"""Bounded preparation-only copy/hash locality qualification; no solver runs."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys, time
from qualification_utils import (utc_now, process_masks, parse_numactl_show,
    parse_hardware_nodes, node_snapshot, require_two_node_snapshot, exact_tree_paths,
    supplementary_hashes, validate_manifest_paths, policy_signature)

KIT=Path(__file__).resolve().parent
SOURCE=Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch56-20261025T063431Z/artifacts/ready-N56-scotch')
MANIFEST=KIT/'accepted-source-manifest.json'
SUPPLEMENTARY=KIT/'supplementary-source-manifest.json'
DEADLINE=540.0
PHASE_CAP=90.0

def save(path,obj):
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def bounded(name,cmd,cwd,cap):
    remaining=DEADLINE-(time.monotonic()-T0)
    if cap>remaining-30: raise TimeoutError(f'{name}: insufficient protected deadline')
    p=subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=cap)
    return {'name':name,'argv':[str(x) for x in cmd],'returncode':p.returncode,'output':p.stdout[-12000:]}

T0=time.monotonic()
def main():
    run=KIT/'runs'/os.environ['SLURM_JOB_ID']; run.mkdir(parents=True,exist_ok=False)
    record={'state':'preflight','started_utc':utc_now(),'source':str(SOURCE),'arms':[],'scored_result':False}
    save(run/'qualification.json',record)
    try:
        assert os.environ.get('SLURM_NTASKS')=='56' and os.environ.get('SLURM_JOB_NUM_NODES')=='1'
        masks=process_masks(); assert len(masks['allowed_cpu_ids'])>=56 and set(masks['allowed_memory_node_ids'])>={0,1},masks
        numactl=shutil.which('numactl'); assert numactl,'numactl unavailable'
        hw=bounded('numactl-hardware',[numactl,'--hardware'],KIT,10); assert hw['returncode']==0
        topology=parse_hardware_nodes(hw['output']); assert topology=={'count':2,'node_ids':[0,1]},topology
        inherited=bounded('inherited-policy',[numactl,'--show'],KIT,10); assert inherited['returncode']==0
        assert parse_numactl_show(inherited['output'])['policy']!='unknown'
        inter=bounded('interleave-child-policy',[numactl,'--interleave=all',sys.executable,'-c',
            'import subprocess,sys; p=subprocess.run(["numactl","--show"],capture_output=True,text=True); print(p.stdout); sys.exit(p.returncode)'],KIT,10)
        assert inter['returncode']==0
        inter_policy=parse_numactl_show(inter['output']); assert inter_policy['policy']=='interleave' and set(inter_policy['interleave_nodes'])>={0,1},inter_policy
        assert policy_signature(inter_policy)!=policy_signature(parse_numactl_show(inherited['output'])), \
            'interleave treatment is effectively identical to inherited policy; reject before any copy'
        require_two_node_snapshot(node_snapshot())
        expected=json.loads(MANIFEST.read_text())
        supplementary=json.loads(SUPPLEMENTARY.read_text())
        assert supplementary['source']==str(SOURCE)
        validate_manifest_paths(expected,supplementary)
        combined={'files':{**expected['files'],**supplementary['files']},
                  'symlinks':{**expected['symlinks'],**supplementary['symlinks']}}
        scanpath=run/'source-before-inventory.json'
        scan=bounded('accepted-source-before',['python3',str(KIT/'seal_tree.py'),'inventory',str(SOURCE),str(scanpath)],KIT,90)
        assert scan['returncode']==0,scan
        actual=json.loads(scanpath.read_text()); assert actual==expected,'source differs from accepted manifest'
        exact_tree_paths(SOURCE,combined,supplementary['directories'])
        supplementary_hashes(SOURCE,supplementary)
        frozen_policy=parse_numactl_show(inherited['output'])
        save(run/'inherited-policy.json',frozen_policy)
        source_bytes=sum((SOURCE/name).stat().st_size for name in combined['files'])
        free=shutil.disk_usage(run).free; required=4*source_bytes+max(5*1024**3,int(.1*4*source_bytes))
        assert free>=required,{'free':free,'required':required,'source_bytes':source_bytes}
        record.update({'state':'running','process_masks':masks,'topology':topology,'inherited_policy':parse_numactl_show(inherited['output']),
          'interleave_child_policy':inter_policy,'source_manifest_sha256':hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
          'source_inventory_sha256':hashlib.sha256(json.dumps(actual,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
          'source_file_count':len(expected['files']),'supplementary_file_count':len(supplementary['files']),
          'supplementary_manifest_sha256':hashlib.sha256(SUPPLEMENTARY.read_bytes()).hexdigest(),
          'source_bytes':source_bytes,'free_bytes':free,'required_free_bytes':required,
          'arms_order':['A1-inherited','B1-interleave-all','B2-interleave-all','A2-inherited']})
        save(run/'qualification.json',record)
        for label,treatment in [('A1-inherited','inherited'),('B1-interleave-all','interleave-all'),('B2-interleave-all','interleave-all'),('A2-inherited','inherited')]:
            if DEADLINE-(time.monotonic()-T0)<PHASE_CAP+120: raise TimeoutError('protected time for remaining arms/source seal exhausted')
            dest=run/'copies'/label
            worker=[sys.executable,str(KIT/'copy_phase.py'),'--source',str(SOURCE),'--destination',str(dest),
              '--manifest',str(MANIFEST),'--supplementary',str(SUPPLEMENTARY),
              '--expected-policy',str(run/'inherited-policy.json'),
              '--numactl',numactl,'--treatment',treatment,'--result',str(run/(label+'.json'))]
            cmd=[numactl,'--interleave=all',*worker] if treatment=='interleave-all' else worker
            row=bounded(label,cmd,KIT,PHASE_CAP); record['arms'].append(row); save(run/'qualification.json',record)
            assert row['returncode']==0,(label,row)
            details=json.loads((run/(label+'.json')).read_text()); assert details['passed'] and details['no_source_inode_reuse']
        scanpath=run/'source-after-inventory.json'
        scan=bounded('accepted-source-after',['python3',str(KIT/'seal_tree.py'),'inventory',str(SOURCE),str(scanpath)],KIT,90)
        assert scan['returncode']==0 and json.loads(scanpath.read_text())==expected,'source changed during qualification'
        exact_tree_paths(SOURCE,combined,supplementary['directories'])
        supplementary_hashes(SOURCE,supplementary)
        record.update({'state':'completed','finished_utc':utc_now(),'source_after_matches':True,
          'interpretation':'Preparation-only. Whole-node NUMA counters are cumulative and non-attributed; no cache or solver-performance causality claim.'})
        save(run/'qualification.json',record)
    except Exception as exc:
        record.update({'state':'failed_or_rejected','finished_utc':utc_now(),'failure':type(exc).__name__,'detail':str(exc)[:1200]})
        save(run/'qualification.json',record); raise
if __name__=='__main__': main()
