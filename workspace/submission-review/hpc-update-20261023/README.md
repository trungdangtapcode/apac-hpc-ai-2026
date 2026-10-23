# Combined TripleU presentation and HPC submission update

The owner requested that HPC occupy about 20% of the presentation. The published
PowerPoint contains **32 existing AI slides plus 8 HPC slides, 40 total**. The
original AI slides, speaker notes, images and supporting payloads are preserved.
Their inherited section footer numbering remains unchanged; HPC is numbered 33–40.
The new HPC section explains the fixed computation, full initialization, failed
NUMA hypothesis, observed scaling, rank density, slow-step tails, selected
configuration and independent confirmation. Sources and image credits are in
speaker notes. The slides contain presentation material rather than a folder tour.

## Deliverables

- [Published presentation](../../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx)
- [Combined 40-page PDF](TripleU_APAC2026_Presentation.pdf)
- [Combined speaker notes](PRESENTER_NOTES.md)
- [HPC script and native logs](../../VNUHCM%20-%20TripleU/HPC_Task/)
- [Team ZIP](../../VNUHCM%20-%20TripleU.zip)
- [Publication checks](publication-validation.json), [merge checks](merge-validation.json),
  [script checks](script-validation.json)

The default CPU entry is `HPC_Task/job_scripts/submit-best.pbs`: four nodes,
128 MPI ranks per node, default Scotch, 150 steps. One/two-node scripts are scaling
checks, not instructions to run three jobs simultaneously. Use authorized
project/mesh paths and the normal research budget/queue policy. The directory
contains the original ASCII case and mesh identity pins, not a large mesh archive.

The historical four-node native record 25921488 has mean 3.677906731 s/step.
The new portable scripts did not produce that record. Native-output validator
replays pass, but a new compute replay has not been performed. Independent
confirmation 25940700 is Q/q5 in the retained **23 October 15:06:39 UTC** scheduler
snapshot, waiting for node_pool resources. No new score or organizer acceptance
is claimed. The preceding draft used a guessed 15:09 label; the published deck
corrects it to the actual 15:06 observation.

## Verification and reproduction

The OOXML merge preserves 201 original package parts byte for byte, including all
AI slide parts and notes, and appends the eight HPC slides. Only four existing
structural/metadata parts change. Every internal relationship resolves. The ZIP
passes CRC and file-hash comparison; 376 AI scripts/raw/supporting files are
protected, with only global presentation/checksum metadata refreshed. All 40
slides have distinct background images. PPTX backgrounds use an 86% paper wash;
the PDF uses the matching 14% photo blend. The previews share drawing coordinates
with the builder and are **not Office-rendered screenshots**.

The original 32-slide AI deck and PDF are retained in `inputs`. Rebuild the HPC
section with `workspace/submission-tools/build_hpc_section_20261023.py`, then run
`merge_hpc_section_20261023.py` in an environment installed from the section's
pinned `requirements.txt`. These builders use the documented active workspace
paths. The publisher refuses an unknown AI deck and permits only the retained original
base or the exact reviewed combined deck, allowing controlled HPC package fixes. Native source origins and hashes
are in `package/HPC_Task/logs/provenance.json`. A previous package was backed up
before publication. No organizer upload occurred.

Large PPTX/PDF/ZIP objects are retained through the research archive's external
artifact manifests; a Git push alone does not upload those object bytes.

[Final extracted-ZIP checks](delivery-validation.json) include all three PBS entry points with a nonexecutable driver and a path containing spaces. The entry points explicitly call `bash`; no executable permission bit is required after extraction. [Retained-input rebuild checks](rebuild-validation.json) verify all 270 PPTX package parts and the speaker notes.
