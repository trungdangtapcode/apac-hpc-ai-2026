# CPU account balance versus research campaign allowance

At **24 October 2026 03:16:46 UTC**, `myprojects -p 59000042` displays:

| Account quantity | SU |
|---|---:|
| Granted | 30,000.000 |
| Used | 2,269.938 |
| Balance | **27,730.062** |
| In doubt / current prepaid | 0.000 |

The report labels its balance snapshot **23/10/2026 23:59:34** (site timestamp, not asserted UTC). The command was queried live, but billing can lag: do not assume recent completed or running work has already posted. CPU rate is 1 SU per allocated CPU hour. CPU project 59000042 is separate from the AI GPU project.

**286.2 SU is the remaining conservative allowance within the owner-approved 5,000-SU research campaign, not the CPU account balance.** Planning commitment is 4,713.8 SU, including uncertain shared/older maxima and the new diagnostic reservation. This planning policy intentionally may double-count unresolved costs. It is not a claim that 4,713.8 SU has been billed. The account's larger balance does not automatically raise that campaign ceiling.

The same query shows job 25956623 running. No new submission, reservation, budget expansion or reconciliation was made for this explanation. [Retained numeric snapshot](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/completed-review-20261024/balance-display-20261024T031646Z.json).
