# A shell exit can fail after successful native transport

23 October 2026. Job 224155 is F/exit 1, 262 s, uniquely posted 18.631 SU. The independent byte gate passes, but the exit gate correctly rejects both final node statuses. New receipts show actual Python 0, container 0 and temporary cleanup 0, followed by shell 1. This narrows the fault boundary; it does not justify calling the job successful.

Controlled CPU tests on the same login service isolate login-shell behavior. A minimal exit 0 script fails only when login mode, errexit and the console-only logout are combined. All seven other combinations pass. The account's noncomment logout commands match that public case. The first negative no-errexit fixture is preserved as part of the reasoning. No profile/logout file or authentication state was changed.

Decision: use a separately frozen nonlogin batch/node launcher and initialize modules explicitly, retain strict errors and all data/exit gates, then one bounded GPU confirmation. This is a concrete repair hypothesis, not an unchanged retry. The old full 223055 NIXL remote disconnect remains unresolved; model outputs, speedup and official accuracy are unverified. A separate source-only auxiliary row-layout review addresses a remaining transport evidence gap.

H100 credit Used 46484.545 / Balance 17515.455 / In Doubt 0 / outstanding maxima 0 / headroom 4515.455 SU under unchanged 51000 cap and 13000 reserve. H200 25682/25712/25713 remain pending in the latest scheduler query, unchanged.

For a presentation: “The computation and container both finished normally. The surrounding login shell then ran a console-cleanup command and turned success into an error under strict shell settings. We proved that with eight small CPU cases before spending another GPU run.”

[Raw boundaries, negative controls, full byte evidence and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-224155-20261023/REVIEW.md).
