"""Derive full PD from sealed 222780 only after actual TP4 readiness review."""
from pathlib import Path
import ast,hashlib,json,re,shutil,subprocess,tarfile
O=Path(__file__).resolve().parent;R=O.parent;C=R/'eagle3-pd-bf16-20261021';P=R/'eagle3-prefill-graph-gate-20261021'
assert not (O/'SHA256SUMS').exists(),'Never overwrite a frozen derived bundle'
proof=json.loads((P/'REVIEW.json').read_text());assert proof['state']=='NATIVE_TP4_PREFILL_READINESS_PASS_FULL_PD_UNVERIFIED' and proof['semantic_gate_replayed'] and proof['all_four_nixl_ranks']
assert json.loads((P/'collection.json').read_text())['semantic_pass']
files=[line.split('  ',1)[1] for line in (C/'SHA256SUMS').read_text().splitlines()]
for name in files:
 if name!='prepare.py':shutil.copyfile(C/name,O/name)
for name in ['dtype-prerequisite.json','native-load-prerequisite.json','corpus-prerequisite.json','reference-prerequisite.json','asset-preflight-code.json','asset-contract.json','validate-candidate.py','collect-terminal.py','inspect-speculative-metadata.py']:
 shutil.copyfile(C/name,O/name)
(O/'prefill-prerequisite.json').write_text(json.dumps(proof,indent=2)+'\n');shutil.copyfile(P/'expected-source.json',O/'expected-source.json')
p=O/'worker.sh';text=p.read_text();needle='--weight-loader-prefetch-checkpoints --moe-runner-backend hpc_ops)';assert text.count(needle)==1;text=text.replace(needle,'--weight-loader-prefetch-checkpoints --moe-runner-backend hpc_ops --cuda-graph-backend-prefill disabled)');p.write_text(text)
assert text.replace(' --cuda-graph-backend-prefill disabled','')==(C/'worker.sh').read_text()
(O/'phase-budget.sh').write_text('''#!/usr/bin/env bash
# Bound pair initialization while retaining 360 seconds for client launch,
# locality capture, actual token checks and the separately reserved cleanup.
qwen_pair_timeout() {
  local deadline=$1 now=$2 remaining
  remaining=$((deadline-now-360))
  ((remaining>0)) || return 1
  ((remaining<=480)) || remaining=480
  printf '%s\\n' "$remaining"
}
''')
p=O/'topology-job.sh';text=p.read_text();text=text.replace('BUNDLE=$QWEN_BUNDLE','BUNDLE=$QWEN_BUNDLE\nsource "$BUNDLE/phase-budget.sh"\nRUN_DEADLINE=$(( $(date +%s)+1800-40 ))');text=text.replace('deadline=${2:-1650}','deadline=${2:-1200}')
needle='srun --overlap -N1 -n1 -w "${NODES[0]}" --gres=gpu:0 --cpus-per-task=4 \\\n  --container-image="$SGLANG" --container-mounts="$(mounts pair-warmup)"'
assert text.count(needle)==1
text=text.replace(needle,'''pair_remaining=$(qwen_pair_timeout "$RUN_DEADLINE" "$(date +%s)") || {
  echo 'FATAL: insufficient token-check reserve before pair warmup' >&2; exit 1;
}
timeout --signal=TERM --kill-after=10s "${pair_remaining}s" '''+needle)
text=text.replace('deadline=$(($(date +%s)+1800-SECONDS-40))','deadline=$RUN_DEADLINE');p.write_text(text)
p=O/'benchmark.pbs';text=p.read_text().replace(C.name,O.name);text=re.sub(r'^#PBS -N .*$', '#PBS -N ap42-eagle3-pd-eager',text,flags=re.M);p.write_text(text)
config=json.loads((O/'config.json').read_text());config.update(experiment=O.name,source_bundle=C.name,source_job='222780.pbs111',retry_of='222780.pbs111',retry_reason='Both prefills split automatic draft graph capture by rank; native uniform-disabled readiness probe 223005 passes',prefill_cuda_graph_backend='disabled',prefill_readiness_probe_job=proof['job'],worker_readiness_deadline_s=1200,pair_warmup_client_reserve_s=360,walltime_minutes=30,purpose='Full PD real-token correctness after native TP4 uniform eager-prefill readiness; decode and exact reference unchanged');(O/'config.json').write_text(json.dumps(config,indent=2)+'\n')
text=(C/'submit-pbs.py').read_text();text=text.replace("assert json.loads((O / 'validation.json').read_text())['passed']", "assert json.loads((O / 'validation.json').read_text())['passed']\nassert json.loads((O / 'prefill-prerequisite.json').read_text())['state']=='NATIVE_TP4_PREFILL_READINESS_PASS_FULL_PD_UNVERIFIED'")
start=text.index('    code = "import subprocess,json');end=text.index('    result = remote(',start)
text=text[:start]+'''    history_ids = list(dict.fromkeys(['222407.pbs111','222408.pbs111'] + [j['job_id'] for j in budget['jobs'] if not j.get('included_in_ledger_used')]))
    argv = [['qstat','-u','apacsc42'], ['qstat','-xf'] + history_ids, ['myprojects']]
    code = "import subprocess,json\\nrows=[]\\nfor args in " + repr(argv) + ":\\n r=subprocess.run(args,capture_output=True,text=True);rows.append(dict(argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))\\nprint(json.dumps(rows))\\n"
'''+text[end:]
text=re.sub(r"    assert set\(active\) <= .*?\n    dependency = .*?\n", "    assert not active, 'Only one isolated full GPU correctness allocation at a time'\n    dependency = ''\n",text)
needle='    proof = costs.reconcile(budget, text, now(), str(O / \'pre-submit.txt\'))'
assert text.count(needle)==1
text=text.replace(needle,'''    # Read only the other project's queue for the combined own-account cap;
    # never modify its jobs, ledger or authentication.
    cpu = subprocess.run(['bash',str(O.parent.parent/'hpc-experiments/tools/nscc-cpu-ssh.sh'),"bash -lc 'qstat -u apacsc42'"],capture_output=True,timeout=30)
    (O/'cpu-queue-readonly.txt').write_bytes(cpu.stdout)
    (O/'cpu-queue-readonly.stderr').write_bytes(cpu.stderr)
    assert cpu.returncode == 0, 'Combined own PBS count unavailable; do not authenticate or submit blindly'
    cpu_active = re.findall(r'^\\s*(\\d+\\.pbs\\d+)\\s+',cpu.stdout.decode(),re.M)
    assert len(active)+len(cpu_active)+1<=3, 'Combined own-account PBS cap'
'''+needle)
text=text.replace('Reserve one 16-H100/30-minute real EAGLE3 PD correctness gate; unranked, no budget increase.', 'Reserve one 16-H100/30-minute full native PD correctness repair after passing single-TP4 eager prefill; exact IDs retained, unranked, no budget increase.')
(O/'submit-pbs.py').write_text(text)
# Freeze exact source/control invariants; runtime source was verified by 223005.
for name in ['nixl-conn.py','token-control.py','check-token-result.py','token-client.sh','prepared-corpus.json','target-reference.json','placement.tsv','benchmark.sh']:
 assert (O/name).read_bytes()==(C/name).read_bytes(),name
for p in O.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in list(O.glob('*.sh'))+[O/'benchmark.pbs']:subprocess.run(['bash','-n',str(p)],check=True)
checks=[]
for now,wanted in [(0,480),(600,480),(1200,200),(1399,1),(1400,None)]:
 command='source "$1"; qwen_pair_timeout 1760 "$2"';r=subprocess.run(['bash','-c',command,'budget',str(O/'phase-budget.sh'),str(now)],capture_output=True,text=True)
 assert (r.returncode==0)==(wanted is not None)
 if wanted is not None:assert int(r.stdout)==wanted and now+wanted+360<=1760
 checks.append(dict(now_s=now,pair_timeout_s=wanted,passed=True))
(O/'deadline-validation.json').write_text(json.dumps(dict(passed=True,cases=checks,scope='Actual shell budget function; no GPU execution'),indent=2)+'\n')
files=list(dict.fromkeys(files+['phase-budget.sh','prefill-prerequisite.json','expected-source.json']))
(O/'SHA256SUMS').write_text(''.join(hashlib.sha256((O/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in files))
subprocess.run(['python3',str(O/'validate-candidate.py')],check=True)
with tarfile.open(O/'payload.tar.gz','w:gz') as tar:
 for name in files+['SHA256SUMS']:tar.add(O/name,arcname=O.name+'/'+name)
(O/'validation.json').write_text(json.dumps(dict(passed=True,source_job='222780.pbs111',prefill_readiness_probe='223005.pbs111',numerical_runtime_change='Uniform native prefill graph disable on prefill roles only',orchestration_change='Absolute startup budget retains client/locality/cleanup window',unchanged_control_files=8,deadline_fixtures=5,semantic_fixtures=9,requested_gpus=16,minutes=30,max_su=1024,scored_benchmark=False),indent=2)+'\n')
print('Frozen full PD eager-prefill correctness repair, not submitted')
