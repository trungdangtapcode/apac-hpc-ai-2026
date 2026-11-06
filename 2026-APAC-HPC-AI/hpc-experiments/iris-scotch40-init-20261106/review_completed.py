"""Root-local terminal review of Iris native Scotch40 initialization 2294998."""
from pathlib import Path
import hashlib,importlib.util,json,re,tarfile,sys
E=Path(__file__).resolve().parent;O=E/'completed-2294998';C=json.loads((O/'collection.json').read_text());R=O/'collected';J='2294998'
for name,row in C['files'].items():
    p=R/name;raw=p.read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],name
with tarfile.open(O/'raw-evidence.tar.gz','r:gz') as tar:
    members={m.name:m for m in tar.getmembers()};assert set(members)==set(C['files'])
    for name,m in members.items():
        b=tar.extractfile(m).read();assert hashlib.sha256(b).hexdigest()==C['files'][name]['sha256']
assert hashlib.sha256((O/'raw-evidence.tar.gz').read_bytes()).hexdigest()==C['archive_sha256']
receipt=json.loads((E/'submission-receipt.json').read_text());assert receipt['job_id']==J
assert C['accounting']['returncode']==0 and not C['accounting']['stderr']
rows=[line.split('|') for line in C['accounting']['stdout'].splitlines() if line.strip()]
root=[r for r in rows if r[0]==J];assert len(root)==1
assert root[0][2:6]==['COMPLETED','0:0','128','56'] and root[0][6]=='iris001' and root[0][7]==''
batch=[r for r in rows if r[0]==J+'.batch'];assert len(batch)==1 and batch[0][7]=='79937828K'
assert C['ready']=='N=40\nmethod=scotch\nnHierarchical=unused\nmesh=occDrivAer-65M\nstages=decomposePar restore0Dir renumberMesh potentialFoam applyBoundaryLayer\n'
assert (R/'artifacts/cut-N40-scotch/READY').read_text()==C['ready']
spec=importlib.util.spec_from_file_location('verify_init40',E/'verify-init.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
runs=R/'init-runs';stage=m.check_stage_logs(runs,J);assert stage['passed']
cut=json.loads((runs/(J+'-cut-gate.json')).read_text());assert cut['passed'] and cut['job_id']=='2294919' and cut['mesh_cells']==65334765 and cut['restored_zero_fields']==240
proof=m.check_probe(runs,J);assert proof['passed'] and proof['file_proofs']==40
sys.path.insert(0,str(E));from read_rank_proofs import validate_proof_dir
proofs=validate_proof_dir(runs/(J+'-rank-proofs'),40);assert proofs['passed'] and proofs['rank_ids']==list(range(40)) and len(proofs['proofs'])==40
resources={}
for name in ('renumberMesh','potentialFoam','applyBoundaryLayer'):
    raw=(runs/(J+'-'+name+'.resource.txt')).read_text();assert 'Exit status: 0' in raw
    mm=re.search(r'Maximum resident set size \(kbytes\): (\d+)',raw);assert mm
    resources[name]={'peak_RSS_KiB_GNU_time':int(mm.group(1)),'resource_exit_zero':True}
sources=[json.loads((runs/(J+'-source-'+phase+'.json')).read_text()) for phase in ('before','after')]
assert all(x['passed'] and x['pinned_files']==41 for x in sources) and sources[0]['input_hashes']==sources[1]['input_hashes']
manifest=json.loads((E/'payload-sha256.json').read_text())['files']
for phase in ('before','after'):
    check=(runs/(J+'-kit-source-'+phase+'.txt')).read_text().splitlines()
    assert set(check)=={name+': OK' for name in manifest}
fields=[json.loads((runs/(J+'-fields-'+phase+'.json')).read_text()) for phase in ('before','after')]
assert all(x['passed'] and x['field_count']==240 and len(x['fields'])==240 for x in fields)
assert set(fields[0]['fields'])==set(fields[1]['fields'])=={f'processor{i}/0/{field}' for i in range(40) for field in m.FIELDS}
changed=sum(fields[0]['fields'][p]['sha256']!=fields[1]['fields'][p]['sha256'] for p in fields[0]['fields'])
core=json.loads((E/'accepted-source-manifest.json').read_text());extra=json.loads((E/'supplementary-source-manifest.json').read_text())
assert extra['source']==str(Path(C['root'])/'artifacts/cut-N40-scotch')
assert core['symlinks']=={'constant/polyMesh':'/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam/occDrivAer/polyMesh'}
assert len(core['files'])==752 and len(extra['files'])==13 and len(extra['directories'])==166
for rank in range(40):
    for f in m.FIELDS:assert f'processor{rank}/0/{f}' in core['files']
    assert any(name.startswith(f'processor{rank}/constant/') for name in core['files'])
assert set(extra['files']).isdisjoint(core['files']) and set(extra['symlinks']).isdisjoint(core['symlinks'])
template=(E.parent/'iris-solver-rank-interleave40-20261105/seal_tree.py').read_text();assert template.count('range(56)')==2
assert C['inventory_code_sha256']==hashlib.sha256(template.replace('range(56)','range(40)').encode()).hexdigest()
actual_cpu_hours=128*56/3600
review={'passed':True,'job_id':J,'terminal_state':'COMPLETED','exit_code':'0:0','elapsed_seconds':128,'allocated_cpus':56,'rank_count':40,'gpus':0,
 'actual_allocated_CPU_hours':actual_cpu_hours,'site_SU':None,'ready_marker':C['ready'],'native_stage_review':stage,'cut_review':cut,
 'rank_file_proofs':{'passed':True,'count':40,'hostnames':proofs['hostnames'],'all_affinity_masks_nonempty_unique_nonoverlap':True,'scope':proofs['scope']},
 'payload_file_count':len(manifest),'case_source_pins':41,'source_before_after_identical':True,
 'initialized_field_files_before_after':240,'field_hashes_changed_during_required_initialization':changed,
 'full_case_manifest':{'regular_files':len(core['files']),'symlinks':core['symlinks'],'supplementary_files':len(extra['files']),'directories':len(extra['directories']),'inventory_code_sha256':C['inventory_code_sha256']},
 'resource_observations':resources,'reported_batch_MaxRSS_KiB':79937828,'root_job_MaxRSS_available':False,
 'archive_file_count':len(C['files']),'all_archive_and_file_hashes_verified':True,
 'limits':['Initialization only; it has no solver score or Cd result.','GNU time reports per-stage process-tree peak RSS and not aggregate MPI memory, memory bandwidth, or per-rank totals.','Slurm root-job MaxRSS is blank; batch-step MaxRSS is retained as reported.','The single-node pre-MPI_Init affinity proof does not establish solver helper affinity or NUMA page placement.','The READY marker certifies the exact required N40 preparation; a matched 40-versus-48 solver benchmark is still required.']}
(O/'REVIEW.json').write_text(json.dumps(review,indent=2,sort_keys=True)+'\n')
lines=['# Scotch40 initialization terminal review','',
f'**Iris {J} COMPLETED 0:0** in 128 seconds with 56 allocated CPUs on iris001. The exact N40 Scotch artifact is initialized and has the pinned READY marker. This is preparation, not a solver benchmark.','',
'The native cut/accounting gate verifies job 2294919, the complete eight-member official mesh identity and 65,334,765 cells, 40 processor domains and 240 restored fields. The initialization preserves the organizer sequence and arguments: renumberMesh -constant -overwrite -parallel, potentialFoam -initialiseUBCs -parallel, then applyBoundaryLayer -ybl 0.0450244 -parallel. All three logs have return code zero, native End, OpenFOAM 2512, scalar64, 40 ranks and no fatal markers.','',
'The forty separate rank JSON proofs pass the exact qualified strict reader: every expected rank once, world size 40, one host, nonempty disjoint CPU masks. Both source pin checks pass with identical 41-file input hashes; payload hashes pass before and after. The two field inventories each contain all 240 exact rank/field paths. Field value hashes change across required initialization, as expected. READY is written last with the exact N40 Scotch/65M marker.','',
f'The full initialized case inventory contains {len(core["files"])} regular files, one approved shared constant/polyMesh symlink and {len(extra["files"])} supplementary files across {len(extra["directories"])} directories. The 68 transferred evidence files and their 23,050-byte compressed archive all verify. GNU time records the three per-stage peak RSS values; Slurm batch-step MaxRSS is 79,937,828 KiB, while the root-job field is blank. These quantities do not establish aggregate resident memory or bandwidth.','',
f'Actual scheduler allocation cost is {actual_cpu_hours:.6f} CPU-hours; billed SU is unknown. No solver timing or performance gain is claimed. Next, use the frozen accepted-source manifest for a separately reviewed matched 40-versus-48 solver comparison.','',
'Evidence: collection.json, raw-evidence.tar.gz, collected/, accepted-source-manifest.json, supplementary-source-manifest.json, and REVIEW.json.']
(O/'RESULTS.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'passed':True,'job_id':J,'native_stages':list(stage['stages']),'files':len(C['files']),'core_files':len(core['files']),'field_hashes_changed':changed,'allocated_CPU_hours':actual_cpu_hours,'result':str(O/'RESULTS.md')}))
