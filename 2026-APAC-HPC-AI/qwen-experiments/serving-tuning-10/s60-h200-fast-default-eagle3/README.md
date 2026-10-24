# S60 fast-default EAGLE3 candidate

This is the candidate arm for the S59 fast-default target-only control. It derives from the helper-fixed S58 candidate and must match S59 on all common topology and serving settings. Its only serving change is enabling EAGLE3 with two steps, top-k 1, and three draft tokens (using the retained draft path and FlashInfer draft attention). The deterministic-inference flag and legacy S46 target-reference binding are removed. Before model startup the bundle requires a root-bound, independently replayed actual S59 control through `matched-control.json`; the checked-in placeholder is deliberately unbound and fails closed.

The common screen retains the strict 90% good-request threshold, zero request errors/cancellations, the 7/8 smoke floor with no known regression, two P/D semantic paths, and 12/12 retrieval cases. The separate exact 1,600-ID failure from job 25797 remains preserved as a quality limitation and is not treated as an official quality verdict. This performance-only bundle does not rerun exact-ID comparison.

Quality remains UNKNOWN; no official accuracy or speedup claim is made. No job was submitted in preparation; root review, actual S59 binding, and submission remain required.
