# Bounded hardware and server sampling

This implements the previously missing low-rate collector for **new derived jobs**. It is not a background Codex service. It starts as a child of each worker, samples at most every five seconds while the parent exists, and stops at a hard duration bound; the scheduler also owns its process group. No model import or external dependency is required.

Each role writes a separate JSONL file, preserving GPU UUID/index, activity percentages, sampled VRAM MiB, power W, temperature degrees C, SM/memory clocks MHz and P-state when nvidia-smi supports them. Unsupported strings remain explicit; failed/missing commands are not zeros. Node CPU jiffies, memory KiB and cumulative interface byte counters are included. Co-located roles see the same node counters: deduplicate by host before calculating deltas. Network interface counters are not NVLink/IB hardware bandwidth or proof of link saturation. GPU activity is not FLOP efficiency; memory activity is not occupied VRAM or percent of peak HBM bandwidth. No Xid, throttling-reason or per-process CPU health claim is made by these samples.

The collector reads only a whitelist of worker Prometheus counters on localhost. `--enable-metrics` is enabled only for observer-on controls/candidates. Startup connection failures remain visible; source and actual collected names determine counter availability. Missing whitelisted counters are not zeros. No raw request, credential, complete environment or arbitrary endpoint body is recorded.

`phase-marker.py` writes UTC epoch and monotonic timestamps around the client call. AIPerf's retained phase manifests define the actual warmup/scored intervals; the outer client markers do not substitute for them. Monotonic values align only within the same host. Record local UTC offset and inspect clock alignment before combining nodes; exclude startup/warmup/profile/drain when summarising the scored interval.

`check-local.py` validates a simulated selected GPU CSV, missing/invalid GPU data, real `/proc` reads, a local HTTP whitelist fixture, phase timestamp fields and the exact pinned scheduler skipper's interval-2 behavior. Six checks pass without a GPU. Seven extracted source files match both clusters' runtime images; see `source-validation.json`. Actual GPU sampling coverage and observer overhead remain **unverified until the submitted pilots complete**.

The paired plan measures observer-off versus observer-on overhead, then compares the candidate to an equally observed control. Preserve raw samples, phase manifests and pilot hashes. See [the full experiment plan](../research-followup-20261020-recv2/PLAN.md).

Primary definitions: [NVIDIA nvidia-smi](https://docs.nvidia.com/deploy/nvidia-smi/index.html), [SGLang observability](https://docs.sglang.ai/advanced_features/observability.html). Available counters and behavior are checked against the installed source, not assumed from current upstream docs.
