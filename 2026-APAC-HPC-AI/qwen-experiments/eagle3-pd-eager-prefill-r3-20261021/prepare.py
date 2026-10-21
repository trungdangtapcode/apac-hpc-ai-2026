"""Derive a frozen shell-dispatch repair from reviewed 223053; no inference changes."""
from pathlib import Path
import hashlib,json,shutil,subprocess,tarfile
O=Path(__file__).resolve().parent; C=O.parent/'eagle3-pd-eager-prefill-r2-20261021'
assert not (O/'SHA256SUMS').exists(),'Never overwrite a frozen payload'
proof=json.loads((C/'REVIEW.json').read_text());assert proof['state']=='ALL_ROLES_READY_WARMUP_LAUNCHER_FAILED' and proof['exit_status']==127 and proof['payload_and_raw_hashes_verified']
files=[line.split('  ',1)[1] for line in (C/'SHA256SUMS').read_text().splitlines()]
for name in files:
 if name!='prepare.py':shutil.copyfile(C/name,O/name)
for name in ['dtype-prerequisite.json','native-load-prerequisite.json','corpus-prerequisite.json','reference-prerequisite.json','asset-preflight-code.json','asset-contract.json','validate-candidate.py','collect-terminal.py','inspect-speculative-metadata.py','submit-pbs.py']:
 shutil.copyfile(C/name,O/name)
(O/'launcher-prerequisite.json').write_text(json.dumps(proof,indent=2)+'\n')
p=O/'topology-job.sh';t=p.read_text();old='"${pair_remaining}s" srun --overlap';new='"${pair_remaining}s" bash -c \'srun "$@"\' qwen-pair-warmup --overlap';assert t.count(old)==1;t=t.replace(old,new);p.write_text(t)
assert t.replace(new,old)==(C/'topology-job.sh').read_text()
p=O/'benchmark.pbs';t=p.read_text().replace(C.name,O.name).replace('ap42-eagle3-pd-egr2','ap42-eagle3-pd-egr3');p.write_text(t)
c=json.loads((O/'config.json').read_text());c.update(experiment=O.name,source_bundle=C.name,source_job=proof['job'],retry_of=proof['job'],retry_reason='All roles/router ready; outer timeout cannot exec exported srun function; invoke child Bash while preserving timeout/argv and native inference',warmup_dispatch='timeout -> bash -c exported srun -> pbsdsh',purpose='Full-PD exact actual-token gate after CPU-validated Bash timeout dispatch repair');(O/'config.json').write_text(json.dumps(c,indent=2)+'\n')
p=O/'submit-pbs.py';t=p.read_text();t=t.replace("assert json.loads((O / 'validation.json').read_text())['passed']", "assert json.loads((O / 'validation.json').read_text())['passed']\nassert json.loads((O / 'launcher-validation.json').read_text())['passed']\nassert json.loads((O / 'launcher-prerequisite.json').read_text())['state']=='ALL_ROLES_READY_WARMUP_LAUNCHER_FAILED'")
t=t.replace("as_of=re.search(r'balance as of (\\S+)', text).group(1))", "as_of=re.search(r'balance as of (\\S+)', text).group(1),\n                            freshness_note='Fresh own GPU queue and published ledger before this receipt; uniquely posted prior charges reconciled, otherwise prior maxima retained. No HPC CPU query.')")
t=t.replace('Reserve one 16-H100/30-minute full native PD correctness repair after passing single-TP4 eager prefill; exact IDs retained, unranked, no budget increase.','Reserve one 16-H100/30-minute shell-dispatch correctness repair after all-role readiness; exact IDs/deadlines retained, unranked, no budget increase.');p.write_text(t)
for name in ['worker.sh','pbs-shim.sh','pbs-container.sh','pbs-exec.py','phase-budget.sh','nixl-conn.py','token-control.py','token-client.sh','check-token-result.py','prepared-corpus.json','target-reference.json','placement.tsv','benchmark.sh']:
 assert (O/name).read_bytes()==(C/name).read_bytes(),name
subprocess.run(['python3',str(O/'test-launcher.py')],check=True)
files=list(dict.fromkeys(files+['launcher-prerequisite.json','test-launcher.py']))
(O/'SHA256SUMS').write_text(''.join(hashlib.sha256((O/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in files))
subprocess.run(['python3',str(O/'validate-candidate.py')],check=True)
with tarfile.open(O/'payload.tar.gz','w:gz') as tar:
 for name in files+['SHA256SUMS']:tar.add(O/name,arcname=O.name+'/'+name)
(O/'validation.json').write_text(json.dumps(dict(passed=True,source_job=proof['job'],numerical_changes=0,orchestration_change='Invoke exported srun via child Bash inside same timeout',unchanged_control_files=13,semantic_fixtures=9,launcher_fixtures=6,requested_gpus=16,minutes=30,max_su=1024,scored_benchmark=False),indent=2)+'\n')
print('Frozen R3, not submitted; native inference and exact token gates unchanged')
