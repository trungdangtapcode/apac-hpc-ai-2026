# 21 October: isolate native KV descriptor mechanics before another full model

Recorded 2026-10-21T19:53:35.773650+00:00. Prospective milestone; no GPU result or reservation at writing.

## Question and prior evidence

The full EAGLE3 integration 223055 reached role readiness but its first actual
warmup failed a NIXL remote disconnect on nodes 019/031. The later metadata error
was downstream. Its shell marker falsely reported warmup success; independent
output checks correctly rejected HTTP500 and zero actual output IDs. The cheaper
223091 base transport gate subsequently completed 80 real bidirectional writes
with exact destination hashes on different nodes 040/035. This establishes base
peer registration and transport there, not the actual SGLang KV descriptor path.

## Hypothesis and controlled change

Exercise the exact pinned `_init_hetero_tp_prep_handle` and `send_kvcache_slice`
methods with noncontiguous pages, the actual common pointer selector, TP4-to-TP8
whole-head routes and 94/94, 94/95, 95/95 pointer layouts. Two physical GPU agents
represent virtual TP ranks. Twenty-four writes must match complete deterministic
GPU destination bytes, including untouched sentinels. No model is loaded and no
precision, native transport adapter or official output verifier is changed.

[Plan and scope](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-descriptor-probe-20261021/PLAN.md), [frozen validation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-descriptor-probe-20261021/validation.json),
[CPU native-method rehearsal](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-descriptor-probe-20261021/numpy-rehearsal.stdout).

## Preflight observations and corrections

CPU review repaired AST extraction, registered peer-name use and the distinction
between GQA route eligibility and the helper's offset calculation. Atomic marker
publication avoids partially written JSON. The semantic checker independently
recomputes expected hashes, rejecting even matching false recorded hashes.
Six CPU regression functions include 24 extracted-init cases and adversarial
missing-row, wrong-hash and swapped-route fixtures. An additional real-NumPy CPU
rehearsal executes all 24 init/send cases and the whole-head coalescing branch.
These are CPU Python checks, not an emulated GPU/backend pass.

## Resource decision and limits

Prospective ceiling: two H100 GPUs on two distinct nodes, at most ten minutes,
maximum 42.666667 SU. A fresh locked ledger/own GPU queue check is required before
one submission receipt. The 51000-SU internal cap and 13000-SU retained reserve
stay fixed. No HPC CPU query, job or ledger is involved.

The fixture registers one small aggregate buffer per logical rank and uses
uniform 256-byte strides. It cannot prove native large KV registration, actual
eight-rank collectives, EAGLE auxiliary/hidden-state exchange, bootstrap lifecycle
or the earlier failed physical node pair. Utilization/power/CPU-demand telemetry
is not collected. A pass only warrants inspecting native KV argument geometry
and adding semantic per-pair warmup receipts before a bounded full-model retry.
Failure requires a demonstrated repair rather than an unchanged retry. No
throughput or official accuracy result is claimed.
