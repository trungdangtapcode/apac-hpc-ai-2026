#!/usr/bin/env python3
"""Freeze and root-review the N40/N48 native ABBA comparison payload."""
from pathlib import Path
import hashlib,json,subprocess,sys
E=Path(__file__).resolve().parent
H=E.parents[2]
INIT=E.parent/'iris-scotch40-init-20261106'
R2=E.parent/'iris-best-recipes40-r2-20261106'
QUAL=E.parent/'iris-rank-probe-files-qualify-20261106/completed-2294996/REVIEW.json'
INIT_REVIEW=INIT/'completed-2294998/REVIEW.json'
PAYLOAD=[E/'job.sbatch',E/'run.py',E/'prepare_arm.py',E/'helpers.py',E/'native_checks.py',E/'native_output.py',E/'source_checks.py',E/'sampler.py',E/'seal_tree.py',E/'probe_writer.py',E/'read_rank_proofs.py',E/'validate_arm_proofs.py',E/'placement.py']
PAYLOAD += [E/n for n in ('accepted-source-manifest-40.json','supplementary-source-manifest-40.json','accepted-source-manifest-48.json','supplementary-source-manifest-48.json','source-pins-40.json','source-pins-48.json')]
PAYLOAD += sorted(p for d in (E/'payload-case-40',E/'payload-case-48') for p in d.rglob('*') if p.is_file())
assert len(PAYLOAD)==len(set(PAYLOAD))
assert all(p.is_file() and not p.is_symlink() for p in PAYLOAD)
files={str(p.relative_to(E)):hashlib.sha256(p.read_bytes()).hexdigest() for p in PAYLOAD}
init=json.loads(INIT_REVIEW.read_text());assert init['passed'] and init['job_id']=='2294998' and init['terminal_state']=='COMPLETED'
assert init['rank_count']==40 and init['ready_marker'].startswith('N=40\nmethod=scotch\n')
assert init['native_stage_review']['passed'] and init['rank_file_proofs']['passed'] and init['rank_file_proofs']['count']==40
assert init['source_before_after_identical'] and init['case_source_pins']==41
assert init['cut_review']['passed'] and init['cut_review']['mesh_cells']==65334765
q=json.loads(QUAL.read_text());assert q['passed'] and q['all_four_file_probes_passed']
assert files['probe_writer.py']==q['protocol_sha256']['probe_writer.py']
assert files['read_rank_proofs.py']==q['protocol_sha256']['read_rank_proofs.py']
r2=json.loads((R2/'completed-2294997/REVIEW.json').read_text())
assert r2['measurement_valid'] and r2['complete_six_arm_matrix'] and r2['rank_proofs_all_passed']
assert r2['runtime_identity_stable'] and r2['source_after_validations']=={'48':True,'56':True}
assert r2['payload_before_return_code']==0 and r2['payload_after_return_code']==0
assert r2['recipe_means']['io48']['mean_seconds_per_step']>0
pins40=json.loads((E/'source-pins-40.json').read_text())['files'];pins48=json.loads((E/'source-pins-48.json').read_text())['files']
assert set(pins40)==set(pins48) and [n for n in pins40 if pins40[n]!=pins48[n]]==['system/include/caseDefinition']
assert json.loads((E/'accepted-source-manifest-40.json').read_text())['files']
assert json.loads((E/'supplementary-source-manifest-40.json').read_text())['source']=='/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch40-cut-20261105T162039Z/artifacts/cut-N40-scotch'
script=(E/'job.sbatch').read_text().splitlines()
for line in ('#SBATCH --job-name=tu-iris-b40v48','#SBATCH --partition=iris','#SBATCH --account=rdmaworkshop','#SBATCH --qos=low','#SBATCH --exclusive','#SBATCH --mem=0','#SBATCH --gpus=0','#SBATCH --nodes=1','#SBATCH --nodelist=iris001','#SBATCH --ntasks=56','#SBATCH --time=03:00:00'):
    assert script.count(line)==1,line
for name in ('A1-control48','B1-candidate40','B2-candidate40','A2-control48'):assert name in (E/'run.py').read_text()
subprocess.run(['bash','-n',str(E/'job.sbatch')],check=True)
subprocess.run([sys.executable,str(E/'offline_checks.py')],check=True)
subprocess.run([sys.executable,'-m','py_compile',*[str(E/n) for n in ('root_review.py','deploy_submit.py','run.py','prepare_arm.py','source_checks.py','validate_arm_proofs.py')]],check=True)
(E/'payload-sha256.json').write_text(json.dumps({'files':files},indent=2,sort_keys=True)+'\n')
(E/'payload-sha256.txt').write_text(''.join(v+'  '+k+'\n' for k,v in sorted(files.items())))
review={'passed':True,'payload_sha256':files,'payload_file_count':len(files),
 'initialization_job_id':'2294998','initialization_review_sha256':hashlib.sha256(INIT_REVIEW.read_bytes()).hexdigest(),
 'accepted_n40_rank_count':40,'accepted_n40_mesh_cells':65334765,
 'qualified_file_proof_job_id':'2294996','qualified_file_proof_protocol_sha256':q['protocol_sha256'],
 'accepted_n48_parent':'iris-best-recipes40-r2-20261106','accepted_n48_manifest_sha256':hashlib.sha256((R2/'accepted-source-manifest-48.json').read_bytes()).hexdigest(),
 'case_input_comparison':{'passed':True,'differing_pinned_file':'system/include/caseDefinition','all_other_pinned_physics_inputs_identical':True},
 'native_comparison':'balanced40 vs default48, partition and placement differ, uncollated I/O fixed, ABBA forty steps/39 intervals',
 'offline_checks_passed':True,'scheduler_admission':'NOT_PERFORMED','deployment':'NOT_PERFORMED',
 'checks':['2294998 terminal native initialization review passed; exact N40 READY and 40 proof files','2294996 strict file proof writer/reader byte hashes match qualification','N40 and N48 case pins differ only by exact rank-dependent caseDefinition','offline exact-profile/config/source/proof rejection checks passed','exclusive 56 CPU,0 GPU,iris001,3h envelope verified','no cross-decomposition bitwise force equality is imposed']}
(E/'ROOT_REVIEW.json').write_text(json.dumps(review,indent=2,sort_keys=True)+'\n')
print(json.dumps({'passed':True,'payload_file_count':len(files),'protocol_hashes':q['protocol_sha256'],'offline_checks':'PASS'}))
