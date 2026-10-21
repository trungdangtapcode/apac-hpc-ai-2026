# HPC research milestone — 21 October 2026

**Question and prior evidence.** After clarifying that published R2/R5 requires
Basic work for both tasks, the owner requested HPC research and said someone
else supports AI. Earlier Qwen-only scope is superseded for this research.
No team HPC baseline or HPC submission evidence is available. Existing AI
jobs, payloads, spending controls and accepted results are preserved.

**Research and exact sources.** Main resolves to
b4df52907f5bbb9152ef6ae902c925fc79d54417. Freeze 177 selected public files with
Git blob verification and SHA256 provenance. Read the current rules/addendum
and Iris/Gadi/ASPIRE-2A application notes. Independently recompute 21 public
reference runs, including all measured step averages, final Cd and every
available partition's cell/interface consistency. Retain source-owner labels;
none are our jobs. Native OpenFOAM-v2512 tag resolves to
87ed40d256d22ea38fcc648dfc82a22162427b18; inspect pinned Scotch tree-coefficient
handling and its actual coefficient-reader path, with COPYING retained.

**Observations and units.** Four-node Gadi hierarchical/scotch averages are
2.379600/2.126043 seconds per step at 416 MPI ranks. ASPIRE-2A defaults give
3.414517/3.575991 at 512 ranks. Repeated ASPIRE Scotch spans about
3.191–3.576 seconds per step with the same coefficient.dat bytes. This is
observed run variation on different node sets, not a universal noise model.
ASPIRE hierarchical's cell imbalance is about 0.002% but worst-rank interface
faces are 119,912; Scotch has about 1.072% cell imbalance and 22,214 worst-rank
interface faces, with maximum neighbor count increasing 20→66. Global cut
faces do not establish off-node communication or a causal bottleneck.

**Assessment and hypothesis.** Prioritize a valid Basic baseline and native
hierarchical/scotch decomposition over random MPI/compiler sweeps. A first
distinct candidate keeps method scotch but sets domains/domainWeights to reflect
actual node/rank grouping. This is supported by pinned native code and F1's
chosen-method coefficient allowance. It is not method multiLevel, not a code
patch, and has no measured speedup yet. processorWeights takes precedence in
the implementation; verify actual parsing and placement before any benchmark.
Other hypotheses are ranked in PLAN.md, with matched controls and repetition.

**Costs and correctness.** Public split-chain Scotch 1/2/4-node examples total
about 217 SU on Gadi and 167 SU on ASPIRE-2A. These are historical costs, not our
reservations or available credit. Basic keeps double precision, fixed numerical
work, all preparation and function objects; GPUs are forbidden. Basic Cd is
a sanity check, not a universal ±0.5% gate. Apply F3's matched-baseline rule
only where required for Bonus, preserving its method-only exception. Keep
solver Average, total walltime and billed service units separate.

**Failed attempts and corrections.** Original/relocated case URLs could not
provide the full case; a sign-in page is not retained as source. An initial
native source parent-path lookup returned 404; the correct path was found and
retained without erasing that observation. A broad parser fatal-string match
was corrected before acceptance to exclude the ordinary trapFpe startup line.
Published ASPIRE default MPI teardown faults stay visible, not relabelled as
clean jobs; the official runtime remedies require matched site validation.

**Access.** Existing AI SSH reaches ASPIRE-2A+ and does not establish CPU
ASPIRE-2A access. The owner said they have Iris or Gadi, then supplied a key
path and endpoint. First SSH rejects 0644 key permissions; chmod 600 fixes it.
Both non-login and login-shell checks then return instance-20210305-2210,
with no scheduler in PATH and no documented Iris kit. A local relay alias iris
refers to that same endpoint, not proof of another compute service. Other
users' Gadi aliases are not used. Next-hop/real-cluster clarification is pending.
No private key contents, authentication state or host-key cache enters research.

**Next decision.** Obtain the genuine practice kit and our own contest project,
then validate the entire Basic chain on Iris before a bounded CPU campaign.
No HPC job, mesh download, install or reservation occurs here. Candidate JSONs
are explicitly unsubmitted. Keep HPC_Task empty until actual reviewed evidence
can support an authorised package update. Autopilot remains off.

**Preservation.** Initial source/access/scope checkpoint 88765a0 was pushed
before the derived analysis and plan. This milestone retains English readable
reports, native-source provenance, analysis code/results, candidate definitions
and access limitations in a second small checkpoint. Git and live origin are
verified; no sensitive SSH material is captured.
