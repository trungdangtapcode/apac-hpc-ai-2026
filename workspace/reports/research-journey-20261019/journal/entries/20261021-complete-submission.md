# Complete N62 submission and semantic replay gate — 21 October 2026

**Question and prior evidence.** The owner requested continued improvement and
an update to the whole submission. Inspection found a material mismatch: the
32-slide presentation described H200 24915/N62, but the portable primary job
still replayed historical 22415/N48. Its old configuration was valid historical
evidence, not the current selected deployment. Native integration 222752 had
also demonstrated why scheduler exit 0 alone cannot establish a useful result.
The owner now explicitly authorised package edits; the old no-edit restriction
is superseded. Qwen-only scope and empty HPC_Task remain unchanged.

**Change and control.** The submission is derived from the reviewed H200
24915 payload: two TP4/EP1 prefills and TP8/EP8 decode on 16 H200, DeepGEMM
prefill/chunk8192, HPC-Ops decode, FlashInfer decode attention, MNNVL and dense
1–64 decode graph sizes, round-robin gateway, published FP8 target and BF16 KV.
Worker, placement, warmup and patched NIXL source match the measured source
bytes. Only portable paths, one-point orchestration and the post-client gate
are adapted. No speculative draft or failed optimization is promoted. The
official command stays identical to pinned upstream
b4df52907f5bbb9152ef6ae902c925fc79d54417, fetched and inspected on this turn.
The rule requires a reconstructible environment, one deployment-plus-benchmark
Slurm/PBS job and slides; its example layout is not a mandatory replacement for
the owner's three-directory team format.

**Measurement and validation.** This milestone adds no GPU measurement or
reservation. The actual primary shell runs under a bounded mock from a path
with spaces. The mock replays retained measured artifacts so that the real
post-client semantic gate is exercised, not replaced. All 264 checks pass,
including exact official arguments, layout/patch checks and raw-source hashes.
Missing artifacts and an injected raw request error both fail closed. The
post-client gate verifies scored completion, zero errors/cancellations,
raw request counts and joint SLA against the canonical export; score remains
exported goodput.avg*200. This is not organiser full-set accuracy or proof that
the adapted portable entry has been GPU-replayed.

**Retained results and interpretation.** H200 24915 remains 3022.034919 good
output tokens/s, 15.110174596 good requests/s, 1860/1884 good requests,
98.726115% joint SLA, mean TTFT 1022.927941 ms, mean ITL 14.971161 ms, zero errors
or cancellations. Its independent N62 repeat 24962 is pending. The N60 treatment
repeats at 2990.150791 and 2989.174711 good output tokens/s. Fresh N62 control
24914 is 2890.878; the observed kernel interaction gain is 4.536934%, not a new
packaging gain. H100 222048 stays separate at 2433.019859 good output tokens/s,
98.687664% joint SLA, N54. The package includes these canonical exports and raw
request/role/client evidence, plus exact source provenance and historical N48
evidence. Large generated inputs are hash-indexed rather than bundled.

**Inspection beyond score.** The H200 review retains TTFT p99 3466.927 ms,
4505.927 ms maximum, ITL p99 15.692 ms and 24 TTFT failures. Role queue/KV and
post-score profile summaries are included with phase-coverage limits. Missing
continuous GPU/CPU/power/network telemetry is explicitly unknown; aggregate
kernel durations are not utilization or critical-path speedups. Later matched
CPU envelopes improve only 0.289035% against a 1% gate; reverse startup prefetch
saves 9.836066% against 10%. Those methods remain closed unchanged. EAGLE3
222763 failed native draft normalization, 222769 reproduces the dtype cause and
validates a BF16 layer graph repair; no speculative throughput is established.

**Delivery.** All 32 English slides, notes and existing distinct backgrounds/
gradients are retained, with current H100 and EAGLE3 findings. All 116 frozen
source hashes, structural bounds, background embeddings, package checksums and
ZIP CRC pass. The overview and updated EAGLE3 slide were visually inspected;
PDF/previews are shared-coordinate renders rather than Office renders.
The 50,207,688-byte ZIP and full folder replace the old delivery after preserving
it under submission-archive/before-full-update-20261021T084937Z. No organiser
upload occurs. HPC_Task has no files. The official full-set >=99%-reference
accuracy requirement and final organiser re-verification remain open.

**Actual scheduler and next decision.** At the linked 21 October 08:50:37 UTC
snapshot, H200 24928/24962/24964/24965/25051 are all PD/Resources. Preserve all
five queue positions; no sixth job. The local VPN wrapper finds no live session,
so 222780.pbs111 cannot be queried or collected. Its earlier running state is
historical. No authentication restart or new DUO is triggered. Until live PBS
access returns, preserve the full outstanding reservation and do not infer a
terminal charge or refresh budget by guesswork. On access recovery, collect
and inspect actual full-PD graphs, state/transport, memory and output IDs first.
Only a passing useful candidate proceeds to the existing matched short N54
screen and prospective 3% gate; no blind full-score retry. Available work in this
turn improves reproducibility and result validity while occupied queue slots
and absent remote access prevent a justified new submission.

**Preservation.** Separate small source and validation checkpoints were pushed
as 7396356 and 64230ed before full delivery. The complete publication/notes are
captured in the following checkpoint. Large presentation/raw objects remain
in the sibling artifact store with checksummed manifests; Git push alone does
not upload those bytes. Preserve the raw submitted evidence and prior delivery.
See the [delivery note](../../../../notes/submission-update-20261021.md) and
[review directory](../../../../submission-review/full-update-2026-10-21/).
