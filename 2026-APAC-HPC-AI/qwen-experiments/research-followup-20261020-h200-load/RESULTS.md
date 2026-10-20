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
