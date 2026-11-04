# AI GPU experiment timeline and research lineage

Evidence captured on 3 November 2026. This report covers the team's AI/GPU work, including setup probes and failed allocations. It excludes the independent CPU/OpenFOAM research.

**[Open the interactive research atlas](https://trungdangtapcode.github.io/apac-hpc-ai-2026/).** The same viewer is available offline as [index.html](index.html) or the directly tracked [compressed HTML](index.html.gz). It has no external runtime dependencies.

The **Research map** offers 31 milestones or all 419 allocations. Drag to pan, scroll to zoom, use **Fit all** for an overview, or **Read width** to reset the scale. Search and platform filters highlight matching nodes; **Next match** centres each match. H200 is green and H100 red. Hover shows four metrics; select a node for its change, outcome, all retained measurement points, documented relationships and sources. The **Run inventory** searches every retained job and exports the filtered rows as CSV. The page opens on the first milestone at a readable scale.

The hosted and offline views use the same retained snapshot. Data and counts are unchanged by the visual redesign. Machine-local paths are converted to repository references for the public page. Source documents may refer to externally retained objects; hosting the viewer does not upload those objects. The site publishes the viewer only, not a directory listing of the repository.

## Visual research map

[![H100 red and H200 green: chronological research milestones](journey.png)](journey.svg)

Click to open the scalable diagram. For hover metrics and all 419 nodes, open the interactive atlas linked above or use its offline copy.

## How many times did we run?

| GPU platform | Recorded scheduler IDs | Confirmed started | Confirmed not started | Start unknown |
|---|---:|---:|---:|---:|
| H200 / Firmus Slurm | 295 | **284** | 11 | 0 |
| H100 / NSCC PBS | 124 | **122** | 1 | 1 |
| Total | **419** | **406** | **12** | **1** |

These are unique **scheduler allocations**, not the number of benchmark points or distinct configurations. A single allocation can run several loads, warmups, tests or repeated measurements. “Started” means the job began execution according to retained evidence; it does not mean that model loading, GPU computation, or a valid benchmark succeeded. A failed startup still consumes a run attempt. Do not describe the 419 recorded IDs as 419 completed benchmarks.

H200's 284 started allocations comprise 219 COMPLETED, 64 FAILED and one TIMEOUT. The 11 other Slurm jobs were cancelled before starting. H100's retained ledger has 80 exit-zero records, 19 nonzero and 25 with no retained exit status; execution is independently supported for 122, explicitly absent for one, and unknown for one. Scheduler success alone does not certify any performance or quality result.

H200 job 20201 is the original GPU learning test, included in 284; therefore **283 started H200 allocations remain after excluding that HelloGPU lesson**. The inventory does not assume all remaining allocations are full performance benchmarks: some are profiles, compatibility/transfer probes, startup tests or quality evaluations.

Read [H200 count provenance](h200/README.md) and [H100 count provenance](h100/README.md). H200 accounting was freshly queried from 1 September through 3 November; the earliest returned record is 29 September, so absence of earlier jobs is not proven. H100 is reconstructed from the retained PBS ledger and artifacts, not a new VPN/PBS query. Unknowns remain visible. These are auditable retained-history counts, not a claim that every historical scheduler record is recoverable.

## What the runs tested

The selected map follows 31 technical milestones, with 27 documented relationships:

1. **Make the deployment work:** allocate prefill/decode workers across sixteen GPUs, respect FP8 geometry, diagnose warmup/transfer failures, and test the request-scoped NIXL descriptor change.
2. **Find a useful serving configuration:** routing, phase-specific DeepGEMM/HPC-Ops/FlashInfer, communication, chunk size and concurrency; compare with controls and rerun promising points.
3. **Keep unsuccessful ideas:** H100 alternatives, cache settings, sparse graphs, speculative decoding and H100-to-H200 transfers. A proxy improvement or a faster component did not necessarily improve latency-qualified goodput.
4. **Verify reproducibility and correctness:** independent N64 performance allocations, repair the portable entry, then perform the complete paired answer-quality study.

Each milestone states the proposed change, measured outcome and retained evidence. The map includes the performance level around 3,044 good output tokens/s, the separate accepted entry 28197 at 3,051.518173 good output tokens/s, and the later quality result: reference 9,460 versus candidate 9,452 correct out of 12,032 each, **99.915433% accuracy retention**. The latter is a local MMLU-Pro quality result; it is not goodput or official certification.

## Read the arrows correctly

- **H100 is red; H200 is green.** Color identifies the GPU platform, not whether a run won.
- **Solid `B → A` (`derived`)**: retained evidence connects A to B's implementation/configuration or repair.
- **Dashed (`control`)**: the two measurements have a documented comparison/control relationship. This is not automatically code inheritance.
- **Dotted (`motivated`)**: an earlier finding supported the next question; it does not establish that the later score was caused by the earlier change.
- The overview is ordered top to bottom by recorded calendar dates. A milestone grouping several jobs uses the last included run date, with its complete date range retained in JSON. Original timestamp/date conventions remain in the inventories; do not infer minute-level ordering from a calendar date.
- **No arrow does not mean no ancestry.** It means that no explicit supported link was recovered for this report. Similar names, adjacent job numbers or chronological order are insufficient.

The complete allocation map uses only retained `parent_job_ids`; these can include a recorded source, control, or PBS scheduling dependency. **A scheduler dependency expresses execution order, not experimental or code inheritance.** Consult the record's evidence and the typed overview before calling a relation an improvement. Invisible layout constraints place jobs chronologically; they are not drawn as arrows.

## Files and exports

| File | Use |
|---|---|
| [Offline interactive viewer](index.html) | Research map, search, filters and clickable detail records |
| [Overview SVG](journey.svg), [PDF](journey.pdf), [PNG](journey.png) | Scalable diagram of the 31 milestones; zoom to read the wide research map |
| [Every allocation as SVG](all-allocations.svg) | All 419 recorded IDs with only retained parent edges; intentionally a large scrolling diagram |
| [Run inventory CSV](runs.csv), [JSON](runs.json) | All counts, purposes, outcomes, dates, parents and source paths |
| [Curated reasoning and edge rationale](CURATED.md), [JSON](curated.json) | Explain each technical decision and why each arrow exists |
| [Validation](validation.json) | Count uniqueness, evidence-path checks and SVG parsing |

All diagrams are generated with standard Graphviz tools, with no invented imagery or fabricated causal links. Run `python3 build.py` followed by `python3 build_allocation_map.py` from any directory; Graphviz `dot` must be installed. Browser interaction has not been exercised with an automated browser in this environment; the offline HTML, embedded data and SVG structure were inspected, and the rendered overview was visually reviewed.

No new GPU jobs, authentication, queue edits, slides/submission update or HPC payload change was needed to build this history. The current presentation remains a separate deliverable.

## Four-metric hover cards

Hover a milestone or an individual allocation to see a compact table of **good output tokens/s**, **mean TTFT (ms)**, **mean ITL (ms)** and **joint SLA pass share (%)**. The same tooltip is available by keyboard focus. Rows retain their job ID, concurrency N and phase. There are complete four-metric retained summaries for **256 jobs**; missing performance exports display N/A, including quality-only measurements and unscored failures. A completed scheduler state does not fill missing metrics.

Different loads and phases stay separate; the tooltip never averages them or selects the best score. A milestone with many points shows the last six retained entries with an explicit count; clicking opens all retained points and their exact source summaries. Red/green continues to identify hardware only.

`collect_hover_metrics.py` collects metrics from exact job-directory matches in retained `summary.json` files, excluding private runtime homes. Run it before `build.py` to refresh this source index. The complete graph view now embeds the same 419 job nodes as the inventory; the 31-milestone option is a grouped explanation, not a separate count of experiments.

The complete offline viewer also has a lossless [compressed copy](index.html.gz), retained directly in Git. If recovering only from Git, run `gzip -dk index.html.gz` in a new directory and open the extracted HTML; it already includes both graph views and the hover data. The extracted HTML exceeds the normal inline capture size, while this compressed copy preserves the exact bytes without a separate object download.

## Rebuild and GitHub Pages

Run `python3 build_viewer.py` from this directory to rebuild the standalone HTML and deterministic gzip from retained JSON and SVG inputs. Graphviz is required at build time for concise milestone labels. The existing `build.py` calls this renderer after refreshing the source graphs. The viewer itself requires only a browser; no analytics, external fonts, scripts or API requests are used.

`viewer/prepare_pages.py --output <empty-directory>` decompresses the reviewed `index.html.gz` into the team site: `index.html`, `.nojekyll` and the HPC companion at `hpc/index.html`. GitHub Actions deploys only those two staged files. The workflow source is retained in `workspace/publication/github-pages/ai-research-pages.yml` and installed as `.github/workflows/ai-research-pages.yml` in the archive. Later data changes must rebuild and capture the gzip to update the hosted snapshot.

## Team HPC companion

The public atlas now also includes [the HPC team’s OpenFOAM investigation](https://trungdangtapcode.github.io/apac-hpc-ai-2026/hpc/). The header switches between AI and HPC. HPC retains its own units, evidence levels and NSCC/Iris colours; its 15 curated milestones are not an allocation census. [Integration, source-preservation and browser checks](../team-research-atlas-20261104/README.md).
