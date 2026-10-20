"""Measure one-shot/two-shot MNNVL fusion without loading the language model."""
from pathlib import Path
import argparse
import datetime
import gzip
import hashlib
import inspect
import json
import os
import statistics
import time

import torch
import torch.distributed as dist
import flashinfer
from flashinfer.comm import AllReduceFusionPattern, allreduce_fusion, create_allreduce_fusion_workspace
from flashinfer.comm.mnnvl import TorchDistBackend
from flashinfer.comm.trtllm_mnnvl_ar import MNNVLAllreduceFusionStrategy


def write_json(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2) + '\n')
    temp.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    local_rank = int(os.environ['LOCAL_RANK'])
    torch.cuda.set_device(local_rank)
    dist.init_process_group('gloo', timeout=datetime.timedelta(seconds=180))
    rank, world = dist.get_rank(), dist.get_world_size()
    assert world == 8 and torch.cuda.get_device_capability()[0] == 9
    assert 'H100' in torch.cuda.get_device_name()
    config = json.loads((Path(__file__).parent / 'config.json').read_text())
    for name, digest in config['runtime_source_sha256'].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest, name
    for func, fields in [(create_allreduce_fusion_workspace, ['force_oneshot_support', 'comm_backend']),
                         (allreduce_fusion, ['use_oneshot', 'launch_with_pdl', 'residual_out', 'norm_out'])]:
        assert set(fields) <= set(inspect.signature(func).parameters)
    hidden = config['hidden_size']
    shapes = config['token_counts']
    workspace = create_allreduce_fusion_workspace(
        backend='mnnvl', world_size=world, rank=rank, max_token_num=max(shapes),
        hidden_dim=hidden, dtype=torch.bfloat16, gpus_per_node=world,
        comm_backend=TorchDistBackend(), force_oneshot_support=True)
    assert workspace.backend == 'mnnvl'
    strategies = [('pdl_on', None, MNNVLAllreduceFusionStrategy.AUTO, True),
                  ('pdl_off', None, MNNVLAllreduceFusionStrategy.AUTO, False)]
    rows = []
    metadata = dict(kind='isolated_kernel_microbenchmark_not_model_goodput', rank=rank,
                    world_size=world, gpu=torch.cuda.get_device_name(), torch=torch.__version__,
                    flashinfer=getattr(flashinfer, '__version__', 'unknown'),
                    workspace_buffer_bytes=workspace.buffer_size_bytes, config=config)
    write_json(args.out / ('rank-' + str(rank) + '-metadata.json'), metadata)
    for tokens in shapes:
        # Independent CPU seeds create reproducible BF16 rank inputs and reference.
        parts = [torch.randn((tokens, hidden), generator=torch.Generator().manual_seed(2026+r))
                 .mul_(0.2).to(torch.bfloat16) for r in range(world)]
        residual_cpu = torch.randn((tokens, hidden), generator=torch.Generator().manual_seed(7000)).mul_(0.1).to(torch.bfloat16)
        reference_residual = (sum(p.float() for p in parts) + residual_cpu.float()).to(torch.bfloat16)
        reference_norm = (reference_residual.float() * torch.rsqrt(reference_residual.float().pow(2).mean(-1, keepdim=True) + 1e-6)).to(torch.bfloat16)
        x = parts[rank].cuda()
        original_x = x.clone()
        residual = residual_cpu.cuda()
        original_residual = residual.clone()
        gamma = torch.ones(hidden, device='cuda', dtype=torch.bfloat16)
        residual_out = torch.empty_like(x)
        norm_out = torch.empty_like(x)
        for repetition in range(2):
            ordering = strategies if repetition == 0 else list(reversed(strategies))
            for name, force, strategy, launch_pdl in ordering:
                assert workspace.is_buffer_size_sufficient(world, tokens, hidden, torch.bfloat16, strategy)
                def run():
                    return allreduce_fusion(input=x, workspace=workspace,
                        pattern=AllReduceFusionPattern.kARResidualRMSNorm,
                        launch_with_pdl=launch_pdl, residual_out=residual_out, norm_out=norm_out,
                        residual_in=residual, rms_gamma=gamma, rms_eps=1e-6,
                        use_oneshot=force)
                dist.barrier()
                warm_stream = torch.cuda.Stream()
                warm_stream.wait_stream(torch.cuda.current_stream())
                with torch.cuda.stream(warm_stream):
                    for _ in range(10):
                        run()
                torch.cuda.current_stream().wait_stream(warm_stream)
                torch.cuda.synchronize()
                for actual, expected in [(residual_out, reference_residual), (norm_out, reference_norm)]:
                    torch.testing.assert_close(actual.cpu(), expected, atol=0.02, rtol=0.02)
                assert torch.equal(x, original_x) and torch.equal(residual, original_residual)
                max_residual_error = (residual_out.cpu().float()-reference_residual.float()).abs().max().item()
                max_norm_error = (norm_out.cpu().float()-reference_norm.float()).abs().max().item()
                graph = torch.cuda.CUDAGraph()
                dist.barrier()
                with torch.cuda.graph(graph):
                    for _ in range(config['graph_operations']):
                        run()
                samples = []
                for _ in range(5):
                    dist.barrier()
                    start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
                    start.record()
                    for _ in range(config['graph_replays_per_sample']):
                        graph.replay()
                    end.record()
                    end.synchronize()
                    samples.append(start.elapsed_time(end) * 1000 / config['graph_replays_per_sample'])
                torch.testing.assert_close(norm_out.cpu(), reference_norm, atol=0.02, rtol=0.02)
                assert torch.equal(x, original_x) and torch.equal(residual, original_residual)
                resolved = MNNVLAllreduceFusionStrategy.select_strategy(world, tokens, hidden, torch.bfloat16) if strategy == MNNVLAllreduceFusionStrategy.AUTO else strategy
                row = dict(tokens=tokens, strategy=name, resolved_strategy=resolved.name,
                           repetition=repetition, launch_with_pdl=launch_pdl, graph_us_samples=samples,
                           median_graph_us=statistics.median(samples), graph_operations=config['graph_operations'],
                           collective_us_samples=[v / config['graph_operations'] for v in samples],
                           median_collective_us=statistics.median(samples) / config['graph_operations'],
                           max_residual_abs_error=max_residual_error, max_norm_abs_error=max_norm_error,
                           local_numerical_check_passed=True, inputs_unchanged=True)
                rows.append(row)
                write_json(args.out / ('rank-' + str(rank) + '-results.json'), dict(metadata=metadata, points=rows, complete=False))
                if repetition == 0 and tokens == 54:
                    dist.barrier()
                    with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU, torch.profiler.ProfilerActivity.CUDA]) as profiler:
                        for _ in range(3):
                            graph.replay()
                        torch.cuda.synchronize()
                    trace = args.out / ('rank-' + str(rank) + '-' + name + '.trace.json')
                    profiler.export_chrome_trace(str(trace))
                    with trace.open('rb') as source, gzip.open(str(trace)+'.gz', 'wb') as target:
                        target.write(source.read())
                    trace.unlink()
                del graph
        del x, original_x, residual, original_residual, residual_out, norm_out, gamma
    dist.barrier()
    write_json(args.out / ('rank-' + str(rank) + '-results.json'), dict(metadata=metadata, points=rows, complete=True))
    workspace.destroy()
    dist.destroy_process_group()
    print('MICROBENCH_COMPLETE', rank, len(rows), flush=True)


if __name__ == '__main__':
    main()
