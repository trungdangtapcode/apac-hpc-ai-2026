# Figure usage and provenance

Use the SVG files when placing figures in slides; PNG copies are for direct viewing. All labels are English and state units. Source review hashes, chosen series values and figure hashes are in provenance.json. The generator is ../render_figures.py with pinned ../requirements-figures.txt.

- research-journey: follows the actual 21–23 October HPC reasoning and preserves the failed NUMA branch. The final repeat/profile box is a research direction; confirmation 25940700 is submitted, with no reviewed result yet.
- four-node-means: six complete native 150-step records, 149 timed samples each; all samples retained. Requested CPUs differ and final accounting is unavailable. No error bars or accepted-score claim.
- observed-scaling: one coherent shared 128-rank/node series for each method at prescribed 40/80/150 endpoints, not cherry-picked historical minima. Separate allocations and different endpoints prevent a controlled identical-work speedup claim.
- iteration-spikes: every native Time 2–150 sample for the two 128-rank/node four-node observations. The Scotch Time-119 maximum remains in the mean. This does not establish a hardware or MPI cause.

The PNG previews were visually inspected; matching SVG versions were exported from the same figures. They are derived teaching assets, not raw benchmark data or replacements for full logs.
