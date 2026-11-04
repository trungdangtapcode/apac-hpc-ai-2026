# AI research atlas polish

The owner requested a more usable interactive graph and GitHub Pages hosting. The viewer retains the original 419 allocation records, 31 curated milestones and 27 documented relationships. Original inventories, measurement JSON and source diagrams remain byte-identical to the preceding archive capture.

The new interface has a readable initial milestone, compact screen labels, drag/pan and wheel/button zoom, platform/search filters, next-match navigation, an inventory table and filtered CSV export. Hover shows four rounded metrics from the latest retained point with its job/load/phase. Selection shows all retained points plus change, outcome, typed relationships and repository source references. Missing measurements remain N/A. The two GPU platforms retain red/green identities, textual platform labels and separate scientific interpretation.

The standalone HTML embeds its data, styles and scripts. There are no external font, analytics, API or JavaScript dependencies. The public rendering converts machine-local paths to repository references. The deterministic compressed HTML is directly Git-tracked so hosting and offline recovery do not need the external object store. Raw objects referenced by research documents are not automatically included in Pages.

`browser_check.py` ran with Playwright and Chromium 148 using a temporary environment. `browser-results.json` records node counts, all four hover fields, exact-job search/detail, measurement table, H100 count, filtering, selection, zoom, pointer drag, mobile width and absence of JavaScript errors or external requests. Screenshots are retained. Drag was exercised but its displacement was not numerically asserted; touch pinch and screen-reader traversal were not tested. The 390 px viewport has no document-level horizontal overflow.

GitHub Pages uses a separate workflow checkpoint to publish only the decompressed viewer. No research jobs, submission payloads, slide files or HPC materials were changed.
