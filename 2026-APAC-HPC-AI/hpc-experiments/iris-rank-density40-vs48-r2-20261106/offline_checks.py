#!/usr/bin/env python3
"""Offline guard checks for the frozen ABBA forty-versus-forty-eight trial."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,tempfile,sys
KIT=Path(__file__).resolve().parent
sys.path.insert(0,str(KIT))
from read_rank_proofs import validate_proof_dir
from source_checks import expected_case_definition,verify,verify_exact_tree
from seal_tree import inventory
from native_checks import FIELDS

def rejects(label,fn):
    try:fn()
    except (ValueError,AssertionError,OSError,KeyError):return
    raise AssertionError(label+' was incorrectly accepted')

def main():
    q=KIT.parent/'iris-rank-probe-files-qualify-20261106/completed-2294996/REVIEW.json'
    qualified=json.loads(q.read_text())
    assert qualified['passed'] and qualified['all_four_file_probes_passed']
    assert hashlib.sha256((KIT/'probe_writer.py').read_bytes()).hexdigest()==qualified['protocol_sha256']['probe_writer.py']
    assert hashlib.sha256((KIT/'read_rank_proofs.py').read_bytes()).hexdigest()==qualified['protocol_sha256']['read_rank_proofs.py']
    p40=json.loads((KIT/'source-pins-40.json').read_text())['files']
    p48=json.loads((KIT/'source-pins-48.json').read_text())['files']
    assert set(p40)==set(p48)
    assert [x for x in p40 if p40[x]!=p48[x]]==['system/include/caseDefinition']
    t40=KIT/'payload-case-40/system/include/caseDefinition'
    t48=KIT/'payload-case-48/system/include/caseDefinition'
    for template,rank in ((t40,40),(t48,48)):
        transformed=expected_case_definition(template,rank).decode()
        assert 'nCores              %d;'%rank in transformed
        assert 'decompositionMethod scotch;' in transformed
        assert '// Not the scotch cut.' in transformed
    with tempfile.TemporaryDirectory(prefix='iris-n40n48-proof-') as temp:
        root=Path(temp)
        for n in (40,48):
            d=root/str(n);d.mkdir()
            for rank in range(n):
                (d/('rank-%04d.json'%rank)).write_text(json.dumps({'rank':rank,'world_size':n,'hostname':'iris-test','affinity_cpu_ids':[rank]}))
            assert validate_proof_dir(d,n)['passed']
            (d/('rank-%04d.json'%(n-1))).unlink()
            rejects('missing N%d rank'%n,lambda:validate_proof_dir(d,n))
        bad=root/'bad';bad.mkdir()
        for rank in range(40):
            m=[0] if rank<2 else [rank]
            (bad/('rank-%04d.json'%rank)).write_text(json.dumps({'rank':rank,'world_size':40,'hostname':'iris-test','affinity_cpu_ids':m}))
        rejects('overlapping CPU masks',lambda:validate_proof_dir(bad,40))
        (bad/'rank-0002.json').write_text('{corrupt')
        rejects('corrupt proof JSON',lambda:validate_proof_dir(bad,40))
    # Exercise the actual inventory traversal for both accepted rank counts.
    from seal_tree import inventory, rank_count
    with tempfile.TemporaryDirectory(prefix='iris-n40n48-inventory-') as temp:
        for ranks in (40,48):
            case=Path(temp)/str(ranks);case.mkdir()
            core=json.loads((KIT/('accepted-source-manifest-%d.json'%ranks)).read_text())
            for name in core['files']:
                p=case/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'fixture')
            for name,target in core.get('symlinks',{}).items():
                p=case/name;p.parent.mkdir(parents=True,exist_ok=True);p.symlink_to(target)
            (case/'READY').write_text('N=%d\n'%ranks)
            assert rank_count(case)==ranks
            result=inventory(case)
            assert set(result['files'])==set(core['files']) and result['symlinks']==core['symlinks']
            (case/'READY').write_text('N=56\n')
            rejects('unselected READY rank count',lambda:rank_count(case))
    # Reproduce the terminal 40-rank manifest schema and call the same verify()
    # interface used by run.py before the first arm. This catches caller/helper
    # return-shape mismatches as well as path, symlink, and directory drift.
    with tempfile.TemporaryDirectory(prefix='iris-source-verify-r2-') as temp:
        root=Path(temp)/'accepted-N40'
        shutil.copytree(KIT/'payload-case-40',root,symlinks=True)
        (root/'Allrun').unlink()
        shutil.copy2(root/'system/controlDict.noWrite',root/'system/controlDict')
        shutil.copy2(root/'system/fvSolution.fixedIter',root/'system/fvSolution')
        cdef=root/'system/include/caseDefinition'
        cdef.write_bytes(expected_case_definition(KIT/'payload-case-40/system/include/caseDefinition',40))
        (root/'READY').write_text('N=40\nmethod=scotch\nnHierarchical=unused\nmesh=occDrivAer-65M\nstages=decomposePar restore0Dir renumberMesh potentialFoam applyBoundaryLayer\n')
        for rank in range(40):
            (root/f'processor{rank}'/'0').mkdir(parents=True)
            mesh=root/f'processor{rank}'/'constant'/'polyMesh';mesh.mkdir(parents=True)
            for field in FIELDS:(root/f'processor{rank}'/'0'/field).write_text(f'{rank} {field}\n')
            # Native decomposed OpenFOAM sources carry rank-local mesh files.
            for name in ('points','faces','owner','neighbour','boundary'):(mesh/name).write_text(f'{rank} {name}\n')
        extra_file=root/'init-runs'/'retained.json';extra_file.parent.mkdir();extra_file.write_text('{"prepared":true}\n')
        core=inventory(root)
        all_files={}
        for base,_,names in os.walk(root,followlinks=False):
            for name in names:
                p=Path(base)/name
                if not p.is_symlink():all_files[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
        supplementary_files={n:h for n,h in all_files.items() if n not in core['files']}
        directories=[]
        for base,dirs,_ in os.walk(root):
            for name in dirs:
                child=Path(base)/name
                if not child.is_symlink():directories.append(child.relative_to(root).as_posix())
        extra={'source':str(root),'files':supplementary_files,
               'symlinks':{},'directories':sorted(directories)}
        manifest=root.parent/'core.json';supplementary=root.parent/'supplementary.json'
        manifest.write_text(json.dumps(core));supplementary.write_text(json.dumps(extra))
        checked_files,checked_dirs=verify_exact_tree(root,core,extra)
        assert isinstance(checked_files,int) and isinstance(checked_dirs,int) and checked_dirs==len(directories)
        report=verify(root,KIT/'payload-case-40',KIT/'source-pins-40.json',manifest,supplementary,40)
        assert report['passed'] and report['rank_count']==40 and report['complete_files']==checked_files
        assert report['directories']==checked_dirs and report['inputs']['ready_sha256']
        clone=Path(temp)/'isolated-arm';shutil.copytree(root,clone,symlinks=True)
        clone_files,clone_dirs=verify_exact_tree(clone,core,extra)
        assert (clone_files,clone_dirs)==(checked_files,checked_dirs)
        assert inventory(clone)==core
    script=(KIT/'job.sbatch').read_text()
    for expected in ('#SBATCH --partition=iris','#SBATCH --account=rdmaworkshop','#SBATCH --qos=low',
        '#SBATCH --exclusive','#SBATCH --gpus=0','#SBATCH --ntasks=56','#SBATCH --nodelist=iris001',
        '#SBATCH --time=02:30:00','timeout --signal=TERM --kill-after=10s 8940s','unset LD_PRELOAD LD_AUDIT FOAM_FILEHANDLER'):
        assert script.count(expected)==1,expected
    runner=(KIT/'run.py').read_text()
    assert "('A1-control48',48,'control48'),('B1-candidate40',40,'candidate40')" in runner
    assert "('B2-candidate40',40,'candidate40'),('A2-control48',48,'control48')" in runner
    assert 'SOLVER_CAP=1800' in runner and 'INTERNAL_SECONDS=8800' in runner and 'steps\':40' in runner and 'intervals\':39' in runner
    assert "'file_handler':'OpenFOAM default uncollated" in runner
    assert 'scored_result\':False' in runner
    subprocess.run(['bash','-n',str(KIT/'job.sbatch')],check=True)
    subprocess.run([sys.executable,'-m','py_compile',*[str(KIT/n) for n in
        ('run.py','prepare_arm.py','source_checks.py','native_checks.py','native_output.py',
         'helpers.py','probe_writer.py','read_rank_proofs.py','validate_arm_proofs.py','sampler.py')]],check=True)
    print('offline comparison/protocol/source/config checks: PASS')
if __name__=='__main__':main()
