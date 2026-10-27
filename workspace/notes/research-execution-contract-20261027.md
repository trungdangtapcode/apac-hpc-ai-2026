# Research execution contract

Recorded 27 October UTC / 28 October 2026 Vietnam time after the owner required
that the same dispatch and reporting failures must not need another reminder.
This is an operating rule for authorised research, not a new allocation,
authentication loop or automation schedule.

## What must happen during an active turn

1. Resolve the worker's track from its session/fork metadata and read its current
   handoff. Refresh the relevant scheduler before treating a snapshot as live.
2. Review completed work and select the next distinct, justified hypothesis.
   Separate required correctness and spending gates from optional investigations.
3. If the preferred cluster is blocked, check an already authorised alternative.
   HPC uses NSCC CPU or Iris CPU; AI remains with its own worker and clusters.
   Rebuild the appropriate native configuration and preserve platform identity.
4. Check the selected cluster's budget, own-job cap, shared-account commitments
   and required locks. Keep NSCC CPU, NSCC GPU and Iris accounting separate.
5. Freeze and review the necessary payload, then obtain a definite scheduler
   receipt. Capture and push that milestone promptly. Do not let unrelated
   diagnostics or repeated unchanged reviews keep a ready research queue idle.
6. After the run, retain raw output and failures, inspect correctness, score,
   tails, resources and missing telemetry, then advance or close the branch.

If capacity is occupied by existing work, preserve its position and prepare the
next useful payload. Do not cancel, requeue, submit blind duplicates or exceed
caps merely to show activity. If no authorised feasible action remains, state
the actual blocker and the evidence needed to proceed.

## Submission and result vocabulary

| State | Minimum evidence |
|---|---|
| Prepared | Scripts/configuration exist and the named local checks passed |
| Deployed | Exact reviewed hashes reached the selected cluster |
| Submitted | Definite scheduler acceptance, job ID, receipt and reservation |
| Running | Dated scheduler observation; distinguish setup from the solver |
| Terminal | Scheduler stopped the allocation; success is not implied |
| Reviewed measurement | Required work, numerical/output/source checks and terminal evidence pass |
| Matched improvement | A qualified candidate beats an appropriate measured control, with stated repetition limits |

A terminal error or timeout is not a completed valid benchmark. Preserve partial
outputs as partial evidence. When queue access fails, the job's current state is
unknown. VPN/SSH disconnection alone does not cancel an accepted batch job.

Use job IDs and dated states when reporting old jobs. Distinguish the absence of
a new submission from the state of earlier allocations. Never imply that an
unqueried job disappeared.

## Avoid the specific failure that prompted this rule

NSCC placement and PMPI diagnostics were allowed to delay native performance
trials that did not require them. After access failed, the worker also failed to
switch promptly to Iris. Producing more notes and tooling did not establish a
new solver-speed result. This must not become the default sequence again.

For example, a native hierarchical `xyz`/`zyx` trial can proceed independently of
an unqualified pinning adapter. The adapter branch keeps its own integration and
Bonus-accuracy gates; it does not become a prerequisite for every other trial.

The concrete fallback was eventually admitted as Iris job **2294234** at
**00:28:44 on 28 October 2026, Vietnam time**. It compares two full 150-step
configurations in one allocation. That receipt proves submission, not a completed
performance improvement. [Actual run record](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-20261027/STATUS.md).

## Budgets, access and truthful attribution

Site limits and owner-set spending limits remain binding. An internal stage
envelope is not automatically a site quota or a permanent owner prohibition.
When the current instruction authorises a new stage, document its bounded
allocation and the authority used before reserving it. Do not move credits
between clusters, reset consumed spending or hide outstanding reservations.

Use existing authorised access without exposing it. A failed login does not
justify an indefinite MFA loop. Ask only for information actually missing to
complete authentication, then continue independent work while it is unavailable.
Never store credentials, OTPs or session state in research records.

Label organiser reference, our reproduction baseline and our new configuration
separately. A lower repeat of the same configuration is not automatically an
optimization gain. Do not pool Iris and NSCC timings or H100 and H200 scores as
matched performance evidence. Preserve all prescribed samples and output gates.

Give owner-facing timestamps in Vietnam time with dates. Do not claim the entire
duration of a delay was caused by an outage when only its later observation is
known. Document unfamiliar terms in readable English prose and preserve exact
identifiers and file paths when editing their surrounding text.

These rules apply to active authorised work. Existing cluster jobs continue
independently, but background Codex, schedules and automatic chat notifications
remain disabled without a new explicit request.
