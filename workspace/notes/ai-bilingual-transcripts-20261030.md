# Bilingual slide learning transcripts

Prepared 30 October 2026, Vietnam time (UTC+7). Research remains stopped. The owner explicitly requested one Vietnamese and one English Markdown transcript, including each slide's purpose, notation, axes, units, colors, tradeoffs and a script they can explain themselves.

The [Vietnamese guide](../reports/ai-final-report-20261030/TRANSCRIPT_VI.md) and [English guide](../reports/ai-final-report-20261030/TRANSCRIPT_EN.md) cover the frozen 40-slide presentation: 24 main AI slides, eight AI backup slides and eight existing HPC slides. These are proposed scripts and explanations, not a verbatim recording of an already delivered talk. The 15–20 minute AI allowance applies to a rehearsed selection, not all explanatory text or the independent HPC segment.

This is an explicit, narrow exception to the English-only artifact preference for the requested Vietnamese guide and its bilingual generation data. Code, other reports and submission materials remain English. The HPC section is explained read-only from the existing deck; its 23 October scheduler snapshots are historical and no later HPC result is invented or certified.

Each slide separates purpose, visual description, terms, reading instructions, observation, hypothesis, supported conclusion, unknowns, spoken script, caution and transition. Color meanings are local: for example, slide 15's orange points are latency failures, whereas slide 10's orange bars mark later historical milestones. One dot on slide 15 is a request; its axes are TTFT in ms and per-request mean ITL in ms. Neither color nor point size encodes a GPU, topology or token count.

The guide is bound to the current PPTX SHA-256 through the extracted source and renderer checks. It explains measurement limits, including mixed historical configurations, latency/goodput tradeoffs, unverified official accuracy, original failed portable replay jobs and independent HPC evidence limits. Images are linked for side-by-side study.

No presentation, ZIP, HPC payload, scheduler, VPN state or budget is changed. No new research, authentication or organiser upload is performed. Retain source JSON, reviewed per-slide bilingual parts, the renderer and validation alongside the two guides so they can be checked when the presentation changes. Safe files are explicitly captured, screened, committed and pushed; the external large-artifact store is not uploaded by Git.

## Correction after presenter feedback

The initial guide used undefined phrases such as “reviewed local full pass” and spent space describing obvious decoration. The owner explicitly rejected that approach. “Local” described team-run validation on the assigned compute cluster; it did not mean a laptop, the login node, one compute node, or organiser validation. The revised guides use that concrete wording and define full protocol, implemented checks, control/candidate, repeat, useful-gain threshold, failed-job score recovery and official quality separately before the slide scripts.

Every slide now emphasizes technical interpretation: what the comparison means, why the decision follows, and what measurement would be needed to establish a cause. Irrelevant descriptions of background photographs, typography and number placement are removed. Actual data encodings, including axes, units, dot meanings and bar colors, remain explained. New terms must be explained where they matter rather than merely translated into equally opaque jargon. The original version remains historical in Git; scientific observations and the presentation itself are unchanged.

## Quick spoken briefs

The owner additionally requested a 10–20 second spoken brief at the beginning of every slide, above its purpose section, in both Markdown files. All 40 slides now have one: main message, a standout number or concrete configuration, and the decision or essential qualification. Necessary terms are explained within the short script; for example, repeated means rerunning the benchmark to check reproducibility, rather than simply appending the unexplained label to a score.

The Vietnamese heading is “Nói nhanh · 10–20 giây”; the English heading is “Quick brief · 10–20 seconds.” The timing is an approximate rehearsal target and is not claimed to have been recorded with a speaker. Detailed explanations remain below. The renderer verifies 40 briefs in each language, bounded length and placement before the purpose. During the same review, accidental Vietnamese replacement fragments in several older English explanations were corrected and a language-pattern guard added. The deck, package and all measurements are unchanged.
