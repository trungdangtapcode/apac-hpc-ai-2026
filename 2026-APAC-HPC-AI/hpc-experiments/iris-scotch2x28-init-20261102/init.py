"""Native Iris Scotch socket-tree cut, graph filter, then required initialization if useful."""
from pathlib import Path
import hashlib, json, os, re, shutil, stat, subprocess, sys, time
from native_checks import FATAL, field_snapshot, sha256
from interface_graph import graph, compare

KIT = Path(__file__).resolve().parent
WORK = KIT.parent
SHARED = Path('/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam')
CASE_SRC = KIT / 'payload-case'
MESH_SRC = SHARED / 'occDrivAer/polyMesh'
CONTROL = Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch56-20261025T063431Z/artifacts/ready-N56-scotch')
DEADLINE_SECONDS = 1680
DEADLINE = time.monotonic() + DEADLINE_SECONDS
RUN = None
CASE = None


def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def bounded(label, args, cwd, cap):
    remaining = int(DEADLINE - time.monotonic())
    assert remaining >= cap + 30, ('insufficient full-stage window before ' + label, remaining, cap)
    seconds = cap
    log = RUN / (label + '.log')
    started = time.monotonic()
    with log.open('w') as out:
        proc = subprocess.run(['/usr/bin/time', '-v', '-o', str(RUN / (label + '.resource.txt')),
            'timeout', '--signal=TERM', '--kill-after=10s', str(seconds) + 's', *map(str,args)],
            cwd=str(cwd), stdout=out, stderr=subprocess.STDOUT, timeout=seconds + 20)
    row = {'command':list(map(str,args)), 'returncode':proc.returncode,
           'elapsed_seconds':time.monotonic()-started, 'cap_seconds':seconds}
    save(RUN / (label + '.status.json'), row)
    assert proc.returncode == 0, (label, proc.returncode)
    return log


def expected_config(relative):
    raw = (KIT / 'payload-case' / relative).read_bytes()
    text = raw.decode()
    if relative == 'system/include/caseDefinition':
        text, count = re.subn(r'(?m)^nCores\s+\d+\s*;[^\n]*$', 'nCores              56;', text); assert count == 1
        text, count = re.subn(r'(?m)^decompositionMethod\s+\w+\s*;[^\n]*$', 'decompositionMethod scotch;', text); assert count == 1
    elif relative == 'system/decomposeParDict':
        assert 'scotchCoeffs' not in text
        marker = '// ************************************************************************* //'
        assert text.count(marker) == 1
        text = text.replace(marker, 'scotchCoeffs\n{\n    domains       (2 28);\n    domainWeights (1 0.1);\n}\n\n' + marker)
    return text.encode()


def check_case_inputs(root, candidate=False):
    pin_doc = json.loads((KIT / 'source-pins.json').read_text())
    assert len(pin_doc['files']) == 41
    for relative, digest in pin_doc['files'].items():
        source = CASE_SRC / relative
        assert source.is_file() and not source.is_symlink(), ('missing canonical file', relative)
        assert sha256(source) == digest, ('group source hash differs from retained pins', relative)
        target = root / relative
        if relative == 'Allrun' and candidate:
            assert not target.exists(), 'Do not ship/execute Allrun in this bounded preparation'
            continue
        expected = (expected_config(relative) if candidate and relative in ('system/include/caseDefinition','system/decomposeParDict')
                    else (KIT/'payload-case'/relative).read_bytes())
        assert target.is_file() and not target.is_symlink() and target.read_bytes() == expected, ('input mismatch', relative)
    if candidate:
        text = (root/'system/decomposeParDict').read_text()
        assert re.search(r'(?m)^\s*domains\s+\(2\s+28\);\s*$', text)
        assert re.search(r'(?m)^\s*domainWeights\s+\(1\s+0\.1\);\s*$', text)
        assert not re.search(r'(?m)^\s*processorWeights\b', text)
    return {'passed':True,'canonical_inputs':41,'allowed_text_changes':['nCores=56','decompositionMethod=scotch','scotchCoeffs domains=(2 28), domainWeights=(1 0.1)'],'processorWeights_absent':True}


def check_mesh():
    doc=json.loads((KIT/'expected-mesh.json').read_text()); rows=[]
    for item in doc['unpacked_members_match_archive']:
        path=MESH_SRC/item['file']; row={'file':item['file'],'bytes':path.stat().st_size,'sha256':sha256(path)}
        assert row==item, ('canonical mesh mismatch',item['file'])
        rows.append(row)
    assert len(rows)==8
    return {'passed':True,'members':rows,'archive_sha256':doc['archive_sha256']}


def main():
    global RUN, CASE
    assert os.environ.get('SLURM_NTASKS')=='56' and os.environ.get('SLURM_JOB_NUM_NODES')=='1'
    RUN=WORK/'runs'/os.environ['SLURM_JOB_ID']; RUN.mkdir(parents=True,exist_ok=False)
    artifacts=WORK/'artifacts'; artifacts.mkdir(exist_ok=True)
    CASE=artifacts/('ready-N56-scotch2x28-'+os.environ['SLURM_JOB_ID'])
    assert not CASE.exists() and not CASE.is_symlink(), 'Refuse any pre-existing candidate path'
    assert CASE_SRC.is_dir() and not CASE_SRC.is_symlink() and MESH_SRC.is_dir() and not MESH_SRC.is_symlink()
    assert CONTROL.is_dir() and not CONTROL.is_symlink() and (CONTROL/'READY').is_file()
    save(RUN/'intent.json',{'candidate':'native Scotch (domains 2 28, domainWeights 1 0.1)','nodes':1,'cpus':56,
        'maximum_seconds':1800,'maximum_allocated_CPU_hours':28,'gpu_count':0,
        'control_source':str(CONTROL),'candidate_root':str(CASE),'method_weight_interpretation':'Synthetic 10:1 hierarchy; not measured latency or bandwidth.',
        'filter_gates':{'cross_package_face_reduction_percent_minimum':5,'maximum_cell_excess_percent':3,'total_faces_increase_percent_maximum':10,'worst_rank_faces_increase_percent_maximum':10,'worst_rank_neighbor_patches_increase_maximum':2},
        'solver_measurement':False,'scope':'Fresh native serial Scotch cut, logical package graph filter, then mandatory parallel initialization only if every predeclared graph gate passes.'})
    bounded('serial-mesh-check',['python3',KIT/'validate_cut.py','--mesh',MESH_SRC,'--expected',KIT/'expected-mesh.json','--mesh-only','--output',RUN/'mesh-check.json'],KIT,180)
    mesh_result=json.loads((RUN/'mesh-check.json').read_text()); assert mesh_result['passed']; save(RUN/'serial_mesh-preflight.json',mesh_result)
    save(RUN/'canonical-source-preflight.json',check_case_inputs(CASE_SRC))
    control_graph=graph(CONTROL,'accepted-default-scotch')
    save(RUN/'control-graph.json',control_graph)
    native_total=re.search(r'^Number of processor faces = (\d+)',(CONTROL/'logFiles/decomposePar.log').read_text(),re.M)
    assert native_total and int(native_total[1])==control_graph['unique_interface_faces'], 'Control parser does not replay native face total'
    accepted=json.loads((KIT/'accepted-control-manifest.json').read_text())
    assert all(accepted['files'][name]==digest for name,digest in control_graph['boundary_file_sha256'].items()), 'Control boundary hashes differ from accepted source'
    pin_doc=json.loads((KIT/'source-pins.json').read_text())
    for relative in pin_doc['files']:
        if relative=='Allrun': continue
        target=CASE/relative; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(CASE_SRC/relative,target)
        target.chmod(target.stat().st_mode | stat.S_IWUSR)
    # Candidate dictionary edits are exact and allow-listed above; no accepted tree is touched.
    (CASE/'system/include/caseDefinition').write_bytes(expected_config('system/include/caseDefinition'))
    (CASE/'system/decomposeParDict').write_bytes(expected_config('system/decomposeParDict'))
    (CASE/'constant').mkdir(exist_ok=True)
    (CASE/'constant/polyMesh').symlink_to(MESH_SRC, target_is_directory=True)
    save(RUN/'candidate-input-check.json',check_case_inputs(CASE, candidate=True))
    (CASE/'logFiles').mkdir()
    cut=bounded('native-decomposePar',['decomposePar','-constant'],CASE,600)
    shutil.copy2(cut,CASE/'logFiles/decomposePar.log')
    restore=bounded('native-restore0Dir',['bash','-ec','. "$WM_PROJECT_DIR/bin/tools/RunFunctions"; restore0Dir -processor'],CASE,120)
    shutil.copy2(restore,CASE/'logFiles/restore0Dir.log')
    # The validator writes its output file; run separately because its stdout is also evidence.
    bounded('native-cut-validator',['python3',KIT/'validate_cut.py','--case',CASE,'--output',RUN/'native-cut.json'],KIT,120)
    cut_validation=json.loads((RUN/'native-cut.json').read_text()); assert cut_validation['passed']
    (CASE/'logFiles/decomposePar.log').write_text(cut.read_text())
    candidate_graph=graph(CASE,'candidate-scotch-2x28-weight-1x0.1')
    native_total=re.search(r'^Number of processor faces = (\d+)',cut.read_text(),re.M)
    assert native_total and int(native_total[1])==candidate_graph['unique_interface_faces'], 'Candidate parser does not replay native face total'
    graph_result=compare(control_graph,candidate_graph)
    save(RUN/'interface-graph-review.json',graph_result)
    if not graph_result['promote_to_mandatory_initialization']:
        save(RUN/'terminal-screen.json',{'state':'GRAPH_FILTER_REJECTED_NO_READY_NO_INITIALIZATION','passed_native_cut':True,'solver_measurement':False,'gates':graph_result['triage_gates']})
        print('SCOTCH2X28_GRAPH_REJECTED_NO_INITIALIZATION')
        return
    # Do not start mandatory initialization unless all stages and sealing fit in the deadline.
    if int(DEADLINE-time.monotonic()) < 3*120 + 180 + 180 + 60:
        save(RUN/'terminal-screen.json',{'state':'GRAPH_PASS_BUT_NO_FULL_INITIALIZATION_WINDOW_NO_READY','passed_native_cut':True,'solver_measurement':False,'gates':graph_result['triage_gates']})
        print('SCOTCH2X28_GRAPH_PASS_INITIALIZATION_SKIPPED_NO_FULL_WINDOW')
        return
    # All mandatory numerical initialization stages run only after native graph gates pass.
    for stage,args in [('renumberMesh',['renumberMesh','-constant','-overwrite','-parallel']),
        ('potentialFoam',['potentialFoam','-initialiseUBCs','-parallel']),
        ('applyBoundaryLayer',['applyBoundaryLayer','-ybl','0.0450244','-parallel'])]:
        log=bounded('native-'+stage,['mpirun','--display-map','--report-bindings','-np','56','--',*args],CASE,120)
        text=log.read_text(errors='replace')
        actual=re.search(r'(?m)^Exec\s*:\s*(.+)$',text)
        assert actual and [Path(actual[1].split()[0]).name,*actual[1].split()[1:]]==args
        assert 'OPENFOAM=2512' in text and 'scalar=64' in text
        assert re.search(r'(?m)^nProcs\s*:\s*56\s*$',text) and re.search(r'(?m)^End\s*$',text)
        assert not FATAL.search(text) and not re.search(r'died from signal',text,re.I)
        shutil.copy2(log,CASE/'logFiles'/(stage+'.log'))
    save(RUN/'candidate-inputs-after-initialization.json',check_case_inputs(CASE,candidate=True))
    fields=field_snapshot(CASE); save(RUN/'initialized-fields.json',fields); assert fields['field_count']==336
    manifest_path=RUN/'accepted-initialized-manifest.json'
    bounded('accepted-manifest',['python3',KIT/'seal_tree.py','inventory',CASE,manifest_path],KIT,180)
    bounded('serial-mesh-after',['python3',KIT/'validate_cut.py','--mesh',MESH_SRC,'--expected',KIT/'expected-mesh.json','--mesh-only','--output',RUN/'mesh-after.json'],KIT,180)
    assert json.loads((RUN/'mesh-after.json').read_text())==mesh_result
    assert graph(CONTROL,'accepted-default-scotch')==control_graph, 'Read-only control changed'
    ready='N=56\nmethod=scotch\ndomains=(2 28)\ndomainWeights=(1 0.1)\nmesh=occDrivAer-65M\nstages=decomposePar restore0Dir renumberMesh potentialFoam applyBoundaryLayer\n'
    (CASE/'READY').write_text(ready)
    save(RUN/'completion.json',{'passed':True,'state':'MANDATORY_INITIALIZATION_COMPLETE_NOT_SOLVER_MEASURED',
        'candidate_root':str(CASE),'manifest_sha256':sha256(manifest_path),'graph_gates':graph_result['triage_gates'],
        'initialized_fields':336,'solver_measurement':None,'READY_sha256':hashlib.sha256(ready.encode()).hexdigest()})
    print('SCOTCH2X28_GRAPH_PASS_AND_INITIALIZATION_COMPLETE')

if __name__=='__main__': main()
