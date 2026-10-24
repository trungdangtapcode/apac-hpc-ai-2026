# H100 prefill observer review — 224276.pbs111

**Result: prefill observer readiness passed; scope is one TP4 H100 prefill worker.** PBS reports terminal `F`, `Exit_status=0`, and `Stageout_status=1`; the output and all 32 collected files are present and hash-verified. This is not a full P/D test or a token-correctness result.

The submitted source checked the patched native NIXL file at SHA-256
`912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f` and
verified four H100 devices, the pinned draft weight SHA, and BF16 target/draft
KV allocation. The preflight gate passed with actual metadata receipts from
TP ranks 0–3 and loaded-source receipts for SGLang `utils.py` and NIXL `conn.py`.
An independent replay of the shipped `check_prefill_observer.py` against a
temporary copy of the collected artifacts also passed.

Every rank recorded the same ten tensor names, shapes, dtypes, row widths, and
96 rows per tensor. `output_hidden_states` is present as BF16, shape `[96,
4096]`, row width 8,192 bytes. Each rank has 10 metadata entries totaling
933,888 bytes. These are measurements from the actual prefill worker; they do
not characterize decode metadata or prove P/D transfer compatibility.

The server reached its built-in startup warmup and ready marker. Its internal
startup log includes a successful `/generate` warmup request, but no controlled
client output IDs were collected. The job did not run an external decoder,
observe P/D transfer methods, or compare output against the accepted H100
reference. Do not treat readiness, the startup warmup, or this result as a full
correctness pass.

Shutdown followed the readiness gate: the launcher sent SIGTERM, and SGLang
logged SIGTERM handling followed by a detokenizer child exit `-15` and SIGQUIT
cleanup. PBS still reports exit 0, but the SGLang log ends during its five
second crash-diagnostic delay. This is consistent with the intentional
post-gate stop, while the final child cleanup state is not fully captured.

The root-owned next run, **224277**, should test the distinct hypothesis that
the observer works on both P roles and the D role, reports matching actual
tensor names and widths with measured per-role row counts, and identifies
whether the first native remote operation follows KV or auxiliary send. It
must retain independent semantic warmup receipts and the complete 1,600-ID
comparison against target reference 222761. This preflight alone does not
resolve the original 223055 remote disconnect.

See [REVIEW.json](REVIEW.json), [PBS accounting](collected/pbs-accounting.txt),
[raw collection manifest](collected/evidence-sha256.json), and
[sealed raw archive](raw-evidence.tar.gz).
