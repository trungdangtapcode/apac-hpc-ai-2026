#!/usr/bin/env python3
"""Offline N48 mapping checks, including the full preparation CLI contract."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile
KIT=Path(__file__).resolve().parent
sys.path.insert(0,str(KIT))
from read_rank_proofs import validate_proof_dir
from source_checks import expected_case_definition,verify,verify_exact_tree
from seal_tree import inventory,rank_count
from native_checks import FIELDS
from placement import validate_balanced48, validate_interleaved48

def rejects(label,fn):
    try:fn()
    except (ValueError,AssertionError,OSError,KeyError):return
    raise AssertionError(label+' was incorrectly accepted')

def main():
    core=json.loads((KIT/'accepted-source-manifest-48.json').read_text())
    extra=json.loads((KIT/'supplementary-source-manifest-48.json').read_text())
    template=KIT/'payload-case-48'; pins=KIT/'source-pins-48.json'
    assert core['files'] and extra['files'] and json.loads(pins.read_text())['files']
    topology={'node0':set(range(0,56,2)),'node1':set(range(1,56,2))}
    balanced={'rank_count':48,'proofs':[{'affinity_cpu_ids':[i%56]} for i in range(48)]}
    assert validate_balanced48(balanced,topology)['passed']
    assert validate_interleaved48(balanced,topology)['passed']
    contiguous={'rank_count':48,'proofs':[{'affinity_cpu_ids':[n]} for n in list(range(0,48,2))+list(range(1,48,2))]}
    rejects('prior contiguous24/24 map',lambda:validate_interleaved48(contiguous,topology))
    skew={'rank_count':48,'proofs':[{'affinity_cpu_ids':[i]} for i in list(range(0,56,2))[:28]+list(range(1,56,2))[:20]]}
    rejects('28/20 skewed placement',lambda:validate_balanced48(skew,topology))
    with tempfile.TemporaryDirectory(prefix='iris-n48-proof-') as tmp:
        root=Path(tmp)
        d=root/'proof';d.mkdir()
        for rank in range(48):(d/f'rank-{rank:04d}.json').write_text(json.dumps({'rank':rank,'world_size':48,'hostname':'iris-test','affinity_cpu_ids':[rank]}))
        assert validate_proof_dir(d,48)['passed']
        (d/'rank-0047.json').unlink();rejects('missing N48 rank',lambda:validate_proof_dir(d,48))
        case=root/'source';case.mkdir()
        for name in core['files']:
            q=case/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b'fixture')
        for name,target in core.get('symlinks',{}).items():
            q=case/name;q.parent.mkdir(parents=True,exist_ok=True);q.symlink_to(target)
        (case/'READY').write_text('N=48\n')
        assert rank_count(case)==48 and set(inventory(case)['files'])==set(core['files']) and inventory(case)['symlinks']==core.get('symlinks',{})
        (case/'READY').write_text('N=40\n');assert rank_count(case)==40
    # Reproduce a complete N48 prepared source and exercise verify()'s tuple-return API.
    with tempfile.TemporaryDirectory(prefix='iris-source-verify-n48-') as tmp:
        base=Path(tmp);root=base/'accepted-N48';shutil.copytree(template,root,symlinks=True)
        (root/'Allrun').unlink();shutil.copy2(root/'system/controlDict.noWrite',root/'system/controlDict')
        shutil.copy2(root/'system/fvSolution.fixedIter',root/'system/fvSolution')
        (root/'system/include/caseDefinition').write_bytes(expected_case_definition(template/'system/include/caseDefinition',48))
        (root/'READY').write_text('N=48\nmethod=scotch\nnHierarchical=unused\nmesh=occDrivAer-65M\nstages=decomposePar restore0Dir renumberMesh potentialFoam applyBoundaryLayer\n')
        for rank in range(48):
            (root/f'processor{rank}'/'0').mkdir(parents=True);mesh=root/f'processor{rank}'/'constant'/'polyMesh';mesh.mkdir(parents=True)
            for field in FIELDS:(root/f'processor{rank}'/'0'/field).write_text(f'{rank} {field}\n')
            for name in ('points','faces','owner','neighbour','boundary'):(mesh/name).write_text(f'{rank} {name}\n')
        extra_file=root/'init-runs'/'retained.json';extra_file.parent.mkdir();extra_file.write_text('{"prepared":true}\n')
        actual=inventory(root);allfiles={}
        for basepath,_,names in os.walk(root,followlinks=False):
            for name in names:
                q=Path(basepath)/name
                if not q.is_symlink():allfiles[q.relative_to(root).as_posix()]=hashlib.sha256(q.read_bytes()).hexdigest()
        sup={'source':str(root),'files':{n:h for n,h in allfiles.items() if n not in actual['files']},'symlinks':{},'directories':sorted(x.relative_to(root).as_posix() for x in root.rglob('*') if x.is_dir() and not x.is_symlink())}
        manifest=base/'core.json';supplementary=base/'supplementary.json';manifest.write_text(json.dumps(actual));supplementary.write_text(json.dumps(sup))
        count,dirs=verify_exact_tree(root,actual,sup);assert isinstance(count,int) and dirs==len(sup['directories'])
        report=verify(root,template,pins,manifest,supplementary,48);assert report['passed'] and report['rank_count']==48 and report['directories']==dirs
        launcher=base/'offline-launcher'
        launcher.write_text('#!'+sys.executable+'\n'+'import sys,json\nfrom pathlib import Path\n'+'a=sys.argv[1:];n=int(a[a.index("-np")+1]);d=Path(a[a.index("--proof-dir")+1])\n'+'for r in range(n):\n (d/("rank-%04d.json"%r)).write_text(json.dumps({"rank":r,"world_size":n,"hostname":"offline-fixture","affinity_cpu_ids":[r]}))\n print("rank %d bound to fixture CPU"%r)\n')
        launcher.chmod(0o700);dest=base/'clone';result=base/'prep.json'
        cmd=[sys.executable,str(KIT/'prepare_arm.py'),'--source',str(root),'--destination',str(dest),'--manifest',str(manifest),'--supplementary',str(supplementary),'--template',str(template),'--pins',str(pins),'--rank-count','48','--recipe','balanced48','--probe-writer',str(KIT/'probe_writer.py'),'--proof-reader',str(KIT/'validate_arm_proofs.py'),'--mpirun',str(launcher),'--result',str(result)]
        subprocess.run(cmd,check=True,capture_output=True,text=True,timeout=30)
        prep=json.loads(result.read_text());assert prep['passed'] and prep['proof_files']==48 and prep['no_source_inode_reuse']
        assert 'endTime 40;' in (dest/'system/controlDict').read_text()
        # Altered source core is rejected by the same strict source gate.
        (root/'processor0/0/U').write_text('tampered')
        rejects('tampered source core',lambda:verify(root,template,pins,manifest,supplementary,48))
    assert "choices=('balanced48','default48')" in (KIT/'prepare_arm.py').read_text()
    assert "flags=['--map-by','ppr:24:package','--rank-by','span','--bind-to','core'] if a.recipe=='balanced48' else []" in (KIT/'prepare_arm.py').read_text()
    runner=(KIT/'run.py').read_text()
    assert "('B1-balanced48',48,'balanced48'),('A1-default48',48,'default48')" in runner
    assert "('A2-default48',48,'default48'),('B2-balanced48',48,'balanced48')" in runner
    assert 'SOLVER_CAP=1800' in runner and 'INTERNAL_SECONDS=8800' in runner and "'steps':40,'intervals':39" in runner
    assert "'file_handler':'OpenFOAM default uncollated for both; FOAM_FILEHANDLER must be unset.'" in runner
    script=(KIT/'job.sbatch').read_text()
    for expected in ('#SBATCH --partition=iris','#SBATCH --account=rdmaworkshop','#SBATCH --qos=low','#SBATCH --exclusive','#SBATCH --gpus=0','#SBATCH --ntasks=56','#SBATCH --nodelist=iris001','#SBATCH --time=02:30:00','timeout --signal=TERM --kill-after=10s 8940s','unset LD_PRELOAD LD_AUDIT FOAM_FILEHANDLER'):
        assert script.count(expected)==1,expected
    subprocess.run(['bash','-n',str(KIT/'job.sbatch')],check=True)
    subprocess.run([sys.executable,'-m','py_compile',*[str(KIT/n) for n in ('run.py','prepare_arm.py','source_checks.py','native_checks.py','native_output.py','helpers.py','probe_writer.py','read_rank_proofs.py','validate_arm_proofs.py','sampler.py')]],check=True)
    print('offline N48 mapping/source/preparation checks: PASS')
if __name__=='__main__':main()
