#!/usr/bin/env python3
"""Validate intended compile runtime and fail-closed receipt interfaces without GPU."""
from pathlib import Path
import json,subprocess,sys,tempfile
D=Path(__file__).resolve().parent;Q=D.parent
B=Q/'serving-tuning-11/s105-h200-decode-compile54'
H=Q/'h200-decode-compile-startup-20261029'
test=subprocess.run([sys.executable,'-B',str(H/'test_check_compile_receipts.py')],capture_output=True,text=True)
assert test.returncode==0,test.stdout+test.stderr
(D/'receipt-fixtures.log').write_text(test.stdout+test.stderr)
base={r:(Q/'runs/27270'/f'{r}.log').read_text() for r in ('prefill-0','prefill-1','decode-0')}
def replace(text,old,new):
    assert old in text
    return text.replace(old,new)
base['decode-0']=replace(base['decode-0'],'enable_torch_compile=False,','enable_torch_compile=True,')
base['decode-0']=replace(base['decode-0'],'torch_compile_max_bs=32,','torch_compile_max_bs=54,')
cases=[
 ('intended_compile54_runtime',{},True),
 ('reject_disabled_compile',{'decode-0':replace(base['decode-0'],'enable_torch_compile=True,','enable_torch_compile=False,')},False),
 ('reject_inactive_cap32',{'decode-0':replace(base['decode-0'],'torch_compile_max_bs=54,','torch_compile_max_bs=32,')},False),
 ('reject_memory_saver_path',{'decode-0':replace(base['decode-0'],'enable_memory_saver=False,','enable_memory_saver=True,')},False),
 ('reject_compile_on_prefill',{'prefill-0':replace(base['prefill-0'],'enable_torch_compile=False,','enable_torch_compile=True,')},False),
 ('reject_changed_decode_cap',{'decode-0':replace(base['decode-0'],'max_running_requests=256,','max_running_requests=64,')},False),
 ('reject_changed_polling',{'decode-0':replace(base['decode-0'],'disaggregation_decode_polling_interval=1,','disaggregation_decode_polling_interval=2,')},False)]
for marker,name in [('Capture target decode CUDA graph end.','reject_missing_graph_rank7'),('NIXL KVManager initialized','reject_missing_NIXL_rank7')]:
    missing='\n'.join(x for x in base['decode-0'].splitlines() if not ('TP7 EP7]' in x and marker in x))
    assert missing!=base['decode-0']
    cases.append((name,{'decode-0':missing},False))
results=[]
with tempfile.TemporaryDirectory(prefix='ap42-tc54-runtime-fixtures-') as t:
    a=Path(t)
    for name,changes,wanted in cases:
        for role,text in {**base,**changes}.items():(a/f'{role}.log').write_text(text)
        p=subprocess.run([sys.executable,'-B',str(B/'check-fast-runtime.py'),str(a),'control','64'],text=True,capture_output=True)
        assert (p.returncode==0)==wanted,(name,p.stdout,p.stderr)
        results.append({'case':name,'expected_pass':wanted,'passed':True})
controller=(B/'topology-job.sh').read_text()
assert controller.index('check_compile_receipts.py') < controller.index('ALL_WORKERS_READY') < controller.index('warm-topology.py')
assert controller.index('check_compile_receipts.py') < controller.index('benchmark.sh')
perf=(B/'check-performance.py').read_text()
assert 'actual_compile=compile_module.check' in perf and 'compile-startup-gate.json' in perf
(D/'validation.json').write_text(json.dumps({'state':'PASS_CPU_GATES_ONLY','runtime_fixtures':results,'receipt_fixtures_returncode':test.returncode,'controller_order':'Compile startup gate before semantic warmup and any official client; independent raw replay after measurement.','scope':'Fixtures and source/control flow only; no actual Qwen eight-rank compile evidence yet.'},indent=2)+'\n')
print('PASS:9 runtime fixtures, strict receipt metadata/capture/counter fixtures, and pre-client gate order.')
