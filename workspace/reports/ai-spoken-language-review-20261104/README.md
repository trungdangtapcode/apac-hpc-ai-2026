# Spoken-language review of the AI scripts

The owner requested speech that is easy to deliver, rather than book-style prose. Both active short scripts were revised in place: `TALK_SCRIPT_EN.md` and `TALK_SCRIPT_VI.md` under `reports/ai-final-report-20261030`. They retain the same sixteen main slides, existing titles and owner-requested numbering 0–15. This revision does not align them to the different 78-slide root-level presentation. No PPTX, PDF, long learning guide, submission payload or HPC script changed.

## Delivery changes

| Previously awkward item | Main speaking version | Exact reference retained |
|---|---|---|
| TP4/EP1 and TP8/EP8 | Explain four GPUs per prefill worker and eight for decode | Full configuration table |
| chunk 8192 | The prefill settings shown here stay fixed | 8192 in reference table |
| Job 28197 | The complete packaged rerun | Job ID and exact score in reference table |
| 3051.518173 good output tokens/s | Just over three thousand good output tokens per second | Exact retained value in study material |
| 99.915433% retention, 12032 questions, 9452 vs9460 correct | About 99.9% of the reference score; over twelve thousand questions | Full counts and percentages in reference material |
| +0.083056% at N68 | Less than a tenth of a percent more goodput at sixty-eight | Exact change and load in reference material |
| +125.335 ms mean TTFT | Roughly a tenth of a second later | Exact delta retained; approximation is explicitly rough |
| 360-second warmup deadline | Six minutes | Exact same duration |

Long sentences and repeated roadmap wording were shortened. Core reasoning, comparison controls, the latency tradeoff and chart explanations remain. The NIXL passage also clarifies that both endpoints must be contiguous and partial-token slices keep separate entries. Names, full configuration values and scoring distinctions sit in study-only sections.

## Checks and limits

English main script: 1,349 whitespace-delimited spoken words; longest sentence 26 words. Vietnamese: 1,710 whitespace-delimited tokens; longest sentence 30. The scripts contain no long decimal literals, four-or-more-digit literals or compact TP/EP/N codes in their main spoken paragraphs. Earlier exact study sections are preserved. The new reference tables retain precise values and local-quality scope.

At an assumed 115–120 English words/minute plus one minute for pointing and transitions, the calculated duration is approximately 12:15–12:45. This is an estimate, not a timed rehearsal. Vietnamese whitespace counts do not share the same speech-rate interpretation.

## Capture boundary

The owner's earlier script-only no-commit instruction is preserved. The two revised scripts and their before copies in `local-before/` remain local and uncaptured; no script bytes or numbering changes are committed by this checkpoint. This review and its validation metadata are backed up separately. Script SHA-256 values in VALIDATION.json identify the local versions without claiming Git contains them.
