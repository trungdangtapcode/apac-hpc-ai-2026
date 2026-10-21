# Complete Qwen submission update — 21 October 2026

The owner explicitly authorised updating the whole submission, not only its
slides. This supersedes the earlier no-package-edit restriction. The delivery
is now consistent: its primary script, configuration, build method, evidence,
results table and presentation describe the reviewed H200 N62 configuration.
The previous N48 package is historical and preserved, not silently overwritten.

- [Submission folder](../VNUHCM%20-%20TripleU/)
- [Submission ZIP](../VNUHCM%20-%20TripleU.zip)
- [Deployment instructions](../VNUHCM%20-%20TripleU/AI_Task/job_scripts/README.md)
- [Results, units and evidence limits](../VNUHCM%20-%20TripleU/AI_Task/logs/README.md)
- [Review PDF](../submission-review/full-update-2026-10-21/TripleU_APAC2026_Presentation.pdf)
- [Publication validation](../submission-review/full-update-2026-10-21/publication-validation.json)
- [Research milestone](../reports/research-journey-20261019/journal/entries/20261021-complete-submission.md)

The three top-level directories remain Presentation, AI_Task and HPC_Task.
The Presentation directory contains the PPTX only; HPC_Task/job_scripts and
HPC_Task/logs remain empty. There is one primary Slurm entry in AI_Task/job_scripts.
Frozen historical job scripts under logs are evidence, not additional entries.
No organiser upload has been made.

## What changed

The primary point changes from historical job 22415/N48 to reviewed job 24915/N62:
two TP4/EP1 prefills, TP8/EP8 decode, DeepGEMM prefill/chunk8192, HPC-Ops decode,
FlashInfer decode attention, MNNVL and round-robin routing on 16 H200. The official
FP8 target, BF16 KV and unchanged request-scoped NIXL patch are retained.
The official command still runs once, after deployment, in the same allocation.
No EAGLE3 draft is used in this primary submission.

The software setup includes image/model metadata hashes, pinned tokenizer,
versions, text transport patch and instructions for a fresh account. The new
post-client gate verifies complete raw requests, zero errors/cancellations,
matching canonical counts and joint SLA. Missing or inconsistent artifacts make
the job fail even if a client or scheduler exit code alone would look successful.
It does not change benchmark traffic or infer goodput by dividing by 120.

Raw recent H200 exports, JSONL requests, frozen payloads and role/router logs
cover the N60 control/repeats and N62 control/candidate. The H100 best result has
its own labelled evidence folder. Large generated input captures are omitted
with hashes/sizes; no weights, runtime caches or authentication are bundled.
Profile summaries and research reviews preserve negative outcomes and telemetry
limits. Original raw evidence is unchanged. The 32 English slides retain the
existing theme, gradients and 32 distinct photographs, with current H100 and
EAGLE3/CPU/startup findings.

## Verification and remaining gates

All 264 component checks pass: actual portable shell orchestration under a mock
from a path containing spaces, exact pinned official AIPerf arguments, worker
layout and patch hash, source-evidence hashes, and the real post-client gate
using retained measured artifacts. A missing-artifact case and injected raw
request failure both fail closed. This is not a new GPU run. The portable entry
point has not been separately GPU-replayed.

All 116 frozen presentation source hashes, 32 embedded distinct backgrounds,
English slide text/notes, text-box bounds, native gradients, package file hashes
and ZIP CRC/contents pass. The overview and changed EAGLE3 slide were visually
inspected. PDF/previews share drawing coordinates with the PPTX; they are not
Office renders and cannot certify font substitution on another machine.

H200 24915 remains a single N62 observation at 3022.034919 good output tokens/s;
its independent repeat 24962 is pending. N60 repeats at 2990.150791 and 2989.174711.
H100 222048 is separately 2433.019859. Official full-set accuracy >=99% of reference
and organiser re-verification remain unverified; neither SLA nor tiny output
checks prove them. No new performance improvement is claimed from packaging.

Fresh queue snapshot is linked in the review directory. All five H200 slots
are occupied by pending jobs, now showing Resources. The local VPN wrapper
found no live session, so 222780.pbs111 could not be queried or collected; its
last running snapshot is historical, not its current status. No new DUO/auth,
VPN replacement, GPU reservation or background automation was started.

setup.sh --check also passes against the actual shared image sizes, model metadata,
offline tokenizer and payload hashes. Full image hashing was not repeated.

The previous delivery is preserved in
submission-archive/before-full-update-20261021T084937Z. New ZIP SHA256:
5a05d69da175c7ed974e2db0d7fa937913b36c1102ae0fab18bd0c07e4467d62.
The ZIP is 50207688 bytes. Git captures manifests for large objects; the sibling
artifact store still needs a separate off-host copy, since a Git push does not
upload its bytes.
