# Read-only intake of completed shared CPU work

On 22 October, PBS reports F / exit 0 for jobs 25921487.pbs101 and 25921492.pbs101. Their full preparation/solver text logs, text case inputs and output function data were collected without changing remote work. This is an intake, not adoption of job ownership or acceptance as a contest result. The collector makes no scheduler, budget, payload or remote filesystem mutation.

The sealed archive has 135 members. Remote hashes were verified after extraction; evidence-sha256.json seals the archive and extracted files. The collection includes only whitelisted bounded text and sanitized PBS metadata. Authentication/session material, full environment, processor trees, mesh binaries and runtime libraries are excluded. Current script copies need not equal frozen submitted bytes. Independent native work/source/timer/force review is a separate checkpoint. Keep existing shared jobs and this worker's ledger unchanged.

Run: `python3 tools/collect_shared_cpu_readonly.py shared-cpu-intake-20261022/collected 25921487.pbs101 25921492.pbs101` from hpc-experiments. The collector refuses an existing output; do not overwrite sealed evidence. Source syntax validation and successful live collection/hash checks passed.
