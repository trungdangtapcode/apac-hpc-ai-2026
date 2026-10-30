# Engineering investigation: response to the presentation feedback

This edition changes the argument, visuals and speaking logic rather than merely renaming chronological sections. It implements the detailed feedback supplied by the owner. No new benchmark, profiling, model-quality evaluation or rehearsal is claimed. Research remains stopped.

## Three stories and their evidence class

1. **Engineering decision — use the fixed GPU budget.** Explain the tradeoff between replicas and tensor width, FP8 eligibility and correct P/D transfer before choosing two TP4 prefill workers and one TP8/EP8 decode worker. Seventeen usable measurements support feasibility and an operating choice; differing loads prevent a uniform topology ranking.
2. **Team implementation — request-scoped transfer setup.** Begin with worker readiness followed by pair-warmup timeout. Trace the source-level whole-pool enumeration, why a narrow setup intervention was worth testing, what the patch changed, CPU range checks and actual patched serving. Retain the missing unpatched scored control: this is feasibility evidence, not a descriptor-only end-to-end speedup.
3. **Experimental method and findings — improve the service objective.** Reuse existing GPU implementations and test a defined decode change under a fixed setup. Explain the +5.295% goodput result together with worse TTFT and better ITL; use independent repetition and the full N62/N64/N68 comparison to select the operating point. Do not claim the team invented the kernels, add component gains or infer a detailed kernel-time cause.

The contribution classification and relationship map are retained in investigation-contributions.json. These are different types of claim, not three independent algorithmic speedups.

## Actions against each feedback stage

| Feedback | Concrete revision | Validation boundary |
|---|---|---|
| Structure by problem and reasoning | Sixteen main AI slides: constraints, topology choice, complete KV case, profile-driven tests, measured tradeoffs, robustness and remaining claims | Four research questions remain the organising questions; not every branch shares one cause |
| Identify contributions | Explicit engineering decision, team implementation and experimental finding labels | Provided kernels and source-only findings are not relabelled original algorithm contributions |
| Redesign for reasoning | Request pipeline, claim/dependency map, resource tradeoff, architecture, failure-stage diagram, request-scoped range illustration, control/treatment setup, metric changes and decision evidence | Diagrams encode relationships; descriptor cells are illustrative, not measured traffic or exact address layouts |
| One message per slide | Message in the title and central evidence; remove the repeated bottom key-message pattern from the main argument | Hardware labels and quiet template footer remain metadata |
| Explain why one slide follows another | The bilingual guide adds problem, objective relevance, test rationale, lesson and next logical question | A prerequisite arrow is not a claim of causal speedup |
| Protect both tasks' time | Compact AI rehearsal target of 10–12 minutes; definite handoff after slide 16; hide AI backups 17–32 in slide-show mode | Official total time/Q&A inclusion is requested from the owner, not invented; HPC content remains owned by its independent presenter |
| Evidence-based questions | MOCK_QA_EVIDENCE.md links short answers, cross-examination, exact source and missing measurements | Proposed rehearsal, not a record of an actual mock or official questions |
| Final review | Check slide messages/geometry, source attribution, transcript alignment, hardware, visible slide sequence, HPC byte preservation and PDF navigation | Office rendering and a human timed rehearsal remain separate checks |

## Relationship between the investigations

Topology and FP8 compatibility determine whether a candidate is eligible to run. A particular heterogeneous-TP recovery branch exposed a pre-score transfer problem; the request-scoped patch was a response to that branch's evidence, not proof that all layouts or mature N64 performance had the same bottleneck. After usable serving is established, diagnostic profiles and request observations motivate separate controlled implementation/load tests. Repetition and held-out checks determine what can be claimed. This is an evidence/dependency argument, not a reconstructed claim that every chronological action caused the next score increase.

## What remains for the human mock

Run the compact route with the actual speakers and equipment. Time the AI-to-HPC transition and the total session. Ask a listener unfamiliar with the runs to explain the problem, why each test was chosen and what the result supports. Probe the missing-cause boundaries. Record actual times and feedback only after that rehearsal. The agent can prepare the material and perform artifact checks; it cannot report that this team mock has taken place.
