# HPC presentation allocation and reproducible CPU submission — 23 October 2026

## Question and prior evidence

The owner asked for updated slides and job submission scripts, then constrained HPC to about 20% of the deck because AI remains the principal presentation topic. The current published source had 32 AI slides. The reviewed CPU candidate was old native job 25921488, default Scotch with 128 ranks per node across four nodes, mean 3.677906731 s/step, 149 timed samples from 150 required steps. Independent confirmation 25940700 had been submitted but had no reviewed result. The record does not imply a measured performance gain during this packaging milestone.

## Hypothesis and exact change

An eight-slide HPC section can explain the task, failed locality hypothesis, observed endpoint scaling, six four-node configurations, tail behavior, selected candidate and next confirmation without overwhelming the AI story. We appended eight slides to the 32-slide AI deck. All original AI slide parts, notes and images were preserved byte for byte; only four existing OOXML structural/metadata parts changed. The result has 40 slides, exactly 20% HPC, with eight new distinct faint photo backgrounds and matching native gradient styling. Sources and credits stay in speaker notes rather than a folder/evidence tour on the slides.

A newly derived portable PBS family embeds the accepted 43-file ASCII case and permits only rank count and official endTime derivations. The main entry requests four exclusive CPU nodes, 128 ranks/node, 440 GB/node, 40 minutes, no GPU, default Scotch and 150 steps. One/two-node scaling scripts use 40/80 steps. All scripts retain the full original initialization, DP precision, fixed numerical work, source/mesh pins, explicit stage exits and output validation. The new bundle is not the submitted payload that produced the historical records. Old collected launchers are retained separately as historical, not retroactively called frozen.

## Observations and verification

Offline Bash and Python 3.6 grammar checks, 58-file bundle seal, positive 1/2/4-node case derivations, wrong-endTime/missing-mesh guards and a spaced-path launcher check passed. The native validator replayed logs from 25921487/25921492/25921488: 14.450756959/7.462835189/3.677906731 s per step, 39/79/149 timed samples respectively. The missing-End negative check was rejected. These are validator replays, not new compute runs. The driver avoids nounset around externally sourced site module and OpenFOAM scripts while retaining explicit required-variable checks; that fix was backed up separately.

The PPTX contains 40 slides; its paired coordinate-based PDF contains 40 pages. All internal OOXML relationships resolve, all notes are present in English, and all 40 background hashes are distinct. A retained-input rebuild reproduces every package part's bytes and the notes; ZIP timestamp bytes may differ. Publication verified 376 protected AI files, ZIP CRC and each package file hash, and backed up the predecessor before updating the ZIP. The PDF/previews are not Office renderings. No organizer upload occurred.

Packaging review also caught a real deployment issue: atomic publication and ordinary ZIP extraction did not preserve the driver's executable permission. We changed the three entry points to invoke it through `bash`, then tested the actual extracted package with a mode 0644 stub driver and a directory containing spaces. All three launchers passed. A retained-input rebuild initially used the input filename as the output name; that path error was fixed and all 270 output part bytes and speaker notes were then verified identical. Neither check runs OpenFOAM or consumes SU. These corrections preserve failed checks rather than treating an untested package as complete.

## Access failure, correction and live status

VPN was found disconnected. A 14:55 authentication attempt failed without a proven cause. The owner authorized another DUO attempt; VPN reported connected at 15:04:45 UTC. A separately authenticated CPU master reached asp2a-login-nscc02 and read-only PBS checks succeeded. No private cache was removed and no AI connection was reset. The retained scheduler JSON at 15:06:39 UTC still shows 25940700 Q/q5 because node_pool resources are insufficient. An intermediate draft used a guessed 15:09 label; the published deck corrects it to the actual 15:06 observation. Phone-side approval and exact future session lifetime were not observed.

## Assessment, limits and next decision

This milestone improves explanation, portability and preservation, not the measured solver score. No new qsub, cancellation, reservation retirement, cost or budget increase occurred. The independent confirmation keeps its queue position under the existing 5,000-SU conservative CPU ceiling. Historical four-node scheduler exit/resources and some original-payload/field/core proof remain incomplete; the extra checks are our internal confidence measures, not invented official scoring requirements. No causal tail bottleneck, global optimum or official acceptance is claimed.

Next inspect 25940700 when it finishes: all stages, complete native outputs, tail samples, startup/core evidence, mesh/source/field checks and terminal PBS state/accounting. Choose the next distinct runtime hypothesis only after that review and a fresh budget/queue check. Keep the losing NUMA decomposition closed. The script/slide/package checkpoints are explicitly captured and pushed; large external artifacts still need an independent off-host copy.

## Sources

- [Published package and checks](../../../../submission-review/hpc-update-20261023/README.md)
- [Learning and concise presentation script](../../../hpc-research-journey-20261023/TALK_TRACK.md)
- [Four-node review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md)
- [Access recovery and retained scheduler snapshot](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/access-recovery-20261023T1504/REPORT.md)

A final read-only scheduler check at 23 October 15:20:58 UTC still showed 25940700 Q/q5 with insufficient node_pool resources. The frozen presentation preserves its 15:06 snapshot; no new measurement or queue action followed.
