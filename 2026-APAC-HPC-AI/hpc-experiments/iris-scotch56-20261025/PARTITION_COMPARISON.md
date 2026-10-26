# Why the Iris Scotch solver test is worth running

The two native decomposition logs describe the same 65,334,765-cell mesh split into 56 partitions. The older hierarchical log is verified against its retained SHA-256 manifest; the new Scotch log belongs to reviewed cut job 2294040.

| Static quantity | Hierarchical, job 2293752 | Scotch, job 2294040 | Interpretation |
|---|---:|---:|---|
| Unique interface faces | 1,326,716 | 1,035,208 | 21.97% fewer faces shared between partitions |
| Largest rank's interface-face count | 93,343 | 68,534 | 26.58% lower maximum |
| Largest cell count above mean | 0.000152% | 0.999901% | Scotch's cell balance is worse |
| Maximum neighbor patches | 14 | 20 | A rank may communicate with more neighbors |

A processor face is a mesh face on a boundary between MPI partitions. Fewer such faces can reduce communication work, but this count is not transferred bytes, memory bandwidth, time spent waiting or solver runtime. Both Iris configurations use one node, so these are not automatically off-node network transfers. More neighbors may also add message overhead; cell imbalance can create stragglers.

The hypothesis is that lower interface work outweighs the extra neighbor count and roughly 1% worst cell imbalance. It remains a hypothesis until a controlled solver comparison completes. Neither a 21.97% speedup nor a quality improvement follows from these static counts. Complete the mandatory initialization first.

Replay with `python3 compare-partitions.py`; exact log hashes and counts are in partition-comparison.json. The parser distinguishes indented per-rank face counts from the unindented global summary, and requires their sum to equal twice the unique interface count. An initial whitespace pattern also consumed blank newlines and included the summary; the consistency assertion rejected that local parser error before reporting a result.
