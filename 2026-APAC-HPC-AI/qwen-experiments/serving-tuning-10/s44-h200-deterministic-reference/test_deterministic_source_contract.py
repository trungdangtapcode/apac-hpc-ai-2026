from pathlib import Path
PIN=Path("/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/dp-attention-ep-feasibility-20261024/pinned-source/sgl-workspace/sglang/python/sglang/srt")
server=(PIN/"server_args.py").read_text(); overrides=(PIN/"arg_groups/overrides.py").read_text()
assert "enable_deterministic_inference: A[" in server and "Enable deterministic inference mode with batch invariant ops." in server
assert "_deterministic_sampling_backend" in server and "_deterministic_attention_backend" in server
assert 'return {"sampling_backend": "pytorch"}' in overrides
assert 'return {"flashinfer_allreduce_fusion_backend": None}' in overrides
assert 'backend = "fa3"' in overrides and 'os.environ["NCCL_ALGO"] = "allreduce:tree"' in server
worker=Path(__file__).with_name("worker.sh").read_text()
assert "--enable-deterministic-inference" in worker
assert "--flashinfer-allreduce-fusion-backend mnnvl" in worker
assert "--decode-attention-backend flashinfer" in worker
print("PINNED_DETERMINISM_SOURCE_CONTRACT_PASS; CPU/source evidence only")
