# Correction: NCCL kernel symbols do not identify the selected protocol

The earlier interpretation that missing named Simple kernels meant the selector had not activated was wrong. This supersedes that interpretation in the 14:18 and 17:20 reports, notes and historical profile summaries. The old raw traces, logs, scores and analyzers remain preserved. No GPU allocation was needed to resolve it.

NVIDIA's [NCCL collaborator explanation](https://github.com/NVIDIA/nccl/issues/1595) describes the same misleading LL symbol when Simple is selected. In the matching-version [2.28.9 generator](https://github.com/NVIDIA/nccl/blob/v2.28.9-1/src/device/generate.py), `best_kernel` maps these protocol variants to an LL-labelled representative. [Device dispatch](https://github.com/NVIDIA/nccl/blob/v2.28.9-1/src/device/common.h) can then run the function selected by the work item. The local six-case AST validation reproduces that mapping for BF16 all-reduce. This tagged upstream source is not a provenance match for every byte of the installed binary.

The preserved logs already contain stronger evidence: [NCCL TUNING decisions](https://github.com/NVIDIA/nccl/blob/v2.28.9-1/src/enqueue.cc) report the algorithm and protocol selected for scheduled tasks. The code emits these records on communicator rank zero; do not label them as independent records from all eight ranks.

| Job and prefill replica | Parsed LL decisions | Parsed Simple decisions | Unparsed selection records |
|---|---:|---:|---:|
| 221884 control, replica 0 | 27 | 4470 | 5 |
| 221884 control, replica 1 | 27 | 4470 | 4 |
| 221885 global Simple, replica 0 | 0 | 4550 | 4 |
| 221885 global Simple, replica 1 | 0 | 4550 | 5 |

The parsed control LL decisions are 4-byte operations. Its larger 18–32 MiB all-reduces already use Simple. The candidate changes the small operations to Simple too; parsed large operations remain Simple. Truncated/interleaved records are excluded and counted. These are run-lifetime records, not a timestamp attribution of every ranked N54 call or proof that all unlogged communicators use this path. Nevertheless, the claim that the global selector failed because traces say LL is refuted.

The scores are unchanged: control 2415.474 and candidate 2421.066 good output tokens/s, a single +0.2315% observation. Most large-message decisions were already the same, and this does not establish a useful gain. Close the forced-Simple performance branch for lack of a useful demonstrated benefit, rather than an alleged failure to activate. Keep the default automatic protocol policy. A further full-model protocol run or communicator reproduction solely to explain the LL symbol is unnecessary.

`analyze-nccl-selection.py` checks each log against its immutable seal and accepts only complete known protocol names. `nccl-selection-log-review.json` retains per-size counts and source hashes; `representative-kernel-validation.json` retains the generator validation. Older `simple_allreduce_events` and `ring_allreduce_events` fields count symbol substrings only. They must not be used as algorithm/protocol activation gates. No performance peak, accuracy result or model-output claim changes.
