# Curated AI run lineage

This curated graph selects 31 milestones from the retained AI research record. It follows evidence-supported research dependencies from early topology and transport work through platform-specific tuning, final deployment acceptance and the separate local answer-quality study. It is not a complete job inventory or a claim that every node caused the next one.

## Reading the graph data

`curated.json` is the source for this view. Every node records its job IDs, platform, the date of its last included allocation, its `date_range` from the earliest through latest included allocation, the change, the measured outcome, and absolute paths to existing evidence. Dates and ranges come from the H200 scheduler inventory or H100 allocation ledger; they are allocation dates, not necessarily the date a later review was written. Every edge names its relationship:

- `derived`: a later experiment or conclusion directly follows from the cited evidence.
- `control`: the cited item supplies a comparison/control relationship; it does not imply derivation.
- `motivated`: the earlier observation gave a reason to ask a later question, without proving its mechanism.

The graph uses green for H200 and red for H100. These colors label hardware provenance only; they do not grade results. A node grouping may contain a treatment and its explicit control/repeat, and its outcome text states what the comparison supports. H100 and H200 scores remain separate and must not be read as a direct ranking.

## Important interpretation limits

The earliest topology points changed multiple factors and establish feasibility, not a cumulative causal speedup. Job 22271 failed before scoring; 22294 establishes that the patched request-scoped NIXL path completed real P/D traffic and a full N32 run, not a descriptor-only speedup. Phase/backend choices are platform-specific. Repeats and fresh controls are identified where the record supports them; a high isolated score is not silently promoted to a confirmed gain.

The 3,044.400475 good output tokens/s historical H200 mean, the separate 3,045.501509 native run, and final exact-package 3,051.518173 run are different evidence classes. Job 28197 is exact-entry acceptance, not a matched optimization comparison. The full-set quality comparison is also separate from performance: 9,452/9,460 reference-score retention (99.915433%) passes the declared local point gate, but is not organiser certification or statistical equivalence. Pilot jobs 28367/28368/28371 include a failed initial reference plus corrected reference and candidate; their 98.076923% result remains a losing milestone and is not mixed into the full-set score.

All conclusions are bounded by their recorded workloads, controls and gates. Evidence files retain the run-level details, source checks, limitations and provenance; the concise node summaries do not replace those reviews.
