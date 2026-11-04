# Source-linked research notes and Markdown reader

The owner requested readable, detailed explanations rather than a plain-text change sentence, and specifically asked how the NIXL idea arose, what research supported it, which code changed and where the evidence is.

## Authored material

There are 31 AI and 15 HPC retrospective notes. Each separates the research question, rationale, exact runtime or study-design changes, measurement evidence, findings, decision, limits and sources. The notes preserve failed and losing branches. They are newly written explanations from retained records, not fabricated original pretrial diary entries. Fifty-eight referenced source files were checked for existence and SHA-256; every one is already tracked in the public archive. The complete underlying AI and HPC data records are unchanged.

The NIXL override gives an expanded source-level investigation: job 22271's warmup timeout, reserved-pool enumeration, the two changed functions, safe coalescing conditions, CPU recording-stub comparisons across 720 cases, the representative descriptor geometry and real job 22294's result. It links original/patched code, the patch, test harness, geometry record, logs and review. Descriptor counts are not interpreted as a speed ratio; historical recovery is kept separate from the later selected recipe.

Canonical material: [research-note index](../team-research-atlas-20261104/research-notes/README.md). The build validates every curated milestone has a note and all linked local sources exist. UI rendering and live-publication checks are added as the reader is completed. No scheduler, GPU, VPN, submission or original HPC-science file was changed.
