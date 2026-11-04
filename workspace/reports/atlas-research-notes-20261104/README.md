# Source-linked research notes and Markdown reader

The owner requested readable, detailed explanations rather than a plain-text change sentence, and specifically asked how the NIXL idea arose, what research supported it, which code changed and where the evidence is.

## Authored material

There are 31 AI and 15 HPC retrospective notes. Each separates the research question, rationale, exact runtime or study-design changes, measurement evidence, findings, decision, limits and sources. The notes preserve failed and losing branches. They are newly written explanations from retained records, not fabricated original pretrial diary entries. Fifty-eight referenced source files were checked for existence and SHA-256; every one is already tracked in the public archive. The complete underlying AI and HPC data records are unchanged.

The NIXL override gives an expanded source-level investigation: job 22271's warmup timeout, reserved-pool enumeration, the two changed functions, safe coalescing conditions, CPU recording-stub comparisons across 720 cases, the representative descriptor geometry and real job 22294's result. It links original/patched code, the patch, test harness, geometry record, logs and review. Descriptor counts are not interpreted as a speed ratio; historical recovery is kept separate from the later selected recipe.

Canonical material: [research-note index](../team-research-atlas-20261104/research-notes/README.md). The build validates every curated milestone has a note and all linked local sources exist. UI rendering and live-publication checks are added as the reader is completed. No scheduler, GPU, VPN, submission or original HPC-science file was changed.

## Reader implementation and validation

The selected record now offers Read investigation. A wide reader presents Markdown as headings, lists, before/after tables, measurements, code blocks and source links, with a section outline and Markdown download. The compact sidebar's Analysis/Context also uses formatted headings and intervention bullets. The original records and metric exports are retained; new explanations are a separate embedded notes layer.

The browser test rendered all 46 notes, checked NIXL's eight outline sections, three tables, two code blocks, exact patch/test links and Markdown download; then exercised the HPC note, Escape close and mobile width. It observed no JavaScript errors and only one document request, since notes are embedded. A small parser check confirms raw HTML and javascript links cannot become executable markup. The source AI and HPC payloads equal the preceding release; notes are explicitly new retrospective material.

`build_notes.py` emits the canonical Markdown and validates source paths; `build_unified.py` embeds the notes with the existing data. No third-party Markdown runtime or note API is required. Live publication verification is recorded after deployment.

## Verified public reader

Actions run 41815319767 succeeded from 26e500df. Public HTML returned HTTP 200 and matched the reviewed SHA-256 450528ea38296bbce16dced3f9aca6d2027a1a29fe1ebc65f19f502775b12330. Hosted Chromium opened the NIXL investigation and verified its three tables, two code blocks, eight contents sections and exact send-function name. All 31 AI and 15 HPC notes are embedded; no JavaScript errors occurred. Publication receipts are retained here.
