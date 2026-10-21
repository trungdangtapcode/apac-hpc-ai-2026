"""Construct and audit the native draft loader, without target inference."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import traceback


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                  job=os.environ.get('PBS_JOBID'), passed=False,
                  draft_model_instantiated=False, target_weights_loaded=False,
                  inference_executed=False, pd_transfer_tested=False,
                  shared_target_embedding_validated=False)

    def save(stage):
        result['stage'] = stage
        args.out.write_text(json.dumps(result, indent=2) + '\n')

    try:
        save('importing')
        import torch
        from safetensors import safe_open
        from sglang.srt.configs.model_config import ModelConfig
        from sglang.srt.model_loader.utils import get_model_architecture
        from sglang.srt.model_loader.weight_utils import default_weight_loader
        from sglang.srt.runtime_context import publish
        from sglang.srt.server_args import ServerArgs
        from sglang.srt.distributed import init_distributed_environment, initialize_model_parallel
        from sglang.srt.layers.dp_attention import initialize_dp_attention
        from gpu_identity import require_same_device
        torch.set_num_threads(2)
        torch.set_num_interop_threads(1)
        assert torch.cuda.device_count() == 1
        require_same_device(os.environ['CUDA_VISIBLE_DEVICES'], str(torch.cuda.get_device_properties(0).uuid))
        assert torch.cuda.get_device_capability(0) == (9, 0)
        for path, digest in json.loads((Path(__file__).parent/'expected-sources.json').read_text()).items():
            assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, path
        native = ModelConfig(str(args.draft), trust_remote_code=False, dtype='bfloat16',
                             quantization=None, context_length=8192,
                             is_draft_model=True, speculative_algorithm='EAGLE3')
        cls, architecture = get_model_architecture(native)
        assert architecture == 'LlamaForCausalLMEagle3'
        server = ServerArgs(model_path=str(args.draft), dtype='bfloat16',
                            skip_tokenizer_init=True, disable_cuda_graph=True,
                            disable_custom_all_reduce=True, attention_backend='flashinfer',
                            speculative_algorithm='EAGLE3',
                            speculative_draft_model_path=str(args.draft),
                            speculative_num_steps=2, speculative_eagle_topk=1,
                            speculative_num_draft_tokens=3)
        publish(server, role='scheduler', hf_config=native.hf_config)
        save('initializing_native_single_rank_groups')
        torch.cuda.set_device(0)
        init_distributed_environment(world_size=1, rank=0, local_rank=0,
                                     distributed_init_method='file:///tmp/eagle3-native-dist',
                                     backend='nccl', timeout=30)
        initialize_model_parallel(tensor_model_parallel_size=1, pipeline_model_parallel_size=1,
                                  backend='nccl')
        initialize_dp_attention(server, native)
        save('constructing_native_class')
        previous_dtype = torch.get_default_dtype()
        try:
            torch.set_default_dtype(torch.bfloat16)
            with torch.device('cuda:0'):
                model = cls(native.hf_config, quant_config=None).eval()
        finally:
            torch.set_default_dtype(previous_dtype)
        result['draft_model_instantiated'] = True
        params = dict(model.named_parameters())
        result['parameters'] = {name:dict(shape=list(p.shape),dtype=str(p.dtype),device=str(p.device))
                                for name,p in params.items()}
        # Observe exact native weight-loader calls; invoke original loaders unchanged.
        calls = []
        current = {}
        for name, param in params.items():
            original = getattr(param, 'weight_loader', default_weight_loader)
            def observed(parameter, value, *shard, _name=name, _original=original, **kwargs):
                _original(parameter, value, *shard, **kwargs)
                calls.append(dict(source=current['source'], parameter=_name, shard=list(shard)))
            param.weight_loader = observed
        save('loading_published_weights')
        weights = args.draft/'model.safetensors'
        with safe_open(weights, framework='pt', device='cpu') as store:
            def source_weights():
                for name in store.keys():
                    current['source'] = name
                    yield name, store.get_tensor(name)
            model.load_weights(source_weights())
            result['native_loader_calls'] = calls
            float_sources = [name for name in store.keys() if name not in ('d2t','t2d')]
            assert sorted(call['source'] for call in calls) == sorted(float_sources), 'Missing/repeated native tensor consumption'
            shared = 'model.embed_tokens.weight'
            loaded = {call['parameter'] for call in calls}
            assert set(params)-loaded == {shared}, 'Unexpected missing or extra model parameters'
            comparisons = []
            for name in sorted(loaded):
                sources = [call['source'] for call in calls if call['parameter'] == name]
                if name.endswith('.qkv_proj.weight'):
                    ordered = [f'layers.0.self_attn.{part}_proj.weight' for part in ('q','k','v')]
                elif name.endswith('.gate_up_proj.weight'):
                    ordered = [f'layers.0.mlp.{part}_proj.weight' for part in ('gate','up')]
                else:
                    ordered = sources
                assert sorted(ordered) == sorted(sources)
                reference = torch.cat([store.get_tensor(n) for n in ordered], dim=0) if len(ordered)>1 else store.get_tensor(ordered[0])
                actual = params[name].detach().cpu()
                equal = actual.shape == reference.shape and actual.dtype == reference.dtype and torch.equal(actual, reference)
                comparisons.append(dict(parameter=name, sources=ordered, shape=list(actual.shape), exact_equal=equal))
                result['parameter_comparisons'] = comparisons
                assert equal, 'Native loaded parameter differs: '+name
            expected_hot = store.get_tensor('d2t') + torch.arange(64000)
            assert torch.equal(model.get_hot_token_id().cpu(), expected_hot), 'Native hot-token mapping differs'
        torch.cuda.synchronize()
        result.update(passed=True, hot_token_mapping_exact=True,
                      shared_embedding_excluded_reason='Runtime must share the actual target embedding; not present in draft checkpoint. Never run forward with this allocation.',
                      peak_allocated_vram_bytes=torch.cuda.max_memory_allocated(),
                      attention_forward_tested=False, tp4_tp8_tested=False)
        save('draft_load_pass_integration_unverified')
    except Exception as error:
        result['failure'] = dict(type=type(error).__name__, message=str(error))
        traceback.print_exc()
        save('failed')
    finally:
        try:
            if 'torch' in locals() and torch.distributed.is_initialized():
                torch.distributed.destroy_process_group()
        except Exception:
            traceback.print_exc()
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
