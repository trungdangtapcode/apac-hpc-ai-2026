from pathlib import Path
import json,hashlib,sys,statistics
E=Path(__file__).resolve().parent.parent;O=E/'completed-2295087';C=O/'collected';run=C/'runs/2295087';d=json.loads((O/'collection.json').read_text());sys.path.insert(0,str(E));from native_output import review_native_output
for n,m in d['files'].items():
 raw=(C/n).read_bytes();assert len(raw)==m['bytes'] and hashlib.sha256(raw).hexdigest()==m['sha256']
comp=json.loads((run/'comparison.json').read_text());assert comp['passed'] and comp['complete_four_arm_comparison'];rows=[]
for a in comp['arms']:
 log,t,forces,it=review_native_output(run/'arms'/a['arm'],a['rank_count']);assert len(t)==39 and len(forces)==40 and statistics.mean(t)==a['mean_s_step'];rows.append({'arm':a['arm'],'rank_count':a['rank_count'],'mean_s_step':statistics.mean(t),'steps':40,'intervals':39})
proofs={a:json.loads((run/'arms'/a/'rank-proofs.json').read_text()) for a in ('B1-candidate40','B2-candidate40')};maps={a:{x['rank']:x['affinity_cpu_ids'] for x in p['proofs']} for a,p in proofs.items()};same=maps['B1-candidate40']==maps['B2-candidate40'];r={'passed':True,'root_verified_files':len(d['files']),'native_arms_replayed':rows,'candidate_exact_rank_to_CPU_masks_repeat_equal':same,'comparison_passed':True,'scope':'Root independent transferred hashes/native output and candidate CPU-map comparison; full acceptance and limits in terminal REVIEW'};from read_rank_proofs import validate_proof_dir
from run import compare_same_partition
strict={}
for row in rows:
 label=row['arm'];strict[label]=validate_proof_dir(run/'arms'/label/'rank-probe-proofs',row['rank_count'])
 assert strict[label]['proofs']==json.loads((run/'arms'/label/'rank-proofs.json').read_text())['proofs']
 assert json.loads((run/'arms'/label/'postsolve-fields.json').read_text())==json.loads((run/('source-fields-%d.json'%row['rank_count'])).read_text())
strict['preflight']=validate_proof_dir(run/'probes/balanced40',40)
force_checks={}
for name,left,right in (('candidate40','B1-candidate40','B2-candidate40'),('control48','A1-control48','A2-control48')):
 forces=[]
 for label in (left,right):
  rank=40 if 'candidate' in label else 48
  forces.append(review_native_output(run/'arms'/label,rank)[2])
 force_checks[name]=compare_same_partition(*forces);assert force_checks[name]['passed']
for name,v in json.loads((E/'ROOT_REVIEW.json').read_text())['payload_sha256'].items():assert hashlib.sha256((E/name).read_bytes()).hexdigest()==v
r.update(strict_rank_file_sets=len(strict),strict_actual_rank_files=sum(x['rank_count'] for x in strict.values()),same_partition_force_checks=force_checks,postsolve_zero_time_fields_equal_source=True,local_frozen_payload_hashes_verified=101)
(O/'ROOT_REPLAY.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
