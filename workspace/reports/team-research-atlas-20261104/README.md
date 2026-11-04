# Combined AI and HPC research atlas

The owner requested combining the HPC team's work with the public AI atlas. The same website now has two linked sections with a common interface:

- AI: https://trungdangtapcode.github.io/apac-hpc-ai-2026/ — 419 retained allocations, 31 milestones.
- HPC: https://trungdangtapcode.github.io/apac-hpc-ai-2026/hpc/ — 15 curated OpenFOAM milestones, 14 documented connections.

The HPC content is read from the existing HPC worker's `hpc-run-lineage-20261104/milestones.json`. Its scientific text, references, status labels and relationships are retained. NSCC is orange and Iris blue. The HPC index is explicitly a milestone index, not an exhaustive job census. Hover displays the recorded result and evidence level, rather than borrowing the AI latency metrics. Selection gives the change, result, job references, source and connected questions. Results include rejected branches, reference reproduction, qualified teammate findings, mechanisms and unreviewed trials. No new performance interpretation or measurement was added.

`build.py` refreshes the AI standalone viewer and builds an HPC companion using shared styling. The generated HPC HTML and deterministic gzip live under `hpc/`. They are publication derivatives: the HPC source report, diagrams, data, code, queues, budgets and submission payloads are untouched. `hpc-source-unchanged.json` verifies the original report files byte-for-byte against the prior archive.

The Pages staging helper publishes exactly three files: `index.html`, `.nojekyll` and `hpc/index.html`. Each HTML is self-contained. The workflow watches both compressed pages. The offline HPC companion is also usable as a standalone HTML; relative track links are intended for the hosted site.

Browser validation exercised real navigation between both sections through a local HTTP server, all 15 HPC nodes, the practice-result tooltip, job 2294637 with its qualified label, five NSCC milestones, mobile width and the existing AI 419-job mode and exact-job search. JavaScript errors were absent. No fresh scheduler or authentication actions were taken.

## Live deployment verified

Actions run 41790772151 succeeded from commit 55e84bb1. Both public routes returned HTTP 200 and exactly matched their reviewed HTML hashes; `ai-published.json` and `hpc-published.json` retain the checks. A hosted Chromium session navigated AI → HPC → AI, checked the node counts, searched job 2294637 and confirmed the qualified evidence label without JavaScript errors. The source-preservation and local mobile checks remain in this report.
