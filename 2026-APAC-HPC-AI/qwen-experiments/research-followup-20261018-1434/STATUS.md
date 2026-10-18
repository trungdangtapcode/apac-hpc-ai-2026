# Live status — 18 October 2026, 14:34 UTC

H200 job 24573 (DeepGEMM prefill chunk 6144 N56 independent repeat) is running; 24574/24575/24588/24589 are pending. Worker readiness is progressing: both prefills and decode became ready around 290–296 seconds, all workers ready at 324 seconds. No new terminal measurement yet. Preserve the five active-job positions; no sixth submission.

The H100 SSH wrapper fails before invoking SSH because it finds no matching live rootless VPN process. The retained client log records **IKE SA expired at 14:08:45.570608 UTC**. The tmux session still exists, which alone does not establish a live VPN tunnel. This is a VPN client availability problem, not evidence of an SSH password failure or a failed PBS allocation. Current H100 scheduler/job results remain unknown this turn.

The last documented VPN reconnection was 17 October 14:08–14:09 UTC, about 24 hours before this event. That timing is consistent with the configured client lifetime 86,400 seconds, but the single log message does not prove whether server authentication or cached IKE state can still be reused. Do not claim a server-imposed limit or delete the authentication cache. No reauthentication, password prompt or DUO request was triggered in this status check. Authentication/session material was not printed or written to notes. Retained cache files were not opened or modified.

PBS jobs execute on the cluster independently of the VPN client. A local tunnel loss does not itself cancel them, but their actual terminal state still requires a successful remote check. Do not present the old queue or credit snapshot as live. No PBS collection, new qsub or budget reconciliation was possible; existing reservations remain conservative until remote accounting is checked.

Latest validated observed peaks remain H200 2786.696 and H100 2371.961 good tokens/s. The H100 both-phase N50 repeat 2371.341 had passed all local gates before access was lost. See previous reviews for exact evidence and accuracy limitations. No new AI schedule, background watcher or official-package changes.
