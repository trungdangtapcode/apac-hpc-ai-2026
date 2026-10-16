from pathlib import Path
notes=Path('/home/apacsc42/workspace/notes');auto=Path('/home/apacsc42/workspace/research-autopilot')
base=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs');eagle=base/'research-next/eagle3-01';p=base/'inspection/wake-20261016-0530UTC'
current=notes/'CURRENT.md';s=current.read_text();a=s.index('## Bàn giao hiện hành');b=s.index('## Bàn giao lịch sử 16/10/2026 05:25 UTC')
s=s[:a]+f'''## Bàn giao hiện hành 16/10/2026 05:38 UTC

Scheduler kiểm **05:36:58 UTC**: **23934/23973/23974/23975/24009 đều
PENDING(Resources), đủ 5/5 slot**. Watcher 419440 sống lúc 05:30:29 UTC.
Chưa có số đo GPU mới. Kết quả 23924 và các gate wave10/N54 ở bàn giao 05:25
vẫn áp dụng; các câu chưa có seal 23924/chưa xác minh N54 bên dưới là lịch sử.
Không thêm job, sửa payload đang queue hoặc khởi watcher mới.

Đã chuẩn bị [bộ đầu vào EAGLE3 14 ca]({eagle}/token-suite-v1/suite.json)
bằng tokenizer của đúng target revision đã pin; 6 file nhỏ khớp cache commit/ETag.
Lưu hash chat template, messages, rendered prompts và IDs. Có cap 1/3/4/5/200
trên cùng prompt, EOS probe, Việt/Trung/code/multiturn, retrieval 3 vị trí với
3.788 token và một ca 7.885 token, đều gồm chat template; input+cap tối đa
8.085/8.192. Preflight bộ thu và seal đạt; dựng lại 5 file giống từng byte.
Đây chỉ là đầu vào CPU, chưa có capture/output model, EOS thật, compatibility,
acceptance hay accuracy. Không tải draft, upload hoặc chạy GPU.

Transformers 5.14.1 trả BatchEncoding mặc định; đã đặt `return_dict=False`, giữ
prototype false-reject. Một attempt CPU chậm đã dừng, giữ source/log rồi giảm
kiểm vocab/encode lặp. Dùng thư viện trích từ aiperf với CPU, chưa xác minh
container runtime GPU; các probe container thất bại cũng được giữ.
[Hướng dẫn]({eagle}/TOKEN_REVIEW.md).

NSCC helper kiểm **05:30:29 UTC** thiếu VPN trước SSH; 220575/result/credit
vẫn chưa xác minh. Không auth/DUO/qsub; giữ dự trù **1.536 SU**, campaign
16.384 SU và thứ tự 04→05→06. Tiếp: thu seal qua watcher rồi dùng
review-n54.py, review-wave10.py và review-mnnvl-n54-repeat.py. Khi nhánh EAGLE3
được phép chạy, so control tự lặp trước candidate. Phần chuẩn bị độc lập đã xong;
kết thúc không chờ queue. Bằng chứng: `nscc-pbs/inspection/wake-20261016-0530UTC/`.

'''+s[b:];current.write_text(s)
policy=auto/'POLICY.md';s=policy.read_text();a=s.index('## Latest checked state');b=s.index('## New measured result')
s=s[:a]+'''## Latest checked state and CPU preparation —16Oct2026 05:38UTC

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

'''+s[b:];policy.write_text(s)
guide=eagle/'TOKEN_REVIEW.md';s=guide.read_text().replace('cập nhật05:30 bên dưới','cập nhật 05:38 bên dưới');a=s.index('## Suite input thực bằng CPU');s=s[:a]+'''## Bộ đầu vào thực bằng CPU —16/10/2026 05:38 UTC

Đã có `token-suite-v1/suite.json` cho native capture; chưa có output model hoặc
HTTP/model/GPU test. `prepare-token-suite.py` dùng AutoTokenizer offline với
`local_files_only=True`, `trust_remote_code=False`; không đọc weights/tải draft.
Sáu file tokenizer/config nhỏ khớp revision e156cb4 đã pin và ETag trong cache.
Provenance lưu hash tài sản, chat template, messages, rendered prompts, IDs và
thứ tự case; chưa chứng thực image/weights/deployment remote.

14 ca gồm một prompt với cap 1/3/4/5/200; EOS probe; Việt/Trung/code/multiturn;
retrieval ở 3 vị trí với 3.788 input tokens và một ca 7.885 token. Khác diagnostic
23975, count này **đã gồm chat template**; input+cap lớn nhất 8.085/8.192.
`prompts.json` lưu thông tin semantic để điều tra, chưa chấm accuracy. EOS probe
chỉ khuyến khích dừng; phải quan sát EOS/finish thật, không giả lập hoặc ép PASS.

Tất cả ca qua preflight của capture-native-tokens.py; seal đạt, 5 cap cùng IDs.
Encode sau render khớp trực tiếp apply_chat_template và roundtrip. Dựng lại 5
file giống từng byte. Dùng Transformers 5.14.1/tokenizers 0.22.2/Jinja 3.1.6 trích
từ aiperf.sqsh bằng 2 CPU, chạy Python và loader giải nén. Đây chưa phải kiểm
container runtime; không có PyTorch/model trong phép thử. Probe container lỗi
và các attempt CPU được giữ ở inspection0530, không phải lỗi của Qwen.
Attempt01 so nhầm BatchEncoding với list đã sửa bằng `return_dict=False`.
Attempt02 chậm đã dừng; bản cuối cache vocab size và bỏ encode lặp khi tìm
độ dài. Payload đang queue giữ nguyên.

Tái tạo từ model cache đúng revision bằng môi trường cùng phiên bản:

```bash
python3 prepare-token-suite.py \\
  --model-dir /scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8 \\
  --outdir /new/path/token-suite
```

Khi deployment/forward đã được phép và audit riêng, dùng cùng file suite đã seal
cho control, control-repeat và candidate; truyền `--suite token-suite-v1/suite.json`
cùng tokenizer.json thực đã xác minh cho bộ thu. So control tự lặp trước; nếu
khác thì điều tra, giữ mọi capture. Không tái tokenize text output hoặc bỏ EOS/tail.
Gate weights/draft, memory, simulation=-1, CUDA, acceptance, quality và accuracy
vẫn chưa đạt. Thứ tự 04→05→06, hạn chế VPN auth, budget và queue gates giữ nguyên.
Bằng chứng: `nscc-pbs/inspection/wake-20261016-0530UTC/suite-validation.json`
và `suite-reproducibility.json`. Preflight PASS không tự mở job GPU.
''';guide.write_text(s)
readme=eagle.parent/'README.md';s=readme.read_text().replace('Designs only:','Designs and offline CPU preparation only:');a=s.index('## CPU input suite16Oct');s=s[:a]+'''## CPU input suite —16Oct2026 05:38UTC

EAGLE3 now has 14 sealed native-token input cases in eagle3-01/token-suite-v1,
prepared offline with the pinned tokenizer/chat template. Retrieval inputs are
3788/7885 tokens including template; max input+cap 8085/8192. Consumer preflight
and byte-identical rebuild pass; no real HTTP/model output/EOS/GPU test, draft
download or submission. See eagle3-01/TOKEN_REVIEW.md; runtime/quality gates and
04→05→06 priorities remain unchanged.
''';readme.write_text(s)
qa=Path('/home/apacsc42/workspace/tutorial/14-so-tay-hoi-dap.md');s=qa.read_text();a=s.index('**16/10/2026 05:38 UTC — Có input');s=s[:a]+f'''**16/10/2026 05:38 UTC — Có input IDs chuẩn bị sẵn đã chứng minh EAGLE3 đúng chưa?**

Chưa. Bộ 14 ca mới chỉ cố định cùng đầu vào bằng tokenizer/chat template của
đúng target revision. Ba retrieval có 3.788 token, ca dài 7.885 token **gồm
chat template**, khác cách đếm prompt trần ở diagnostic 23975. Cap 1/3/4/5/200
để quan sát biên draft4; EOS probe vẫn phải có EOS/finish thật khi chạy.
Preflight, hash và dựng lại giống byte chỉ kiểm bộ đầu vào, chưa có output model.

Trong Transformers 5.14.1 trích từ image aiperf, apply_chat_template(tokenize=True)
mặc định trả BatchEncoding; đặt `return_dict=False` để lấy list IDs trực tiếp.
Prototype so cả object với list đã false-reject; chưa có bằng chứng tokenizer sai.
Cần thu control, control-repeat và candidate cùng suite/cùng thứ tự; so control
tự lặp trước, giữ IDs/EOS/tail nguyên bản và audit deployment/simulation=-1 riêng.
Chưa có capture thật, acceptance hay accuracy BTC; preflight đạt không tự mở job.
[Hướng dẫn]({guide}) · [Suite]({eagle}/token-suite-v1/suite.json).
''';qa.write_text(s)
report=f'''# Báo cáo Qwen —16/10/2026 05:38 UTC

- **05:36:58 UTC:** 23934/23973/23974/23975/24009 đều **PENDING(Resources), 5/5 slot**. Watcher 419440 sống lúc 05:30:29. Chưa có số đo GPU mới; gain N54 1,6004% của 23924 vẫn chưa lặp xác nhận.
- Đã chuẩn bị **bộ đầu vào EAGLE3 14 ca** bằng tokenizer/template đúng revision. Retrieval có 3.788/7.885 token gồm template; input+cap tối đa 8.085/8.192.
- Preflight bộ thu, seal và dựng lại 5 file giống byte đều đạt. Chỉ chuẩn bị CPU; chưa có HTTP/output model/EOS thật, compatibility, acceptance hay accuracy. Giữ các attempt/probe lỗi và bản sửa API Transformers.
- **NSCC 05:30:29 UTC:** thiếu VPN trước SSH; 220575/result/credit chưa xác minh. Không auth/DUO/qsub; giữ dự trù **1.536 SU**, campaign 16.384 SU và 04→05→06. Không thêm job hoặc sửa payload đang queue.
- Đã cập nhật CURRENT, POLICY, Q&A, design và metadata kiểm truy cập trong budget. Tiếp: thu seal qua watcher, review 23934/wave10/24009 bằng các công cụ hiện có. Phần độc lập đã xong; kết thúc không chờ queue.

[Suite]({eagle}/token-suite-v1/suite.json) · [Hướng dẫn]({guide}) · [Kiểm CPU]({p}/suite-validation.json) · [Scheduler]({p}/final-queue.json).
'''
(auto/'LATEST.md').write_text(report)
history=auto/'HISTORY.md';s=history.read_text();a=s.rindex('## Lượt Qwen —16/10/2026 05:38 UTC');s=s[:a]+report.replace('# Báo cáo Qwen','## Lượt Qwen',1);history.write_text(s)
