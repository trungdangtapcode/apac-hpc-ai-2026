# Full local MMLU-Pro comparison after the pilot

## Question and measured prior

The owner explicitly authorised research and actual quality measurement. The local pilot is below its predeclared point gate: reference 28371 = 104/128, candidate 28368 = 102/128, ratio 98.076923%, with zero request errors. We preserve this failure rather than infer a pass from unchanged weights. The full fixed test set is the next measurement; a small balanced pilot cannot stand in for all 12,032 questions or the organiser suite.

## Fixed protocol and native-load qualification

Keep the exact prepared 12,032 prompts, tokenizer/template, adaptive shot counts, greedy generation, 2,048 output cap, stop string and scoring policy. Invalid/error outputs stay in the denominator and no random guesses or post-result parser changes are allowed. Reference remains stock FP8 TP8/EP8 on each node, without the transport patch or explicit backend tuning. Candidate model workers, FP8/BF16 precision, P/D topology, transport patch and kernel flags remain the accepted configuration.

Full measurement uses concurrency 64 for both roles, the candidate's declared production request load. This is a new full-set load series; do not combine N16 pilot answers with N64 full-set answers. Eight deterministic row-modulo shards per role each contain 1,504 questions. Membership is fixed before inference, reference/candidate IDs match, and each role's eight shards are disjoint and exhaustive. Aggregate item-level correct counts over 12,032; never average shard ratios.

Both pilots completed 128 questions in about 83–84 seconds at N16, with mean output around 662–680 tokens. The candidate's earlier N64 AIPerf rate around 3k output tokens/s informs sizing only; it is not a measured throughput for long CoT. The first native-N64 reference/candidate pair must complete all 1,504 questions without errors/deadline skips before admitting the other fourteen shards. Their runtime, usage/finish reasons, parsing and raw outputs will validate or reject the duration forecast.

## Resource envelope and admission

The full phase has at most sixteen 16-H200/two-node allocations, each capped at the site's 17 minutes: **72.533333 GPU-hours maximum**, zero PBS SU. First-pair reservation is **9.066667 GPU-hours**; the other fourteen entries are prepared, not reserved or submitted until qualification. Prior pilot allocations used **4.213333 actual GPU-hours**, including the failed FP8 layout. The planned full-phase-plus-pilot maximum is **76.746667 GPU-hours**, not actual spending. This is a declared bounded stage within the owner's measurement request, not a new owner-wide quota or an inference of H100 spending authority.

Use the shared Slurm admission lock, definite receipts and maximum own active/pending cap 5. After first-pair qualification, keep up to five distinct remaining ready shards admitted as capacity permits. Preserve queue positions, failed and incomplete runs. Do not restart an unchanged failure blindly, cherry-pick successful answers or silently shrink the test denominator. A capacity/time failure is not an accuracy result; diagnose it and freeze any revised complete-coverage plan before further admission.

## Claims and preservation

The paired gate is candidate/reference full-set accuracy >=0.99, exact complete coverage and zero service errors for the local protocol. This is **local full MMLU-Pro evidence**, not a BTC-issued multi-task certificate or the organisers' unpublished reference. Record each role's correct/total, accuracy, per-category results, disagreement types, invalid/length-limited outputs, raw source hashes, actual configuration and costs. Preserve all truncations and errors. No causal kernel/transport attribution follows from the aggregate ratio.

Current ranked ZIP, slides and all HPC payloads stay untouched while measurement proceeds. No H100/PBS access, authentication, background Codex or schedules are started. Capture safe source, actual receipts and completed-run reviews in separate verified commits; exclude weights, private runtime homes and disposable caches.
