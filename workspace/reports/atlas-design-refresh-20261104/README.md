# Research workspace visual redesign

The owner rejected the prior large-heading layout and requested visual inspiration and/or generated artwork. The new one-page interface is a working research dashboard: persistent dark navigation, a restrained light graph canvas, compact task-specific scope cards, a fixed-width evidence inspector and an original generated sidebar asset. The marketing-style introduction is removed. Supporting evidence-reading notes are collapsed but remain available. Controls and evidence text have increased font size and contrast; colour semantics remain explicit, with green/red H200/H100 and orange/blue NSCC/Iris. Purple is a selection/control accent.

Switching tasks still uses one document with independent state. The sidebar sets the active task, scope cards are derived from its existing records, and the header states the applicable metric direction. HPC uses milestone/connection/platform counts, never the AI allocation count or latency metrics. Neither a decorative image nor a compact counter is presented as scientific evidence.

[Visual references and generated-asset provenance](SOURCES.md). Only original generated art is shipped. The page and generated WebP are embedded in the deterministic standalone HTML; the directly tracked gzip remains sufficient for Pages deployment and offline restoration.

The complete embedded research payload is equal to the prior published payload. No underlying AI/HPC records, measurements, queues, budgets, slides or submission files changed. The new build and source CSS/HTML are reproducible through the team atlas build.

`browser-results.json` records functional regression checks: AI 419 allocations/31 milestones, HPC 15 milestones, metric hover, job lookup, retained filters and selected items, keyboard switching, hash entry, redirect and no reload/iframe. `design-checks.json` records the unchanged data payload, embedded asset, H200 legend colour, correct task-specific counters and no horizontal overflow at 390/820/1440 px. Screenshots retain the final UI. No JavaScript errors were observed; touch pinch and screen-reader interaction were not tested. Live deployment is verified separately after publication.

## Verified publication

Actions run 41799178728 succeeded from 2ce270d5. Public HTTP returned 200 and SHA-256 9ea8fb79f16974cd5c79186dc50e7a84a88033858758f4ddabc46394a88e4607, exactly matching the reviewed redesigned page. Hosted Chromium verified the fixed sidebar and embedded generated asset, 31 AI/15 HPC milestones, task-specific counters, no additional document requests on track switches and no JavaScript errors. Deployment, byte-comparison and browser receipts are retained here.
