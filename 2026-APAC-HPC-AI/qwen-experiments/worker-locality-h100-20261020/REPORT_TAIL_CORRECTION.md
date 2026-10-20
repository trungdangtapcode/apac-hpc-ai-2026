# Single-pilot report bookkeeping correction

The 222435 per-job sealed serving review completed and wrote LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS before the copied generic pair-report tail raised KeyError: paired_role. This one-pilot mapping experiment has no paired_role. The original stdout/stderr are retained; scheduler success alone is not used as evidence.

The report tail now requires exactly two role-tagged points before writing a pair and writes paired-serving-comparison.json, leaving the separate predeclared startup cost-gate comparison untouched. CPU fixtures exercise one-pilot and two-pilot saved results and a sentinel cost report. Per-job review SHA is unchanged; no full native benchmark re-audit or GPU retry was needed. The matching startup readers receive the same non-destructive tail fix. See report-tail-validation.json. This fixes local report bookkeeping, not a model/transport/benchmark failure.
