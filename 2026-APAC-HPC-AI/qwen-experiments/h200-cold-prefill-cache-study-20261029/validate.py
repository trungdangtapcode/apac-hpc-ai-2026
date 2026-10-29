#!/usr/bin/env python3
"""Reject wrong cache flags/classes/ranks before spending the two full allocations."""
from pathlib import Path
import json,subprocess,sys,tempfile
D=Path(__file__).resolve().parent
Q=D.parent
prep=json.loads((D/'preparation.json').read_text())
base={r:(Q/'runs/27270'/f'{r}.log').read_text() for r in ('prefill-0','prefill-1','decode-0')}
def replace(text,old,new):
    assert old in text
    return text.replace(old,new)
results=[]
for item in prep['bundles']:
    B=Q/item['bundle']
    logs=dict(base)
    disabled=item['disabled_prefill_radix']
    expected='ChunkCache' if disabled else 'RadixCache'
    if disabled:
        for role in ('prefill-0','prefill-1'):
            logs[role]=replace(logs[role],'disable_radix_cache=False,','disable_radix_cache=True,')
            logs[role]=replace(logs[role],'impl=RadixCache ','impl=ChunkCache ')
    wrong='False' if disabled else 'True'
    cases=[('intended_native_cache_selection',{},True),
      ('reject_wrong_prefill_flag',{'prefill-0':replace(logs['prefill-0'],f'disable_radix_cache={disabled},',f'disable_radix_cache={wrong},')},False),
      ('reject_wrong_prefill_class',{'prefill-0':replace(logs['prefill-0'],f'impl={expected} ','impl=WrongCache ')},False),
      ('reject_physical_KV_disable',{'prefill-0':replace(logs['prefill-0'],'prefill_only_disable_kv_cache=False,','prefill_only_disable_kv_cache=True,')},False),
      ('reject_changed_decode_cap',{'decode-0':replace(logs['decode-0'],'max_running_requests=256,','max_running_requests=64,')},False),
      ('reject_changed_polling',{'decode-0':replace(logs['decode-0'],'disaggregation_decode_polling_interval=1,','disaggregation_decode_polling_interval=2,')},False),
      ('reject_wrong_decode_cache',{'decode-0':replace(logs['decode-0'],'impl=ChunkCache ','impl=RadixCache ')},False),
      ('reject_wrong_decode_flag',{'decode-0':replace(logs['decode-0'],'disable_radix_cache=True,','disable_radix_cache=False,')},False)]
    role='prefill-1'
    missing='\n'.join(x for x in logs[role].splitlines() if not ('TP3]' in x and 'Tree cache initialized:' in x))
    assert missing!=logs[role]
    cases.append(('reject_missing_prefill_rank3_cache',{role:missing},False))
    for marker,name in [('Capture target decode CUDA graph end.','reject_missing_graph_rank7'),('NIXL KVManager initialized','reject_missing_NIXL_rank7')]:
        missing='\n'.join(x for x in logs['decode-0'].splitlines() if not ('TP7 EP7]' in x and marker in x))
        assert missing!=logs['decode-0']
        cases.append((name,{'decode-0':missing},False))
    with tempfile.TemporaryDirectory(prefix='ap42-pcache-fixtures-') as t:
        a=Path(t)
        for name,changes,wanted in cases:
            for role,text in {**logs,**changes}.items():(a/f'{role}.log').write_text(text)
            run=subprocess.run([sys.executable,'-B',str(B/'check-fast-runtime.py'),str(a),'control','64'],text=True,capture_output=True)
            assert (run.returncode==0)==wanted,(B.name,name,run.stdout,run.stderr)
            results.append({'bundle':B.name,'case':name,'expected_pass':wanted,'passed':True})
assert len(results)==22
(D/'validation.json').write_text(json.dumps({'state':'PASS_CPU_CACHE_AND_RUNTIME_FIXTURES_ONLY','fixtures':results,'scope':'Historical real logs with explicitly synthetic altered flags/classes/rank records; no new GPU inference proof.'},indent=2)+'\n')
print('PASS:22 meaningful cache/runtime fixtures.')
