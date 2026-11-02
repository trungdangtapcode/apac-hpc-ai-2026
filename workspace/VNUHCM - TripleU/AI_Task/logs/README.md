# TripleU AI submission: native FP8 serving on 16 H200 GPUs

The Basic deliverable preserves the published Qwen FP8 model, BF16 KV and all
layers/experts. It supplies reconstruction instructions, the text transport patch,
one deployment-plus-official-benchmark job and the presentation. No model weights,
authentication material or disposable runtime cache are bundled.

## Complete portable verification

**Job 28197 completed 0:0 in 10 min 11 s** on two H200 nodes at N64. It measured
**3051.518173 good output tokens/s**, with **1881/1907 requests passing both
latency limits (98.636602%)**, zero errors/cancellations, both P/D semantic paths,
the original official client, corrected readers, performance gate and cleanup.
This reproduces the retained operating level; it is not a matched new speedup.
The earlier failed jobs remain in the historical evidence folders.

- [Reconstruct and run](../job_scripts/README.md).
- [Final AI report](FINAL_REPORT.md), [result review](acceptance-20261102/RESULTS.md)
  and [latest measured results](measured/latest-results.md).
- [English speaking script](TALK_SCRIPT_EN.md), [presentation plan](PRESENTATION_PLAN.md),
  [evidence cards](EVIDENCE_CARDS.md) and [technical Q&A](PANEL_QA.md).
- [Nine final H200 verification allocations](research-20261101/README.md) retain
  eight N64 observations and one N54 observation, with separate branch controls.

## Evaluation provenance

The 98.636602% value is joint request-latency success, not answer accuracy.
Model-quality evaluation follows organiser Q1 against its unchanged official FP8
reference. The submitted methods preserve the target model and precision; no
team full-set quality score or completed organiser review is claimed here.
The Q&A distinguishes source checks, local output screens and that evaluation.
H100 and H200 scores remain separate. The existing HPC payload is preserved.

The main deck contains 16 AI slides followed by eight HPC slides; 18 additional
AI slides are hidden backups. The combined talk is 15–20 minutes with a separate
10-minute Q&A. The AI rehearsal target leaves the agreed HPC speaking time.
