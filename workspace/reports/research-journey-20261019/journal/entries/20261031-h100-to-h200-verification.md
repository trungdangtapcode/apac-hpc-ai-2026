# Test transferability rather than compare unlike GPUs

Owner request, 31 October 2026 Vietnam time: after a panel question about H100
versus H200, verify useful H100 ideas on H200 and explain how many jobs suffice.
This resumes only this bounded AI scope after the reporting stop.

The evidence audit found no justification for filling four initial queue slots.
H100 222027/222028 tested FlashInfer versus FA3 decode at N54. FA3 lowered mean
TTFT 713.198502 to 594.276232 ms while increasing request-mean ITL 18.214406 to
18.987684 ms; good output throughput fell 2420.945479 to 2401.283565 tokens/s.
This is a tradeoff, not a H100 winner. CPU-envelope 222551/222552 gained only
0.289035% with mixed tails. Equal-TP EAGLE observations establish a functional
path, not full scored performance. Existing unchanged losing H200 branches stay
closed. A new H200 decode-attention comparison is a distinct hardware question;
H200 27077 concerned prefill attention.

The hypothesis is that the attention-backend tradeoff may depend on hardware and
the current serving operating point. Derive one fresh FlashInfer control and one
FA3 decode candidate from actual frozen H200 27376. Keep16 H200, N64, the pinned
runtime, source, precision, two TP4 prefills and TP8/EP8 decode, full workload,
semantic/KV/output gates and telemetry. Change one serving factor only. CPU
fixtures verify the backend gate accepts each intended configuration and rejects
wrong backend, altered capacity/dtype/prefill attention and missing rank evidence.
Synthetic altered logs are not new GPU evidence.

Start with two jobs, maximum 9.066667 GPU-hours and zero PBS SU. Only a valid gain
above 1% with acceptable tails qualifies a second independent pair, four total.
The scope does not revive background Codex, PBS spending or HPC work. Current
preparation and later actual receipts/results are linked below; no invented
speedup or official quality certification.

[Study plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-h100-attention-transfer-20261031/PLAN.md),
[H100 evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261020-0132/RESULTS.md),
[owner explanation](../../../../notes/ai-h100-to-h200-verification-20261031.md).

## Definite admission

At 2026-10-31T10:26:03.546470+07:00, actual scheduler receipts confirm **27777** FlashInfer control
and **27779** FA3 decode, each 16 H200 / two nodes / at most 17 minutes.
Both are Resources-pending in this observation, not measured results. The
shared Slurm admission lock protected the fresh own cap-five check, frozen
manifests and site/test-only validation. No dependency, cancellation, requeue,
H100 spending or HPC edit. Preparation was safely captured and pushed in
b0bbbd5a before actual submission. Retain this stage separately from later
terminal acceptance, interpretation and any conditional repeat.
