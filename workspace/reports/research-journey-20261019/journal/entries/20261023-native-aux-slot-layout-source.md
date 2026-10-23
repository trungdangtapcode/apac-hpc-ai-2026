# Whole registered buffers are different from per-request metadata rows

23 October 2026, source-only. Full-span native probes move whole auxiliary buffers. Actual serving instead moves one metadata row at source/destination request-slot indices, so successful whole-buffer writes do not prove production row addressing. This is a separate remaining gap after the login-shell failure diagnosis.

Pinned source returns ten ordered arrays of pointers, region lengths and item lengths; the item width is the first row's nbytes. Most widths are fixed. Hidden-state width/dtype comes from the draft runner and was not collected. Actual prefill cap 48 plus the independent source allocation rule derives 96 metadata slots. The decode cap 256 is logged, but decode allocates twice req_to_token_pool.size, a different property absent from old receipts. Treat 512 rows only as the conditional pool-size 256 scenario. Sender send_aux uses the source item width for both offsets and does not compare a destination item-width list.

The CPU arithmetic fixture matches all ten observed aggregate lengths under the explicit 4096/BF16 hidden-state assumption and checks first/last-slot bounds in a conditional 96-to-512 scenario. This is not live tensor allocation, runtime stride, all-peer transfer, model output or a cause for the old full NIXL disconnect. Source files, hashes and exact gaps are retained. No GPU, credit or queue action occurs in this review.

Next useful full integration evidence must include actual P/D list counts, per-index row widths, shapes, strides/dtypes, allocated slot counts and transfer phase markers. A no-model row transfer can test declared schemas, but cannot prove a missing live decoder pool size by assumption. [Source-linked report and structured known/conditional/uncollected fields](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-aux-layout-review-20261023/REPORT.md).

For a presentation: “We first verified that registered memory can transfer. A real request copies one row inside that memory, so we also need to verify the row size and slot index on both endpoints. A large-buffer pass alone cannot answer that.”
