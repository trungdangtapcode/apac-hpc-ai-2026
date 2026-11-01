# Final submission readiness — research complete, release handoff still pending

Checked **2026-11-01T11:15:41.894615+07:00**, Vietnam time (UTC+7). This is a fresh audit of the exact
current team ZIP and slide deck, not an organiser upload or a new benchmark.
The AI research and the four distinct H100-derived intervention reviews are
complete. No useful incumbent goodput gain was established; keep the selected
H200 N64 recipe and its historical reproduced performance claims.

## Verified now

| Surface | Result |
|---|---|
| ZIP | CRC passes; no duplicate/unsafe member names or symlinks; 1906 files |
| ZIP manifest/checksums |1904 manifest entries and 1905 checksum lines validate; zero missing/bad hashes |
| Working folder manifest/checksums |1916 manifest entries and 1917 checksum lines validate independently |
| AI shell/Python |11 syntax checks pass |
| Portable setup | Exact script/tokenizer payload copied to a neutral path with spaces; setup.sh --check passes |
| AI official protocol | Static review matches native FP8 target, 16 GPU PD, gateway, N64, fixed 4000/200, seed 2026 and 60/120/30 |
| Shared runtime assets | Expected images/model metadata available to current user; images root-owned 0644, parent directories 0755 |
| Deck |40 slides: 16 main AI, 16 hidden AI backups, 8 HPC; current main PDF has 24 pages |
| Own H200 queue | Empty in this observation |

The folder has 1918 files and the ZIP 1906. The 13 documented HPC differences are
pre-existing and deliberately preserved. Each surface has a valid manifest for
its own bytes; the two global manifest files should not be forced to match.
Do not rezip the working folder and silently replace the reviewed HPC snapshot.
The tokenizer cache is needed for offline reproduction and contains vocabulary/
configuration assets, not model weights or authentication caches. Scanned ZIP
text/paths showed no credential-assignment or auth-cache findings; that is a
scoped scan, not a claim about every possible hidden binary property.

## Remaining checks and decisions before calling the whole package final

1. **Align the presentation materials.** Packaged AI logs/PRESENTATION_PLAN.md
   still describes the old 32-AI-slide route. Current deck has 16 main AI +16 hidden
   backups and unchanged HPC 33–40. Add a short dated appendix/guide summary of
   the nine late H200 verification runs and their no-win decision, without
   turning the main talk back into an experiment-by-experiment timeline. Keep
   deck, PDF, bilingual guides, notes and package references on the same version.
2. **Recommended final portable GPU acceptance.** The exact current primary has
   not completed a full allocation after its reader repair. 27136/27145 passed
   actual serving/semantic/client stages but failed in postprocessing; 27152
   later verified the corrected exact readers on compute CPU. One final run of
   the frozen packaged submit.sbatch through scoring and cleanup would close
   that remaining end-to-end gap. It is not a new optimisation sweep or an
   extra mandatory organiser deliverable. No GPU job was started by this audit.
3. **HPC owner handoff.** Confirm that the reviewed ZIP snapshot is the intended
   final HPC submission. Its documented differences from the live working
   folder must be accepted by its owner or replaced by that worker's reviewed
   publication. This AI session neither merges nor changes the other track.
4. **Human rehearsal.** Test the actual PPTX application, hidden-slide navigation,
   main PDF fallback, microphone/screen sharing and speaker handoff. Rehearse
   the combined Qwen+OpenFOAM interview, then exercise evidence-backed Q&A.
   The published HPC task rules explicitly specify one shared 15–20 minute
   presentation and 10 minutes of Q&A, with time split chosen by the team. Earlier
   "official combined duration unknown" notes are historical for the public
   rule; only a special assigned invitation/override remains uninspected.
5. **Delivery logistics and freeze.** Confirm the real final-upload destination,
   deadline/timezone and file-size limit from the organiser's actual message.
   They were not found in the inspected public rules or retained final-delivery
   notes. The accessible proposal-registration form is not assumed to be the
   final result portal. Freeze one deck/ZIP/checksum after all authorised edits.

## Official accuracy is a validation boundary, not an invented missing file

The current [Qwen rules](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/1.%20Qwen3%20AI%20Task%20Rules.md#q1-basic-vanilla) say organisers reconstruct the stack under a dedicated account and run
their full-set accuracy check, with a 99%-reference pass line. Team smoke/retrieval
checks do not certify that result, and its outcome remains UNKNOWN. Do not claim
99% was passed; also do not invent a requirement that the team must first run an
unprovided official dataset before it may submit a Basic package. Bonus claims
would need the corresponding correctness proof and same-platform own-baseline
comparison; unproven speedups stay out of the claimed result.

The published [combined presentation rules](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/2.%20OpenFOAM%20HPC%20Task%20Rules.md#presentation-guidelines) and [scoring addendum](https://github.com/hpcac/2026-APAC-HPC-AI#r4-scoring) were checked online on 1 November 2026. They support a concise
problem/evidence/decision talk; both tasks require their Basic result.

## Exact audited release

- ZIP: VNUHCM - TripleU.zip; 119,982,571 bytes.
- ZIP SHA256: 23192cb9b708935f0c3d1d4af044b98e8cbe5d015f2941cfb4fff571f78fc895.
- PPTX SHA256: dcc56658f7efa1b43294d32316de4eb27c65d765d2a9f1806e18c67a40ca9d13.
- [Structured preflight](preflight.json), [fresh neutral-path AI setup](offline-ai-preflight.json).

No packaged file, submitted frozen payload, HPC content, GPU budget or scheduler
state was changed. No organiser upload, authentication or background schedule
was performed. The published ZIP/PPTX remain the audited versions above.
Large research artifacts remain in the separate local store; Git recovery
metadata alone is not an off-host copy of those  bytes.
