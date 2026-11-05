# Delivery recheck after the owner found another mismatch

## What the previous review missed

There were two active sources of confusion. The short scripts started at index zero while printed PPTX labels started at one. In addition, `VNUHCM - TripleU/AI_Task/logs/TALK_SCRIPT_EN.md` was an older script and had not been included in the previous review. Calling the entire delivery aligned was therefore incorrect.

## Files actually changed in this correction

- `reports/ai-final-report-20261030/TALK_SCRIPT_EN.md`: every main and spoken-backup heading now explicitly identifies its actual PPTX page.
- `reports/ai-final-report-20261030/TALK_SCRIPT_VI.md`: the same explicit page map.
- `VNUHCM - TripleU/AI_Task/logs/TALK_SCRIPT_EN.md`: replaced the stale script with the current English source; their bytes are identical.

No additional PPTX/PDF content was changed in this correction. The active deck already contains “17 layouts explored” on actual page 03. Actual page 02 is the contribution overview. Thus the zero-based script's index 2 maps to actual PPTX page 03. This is now stated in its heading rather than left for the presenter to infer.

## Three independent checks

1. **Actual page routing:** raw ZIP/XML relationships and a separate PPTX object reader agree on the presentation sequence. All twenty spoken sections in each language identify the correct physical page and title. Old unreferenced embedded slide parts are excluded.
2. **Content review:** a separate reviewer compared both source scripts and the packaged English script against all sixteen main slides, four spoken backups and the scatter image. Layout count, prefill/decode choices, matched controls, numerical approximations, quality versus SLA, axes, failure colours and limits of causal claims were checked. No remaining material mismatch was found in this scope.
3. **Exact delivery files:** the canonical user-facing PPTX and both companion PDFs were reopened. Forty bilingual section/page routes and selected numerical/text anchors match the actual PDF pages as well as the active PPTX. The packaged English script matches the source byte-for-byte. HPC package parts and eight PDF page renders remain unchanged. [Machine-readable receipt](DELIVERY_CHECK.json).

The detailed teaching guides were checked for their 34 title routes only; this is not a claim of rewriting their entire prose. Historical ZIPs and the older root-level deck are not claimed to match this revision. Coordinate PDF checks do not substitute for a live PowerPoint rehearsal.

Script bytes remain local and uncommitted under the owner's earlier instruction. This correction's audit, navigation map, validators, hashes and handoff are backed up separately.
