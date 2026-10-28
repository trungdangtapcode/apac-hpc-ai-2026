# Iris reversed-order full-work comparison

## Question

The preceding full-length Iris pair ran hierarchical `zyx` first and `xyz`
second. `zyx` averaged 21.2296 s/step and `xyz` averaged 26.9538 s/step over
149 native timing intervals each. Shorter earlier pairs also favored `zyx`, but
the serial arms can still be affected by node state and execution order. This
candidate reverses the order in a fresh allocation to test whether the measured
difference survives that change.

## Frozen experiment

- One exclusive Iris CPU node, 56 MPI ranks, zero GPUs, QoS `low`, at most three
  hours (168 allocated CPU-hours).
- Run `xyz` then `zyx`, each for 150 solver steps and retain all 149 native
  timing samples and 150 force-coefficient rows.
- Keep the same initialized cases, hierarchy factors `(7 4 2)`, physics,
  fixed solver iterations, and OpenFOAM runtime as job 2294234. Only the
  hierarchy order and arm order distinguish this follow-up.
- Preserve per-arm field seals, source checks, runtime identity, native logs,
  resource snapshots and terminal Slurm evidence.

The hypothesis passes only as a full matched technical comparison if both arms
complete all gates and the resolved executable/library identities remain
stable. A single reversed-order pair cannot establish independent repeatability,
prove a performance gain on NSCC, or qualify as the competition's scored result.
Iris and NSCC timings must remain separate.

## Submission state

This directory is a derived, offline-prepared candidate. Its payload must pass
independent review, and the prior job 2294234 must have a complete raw-evidence
review before deployment. Budget reconciliation and a fresh queue check are
separate mandatory admission gates. No submission receipt or new job ID is
claimed by this README.
