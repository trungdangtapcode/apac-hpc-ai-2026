#!/usr/bin/env python3
"""Freeze and independently review the bounded N48 mapping payload."""
from pathlib import Path
import hashlib,json,subprocess,sys
E=Path(__file__).resolve().parent
PARENT=E.parent
R2=PARENT/'iris-best-recipes40-r2-20261106'
QUAL=PARENT/'iris-rank-probe-files-qualify-20261106/completed-2294996/REVIEW.json'
PAYLOAD=[E/n for n in ('job.sbatch','run.py','prepare_arm.py','helpers.py','native_checks.py','native_output.py','source_checks.py','sampler.py','seal_tree.py','probe_writer.py','read_rank_proofs.py','validate_arm_proofs.py','placement.py','accepted-source-manifest-48.json','supplementary-source-manifest-48.json','source-pins-48.json')]
PAYLOAD += sorted(p for p in (E/'payload-case-48').rglob('*') if p.is_file())
assert len(PAYLOAD)==len(set(PAYLOAD)) and all(p.is_file() and not p.is_symlink() for p in PAYLOAD)
files={str(p.relative_to(E)):hashlib.sha256(p.read_bytes()).hexdigest() for p in PAYLOAD}
q=json.loads(QUAL.read_text());assert q['passed'] and q['all_four_file_probes_passed']
assert files['probe_writer.py']==q['protocol_sha256']['probe_writer.py'] and files['read_rank_proofs.py']==q['protocol_sha256']['read_rank_proofs.py']
r2=json.loads((R2/'completed-2294997/REVIEW.json').read_text())
assert r2['measurement_valid'] and r2['complete_six_arm_matrix'] and r2['rank_proofs_all_passed']
assert r2['runtime_identity_stable'] and r2['source_after_validations']['48'] is True
assert r2['payload_before_return_code']==0 and r2['payload_after_return_code']==0
manifest=json.loads((E/'accepted-source-manifest-48.json').read_text())
supplementary=json.loads((E/'supplementary-source-manifest-48.json').read_text())
pins=json.loads((E/'source-pins-48.json').read_text())['files']
assert manifest['files'] and supplementary['files'] and len(pins)==41
assert supplementary['source']=='/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch48-cut-20261105T073707Z/artifacts/cut-N48-scotch'
assert files['accepted-source-manifest-48.json'] and files['supplementary-source-manifest-48.json']
runner=(E/'run.py').read_text()
for token in ("('B1-balanced48',48,'balanced48'),('A1-default48',48,'default48')", "('A2-default48',48,'default48'),('B2-balanced48',48,'balanced48')", "'solver_steps':40,'timed_intervals':39", "'request_maximum_allocated_CPU_hours':140", "'file_handler':'OpenFOAM default uncollated for both; FOAM_FILEHANDLER must be unset.'"):
 assert token in runner,token
assert 'for ranks in (40,48)' not in runner
script=(E/'job.sbatch').read_text().splitlines()
for line in ('#SBATCH --partition=iris','#SBATCH --account=rdmaworkshop','#SBATCH --qos=low','#SBATCH --exclusive','#SBATCH --mem=0','#SBATCH --gpus=0','#SBATCH --nodes=1','#SBATCH --nodelist=iris001','#SBATCH --ntasks=56','#SBATCH --time=02:30:00'):
 assert script.count(line)==1,line
subprocess.run(['bash','-n',str(E/'job.sbatch')],check=True)
subprocess.run([sys.executable,str(E/'offline_checks.py')],check=True)
subprocess.run([sys.executable,'-m','py_compile',*[str(E/n) for n in ('root_review.py','run.py','prepare_arm.py','source_checks.py','validate_arm_proofs.py')]],check=True)
(E/'payload-sha256.json').write_text(json.dumps({'files':files},indent=2,sort_keys=True)+'\n')
(E/'payload-sha256.txt').write_text(''.join(v+'  '+k+'\n' for k,v in sorted(files.items())))
review={'passed':True,'payload_sha256':files,'payload_file_count':len(files),'source_rank_count':48,
 'accepted_source_manifest_sha256':hashlib.sha256((E/'accepted-source-manifest-48.json').read_bytes()).hexdigest(),
 'accepted_source_path':supplementary['source'],'reference_complete_native_review_job_id':'2294997',
 'reference_review_sha256':hashlib.sha256((R2/'completed-2294997/REVIEW.json').read_bytes()).hexdigest(),
 'qualified_rank_proof_protocol_job_id':'2294996','qualified_rank_proof_protocol_sha256':q['protocol_sha256'],
 'hypothesis':'With N48 initialized source, 24/24 socket/core MPI mapping versus default mapping changes native seconds per step.',
 'matrix':['B1-balanced48','A1-default48','A2-default48','B2-balanced48'],'steps_per_arm':40,'timed_intervals_per_arm':39,
 'single_factor':'MPI mapping only; same accepted N48 source, physics, fixed iterations, runtime, rank count, node and uncollated I/O.',
 'placement_gate':'Actual 48-rank socket/core probe must verify 24/24 masks across observed NUMA CPU sets before any solver; each candidate preparation revalidates its own 48-rank proofs.',
 'resource_envelope':{'nodes':1,'cpus':56,'gpus':0,'partition':'iris','nodelist':'iris001','wall_seconds':9000,'wrapper_seconds':8940,'internal_seconds':8800,'max_allocated_CPU_hours':140,'solver_cap_seconds_per_arm':1800,'prep_cap_seconds_per_arm':180,'finalize_reserve_seconds':480},
 'worst_case_internal_window_seconds':8400,'offline_checks_passed':True,'scheduler_admission':'NOT_PERFORMED','deployment':'NOT_PERFORMED',
 'limits':['Offline launcher fixture checks the CLI contract, not MPI hardware placement.','Pre-MPI affinity does not prove solver helper binding, NUMA page residency, or causal bandwidth improvement.','Single-allocation 40-step microbenchmark; not official workload score or stable general speedup.']}
(E/'ROOT_REVIEW.json').write_text(json.dumps(review,indent=2,sort_keys=True)+'\n')
print(json.dumps({'passed':True,'payload_file_count':len(files),'offline_checks':'PASS','scheduler_admission':'NOT_PERFORMED'}))
