"""Permit only the exact native prefill-graph consequence of chunk4096 to8192."""
import ast
from pathlib import Path

O = Path(__file__).resolve().parent
SOURCE = O/'runtime-source/server-args/sgl-workspace/sglang/python/sglang/srt/server_args.py'
node = next(n for n in ast.walk(ast.parse(SOURCE.read_text()))
            if isinstance(n,ast.FunctionDef) and n.name=='_generate_prefill_cuda_graph_batch_sizes')
environment = {}
exec(compile(ast.Module(body=[node],type_ignores=[]),str(SOURCE),'exec'),environment)
native_buckets = environment[node.name]

def parse(text):
    value = ast.parse(text,mode='eval').body
    assert isinstance(value,ast.Call) and isinstance(value.func,ast.Name) and value.func.id=='CudaGraphConfig'
    assert not value.args
    result = {}
    for phase in value.keywords:
        assert phase.arg in ['decode','prefill'] and phase.arg not in result
        call = phase.value
        assert isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='PhaseConfig'
        assert not call.args and len({k.arg for k in call.keywords})==len(call.keywords)
        result[phase.arg] = {k.arg:ast.literal_eval(k.value) for k in call.keywords}
    assert set(result)=={'decode','prefill'}
    return result

def check(reference,candidate):
    a,b = parse(reference),parse(candidate)
    assert a['decode']==b['decode'], 'Decode graph configuration changed'
    x,y = a['prefill'],b['prefill']
    assert x['max_bs']==4096 and y['max_bs']==8192
    assert x['bs']==native_buckets(None,4096)
    assert y['bs']==native_buckets(None,8192)
    assert x['backend']==y['backend']=='breakable'
    assert {k:v for k,v in x.items() if k not in ['max_bs','bs']}=={k:v for k,v in y.items() if k not in ['max_bs','bs']}
    return dict(decode_unchanged=True,prefill_backend_unchanged=True,
                max_bs=[4096,8192],buckets_match_pinned_native_generator=True,
                added_buckets=[n for n in y['bs'] if n not in x['bs']])
