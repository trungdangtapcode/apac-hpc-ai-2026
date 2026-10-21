# Competition scoring, two tasks and specialist prizes

Checked 2026-10-20T17:40:50.865371+00:00. This answers the owner's question about why a competition described as two tracks also has a combined score. Public upstream main resolved to `b4df52907f5bbb9152ef6ae902c925fc79d54417` by a fresh `git ls-remote`; no pull, reset or working-tree replacement occurred. The pinned documents below were inspected through the web tool. This is a rules clarification, not an official result or new experiment.

## Current interpretation after the registration followup

The current public form inspected on 20 October has no separate mandatory AI/HPC selection control. NCI's original recruitment post invites applicants to choose a track. The pinned README requires Basic results for both tasks. These statements do not establish which registration arrangement was accepted for this team; the original accepted proposal or an organiser clarification is still needed. Do not treat the initial two-task interpretation as proof that an AI-only entry was registered incorrectly. The detailed evidence, failed archival checks and corrections remain below.

## What the two tracks mean

The official [benchmarking page](https://www.hpcadvisorycouncil.com/events/2026/APAC-AI-HPC/benchmarking.php) calls OpenFOAM and Qwen two tracks. The more specific [README R2](https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/README.md#r2-three-tiers) nevertheless requires every team to supply a Basic result for each task. The [OpenFOAM presentation rules](https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/2.%20OpenFOAM%20HPC%20Task%20Rules.md#presentation-guidelines) specify one interview covering both, with separate presentation assessments.

Historical limitation of the initial review: this conclusion was based on the current README and did not inspect the registration page or recruitment messages. The registration followup below identifies conflicting public wording; do not treat the initial review as proof of what this team was required to choose when applying.

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

## Registration followup — 2026-10-20T17:45:15.788237+00:00

The owner asked whether entrants had to declare their track in advance, and explicitly requested no commit for this followup. No Git capture, staging, commit or push is performed for it. These local corrections are intentionally not yet backed up to the Git archive.

The accessible official [proposal submission form](https://www.hpcadvisorycouncil.com/events/2026/APAC-AI-HPC/register.php) has contact/institution/country fields, a PDF proposal upload and comments. It requires a team competition plan within the proposal. No separate required AI/HPC selection field or explicit instruction to declare a track is visible. This is the currently accessible page, not a verified archival copy of the form on the team's original registration date. The team's submitted PDF and acceptance correspondence have not been inspected.

An official [NCI recruitment post](https://www.linkedin.com/posts/national-computational-infrastructure_do-not-forget-to-register-before-the-deadline-activity-7462736799379922944-8uEO) advertising the 22 May 2026 deadline explicitly says “Choose your track” and lists HPC/OpenFOAM and AI/Qwen. This is primary evidence that recruitment messaging invited track choice. It does not establish a mandatory form field, what this team selected or how specialist/overall eligibility is handled.

There is therefore a real ambiguity between recruitment wording and current README R2/R5's requirement for both Basic submissions. Preserve both sources; do not resolve the conflict by assuming an exemption, assuming the team registered incorrectly, or claiming the current form proves the original process. The team's accepted proposal/correspondence or an organiser clarification would resolve the team-specific question. No organiser message was sent. Qwen-only work scope, empty HPC_Task and existing jobs are unchanged.

## Continued check: original recruitment post and static form fields — 2026-10-20T22:24:44.620178+00:00

A direct read of current registration HTML succeeded even though the web fetch was intermittently inaccessible. HTMLParser found one POST form to formmail_register.php and nine controls: name, email, university, country, phone, proposal file upload, comments, human check and image submit. There is no select control or track-named input. [Value-free structured observation](registration-form-fields-20261020.json). The page asks for a team competition plan in the PDF; it does not visibly instruct the applicant to declare AI/HPC. Static field inspection does not establish the historical form, server-side checks or contents of an accepted proposal.

The [original NCI recruitment post](https://www.linkedin.com/posts/national-computational-infrastructure_hpc-ai-supercomputing-activity-7460109698856370176-wxv-) was also inspected. It contains the same track-choice invitation and 22 May 2026 deadline as the later reminder already linked above. These are an original and a reminder of the same message, not two independent policy confirmations. The shortened registration link could not be resolved through the web tool, so its destination is not asserted.

Wayback CDX and archive.org snapshot-availability requests were inaccessible through the web tool. This failure does not show that historical snapshots do not exist. RIKEN's early support guidelines concern its own Japanese support programme and do not resolve whether this Vietnamese team could elect AI-only; they are not substituted for the organiser's registration rules. Targeted searches produced no further explicit primary-source AI-only eligibility or mandatory track-declaration rule.

Conclusion remains bounded: no mandatory advance track field is evident in the accessible official form; recruitment invited a choice; the current README requires both Basic results. Do not infer which promise governed this team's accepted entry or whether specialist awards permit incomplete overall submissions. A concise unsent clarification for the organisers is: At registration, NCI advertised a choice between HPC and AI. May a team submit only Qwen and remain eligible for the AI Special Prize, or are Basic results for both tasks mandatory even for specialist prizes? Was track selection required in the original proposal?

The owner-requested no-commit restriction continues. This observation file and local note continuation are intentionally not captured or pushed. No GPU job, scheduler query, credit change, submission material or organiser communication occurred.

## Preservation authorised — 2026-10-21T02:11:16.205433+00:00

On 21 October the owner explicitly requested a commit, then asked to record the findings. That later instruction supersedes the earlier no-commit restriction for this registration clarification. The dated 20 October no-commit accounts above remain historical. This checkpoint captures the existing local corrections, the value-free form observation, source references and journal entry using the actual current date. It does not re-fetch the form, resolve the eligibility conflict or claim new organiser confirmation. No messages, job submissions, queue/budget refresh, submission edits or authentication changes accompany this documentation checkpoint.

## Mandatory HPC clarification — 2026-10-21T09:55:09.406614+00:00

The owner asked directly whether HPC is compulsory after the Qwen package update.
A fresh web read of the official public README still explicitly requires a
Basic result for each task in R2 and repeats that requirement in R5:
https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/README.md#r2-three-tiers
https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/README.md#r5-work-already-done

The direct answer under the published rules is yes: Basic Qwen and Basic
OpenFOAM are both required. Bonus work is optional. The previously recorded
track-choice recruitment wording does not itself establish an exemption for
this team. No accepted proposal or organiser confirmation granting an AI-only
exception has been supplied. AI Special Prize eligibility for an AI-only
package remains unresolved.

Correction to how the delivered package should be described: the 21 October
update is a complete update of our Qwen materials, not a claim of a complete
two-task competition submission. HPC_Task is empty because of the owner's
explicit Qwen-only working scope, not because the organisers waived HPC. Do
not infer that a missing HPC entry merely loses 50 points or is accepted for
specialist awards. The official Need To Know page could not be fetched by the
web tool in this recheck; no new claim about its contents is made from that
failed request. Existing historical source observations remain dated.

This is a documentation clarification only. No submission material, GPU job,
budget reservation, authentication or background automation is changed.
