# S61 fast-default EAGLE3 decode-only candidate

This is the candidate arm for the S59 fast-default target-only control. It derives directly from frozen S60 and must match S59 on all common topology and serving settings. The earlier S60 showed EAGLE3 on all three workers reduced ITL but failed the TTFT gate. S61 keeps S60’s EAGLE3 settings on decode-0 only; both prefill workers remain target-only, matching the established disaggregated target-serving path. The deterministic-inference flag and legacy S46 target-reference binding are removed. Before model startup the bundle requires a root-bound, independently replayed actual S59 control through `matched-control.json`; the checked-in placeholder is deliberately unbound and fails closed.

The common screen retains the strict 90% good-request threshold, zero request errors/cancellations, the 7/8 smoke floor with no known regression, two P/D semantic paths, and 12/12 retrieval cases. The separate exact 1,600-ID failure from job 25797 remains preserved as a quality limitation and is not treated as an official quality verdict. This performance-only bundle does not rerun exact-ID comparison.

Quality remains UNKNOWN; no official accuracy or speedup claim is made. This is a distinct bounded follow-up to S60. The actual S59 control review is retained and bound; source/runtime preflight must pass before submission.
