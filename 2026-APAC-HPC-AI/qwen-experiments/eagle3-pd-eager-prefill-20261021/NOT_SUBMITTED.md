# Superseded before submission

This preparation was archived as 41551c1, but never uploaded, reserved or qsubbed.
Read-only peer review found an unnecessary dependency on the HPC CPU SSH helper
for a queue count and incomplete prefill_extra_flags metadata. The runtime
prefill-only graph change was correct. Use separately named
eagle3-pd-eager-prefill-r2-20261021, which removes all cross-track connections
and conservatively retains one external CPU slot for combined-cap checking.
No HPC connection, budget or job change was executed by this preparation.
