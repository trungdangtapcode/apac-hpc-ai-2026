#!/usr/bin/env python3
"""CPU-only bundle, source, flag, and synthetic-log parser fixtures."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent
EXP = ROOT.parent
TUNING = EXP / 'serving-tuning-10'
S41 = TUNING / 's41-h200-graph-disabled-cap64-screen'
BUNDLES = {
    'auto': TUNING / 's47-h200-bf16-kv-control',
    'fp8_e4m3': TUNING / 's48-h200-fp8-kv-screen',
}
PREFLIGHT = json.loads((ROOT / 'checkpoint-kv-scale-preflight.json').read_text())


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def worker_contract(text: str, mode: str) -> bool:
    if '--dtype bfloat16' not in text or '"${extra[@]}"' not in text:
        return False
    if '--cuda-graph-backend-prefill disabled' not in text:
        return False
    if 'kv_extra=(--kv-cache-dtype fp8_e4m3)' not in text:
        return False
    if mode == 'fp8_e4m3':
        return 'if [[ ${QWEN_KV_CACHE_DTYPE:-auto} == fp8_e4m3 ]]' in text
    return mode == 'auto' and 'elif [[ ${QWEN_KV_CACHE_DTYPE:-auto} != auto ]]' in text


def argv_line(role: str, kv: str, rank: int) -> str:
    tp, ep, cap, moe, disagg = {
        'prefill-0': (4, 1, 64, 'deep_gemm', 'prefill'),
        'prefill-1': (4, 1, 64, 'deep_gemm', 'prefill'),
        'decode-0': (8, 8, 256, 'hpc_ops', 'decode'),
    }[role]
    backend = ", decode_attention_backend='flashinfer'" if role == 'decode-0' else ''
    return (f"2026-10-24 [TP{rank}] server_args=ServerArgs(kv_cache_dtype='{kv}', "
            f"quantization_param_path=None, dtype='bfloat16', max_running_requests={cap}, "
            f"tp_size={tp}, ep_size={ep}, chunked_prefill_size=8192, "
            f"moe_runner_backend='{moe}', disaggregation_mode='{disagg}', "
            f"cuda_graph_backend_prefill='disabled'{backend}, "
            "disable_prefill_cuda_graph=False, speculative_algorithm=None, "
            "speculative_draft_model_path=None, speculative_num_steps=None, "
            "speculative_eagle_topk=None, speculative_num_draft_tokens=None, "
            "enable_multi_layer_eagle=False, "
            "cuda_graph_config=Graph(decode=GraphConfig(backend='full', max_bs=64, bs=[1, 2]), "
            "prefill=PhaseConfig(backend='disabled', max_bs=0, bs=[])))")


def synthetic_role_log(role: str, kv: str, dtype: str) -> str:
    tp = 4 if role.startswith('prefill') else 8
    rows=[]
    for rank in range(tp):
        rows.append(argv_line(role, kv, rank))
        rows.append(f'2026-10-24 [TP{rank}] KV Cache is allocated. dtype: {dtype}, #tokens: 8192, KV size: 1.00 GB')
    return '\n'.join(rows) + '\n'


def main() -> None:
    assert PREFLIGHT['checkpoint_kv_scale_key_count'] == 0
    assert PREFLIGHT['weight_shards_opened'] is False
    assert PREFLIGHT['num_hidden_layers'] == 94 and PREFLIGHT['num_key_value_heads'] == 4 and PREFLIGHT['head_dim'] == 128

    provenance=json.loads((ROOT/'SOURCE_PROVENANCE.json').read_text())
    report=EXP/'fp8-kv-source-preflight-20261023'/'source-image'
    by_rel={row['path']:row['sha256'] for row in provenance['pinned_source_files']}
    dtype_source=report/'sgl-workspace/sglang/python/sglang/srt/mem_cache/kv_cache_dtype.py'
    pool_source=report/'sgl-workspace/sglang/python/sglang/srt/mem_cache/memory_pool.py'
    assert hashlib.sha256(dtype_source.read_bytes()).hexdigest()==by_rel['sgl-workspace/sglang/python/sglang/srt/mem_cache/kv_cache_dtype.py']
    assert hashlib.sha256(pool_source.read_bytes()).hexdigest()==by_rel['sgl-workspace/sglang/python/sglang/srt/mem_cache/memory_pool.py']
    dtype_text=dtype_source.read_text();pool_text=pool_source.read_text()
    assert 'kv_cache_dtype = model_dtype' in dtype_text and 'KV cache scaling factors default to 1.0' in (report/'sgl-workspace/sglang/python/sglang/srt/server_args.py').read_text()
    assert 'torch.float8_e4m3fn' in dtype_text and 'self.store_dtype = torch.uint8' in pool_text
    assert 'dtype: {self.dtype}' in pool_text

    changed=[]
    for mode,bundle in BUNDLES.items():
        worker=(bundle/'worker.sh').read_text()
        assert worker_contract(worker,mode),f'{bundle.name}: worker argv contract failed'
        # Regression: the prior S44 worker omitted explicit model dtype. The fixture must reject it.
        assert not worker_contract(worker.replace('--dtype bfloat16 ',''),mode), 'omitted --dtype bfloat16 must fail'
        job=(bundle/'job.sbatch').read_text()
        assert f'QWEN_KV_CACHE_DTYPE={mode}' in job
        topology=(bundle/'topology-job.sh').read_text()
        assert 'QWEN_KV_CACHE_DTYPE="$QWEN_KV_CACHE_DTYPE"' in topology
        assert 'check-kv-runtime.py' in topology
        config=json.loads((bundle/'config.json').read_text())
        assert config['kv_dtype']==mode and config['screen_unranked'] is True
        assert config['concurrency']==[64] and config['context_length']==8192
        assert config['screen_warmup_s']==20 and config['screen_measure_s']==40
        assert config['client_walltime_limit_s']==135
        assert config['official_accuracy_verified'] is False
        expected=json.loads((bundle/'expected-input-config.json').read_text())
        assert expected==json.loads((S41/'expected-input-config.json').read_text())
        for name in ('benchmark.sh','summarize.py','output-smoke.py','long-context-check.py','warmup_semantic.py','warm-topology.py','placement.tsv','nixl-conn.py','profile-serving.py','resource-sampler.py','reference-output-smoke.json'):
            assert (bundle/name).read_bytes()==(S41/name).read_bytes(),f'{bundle.name}: changed S41 file {name}'
        changed.append(bundle)

    # The only protocol data change is KV dtype; both roles get the candidate flag via one shared worker path.
    c0=json.loads((BUNDLES['auto']/'config.json').read_text())
    c1=json.loads((BUNDLES['fp8_e4m3']/'config.json').read_text())
    for key in ('context_length','concurrency','prefill_workers','decode_workers','prefill_tp','decode_tp','decode_ep','dtype','memory_fraction','decode_max_running_requests','prefill_max_running_requests','prefill_chunk_size','transfer','transport_patch','prefill_cuda_graph_policy','screen_warmup_s','screen_measure_s','grace_s'):
        assert c0[key]==c1[key],f'pair mismatch in {key}'
    assert c0['kv_dtype']=='auto' and c1['kv_dtype']=='fp8_e4m3'

    # Parser fixtures use synthetic text only. They test the gate, never imitate a GPU result.
    checker=load(BUNDLES['auto']/'check-kv-runtime.py','kv_runtime_checker')
    capacity=load(BUNDLES['auto']/'audit-capacity.py','capacity_fixture')
    with tempfile.TemporaryDirectory(prefix='fp8-kv-parser-fixture-') as temp:
        tmp=Path(temp)
        scale_file=tmp/'kv-scale-provenance.json';scale_file.write_text(json.dumps(PREFLIGHT))
        outcomes=[]
        for mode in ('auto','fp8_e4m3'):
            bundle=BUNDLES[mode]
            art=tmp/mode;art.mkdir()
            shutil.copy2(scale_file,art/'kv-scale-provenance.json')
            dtype='torch.bfloat16' if mode=='auto' else 'torch.float8_e4m3fn'
            for role in ('prefill-0','prefill-1','decode-0'):
                (art/f'{role}.log').write_text(synthetic_role_log(role,mode,dtype))
                result=checker.check(bundle,art,role,mode)
                assert result['status']=='PASS_RUNTIME_KV_ALLOCATION',result
                outcomes.append({'mode':mode,'role':role,'status':result['status']})
            parsed=capacity._parse_server_args((art/'decode-0.log').read_text().splitlines()[0])
            assert parsed['dtype']=='bfloat16' and parsed['max_running_requests']==256
            assert parsed['graph_config']['prefill']['backend']=='disabled'
        bad=tmp/'missing-runtime-proof';bad.mkdir();shutil.copy2(scale_file,bad/'kv-scale-provenance.json')
        (bad/'decode-0.log').write_text(argv_line('decode-0','fp8_e4m3',0)+'\n')
        try: checker.check(BUNDLES['fp8_e4m3'],bad,'decode-0','fp8_e4m3')
        except ValueError as error: assert 'no resolved ServerArgs' in str(error) or 'missing actual KV Cache allocation' in str(error)
        else: raise AssertionError('missing actual cache allocation proof must fail')
        bad_dtype=tmp/'wrong-runtime-dtype';bad_dtype.mkdir();shutil.copy2(scale_file,bad_dtype/'kv-scale-provenance.json')
        (bad_dtype/'decode-0.log').write_text(synthetic_role_log('decode-0','fp8_e4m3','torch.bfloat16'))
        try: checker.check(BUNDLES['fp8_e4m3'],bad_dtype,'decode-0','fp8_e4m3')
        except ValueError as error: assert 'logical KV allocation dtype set differs' in str(error)
        else: raise AssertionError('wrong actual KV allocation dtype must fail')

    result={
        'status':'PASS_CPU_FIXTURES_ONLY',
        'scope':'Static bundle and parser tests; synthetic logs only. No H200, CUDA, SGLang server, NIXL transfer, benchmark, or GPU performance is emulated.',
        'checkpoint_preflight_sha256':PREFLIGHT['index_sha256'],
        'checkpoint_kv_scale_keys':0,
        'worker_argv_regression':'S44-style omission of explicit --dtype bfloat16 is rejected for both bundles',
        'fp8_worker_flag':'single worker path injects --kv-cache-dtype fp8_e4m3 for both P and D roles',
        'synthetic_runtime_parser_cases':outcomes,
        'negative_cases':['missing actual cache allocation proof','wrong logical cache allocation dtype'],
        'quality_status':'UNKNOWN',
        'official_accuracy_verified':False,
    }
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
