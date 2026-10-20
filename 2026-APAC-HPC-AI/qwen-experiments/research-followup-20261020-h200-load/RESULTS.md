# H200 load followup submission receipts

Submitted four source-gated full-protocol trials after review of the five completed jobs:

| Job | N | Configuration and decision answered |
|---|---:|---|
| 24912 | 60 | Fresh auto-decode control for the new N60 incumbent |
| 24913 | 60 | Independent HPC-Ops decode repeat of 24738 = 2990.151 |
| 24914 | 62 | Fresh auto-decode control for the next runner comparison |
| 24915 | 62 | HPC-Ops decode at one higher load, then separate post-score profile |

All four were pending Resources at the first progress check; no new measurements yet. The fixed 4000/200 and 60/120/30 protocol, model precision, BF16 KV, DeepGEMM prefill chunk8192, MNNVL/FlashInfer decode, transport and output checks are retained. [Hypothesis, evidence and stopping rules](PLAN.md). Exact frozen hashes, syntax checks and definite sbatch receipts are preserved beside this report.

Compare 24913 with 24912 at N60 and prior HPC-Ops N60 24738. Compare 24915 with 24914 at N62 and the passing HPC-Ops N60 region; do not use a different load/platform as a matched control. Profile follows scoring. Candidate runs require full local acceptance and a useful gain needs independent repetition before promotion. Official accuracy remains unverified.

The shared registry marks five preceding jobs measured only after full local review; terminal status alone does not establish acceptance. At most five active H200 jobs, four used here. No extra N64 load, submission/slide promotion or AI schedule is implied.

## First completed fresh control — 20 October 2026, 00:51 UTC

Job **24912**, auto decode at N60, passes the complete local raw protocol, joint SLA, output/runtime and long-context gates: **2838.852531 good output tokens/s**, joint SLA fraction **0.987598647**, mean TTFT **822.292287 ms**, mean ITL **16.578515 ms**. Core batch completed with exit 0; cancelled auxiliary worker steps are cleanup, not failed scored requests. The terminal file manifest preserves evidence hashes.

The earlier HPC-Ops N60 observation 24738 = 2990.150791 is 5.33% above this new control. That is a preliminary cross-deployment comparison, not an independently reproduced treatment gain. **24913** remains the required HPC-Ops repeat; 24914/24915 remain the matched N62 comparison. At 00:51 UTC these three jobs were pending for Resources. No automatic N64 expansion follows from the control alone.

[24912 full review](24912-review.json), [terminal accounting](slurm-accounting.psv), [review program](review-slurm.py). Official full-set accuracy remains unverified.
