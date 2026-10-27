# Public organiser AI reference: H100 versus H200

Checked 2026-10-27T08:02:30.860729+00:00. This is a read-only answer to an owner question, not a takeover of AI research or a new benchmark. No AI payload, queue, budget or handoff was modified.

The public ASPIRE 2A+ application notes list a two-node, **16-H100** Qwen3-235B FP8 deployment: two TP4 prefill workers and two TP4/EP4 decode workers. Among the four published concurrency points, N32 is the highest passing latency-gate point: **1173.718122217179 good output tokens/s**, computed from the raw export's Goodput 5.868590611085894 requests/s times 200, with good-request fraction **0.9084065244667503**. PBS job **217989.pbs111**. N24 gives **1053.8215654287058 tokens/s**, fraction **0.9863429438543247**, job217990. N48 and N64 fail the 90% fraction gate. These are reference observations, not an official leaderboard, an exhaustive engine optimum or a full-set accuracy certificate.

[Official results and job/log links](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/3.2%20Qwen3%20Application%20Notes%20-%20ASPIRE%202A%2B.md#results). The retained raw-export parsing, hashes and pinned source are in [the 20 October review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/upstream-review-20261020/REPORT.md) and its `official-h100-reference.json`. Read those artifacts without modifying the AI worker's evidence.

The Firmus H200 application notes and script README checked today provide verified deployment examples, but no numerical benchmark table was found in those two documents. Do not relabel the H100 1173.718 result as an H200 reference. This limited search does not establish that no H200 result exists elsewhere. [Firmus script guide](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/3.1-firmus-scripts/README.md).

The official ranking unit is Goodput requests/s times 200; higher is better and the run separately needs at least 90% joint TTFT/ITL compliance. Keep platform, GPU count, workload and model-quality limitations attached to comparisons.
