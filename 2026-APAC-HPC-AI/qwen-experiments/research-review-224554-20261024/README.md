# R6 serial/concurrent transport review: job 224554

## Question and prior evidence

R6 tested whether initializing the two P-to-D paths serially would allow first semantic transfers to pass, followed by the same paths concurrently in the same allocation. The preceding R5 run had passed metadata checks but failed its first concurrent requests. R6 kept the workers and native NIXL patch fixed, replayed independent phase tokens/receipts, and intended to run concurrent traffic only after the serial phase passed.

## Terminal result

PBS job `224554.pbs111` finished `F`, exit status 1, stage-out status 1. It used 16 GPUs across `a2ap-dgx028` and `a2ap-dgx032`; PBS wall time was 564 seconds (9 minutes 24 seconds), against a 1,200-second maximum. The allocated wall-time estimate is `564 × 16 × 128 / 3600 = 320.853 SU`; the maximum reservation was `1,200 × 16 × 128 / 3600 = 682.667 SU`. These are estimates, not posted ledger charges.

## First failed phase and observed transport errors

All three roles became ready and the pre-warmup gate passed before either semantic request. The gate records 16 metadata receipts with matching role tensor names and widths, plus six loaded source reports for `conn.py` and `utils.py`. The controller then entered the **serial** phase at 13:29:02 UTC. That phase failed, and the controller stopped before concurrent traffic; no `concurrent_warmup_start` marker exists, the `after-serial-gate.json` is empty, and no independent serial success receipts were produced.

The P0-to-D request returned HTTP 500 with `NIXL_ERR_REMOTE_DISCONNECT`. The P1-to-D route also returned HTTP 500: the first response reported `NIXL_ERR_REMOTE_DISCONNECT`, followed by retry responses reporting `NIXL_ERR_NOT_FOUND`. The transfer observer records for P1 include `nixlNotFoundError` exceptions while sending KV slices. P0's observer records a returned NIXL transfer handle, but the source marker explicitly says that return is not proof of transfer completion. These records identify the failing phase and API outcomes; they do not establish the lower-level cause.

No P/D semantic receipt passed. This run therefore does not show that serial initialization repaired first-transfer behavior, and it cannot decide whether concurrent follow-on traffic would pass after successful serial initialization. It produced no EAGLE token comparison, AIPerf score or model-quality result.

## Evidence and limits

The retained terminal qstat and PBS joined output show the scheduler result and job wrapper output. The run archive preserves phase markers, all 16 role metadata receipts, source-module reports, P/D send markers, failed semantic responses, router logs, worker locality launch observations, and bounded telemetry. The observed worker roles were prefill-0 and prefill-1 on `a2ap-dgx028`, and decode-0 on `a2ap-dgx032`. The two prefill workers had separate router endpoints. Worker-locality launch captures exist, but their state is `WAITING_FOR_CAPTURE`; those files do not establish the actual worker processes' locality. Resource samples are diagnostic observations, not evidence of a transport cause.

The R6 request context states `authentication_material: none`. Raw artifacts and submission sources remain unchanged at their source paths. No authentication material or tensor payload was collected in this review.

## Next decision

Treat the serial-first hypothesis as **not confirmed**: the serial phase itself failed. A follow-up should first address or instrument the P0 remote-disconnect and P1 KV-send `nixlNotFoundError` paths, with receipts that prove transfer completion rather than merely handle return. Do not spend on the planned concurrency contrast until both serial semantic receipts pass independently. Any later pass remains local evidence for that exact worker/node allocation, not proof of a general NIXL initialization cause.

## Preserved artifacts

- `collected/raw-run.tar.gz`: complete compact run directory archive, retaining remote relative paths.
- `collected/qstat-224554.txt`: terminal PBS accounting and stage-out fields.
- `collected/pbs-joined-output.txt`: PBS stdout/stderr (joined by PBS).
- `collected/SHA256SUMS` and `collected/ARCHIVE_SHA256`: collected-file and archive integrity records.
- `REVIEW.json`: machine-readable terminal, phase and failure summary.
