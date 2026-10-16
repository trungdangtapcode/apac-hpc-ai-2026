# Current Qwen research handoff —16Oct2026 05:42UTC

## Latest checked state —16Oct2026 05:42UTC

At05:40:37UTC all23934/23973/23974/23975/24009 are PENDING(Priority),5/5slots;
sacct has no start/allocation and watcher419440 is alive. No new GPU result.
Snapshots below are historical. No job/queued payload/watcher changes this wake.

NSCC existing-access ssh-batch now reaches the SSH server but returns
Permission denied(password), exit255. A read-only namespace check at05:40:56
confirms snx-tun UP and route via that tunnel. Earlier missing-VPN observations
are historical; current blocker is unavailable authenticated SSH access, not a
proven bad password. No inference about who started this tunnel, its age or
24h lifetime. No credentials/session contents read, no VPN connect/login/DUO,
no password supplied or repeated SSH/qsub.220575/result/credit stay unknown;
keep1536SU reserve,16384SU campaign cap,13000SU project reserve and04→05→06.

NEXT_STEP.md in nscc-pbs/inspection/wake-20261016-0540UTC gives the prepared
seal-review sequence and conditional NSCC recovery actions. CPU token suite and
reviewers are ready; do not repeat immutable audits/mocktests while pending.
continuous-plan metadata now reflects the prepared14case suite, not model output.
Independent work is complete; finish without waiting. Existing bounded repeats,
comboN54 gates and noN56/noextra successful repeat/no promotion remain current.

## Historical checked state and CPU preparation —16Oct2026 05:38UTC

At 05:36:58 UTC, 23934/23973/23974/23975/24009 are all PENDING(Resources),
5/5 slots; watcher 419440 alive at 05:30:29 UTC. No new GPU measurements.
Earlier scheduler checks below are historical. No new job, queued payload or
watcher modification this wake. NSCC helper lacked VPN before SSH at 05:30:29;
220575/result/credit remain unknown. No auth/DUO/qsub; keep the 1536 SU reserve.

EAGLE3 input suite now prepared at nscc-pbs/research-next/eagle3-01/token-suite-v1:
14 cases with the pinned tokenizer/chat template, retrieval inputs 3788/7885
tokens including template, input+cap <=8085. Capture preflight and byte-identical
rebuild pass. No real model capture/EOS/output/acceptance/accuracy or GPU test.
Preparation does not open a job or alter 04→05→06 priorities. See TOKEN_REVIEW.md.
Evidence: nscc-pbs/inspection/wake-20261016-0530UTC/. Independent preparation
complete; finish without waiting for queue. Existing bounded MNNVL repeat and
combo gates below remain current; no N56, extra successful repeat or promotion.

## New measured result and bounded continuation

23924 MNNVL N54 COMPLETED exit0 at04:31:37UTC. Sealed/raw/runtime review PASS:
2634.0344goodt/s,SLA98.9024%,TTFT600.4446ms,ITL17.1102ms,0requesterrors/cancel,
short7/8 only knownreverse. Gain+1.6004% versus two N52 controls mean; TTFT
+88.1784ms. One N54 observation, not a reproduced improvement or accuracy proof.
05:20:46UTC queue has23934/23973/23974/23975 PENDING(Resources),4/5slots,
watcher419440 alive. Prior five-pending snapshot below is historical.
Explicitly extend wave10 by ONE unchanged MNNVL N54 repeat in the freed slot,
s10-mnnvl-repeat-n54, submitted24009; see serving-tuning-10/PLAN.md. Use existing prepared-pilot
loader/watcher, sharedcap5; do not modify queued payloads or add a controller.
Review against23924 and all three MNNVL N52 controls. No third repeat, N56,
promotion or bypass of the comboN54 gates. This replaces the old wave7 bounded
stopping decision only for this one measured promising point. VPN restriction,
NSCC budget and04→05→06 remain unchanged;05:20 helper still lacks liveVPN.
Final05:24:11UTC:23934/23973/23974/23975/24009 PENDING(Resources),5/5slots;
watcher419440 alive, stored24009 launcher matches frozen. Use
serving-tuning-10/review-mnnvl-n54-repeat.py after seal to compare23924 and
all3N52controls. Existing watcher budget-deferred replacements remain capped
at3attempts for this single confirmation point; preserve failed attempts, and
review manually if replacements occur. No further successful N54 repeat planned.

Read workspace/notes/README.md andCURRENT.md first. Latest user asks about real
progress versus competitor v111; earlier directive remains: continue research,
use time/GPU, preserve all results, don't require manual reminders. Previous
policy is archived in POLICY-before-wave10-20261016.md, not current constraints.

## Current jobs and confirmed results (older observations explicitly dated)

Root /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments.
- H200Slurm queue cap5; live watcher PIDfile serving-tuning/watcher.pid,
  latestPID419440. Never duplicate watcher or change queued frozen bundles.
- Historical02:45 H200jobs23924(MNNVLN54),23934(DP+DeepEPN54),23973(comboN52repeat1),
  23974(freshMNNVLN52control),23975(comboN52repeat2+post-measurementlongchecks).
  At02:45:04UTC allPENDING(Resources),5/5slots; watcher419440 alive. These are scheduler observations, not GPU results. Wave10filled the three unused slots.
- Original combo single result23904MNNVL+FlashInfer:2631.0854goodt/s,SLA99.022%,
  ITL16.233ms,0errors/cancel. Only one observation. Wave10replicates a1.4867%
  gain against MNNVL23778/23839mean2592.543. Repeat control to assess drift.
- Losing wave9chunks2048/8192:2331.353/2547.854goodt/s; don't repeat losers.
- MNNVL independently reproduced:2592.16/2592.92,SLA99.01%.
  DP independently reproduced:2549.20/2538.08,SLA98.87%.
- Fullprotocol60/120/30,officialFP8 checkpoint,BF16KV,16H2008+8,RR.
 8case smoke7/8knownreverse,notorganiser99%accuracy. Longchecks separate.
- Plans:serving-tuning-10/PLAN.md andprepared-pilots.json. Watcher now includes
  wave10. CPUvalidation and mockedcap2/4/5 tests passed, realjobIDs above.

## Next actions

1. Check actual schedulers and logs; controllerACTIVE is not RUNNING.
2. 23924 already final-reviewed. Collect23934 using serving-tuning/review-n54.py; compare both source
   baselines andmean, output/protocol/runtime. Preserve failed points as data.
3. Read serving-tuning-10/MATCHED_REVIEW.md and use review-wave10.py after seals. Offline tool compares all three controls, means and fresh-control drift; long failure/deferred remains separate. CPU preparation validated; no wave10 GPU results yet. Review wave10replications andfreshcontrol, not just peak; first two preserve
   all execution files; third appends12~3800token retrieval tests after ranked
   benchmark. Keep failed/deferred diagnostics explicit and investigate.
4. Previous wave9 'no new repeat/job' statements described stopping that bounded
   wave, NOT cancellation of user's continuous request. Wave10is now explicitly
   planned andsubmitted. Do not reimpose old self-created prohibitions.
5. After validcombo replications, write the next bounded load/kernel plan based
   on measured gain/ITL. If SLA>=95%,ITL<=19.3ms,zeroerrors/cancel,no new output
   regression andlongdiagnostic passes, prioritize comboN54 then boundedload
   refinement. Preserve existingwave7/8gates. No blindN56 or automaticpromotion.
6. Do useful preparatory research while queued; sourceinspection/EAGLE3/vLLM
   work should make a concrete candidate reviewable. Avoid repeated audits of
   already sealed immutable files or mocktests that don't advance a hypothesis.

## NSCC and authentication restriction

NO NEW VPN AUTHENTICATION/DUOPUSH. User explicitly objected and authorized only
local recovery search. Old session not found; launcher hadike-persistfalse.
OldLinux tunnel ended20:17UTC,IKEexpiry, defaultclient8h; helpernowrequests24h,
at00:18 no successful new tunnel; loginfailed status0,reasonunknown.
At05:40 an existing tunnel was observed, but authenticated SSH remains unavailable;
its origin and24h lifetime are unverified. See current handoff above.
Windows user session reported stillworking; do not dispute or readitssecrets.
NSCC220575 lastconfirmedR20:12UTC15Oct; result/terminalstateunknown afterVPNloss.
Do not duplicate it or qsub without liveownqueue/credit/reconciliation.
Already prepared frozen H100pilots04/05/06; don't clone themagain.
Budget16384SUtotal,retain13000SU; max16GPUallocated at once; max3pending/runningPBSjobs only in verifiedafteranychain,45min1536SUreserve.
Keep220575reserve until actualaccounting; lastledger1343.147used beforejob.
See nscc-pbs/nscc-budget.json andcontinuous-plan.json.

## Reports and limits

Eachwake20min, no subagents/nestedCodex/new schedules, externalmessages/BTCupload,
others'privatefiles orGPUworkonlogin. CPUstaging<=4threads. No secrets innotes,
no authfile/chatcredential access orTLSbypass. No submission/slide changes.
Write concise Vietnamese LATEST.md, appendHISTORY andupdateCURRENT/knowledge.
Cron is localfreshCodexsessions, every5mincheck withchangegate, quota30minbackoff;
no push intooriginalchat. Codexquota is separatefromGPUSU.

## ACCESS OVERRIDE16Oct05:43UTC
## Bàn giao hiện hành16/10/2026 05:43UTC — VPN/SSH đã khôi phục

Người dùng chủ động cho phép thửDUO/login lúc05:40. TunnelIPsec/TCPT lên
05:40:20UTC,IP10.103.62.11/24; SSH đãđăngnhậpthànhcông,a2ap-login01.
**KiểmtralạiBatchMode05:42:43UTC thànhcông**, khôngphải chỉcóIP/TCP.
Các ghi chúmissingVPN/Permissiondenied ởwake05:40 là snapshottrướcxácthựchoàn tất.
Giữ nguyênVPNtool79786, khôngCtrl-C/restart. Không cóchallengeDUOtext, chưa
có phản hồiđiệnthoại; chỉxácnhậnVPN/SSHđạt,không đoánfactor. HelperđềxuấtIKE24h,
chưakiểmđủ24h. Phiênnày vẫnkhởiđộngvớiike-persistfalse,**chưa lưuSAtrêndisk**;
khôngđược tuyênbốđãcache hayrestartđểthayconfig.
PBS220575đãterminalF/exit0,wall30m25s;khôngownPBSjobactive. Ledger13:40Singapore:
used2381,369SU,balance61618,631SU,InDoubt0; khoảnjobđãđốisoát.
Collect-run.py lần05:41 bịtimeout60s khi tarstream, **chưareviewfullbenchmark**.
Giữpartial/log, tăng timeoutstream hợp lý trướcthu lại,khôngnhânđôicopyđangchạy.
Resume research04→05→06chỉsauđủgatefullartifact/queue/credit;khôngauthmới.
[Bằngchứng](/home/apacsc42/workspace/vpn-rootless/inspection/login-success-20261016-0540UTC.json).


## CURRENT EXECUTION OVERRIDE16Oct05:53UTC
## Bàn giao hiện hành16/10/2026 05:53UTC — chuỗi3jobNSCC đã gửi

User yêu cầu“submit nhiều vào,tận dụng thời gian”. Đã reviewbaseline220575:
fullartifact đãthu, frozenpayloadđạt,protocol60/120/30 ởN32/34/36đạt;
N32=1570,21,SLA100%;N34=1625,59,SLA100%;N36=1356,35,SLA82,12%thấtbại,
0errors/cancel ởcảba; short7/8chỉreverseđãbiết. Đãdừngtăngở36đúnggate.
PBSstdout chuyển về khôngcótrongarchive,khôngquy kết runtimebackendngoàibằngchứng;
khôngcoismokelàaccuracyBTC. Collectlần600s05:45đãđủ, bảncompressed05:50cũngđủ,
partial60strướcđượcgiữ. Đãsửacollector gzip đểgiảmtraffic quaVPN.

**220720.pbs111(MNNVL04) RUNNING16H100**;**220721.pbs111(FlashInfer05) HELD**
`afterany220720`;**220722.pbs111(loaderprefetch06) HELD**`afterany220721`.
DependencyđãđọclạitừPBS,đảm bảo1job16GPUchạymỗilúc. HELDdo dependency làđúng,
khôngqrls/hủy/jobduplicate. Mỗi allocation45phút, fullgridN32/34/36/38/40/42,
dừngtăngkhipointtrướcSLA/errorfail.04/05/06độclậpso baseline220575;
04failkhôngtựkếtluận05/06vôgiátrị. Nếulỗihạtầngchungcầnphân tíchdừngchuỗicóreason.

Budgetledger13:40Singaporeused2381,369,balance61618,631trướcjobmới;
reserve3×1536=4608SU,cap16384còn9394,631SUchưaphânbổ. Max3PBSjobpending/running,
max1running16GPU,giữ13000SUprojectreserve. Đây là amendment thayquytắc1queued
đểtận dụngthờigian,theo yêucầumớicủauser;khôngnângcapcampaign.
H20023934/23973/23974/23975/24009đủ5slot,đềuPENDING(Resources)05:52UTC.

VPNtool79786vàSSHđanghoạtđộng,giữphiênkhôngrestart/auth/DUOthêm.
Tiếp: thu vàphân tích04kếtthúc,khôngsubmitduplicate05/06đãqueued;so cácđiểm
cùngN/cùngH100baseline,kiểm12longretrieval nếuđủthờigian. Tựchuẩn bịbướcnext
basedondata khiđượcslot;khôngđua sốversion/tạo hàngloạtconfigvôcăn cứ.
[Bằngchứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/chain-20261016-0551UTC/chain.json).

