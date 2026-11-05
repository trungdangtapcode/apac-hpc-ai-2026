# AI speaking route: script index and actual PPTX page

The script index starts at zero by owner request. Actual PPTX pages and printed labels start at one. These are the same sixteen main slides.

| Actual PPTX page / printed label | Script index | Topic |
|---|---|---|
| 01 | 0 | Fast tokens count only when requests meet both latency limits |
| 02 | 1 | Three investigations support three different kinds of claim |
| 03 | 2 | Replica count and parallel width compete for the same 16 GPUs |
| 04 | 3 | Two TP4 prefills feed one TP8 decode within the two-node budget |
| 05 | 4 | Ready workers still failed before the first usable benchmark |
| 06 | 5 | Request-scoped descriptors remove work unrelated to the request |
| 07 | 6 | The patched path became usable; descriptor-only speedup is unknown |
| 08 | 7 | Profiles identify candidates for investigation, not a proven time budget |
| 09 | 8 | Test the decode implementation while holding the serving setup fixed |
| 10 | 9 | Higher goodput came with slower first tokens and faster streaming |
| 11 | 10 | N64 survives a full repeat; N68 loses its short-test advantage |
| 12 | 11 | The remaining latency failures are first-token tails |
| 13 | 12 | A complete portable run reproduces the retained operating level |
| 14 | 13 | Direct H200 tests decide which H100 ideas transfer |
| 15 | 14 | Better proxy metrics did not always improve qualifying throughput |
| 16 | 15 | The retained recipe survives performance and quality checks |

**Seventeen layouts is on actual PPTX page 03 (script index 2). Actual PPTX page 02 is the three-contribution overview.**

The packaged AI_Task/logs/TALK_SCRIPT_EN.md is now byte-identical to the current English source script. The previous review omitted this packaged copy; its all-artifact alignment conclusion was too broad. Scripts remain uncommitted under the owner instruction.
