"""Allocated component checks, not a target/draft model load or inference test."""
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
                  target_weights_loaded=False, draft_model_instantiated=False,
                  inference_executed=False, pd_transfer_tested=False)
    try:
        import torch
        from safetensors import safe_open
        from sglang.srt.configs.model_config import ModelConfig
        from sglang.srt.model_loader.utils import get_model_architecture
        torch.set_num_threads(2)
        torch.set_num_interop_threads(1)
        allocated = os.environ.get('CUDA_VISIBLE_DEVICES', '')
        assert allocated.startswith('GPU-') and ',' not in allocated
        assert torch.cuda.device_count() == 1
        device = torch.cuda.get_device_properties(0)
        assert str(device.uuid) == allocated and 'H100' in device.name
        assert torch.cuda.get_device_capability(0) == (9, 0)
        result['gpu'] = dict(uuid=str(device.uuid), name=device.name)
        expected = json.loads((Path(__file__).parent / 'expected-sources.json').read_text())
        for path, digest in expected.items():
            assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, path
        result['native_source_hashes'] = expected
        original = json.loads((args.draft / 'publisher-config.json').read_text())
        config = json.loads((args.draft / 'config.json').read_text())
        assert {key for key in config.keys() | original.keys() if config.get(key) != original.get(key)} == {'architectures'}
        assert config['architectures'] == ['LlamaForCausalLMEagle3']
        native = ModelConfig(str(args.draft), trust_remote_code=False,
                             dtype='bfloat16', quantization=None, context_length=8192,
                             is_draft_model=True, speculative_algorithm='EAGLE3')
        cls, architecture = get_model_architecture(native)
        assert architecture == cls.__name__ == 'LlamaForCausalLMEagle3'
        assert native.dtype == torch.bfloat16 and native.quantization is None
        result['native_config'] = dict(architecture=architecture, module=cls.__module__,
                                       dtype=str(native.dtype), quantization=native.quantization)
        weights = args.draft / 'model.safetensors'
        digest = hashlib.sha256()
        with weights.open('rb') as stream:
            while block := stream.read(4194304):
                digest.update(block)
        assert weights.stat().st_size == 1145943008
        assert digest.hexdigest() == 'bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86'
        result['draft_sha256'] = digest.hexdigest()
        tensors = []
        with safe_open(weights, framework='pt', device='cpu') as store:
            assert len(store.keys()) == 15
            for name in store.keys():
                value = store.get_tensor(name)
                row = dict(name=name, shape=list(value.shape), dtype=str(value.dtype))
                if name in ('d2t', 't2d'):
                    assert value.dtype == torch.int32
                    row.update(minimum=int(value.min()), maximum=int(value.max()))
                    if name == 'd2t':
                        hot = value.to(torch.int64) + torch.arange(value.numel())
                        assert value.numel() == 64000 and hot.unique().numel() == 64000
                        assert hot.min() >= 0 and hot.max() < 151936
                        row['target_id_range'] = [int(hot.min()), int(hot.max())]
                    else:
                        assert value.numel() == 151936
                        row['native_loader_usage'] = 'Ignored by inspected native load_weights; no inverse-map convention assumed'
                else:
                    assert value.dtype == torch.bfloat16
                    gpu = value.to('cuda:0')
                    assert torch.isfinite(gpu).all().item(), name
                    row['all_finite_on_allocated_gpu'] = True
                    del gpu
                tensors.append(row)
        torch.cuda.synchronize()
        result.update(passed=True, tensors=tensors,
                      peak_validation_vram_bytes=torch.cuda.max_memory_allocated())
    except Exception as error:
        result['failure'] = dict(type=type(error).__name__, message=str(error))
        traceback.print_exc()
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
