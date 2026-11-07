from pathlib import Path
import json,hashlib,statistics,sys
E=Path(__file__).resolve().parent.parent;O=E/'completed-2295090';C=O/'collected';R=C/'runs/2295090';d=json.loads((O/'collection.json').read_text());sys.path.insert(0,str(E));from native_output import review_native_output
from read_rank_proofs import validate_proof_dir
from run import compare_same_partition
for n,v in d['files'].items():
 b=(C/n).read_bytes();assert len(b)==v['bytes'] and hashlib.sha256(b).hexdigest()==v['sha256']
frozen=json.loads((E/'ROOT_REVIEW.json').read_text())['payload_sha256'];assert len(frozen)==57 and all(hashlib.sha256((E/n).read_bytes()).hexdigest()==v for n,v in frozen.items())
comp=json.loads((R/'comparison.json').read_text());assert comp['passed'] and comp['complete_four_arm_comparison'];means={};forces={};proofs={}
for a in comp['arms']:
 label=a['arm'];log,t,ff,it=review_native_output(R/'arms'/label,48);assert len(t)==39 and len(ff)==40 and statistics.mean(t)==a['mean_s_step'];means[label]=statistics.mean(t);forces[label]=ff;proofs[label]=validate_proof_dir(R/'arms'/label/'rank-probe-proofs',48);assert proofs[label]['proofs']==json.loads((R/'arms'/label/'rank-proofs.json').read_text())['proofs'];assert json.loads((R/'arms'/label/'postsolve-fields.json').read_text())==json.loads((R/'source-fields-48.json').read_text())
validate_proof_dir(R/'probes/balanced48',48)
checks={}
for left,right in [('B1-balanced48','B2-balanced48'),('A1-default48','A2-default48'),('B1-balanced48','A1-default48'),('B2-balanced48','A2-default48')]:
 check=compare_same_partition(forces[left],forces[right]);assert check['passed'];checks[left+'_vs_'+right]=check
m=lambda label:{r['rank']:r['affinity_cpu_ids'] for r in proofs[label]['proofs']}
report={'passed':True,'raw_hashes_verified':len(d['files']),'local_payload_hashes_verified':57,'strict_rank_sets':5,'strict_rank_records':240,'native_means_s_step':means,'zero_time_fields_equal_source':True,'same_source_force_checks':checks,'balanced_repeat_exact_CPU_map_equal':m('B1-balanced48')==m('B2-balanced48'),'default_repeat_exact_CPU_map_equal':m('A1-default48')==m('A2-default48'),'final_comparison_passed':True,'limits':'Root replay of native/hash/proof/field/force data; full source/runtime/telemetry checks in REVIEW.json'};(O/'ROOT_REPLAY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
