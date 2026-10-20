# Competition scoring, two tasks and specialist prizes

Checked 2026-10-20T17:40:50.865371+00:00. This answers the owner's question about why a competition described as two tracks also has a combined score. Public upstream main resolved to `b4df52907f5bbb9152ef6ae902c925fc79d54417` by a fresh `git ls-remote`; no pull, reset or working-tree replacement occurred. The pinned documents below were inspected through the web tool. This is a rules clarification, not an official result or new experiment.

## What the two tracks mean

The official [benchmarking page](https://www.hpcadvisorycouncil.com/events/2026/APAC-AI-HPC/benchmarking.php) calls OpenFOAM and Qwen two tracks. The more specific [README R2](https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/README.md#r2-three-tiers) nevertheless requires every team to supply a Basic result for each task. The [OpenFOAM presentation rules](https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/2.%20OpenFOAM%20HPC%20Task%20Rules.md#presentation-guidelines) specify one interview covering both, with separate presentation assessments.

Therefore, two subject areas do not establish two independent, optional registration divisions. The reviewed public rules do not grant a Qwen-only exemption. If an organiser has given this team a private exemption, it would need its own evidence; none is established by this review.

## Published point allocation

The September 25 addendum [README R4](https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/README.md#r4-scoring) supersedes the earlier 60% presentation / 40% performance wording.

| Component | Qwen AI | OpenFOAM HPC | Arithmetic sum |
|---|---:|---:|---:|
| Judges: Basic work | 20 | 20 | 40 |
| Judges: Bonus work | 15 | 15 | 30 |
| Performance and organiser re-verification | 15 | 15 | 30 |
| Maximum per task | 50 | 50 | 100 |

Each task is thus 70% judged work and 30% performance/re-verification. The 100-point ceiling follows from adding the two published 50-point task allocations. The reviewed pages do not separately specify every overall ranking conversion, tie-break or award-selection detail; this arithmetic is not an invented full ranking algorithm.

Basic means a permitted reproducible deployment/result that the organisers re-run. Its judged points assess the work and explanation; merely launching the official example does not automatically earn all 20 points. Bonus is optional and can reward careful Basic tuning as well as justified experiments. It does not require a separate experimental engine or a speculative technique, and it never replaces the required Basic result. Strong, well-explained failed experiments may still receive recognition; no particular award of points is guaranteed.

## What the performance component measures

- **Qwen:** good output tokens/s, calculated as exported AIPerf goodput in requests/s multiplied by 200. Requests qualify jointly at TTFT at most 3000 ms and request-mean ITL at most 20 ms; the qualifying fraction must reach 0.90, including errors in its denominator. Model correctness/quality and the other deployment rules remain separate requirements. [Qwen rules and addendum](https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/1.%20Qwen3%20AI%20Task%20Rules.md).
- **OpenFOAM:** the four-node `Average wall-clock time per time step`, in seconds per step, with lower values better. One- and two-node runs support scaling analysis. [OpenFOAM task](https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/2.%20OpenFOAM%20HPC%20Task%20Rules.md).
- Platforms are assessed separately; raw H100/H200 throughput or Gadi/ASPIRE timings must not be treated as one directly comparable hardware ranking.
- README R4 also replaces the old Qwen zero-performance wording: a re-run below the fraction gate or reference performance is assigned the reference deployment's score. This is not permission to omit a Basic submission or bypass the official quality checks. R4 names Firmus script 07; the newer Common Baselines page shows a script 09 H200 reference. This review does not silently equate those deployments or resolve their different reference roles.

The reviewed sources give no explicit mathematical curve converting a measured throughput/time into the 15 performance points. Consequently, a local result such as 3022 good output tokens/s cannot yet be converted into an exact contest point total. Neither a baseline-normalized percentage nor an assumed winner-takes-15 rule should be invented.

## Awards and what remains unknown

The official [overview](https://www.hpcadvisorycouncil.com/events/2026/APAC-AI-HPC/) lists First, Second, Third and Merit awards, plus **AI Special Prize** and **HPC Special Prize**. Thus there are specialist awards in addition to the main awards. The reviewed public pages do not specify a separate application route, a numerical specialist-prize formula, or permission for a team submitting only one task to ignore the Basic requirement for the other. Specialist award eligibility for an incomplete package remains unconfirmed.

The [Need To Know rules](https://www.hpcadvisorycouncil.com/events/2026/APAC-AI-HPC/need-to-know.php) also reserve the organiser's ability to disqualify incomplete task participation. Do not describe omitting HPC as a guaranteed safe 50-point ceiling; completeness and eligibility are a separate issue.

## Correction for our workspace

Our active work is Qwen-only by the owner's explicit scope. Keeping HPC_Task empty is a workspace instruction; it is **not evidence of an organiser exemption**. Any earlier implication that focusing this assistant on Qwen means the competition itself lets a team select only AI should be treated as unsupported and superseded by this clarification. No submission folder, slide, HPC script, scheduler job, budget, authentication state or automation was changed for this question.

For any organiser question, the unresolved points are the exact performance-to-points conversion, overall tie-breaking and AI Special Prize eligibility for a Qwen-only team. No message was sent to the organisers.
