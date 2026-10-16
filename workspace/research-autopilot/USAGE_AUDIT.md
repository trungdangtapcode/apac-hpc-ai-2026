# Codex usage audit —16Oct2026

CLI on thisVPS reports Logged in usingChatGPT. Cron invokes codexexec using that
login. GPU SU and localPython/schedulerpolls are separate from Codexmodelusage.
Otherdevices and thisinteractivechat may also consume accountallowance.

Last24h completed-log audit:133starts,35completed,95quotaerrors;
43,491,143inputtokens INCLUDING40,644,352cached;442,203outputtokens.
Some interrupted/failedturns lack counters. This is not exactbilling or a direct
remaining-quota percentage. Cachedtokens are included in input,not extra.

Confirmed inefficiencies:Priority/Resources reason flips couldwakeLLM; overly
broadregistryfingerprint; growingCURRENT54,238bytes+POLICY14,554bytes; cronPATH
lackedrg so quotaerrorbackoff failed. Rejectedrequests are not proof of the
same usage cost as completedrequests, but retry behavior was broken.

Fixed: semanticjob/state/completion triggers; Pythonquota detection with30min
backoff; compactCURRENT/POLICY3913+3899bytes initially, originals archived in
context-archive-20261016-1328UTC. Targetedreads and no repeatimmutableaudit.
Model unchanged. GPUwatcher,VPN andqueuedjobs untouched. Localchecks remain5min,
modelinvokedonly for meaningfulchange,FORCE or6h researchfallback.
Semantic andlive no-change tests passed withoutmodel/GPU. See
usage-fix-validation.json andusage-audit-20261016.json.

Official docs: https://learn.chatgpt.com/docs/pricing and
https://learn.chatgpt.com/docs/non-interactive-mode .
