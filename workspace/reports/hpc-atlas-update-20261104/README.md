# HPC update in the hosted team atlas — 4 November 2026

The owner clarified that diagram updates must reach the existing GitHub Pages team atlas, which contains both AI and HPC: https://trungdangtapcode.github.io/apac-hpc-ai-2026/#hpc . This is now the delivery target for HPC diagram updates; standalone SVG/README remains a secondary reproducible output.

The hosted HPC milestone and its investigation reader now include the reviewed native preparation-policy job 2294676: 22.163497501 versus 21.771496718 seconds/step, 1.768677456% lower pooled time, with conflicting adjacent comparisons (+0.73172% /−4.20539%). Four native replays and force trajectories pass. The result remains qualified; a reversed longer confirmation is proposed and not submitted. No newer solver result was invented. Source links lead to completed review and independent replay, replacing stale accepted/unreviewed wording.

The build has a new `--hpc-only` option. It reuses the existing AI component, then composes both tracks with the original shared UI. All 35 protected AI component/data/note files remain byte-identical; the embedded AI data is equal. Browser checks validate the native investigation, AI/HPC switching, 419 AI allocations /31 AI milestones and mobile width 390. The generated page contains 15 HPC milestones. The build does not query queues, start VPN or submit a job.

Run `python3 workspace/reports/team-research-atlas-20261104/build.py --hpc-only`. The existing Pages workflow stages only the reviewed generated HTML and redirect, excluding the repository root. A push of the captured team `index.html.gz` triggers deployment; deployment and served-byte verification receipts are recorded alongside this review.

## Published verification

GitHub Pages run 41825455762 completed successfully for source commit `d572069b`. The live root returned HTTP 200 and exactly matched the reviewed HTML SHA-256, `6483754c86515e31be109c9062ff8cea966561a18337f4adc87f34c55c3d23be`. See `deployment.json` and `published-verification.json`. The `#hpc` entry opens the shared page directly at the HPC track.
