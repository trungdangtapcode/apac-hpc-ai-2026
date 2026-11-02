# Submission delivery check — 2 November 2026

## Result

**Package integrity: PASS. Portal submission readiness: not fully confirmable.** The current team folder, published ZIP, and 1 November reviewed release ZIP contain the same presentation and AI package bytes. The ZIP passes CRC and path/member checks. This audit checks package integrity and routing; it does not certify the scientific correctness of the HPC track or prove that organizers have received the package.

## Verified artifacts

| Item | Check | Result |
|---|---|---|
| Presentation in the live folder | SHA-256 | `1ba55e8007f0ef7796076a35e82a1afc372a706c13500b80fbf9b27d723a2195` |
| Presentation inside published ZIP | SHA-256 | Same as live folder; one deck member |
| Published ZIP | SHA-256; size | `a0da31120fa6cb5d1c49bfbb693ca74af20610e5cf368f9c3cc18dd703c3659e`; 148,233,835 bytes |
| ZIP sidecar | SHA-256 | Matches ZIP |
| 1 Nov reviewed release ZIP | SHA-256 | Same as published ZIP |
| ZIP structure | CRC, duplicate names, unsafe paths, symlinks | CRC clean; no duplicate names, unsafe paths, or symlinks (2,327 members; 2,015 files) |
| Presentation routing | Published validator | 42 slides: 16 visible AI slides, 18 hidden AI backup slides (17–34), and eight preserved HPC slides (35–42); visible sequence is 1–16 then 35–42 |
| Presentation PDFs | Page counts | Main talk 24 pages; full deck 42 pages |
| Bilingual transcript PDFs | Page counts | English 109 pages; Vietnamese 104 pages |
| Per-surface manifests | Independent manifest and SHA256SUMS verification | Folder: 2,025 manifest entries and 2,026 checksum lines, no mismatches. ZIP: 2,013 manifest entries and 2,014 checksum lines, no mismatches. |
| AI package files | Folder/ZIP byte comparison | No AI file differences |
| Scoped secret scan | Credential filenames and targeted private-key/token/credential patterns in ZIP | No matches |

The deterministic published validator passed. It confirms the slide sequence, 68 protected HPC presentation dependency parts, 116 explicitly packaged AI files, nine score exports, nine lossless request exports, and 180 working source links. The official full-set model-quality evaluation and a new complete portable GPU replay after reader repair were not performed.

## HPC preservation boundary

The folder has 277 HPC files and the ZIP has 265. The 13 folder/ZIP differences match the retained pre-existing list: 12 HPC files present only in the folder and one differing `HPC_Task/job_scripts/case/system/decomposeParDict`. The release validation also confirms unchanged hashes/modes for folder HPC files, unchanged ZIP member hashes/metadata, and unchanged bytes for 68 protected slide dependency parts. This is preservation evidence only; this check does **not** validate HPC task rules, scripts, measurements, or scientific claims.

## Remaining delivery checks

- No organizer portal upload or receipt was checked. The final upload destination, deadline, and whether supplementary PDFs are required remain unconfirmed.
- The actual PowerPoint slideshow/device check and a timed combined human mock remain outstanding.
- The QA companion created after release is intentionally outside the ZIP; it is not a package synchronization failure.

Before upload, confirm the organizer's final file/directory requirements and deadline, then upload the ZIP and verify the portal receipt. If slides are uploaded separately, use the checked PPTX hash above.
