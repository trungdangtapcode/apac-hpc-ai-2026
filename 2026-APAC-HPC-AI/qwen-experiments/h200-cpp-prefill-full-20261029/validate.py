#!/usr/bin/env python3
"""Offline mutation fixtures for the staged S106 pre-model and runtime gates.

This script imports no model-serving runtime, PyTorch, CUDA, Slurm client, or
network service. It calls the actual pure admission functions and executes the
actual S106 runtime log validator against synthetic, rank-complete logs.
"""
from __future__ import annotations
import copy
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

Q=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
S106=Q/'serving-tuning-11/s106-h200-prefill-cpp-cache'
RESULTS=[]


def record(name,fn,should_pass):
    try:
        value=fn()
        passed=True
        detail=value
    except (AssertionError,ValueError,SystemExit,subprocess.CalledProcessError) as exc:
        passed=False
        detail=str(exc)
    if passed!=should_pass:
        raise AssertionError(f'{name}: expected pass={should_pass}, observed pass={passed}; {detail}')
    RESULTS.append({'fixture':name,'expected':'PASS' if should_pass else 'REJECT',
                    'observed':'PASS' if passed else 'REJECT','detail':str(detail)[:240]})


def load_admission_module():
    path=S106/'check-cpu-prerequisite.py'
    spec=importlib.util.spec_from_file_location('s106_cpu_admission',path)
    module=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def admission_fixtures():
    gate=load_admission_module()
    expected=json.loads((S106/'CPP_SOURCE_HASHES.json').read_text())['cpu_probe_runtime_sha256']
    control=json.loads((Q/'h200-cold-prefill-cache-study-20261029/control-review-27376.json').read_text())
    parent=json.loads((S106/'PARENT_PAYLOAD_PROVENANCE.json').read_text())
    valid={
        'state':'PASS_CPU_FIXTURES_ONLY','launcher_exit_code':0,'native_remove_end_seen':True,
        'scope':'CPU-only C++ extension and synthetic radix-tree data structure; not RadixCacheCpp integration, P/D, Qwen, or performance.',
        'image_sha256_from_pinned_provenance':'b74ae77446bfedd6c5d72820b45be255cc513cf7c7c039d1bf63679c8178bfe5',
        'cuda_visible_devices':'','nvidia_visible_devices':'void',
        'absolute_job_start_epoch':1000000,'process_deadline_epoch':1000090,'finalized_epoch':1000060,
        'torch_cuda_available':False,'torch_visible_device_count':0,
        'extension_sha256':'a'*64,'extension_path':'/tmp/apac_cpp_radix_probe/cache/torch_extensions/radix_tree_cpp/radix_tree_cpp.so',
        'compiler_version':'c++ (GCC) fixture','gxx_version':'g++ (GCC) fixture',
        'ninja_version':'1.11.1 fixture','torch':'2.11.0+cu130 fixture','python':'3.12 fixture',
        'phase_jit_import_seconds':19.75,'prebuild_runtime_source_sha256':expected,
        'runtime_source_sha256':expected,
        'torch_extensions_dir':'/tmp/apac_cpp_radix_probe/cache/torch_extensions',
        'cases':[]}
    one={
        'result':'PASS','initial_insert_matched_tokens':0,'exact_repeat_matched_tokens':32,
        'prefix_tokens_checked':16,'overlap_matched_tokens':16,
        'unique_cached_indices_after_split':48,'protected_indices_while_locked':32,
        'indices_evicted_while_locked':16,'indices_evicted_after_unlock':32,
        'reset_sizes':{'total':0,'evictable':0,'protected':0},
        'interpretation':'page1 is the production-page-size fixture; page16 is metadata-only and does not qualify page16 KV behavior'}
    valid['cases']=[dict(one,page_size=1),dict(one,page_size=16)]
    status='27387|COMPLETED|0:0\n'
    host=('PROBE_EXECUTION_STATE=running_diagnostic\nJOB=27387\nHOST=fixture\n'
          'JOB_START_EPOCH=1000000\nPROCESS_DEADLINE_EPOCH=1000090\nGPU_REQUEST=0\nCPU_REQUEST=2\n')
    def admission(probe=valid,sacct=status,rc=0,stderr='',host_start=host):
        return gate.validate_admission(sacct,rc,stderr,host_start,json.dumps(probe),expected,control,parent)
    record('cpu-positive-exact-job-host-and-probe-shape',admission,True)
    record('cpu-wrong-scheduler-job-id',lambda:admission(sacct='27388|COMPLETED|0:0\n'),False)
    record('cpu-wrong-terminal-state',lambda:admission(sacct='27387|FAILED|1:0\n'),False)
    record('cpu-host-start-wrong-job-id',lambda:admission(host_start=host.replace('JOB=27387','JOB=27388')),False)
    bad=copy.deepcopy(valid);bad['absolute_job_start_epoch']+=1
    record('cpu-probe-job-time-does-not-match-host-start',lambda:admission(probe=bad),False)
    record('cpu-host-start-deadline-wrong',lambda:admission(host_start=host.replace('PROCESS_DEADLINE_EPOCH=1000090','PROCESS_DEADLINE_EPOCH=1000100')),False)
    record('cpu-sacct-command-error',lambda:admission(rc=1,stderr='accounting unavailable'),False)
    record('cpu-malformed-actual-result-json',lambda:gate.parse_actual_probe_json('{broken'),False)
    bad=copy.deepcopy(valid);bad['state']='FAIL'
    record('cpu-failed-probe-state',lambda:admission(probe=bad),False)
    bad=copy.deepcopy(valid);bad['native_remove_end_seen']=False
    record('cpu-missing-native-cleanup-receipt',lambda:admission(probe=bad),False)
    bad=copy.deepcopy(valid);bad['runtime_source_sha256']['tree_v2.cpp']='0'*64
    record('cpu-source-hash-does-not-match-candidate',lambda:admission(probe=bad),False)
    bad=copy.deepcopy(valid);bad['prebuild_runtime_source_sha256']['tree_v2.cpp']='0'*64
    record('cpu-pre-JIT-source-hash-does-not-match-candidate',lambda:admission(probe=bad),False)
    bad=copy.deepcopy(valid);bad['extension_path']='/tmp/shared/radix_tree_cpp.so'
    record('cpu-extension-not-in-private-cache',lambda:admission(probe=bad),False)
    bad=copy.deepcopy(valid);bad['finalized_epoch']=1000121
    record('cpu-finalized-beyond-cleanup-grace',lambda:admission(probe=bad),False)
    bad=copy.deepcopy(valid);bad['scope']='full RadixCacheCpp integration'
    record('cpu-probe-scope-overclaim',lambda:admission(probe=bad),False)
    bad=copy.deepcopy(valid);bad['cases']=[bad['cases'][0]]
    record('cpu-page16-fixture-missing',lambda:admission(probe=bad),False)
    bad=copy.deepcopy(valid);bad['cases'][1]['interpretation']='page16 KV is qualified'
    record('cpu-page16-scope-mislabelled',lambda:admission(probe=bad),False)
    bad=copy.deepcopy(valid);bad['extension_sha256']='not-a-sha256'
    record('cpu-native-binary-hash-malformed',lambda:admission(probe=bad),False)
    bad_control=copy.deepcopy(control);bad_control['summary']['good_output_tokens_s']+=1
    record('cpu-frozen-control-score-changed',lambda:gate.validate_admission(status,0,'',host,json.dumps(valid),expected,bad_control,parent),False)


def server_args(role,cfg,mutations):
    p=role.startswith('prefill')
    values={
        'model_path':'/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8',
        'dtype':'bfloat16','context_length':8192,'mem_fraction_static':0.9,
        'disaggregation_mode':'prefill' if p else 'decode','disaggregation_transfer_backend':'nixl',
        'trust_remote_code':True,'kv_cache_dtype':'auto','tp_size':4 if p else 8,
        'ep_size':1 if p else 8,'moe_dp_size':1,
        'max_running_requests':cfg['prefill_max_running_requests'] if p else 256,
        'enable_deterministic_inference':False,'sampling_backend':'flashinfer',
        'disable_custom_all_reduce':False,'attention_backend':'fa3','decode_attention_backend':'flashinfer' if not p else None,
        'chunked_prefill_size':cfg['prefill_chunked_prefill_size'] if p else None,
        'moe_runner_backend':'deep_gemm' if p else 'hpc_ops',
        'flashinfer_allreduce_fusion_backend':'auto' if p else 'mnnvl',
        'enable_dynamic_batch_tokenizer':False,'dynamic_batch_tokenizer_batch_size':32,
        'dynamic_batch_tokenizer_batch_timeout':cfg['prefill_tokenizer_batch_timeout'] if p else 0.002,
        'enable_tokenizer_batch_encode':False,'skip_tokenizer_init':False,
        'disaggregation_decode_polling_interval':cfg['prefill_transfer_polling_interval'] if p else cfg['decode_transfer_polling_interval'],
        'disable_radix_cache':cfg['prefill_disable_radix_cache'] if p else cfg['decode_disable_radix_cache'],
        'prefill_only_disable_kv_cache':False,'radix_cache_backend':None,
        'enable_session_radix_cache':False,'enable_streaming_session':False,
        'enable_hierarchical_cache':False,
        'speculative_algorithm':None,'speculative_draft_model_path':None,
        'speculative_num_steps':None,'speculative_eagle_topk':None,
        'speculative_num_draft_tokens':None,'speculative_draft_attention_backend':None,
        'speculative_draft_model_quantization':None,
    }
    values.update(mutations.get('args',{}))
    pg=cfg['prefill_cuda_graph'] if p else 'disabled'
    if p:
        decode_cfg="Graph(backend='disabled')"
    else:
        batches=repr(list(range(1,65)))
        decode_cfg=f"Graph(backend='full', max_bs=64, bs={batches})"
    fields=[]
    for k,v in values.items():
        if k=='chunked_prefill_size' and not p: continue
        fields.append(f'{k}={v!r}')
    fields.append(f"cuda_graph_config=GraphConfig(prefill=Graph(backend={pg!r}), decode={decode_cfg})")
    return 'server_args=ServerArgs('+', '.join(fields)+')'


def role_log(role,cfg,mutation=None):
    mutation=mutation or {}; p=role.startswith('prefill'); ranks=4 if p else 8
    rows=[f"CPP_RADIX_ENV role={role} value={'1' if p else 'unset'} MAX_JOBS={'2' if p else 'unset'}",
          'TRANSFER_POLL_SOURCE_VERIFIED','CACHE_LIFECYCLE_SOURCE_VERIFIED',
          'CPP_RADIX_SOURCE_VERIFIED 13']
    rows.append(server_args(role,cfg,mutation))
    rows.append('The server is fired up and ready to roll!')
    for rank in range(ranks):
        selected=not (mutation.get('missing_cpp_rank')==rank and p)
        if p and selected:
            selected_rank=mutation.get('duplicate_cpp_rank') if mutation.get('duplicate_cpp_rank') is not None and rank==3 else rank
            rows.append(f'[TP{selected_rank}] Using experimental C++ radix tree implementation.')
        actual_class=mutation.get('cache_class_override',{}).get(rank,
            cfg['prefill_expected_cache'] if p else cfg['decode_expected_cache'])
        rows.append(f'[TP{rank}] Tree cache initialized: source=default impl={actual_class} hybrid_swa=False hybrid_ssm=False hierarchical=False streaming_wrapped=False')
        rows.append(f'[TP{rank}] KV Cache is allocated. dtype: torch.bfloat16, #tokens: 1024, K size: 2.0 GB, V size: 2.0 GB')
        rows.append(f'[TP{rank}] NIXL KVManager initialized')
        if p and cfg['prefill_cuda_graph']=='breakable':
            rows.append(f'[TP{rank}] Capture target prefill CUDA graph begin. backend=breakable')
            rows.append(f'[TP{rank}] Capture target prefill CUDA graph end.')
        if not p:
            rows.append(f"[TP{rank} EP{rank}] Disable prefill CUDA graph because cuda_graph_config resolved prefill.backend='disabled'")
            rows.append(f'FlashInfer AllReduce Fusion enabled and workspace initialized: backend=mnnvl, rank={rank}, world_size=8')
            rows.append(f'[TP{rank} EP{rank}] Capture target decode CUDA graph end.')
    if mutation.get('missing_source_marker'):
        rows.remove('CPP_RADIX_SOURCE_VERIFIED 13')
    if mutation.get('bad_source_count'):
        rows[rows.index('CPP_RADIX_SOURCE_VERIFIED 13')]='CPP_RADIX_SOURCE_VERIFIED 12'
    if mutation.get('decode_cpp_marker'):
        rows.append('[TP0] Using experimental C++ radix tree implementation.')
    if mutation.get('bad_env'):
        rows[0]=rows[0].replace('value=1','value=unset')
    if mutation.get('bad_build_cap'):
        rows[0]=rows[0].replace('MAX_JOBS=2','MAX_JOBS=8')
    return '\n'.join(rows)+'\n'


def runtime_fixtures():
    cfg=json.loads((S106/'config.json').read_text())
    checker=S106/'check-fast-runtime.py'
    source_hashes=json.loads((S106/'CPP_SOURCE_HASHES.json').read_text())
    def run(muts=None):
        muts=muts or {}
        with tempfile.TemporaryDirectory(prefix='s106-runtime-fixture-') as tmp:
            tmp=Path(tmp); bundle=tmp/'bundle'; art=tmp/'art'
            bundle.mkdir(); art.mkdir()
            (bundle/'config.json').write_text(json.dumps(cfg))
            (bundle/'CPP_SOURCE_HASHES.json').write_text(json.dumps(source_hashes))
            test_checker=bundle/'check-fast-runtime.py'
            test_checker.write_bytes(checker.read_bytes())
            for role in ('prefill-0','prefill-1','decode-0'):
                text=role_log(role,cfg,muts.get(role))
                (art/f'{role}.log').write_text(text)
            proc=subprocess.run([sys.executable,'-B',str(test_checker),str(art),'control','64'],
                                text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,timeout=10)
            if proc.returncode:
                raise ValueError(proc.stdout+proc.stderr)
            return json.loads(proc.stdout)
    record('runtime-positive-eight-P-Cpp-and-native-D-Chunk',run,True)
    record('runtime-missing-P-rank-selection-marker',lambda:run({'prefill-0':{'missing_cpp_rank':3}}),False)
    record('runtime-duplicate-P-rank-selection-marker',lambda:run({'prefill-1':{'duplicate_cpp_rank':2}}),False)
    record('runtime-wrong-P-rank-cache-class',lambda:run({'prefill-1':{'cache_class_override':{2:'RadixCache'}}}),False)
    record('runtime-wrong-P-cache-disable-flag',lambda:run({'prefill-0':{'args':{'disable_radix_cache':True}}}),False)
    record('runtime-wrong-D-cache-class',lambda:run({'decode-0':{'cache_class_override':{5:'RadixCacheCpp'}}}),False)
    record('runtime-wrong-D-cache-disable-flag',lambda:run({'decode-0':{'args':{'disable_radix_cache':False}}}),False)
    record('runtime-D-selects-experimental-CPP',lambda:run({'decode-0':{'decode_cpp_marker':True}}),False)
    record('runtime-P-env-flag-mismatch',lambda:run({'prefill-0':{'bad_env':True}}),False)
    record('runtime-P-JIT-build-cap-mismatch',lambda:run({'prefill-1':{'bad_build_cap':True}}),False)
    record('runtime-missing-image-source-hash-guard-marker',lambda:run({'prefill-0':{'missing_source_marker':True}}),False)
    record('runtime-wrong-image-source-guard-file-count',lambda:run({'decode-0':{'bad_source_count':True}}),False)


def config_single_factor_fixture():
    parent=json.loads((Q/'runs/27376/submitted-payload/config.json').read_text())
    candidate=json.loads((S106/'config.json').read_text())
    allowed={'cpp_radix_cache_env','experiment','label','matched_control_job','matched_pair',
             'prefill_expected_cache','source_parent_job','staging_state'}
    changed={key for key in set(parent)|set(candidate) if parent.get(key)!=candidate.get(key)}
    if changed!=allowed:
        raise ValueError(f'candidate config has unexplained differences from exact 27376 control: {sorted(changed^allowed)}')
    worker=(S106/'worker.sh').read_text()
    assert 'export SGLANG_EXPERIMENTAL_CPP_RADIX_TREE=1' in worker
    assert 'export MAX_JOBS=2' in worker and 'TORCH_EXTENSIONS_DIR=/tmp/sglang-$name/torch_extensions' in worker
    assert 'unset SGLANG_EXPERIMENTAL_CPP_RADIX_TREE MAX_JOBS TORCH_EXTENSIONS_DIR' in worker
    RESULTS.append({'fixture':'exact-control-config-single-treatment-and-compile-only-environment','expected':'PASS','observed':'PASS','detail':'only P CPP radix flag changes serving behavior; MAX_JOBS=2/private JIT cache are bounded build controls, D unsets all three'})


def patchcheck_fixtures():
    worker=(S106/'worker.sh').read_text()
    assert worker.index('export QWEN_ROLE_NAME="$name"') < worker.index("python3 - <<'PATCHCHECK'")
    block=worker.split("python3 - <<'PATCHCHECK'\n",1)[1].split('\nPATCHCHECK',1)[0]
    assert 'import hashlib,json,os' in block
    with tempfile.TemporaryDirectory(prefix='s106-patchcheck-fixture-') as tmp:
        root=Path(tmp); src=root/'sglang/python'; bundle=root/'bundle'; bundle.mkdir()
        names=re.findall(r"Path\('(/sgl-workspace/sglang/python/[^']+)'\)",block)
        rels=sorted({name.removeprefix('/sgl-workspace/sglang/python/') for name in names})
        pins=json.loads((S106/'CPP_SOURCE_HASHES.json').read_text())['image_source_sha256']
        rels=sorted(set(rels)|set(pins))
        hashes={}
        for rel in rels:
            target=src/rel; target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text('fixture:'+rel)
            hashes[rel]=__import__('hashlib').sha256(target.read_bytes()).hexdigest()
        adapted=block.replace('/sgl-workspace/sglang/python',str(src))
        rewritten=[]
        for line in adapted.splitlines():
            match=re.search(r"Path\('([^']+)'\).*?\.hexdigest\(\)==('[0-9a-f]{64}')",line)
            if match:
                path=Path(match.group(1))
                rel=path.relative_to(src).as_posix()
                line=line.replace(match.group(2),"'"+hashes[rel]+"'")
            rewritten.append(line)
        adapted='\n'.join(rewritten)+'\n'
        cpp_map={rel:hashes[rel] for rel in pins}
        (bundle/'CPP_SOURCE_HASHES.json').write_text(json.dumps({'image_source_sha256':cpp_map}))
        env={'QWEN_NIXL_PATCH_SHA256':hashes['sglang/srt/disaggregation/nixl/conn.py'],
             'QWEN_BUNDLE':str(bundle),'QWEN_ROLE_NAME':'prefill-0','SGLANG_EXPERIMENTAL_CPP_RADIX_TREE':'1'}
        positive=subprocess.run([sys.executable,'-c',adapted],env={**os.environ,**env},text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,timeout=5)
        if positive.returncode: raise ValueError('actual PATCHCHECK positive fixture failed: '+positive.stderr)
        tamper=src/next(iter(pins)); tamper.write_text('tampered after pin')
        changed=subprocess.run([sys.executable,'-c',adapted],env={**os.environ,**env},text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,timeout=5)
        if changed.returncode==0: raise ValueError('actual PATCHCHECK accepted a mutated pinned C++ source')
        env['QWEN_ROLE_NAME']='decode-0'; env['SGLANG_EXPERIMENTAL_CPP_RADIX_TREE']='1'
        negative=subprocess.run([sys.executable,'-c',adapted],env={**os.environ,**env},text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,timeout=5)
        if negative.returncode==0: raise ValueError('actual PATCHCHECK accepted C++ radix env on decode role')
    RESULTS.append({'fixture':'worker-patchcheck-import-env-order-and-execution','expected':'PASS','observed':'PASS','detail':'actual embedded guard passed P, rejected changed pinned C++ source and leaked decode flag'})


def main():
    admission_fixtures()
    runtime_fixtures()
    config_single_factor_fixture()
    patchcheck_fixtures()
    assert RESULTS and all(row['observed']==row['expected'] for row in RESULTS)
    print(json.dumps({'state':'PASS_OFFLINE_MUTATION_FIXTURES','runtime_imports':'stdlib only; no Torch/model/CUDA',
                      'actual_cpu_job_result_used':False,'fixtures':RESULTS},indent=2))


if __name__=='__main__': main()
