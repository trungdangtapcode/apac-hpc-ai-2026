from pathlib import Path
import ast,copy,hashlib,json,shutil,logging,types,__future__,subprocess,tarfile
R=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments');O=R/'eagle3-prefill-graph-gate-20261021';B=R/'eagle3-pd-bf16-20261021';source=O/'source/image/sgl-workspace/sglang/python/sglang/srt/model_executor/model_runner_components/cuda_graph_setup.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
empty=O/'source/cuda_graph_setup.py'
if empty.exists():assert empty.stat().st_size==0;empty.unlink()
tree=ast.parse(source.read_text());functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['should_skip_auto_prefill_cuda_graph_for_memory','capture_prefill_graph']]
assert len(functions)==2
phase=types.SimpleNamespace(PREFILL='prefill');backend=types.SimpleNamespace(DISABLED='disabled');logger=logging.getLogger('graph-gate-proof');logger.addHandler(logging.NullHandler())
ns=dict(Phase=phase,Backend=backend,GraphCapture=types.SimpleNamespace,logger=logger,check_cuda_graph_backend=lambda p,b:True,_MIN_AUTO_PREFILL_CUDA_GRAPH_FREE_MEMORY_GB=4.)
exec(compile(ast.Module(body=copy.deepcopy(functions),type_ignores=[]),str(source),'exec',flags=__future__.annotations.compiler_flag),ns)
cases=[]
for free,locked,want in [(3.90,set(),True),(3.98,set(),True),(4.37,set(),False),(3.90,{('prefill','backend')},False)]:
 actual=ns['should_skip_auto_prefill_cuda_graph_for_memory'](free,locked);assert actual==want;cases.append(dict(free_gib=free,explicit_backend=bool(locked),skip=actual))
for is_draft in [False,True]:
 eager=object();actual=ns['capture_prefill_graph'](model_runner=types.SimpleNamespace(is_draft_worker=is_draft),eager_runner=eager,force_for_draft_worker=True)
 assert actual.runner is (None if is_draft else eager)
(O/'native-proof.json').write_text(json.dumps(dict(passed=True,source_sha256=sha(source),source=str(source),threshold_cases=cases,disabled_target_returns_eager=True,disabled_draft_skips_capture=True,scope='Exact native AST functions; no model/graph/collective execution'),indent=2)+'\n')
for name in ['worker.sh','capture-worker-locality.py','resource-sampler.py','verify-draft.py','asset-contract.json','nixl-conn.py','target-staging-record.json']:
 shutil.copyfile(B/name,O/name)
(O/'expected-source.json').write_text(json.dumps({'/sgl-workspace/sglang/python/sglang/srt/model_executor/model_runner_components/cuda_graph_setup.py':sha(source)},indent=2)+'\n')
(O/'entry.sh').write_text('''#!/bin/bash
set -euo pipefail
bundle=$1; art=$2
export HOME=/tmp/ap42-home XDG_CACHE_HOME=/tmp/ap42-home/.cache HF_HOME=/tmp/ap42-home/.cache/huggingface
mkdir -p "$HOME" "$XDG_CACHE_HOME" "$HF_HOME"
python3 - "$bundle" <<'CHECK'
import hashlib,json,sys,os,torch
from pathlib import Path
for name,wanted in json.loads((Path(sys.argv[1])/'expected-source.json').read_text()).items():
 assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==wanted,'Native graph source mismatch'
assert torch.cuda.device_count()==4
assert len(os.environ['CUDA_VISIBLE_DEVICES'].split(','))==4
assert all(torch.cuda.get_device_capability(i)[0]==9 for i in range(4))
print('SOURCE_AND_FOUR_HOPPER_DEVICES_VERIFIED',flush=True)
CHECK
export QWEN_BUNDLE="$bundle" QWEN_ARTDIR="$art" QWEN_RESOURCE_MONITOR=1 QWEN_TELEMETRY_MAX_S=1200
export QWEN_NIXL_PATCH_SHA256=912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f
exec bash "$bundle/worker.sh" prefill-0 30100 /scratch/users/industry/ai-hpc/apacsc42/qwen-assets/Qwen3-235B-A22B-Instruct-2507-FP8 4 \\
 --nccl-port 20000 --disaggregation-bootstrap-port 8998 --cuda-graph-backend-prefill disabled
''')
(O/'component.pbs').write_text('''#!/bin/bash -l
#PBS -P 59010042
#PBS -q normal
#PBS -N ap42-eagle3-pgraph
#PBS -l select=1:ngpus=4:ncpus=56:mem=940gb
#PBS -l walltime=00:20:00
#PBS -j oe
set -euo pipefail
cd "$PBS_O_WORKDIR"
sha256sum --check SHA256SUMS
art="$PBS_O_WORKDIR/runs/$PBS_JOBID"
mkdir -p "$art/submitted" "$art/resource-telemetry"
cp worker.sh capture-worker-locality.py resource-sampler.py verify-draft.py asset-contract.json nixl-conn.py expected-source.json target-staging-record.json entry.sh component.pbs check-probe.py SHA256SUMS "$art/submitted/"
module load singularity/4.1.5
image=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/sglang-harbor.sqsh
private_tmp=$(mktemp -d "${TMPDIR:-/tmp}/ap42-prefill.XXXXXXXX")
timeout --signal=TERM --kill-after=10s 1100s singularity exec --nv --cleanenv --no-home \\
 --bind "/scratch:/scratch,$PBS_O_WORKDIR:$PBS_O_WORKDIR,$private_tmp:/tmp,$PBS_O_WORKDIR/nixl-conn.py:/sgl-workspace/sglang/python/sglang/srt/disaggregation/nixl/conn.py:ro" "$image" /usr/bin/env \\
 PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \\
 LD_LIBRARY_PATH=/.singularity.d/libs:/usr/local/nvidia/lib64:/usr/local/nvidia/lib:/usr/local/cuda/lib64:/usr/local/lib \\
 CUDA_VISIBLE_DEVICES="$CUDA_VISIBLE_DEVICES" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \\
 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 \\
 bash "$art/submitted/entry.sh" "$art/submitted" "$art" >"$art/prefill.log" 2>&1 &
runner=$!
cleanup() { kill "$runner" 2>/dev/null || :; wait "$runner" 2>/dev/null || :; }
trap cleanup EXIT
ready=0
for ((i=0;i<210;i++)); do
 if curl -fsS --max-time 2 http://127.0.0.1:30100/health >"$art/health.json" 2>"$art/health.stderr" && grep -q "The server is fired up and ready to roll!" "$art/prefill.log"; then ready=1; break; fi
 kill -0 "$runner" 2>/dev/null || break
 sleep 5
done
python3 "$art/submitted/check-probe.py" "$art" "$ready" >"$art/probe-result.json"
''')
(O/'check-probe.py').write_text('''"""Semantic readiness gate: no serving request or performance claim."""
import json,re,sys
from pathlib import Path
root=Path(sys.argv[1]);text=(root/'prefill.log').read_text(errors='replace')
nixl=set(re.findall(r' TP(\\d+)\\] NIXL KVManager initialized',text))
proof=dict(health_200=sys.argv[2]=='1',source_and_devices='SOURCE_AND_FOUR_HOPPER_DEVICES_VERIFIED' in text,
 ready_log='The server is fired up and ready to roll!' in text,
 disable_logs=len(re.findall('resolved prefill.backend=',text)),nixl_ranks=sorted(nixl),
 capture_begin=bool(re.search('Capture (target|draft) prefill CUDA graph begin',text)),
 fatal=bool(re.search('Traceback|RuntimeError:|OutOfMemoryError:|Mismatched Tensor',text)))
passed=proof['health_200'] and proof['source_and_devices'] and proof['ready_log'] and proof['disable_logs']>=8 and nixl=={'0','1','2','3'} and not proof['capture_begin'] and not proof['fatal']
print(json.dumps(dict(passed=passed,proof=proof,scope='Single TP4 EAGLE3 prefill readiness only; no complete PD, token-equivalence or ranked performance'),indent=2))
sys.exit(0 if passed else 1)
''')
for p in [O/'entry.sh',O/'component.pbs']:subprocess.run(['bash','-n',str(p)],check=True)
ast.parse((O/'check-probe.py').read_text())
# Exercise the exact artifact guard with synthetic positive/missing-rank/capture cases.
import tempfile
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);good='SOURCE_AND_FOUR_HOPPER_DEVICES_VERIFIED\nThe server is fired up and ready to roll!\n'+('resolved prefill.backend=disabled\n'*8)+''.join(' TP%d] NIXL KVManager initialized\n'%i for i in range(4))
 for case,text,expected in [('valid_fixture',good,True),('missing_rank',good.replace(' TP3] NIXL KVManager initialized\n',''),False),('capture_not_disabled',good+'Capture draft prefill CUDA graph begin',False)]:
  (root/'prefill.log').write_text(text);result=subprocess.run(['python3',str(O/'check-probe.py'),str(root),'1'],capture_output=True,text=True);assert (result.returncode==0)==expected,case
(O/'validation.json').write_text(json.dumps(dict(passed=True,native_function_proof=True,semantic_fixtures=3,requested_gpus=4,minutes=20,max_charge_su=4*128/3,gpu_execution=False),indent=2)+'\n')
files=[p for p in O.iterdir() if p.is_file() and p.name not in ['SHA256SUMS','payload.tar.gz']]
(O/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(files)))
with tarfile.open(O/'payload.tar.gz','w:gz') as tar:
 for p in files+[O/'SHA256SUMS']:tar.add(p,arcname=O.name+'/'+p.name)
print('Prepared native-proof-gated single TP4 readiness probe; max 170.666667 SU, not submitted')
