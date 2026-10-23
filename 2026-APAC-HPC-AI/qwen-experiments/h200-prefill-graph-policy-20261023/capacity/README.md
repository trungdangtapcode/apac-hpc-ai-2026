# H200 capacity and prefill graph policy log gate

This CPU-only gate checks the three serving roles in an H200 artifact directory before a benchmark is considered capacity-initialized:

- `prefill-0` and `prefill-1`: TP4, EP1, DeepGEMM MoE runner, BF16, chunk size 8192, and explicit `max_running_requests=64`.
- `decode-0`: TP8, EP8, HPC-Ops MoE runner, BF16, chunk size 8192, and explicit `max_running_requests=256`.
- All roles: EAGLE/speculative fields must be unset. Decode graph capture verification is handled by the separate graph gate.
- The requested prefill policy must agree across every role's resolved `ServerArgs` and resolved graph configuration.

SGLang's CLI does not define a literal `auto` graph backend. Here `--prefill-policy auto` means the default/unset `cuda_graph_backend_prefill=None` and `disable_prefill_cuda_graph=False` on every role. The pinned resolver then gives the Qwen prefill workers a resolved `breakable` backend, while the decode role resolves prefill graphs to `disabled` because its `disaggregation_mode='decode'` and no explicit backend overrides the role default. `--prefill-policy disabled` means `cuda_graph_backend_prefill='disabled'` on every role, `disable_prefill_cuda_graph=False`, and resolved backend `disabled` on each role. These role-specific runtime states express one common user policy; if a future runtime changes them, this gate fails for review instead of widening the accepted values.

For every role the gate requires a resolved `server_args=ServerArgs(...)` record and at least one initialized scheduler line containing both a positive `max_total_num_tokens` and `max_running_requests`. Every observed scheduler capacity must agree with its role's explicit ServerArgs and expected capacity; missing, malformed, defaulted, or contradictory evidence fails closed.

Run against an artifact directory whose root or descendants contain the role logs:

```sh
python3 capacity/audit_capacity.py --artdir /path/to/artifacts --prefill-policy auto
python3 capacity/audit_capacity.py --artdir /path/to/artifacts --prefill-policy disabled
```

The command writes a JSON report to stdout and exits nonzero on any error. CPU fixtures are synthetic parser tests only. They do not establish that the pending target jobs used the explicit capacities, initialized the schedulers, completed correctly, or achieved any performance result. In particular, source-only evidence and existing runtime fixtures cannot establish the current explicit 64/256 scheduler state until target logs exist.

## Source and runtime evidence

The pinned source snapshot is `qwen-experiments/h100-prefill-hpc-chunk-interaction-20261020/runtime-source/server-args/sgl-workspace/sglang/python/sglang/srt/server_args.py`, SHA-256 `79d9bbb61b429574e31e7a7e319831fcd129a83a475e6ffe2b7e8a5e8eb06b0f`. At lines 1815–1822, the prefill backend type allows `full`, `breakable`, `tc_piecewise`, or `disabled`; `auto` is not a backend literal. Lines 4309–4313 fold an explicitly selected prefill backend into the graph config. The graph config starts from defaults at line 4289. Lines 4212–4223 document an architecture-specific exception to the generic default. Most relevant, lines 4369–4375 disable the prefill graph on a decode disaggregation role when no backend was explicitly locked; this is why the auto treatment expects `breakable` on prefill workers and `disabled` on decode while retaining `None` in all three ServerArgs fields. The gate checks each resolved config and role mode from actual logs.

The retained H200 runtime example is `qwen-experiments/runs/25487/`. In `prefill-0.log:10`, `ServerArgs` records `max_running_requests=None`, `dtype='auto'`, `cuda_graph_backend_prefill=None`, `disable_prefill_cuda_graph=False`, and `disaggregation_mode='prefill'`; its resolved prefill config is `breakable`. The scheduler initialization receipt at `prefill-0.log:193` reports `max_running_requests=4096`. In `decode-0.log:11`, ServerArgs records `disaggregation_mode='decode'`, and its prefill graph resolves `disabled` through the source role rule. At `decode-0.log:226`, explicit and initialized decode capacity both report 256. These are historical examples of log syntax, not evidence for the pending 64/256 target. They show why the gate checks both ServerArgs and initialized scheduler receipts instead of trusting a launch script or a default.

Run the tests with:

```sh
python3 -m unittest -v test_audit_capacity.py
```
