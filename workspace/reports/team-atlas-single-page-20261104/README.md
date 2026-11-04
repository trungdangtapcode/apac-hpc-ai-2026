# Single-page team atlas revision

The owner explicitly requested one page and one UI after the earlier two-route integration. The published product now has a common introduction, shared task selector and in-place explorers. Switching tasks does not navigate or load another document. Both task datasets are embedded; no iframes, runtime API requests or external frontend dependencies are used.

Design choices: a concise team-level summary distinguishes 46 curated milestones from 419 AI allocation records; two task cards give an immediate choice without repeating the page introduction. A sticky task selector remains available while exploring. The active task identifies its units and comparison direction. Shared styling and controls provide consistency while each task keeps its own evidence labels, platform colours, filters and selected item. Deep links and browser history use #ai/#hpc. The former /hpc/ path redirects to the same document.

The build composes the existing tested components into namespaced sections, initialises each only when first opened and keeps its controller state separate. 818 HTML/SVG IDs are unique. The single page is self-contained and its deterministic gzip is directly Git-tracked. Raw AI inventories/measurements and the HPC milestone JSON are unchanged. No claim is added about HPC measurements or cluster state.

Browser checks: 31 AI milestones, 419 AI allocation nodes, 15 HPC milestones, all four AI hover fields, the HPC practice tooltip and qualified teammate result, five NSCC milestones, preserved independent search and selection across repeated switches, no extra document request on switches, no iframe, keyboard switching, direct #hpc entry and legacy redirect. The 390 px mobile viewport has no horizontal document overflow. No JavaScript errors occurred. Saved screenshots cover both tasks and mobile. Touch pinch and assistive-technology traversal were not tested.

The earlier two-route README is preserved as PREVIOUS_TEAM_README.md. Older standalone component/browser receipts remain historical. Current deployment verification is recorded separately after publication. Submission files, research jobs and the original HPC report remain unchanged.

## Public verification

Actions run 41793272928 succeeded from c91d6c8b. The root URL returned HTTP 200 and SHA-256 ea978fdc8bdd69088a98ef3edcd7d4b3d0418a95bc8e2552c02638b095966ccf, exactly matching the reviewed single-page HTML. Hosted Chromium checks confirmed both track node counts, preserved HPC search and zero document requests caused by repeated task switches. No JavaScript errors occurred. Deployment, HTTP and browser receipts are retained in this directory.
