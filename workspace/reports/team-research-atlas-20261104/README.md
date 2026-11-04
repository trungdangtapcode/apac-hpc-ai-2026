# Team research atlas — one page

Open https://trungdangtapcode.github.io/apac-hpc-ai-2026/ . AI and HPC switch in place in the same document. `#ai` and `#hpc` are shareable entry points. The old `/hpc/` path redirects to `/#hpc`. There are no iframes or track-to-track document loads.

The common header, overview and sticky track selector cover both tasks. The explorer shows the appropriate graph, index, platform legend, evidence panel and units for the active track. Each track retains its own search, filters, selected item and view state. The whole page works offline from the generated HTML.

AI retains 419 allocations, 31 milestones and its four latency/goodput metrics. HPC retains 15 curated milestones, not an allocation census, with the original recorded result and evidence classification. Forty-six is the sum of curated milestones, not the number of benchmark runs. Scientific text and data are unchanged. Original HPC reports remain outside this publication derivative.

Run `python3 build.py` with Graphviz installed. It refreshes the standalone source components and then calls `build_unified.py` to compose `index.html` and a deterministic `index.html.gz`. Shared component data, scripts and styles are embedded. HTML/SVG IDs are namespaced and checked for uniqueness. Components initialise only when opened and have isolated runtime state. `viewer/unified.html` and `viewer/unified.css` define the shared shell.

Pages stages the reviewed team `index.html.gz` as the root page, `.nojekyll` and a tiny legacy redirect at `hpc/index.html`. The workflow watches the team gzip. It never uploads the repository root or the external object store. Individual AI and HPC component pages remain build inputs and historical offline views; the hosted product is the unified document.

[Single-page browser validation and design record](../team-atlas-single-page-20261104/README.md). Earlier two-route publication receipts and tests in this directory are historical; the previous README is preserved with the new review. Source scientific records and original HPC report hashes remain retained.

## Current workspace design

The visual refresh replaces the large introduction with a dark navigation sidebar, a light graph workspace, compact scope cards and an original generated sidebar image. The shared page and task state are preserved. [Design direction, references, asset hashes and regression checks](../atlas-design-refresh-20261104/README.md).
