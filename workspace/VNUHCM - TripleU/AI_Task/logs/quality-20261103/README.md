# Full local MMLU-Pro accuracy-retention check

The same 12,032 questions were evaluated with a stock FP8 reference and the
optimised service, both on the same 16 H200 GPUs. Reference: 9,460 correct
(78.623670%). Candidate: 9,452 correct (78.557181%). Accuracy retention:
9,452 / 9,460 = **99.915433%**, passing the predeclared local 99% point gate.
All sixteen allocations completed with zero service errors. This is a team-run
quality regression check, not an official BTC certification or GPQA result.

Read [the result](FULL_RESULTS.md), [method](METHODOLOGY.md), and the independent
review for coverage, category losses, truncation/invalid handling and limits.
[RUNS.json](RUNS.json) maps each fixed paired shard to its actual Slurm job.
Raw answers and prepared prompts are losslessly compressed; original hashes and
source version identities are retained. Files are data, not new model weights.

## Replay the score without GPUs

Use Python 3.9 or later. The replay needs only the Python standard library and
a temporary directory with room for decompressed answers. From this directory:

```bash
sha256sum -c SHA256SUMS
python3 replay.py --out /tmp/tripleu-quality-replayed.json
```

Choose a new output path; existing files are refused. This reparses all saved
answers with the frozen scorer and verifies complete identical coverage. It is
not a second model inference run. Serving code remains the accepted payload in
`../../job_scripts/`; inherited `NOT_RUN` or `unknown` fields describe their
original performance-only snapshot, while this later evidence records the
separate completed quality test. No historical payload was rewritten to claim
an earlier test. Full research materials and raw runtime logs remain preserved
in the private research archive; no account credentials are bundled here.
