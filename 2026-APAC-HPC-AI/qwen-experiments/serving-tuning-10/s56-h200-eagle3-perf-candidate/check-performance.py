#!/usr/bin/env python3
"""Independent CPU head gate for the unranked N=64 performance protocol."""
from __future__ import annotations
import ast, hashlib, importlib.util, json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent

def read_server_args(art, role):
    text=(Path(art)/f'{role}.log').read_text(errors='replace')
    rows=[line.split('server_args=',1)[1] for line in text.splitlines() if 'server_args=ServerArgs(' in line]
    assert len(rows)==1, f'{role}: expected one resolved ServerArgs record'
    node=ast.parse(rows[0],mode='eval').body
    assert isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='ServerArgs'
    needed = {'max_running_requests', 'dtype', 'enable_deterministic_inference',
              'speculative_algorithm', 'speculative_num_steps', 'speculative_eagle_topk',
              'speculative_num_draft_tokens', 'speculative_draft_attention_backend',
              'speculative_draft_model_quantization', 'speculative_draft_model_path'}
    keywords = {kw.arg: kw.value for kw in node.keywords if kw.arg}
    assert needed <= set(keywords), f'{role}: required literal arguments missing'
    # Other values include native CudaGraphConfig(...) expressions. Never evaluate them.
    return {name: ast.literal_eval(keywords[name]) for name in needed}

def validate(art):
    art=Path(art); cfg=json.loads((HERE/'config.json').read_text())
    assert json.loads((art/'config.json').read_text())==cfg, 'submitted config differs from bundle config'
    context=json.loads((art/'launch-context.json').read_text())
    expected_draft=cfg['arm']=='candidate'
    assert context.get('arm')==cfg['arm'] and context.get('has_draft') is expected_draft, 'missing/false control-versus-candidate launch flag'
    assert context.get('bundle_config_sha256')==hashlib.sha256((HERE/'config.json').read_bytes()).hexdigest()
    assert context.get('nixl_conn_wrapper_sha256')==cfg['nixl_conn_wrapper_sha256']
    warm=json.loads((art/'pair-warmup-context.json').read_text())
    assert context.get('experiment_id') and context.get('experiment_id')==warm['experiment_id']
    for role in ('prefill-0','prefill-1','decode-0'):
        args=read_server_args(art,role); cap=48 if role.startswith('prefill') else 256
        assert args.get('max_running_requests')==cap, f'{role}: resolved request cap differs'
        assert args.get('dtype')=='bfloat16' and args.get('enable_deterministic_inference') is True
        if expected_draft:
            required={'speculative_algorithm':'EAGLE3','speculative_num_steps':2,'speculative_eagle_topk':1,'speculative_num_draft_tokens':3,'speculative_draft_attention_backend':'flashinfer','speculative_draft_model_quantization':'unquant'}
            for key,value in required.items(): assert args.get(key)==value, f'{role}: resolved {key} differs'
        else:
            for key in ('speculative_algorithm','speculative_num_steps','speculative_eagle_topk','speculative_num_draft_tokens','speculative_draft_attention_backend','speculative_draft_model_path'):
                assert args.get(key) is None, f'{role}: control resolved unexpected speculative setting {key}'
    runtime=json.loads((art/'runtime-readiness.json').read_text())
    assert runtime.get('state')=='PASS', 'deterministic all-rank runtime gate missing'
    geometry=json.loads((art/'kv-geometry-validation.json').read_text())
    assert geometry.get('passed') is True, 'native per-rank geometry gate missing'
    observed=geometry.get('observed_prefill_mha_signature',{}).get('kv_regions_per_rank')
    assert observed==cfg['expected_prefill_kv_regions_by_arm'][cfg['arm']], 'native prefill geometry differs from arm-specific source expectation'
    token=hashlib.sha256(warm['experiment_id'].encode()).hexdigest()[:32]
    spec=importlib.util.spec_from_file_location('warm_semantic',HERE/'warmup_semantic.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    pair=module.check(art/'pair-warmup-receipts',art/'endpoints.tsv',token)
    assert pair['pair_count']==2, 'both P/D semantic paths required'
    if expected_draft:
        draft=json.loads((art/'draft-worker-headcheck.json').read_text())
        assert draft.get('state')=='PASS', 'candidate draft identity worker gate missing'
    expected_input=json.loads((HERE/'expected-input-config.json').read_text())
    gate_spec=importlib.util.spec_from_file_location('performance_gates',HERE/'performance_gates.py')
    gates=importlib.util.module_from_spec(gate_spec); gate_spec.loader.exec_module(gates)
    profile=gates.check_aiperf(art,expected_input)
    smoke=gates.check_smoke(art,HERE/'reference-output-smoke.json')
    retrieval=gates.check_retrieval(art)
    assert not any((art/x).exists() for x in ('deferred-ns.txt','stop-increase-n.txt','output-smoke-failed.txt','output-smoke-deferred.txt','long-context-check-failed.txt','long-context-check-deferred.txt'))
    return {'state':'PASS_UNRANKED_PERFORMANCE_PROTOCOL','arm':cfg['arm'],'concurrency':64,**profile,'smoke_passed':smoke['passed'],'smoke_total':8,'retrieval_passed':retrieval['passed'],'semantic_pd_pairs':2,'quality':'UNKNOWN_NOT_EVALUATED','ranked':False,'speedup_claim':False}

if __name__=='__main__':
    try: result=validate(sys.argv[1])
    except Exception as e: result={'state':'FAIL','error':str(e)}
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['state']=='PASS_UNRANKED_PERFORMANCE_PROTOCOL' else 1)
