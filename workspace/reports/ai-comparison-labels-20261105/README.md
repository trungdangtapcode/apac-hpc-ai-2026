# Make the comparison understandable on the slide

The owner showed page 10 in PowerPoint beside the current script: the script named HPC-Ops while the slide displayed metric arrows without naming the two conditions. The previous checks proved page routing and numerical agreement but missed whether an audience could understand the comparison. Those earlier broad alignment conclusions are superseded by this review.

## What changed

| Actual PPTX page | Change visible to the audience |
|---|---|
| 08 | Names **default prefill path versus DeepGEMM prefill**, fixed decode/chunk 4096/N56 and the approximately 1.8% gain. The header now distinguishes the N48 diagnostic from the N56 experiment. |
| 10 | Replaces unlabelled metric arrows with a table: **SGLang AUTO (automatic control)**, **HPC-Ops (selected decode expert backend)**, and **change versus AUTO**. Rows name good output tokens/s, mean TTFT and mean ITL, with units and desirable direction. The selection and first-token tradeoff are explicit. |
| 11 | Replaces N62/N64/N68 shorthand in result headings with **62 to 64 requests**, **64-request repeat** and **64 to 68 requests**. |
| 14 | Names the H200 control recipe and the exact H100-derived changes tested on H200: HPC-Ops prefill/chunk 4096; chunk raised to 8192; phase-only inference mode against fresh no_grad control. Percentages explicitly measure goodput versus the appropriate H200 control. |
| 15 | Names **dense versus sparse CUDA graphs** and **no speculation versus EAGLE3**, explains draft/verify, and states capture-memory units and retained choices. The graph comparison's earlier control and differing seeds are explicitly preserved; it is not called a fully matched causal comparison. |
| 16 | Names DeepGEMM prefill/HPC-Ops decode beside the accepted performance result; explicitly calls quality **score retention**, with optimised/stock correct-answer counts and common question coverage. |

[Page 10 preview](page-10.png), [all main slides](OVERVIEW.jpg), [editable changes](EDITS.json) and [validation](VALIDATION.json).

The English/Vietnamese short scripts now name the default prefill comparator and the H100-ported prefill choice. The packaged English script remains byte-identical to its source. Their sections retain explicit actual PPTX page numbers. Script bytes remain local/uncommitted under the owner's instruction.

## Conditions and evidence

- Prefill control 24263 has `--chunked-prefill-size 4096` and no explicit MoE runner override. Candidate 24291 adds `--moe-runner-backend deep_gemm`; decode flags and N56 stay fixed. Fresh control/repeat are 24320/24327. The label says “default path”; it does not invent a resolved backend name. See the retained run configs and [thinking-process evidence](../teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md).
- Decode control 24912 uses automatic expert implementation; candidate repeat 24913 explicitly adds `--moe-runner-backend hpc_ops`. Both use DeepGEMM prefill/chunk 8192, N60, FlashInfer attention and MNNVL collective settings. Displayed values remain 2,838.85 versus 2,989.17 good output tokens/s; mean TTFT 822.29 versus 947.63 ms; mean ITL 16.58 versus 14.93 ms. The exact-data deltas retained from the prior figure are +5.30%, +125.34 ms and −1.64 ms. The repeat's absolute goodput difference from the original HPC-Ops treatment is below 0.04%.
- H200 control 27777 uses DeepGEMM prefill/chunk 8192 and HPC-Ops decode. Port 27783 uses HPC-Ops prefill/chunk 4096; port 27806 raises chunk to 8192. Phase-mode 27828/27830 compare against their separate fresh 27826 no_grad control with the incumbent serving recipe. These are direct H200 measurements, not a cross-hardware score ratio. See [transfer results](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-phase-inference-transfer-20261031/RESULTS.md).
- Sparse graph and shallow EAGLE results retain their original separate controls and limitations; see the detailed study guide's page 15. The former uses an earlier control with a different request seed, so lower goodput is an observed comparison, not an isolated causal effect of graph sparsity.
- Quality is 9,452 / 9,460 =99.9154% retention of the measured reference accuracy, on the same 12,032 questions per role. It is not absolute accuracy or organiser certification. [Full quality result](../ai-quality-verification-20261103/FULL_RESULTS.md).

## Review and preservation boundary

A separate reviewer inspected all sixteen main slides for missing comparator names, baseline ambiguity, chart legends and selection logic, then reviewed the redesigned candidate. Page 10 was also visually inspected at full size; pages 14 and 16 and the full overview were reviewed. Automated checks bind each of the nine measured table cells to the correct condition column, check actual slide/PDF anchors, all forty bilingual spoken-section routes, active slide shape IDs, ZIP integrity and the identical packaged English copy. This is more specific than checking whether a number appears somewhere in a package.

All scientific observations remain unchanged. Only six main AI slide bodies and five corresponding AI note parts change. All eighteen AI backup slide bodies and all eight HPC slide bodies remain byte-identical; appendix/HPC PDF pages are pixel-identical to the input. No job, budget, VPN, HPC payload or optimiser setting was changed.

The screenshot showed PowerPoint's “[Repaired]” title. Basic package checks found no concrete repair cause in either the old or new input. No Microsoft Office execution or clean-open certification is claimed. PDF previews are coordinate renderings with native editable PPTX equivalents.

`build.py` reads preserved `inputs/before.pptx` and `inputs/before.pdf`. Use the pinned requirements from the preceding alignment review, then run `build.py` and `validate.py`. `PUBLICATION.json` records local output paths and hashes. The historical root deck, historical submission ZIP, long teaching guides/PDFs and website are not relabelled as this revision. Large slide/PDF bytes are captured in the external artifact store; Git manifests alone are not an off-host upload of those bytes. Short scripts remain excluded from capture.
