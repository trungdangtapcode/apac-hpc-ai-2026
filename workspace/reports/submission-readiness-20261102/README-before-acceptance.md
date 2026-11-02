# Final submission audit — 2 November 2026

**New runtime finding — 2026-11-02T08:00:53.498588+07:00:** exact-entry job28194 failed before benchmark on a gateway readiness race. A qualified readiness-only repair has been submitted as28197; [current details](../../notes/ai-final-portable-acceptance-20261102.md). The static/integrity findings below remain scoped as such; the published original entry is not end-to-end accepted, and no new benchmark/quality pass is claimed. Do not submit the old ZIP as if this runtime defect were already repaired.

**Subsequent owner-authorised action:** [final exact-entry acceptance job 28194](../../notes/ai-final-portable-acceptance-20261102.md) has now been submitted; the audit-only no-job statement below describes its earlier timestamp. [Quality clarification](../../notes/ai-quality-threshold-clarification-20261102.md) explains that organiser-run accuracy pending is not a Basic pre-upload prohibition.

Checked **2026-11-02T07:23:42.778551+07:00, Vietnam time (UTC+7)**. **AI materials and package integrity pass the present checks. Full organiser acceptance and the combined two-task submission are not certified.** This audit finishes the authorised read-only/offline checks; it does not submit a GPU job, rebuild the release, alter HPC or upload to the organiser.

## Official rules checked again

The current official main commit is **b4df52907f5bbb9152ef6ae902c925fc79d54417**, matching the rules revision named in the packaged environment. Fresh exact rule snapshots and hashes are retained in [source metadata](official-rules/source.json).

Primary references: [Qwen task and addendum](https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/1.%20Qwen3%20AI%20Task%20Rules.md), [tier/scoring addendum](https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/README.md), and [combined presentation/HPC deliverables](https://github.com/hpcac/2026-APAC-HPC-AI/blob/b4df52907f5bbb9152ef6ae902c925fc79d54417/2.%20OpenFOAM%20HPC%20Task%20Rules.md).

## What is verified

| Requirement or artifact | Result and practical limit |
|---|---|
| Required AI materials | Build/reconstruction instructions and pinned shared-image/model references, a single Slurm deployment-plus-benchmark entry, submitted text patch, result exports/logs and presentation are present. The task's example directory names do not require renaming the team's chosen layout. |
| Model/precision | Published Qwen3-235B-A22B-Instruct-2507-FP8 target; native FP8 weights and BF16 activation/KV. No selected draft, requantisation, smaller replacement or intentional layer/expert skipping. This is configuration/source evidence, not official numerical-quality certification. |
| Serving topology | Two eight-GPU nodes; two TP4/EP1 prefills and one TP8/EP8 decode; declared N64. The official client targets the chat gateway. Full serving/client evidence exists in previous portable jobs, whose later reader failures remain explicit. |
| Official client command | Closed-loop; required tokenizer, requested 4000/200 with zero standard deviations; 12800 dataset entries; seed 2026; cold-prefix busting; greedy generation settings; unchanged 60/120/30 and TTFT/ITL thresholds; no added request-rate flag. |
| Context | Configured 8192, leaving 3992 beyond nominal input+output for template overhead. Existing serving completed actual requests; a fresh formal per-request rendered-token maximum was not measured here. No context-truncation shortcut is selected. |
| Same-computation stack patch | Q1 explicitly permits text-submitted stack patches that preserve computation. Request-scoped NIXL metadata is not automatically outside Basic, and no separate unpatched Basic is imposed by that wording. CPU range equivalence and actual P/D GPU operation support the stated scope; final output quality and organiser review remain separate. |
| Offline reconstruction | Exact copied setup/tokenizer/payload passes from a neutral path containing spaces. All 11 shell/Python syntax checks pass. No container/model launch or scheduler submission was performed. |
| Runtime assets | Both recorded image sizes and model metadata pass; shared paths resolve without private-home symlinks, directory modes permit traversal and all 24 indexed weight shards exist with other-read mode. Full image/weight bytes were not freshly rehashed; the real judge identity, ACLs and compute-node/container policy were not exercised. |
| Package integrity | ZIP CRC, duplicate/unsafe-path/symlink checks pass. Per-surface manifests and checksums independently validate. The ZIP has 2015 files; all AI bytes agree with the working folder. Scoped credential checks reported no finding. |
| Current presentation | PPTX folder/ZIP identities match; 42 total slides: 16 main AI, 18 hidden backups, eight preserved HPC slides. Main PDF 24 pages, full PDF 42; matching English/Vietnamese learning PDFs 109/104 pages. |
| Latest AI evidence | Nine final score exports and nine lossless compressed request exports verify. Eight jobs are N64 and 27781 is N54; branch controls are separate. No late candidate displaced the retained H200 recipe. |
| HPC preservation | 68 slide dependencies, eight slide contents, 277 folder files/modes and 265 ZIP files/member metadata preserved. The existing 13 differences remain intentional: 12 folder-only files and one differing decomposeParDict. Preservation is not HPC scientific validation. |

Details: [AI rule review](AI_RULE_CHECK.md), [delivery review](DELIVERY_CHECK.md), [offline check](OFFLINE_PREFLIGHT.json), [setup output](setup-check.log), [asset-access scope](ASSET_ACCESS.json).

## The remaining checks before saying “fully verified”

1. **Recommended: one final full run of the exact repaired portable AI entry.** Jobs 27136/27145 completed real P/D semantic checks and the official GPU client but failed in result postprocessing. CPU job 27152 verified repaired readers on their saved datasets. That is valuable evidence, but it is not a fresh successful whole allocation after repair. A final 16-H200/two-node run of the frozen packaged entry through scoring, summary/gate and cleanup would close this reproduction gap. This is a recommendation for confidence, not a newly invented extra organiser deliverable. No run is submitted under this audit-only request; broad research remains stopped.
2. **Official quality is still UNKNOWN.** The organisers perform the full-set ≥99%-of-reference evaluation and official rebuild/re-run. Local SLA, smoke 7/8 non-regression and retrieval 12/12 are not substitutes. Unknown organiser evaluation is not automatically a missing Basic file or a reason to fabricate a team reference score.
3. **Get the HPC owner's explicit final payload choice and scientific confirmation.** Both tasks require a Basic result. That worker must confirm official-platform 4-node scored evidence, 1/2/4-node scaling, required text inputs/preparation/runtime and Cd evidence for the chosen HPC snapshot. The AI worker does not certify or silently merge those files. The checked ZIP preserves the older reviewed HPC snapshot; the working folder has documented additional/different files.
4. **Perform the actual presentation test.** Open the PPTX in the real application, verify hidden backup navigation and the main PDF fallback, microphones/screen sharing and speaker handoff. Time the combined AI+HPC talk at 15–20 minutes, with 10 minutes Q&A separately, and rehearse the teacher's reasoning questions. Prepared scripts and a rendered PDF are not that human test.
5. **Confirm final upload logistics and receipt.** The actual final destination, assigned deadline/timezone and file-size/additional-file limits have not been supplied or verified. The ZIP is 148,233,835 bytes (about 148.23 MB / 141.37 MiB). Use the reviewed ZIP rather than recreating it from the divergent live folder. After any authorised upload, retain the received-file identity and organiser/portal receipt. No organiser upload was performed here.

## What has already been resolved since the older preflight

The 1 November morning preflight described a 40-slide deck, an obsolete packaged speaking plan and missing late-run coverage. Those material-version gaps were fixed by the later published 42-slide edition. They are not current blockers. The newer thinking-process/Q&A study companions intentionally remain outside the frozen submission ZIP; they are preparation aids, not a failed package synchronisation.

A reviewer initially over-interpreted custom stack patches as requiring an unpatched Basic and treated CPU geometry's scope limit as absence of any GPU evidence. The final review was corrected using explicit Q1 wording and actual P/D/GPU-client records. A private team home is not a hard-coded judge-account dependency when the ZIP is extracted in the evaluator's shared path. No home permissions, credentials or auth state were changed.

## Exact release to submit after the handoffs

- [Team ZIP](../../VNUHCM%20-%20TripleU.zip): `a0da31120fa6cb5d1c49bfbb693ca74af20610e5cf368f9c3cc18dd703c3659e`.
- [Presentation](../../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx): `1ba55e8007f0ef7796076a35e82a1afc372a706c13500b80fbf9b27d723a2195`.
- [Main PDF](../../submission-review/ai-final-update-20261101/TripleU_APAC2026_Main_Talk.pdf).
- [Study and Q&A route](../teacher-qa-preparation-20261101/README.md).

Safe Git checkpoints preserve the audit, source snapshots and recovery metadata. Pushing Git alone does not upload sibling-store large artifacts; the full local ZIP and other external objects still need their intended separate off-host transfer. This report does not claim that an upload or official scoring has happened.
