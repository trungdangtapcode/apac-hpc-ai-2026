"""CPU-only regression fixtures execute the actual warmup block and PBS shim."""
from pathlib import Path
import json,os,shlex,shutil,subprocess,tempfile,time
O=Path(__file__).resolve().parent;top=(O/'topology-job.sh').read_text();start=top.index('timeout --signal=TERM --kill-after=10s "${pair_remaining}s"');end=top.index('echo "ALL_PAIRS_WARM',start);block=top[start:end]
assert 'bash -c \'srun "$@"\' qwen-pair-warmup' in block
results=[]
with tempfile.TemporaryDirectory(prefix='eagle3 launcher ') as temporary:
 T=Path(temporary);nodefile=T/'nodes';nodefile.write_text('mock-node0\nmock-node1\n');art=T/'art';art.mkdir();binpath=T/'bin';binpath.mkdir()
 for command in ['timeout','bash','python3','awk','sleep']:(binpath/command).symlink_to(shutil.which(command))
 env=os.environ.copy();env.update(PBS_NODEFILE=str(nodefile),PBS_JOBID='cpu-fixture',QWEN_BUNDLE=str(O),SLURM_SUBMIT_DIR=str(T),APAC_PBS_DRY_RUN='1',PATH=str(binpath))
 prefix='set -euo pipefail\nsource '+shlex.quote(str(O/'pbs-shim.sh'))+'\nNODES=(mock-node0 mock-node1)\nSGLANG="fake image"\nBUNDLE='+shlex.quote(str(O))+'\nART='+shlex.quote(str(art))+'\npair_remaining=3\nIPS=(127.0.0.1)\nmounts() { printf "%s" "path with spaces:target"; }\n'
 def run(code,extra=None):return subprocess.run(['bash','-c',prefix+code],env={**env,**(extra or {})},capture_output=True,text=True,timeout=15)
 r=run('timeout 1s srun --overlap\n');assert r.returncode==127 and "failed to run command" in r.stderr;results.append(dict(case='old_external_timeout_reproduces_127',passed=True))
 r=run("timeout 1s bash -c 'declare -F srun >/dev/null'\n");assert r.returncode==0;results.append(dict(case='child_bash_imports_actual_exported_shim',passed=True))
 r=run(block+'echo ALL_PAIRS_WARM\n');assert r.returncode==0 and 'ALL_PAIRS_WARM' in r.stdout
 value=json.loads((art/'pair-warmup.log').read_text());assert value['node']==0 and value['gpu_indices']==[] and value['cpus']==4
 assert value['command']==['env','QWEN_PAIR_TIMEOUT=360','QWEN_PAIR_PARALLELISM=8','python3',str(O/'warm-topology.py'),'127.0.0.1',str(art)],value
 results.append(dict(case='actual_block_shim_dryrun_preserves_argv_and_spaces',passed=True))
 mock=binpath/'pbsdsh';mock.write_text('''#!/usr/bin/env bash
set -eu
if [[ ${QWEN_MOCK_MODE:-exit} == sleep ]]; then
  sleep 30 & child=$!
  printf '%s' "$child" > "$QWEN_MOCK_PIDFILE"
  trap 'kill "$child" 2>/dev/null || :; wait "$child" 2>/dev/null || :; printf terminated > "$QWEN_MOCK_TERMFILE"; exit 143' TERM
  wait "$child"
else
  exit "${QWEN_MOCK_STATUS:-0}"
fi
''');mock.chmod(0o755)
 for status in [0,23]:
  r=run(block+'echo ALL_PAIRS_WARM\n',dict(APAC_PBS_DRY_RUN='0',QWEN_MOCK_STATUS=str(status)));assert r.returncode==status and ('ALL_PAIRS_WARM' in r.stdout)==(status==0),(status,r.returncode,r.stderr)
  results.append(dict(case='actual_shim_status_'+str(status)+'_and_set_e_gate',passed=True))
 pidfile=T/'child.pid';termfile=T/'term'
 r=run('pair_remaining=1\n'+block+'echo ALL_PAIRS_WARM\n',dict(APAC_PBS_DRY_RUN='0',QWEN_MOCK_MODE='sleep',QWEN_MOCK_PIDFILE=str(pidfile),QWEN_MOCK_TERMFILE=str(termfile)))
 assert r.returncode==124 and 'ALL_PAIRS_WARM' not in r.stdout and termfile.read_text()=='terminated',(r.returncode,r.stderr)
 pid=int(pidfile.read_text())
 try:os.kill(pid,0)
 except ProcessLookupError:pass
 else:raise AssertionError('Timed mock child remains alive')
 results.append(dict(case='timeout_124_terminates_mock_step_child_and_blocks_success',passed=True))
(O/'launcher-validation.json').write_text(json.dumps(dict(passed=True,cases=results,scope='Actual warmup shell block and exported PBS shim on CPU; dry-run argv and mocked pbsdsh status/process timeout, no GPU/model/scheduler access',limits=['Real remote pbsdsh termination is not established by a local mock; PBS walltime and head EXIT cleanup remain final bounds.','No native output, heterogeneous transfer, scored performance or accuracy claim.']),indent=2)+'\n')
print('Actual shim CPU regression fixtures PASS:',len(results))
