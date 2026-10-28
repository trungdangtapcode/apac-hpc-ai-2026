# AI submission and presentation update — 28 October 2026

The published team ZIP contains the same required Presentation, AI_Task and HPC_Task top-level directories. Presentation contains one PowerPoint: 32 updated AI slides followed by the existing eight HPC slides. The AI primary is now the replicated N64 configuration, replacing the stale N62 entry. The full HPC_Task payload and its presentation section remain byte-identical.

## Deliverables

- [Current PowerPoint](../../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx)
- [Complete team ZIP](../../VNUHCM%20-%20TripleU.zip)
- [40-page review PDF](TripleU_APAC2026_Presentation.pdf)
- [Presenter notes](PRESENTER_NOTES.md)
- [AI primary instructions](../../VNUHCM%20-%20TripleU/AI_Task/job_scripts/README.md)
- [Latest results, units and interpretation](../../VNUHCM%20-%20TripleU/AI_Task/logs/measured/latest-results.md)
- [Publication validation](publication-validation.json), [delivery validation](delivery-validation.json), [script checks](VALIDATION.json), [HPC preservation baseline](HPC_BEFORE.json)

The AI point uses 16 H200 on two nodes: two TP4 prefill workers with DeepGEMM, chunk 8192 and breakable prefill graphs, and one TP8/EP8 decode worker with HPC-Ops, FlashInfer, MNNVL and full decode graph sizes 1–64. It retains the official FP8 checkpoint with BF16 activation/KV, round-robin routing and fixed N64. There is no speculative decoding or dynamic tokenization in the selected primary. The portable entry calls the exact official closed-loop 4000/200, seed 2026, cold-prefix, 60/120/30 workload once, after independently validated semantic warmups on both P/D routes. The score gate rejects missing or failed raw data.

The talk records the three historical N64 full runs, mean 3044.400475 good output tokens/s, and a separate new native-runtime full observation at 3045.501509. It retains valid lower replay results and explains why this is not a causal runtime speedup. Larger chunks, the subthreshold N68 increase and the losing EAGLE3 screen are reported with their limits. Tokenizer experiments that timed out before AIPerf have no score. H100 remains a separate series. Official full-set accuracy at least 99% of reference remains UNKNOWN, and the updated portable entry has not received a separate GPU replay.

## What was verified

The staged package passed 591 targeted checks: setup, shell/Python syntax and hashes, exact official client arguments, semantic receipts and stale-token rejection, retained raw score-gate success and injected failure, configurable image/model paths and mock orchestration from a path containing spaces. Published scripts match that reviewed stage. Global package checksums and ZIP CRC/member hashes pass.

All 265 HPC_Task file hashes and modes are unchanged, and the old ZIP's HPC permissions/timestamps are preserved. Slides 33–40 keep all 68 transitive OOXML dependency parts byte-identical, including notes, layouts, themes and images. The review PDF's eight HPC pages render to identical pixels. The full deck has 40 distinct ambient background photographs, retaining the established theme and gradients. The PDF/previews use shared drawing coordinates rather than an Office renderer; visual inspection does not certify font substitution in another installation.

Six identical 227,995,065-byte generated inputs.json dataset copies are omitted from the compact delivery, saving 1,367,970,390 uncompressed bytes. Exact sizes and hashes are retained in AI_Task/logs/omitted-artifacts-20261028.json; original research artifacts remain preserved. Raw scored requests, input configuration, exports, key logs and source provenance remain included. No model weights, authentication state or disposable Python bytecode is packaged. The previous published delivery is preserved in the backup named by publication-validation.json. No organiser upload occurred.

## Rebuild and preservation

Use the pinned slides/requirements.txt with build_ai_slides_20261028.py, then merge_ai_update_20261028.py. The merger reads the retained inputs/combined-before-ai-update.pptx and protects the HPC closure. Prepare/validate the AI payload with prepare_ai_update_20261028.py and validate_ai_update_20261028.py; preparation replaces only its AI_Task stage and preserves sibling slide/audit files. Publish only after reviewing the exact staged artifacts with publish_ai_update_20261028.py. The publisher serializes with the shared publication lock and checks for concurrent changes.

The first staging helper version incorrectly removed the whole review directory; only regenerable unpublished slide/audit outputs were affected. Its scope guard was corrected, all affected outputs regenerated, and preservation verified before publication. A review ZIP briefly included repeated generated inputs and one disposable bytecode cache; the final publisher excludes both and reverified the compact delivery. Original research measurements and the existing HPC delivery were not altered by either staging correction.

Git captures retain scripts, reports, hashes and recovery metadata. Large PPTX/PDF/ZIP bytes use the sibling artifact store; a Git push does not upload those external object bytes. No background schedule or service was enabled.
