from pathlib import Path
import datetime,hashlib,json,re,fcntl
project=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
notes=Path('/home/apacsc42/workspace/notes');auto=Path('/home/apacsc42/workspace/research-autopilot')
p=project/'nscc-pbs/inspection/wake-20261016-0530UTC'
eagle=project/'nscc-pbs/research-next/eagle3-01'
now=datetime.datetime.now(datetime.timezone.utc);stamp=now.strftime('%d/%m/%Y %H:%M UTC')
evidence=str(p)
files=[notes/'CURRENT.md',auto/'POLICY.md',auto/'LATEST.md',auto/'HISTORY.md',eagle/'TOKEN_REVIEW.md',eagle/'design.json',eagle.parent/'README.md',Path('/home/apacsc42/workspace/tutorial/14-so-tay-hoi-dap.md')]
for path in files:
 (p/(path.name+'.before-handoff')).write_bytes(path.read_bytes())
current=notes/'CURRENT.md';s=current.read_text()
s=re.sub(r'Cập nhật kiến thức: \*\*.*?\*\*\.',f'Cập nhật kiến thức: **{stamp}**.',s,count=1)
s=s.replace('## Bàn giao hiện hành 16/10/2026 05:25 UTC','## Bàn giao lịch sử 16/10/2026 05:25 UTC',1)
block=f'''## Bàn giao hiện hành {stamp}

Scheduler kiểm **05:36:58 UTC**: **23934/23973/23974/23975/24009 đều
PENDING(Resources), đủ5/5slot**. Watcher419440 sống lúc05:30:29UTC; không có
phép đo GPU mới. Kết quả23924 và các gate wave10/N54 ở bàn giao05:25 giữ nguyên;
các câu chưa có seal23924/chưa xác minhN54 trong ghi chú cũ là lịch sử.
Không sửa queuedpayload, thêmjob/watcher/N56 hay tự chọn cấu hình.

Đã chuẩn bị [bộ đầu vào EAGLE3 14ca]({eagle}/token-suite-v1/suite.json)
bằng tokenizer đúng target revision đã pin:6file nhỏ khớp cache commit/ETag,
chattemplate đã hash, apply_chat_template và encode/render/roundtrip khớp.
Cap1/3/4/5/200 cùng prompt;thêmEOS-probe,Việt/Trung/code/multiturn vàretrieval
3788token đầu/giữa/cuối,7885token giữa. Token đếm gồmchattemplate;
maxinput+cap8085<=8192. Preflight bộthu đạt;dựng lại5file giống từngbyte.
Đây chỉ là **input CPU thật**, chưa có capture/outputmodel,EOSthật,compatibility,
acceptance hayaccuracy. Không tải draft/upload/chạyGPU. Transformers5.14.1
trảBatchEncoding mặc định;đã đặtreturn_dict=False,giữattempt01false-reject;
attempt02CPUchậm đã dừng vàgiữsource/log trước khi giảm kiểm/encode lặp.
Môi trường dùng thư viện trích từaiperf bằngCPU,không phải container runtime
đã kiểm GPU;các probe container thất bại đã giữ. [Hướng dẫn]({eagle}/TOKEN_REVIEW.md).

NSCC helper kiểm **05:30:29 UTC** thiếuVPN trướcSSH;220575/result/credit vẫn
chưa xác minh. Khôngauth/DUO/qsub;giữ1536SUreserve,campaign16384SU và04→05→06.
Tiếp:thu seal cácjob qua watcher rồi dùngreview-n54.py/review-wave10.py/
review-mnnvl-n54-repeat.py;đối soát control tự lặp trước candidate khi nhánh
EAGLE3 được phép chạy. Phần chuẩn bị độc lập lượt này xong;kết thúc không chờqueue.
Bằng chứng:`nscc-pbs/inspection/wake-20261016-0530UTC/`.

'''
pos=s.index('## Bàn giao lịch sử 16/10/2026 05:25 UTC');s=s[:pos]+block+s[pos:];current.write_text(s)
policy=auto/'POLICY.md';s=policy.read_text();s=s.replace('# Current Qwen research handoff —16Oct2026 05:25UTC',f'# Current Qwen research handoff —{now.strftime("16Oct2026 %H:%MUTC")}',1)
insert='''
## Latest checked state and CPU preparation —16Oct2026 05:37UTC

05:36:58UTC:23934/23973/23974/23975/24009 all PENDING(Resources),5/5slots;
watcher419440 alive at05:30:29UTC. No new GPU measurements; earlier checks below
are historical. No new job, queued payload or watcher modification this wake.
NSCC05:30:29UTC helper lackedVPN beforeSSH;220575/result/credit remain unknown.
No new auth/DUO/qsub; keep1536SUreserve and all existing gates/budgets.
EAGLE3 CPU input suite now prepared:research-next/eagle3-01/token-suite-v1,
14cases with exact pinned tokenizer/chat template,3788/7885token retrieval,
input+cap<=8085. Capture preflight and byte-identical rebuild pass; no real model
capture/EOS/output/acceptance/accuracy or GPU validation. Preparation does not
open a GPU job or alter04→05→06 priorities. Use TOKEN_REVIEW.md for next steps.
Evidence:nscc-pbs/inspection/wake-20261016-0530UTC/. Independent work complete;
finish without waiting for queue. Existing bounded MNNVL repeat/combo gates below
remain current; no N56, extra successful repeat or configuration promotion.
'''
s=s.replace('\n## New measured result and bounded continuation',insert+'\n## New measured result and bounded continuation',1);policy.write_text(s)
guide=eagle/'TOKEN_REVIEW.md';s=guide.read_text();s+='''

## Suite input thực bằng CPU —16/10/2026 05:37UTC

Đã có `token-suite-v1/suite.json` cho native capture; chưa có outputmodel hay
HTTP/model/GPUtest. `prepare-token-suite.py` chỉ dùng AutoTokenizer offline,
local_files_only và trust_remote_code=false; không đọc weights hoặc tải draft.
6file tokenizer/config nhỏ khớp revisione156cb4 đã pin vàETag trong local cache;
SHA256/template/messages/renderedprompts/IDs vàthứ tự case được giữ riêng.
Provenance này không chứng thực image/weights/deployment remote.

14case: một prompt với cap1/3/4/5/200;EOS-probe;Việt/Trung/code/multiturn;
retrieval3vị trí với3788inputtokens và1ca7885token. Khác diagnostic23975,
countnày **đã gồmchattemplate**;maxinput+cap8085 trong8192. `prompts.json`
lưu thông tin semantic để điều tra,không tự chấm nhưaccuracy. EOS-probe chỉ
là prompt khuyến khích dừng;phải quan sát EOS/finishthật,không giả lập/ép PASS.

Kiểm CPU: tất cả case qua preflight của capture-native-tokens.py;hashseal đạt,
5cap cùngIDs;encode sau render khớp trực tiếpapply_chat_template vàroundtrip.
Dựng lại5file giống từngbyte. Transformers5.14.1/tokenizers0.22.2/Jinja3.1.6
trích từaiperf.sqsh bằng2CPU;dùngPython+loader giải nén,không phảicontainer
runtime đã được xác minh. Không cóPyTorch/model trong phép thử này. Probe
container thất bại vàattemptCPU trước được giữ tronginspection0530;không phải
thất bại củaQwen. Attempt01so nhầmBatchEncoding vớilist đã sửa bằng
return_dict=False;attempt02chậm đã dừng,trước khi cachevocabsize vàbỏ encode
lặp trong tìm độdài. Không đổi queuedpayload.

Tái tạo bằng môi trường cùngphiênbản từmodelcache đúngrevision:

```bash
python3 prepare-token-suite.py \\
  --model-dir /scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8 \\
  --outdir /new/path/token-suite
```

Khi deployment/forward đã được phép vàaudit riêng, dùng cùngfile suiteđãseal
cho control,control-repeat,candidate với bộthu đã hướng dẫn phía trên;truyền
`--suite token-suite-v1/suite.json` vàtokenizer.json thực đã xác minh. Thu lại
control nếu không tựlặp;giữ mọi sai khác/EOS/tail,không tái tokenize textoutput.
Gateweights/draft,memory,simulation=-1,CUDA,acceptance,quality vàaccuracy vẫn
chưa đạt;04→05→06,VNPauthrestriction,budget vàqueuegates giữ nguyên.
Bằngchứng:`nscc-pbs/inspection/wake-20261016-0530UTC/suite-validation.json`
và`suite-reproducibility.json`. Không tạoGPUjob từ PASSpreflight.
''';s=s.replace('VNPauthrestriction','VPNauthrestriction');guide.write_text(s)
design=eagle/'design.json';v=json.loads(design.read_text());v['updated_utc']=now.isoformat();v['native_capture_preparation']['limits']='No real model/SGLang HTTP capture; local input suite prepared at token-suite-v1. Runtime and provenance audit remain separate.'
v['token_suite_preparation']={'state':'OFFLINE_INPUTS_ONLY_14_CASES_PREFLIGHT_PASS_BYTE_IDENTICAL_REBUILD','script':'prepare-token-suite.py','suite':'token-suite-v1/suite.json','case_count':14,'retrieval_input_tokens_including_chat_template':[3788,3788,3788,7885],'max_input_plus_output_cap':8085,'evidence':'nscc-pbs/inspection/wake-20261016-0530UTC/suite-validation.json','model_executed':False,'gpu_executed':False,'real_eos_observed':False,'uploaded':False};design.write_text(json.dumps(v,indent=2)+'\n')
readme=eagle.parent/'README.md';readme.write_text(readme.read_text()+'''\n## CPU input suite16Oct05:37UTC\n\nEAGLE3 now has14sealed native-token input cases in eagle3-01/token-suite-v1,\nprepared offline with exact pinned tokenizer/chat template. Retrieval inputs\nare3788/7885tokens including chattemplate;maxinput+cap8085/8192. Consumer\npreflight andbyte-identical rebuild pass;no realHTTP/modeloutput/EOS/GPUtest,\ndraft download orsubmission. Seeeagle3-01/TOKEN_REVIEW.md;runtime/quality gates\nand04→05→06 priorities remain unchanged.\n''')
qa=Path('/home/apacsc42/workspace/tutorial/14-so-tay-hoi-dap.md');qa.write_text(qa.read_text()+f'''\n\n**{stamp} — Có input IDs chuẩn bị sẵn đã chứng minh EAGLE3 đúng chưa?**\n\nChưa. Bộ14ca mới chỉ cố định cùngđầu vào bằngtokenizer/chattemplate của\nrevisiontarget đã pin. Ba retrieval có3788token,ca dài7885token **gồmtemplate**,\nkhác cáchđếm prompttrần của diagnostic23975. Cap1/3/4/5/200giúp đọc ranhgiới\ndraft4;EOS-probe vẫn phải cóEOS/finishthật khi chạy. Preflight/hash vàdựng lại\ngiốngbyte chỉ xácminh bộđầu vào,không phải14outputmodel đúng.\n\nTrongTransformers5.14.1 ởimageaiperf đã trích,apply_chat_template(tokenize=True)\nmặc định trảBatchEncoding;đặtreturn_dict=False mới lấylistIDs trực tiếp.\nPrototype so cảobject vớilist đãfalse-reject;không có bằngchứngtokenizer sai.\nCần thu control,control-repeat,candidate cùngsuite theođúngthứtự,đọcIDs/EOS/tail\nnguyênbản vàaudit deployment/simulation=-1 riêng. Chưa cócapturethật,acceptance\nhayaccuracyBTC;khôngtạoGPUjob từpreflightđạt.\n[Hướngdẫn]({guide}) · [Suite]({eagle}/token-suite-v1/suite.json).\n''')
# Only refresh access metadata; retain the dated ledger and conservative SU reservation.
budget=project/'nscc-pbs/nscc-budget.json'
with (budget.parent/'budget.lock').open('a+') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);(p/'nscc-budget.json.before-handoff').write_bytes(budget.read_bytes());v=json.loads(budget.read_text())
 check=json.loads((p/'nscc-readonly.json').read_text())['checked_utc'];source='nscc-pbs/inspection/wake-20261016-0530UTC/nscc-readonly.json'
 note=f'No PBS/credit refresh at{check}: helper found no live VPN before SSH.220575 current state/result unknown; retain1536SU reserve. Historical ledger unchanged. No authentication/DUO/qsub.'
 v['updated_utc']=now.isoformat();v['reconciliation_note']=note
 v['latest_access_check']={'checked_utc':check,'state':'VPN_SESSION_MISSING_BEFORE_SSH','pbs_and_credit_refreshed':False,'new_authentication_attempted':False,'qsub_attempted':False,'source':source,'last_confirmed_job_state':'220575.pbs111 R at2026-10-15T20:12:38Z'}
 for job in v['jobs']:
  if job['job_id']=='220575.pbs111':job.update(scheduler_comment=note,latest_attempted_check_utc=check,state_fresh=False)
 if source not in v['evidence']:v['evidence'].append(source)
 temp=budget.with_name('nscc-budget.json.wake0530.tmp');temp.write_text(json.dumps(v,indent=2)+'\n');temp.replace(budget)
report=f'''# Báo cáo Qwen —{stamp}

- **05:36:58UTC:**23934/23973/23974/23975/24009 đều **PENDING(Resources),5/5slot**;watcher419440 sống lúc05:30:29. Chưa có số đoGPU mới;23924 vẫn là1lượtN54,2634,03goodtokens/s,gain1,6004% chưa lặp.
- Đã chuẩn bị **suite14ca EAGLE3** bằngtokenizer/template đúngrevisionpin;6file khớpcache/ETag. Cap1/3/4/5/200,short/multilingual/multiturn vàretrieval3788/7885token gồmtemplate;maxinput+cap8085/8192.
- Preflight bộthu,hashseal vàdựng lại5file giốngbyte đạt. ChỉinputCPU;chưa cóHTTP/modeloutput/EOSthật,compatibility,acceptance hayaccuracy. Giữ cácattempt/probeCPU lỗi;đãsửareturn_dict=False choTransformers5.14.1.
- **NSCC05:30:29UTC:**thiếuVPN trướcSSH;220575/result/credit chưa xácminh. Khôngauth/DUO/qsub;giữ1536SUreserve,campaign16384SU và04→05→06. Khôngthêmjob/watcher/N56hay sửaqueuedpayload.
- Đã cậpnhậtCURRENT,POLICY,Q&A,design vàbudgetaccessmetadata. Tiếp:thu seal qua watcher,review23934/wave10/24009 theo3reviewer hiện có. Phần độc lập xong;kếtthúc khôngchờqueue.

[Suite]({eagle}/token-suite-v1/suite.json) · [Hướngdẫn]({guide}) · [KiểmCPU]({p}/suite-validation.json) · [Scheduler]({p}/final-queue.json).
'''
(auto/'LATEST.md').write_text(report)
with (auto/'HISTORY.md').open('a') as f:f.write('\n\n'+report.replace('# Báo cáo Qwen','## Lượt Qwen',1))
summary={'utc':now.isoformat(),'queue_checked_utc':'2026-10-16T05:36:58.203878+00:00','jobs_pending':[23934,23973,23974,23975,24009],'watcher_pid':419440,'gpu_measurements_new':False,'suite_case_count':14,'suite_preflight_pass':True,'rebuild_byte_identical':True,'model_executed':False,'new_authentication_attempted':False,'qsub_attempted':False,'slurm_job_added':False,'reserve_su_unchanged':1536,'campaign_cap_su_unchanged':16384,'cpu_attempts':[{'attempt':1,'outcome':'FALSE_REJECT_BATCHENCODING_VS_LIST','source':'prepare-token-suite.attempt01.py','log':'prepare-token-suite.txt'},{'attempt':2,'outcome':'STOPPED_SLOW_CPU_LOOP_NO_SUITE_WRITTEN','source':'prepare-token-suite.attempt02.py','log':'prepare-token-suite.attempt02-stopped.txt'},{'attempt':3,'outcome':'PASS_AFTER_CACHING_VOCAB_AND_REDUCING_REPEATED_ENCODING','source':str(eagle/'prepare-token-suite.py'),'log':'prepare-token-suite-final.txt'}],'reason_stopped':'Independent CPU preparation complete; all5authorizedGPUslots pending; noVPNauthallowed.'}
(p/'wake-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
for path in files:
 (p/(path.name+'.after-handoff')).write_bytes(path.read_bytes())
print(stamp)
