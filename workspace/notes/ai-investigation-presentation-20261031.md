# Engineering investigation presentation — current delivery

Updated 2026-10-31T00:53:11.262480+07:00, Vietnam time (UTC+7). Research remains stopped. This edition implements the owner's detailed feedback on reasoning, contribution ownership, visual evidence, verbal transitions, balanced task timing and defensible Q&A. It supersedes the earlier question-led draft, which still relied too heavily on tables and did not complete the KV case in the main route.

## Current files

- [PowerPoint](../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx): 16 main AI slides, 16 hidden AI backups and eight unchanged HPC slides.
- [Main talk PDF](../submission-review/ai-investigation-update-20261030/TripleU_APAC2026_Main_Talk.pdf): the 24 visible pages, AI 1–16 then OpenFOAM 33–40.
- [Full slide PDF](../submission-review/ai-investigation-update-20261030/TripleU_APAC2026_Presentation.pdf): all 40 pages for questions.
- Learning guides: [Vietnamese Markdown](../reports/ai-final-report-20261030/TRANSCRIPT_VI.md), [English Markdown](../reports/ai-final-report-20261030/TRANSCRIPT_EN.md), [Vietnamese PDF](../reports/ai-final-report-20261030/TRANSCRIPT_VI.pdf), [English PDF](../reports/ai-final-report-20261030/TRANSCRIPT_EN.pdf).
- Rehearsal: [pacing and handoff](../reports/ai-final-report-20261030/PRESENTATION_PLAN.md), [verified-source Q&A](../reports/ai-final-report-20261030/MOCK_QA_EVIDENCE.md), [feedback response](../reports/ai-final-report-20261030/FEEDBACK_RESPONSE.md).

Current transcript PDFs have 98 Vietnamese pages and 104 English pages. Each slide has hardware, evidence class for the main talk, a short spoken brief and explicit problem/relevance/test/lesson/transition explanations. The longer technical reference remains below. The requested Vietnamese exception remains limited to learning guides and bilingual source data; submission slides are English.

## What changed

Three complete stories carry the main argument. The layout is an **engineering decision** supported by eligible measured candidates, not a uniform topology contest. The request-scoped NIXL patch is a **team implementation** whose CPU and real-serving checks support patched-path feasibility, not an isolated speedup factor. The matched implementation/load campaign is **experimental method and findings** using existing kernels, not a claim that the team invented those kernels.

The main visuals now include a request objective, ownership/dependency map, replica/width tradeoff, architecture, warmup failure stage, before/after range construction, controlled setup, measured tradeoffs and open validation boundaries. The main slide titles carry their key message; repeated footer takeaways and most main-route tables are removed. Descriptor counts retain their different scopes. Main slides 5–7 now complete the KV case from symptom through source-based prioritisation and intervention to actual serving and the missing counterfactual.

The updated spoken scripts explain why the next question follows. AI backups 17–32 are marked hidden in PowerPoint; normal slide-show mode advances from 16 to the unchanged OpenFOAM slide 33. The full PDF deliberately retains backups, while the main-talk PDF avoids manual jumps. The physical HPC slide numbers and content are unchanged.

## Evidence boundaries

KV job 22271 timed out at 360 seconds before scoring; patched 22294 warmed real P/D paths in 0.68–0.70 seconds/request and measured 1422.96 good output tokens/s at N32, 95.87% joint SLA and zero errors. Source geometry and 720 CPU tests motivate/support the patch, but there is no successful unpatched scored control or isolated descriptor timer. A timeout is not a throughput baseline or an acceleration ratio.

N48 kernel-duration shares do not establish an N64 wall-time bottleneck. The matched N60 +5.295% goodput result includes worse TTFT and better ITL. N64 has a full comparison and independent repeat; N68's short signal does not survive its full useful-gain rule. Recovered portable data remain tied to originally failed jobs, official quality remains unverified, and candidate proxy savings do not automatically improve service. No new experiment or scientific result is introduced.

## Timing and human rehearsal

The compact AI script targets about 10:40, with a proposed rehearsal stop by 12 minutes to protect the HPC handoff. The official combined duration and Q&A inclusion were requested from the owner and remain unknown; these targets are not organiser limits or recorded speech times. A human mock, live slideshow test, microphones and screen sharing must still be tested by the team. The prepared Q&A has verified source links and follow-up boundaries; it is not a record of a performed mock or an official question list. HPC questions go to its independent owner.

## Validation and publication

[Investigation validation](../submission-review/ai-investigation-update-20261030/INVESTIGATION_VALIDATION.json) checks the slide messages/hardware and the visible sequence. The 24-page PDF exactly matches the selected pages of the full 40-page PDF. [Publication validation](../submission-review/ai-investigation-update-20261030/publication-validation.json) preserves all 68 HPC dependency parts, the eight HPC slide/PDF pages, 277 current HPC folder files/modes and 265 existing ZIP HPC files/member metadata independently. Preexisting folder/ZIP differences remain; no unpublished HPC work is silently packaged. Only the PPTX and necessary global manifests change inside the package; serving code and metrics remain unchanged.

Both transcript PDFs match their current Markdown source, retain all 40 briefs/images and clickable navigation, embed the Vietnamese font, and have no blank pages or out-of-page text. A preflight now rejects stale Markdown before replacing a PDF. Representative diagram, controlled-test and handoff pages were inspected visually. These are coordinate-based slide PDF renders, not a claimed Office playback test.

PPTX SHA-256: dcc56658f7efa1b43294d32316de4eb27c65d765d2a9f1806e18c67a40ca9d13. ZIP SHA-256: 23192cb9b708935f0c3d1d4af044b98e8cbe5d015f2941cfb4fff571f78fc895. Previous presentation and package are retained under /home/apacsc42/workspace/submission-archive/before-ai-investigation-20261030T174945Z. No organiser upload, new job, authentication or schedule occurred. Capture and push source/recovery metadata explicitly; Git does not upload sibling-store large object bytes.
