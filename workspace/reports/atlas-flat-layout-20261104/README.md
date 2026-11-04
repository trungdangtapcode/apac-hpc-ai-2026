# Flat layout and compact evidence inspector

The owner requested fewer rounded surfaces and less paragraph-heavy UI. The current layout replaces scope cards with a ruled counter strip, removes decorative copy and redundant labels, uses square graph nodes and panels, and reduces controls/tooltips to small corner radii. Graph node geometry is replaced at mount without changing node IDs, positions, evidence or relationship endpoints.

The inspector defaults to a four-metric definition list for AI, or the recorded result and classification for HPC, followed by compact job/configuration fields and navigable connections. Full original outcomes and changes are behind Analysis/Context; every measurement remains available in a table and source references remain expandable. HPC qualification wording is preserved in Context. The data payload remains exactly equal to the preceding release.

This is display composition only: source AI/HPC scientific records, measurements, submissions, budgets and jobs are unchanged. The original module selection logic still controls selection and navigation; a shared display renderer compacts the selected record.

Browser checks cover all 465 graph nodes, 31 AI milestones and 419 allocations, 15 HPC milestones, square panels, metric readout, zero visible default AI inspector paragraphs, full analysis, all 13 measurements on the first milestone, the qualified HPC context, job lookup/hover, independent task state and 390/820/1440 px widths. No JavaScript errors. Final tooltip corner changes are styling only. Live deployment is checked separately.

## Live verification

Actions run 41804014366 succeeded from 9dcfcd93. The public root returned HTTP 200 and exact reviewed HTML bytes (SHA-256 026568285f67b2693d57d264f66c88248d2aa081cb50e358210c7951c67545c5). Hosted Chromium confirmed 465 square graph nodes, zero-radius panels, four metric readouts, no visible default AI inspector paragraphs and no JavaScript errors. Receipts are retained in this directory.
