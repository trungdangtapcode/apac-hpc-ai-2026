# Native bytes pass; login-shell failure isolated

**224155.pbs111 is terminal F / exit 1**, 262 seconds, posted charge **18.631 SU**. The new independent exit gate correctly rejects the failed job. Do not relabel it passing because one subgate succeeds.

## What the actual process boundaries show

Both native Python children finish and are fully waited with **return 0**, no timeout. Both Singularity invocations also return 0, and private temporary-directory deletion returns 0. Yet both node EXIT traps receive/record final 1; PBS reports Exit_status 1 and Stageout_status 1. The outer pbsdsh return remains 0 even though its task log reports exit 1. Parent batch exit is 1 because the strict head exit gate rejects these node records. This localizes the discrepancy outside the completed native Python/container computation in this allocation.

The independently replayed byte proof passes again on 037/039: 190 regions of 76,132,096 bytes per GPU, total 14,465,098,240 bytes registered each; 380 selected region/page payloads / 97,280 bytes; 14,465,000,960 untouched destination bytes GPU-scanned; independent source preservation; ten host auxiliary spans totaling 933,888 bytes. Complete semantic rank receipts arrive by T0+218.225 s. This is a second physical pair, not a serving performance result. Runtime/source identities and actual raw evidence hashes are retained.

## Controlled CPU isolation

On the same AI login service, a strict minimal script explicitly executes exit 0. A nonlogin Bash returns 0 and its trap receives 0; /bin/bash -l returns 1 and its trap receives 1. A first isolated-home test without errexit does not reproduce the failure, and that negative result is retained. Adding an eight-case factorial test identifies the necessary combination: **login shell + set-e/errexit + console-cleanup logout code**. Empty HOME, nonlogin mode or no errexit each returns 0. Only the full combination returns 1. The actual account logout's noncomment commands match the public clear_console-only test case; its bytes are hashed, not copied into research artifacts. Tests use private temporary HOME directories and do not alter user startup/logout files.

This establishes a real batch-launcher bug consistent with the process receipts. It does not prove that all historical failures share this cause, and specifically does not explain the separate full-serving 223055 NIXL remote disconnect. Do not disable all error checks or change the account's shared logout file. Derive a nonlogin batch/node launcher, explicitly initialize the modules it needs, retain set-e and every independent data/exit gate, then run one bounded confirmation.

## Inspection and limits

Both rank phase samples include RSS and CUDA allocator/free/total bytes. Native child runtime is approximately 34–35s while batch-relative semantic completion is 218.225 s, so the surrounding container/startup interval dominates this diagnostic; it is not a model bottleneck. The allocator/process maxima are retained in REVIEW.json. Scheduler GPU counters again conflict with allocation/duration; they do not establish zero utilization or healthy hardware. No continuous hardware sampler, serving queue, request tail latency or model-output measurements were collected.

The native reference-lifetime check is still only an in-function observation; clean child return does not certify every deregistration or storage-lifetime invariant. Whole-buffer auxiliary transfers still do not verify native request-slot widths or the actual full model's destination layout. Source-only auxiliary layout work is separate and must not be promoted into runtime proof.

Fresh selected credit at 15:42 UTC uniquely posts 18.631 SU: Used 46484.545 / Balance 17515.455 / In Doubt 0 / outstanding maxima 0 / internal headroom 4515.455 SU. The original job remains failed; accounting success does not change that. The unchanged 51000 cap and 13000 reserve remain in force.

[Exact byte replay](independent-byte-replay.json), [exact exit replay](independent-exit-replay.json), [verified eight-case CPU reproduction](reproduction-verified.json), [reproducer](reproduce-login-exit.py), [raw evidence manifest](collected/evidence-sha256.json), [cost reconciliation](RECONCILIATION.json).
