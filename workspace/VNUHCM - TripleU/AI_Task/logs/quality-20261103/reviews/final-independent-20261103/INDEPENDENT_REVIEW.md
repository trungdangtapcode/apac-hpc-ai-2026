# Independent full-set quality replay

Reviewed: 2026-11-03T04:22:50Z (UTC)

## Result

The immutable local aggregator independently reproduced **9,460/12,032 (78.6237%)** for the reference and **9,452/12,032 (78.5572%)** for the candidate. Candidate/reference accuracy ratio is **0.999154334 (99.9154%)**. The declared aggregate local gate passes: at least 99% of reference accuracy, complete paired coverage, and zero service errors. The candidate trails by 8 answers (−0.06649 percentage points); it is 0.71975 percentage points above the 99%-of-reference threshold.

This establishes `LOCAL_FULLSET_GATE_PASS` for this frozen local comparison only. It is **not** an official BTC/organizer pass.

## Paired outcomes and categories

Paired outcomes: 9,018 both correct; 2,138 both wrong; 434 candidate-only correct; 442 reference-only correct. There are 876 discordant items.

| Category | Reference | Candidate | Candidate/reference | Δ correct |
|---|---:|---:|---:|---:|
| biology | 646/717 | 651/717 | 1.0077 | +5 |
| business | 643/789 | 642/789 | 0.9984 | -1 |
| chemistry | 912/1132 | 905/1132 | 0.9923 | -7 |
| computer science | 345/410 | 338/410 | 0.9797 | -7 |
| economics | 725/844 | 723/844 | 0.9972 | -2 |
| engineering | 594/969 | 590/969 | 0.9933 | -4 |
| health | 633/818 | 641/818 | 1.0126 | +8 |
| history | 268/381 | 270/381 | 1.0075 | +2 |
| law | 685/1101 | 679/1101 | 0.9912 | -6 |
| math | 1157/1351 | 1161/1351 | 1.0035 | +4 |
| other | 730/924 | 726/924 | 0.9945 | -4 |
| philosophy | 387/499 | 383/499 | 0.9897 | -4 |
| physics | 1075/1299 | 1079/1299 | 1.0037 | +4 |
| psychology | 660/798 | 664/798 | 1.0061 | +4 |

The aggregate gate hides category variation: computer science is 338/410 vs 345/410 (ratio 0.979710), and philosophy is 383/499 vs 387/499 (0.989664). These are descriptive category differences; no category-specific pass threshold was declared. The largest absolute category deficit is chemistry and computer science (−7 each), then law (−6).

## Integrity and replay

Exact replay command with all 16 source-run paths: [`COMMANDS.txt`](<COMMANDS.txt>).

The replay used the prepared 4k evaluator sequence budget (`bdd30112c2f4afb33eb77837b56e6cbd19f438256378726842a2a41bca8dc76a`; compiled corpus `6f80e430896a0aa12658678887676dbefae71460b6e8ea326f9bfc10ec1e0db9`). Each of 16 source run directories reports 1,504/1,504 complete records; the run JSON and raw responses SHA-256 values match the source hashes in the original full comparison. Both roles have the same complete 12,032-question ID set, each ID unique and spanning IDs 70–12256.

Frozen 310-file payload verification: 310/310 byte length and SHA-256 matches. Additional workflow code guard: 27/27 matches.

Native allocations checked with `sacct -X`:

- `28373`: `COMPLETED` exit `0:0`
- `28375`: `COMPLETED` exit `0:0`
- `28382`: `COMPLETED` exit `0:0`
- `28384`: `COMPLETED` exit `0:0`
- `28386`: `COMPLETED` exit `0:0`
- `28388`: `COMPLETED` exit `0:0`
- `28390`: `COMPLETED` exit `0:0`
- `28392`: `COMPLETED` exit `0:0`
- `28394`: `COMPLETED` exit `0:0`
- `28396`: `COMPLETED` exit `0:0`
- `28398`: `COMPLETED` exit `0:0`
- `28400`: `COMPLETED` exit `0:0`
- `28402`: `COMPLETED` exit `0:0`
- `28404`: `COMPLETED` exit `0:0`
- `28406`: `COMPLETED` exit `0:0`
- `28408`: `COMPLETED` exit `0:0`

All 16 allocations are `COMPLETED` with `0:0`. The exact invocations are preserved in [`COMMANDS.txt`](<COMMANDS.txt>), native scheduler output in [`SACCT.txt`](<SACCT.txt>), and per-run/input/artifact hashes in `INDEPENDENT_REVIEW.json`.

## Validity limits

- The method is the pinned local MMLU-Pro split, adaptive five-to-zero demonstrations, a chosen evaluator sequence budget of 4,096 tokens (prompt length strictly <2,048 plus up to 2,048 generated tokens), and max generated output 2,048. The worker serving capacity is 8,192 tokens; 4,096 is the evaluator protocol budget, not the workers’ context limit. This does not reproduce the private organizer evaluation or certify BTC scoring.
- Local invalid outputs are wrong by fixed-denominator rule; both roles have 101. Truncated outputs: reference 1,484; candidate 1,468. No service errors were recorded.
- This is an independent replay of saved answers using the same fixed scorer and artifacts, not an independent second GPU inference replicate. The aggregate result is a point estimate on this set. It does not prove statistical equivalence, identify a causal model/kernel/transport effect, or determine the organizer score.
- Candidate serves the submitted model under its recorded configuration, while the reference is the study’s pinned FP8 reference deployment. Attribute only to this paired local comparison.

## Evidence files

- Replay: [`REPLAY.json`](<REPLAY.json>), SHA-256 `0708d2f64193675fb038f5bc0d830b1ef9cb6099f7f84475c853dd377bfd65f2`.
- Machine-readable audit: [`INDEPENDENT_REVIEW.json`](<INDEPENDENT_REVIEW.json>).
- Aggregator SHA-256: `3ca474a7703de50d6164395bacafba0d6350869e2f64e8d554fdd88fed449f22`.
- Original comparison SHA-256: `60f7117b9a7d3d34c39a58f91a118f1da6c5038ede3ab64c65251f5e36e3a4e9`.
