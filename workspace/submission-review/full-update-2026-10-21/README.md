# Full submission build and review — 21 October 2026

See ../../notes/submission-update-20261021.md for the delivered package and limits.
This directory preserves frozen inputs, editable slide content, previews,
validation and source provenance. The VNUHCM - TripleU staging tree and
updated-package.zip are build products; the published delivery is in workspace.

Build dependencies are pinned in requirements.txt. With those installed, run
workspace/submission-tools/prepare_full_update_20261021.py to create a new stage,
then freeze_full_update_20261021.py, build_research_update_20261021.py,
package_evidence_20261021.py, validate_full_update_20261021.py and finally
publish_full_update_20261021.py. The stage builder refuses an existing stage;
use a fresh restored layout rather than overwriting frozen evidence. The frozen
presentation-data.json suffices for rebuilding the deck without rescanning.
All tools currently resolve the original /home/apacsc42 workspace layout;
restore that layout or adapt these build-only paths. The submitted primary
Slurm scripts themselves are portable across accounts and paths with spaces.

The GPU-free mock verifies orchestration using retained artifacts. It is not a
new inference benchmark. PDF previews use shared coordinates, not an Office
renderer. The publisher checks current source hashes and preserves the prior
full delivery before replacing it. No organiser delivery or GPU submission is
performed by these packaging tools. Background licences/credits remain in the
package and source manifest; photos illustrate infrastructure, not these clusters.
