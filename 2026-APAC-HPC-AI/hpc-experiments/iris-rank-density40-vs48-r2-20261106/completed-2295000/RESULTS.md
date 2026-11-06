# Job 2295000 review

**Disposition: failed during arm preparation; no valid solver measurement.** Slurm reports `FAILED`, exit `1:0`, after 303 seconds on `iris001` with 56 CPUs. Accounting reports 04:56.041 total CPU and 75,848 KiB batch MaxRSS. There are no solver arms in the run record.

## What passed and where execution stopped

The pre-run payload check passed in 0.167 seconds. Both accepted-source preflights passed: N40 in 53.931 seconds and N48 in 58.389 seconds. The runner then selected the accepted N48 source for `A1-control48` and started its preparation command. That command hit its 180-second cap (180.033 seconds, return code 124); the runner raised an assertion on that return code and exited.

The retained preparation log is empty (zero bytes). A source-selection record and partial A1 configuration files are present, but there is no preparation result or READY proof. These artifacts do not reveal which internal preparation operation was active at timeout. No cause is inferred. Since preparation did not return success, the solver was not launched. Source-after and payload-after checks, native output/force checks, the remaining arms, and the four-arm ABBA comparison were not reached.

## Integrity and interpretation

All 53 collected raw-evidence files match their recorded byte counts and SHA-256 values. The archive is 29,068 bytes with SHA-256 `88092d8114e7fad3e99603a0e8c52339acd1e31b0927ffa8e87cb65584698484`. All 100 frozen payload file hashes match the collector's frozen-runtime hash map; the payload hash-manifest SHA-256 is `19da1044d1a8854fe7aa3774c74a1de9490e86909b9096631b9d5a49dda9223d`.

This run supplies no solver timing, speed comparison, or evidence for either rank count. Treat it as a failed preparation attempt, not a performance result. Raw scheduler, phase, preparation, source-selection, and payload evidence remains in `raw-evidence.tar.gz`; verification details are in `REVIEW.json`.
