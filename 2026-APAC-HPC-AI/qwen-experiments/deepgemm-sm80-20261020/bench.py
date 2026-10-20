"""Screen native FP8 linear helpers with synthetic Qwen TP8 attention shapes."""
import argparse
import contextlib
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rank', type=int, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    args.out.mkdir(parents=True, exist_ok=True)
    rank = args.rank
    from runtime_cache import configure
    routes = configure(rank)
    (args.out / ('cache-preflight-rank-' + str(rank) + '.json')).write_text(
        json.dumps(dict(rank=rank, routes=routes, writable=True)) + '\n')
    import torch
    torch.set_num_threads(1)
    torch.cuda.set_device(rank)
    from sglang.srt.layers.quantization import fp8_utils as fp8
    from sglang.srt.layers import deep_gemm_wrapper
    from flashinfer.jit import env as flashinfer_env
    expected_base = Path(routes['FLASHINFER_WORKSPACE_BASE'])
    assert flashinfer_env.FLASHINFER_WORKSPACE_DIR.is_relative_to(expected_base)
    flashinfer_env.FLASHINFER_WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(config['seed'] + rank)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    assert torch.cuda.get_device_capability() == (9, 0)
    assert deep_gemm_wrapper.ENABLE_JIT_DEEPGEMM
    assert not deep_gemm_wrapper.DEEPGEMM_SCALE_UE8M0
    source = Path(fp8.__file__)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest == config['fp8_utils_sha256'], 'Pinned runtime source differs'
    import deep_gemm
    from sglang.srt.layers.deep_gemm_wrapper import compile_utils
    assert hashlib.sha256(Path(deep_gemm.__file__).read_bytes()).hexdigest() == config['deepgemm_init_sha256']
    assert hashlib.sha256(Path(compile_utils.__file__).read_bytes()).hexdigest() == config['compile_utils_sha256']
    assert not compile_utils._ENABLE_JIT_DEEPGEMM_PRECOMPILE
    default_sms = deep_gemm.get_num_sms()
    assert default_sms == torch.cuda.get_device_properties(rank).multi_processor_count == 132
    funcs = {'sms_' + str(n): fp8.deepgemm_w8a8_block_fp8_linear_with_fallback for n in config['sm_settings']}
    report = dict(rank=rank, device=torch.cuda.get_device_name(rank),
                  source_sha256=digest, config_sha256=hashlib.sha256(args.config.read_bytes()).hexdigest(),
                  torch_version=torch.__version__, model_loaded=False, cases=[],
                  units='microseconds per helper call, including activation quantisation',
                  limitation='Isolated synthetic matrix calls; not serving goodput, SLA or official model accuracy.')
    begin = time.monotonic()
    out_path = args.out / ('rank-' + str(rank) + '.json')
    def save():
        tmp = out_path.with_suffix('.tmp')
        tmp.write_text(json.dumps(report, indent=2) + '\n')
        tmp.replace(out_path)
    save()
    with torch.no_grad():
        for shape in config['shapes']:
            n, k = shape['n'], shape['k']
            assert n % 128 == 0 and k % 128 == 0
            raw_weight = torch.randn(n, k, device='cuda', dtype=torch.float32) * .05
            scale = raw_weight.view(n // 128, 128, k // 128, 128).abs().amax((1, 3)).clamp_min(1e-8) / 448
            expanded = scale.repeat_interleave(128, 0).repeat_interleave(128, 1)
            weight = (raw_weight / expanded).clamp(-448, 448).to(torch.float8_e4m3fn).contiguous()
            scale = scale.contiguous()
            weight_ref = weight.float() * expanded
            weight_before, scale_before = weight.clone(), scale.clone()
            for m in config['batch_tokens']:
                x = torch.randn(m, k, device='cuda', dtype=torch.bfloat16)
                x_before = x.clone()
                reference = x.float() @ weight_ref.T
                ref_rms = reference.square().mean().sqrt().clamp_min(1e-8)
                backends = ['sms_' + str(n) for n in config['sm_settings']]
                # Rotate ordering across independent GPUs; no significance claim.
                at = rank % len(backends)
                backends = backends[at:] + backends[:at]
                baseline = None
                outputs = {}
                for backend in backends:
                    assert time.monotonic() - begin < config['python_budget_s'], 'Microbenchmark time budget exhausted'
                    requested_sms = int(backend.split('_')[1])
                    deep_gemm.set_num_sms(requested_sms)
                    assert deep_gemm.get_num_sms() == requested_sms
                    func = funcs[backend]
                    def run():
                        return func(x, weight, [128, 128], scale)
                    for _ in range(4):
                        output = run()
                    torch.cuda.synchronize()
                    assert output.shape == (m, n) and output.dtype == torch.bfloat16
                    assert torch.isfinite(output).all()
                    rel_rmse = float((output.float() - reference).square().mean().sqrt() / ref_rms)
                    assert rel_rmse <= config['max_relative_rmse'], (backend, m, n, k, rel_rmse)
                    outputs[backend] = output.clone()
                    graph = torch.cuda.CUDAGraph()
                    with torch.cuda.graph(graph):
                        for _ in range(config['operations_per_graph']):
                            output = run()
                    for _ in range(5):
                        graph.replay()
                    torch.cuda.synchronize()
                    samples = []
                    for _ in range(config['samples']):
                        start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
                        start.record()
                        for _ in range(config['replays_per_sample']):
                            graph.replay()
                        end.record()
                        end.synchronize()
                        samples.append(start.elapsed_time(end) * 1000 / config['replays_per_sample'] / config['operations_per_graph'])
                    case = dict(role_shape=shape['name'], m=m, n=n, k=k, backend=backend,
                                relative_rmse=rel_rmse, configured_sms=deep_gemm.get_num_sms(), samples_us=samples,
                                median_us=statistics.median(samples))
                    report['cases'].append(case)
                    save()
                    if rank == 0 and m == 54:
                        with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU,
                                                               torch.profiler.ProfilerActivity.CUDA]) as prof:
                            with torch.profiler.record_function('fp8-linear:' + backend):
                                for _ in range(5):
                                    run()
                                torch.cuda.synchronize()
                        path = args.out / (shape['name'] + '-' + backend + '.trace.json')
                        prof.export_chrome_trace(str(path))
                        with path.open('rb') as src, gzip.open(str(path) + '.gz', 'wb') as dst:
                            import shutil
                            shutil.copyfileobj(src, dst)
                        path.unlink()
                    del graph
                baseline = outputs['sms_132'].float()
                for backend, output in outputs.items():
                    diff = float((output.float() - baseline).square().mean().sqrt() / ref_rms)
                    assert diff <= config['max_between_backend_relative_rmse'], (backend, m, n, k, diff)
                    next(c for c in reversed(report['cases']) if c['backend'] == backend)['vs_deepgemm_relative_rmse'] = diff
                # Check inputs after graph and profiling as well as ordinary calls.
                assert torch.equal(x, x_before)
                assert torch.equal(weight.view(torch.uint8), weight_before.view(torch.uint8))
                assert torch.equal(scale, scale_before)
                save()
    deep_gemm.set_num_sms(default_sms)
    assert deep_gemm.get_num_sms() == default_sms
    report.update(default_sms_restored=True)
    report.update(completed=True, input_integrity_passed=True, elapsed_s=time.monotonic() - begin)
    save()
    print(json.dumps(dict(rank=rank, completed=True, cases=len(report['cases']))), flush=True)


if __name__ == '__main__':
    main()
