# First 65M Iris baseline: submitted

Job **2293752** was accepted at 2026-10-21T11:38:43.233405+00:00.
The immediate scheduler response was PENDING, then the retained collection
shows RUNNING on iris031, one node / 56 allocated CPUs / one serial process.
This is the decomposition and restore0Dir stage, maximum 15 minutes. It has
not yet been accepted as a completed stage or a solver result.

The unchanged payload hash matches the reviewed source. The submit receipt,
empty pre-submit queue and subsequent queue/accounting/job responses are in
cut-submission.json. Scheduler output timestamps use the site's local timezone;
the Python receipt and collection clocks explicitly use UTC. Preserve both.

A pre-submit guard attempt mistakenly compared the hash with an unset local
orchestration value and stopped before sbatch. No job was created by that
attempt and no case was modified. The corrected guard uses the explicit
frozen SHA256 and the only successful submission returns 2293752. Never retry
an uncertain submit without checking the retained receipt and actual queue.

Next inspect terminal accounting and decomposePar/restore0Dir logs, the full
56-processor set and total cell count before init. No dependent allocation is
submitted yet. No benchmark Average or Cd exists for this 65M attempt.
Iris SU billing and CPU/NUMA/network hardware telemetry are not collected.
