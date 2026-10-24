# CPU fixture results

Executed `python3 cpu_fixture.py` on 24 October 2026.

Result: **PASS** for exact upstream source hashes, source-derived intermediate operations, unchanged 2% and 1e-7 gates, and a tiny pure-Python BF16/E4M3 cast and scaling example.

The fixture uses a hand-coded CPU arithmetic example and source-text checks. It has no PyTorch, CUDA, Triton, HPC-Ops extension or H100 execution. It does not prove native outputs, a GPU oracle match or that R3 will pass its numerical gates.
