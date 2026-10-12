# Supplementary transport work

The packaged Basic entry point remains the unpatched job-22219 configuration. These patches are included as separately labelled serving research and are not mounted by `submit.sbatch`.

Job 22415, P8-TP4_D8-TP8-EP8 / N48 with `hetero-tp-request-descriptors-v1`, is the current best local long run: 1912.30 good output tokens/s, 97.44% SLA, zero errors/cancellations. That is an observed 14.78% above job 22219 (1666.01); topology, concurrency and transport differ, so the gain is not isolated to the patch. The patch passed 720 CPU byte-range cases and real GPU benchmarks.

The separate `equal-tp8-request-descriptors-v1` passed 936 CPU range cases and 5 fallback guards. Job 22809 completed all four sweeps and long N32: 1507.96 good tokens/s, 95.38% SLA, zero errors/cancellations. N40/N48 sweeps miss the 90% gate. Source metadata with `gpu_validated: false` describes the pre-submission snapshot; later evidence is in `gpu-validation.json` and the immutable job logs. Prefill EP2 is a separate layout change.

Full-set accuracy and official organiser acceptance remain unverified for both stacks. Original frozen payloads, including source hashes, are under `archive/22415` and `archive/22809`; those historical scripts contain the team's paths and are audit evidence, not portable entry points.

To reproduce the CPU check independently, use Python with NumPy, then `python3 test-nixl-ondemand.py` from this directory. The patch, original/patched module and exact geometry helper are in `nixl-ondemand/`. Do not confuse this descriptor test with the competition's accuracy gate.

For the equal-TP patch, run `python3 test-nixl-equal-ondemand.py` here; the exact image helper sources are included under `nixl-equal-ondemand/`.
