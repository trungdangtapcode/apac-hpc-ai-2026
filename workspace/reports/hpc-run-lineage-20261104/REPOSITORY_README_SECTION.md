## HPC research at a glance

**17 curated OpenFOAM CPU research milestones · NSCC and Iris kept separate.** The map follows the questions, changed settings, measured outcomes and decisions, including losing branches and incomplete tests. Retrospective snapshot: 4 November 2026; retained reviews through 3 November.

[![OpenFOAM CPU research journey: NSCC in orange and Iris in blue](workspace/reports/hpc-run-lineage-20261104/journey.png)](workspace/reports/hpc-run-lineage-20261104/journey.svg)

**Click to zoom.** Orange identifies NSCC CPU and blue identifies Iris CPU. Dotted arrows show the next research question; solid arrows identify a repeat. Node labels distinguish baseline reproduction, observations, qualified signals, mechanisms and rejected performance claims. This is a curated overview, not an exhaustive allocation count.

NSCC job **25940700** reproduced the organizer recipe at **3.364622070 seconds/step**. On Iris, supplied teammate settings had a qualified **11.2228% lower mean** against their own control; our decomposition and graph-placement branches have **no stable matched win**. The selected **21.0512 seconds/step** graph arm used only **14 steps** and does not establish first place. Different platforms, allocations and horizons are never combined into a speed ranking.

**Explore:** [research guide](workspace/reports/hpc-run-lineage-20261104/README.md) · [PDF](workspace/reports/hpc-run-lineage-20261104/journey.pdf) · [milestone CSV](workspace/reports/hpc-run-lineage-20261104/milestones.csv) · [offline hover/zoom viewer](workspace/reports/hpc-run-lineage-20261104/index.html.gz). Extract the viewer and open it locally; GitHub displays the static map above.

