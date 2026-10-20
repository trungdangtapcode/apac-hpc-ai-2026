## Current VPN duration explanation — 20 October 2026

[VPN lifetime and how to change it](19-vpn-session-lifetime.md) distinguishes the 24-hour IKE proposal, measured client uptime, detached terminal, private recovery state and SSH persistence. At 01:04 UTC the process had about 21 hours uptime and SSH worked. No exact negotiated expiry or infinite renewal is claimed. Historical answers below keep their original dates and may describe earlier configurations.

# Sổ tay hỏi–đáp từ cuộc trò chuyện

Cập nhật: **15/10/2026**. Ghi lại kiến thức đã giải thích để tra cứu; các con số về job, queue, quota là **ảnh chụp tại thời điểm ghi**, không phải trạng thái trực tiếp.

Không lưu mật khẩu, OTP hoặc mã khôi phục vào sổ này. Những thông tin chưa kiểm chứng được ghi rõ.

## Mục lục

- [Hai hệ thống đang dùng](#hai-hệ-thống-đang-dùng)
- [Login node, GPU và cách chạy job](#login-node-gpu-và-cách-chạy-job)
- [Storage, checkpoint và container](#storage-checkpoint-và-container)
- [Slurm và PBS](#slurm-và-pbs)
- [Bài thi Qwen và benchmark](#bài-thi-qwen-và-benchmark)
- [Cấu hình tối ưu nghĩa là gì?](#cấu-hình-tối-ưu-nghĩa-là-gì)
- [Queue, lỗi và lịch sử thí nghiệm](#queue-lỗi-và-lịch-sử-thí-nghiệm)
- [VPN và NSCC](#vpn-và-nscc)
- [Các mốc kết quả đã xác nhận](#các-mốc-kết-quả-đã-xác-nhận)

## Hai hệ thống đang dùng

**Hỏi: Firmus là gì?**

Trong các cập nhật của trợ lý, “Firmus” dùng để gọi cụm H200 ban đầu, phân biệt với NSCC. Đây không phải tên scheduler hay một lệnh cần cài. Cách nhận diện thực tế là máy đăng nhập, GPU và scheduler dưới đây; không cần dựa vào tên gọi của trợ lý để chạy lệnh.

| | Cụm H200 ban đầu, được gọi là Firmus | NSCC ASPIRE 2A+ |
|---|---|---|
| Điểm đăng nhập | `apacsc42@login`, hostname đã ghi nhận `login.hpcai2025.smc` | `aspire2p.nscc.sg`, vào qua VPN |
| Scheduler đang dùng | Slurm | PBS |
| Gửi / xem job | `sbatch` / `squeue` | `qsub` / `qstat` |
| GPU đã kiểm tra | H200, 8 GPU/node, hai node `g1`, `g4` | H100 80 GB, 8 GPU/node |
| Queue/partition dùng | `hpcai` | Gửi vào `normal`, hệ thống route sang execution queue |

**Hỏi: Có dùng PBS trên server hiện tại không?**

Cụm H200 đang chạy các thí nghiệm bằng Slurm. NSCC dùng PBS. Không suy ra một chương trình đã cài chỉ từ việc scheduler khác có cùng chức năng; dùng đúng bộ lệnh của từng cụm.

## Login node, GPU và cách chạy job

**Hỏi: Tại sao không `nvidia-smi` rồi chạy Python luôn?**

Shell ban đầu ở login node: nơi sửa code, gửi job, đọc kết quả. GPU ở compute node. `nvidia-smi` chỉ xem GPU mà môi trường hiện tại nhìn thấy, không xin GPU hay chuyển Python sang máy khác. Scheduler cấp tài nguyên rồi chạy chương trình trên compute node; ở đó vẫn dùng Python và `nvidia-smi` bình thường.

**Hỏi: Tại sao job hello chỉ thấy một H200, tưởng có tám?**

Job hello xin một GPU nên môi trường job chỉ thấy GPU được cấp. Số GPU nhìn thấy trong job không phải tổng số GPU trên node hay toàn cluster. Muốn dùng nhiều GPU phải xin đúng tài nguyên và chương trình phải có cơ chế chạy nhiều GPU.

**Hỏi: Job chỉ có GPU thôi à?**

Không. Job còn dùng CPU, RAM, ổ đĩa và mạng. GPU tăng tốc phần tính toán của model; CPU vẫn chạy Python, tokenizer, điều phối và benchmark client.

**Hỏi: `bash file.sbatch` khác gì `sbatch file.sbatch`?**

`sbatch` đọc `#SBATCH`, gửi yêu cầu và tạo môi trường Slurm khi job chạy. `bash` coi các dòng đó là comment. Vì vậy chạy trực tiếp từng gây lỗi `SLURM_SUBMIT_DIR: unbound variable`: biến này chưa được Slurm cung cấp.

**Hỏi: Giống GitHub commit là CI/CD tự chạy không?**

`sbatch` giống gửi một lần chạy vào hàng đợi. Commit Git chỉ lưu phiên bản code; không tự gửi job nếu chưa thiết lập automation. Job batch thường tiếp tục chạy sau khi đóng terminal.

**Hỏi: Job chạy rồi có SSH vào được không?**

Cách được hỗ trợ trên Slurm là mở một job step trong allocation, ví dụ `srun --jobid=JOB_ID --pty bash`, tùy chính sách và tài nguyên còn lại. SSH trực tiếp vào compute node phụ thuộc chính sách cụm; biết hostname không đồng nghĩa có quyền vào. Job đã kết thúc thì allocation đã được trả lại.

Đọc thêm: [máy và Slurm](01-may-va-slurm.md), [thực hành](02-thuc-hanh.md), [lỗi thường gặp](03-lenh-va-loi.md).

## Storage, checkpoint và container

**Hỏi: Có phải mount ổ của VPS hiện tại qua compute node không?**

Gần với hình dung đó, nhưng storage dùng chung thường là hệ thống lưu trữ riêng mà login node và compute node cùng mount. Không nhất thiết compute node đọc ổ đĩa vật lý của login node. Cùng đường dẫn chia sẻ thì cùng thấy file; Python vẫn chạy trên máy chứa tiến trình.

**Hỏi: Code, weights, kết quả để đâu?**

- Code và bài hướng dẫn: `~/workspace`, `~/2026-APAC-HPC-AI`.
- Checkpoint trên cụm H200: `/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8`.
- Container trên cụm H200: `/scratch/enroot-images/`.
- Kết quả thí nghiệm Qwen: `~/2026-APAC-HPC-AI/qwen-experiments/runs/`.
- NSCC có storage riêng; file trên cụm H200 không tự xuất hiện ở NSCC.

Container chứa môi trường phần mềm; checkpoint là file weights riêng. Mount làm những file bên ngoài xuất hiện trong container. Không phải tải lại model cho mỗi job nếu checkpoint đã nằm trên storage dùng chung.

Đọc thêm: [CI/CD, storage và vào job](04-cicd-storage-va-job.md).

**Hỏi: Máy hiện tại có cài và chạy Docker rootless được không? (17/10/2026)**

Kiểm tra trực tiếp lúc 02:20 UTC trên shell `apacsc42@login.hpcai2025.smc`:
user namespace hoạt động (`unshare --user --map-root-user id` thành công),
nhưng `/etc/subuid` và `/etc/subgid` không có dải nào cho `apacsc42`/UID3042.
Docker rootless chuẩn cần ít nhất 65.536 subordinate UID và GID cho user.
Vì vậy hiện chưa đủ điều kiện để tự cài rồi chạy Docker rootless; quản trị viên
cần cấp hai dải không trùng người khác trước. Rootless nghĩa là daemon/container
chạy không có root trên host, không có nghĩa mọi prerequisite hệ thống đều tự
cấu hình được bằng user thường.

`newuidmap`/`newgidmap` đã có file capabilities `cap_setuid=ep`/`cap_setgid=ep`;
không được kết luận helper thiếu quyền chỉ vì không có bit setuid.
`sudo -n -l` yêu cầu mật khẩu: chưa có bằng chứng dùng được sudo không tương tác,
không phải bằng chứng tài khoản tuyệt đối không có sudo. Docker/dockerd/RootlessKit
chưa có trên PATH; `slirp4netns` có riêng trong `workspace/vpn-rootless/bin`.
Kernel thực là 4.18 dù userspace báo Rocky9.8; `/home` là BeeGFS.
Sau khi cấp ID vẫn cần kiểm tra storage driver/data-root: tài liệu Docker nêu
`fuse-overlayfs` cho kernel>=4.18, hoặc `vfs`; chưa thử Docker trên BeeGFS.
VPN đã chạy bằng mapping một UID không chứng minh đủ mapping nhiều UID cho Docker.
Ở lần kiểm tra 02:20 UTC chưa cài Docker hay thử daemon; đây là mốc lịch sử,
được bổ sung bằng lần cài thử bên dưới. Kết luận chỉ áp dụng shell đã kiểm tra,
không suy sang compute node hay NSCC.

**Cài thử theo yêu cầu tiếp theo, khoảng 02:23 UTC:** đã giải nén binary Docker29.9.1
và RootlessKit3.3.0 vào `~/.local/opt/docker-rootless/bin`, symlink CLI ở
`~/.local/bin/docker`; `docker --version` chạy được. Trình cài chính thức,
setuptool install, `rootlesskit true` và lệnh start daemon đều thất bại ở subuid/subgid.
Lỗi runtime xác nhận `no subuid ranges found for user 3042 ("apacsc42")`.
Chưa chạy được container, chưa có Docker service; không sửa cấu hình host.
[Cách dùng và log cài thử](../docker-rootless/README.md).

[Bằng chứng](../notes/inspection/docker-rootless-20261017-022048UTC.json),
[Docker prerequisites](https://docs.docker.com/engine/security/rootless/),
[storage limitations](https://docs.docker.com/engine/security/rootless/troubleshoot/).

## Slurm và PBS

**Hỏi: PBS là gì, khác Slurm thế nào?**

Cả hai là hệ thống nhận job, xếp hàng, cấp tài nguyên và thu hồi khi job kết thúc. Script và cách yêu cầu tài nguyên khác nhau.

| Việc cần làm | Slurm | PBS |
|---|---|---|
| Gửi job | `sbatch job.sbatch` | `qsub job.pbs` |
| Xem job của mình | `squeue -u "$USER"` | `qstat -u "$USER"` |
| Hủy job | `scancel JOB_ID` | `qdel JOB_ID` |
| Xem chi tiết job | `scontrol show job JOB_ID` | `qstat -f JOB_ID` |
| Xem partition/queue | `sinfo` | `qstat -Q`, `qstat -Qf` |
| Xem node | `sinfo -N`, `scontrol show node` | `pbsnodes -a` |
| Chỉ thị trong script | `#SBATCH` | `#PBS` |

Không có một lệnh PBS duy nhất thay toàn bộ thông tin của `sinfo`: xem queue bằng `qstat -Q`, node bằng `pbsnodes`.

Đọc thêm: [submit PBS trên NSCC](13-submit-pbs-nscc.md).

## Bài thi Qwen và benchmark

**Hỏi: “Submit job” có phải nộp bài BTC không?**

Không. `sbatch`/`qsub` chỉ gửi công việc vào scheduler để chạy. Nộp bài cuộc thi là gửi gói theo yêu cầu BTC qua kênh nộp bài của họ. Một job có điểm tốt chưa có nghĩa đã nộp bài hoặc đã lên leaderboard.

**Hỏi: Benchmark mở API rồi gửi đồng thời à?**

Đúng. Job bật model server/gateway, AIPerf gửi request HTTP streaming. Với concurrency N, client giữ tối đa N request đang xử lý và thay request kết thúc bằng request mới. Đây là tải closed-loop.

**Hỏi: Dataset Shakespeare với MMLU-Pro/GPQA là sao?**

Đó là hai mục đích khác nhau:

- Prompt synthetic dựa trên Shakespeare dùng tạo tải có độ dài kiểm soát để đo tốc độ.
- Các bộ câu hỏi kiến thức/khoa học như MMLU-Pro, GPQA minh họa cách đo chất lượng câu trả lời. Không được coi chúng là danh sách evaluation cuối cùng của BTC nếu chưa có xác nhận.

**Hỏi: Mục tiêu là chạy hết dataset à?**

Mục tiêu hiệu năng là phục vụ nhiều request đạt chuẩn mỗi giây trong cửa sổ đo. 12.800 entry tạo sẵn không phải số request bắt buộc chạy hết. Cấu hình benchmark đã dùng: input khoảng 4.000 token, output 200 token; warmup 60 giây, đo 120 giây, grace tối đa 30 giây.

**Hỏi: TTFT, ITL, SLA, goodput là gì?**

- **TTFT**: thời gian từ gửi request tới token đầu tiên; ngưỡng 3.000 ms.
- **ITL**: thời gian trung bình giữa các token trong một request; ngưỡng 20 ms.
- Một request đạt SLA phải đạt **cả hai**; ít nhất 90% request phải đạt, tính request lỗi trong mẫu số.
- **Goodput**: số request đạt SLA mỗi giây. Với 200 output token/request, nhân 200 thành good output tokens/s.

“Good” ở goodput nói về độ trễ, không chứng minh câu trả lời đúng. Điểm lấy từ export AIPerf, không tự thay bằng phép chia số request cho 120 giây.

**Hỏi: Chất lượng phải đạt 99% nghĩa là output giống 99% à?**

Là ít nhất 99% **điểm tham chiếu**, không phải giống từng token và không phải 99% câu đều đúng. Ví dụ reference 80 điểm thì 99% là 79,2. Harness cuối cùng, reference scores và cách gộp benchmark chưa được xác nhận trong các lần kiểm tra đã ghi; không tự tuyên bố qua accuracy chỉ vì đã qua SLA hay smoke test.

**Hỏi: Quantize có làm output khác không?**

Có thể. Cả khác biệt kernel và thứ tự tính số thực cũng có thể đổi token. Theo luật đã nghiên cứu, dùng checkpoint FP8 chính thức, không tự requantize weights xuống INT4/FP4; không bỏ layer/experts để lấy tốc độ. KV phải FP8 hoặc cao hơn. Qua ngưỡng accuracy không miễn các hạn chế kỹ thuật riêng.

Nguồn luật và giải thích chi tiết đã lưu tại [cơ chế benchmark Qwen](07-co-che-benchmark-qwen.md). Các thông tin này là ghi chép từ nghiên cứu trước; khi nộp bài cần đối chiếu bản luật hiện hành.

## Cấu hình tối ưu nghĩa là gì?

**Hỏi: Một ứng viên là bộ config hay một cách host model? Có SGLang/optimizer không?**

Có thể là một bộ tham số trong cùng engine, hoặc một kiến trúc phục vụ khác. Những trục đã bàn gồm engine SGLang/vLLM, chia GPU prefill/decode, TP/DP/EP, routing, concurrency, KV dtype, attention/MoE kernels, CUDA graphs và speculative decoding. Đổi engine là thay đổi lớn hơn đổi một tham số; kết quả vẫn phải đo cùng protocol.

**Hỏi: Prefill và decode là gì?**

Prefill đọc prompt, tính trạng thái ban đầu và KV cache. Decode dùng trạng thái đó để sinh từng token tiếp. Tách hai phần cho phép cấp GPU và tối ưu riêng, nhưng phải truyền KV và điều phối thêm.

**Hỏi: `P8-TP4_D8-TP4-EP4` đọc sao?**

Trong cách đặt tên thí nghiệm của mình: P8 là tổng 8 GPU prefill, TP4 thường thành hai worker 4 GPU; D8 là tổng 8 GPU decode, TP4/EP4 mô tả cách chia tensor và experts ở decode. Phải đọc placement/script để biết chính xác số replica và nhóm song song; tên chưa mô tả hết cấu hình. Bản tốt nhất hiện ghi nhận dùng **D8-TP8-EP8**, khác ví dụ trong câu hỏi.

**Hỏi: EP1 → EP2 đổi gì?**

Đổi expert-parallel group từ một lên hai GPU/rank: chia experts qua nhiều thiết bị thay vì giữ toàn bộ nhóm experts ở một rank. Có thể giảm bộ nhớ/tính toán mỗi rank nhưng tăng trao đổi dữ liệu; không mặc định nhanh hơn. Việc đổi trong từng thí nghiệm phải đọc cùng TP và placement.

**Hỏi: Topology 07 với 09 là tên gì?**

Là mã ứng viên nội bộ theo danh sách đã lập, không phải phiên bản model hay mã chuẩn BTC. Đọc bảng topology/script để biết chúng khác gì; số lớn hơn không có nghĩa tốt hơn.

**Hỏi: NIXL là gì?**

Thư viện trao đổi dữ liệu cho hệ inference phân tán. Trong thí nghiệm này nó tham gia chuyển KV cache từ prefill sang decode; không phải một model hay optimizer tự tăng chất lượng.

Đọc thêm: [ứng viên](06-ung-vien-qwen.md), [không gian tìm kiếm](08-khong-gian-tim-kiem-qwen.md), [17 topology](09-thu-het-topology-qwen.md), [NIXL](10-nixl-la-gi.md).

## Queue, lỗi và lịch sử thí nghiệm

**Hỏi: `PENDING (Priority)` có phải job treo?**

Là chưa được scheduler cấp tài nguyên do thứ tự ưu tiên/tài nguyên phù hợp. Chưa chạy thì chưa có benchmark. Có job đội khác chạy trước không tự chứng minh scheduler lỗi hay đội đó có quyền đặc biệt.

**Hỏi: “Nodes required ... DOWN, DRAINED or reserved ...” nghĩa là gì?**

Tài nguyên phù hợp đang không khả dụng vì trạng thái node hoặc reservation/partition ưu tiên. Đây là lý do scheduler chưa khởi chạy; không đủ để kết luận script mình hỏng hay tất cả GPU đều hỏng.

**Hỏi: Hủy rồi submit lại có lên trước không?**

Không có bảo đảm. Có thể mất tuổi chờ; phải xem chính sách priority của cụm. Không tự hủy và gửi lại chỉ vì đang chờ.

**Hỏi: Team 01 gửi nhiều job vì có ưu đãi à?**

Snapshot 15/10 cho thấy cả hai tài khoản dùng QoS normal với giới hạn 5 job đang trong hệ thống. Họ có lịch sử nhiều lần submit hơn, không có nghĩa chạy đồng thời hàng trăm job. Tên job chỉ gợi ý hướng thử, không tiết lộ cấu hình đầy đủ hay điểm số.

**Hỏi: Job `COMPLETED` là thí nghiệm thành công à?**

Chỉ xác nhận scheduler thấy tiến trình kết thúc theo mã trả về. Cần kiểm tra có đủ artifact, server/client không lỗi, benchmark hoàn chỉnh và đạt SLA. Job lỗi vẫn lưu làm dữ kiện nhưng **không tính là cấu hình đã đo thành công**.

**Hỏi: Mỗi lần chạy có lưu không? Tra ở đâu?**

Tại [thư mục thí nghiệm](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/):

- [RUNS.md](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/RUNS.md): sổ các lần chạy.
- [SERVING_TUNING_RESULTS.md](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/SERVING_TUNING_RESULTS.md): báo cáo tuning.
- `runs/JOB_ID/`: log và artifact của từng job.
- `serving-tuning/registry.json`: trạng thái controller; đối chiếu scheduler để biết job thật sự đang chạy hay chỉ đang chờ.

Đọc thêm: [vì sao chờ lâu](11-tai-sao-job-cho-lau.md).

## VPN và NSCC

**Hỏi: Không có root có cài VPN bằng terminal được không? Docker có giúp không?**

Trên máy này đã kết nối được bằng `snx-rs` và rootless user/network namespace cùng `slirp4netns`. Không cần Docker. Đây là khả năng đã kiểm chứng của môi trường này; không phải mọi server đều cho phép unprivileged namespaces/TUN.

**Hỏi: Kết nối NSCC dùng địa chỉ nào?**

Gateway đã xác minh là **`vpn1.nscc.sg`**. SSH vào **`aspire2p.nscc.sg`** qua VPN. Không ghi credential vào note. Helper và hướng dẫn ở [VPN NSCC](12-vpn-nscc.md).

**Hỏi: Submit PBS thay cụm H200 được không?**

Đã chạy thành công probe PBS **220457.pbs111** trên hai node, tổng **16 H100**, kiểm tra phép nhân ma trận trên cả 16 GPU. Đã chuẩn bị bản chuyển Qwen sang PBS. Điều này chưa chứng minh benchmark Qwen hoặc đường truyền KV đã hoạt động trên NSCC.

**Hỏi: Có credit không, submit thoải mái không?**

NSCC có dự án `59010042`, grant ghi nhận 64.000 SU, mức 128 SU/GPU-giờ. Tương đương 500 GPU-giờ, hay 31,25 giờ nếu dùng liên tục 16 GPU, **trước khi trừ sử dụng**. Đây không phải số dư trực tiếp; cần xem accounting mới. Không áp mức giá NSCC sang cụm H200 khi chưa có chính sách tương ứng.

Chi tiết script, quota và các hạn chế chuyển môi trường: [PBS trên NSCC](13-submit-pbs-nscc.md).

## Các mốc kết quả đã xác nhận

**16/10/2026 — Vì saoCodexusage tụt dù khôngnhắn? CóphảiVPS?**

AutopilotVPSgọicodexexec bằngtài khoảnChatGPTđãđăngnhập,nênvẫntiêuquota.
LocalPythonpoll/squeue/PBSkhôngtựgọiLLM;GPU SU làngânsáchriêng. Chat vàCodex
nơikhác cũngcóthểtiêu. Audit24h:133starts,35completed,95quotaerror;43,49Minput
GỒM40,64Mcached,442203output. Khôngquyđổitrựctiếp tokensangtiền/%quota.
ĐãsửatriggerPriority/Resources,cronthiếurg làmbackoffhỏng,vàrútCURRENT+POLICY
68,8KB→7,8KB,giữarchiveđầyđủ. Khôngđổimodel,dừngGPUhayVPN.
[Audit](../research-autopilot/USAGE_AUDIT.md),[OpenAIdocs](https://learn.chatgpt.com/docs/pricing).


**16/10/2026 13:23UTC — Launcher mới đã hoạt động thật chưa?**

Có. Usercho phép login,VPN lênIP10.103.62.12,tách tmuxbằngCtrl-B,D rồi
kiểm lại tunnelvẫnUP;SSHNSCCthànhcông. Đãcó1savedIKEsessiontrongprivateSQLite,
DB0600/cache0700,khôngcopykeys/passwordvàonote. Cấu hìnhđềxuất24giờ,chưa
đủthờigianchứngminh24h;persistkhôngbảođảmreuseSAđãexpired/revoked.
KhôngCtrl-C/killphiênđangchạy. ClientkhônghiệnchallengeDUOtextnênkhôngđoánfactor.
[Bằngchứng](../vpn-rootless/inspection/login-success-20261016-1323UTC.json).


**16/10/2026 — Credential, session cũ và lầnVPNngắt mới nhất khác nhau thế nào?**

Username/passwordngườidùngđãcungcấpởchat,khôngchépvàonote/file;05:40UTC
đãdùngthànhcông. Hiệulựchiệntạikhôngđượcxácminhlại,chỉcóthểthử khiusercho
phép;loginmớicóthểcầnDUO. PasswordkhôngthaythếSA/ticketcũđãmấtbảnlocal.

Lầnngắtmới chưađủlogđểkếtluận. VPNcòntraffic06:26,journalghiSSHdisconnect
06:28–06:29. CáchlaunchquaPTYgắnphiênlàđiểmyếu;quan hệnguyênnhânchưachứngminh.
Đãchuẩnbịtmuxterminalđộclập+privateexitlogs,chưaloginthật;đãtestmockPTYvà
privatecachebind. Helpermớiike-persisttrue,sessioncacheđượclưuprivate0700/0600
khiđăngnhậpthànhcông;khôngthểhứakhôiphụcSAđãexpired/revokedhayđủ24giờ.
[Hướngdẫn](../vpn-rootless/README.md),[chẩnđoán](../vpn-rootless/inspection/vpn-drop-forensics-20261016.json).


**16/10/2026 — Có tựtrigger đúngchat này khi người dùngđi vắng không?**

CơchếđãcàilàcronVPS5phút,kiểmtrạngthái vàgọiCLIphiênmới qua notehandoff,
khôngphảifork/resumechatgốc vàkhôngtựđẩy tin vàochat. Vẫn tiếp tục nghiêncứu,
thu/đánhgiákếtquả vàsubmitcácbướcđủgate/budget khiuserkhôngnhắn.
Userđãgiaoquyềntiếptục lúc06:21UTC;khôngcầnnhắclạichomỗiwave. Giữgiớihạn
ngânsách,slotGPU vàkhôngtựloginVPN/DUOmới. Báocáoởresearch-autopilot/LATEST.md.


**16/10/2026 — Submit nhiềujob có nhất thiết dùngnhiềuGPU cùnglúc không?**

Không. ĐãgửiPBS220720(MNNVL)→220721(FlashInfer)→220722(prefetch) với
`qsub -W depend=afterany:JOB_ID benchmark.pbs`. Job sau giữH(chờdependency)
cho đếnjobtrướckếtthúc,bấtkểmãexit. Chỉ1job16GPUallocated cùnglúc,khôngphải48GPU.
Mụcđíchgiảmđợi người submit khiGPUvừarảnh. Các thửnghiệm nàyđộclậpso cùngbaseline;
`afterany` khôngxácnhậnjobtrướcđạtSLA hayquality. Mỗi45phútreserve1536SU,
chuỗi3jobreserve4608SUtrướckhiqsub. Khôngreleaseholdđểphádependency.


**16/10/2026 05:40UTC — Lần usercho phép thửDUO mới nhất?**

VPN đãkếtnốiIP10.103.62.11, SSHverifieda2ap-login01, BatchModekiểm lại05:42:43UTC
đạt. KhôngthấyDUOchallengechữ,ngườidùngchưabáophone,nênkhôngđoánfactor.
ĐềxuấtIKE24h,chưakiểmđủ24h;phiênhiện chưa lưuSA,giữnguyênkhôngrestart.
220575terminalexit0,artifactcầnreviewriêng;khôngcoiexit0làbenchmarkđạt.


**16/10/2026 — Đội khácv111 có nghĩa mình thua không?**

v111là nhãnversion họ đặt, không phải benchmarkscore. Chưa cóđiểmcủahọ để
kếtluậnaihơn. Kếtquảmới mình23904MNNVL+FlashInfer2631,09goodt/s,SLA99,02%,
hơnMNNVLmean1,49%nhưngmớimộtlượt; đãgửi23973/23975lặp độc lập và23974freshcontrol.
Chunk2048/8192đãthử vàkém hơn. Mục tiêu là đođủ vàlặpđượcgain,khôngđua tênjob.


**16/10/2026 — PhiênVPN cũ có được lưu đểresume không?**

Cấu hình ban đầu của trợ lý đặt`--ike-persist false`. Sourceclient chỉ ghiSA
vào`/var/cache/snx-rs/ike-sessions.db` khi bậtpersist. Đã tìm đườngchuẩn,
cache/config/data, namespace, SSHsocket vàfd của process còn sống: không có
sessionblob/DB hay process cũ. Vì vậy chưa có dữliệulocal đểresume phiênVPS.
PhiênWindows của người dùng là kết nối riêng; search không kiểm chứng trạng
thái server hay lấy sessionWindows. Không thửlogin/DUO trong lần tìm này.
[Bằng chứng](../vpn-rootless/inspection/session-recovery-search-20261016.json).


**16/10/2026 — Đổi IKE sang24giờ có đăng nhập lại được chưa?**

Đã thử lại đúng thông tin được cung cấp lúc00:17:42UTC, helper đặt86400s.
00:18:46UTC gateway vẫn trả`Authentication failed,status0`, không tạo tunnel.
Đổi thời hạnIKE không tự giải quyết lỗi xác thực. Mã0 chưa chỉ ra nguyên nhân;
đã hỏi điện thoại đội trưởng cóDUOpush khớp lần này, chưa nhận phản hồi.
[Bằng chứng](../vpn-rootless/inspection/login-attempt-20261016-0017UTC.json).


**16/10/2026 — 8giờ là thời gian đặt ở client thôi à?**

8giờ là **mặc định client snx-rs đề xuất** (`ike-lifetime=28800`), không phải
bằng chứng gateway NSCC chỉ cho8giờ. Thời hạnIKE thực tế là giá trị sau đàm phán;
client dùng giá trị đó để kiểm tra hết hạn. Vì vậy không được nói đó chỉ là bộ
đếm tùy ý ởclient, hoặc tự đặt24giờ là chắc chắn server sẽ giữ24giờ. Helper đã
đổi sang đề xuất86400giây; chưa kiểm chứng phiên mới giữ24giờ. Thời hạnIKE cũng
không đồng nhất với phiên đăng nhập24giờ trênWindows. Lỗi login mới là vấn đề riêng.


**15/10/2026 — Đã tìm thấy vì sao clientLinux có thể ngắt sau8giờ.**

Kiểm tra đúng source`snx-rs6.5.1`: default`ike-lifetime=28800` (8giờ).
Helper cũ không override; client đề xuất lifetime này khi tạoSA và kiểm tra
lifetime đã đàm phán để tự ngắt. Điều này phù hợp log phiên cũ ngắt20:17UTC,
không phải bằng chứng giới hạn phiênWindows/BTC chỉ8giờ. Đã sửa helper thành
`--ike-lifetime 86400` để đề xuất24giờ cho kết nối mới. Chưa kiểm chứng giữ đủ
24giờ; gateway vẫn có thể áp lifetime riêng. Lỗi từ chối đăng nhập lại là vấn đề
riêng, không được coi mặc nhiên là do lifetime. [Tài liệu đúng phiên bản](https://github.com/ancwrd1/snx-rs/blob/v6.5.1/docs/options.md),
[chẩn đoán đã lưu](../vpn-rootless/inspection/ike-lifetime-diagnosis.json).


**15/10/2026 — Vì sao VPN thoát dù Windows thường giữ24giờ?**

Đã lấy được log cuối của phiênLinux cũ: **20:17:01UTC** báo
`IKE SA expired, disconnecting tunnel`, sau đó`Tunnel disconnected`, tiến trình
thoát mã0. Nguyên nhân ngắt được ghi nhận là IKE SA hết hạn, không phải kết luận
mật khẩu sai. Lần đăng nhập lại20:40 bị từ chối xác thực là sự kiện riêng, chưa
rõ nguyên nhân. Chưa xác định vì sao clientLinux không giữ/gia hạn được như
Windows; không khẳng định chính sách phiênVPN của BTC chỉ kéo dài8giờ.

**24giờ đã chỉnh trong helper là SSH `ControlPersist=86400`, không phải lifetimeVPN.**
Localhelp nói `ike-persist` là lưu/đọc phiênIKE trên đĩa; không được đồng nhất
nó với chức năng tự gia hạn khóa. [Log chẩn đoán](../vpn-rootless/inspection/vpn-disconnect-20261015.json).


**15/10/2026 20:07UTC — Tận dụng GPU và thời gian thế nào?**

NSCC baseline tốn khoảng20phút load/khởi tạo nhưng đo một mức tải chỉ vài phút.
Vì vậy job220575 xin16H100 tối đa45phút, load một lần rồi đo N32/34/36/38/40/42.
Mỗi mức vẫn warmup60giây, đo120giây, grace30giây; dừng tăng nếu mức trước không
đạtSLA hoặc có lỗi. Không rút ngắn phép đo để có nhiều con số.

H200 đã đủ5slot với23839,23859 và ba pilot23904–23906. Cả hai cụm đang queued tại
lần kiểm tra; submit đầy queue không có nghĩa GPU đã chạy. Hai backendH100 kế
tiếp đã chuẩn bị, chỉ gửi từngjob sau khi đọc kết quả và đối soátcredit.

Ngân sách commissioning4096SU được mở sang campaign16384SU tổng theo yêu cầu
tiếp tục research, gồm cả chi phí cũ; vẫn giữ13000SU dự phòng. Job45phút16GPU
reserve1536SU. Cron được đổi từ30 sang **5phút** để phản ứng với job kết thúc;
không đổi trạng thái thì không gọiLLM liên tục, lỗiquota nghỉ30phút.
[Plan và script](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/CONTINUOUS_RESEARCH.md).

**15/10/2026 — Codex có tự thức để làm tiếp được không?**

Đã thử chạy CLI thực tế thành công và cài cron trên VPS: kiểm tra mỗi30phút,
gọi `codex exec` khi trạng thái đổi hoặc đã6giờ chưa thức. Mỗi lượt tối đa20phút,
có lock chống chạy chồng. Controller Slurm vẫn riêng, tự theo dõi/gửi các bước đã
lập; Codex wake dùng để phân tích và chuẩn bị bước nghiên cứu tiếp.

Đây là workflow cron cục bộ, không phải automation đã đăng ký trong giao diện
Scheduled. Không tự gửi được tin vào chat hiện tại. Xem [báo cáo mới nhất](../research-autopilot/LATEST.md),
[lịch sử](../research-autopilot/HISTORY.md), [cách tạm dừng](../research-autopilot/README.md).
Cần VPS, cron và đăng nhập Codex hoạt động; dùng quota Codex riêng với SU GPU.
VPN/SSH hết phiên có thể cần đăng nhập lại. Lịch dừng sau15/11/2026.
Tham khảo [OpenAI: non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode)
và [Scheduled tasks](https://learn.chatgpt.com/docs/automations).

**15/10/2026 — credit có đủ research còn lại không?**

Kiểm tra trực tiếp bằng `myprojects` lúc 22:55 giờ Singapore (14:55 UTC); ledger ghi mốc 22:40:02: grant **64.000 SU**, đã dùng **70,543 SU**, còn **63.929,457 SU**, không có SU đang giữ cho job chạy. Không có job PBS của mình trong queue tại lần kiểm tra.

Với mức 128 SU/GPU-giờ và 16 GPU/job, số dư tương đương **31,22 giờ chạy đủ 16 GPU**. Nếu một lượt chiếm GPU 10/20/30 phút thì khoảng 187/93/62 lượt tương ứng, chưa dành dự phòng. Tính cả load model, khởi tạo, diagnostic và thời gian lỗi vẫn giữ allocation; không chỉ tính 120 giây benchmark. Chờ queue chưa chạy không phải GPU runtime.

Đánh giá: đủ cho một chiến dịch có giới hạn khoảng **40–49 lượt, mỗi lượt tối đa 30 phút**, còn khoảng 20% trở lên cho sửa lỗi và xác nhận. Chưa thể bảo đảm thử hết mọi nhánh nghiên cứu: EAGLE3, vLLM và topology mới có thể cần nhiều lần sửa, và thời gian chạy H100 chưa được đo cho Qwen. Bốn job H200 đang chờ thuộc cụm khác, không được tự quy thành khoản trừ vào project NSCC này. Raw ledger: [credit snapshot](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/credit-20261015-1455UTC.txt).

**15/10/2026 — trả lời câu “Còn job ở đây sao rồi?”**

- Cụm H200: N53 round-robin, topology P8-TP4 / D8-TP8-EP8, job **23773** đạt **2.438,47 good output tokens/s**, SLA **98,88%**, không lỗi/hủy request.
- Lần độc lập trước, job **23616**, đạt **2.433,41**. Hai lần gần nhau giúp xác nhận khả năng lặp lại; không phải chứng nhận accuracy của BTC.
- Tại lần kiểm tra đó, **23776, 23777, 23778, 23780** còn `PENDING (Priority)`. Đây là lịch sử, muốn biết hiện tại phải kiểm tra queue mới.
- NSCC mới xác nhận probe 16 GPU; checkpoint đầy đủ và serving images chưa được chuyển xong tại mốc ghi chép này, chưa có số benchmark Qwen NSCC.

**15/10/2026 — FlashInfer nhanh nhất một lượt thì đã chọn được cấu hình tốt hơn chưa?**

Job H200 **23777** đạt **2.440,39 good tokens/s**, SLA **98,95%**, ITL trung bình **18,71 ms**, không lỗi/hủy. Log cả tám rank xác nhận decode dùng FlashInfer, prefill dùng FA3. Tuy nhiên chỉ cao hơn control N52 **1,68%**, chưa đạt ngưỡng tự lặp **2%**, và hơn lượt N53 đã lặp **23773** khoảng **0,08%**. Vì vậy chưa đủ bằng chứng chọn cấu hình thắng. Diagnostic đầu ra vẫn **7/8**, không có lỗi mới so với baseline; chưa phải accuracy BTC. [Đối chiếu và log gốc](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-07/PLAN.md).

**15/10/2026 — Có tên file model rồi thì có thể gửi job GPU ngay không?**

Chưa. Downloader có thể đổi tên shard trước khi băm SHA256 xong. Preflight NSCC hiện yêu cầu manifest tải hoàn tất đúng revision, đủ kích thước chính thức và kết quả SHA256 LFS của model; images được băm lại trước khi gửi job. Năm ca kiểm thử CPU đã xác nhận chặn manifest chưa xong, shard thiếu, digest sai và image hỏng dù cùng kích thước. Vẫn phải kiểm ngân sách riêng: cap commissioning **4.096 SU** tính cả **70,543 SU** probe, dành tối đa **1.024 SU** trước mỗi job 16 GPU/30 phút. [Sổ ngân sách](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/nscc-budget.json).

**15/10/2026 — Có cờ backend trong config là đủ chứng minh đã dùng backend đó chưa?**

Cần xem log thực thi vì engine có thể tự chọn hoặc fallback. Job **23778** có đủ tám rank ghi `workspace initialized: backend=mnnvl` lúc **16:02:43 UTC**; đây là xác nhận MNNVL đã khởi tạo trên H200, tiến thêm so với kiểm tra tương thích source. Chưa có benchmark đầy đủ thì chưa kết luận backend chạy hết workload, nhanh hơn hay đạt SLA/accuracy. [Chứng cứ startup](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-1600UTC/wake-summary.json).

**15/10/2026 — MNNVL đã giúp nhanh hơn chưa, và có đánh đổi gì?**

Job H200 **23778** đã hoàn tất N52: **2.592,16 good tokens/s**, SLA **99,01%** (1.595/1.611 request), ITL trung bình **17,13 ms**, không lỗi/hủy. Cao hơn control N52 **23607** khoảng **8,01%** và N53 **23773** khoảng **6,30%**. Tuy nhiên TTFT trung bình tăng từ **346,84 lên 516,28 ms** so với 23607, nên cần xem cả tốc độ decode và độ trễ token đầu. Đây vẫn là một lần đo; watcher đã gửi lượt lặp độc lập **23839**, còn N54 phải qua cổng xác nhận cũ. Diagnostic **7/8** không có lỗi mới, chưa chứng minh accuracy BTC. [Export, đối chiếu và hash chứng cứ](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-1630UTC/mnnvl-review.json).


**15/10/2026 — Exit 137 khi chuyển serving sang PBS có chắc là hết GPU memory không?**

Không. Baseline H100 **220486.pbs111** kết thúc exit1, còn `pbsdsh` ghi137; log PBS đầy đủ chỉ ra **PermissionError** khi Triton ghi cache `/tmp/sglang-decode-0/triton/...` trong bước CUDA graph. Chưa có export nên không phải một điểm đo thất bại SLA. Bản retry **220489.pbs111** giữ nguyên worker/model/client/N32, dùng thư mục tạm duy nhất cho từng container và bind vào `/tmp`; kiểm tra CPU chỉ xác nhận tính riêng và quyền ghi, runtime phải kiểm tra trên compute node. Khi log role rỗng, vẫn cần giữ stdout PBS vì output con của `pbsdsh` có thể nằm ở đó. [Log và kiểm tra bản sửa](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-1701UTC/).

**15/10/2026 — “In Doubt” có phải credit đã tiêu hết chưa?**

Snapshot lịch sử NSCC lúc **01:00:01 Singapore ngày16/10** ghi70,543SU đã dùng,1.024SU “In Doubt”,62.905,457SU balance. Balance đã trừ khoản giữ trước của job; không trừ cùng khoản đó lần nữa khi đọc số dư. Khi ledger chưa đối soát, giữ dự phòng local bảo thủ cho chi phí chưa xác định; không bắt buộc chờ ledger cũ nếu còn ngân sách đủ cho bước được phép. Trầncommissioning tại mốc đó là4.096SU; đã được thay bằng campaign **16.384SU tổng** lúc20:03UTC15/10, giữ tối thiểu13.000SU projectbalance. Không dùng4.096SU như chính sách hiện hành. [Sổ ngân sách](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/nscc-budget.json).

**15/10/2026 — Hết readiness timeout có nghĩa model bị treo không?**

Chưa đủ để kết luận. NSCC **220489.pbs111** hết hạn600giây khi hai prefill vẫn tăng số shard đã đọc; decode đã hoàn tất graph và sẵn sàng. Log ghi khoảng38giây/shard, nên checkpoint có thể cần lâu hơn giới hạn cũ; đây là suy luận từ tiến độ, chưa xác định nguyên nhân đọc chậm. Retry **220562.pbs111** dùng hạn khởi động chung1.200giây cho cả worker, giữ walltime30phút và benchmark60/120/30 đầy đủ. Không làm mới timeout cho từng endpoint và không rút ngắn phép đo khi gần hết giờ. Tại19:18UTC job còn Q, chưa có kết quả H100. [Log, chẩn đoán và kiểm tra CPU](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-1915UTC/readiness-review.json).

**15/10/2026 — Có thể tách thời gian startup prefill và decode khi log PBS chưa xuất không?**

Có thể dùng `/health` và `/get_server_info` của chính job đang chạy. NSCC **220562.pbs111** ghi hai prefill TP4/EP1 tải weight **851,14/851,64 giây**, CUDA graph **119,07/114,96 giây**; decode TP8/EP8 tải weight **98,57 giây**, graph **126,82 giây**. Cả ba healthy lúc **19:42:11 UTC**, trước hạn readiness1.200giây; hai router P/D riêng đều ghi chat HTTP200 lúc19:42:56. Như vậy lần này đã quan sát startup hoàn tất, không chỉ ngoại suy từ shard. Thời gian tải weight chưa xác định nguyên nhân I/O hay xử lý CPU, và HTTP200 chưa phải accuracy hoặc benchmark đầy đủ. Khi kiểm tra IP compute trực tiếp, tắt proxy cho request đó để không nhầm lỗi proxy503/504 với phản hồi worker. [Runtime và bằng chứng từng cặp](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-1930UTC/startup-review.json).

**15/10/2026 — Đã có baseline Qwen thật trên H100 NSCC chưa?**

Có. **220562.pbs111** kết thúc exit0 sau23phút33giây: N32 đạt **1.565,16 good tokens/s**, **100% SLA (966/966)**, ITL18,57ms, TTFT346,63ms, không lỗi/hủy; export giữ đủ60/120/30 và4000/200. Diagnostic7/8 còn lỗi reverse đã biết, chưa phải accuracy BTC. Đây là một điểm H100, cần xác nhận và kiểm tra long-context trước khi chọn cấu hình; số đo H200 không thay thế phép đo H100. [Export, protocol và log cuối](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261015-1930UTC/baseline-review.json).

## Cách tiếp tục ghi sổ

Khi bổ sung câu hỏi kiến thức từ cuộc trò chuyện: ghi câu hỏi, trả lời ngắn, link tới bài chi tiết nếu đã có. Với số liệu thay đổi theo thời gian: ghi ngày, job ID và nguồn kết quả. Khi sửa một kết luận cũ: nêu rõ phần đã sửa; không biến suy đoán thành dữ kiện. Các cập nhật trạng thái lặp lại để trong lịch sử thí nghiệm, chỉ đưa mốc đáng nhớ vào sổ này.

## Prefill nạp weights chậm và nhánh engine — 2026-10-15 20:13 UTC

**Hỏi: Prefill851giây, decode99giây có chứng minh storage chậm không?**

Chưa. Job220562 dùng hai replicaTP4/EP1 ở prefill và TP8/EP8 ở decode; lượng weights mỗi rank phải xử lý, số tiến trình và CPU binding khác nhau. Nguồn image thực cho thấy loader mặc định8luồng/rank, dùng mmap và bộ đệm giới hạn. Cần dữ liệu page fault/I/O/NUMA và phép thử kiểm soát để kết luận nguyên nhân.

**Hỏi: Bật prefetch chỉ thay cách đọc file?**

Trong image đã kiểm tra, một flag prefetch vừa đọc nền vào page cache, vừa chuyển loader sang iterator một luồng khi extra config để mặc định. Việc chia shard diễn ra trong từng nhómTP; hai replica có thể vẫn đọc trùng. Pilot06 mới được chuẩn bị cục bộ, chưa chứng minh tăng tốc. Xem [phân tích nguồn](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/LOADER_RESEARCH.md).

**Hỏi: Có draftEAGLE3 và vLLM hỗ trợMoE là chạy ngay được không?**

[Draft công khai](https://huggingface.co/lmsys/Qwen3-235B-A22B-EAGLE3) nêu Qwen3-235B-A22B; tương thích và acceptance vớiInstruct-2507-FP8 chưa xác minh. NhánhEAGLE3 phải giữ target kiểm chứng mọi token và kiểm tra riêng trước khi kết hợpPD. [NIXL vLLM](https://docs.vllm.ai/en/latest/features/nixl_connector_compatibility/) có hỗ trợMoE/heteroTP trong tài liệu hiện tại; image được chọn vẫn phải kiểm tra độc lập, giữ handshake và thống nhất model/KV/backend. Chưa chạy hai nhánh này. Thiết kế và nguồn ghim ở [research-next](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/README.md).

## Đo nguyên nhân startup chậm — 2026-10-15 20:20 UTC

**Hỏi: Expert không thuộc rank bị bỏ qua có chứng minh rank không đọc weights đó không?**

Chưa. Source image thực tạo tensor view qua iterator rồi mới gọi loader expert; loader trả sớm khi expert không thuộc rank. Điều này chứng minh thứ tự xử lý, chưa đo các trang mmap đã đọc. Công cụ [startup-sampler.py](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/startup-sampler.py) mới kiểm tra CPU cục bộ, chưa chạy NSCC; dự kiến lấy counter của đúng cây tiến trình worker để đối chiếu page fault, CPU, I/O và NUMA. Không đọc command line, môi trường hay file model.

**Hỏi: Ghi4MiB thì write_bytes phải tăng4MiB?**

Không: kiểm tra cục bộ trên `/tmp` dạng tmpfs ghi4MiB nhưng write_bytes bằng0, còn wchar tăng4.194.309byte tính cả dòng xác nhận. Counter logical I/O và physical I/O có ý nghĩa khác nhau; không dùng counter đơn lẻ để kết luận storage NSCC. Xem [hướng dẫn và giới hạn](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/STARTUP_SAMPLING.md).

**15/10/2026,20:57UTC — Counter bị thiếu hoặc PID đổi có được coi là không làm việc không?**

Không. Chỉ tính hiệu counter khi cùngPID vàstart-time xuất hiện trong hai mẫu
liền nhau; PID tái sử dụng là tiến trình mới. Counter không đọc được phải là
`null`, không phải0. Công cụphân tíchoffline mới đánh dấu tiến trình mới/mất,
counter giảm và khoảng lấy mẫu dài; CPUcore tính từCPU-seconds/wall-second,
không tự quy ra phần trămGPU/CPUallocation. Kiểm tra bằng fixture và rawown-child
cũ đạt; chưa có phép đoNSCC. [Công cụ và hướng dẫn](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/STARTUP_SAMPLING.md).

**15/10/2026,21:01UTC — MNNVL đã lặp lại được chưa; hai số gần nhau có đủ chọn bài nộp?**

H20023778/23839 đạt2592,16/2592,92goodtokens/s ởN52, trung bình2592,54,
chênh0,029%. Đã đối chiếu payload, đủ60/120/30 và8rank khởi tạoMNNVL; lợi ích
hiệu năng được tái hiện trong hai lần triển khai này. So control23607, ITL
trung bình giảm2,38ms nhưngTTFT tăng165,43ms; phải giữ cả đánh đổi này.
Hai lượt chưa mô tả mọi biến thiên của cụm. Diagnostic7/8 chỉ còn lỗi reverse
đã biết, chưa chứng minh accuracy99%reference. Watcher đã gửiN54 job23924 theo
gate hiện có; chưa có kết quảN54 tại21:01UTC.4000/200 là cấu hình yêu cầu,
export quan sát input trung bình3986,004 vàoutput xấp xỉ200; không gọi4000 là
độ dài quan sát chính xác. [Đối chiếu và bước tiếp](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-07/MNNVL_REPEAT_REVIEW.md).


**15/10/2026,21:09UTC — Export thiếu error_request_count có đồng nghĩa0lỗi?**

Không tự suy ra như vậy. Export AIPerf thành công220562 không có metric này;
trườngerror_summary rỗng, phase manifest và log hoàn tất cùng xác nhận0lỗi,
0hủy. Bộ [review sweep offline](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/LOAD_SWEEP_REVIEW.md)
chỉ chấp nhận metric vắng khi có những bằng chứng này. Tool kiểm tra protocol,
thời gian phase thật và output so baselineH100;11ca kiểm tra CPU đạt, chưa phải
repeatGPU. Một mức tải cao fail không xóaN32đạt đầy đủ; flagoffline vẫn cần
ownqueue/credit mới, job cũ terminal và giữ budget trước khi gửi pilot kế tiếp.


**15/10/2026,21:52UTC — ConfigJSON có luôn mô tả đầy đủ lệnh đã chạy không?**

Không. Audit3jobwave9 đangPENDING cho thấyconfig kế thừa một sốtrường:23904
không ghi densegraphflags trongdecode_extra_flags,23905/23906 còn ghi4096 ở
prefill_extra_flags. Stored batchscript từSlurm khớp bảnfrozen; worker được
hash vẫn giữgraph64 và chỉ thayFlashInfer hoặcchunk2048/8192 đúng dự kiến.
Chưa cólogruntime vìjobchưa chạy. Khi đọc kết quả, đối chiếu launcher→worker→
logkhởi tạo; không suy ra thực thi chỉ từnhãnmetadata. Giữ nguyên frozenartifact
và ghi rõ giới hạn. So wave9 với23778 **và** repeat23839; control_job/reference_jobs
cũ là provenance, không phải matchedcomparator. [Bảng đối chiếu vàaudit](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/MATCHED_REVIEW.md).


**15/10/2026,22:08UTC — Weightload xong và đúngServerArgs đã đủ xác nhận repeatDP-attention chưa?**

Chưa.23859 đãRUNNING,8decodeweightload xong vàServerArgs khớp23780 ởsnapshot22:06;
đây chỉ xác nhận bước nạp/cấu hình. Cần đủ8rankNIXL, pairwarmup, full60/120/30,
export không lỗi/hủy và shortoutput không có lỗi mới. Chỉ khi đó mới so repeat,
TTFT/ITL và xétgateN54 hiện có. MNNVL là package thay thế đểsohiệu năng, không
đổi floor củagateDP đã cấu hình; DP+DeepEP thay nhiều cơ chế nên không quy gain
cho mộtkernel. Checksum/filegiống nhau giúp kiểm soát payload, không chứng minh
GPUtransport hayaccuracy99%. [Checklist vàbằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-08/REPEAT_REVIEW.md).


**15/10/2026,22:14UTC — Repeat DP-attention có xác nhận tăng tốc không; vì sao chưa chọn nó?**

Có:23780/23859 đạt2549,20/2538,08goodtokens/s, trungbình2543,64; chênh−0,436%.
Cảhai đủprotocol60/120/30,0lỗi/hủy vàkhôngcócaseoutputmớithấtbại. Mean hơn
RRcontrol23607 5,98%, nhưngthấphơnMNNVLmean1,89%. MeanITL giảm2,566ms còn16,959ms,
TTFT tăng259,95ms lên606,79ms socontrol: tănggoodputvàgiảmITL vẫn cóđánhđổiTTFT.
Đây làhiệuứngcủagóiDP8+DeepEP, khôngtácriêngđượcđónggópmỗikernel.

Runtime8rankNIXL/UCX vàcả2P/Dwarmupđạt; frozenpayload12filegiốngnhau,
sealsđạt. Watcherđãgửi23934(N54) theoexistinggate,hiệnchờResources22:12:35UTC;
queuedchưalàsốđo. Short7/8chỉreverseđãbiếtvẫnlàdiagnostic,khôngphảichứngnhận
accuracyBTC99%. Xemserving-tuning-08/REPEAT_REVIEW.md vàevidencewake-20261015-2210UTC.


**15/10/2026,22:17UTC — Gate mở N54 có phải tiêu chí đọc kết quả N54 không?**

Gate hiện có dùng repeatN52: goodput≥2448,186716, SLA≥95% và meanITL≤19,3ms
để cho phép thửN54. Benchmark lại tính tỷ lệ request đồng thời đạt TTFT≤3000ms
và ITL≤20ms, yêu cầu tỷ lệ≥90%; meanITL không thay được tỷ lệ này. Còn phải đủ
protocol60/120/30, không lỗi/hủy và output non-regression. N54 đủSLA vẫn có thể
chậm hơnN52: so goodput với từng lượt và mean, báo thêmTTFT/ITL. Một lượt chưa
xác nhận repeat hay accuracyBTC. Cả hai N54 đã audit payload đạt nhưng cònPENDING
ở22:17:19UTC; `matched_concurrency=52` làmetadata kếthừa, launcher đặt54, runtime
chưa kiểm được. [Bảng đọc N54](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/N54_REVIEW.md).


**15/10/2026,22:57UTC — AIPerf seed2026 có khóa seed của SGLang không?**

Không. Seed2026 trong benchmark điều khiển phía AIPerf; nó không tự đặt
`ServerArgs.random_seed` của engine. Audit runtime23904 so với cả23778/23839
cho thấy seed engine tự sinh khác nhau ở cảprefill vàdecode. Các ServerArgs
khác chỉ thaydecode_attention_backend sangFlashInfer đúng thiết kế. Temperature0
vàpayloadhash giống nhau không đồng nghĩa đã khóa toàn bộ nguồn biến thiên.
Chưa đo riêng tác động seed, không quy mọi chênh lệch cho seed hay cho kernel.
Giữ frozenpayload, ghi caveat và xem repeat như bằng chứng thực nghiệm có giới hạn.

23904 đã khởi tạo đủ8rankMNNVL/FlashInfer/NIXL và2P/Dwarmup, nhưng snapshot này
chưa phải phép đo hoàn tất hay xácnhậnaccuracy. [Audit và bước đọc tiếp](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/MATCHED_REVIEW.md).


**16/10/2026,00:19UTC — ITL thấp hơn có chắc goodput cao hơn; một CLI factor có cô lập mọi hiệu ứng không?**

Không. 23905 giảm prefillchunk4096→2048: ITL giảm1,3345ms so meanMNNVL,
nhưngTTFT tăng676,5036ms vàgoodputgiảm10,0747% xuống2331,35goodtokens/s.
CảSLA98,77%vàprotocolđềuđạt,khônglỗihủy:đây làphépđo hoànchỉnh chothấyđánhđổi
ởclosed-loopN52. ITL chỉđophầnpháttoken,khôngđạidiệnthờigianchờtokenđầu.
Khôngquymọichênhlệchchomộtkernelhaylậpcôngthứcnhânquảtừmeanlatency.

Dùworkerchỉđổi1flagchunk,ServerArgscả2prefillcũngđổibreakableCUDAgraphmax_bs
4096→2048vàrútgọncapture sizes. Sourcetríchimagecũngđặtdefaultgraphmaximum
theochunk. Phảighiđầyđủhiệuứngruntime,khôngnóigraphgiữnguyên;decodegraphvẫngiống.
Snapshot23906PENDINGở00:19:38UTC là lịch sử;runtime01:43 xác nhận graph8192,
finalaudit01:51 bên dưới đã hoàn tất.

23904MNNVL+FlashInferđạt2631,09goodtokens/s,hơnmeanMNNVL1,4867%;TTFTtăng122,97ms
vàITLgiảm0,9075ms. Mộtlượtđotốthơnchưachứngminhlợithếlặplại;chưachọncấuhình,
short7/8chỉkhôngcólỗimới,khôngthayaccuracyBTC. Outputobserved199–201/199–200token
khôngphảimọiresponseđúng200;giữquyướcgoodput200tokensđồngnhấtvớibaseline.
[Finalaudit vàso cả2baseline](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-09/MATCHED_REVIEW.md).


**16/10/2026, 00:52 UTC — Tái tính goodput bằng thời gian nào, và kiểm thử offline có phải repeat mới không?**

Trong bốn export N52 của 23778/23839/23780/23859, `good_request_count / goodput`
khớp đúng khoảng profiling phase `(end_ns-start_ns)/1e9` trong manifest.
`benchmark_duration` ngắn hơn lần lượt 2,798247 / 3,975055 / 2,993710 / 2,870008 ms.
Khi đối soát các run này, dùng thời gian phase để giữ convention benchmark;
không thay bằng đúng 120 giây hay thời gian job Slurm. Chưa xác định nguyên nhân
khác biệt và không suy rộng thành quy tắc mọi phiên bản AIPerf.

`review-n54.py` được kiểm bằng bốn run đã lưu và 21 ca CPU. Tái tính đúng số cũ
chỉ chứng minh bộ đọc/đối soát hoạt động với bằng chứng đó; không tạo phép đo GPU
hay independent repeat mới. Hai job N54 vẫn pending tại 00:50:03 UTC; chưa có
terminal seal thì tool không báo đã đo. Một run có đầy đủ bằng chứng nhưng SLA
thấp hơn 90% phải được ghi là điểm đo fail SLA; startup thiếu export là loại khác.

Đừng đặt thêm điều kiện observed extrema phải giống hệt giữa hai run: DP original
và repeat có max 200/201 tokens. Giữ raw count/sum/min/max và suite kiểm chất lượng;
điều này không đồng nghĩa mọi response đúng 200 hay accuracy BTC đã đạt.
[Hướng dẫn và giới hạn công cụ](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/N54_REVIEW.md).


**16/10/2026, 00:59 UTC — EAGLE3 đặt threshold1.0 đã đủ chứng minh lossless chưa?**

Chưa. Source trong image đang dùng cho thấy nhánh toàn request greedy lấy
argmax từ logits target rồi gọi compiled greedy verifier; hai threshold được
truyền ở nhánh sampling. Đây là bằng chứng luồng gọi, chưa kiểm CUDA/output thật.
FP8, cách batch và kernel verify có thể khác decode thường; phải lưu token IDs
và đối chiếu control cùng target/settings. Không suy rộng kết luận greedy sang
phân phối sampling, request penalties hoặc grammar.

Đặc biệt `SGLANG_SIMULATE_ACC_LEN > 0` có thể ghi đè acceptance sau verifier,
thậm chí điền token100 hay ép nhận draft. Default trong image là -1; future worker
phải ghi rõ -1 bên trong container. Không có bằng chứng các run trước bật chế độ
này. EAGLE hook còn tự đặt max_running_requests48 khi chưa có giá trị: control
và candidate phải cùng48 để tránh so khác giới hạn. Thiết kế hiện có3steps/topk1/
4tokens nhất quán với hook; chưa có draft weights/GPU test hay kết luận accuracy.
12 kiểm tra source/72 file hash không phải phép đo serving hoặc kiểm output.
[Review thực tế và bước thử tiếp](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/SOURCE_REVIEW.md).


**16/10/2026, 01:43 UTC — Chunk8192 có thực sự giữ graph prefill như baseline4096 không?**

Không. Runtime job23906 xác nhận cả hai worker prefill dùng chunk8192 và
breakable CUDAgraph max_bs8192, bổ sung8capture4608–8192 so với hai baseline
23778/23839. Decodegraph1–64 giữ nguyên; các trường graph khác không đổi.
Kết hợp bằng chứng chunk2048 trước đó, ba cấu hình đã đổi cả chunk lẫn graph
prefill được engine suy ra. Không quy riêng hiệu ứng goodput/startup cho chunk
scheduling. Đoạn01:43 này là audit khởi tạo lịch sử;finalaudit01:51 bên dưới
đã có đủ export/seal/protocol/raw output;accuracyBTC vẫn chưa xác nhận. [Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0140UTC/runtime-review.json).


**16/10/2026, 01:52 UTC — Tăng chunk8192 có tốt hơn baseline4096 sau khi đo đủ không?**

Lần23906 đạt2547,85goodtokens/s,SLA98,87%,0lỗi/hủy request;seal/raw/protocol đềuđạt.
So meanhai baseline23778/23839,goodputgiảm1,7238%;TTFTtăng223,294ms dùITLgiảm0,8249ms.
Đây là điểm đo hoàn chỉnh nhưng kém vềgoodput,chưa phải cấu hình nên chọn.
Cảchunk2048 và8192 đều cómeanITLthấp hơn4096 nhưnggoodputthấp hơn trong các lượt này;
không suy ra ITLthấp hơn luôn phục vụnhanh hơn,hay khẳngđịnh4096tốiưu mọi tải.

Chunk8192 còn tănggraphprefilltheo giátrịchunk;không cô lập hiệuứng scheduling.
Observedoutput200–201token,rawsum317801/1589request khớp;quyướcgoodputvẫn200tokens.
Short7/8chỉreverseđãbiết chứngminh không thêm lỗi trong suite nhỏ,khôngthayaccuracyBTC.
[Finalaudit](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0150UTC/chunk8192-final-review.json).


**16/10/2026, 02:10 UTC — Có cần tái tokenize text để so token EAGLE3 không?**

Không dùng text tái tokenize làm bằng chứng token phát sinh. Source image hiện
có native `/generate` nonstreaming trả `output_ids` cả khi tokenizer hoạt động;
đặt `return_prompt_token_ids=true` để giữ input IDs. Nhánh detokenizer chuyển
raw IDs từ scheduler; không cần bật logprob hay skip-tokenizer chỉ để lấy IDs
ở image này. Chưa kiểm bằng HTTP/model thật; không suy sang mọi phiên bản.

Tool local mới so exact request/input IDs, counts, raw output IDs và finish
reason; giữ EOS/tail và phân biệt capture hỏng với khác biệt thật. 30 ca CPU
tổng hợp và6kiểm source đạt, không phải30ca Qwen/accuracy. Chuẩn bị greedy,
neutral penalties, cùng target/tokenizer, kiểm cả biên cap1/3/4/5/200, EOS và
short/long. Audit runtime/env riêng; token khớp trên suite nhỏ chưa chứng minh
lossless toàn miền, sampling tương đương hoặc accuracy BTC. Chưa tải draft,
chạy GPU hay thay thứ tự04→05→06.
[Hướng dẫn](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/TOKEN_REVIEW.md) ·
[Bằng chứng CPU/source](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0205UTC/token-review-validation.json).


**16/10/2026 02:19:28 UTC — HTTP200 hoặc JSON parse được có đủ làm capture token hợp lệ?**

Chưa đủ. Phải giữ exact request/response bytes, kiểm prompt IDs/count và output
IDs/count/cap/finish reason. Body có thể là JSON hợp lệ nhưng HTTP Content-Length
vẫn thiếu; bộ thu mới chặn trường hợp này, giữ raw body, không nhận là capture đủ.
Kết nối đứt giữa chừng thì giữ phần bytes đã đọc, không retry tự động hoặc cắt
EOS/tail để ép khớp. Chỉ tạo capture.json sau khi tất cả case hợp lệ; lỗi giữ
failure.json/journal và raw files trong outdir riêng.

Tool mới đã qua35ca HTTP giả lập trên loopbackCPU, không phải model/Qwen hay
HTTP SGLang thật. Suite/hash tokenizer cần chuẩn bị/xác minh đúng target; tool
không xác nhận deployment, image, weights, simulation hay accuracy. So control tự
lặp trước rồi mới so candidate; thời gian thu là diagnostic, không phải benchmark.
[Hướng dẫn](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/TOKEN_REVIEW.md) · [Bằng chứng](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0215UTC/attempt02/capture-validation.json).


**16/10/2026 02:46 UTC — Vì sao lặp combo còn cần control MNNVL mới?**

Gain23904 chỉ1,4867% so meanhai controlcũ. Nếu thời điểm sau cả combo lẫn
control cùng nhanh lên thì chưa thể gán toàn bộ tăng tốc cho FlashInfer.
Vì vậy wave10 có23973/23975 lặpcombo và23974 controlmới;so từng lượt với
cả23778/23839/23974,mean và driftcontrol,không chỉ lấy điểm cao nhất. Ba lượt
mỗi nhóm vẫn ít;không khẳng định ý nghĩa thống kê haySOTA.

Long23975 chạy sau benchmark vàchỉ ghi JSON sau khi thu đủ. Timeout có thể chỉ
có log/marker;thiếuJSON không có nghĩa pass. Reviewer tái chấm responsegốc,
phân biệt FAILED/DEFERRED/INCOMPLETE/MISSING;giữ benchmark riêng khi diagnostic
không đạt. Inputtoken được encode từprompt,chưa tính chattemplate,không gọi
là chính xác3800. Long12/12 vàsmoke7/8 không thay accuracy99%referenceBTC.
[Hướng dẫn](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/MATCHED_REVIEW.md).


**16/10/2026 05:25 UTC — N54 đã nhanh hơn N52 thì có thể chọn ngay chưa?**

23924 MNNVL N54 đo2634,03goodtokens/s,SLA98,90%,0lỗi/hủyrequest;đối soát
seal/raw/protocol/runtime đạt. Hơn cảhaiMNNVLN52 vàmean1,6004%,nhưngTTFT
lại tăng88,18ms;ITL chỉgiảm0,0307ms. Tăngconcurrency không tự làm mọi latency
giảm vàđiểm cao hơn một lượt chưa chứng minh gainlặp. Vìvậy dùng slot trống
cho24009 lặp cùngN54,giữ12file thực thi vàprotocol;đọc cảcontrol23974mới để
xemdrift,không chỉchọnpeak. Mean phải táchN52/N54;soMNNVLN54 vớiFlashInferN52
khác cảload lẫnbackend nênkhông quy kết riêngkernel. DP N54 23934 vẫnchờ tại snapshot05:25; đã COMPLETED vàfinalaudit10:29, xem câu hỏi bổ sung cuối sổ.

Raw818warmup/1640profiling vàoutput199–201tokens đượcgiữ;goodput vẫnquyước
200tokens/goodrequest nhưbaseline. ChildSlurmsteps vàrequestcancellation phải
đọc riêng;ở đây topjobexit0 vàraw/export đều0requestcancel. Short7/8không thay
accuracy99%referenceBTC. Repeat cóbudget-deferred replacement thì giữmọiattempt
vàreviewtay;không tựchọnattempt đẹp. KhôngN56 haybỏgatecomboN54.
[Review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning/N54_REVIEW.md).


**16/10/2026 05:38 UTC — Có input IDs chuẩn bị sẵn đã chứng minh EAGLE3 đúng chưa?**

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
[Hướng dẫn](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/TOKEN_REVIEW.md) · [Suite](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/eagle3-01/token-suite-v1/suite.json).


**16/10/2026 05:42 UTC — SSH báo Permission denied có còn là mất VPN không?**

Không đồng nhất hai tầng lỗi. Lúc05:30 helper chưa tìm thấy namespace VPN sống;
lúc05:40 ssh-batch đã tới SSH server nhưng bị Permission denied(password).
Kiểm chỉ đọc xác nhận snx-tun UP và route tới NSCC qua tunnel. Chưa có SSH
xác thực dùng được nên PBS220575 vàcredit vẫn chưa biết. BatchMode không hỏi
password; lỗi này không chứng minh password sai. Không suy ai tạo phiên mới,
hoặc cấu hình/lifetime24h đã thành công, chỉ từ interface đang UP. Không đọc
session/credential, không thửloginVPN/DUO/password hay SSH lặp khi không có
chỉ dẫn mới. Giữ1536SU reserve đến khi thật sự thu được queue/accounting.
Bằng chứng: `nscc-pbs/inspection/wake-20261016-0540UTC/`.


### Serverinfo có chứng minh MNNVL đã chạy trên mọi rank không? (16/10 06:18UTC)

Chưa đủ. Job220720 trả serverinfo từ3endpoint: hai prefillTP4/EP1 và decodeTP8/EP8;
decode báo `flashinfer_allreduce_fusion_backend=mnnvl`,FA3,graph1–64. Mỗi endpoint
chỉ trả1`internal_state`;không được đếm thành tổng16rank hoặc nói đủ8decode rank
đãkhởi tạo backend. Hai pairrouterHTTP200 chứng minh requestP/D đi qua được,
chưa chứng minh từngkernel hayaccuracy. Rolelogs lúc06:15 vẫn0byte.
`kv_cache_dtype=auto` là cấu hình tựchọn,chưa đủ nói dtype thực làBF16.
Reportedweightload prefill842,03/842,82s,decode89,74s giúpso startup,
nhưng chưa phânbiệt I/O,mmap,CPU haycache. Lưu evidence khijobcònR bằng
[collector chỉ đọc](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collect-live-runtime.py);
terminal vẫn cần thu artifact vàreview riêng.


**16/10/2026 10:29 UTC — Tăng concurrency có luôn đáng tiếp tục không?**

Không. DP+DeepEP23934 ởN54 đạt2555,42goodtokens/s,SLA98,75%,nhưng chỉhơn
trungbình2lượtDP N52 0,46%,trongkhiTTFT tăng145,20ms. SoMNNVL23924 cùngN54,
goodput thấp2,98%,TTFT cao151,54ms;ITL giảm0,223ms. Mộtlượt/package chưađủ
đểkếtluậnlặplại hoặcquyriêngkernel. ĐãkếtthúcnhánhDPcógiớihạn tạiN54,
giữ4jobxácnhận/combo/control/long đangchờ,khôngmởN56haylặpDPchỉđểlấpslot.
Seal/raw/runtime đạt vàshort7/8knownreverse khôngphảichứngnhậnaccuracyBTC.
[Final review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-08/DP_N54_RESULT.md).

**Lệnh thu archive trả lỗi có nghĩa là toàn bộ dữ liệu mất không?**

Không thể kết luận chỉ từ exitcode. Lầnthu22072006:26 tar báo thưmụcn38/confirm
đangthayđổi,nhưngarchive vẫnđọcđượcđếncuối102member. Lượt10:25giữnguyênbảngốc,
phụchồichọnlọcN32/34/36vàkiểmraw/phases/protocol/count/latency/lengthkhớp.
Đâychỉlàbảnchụpjobđangchạylúc06:26,khôngterminalseal hoặcqualitycuối;
N38chưaxongkhôngđượcdùng. Hash lúckhôiphụcchỉbảovệfilekểtừlúcbăm,
khôngchứngminhtrạngtháiđồngnhấtởthờiđiểmthu. KhiVPNmấtvẫngiữreserve,
khôngsuyjobđãhủyhoặcđãxongtừviệcđãquáwalltime.


**16/10/2026 10:59 UTC — Vì sao chuẩn bị log bên trong PBS task?**

Redirect `pbsdsh ... >role.log 2>&1` ởlauncher chỉ thu output màlauncher nhận;
rolelog rỗng chưa chứng minh worker khôngchạy hoặc chỉra nguyên nhân spool.
Bản[chuẩn bịCPU](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/research-next/pbs-task-logging-01/README.md) mởfile trực tiếp trongcompute task trước module/container
rồiexec command. Unique sidecar tránh ghiđè,giữexitstatus/SIGTERM và khôi phục
umask sau khi mởlog0600. Collector đãthu cảrun;reviewer phải đọc sidecar mới.
12kiểmCPUstub chỉ xácminh logic cục bộ, không xácminh pbsdsh thật/8rank/MNNVL/
BF16KV/accuracy. Chưadeploy. Cùnglogging phải có ởcontrol vàcandidate tương lai;
không sửa job cũ hoặc dùngtestCPU đểbỏ gatequality/runtime/credit.


**16/10/2026 12:13 UTC — Hai lượt combo gần nhau đã đủ mở tải cao hơn chưa?**

Chưa đủ theo gate nghiên cứu hiện tại.23904/23973 đạt2631,09/2632,06goodtokens/s,
chênh0,037%;repeat1 đãsealed/raw/runtimePASS vàhơnmean2controlcũ1,524%.
Sựgầnnhau giúp xácnhận phépđo combo ổnđịnh ởhai lượt,nhưngfreshcontrol23974
chưa cókếtquả nênchưa đối soátdrift;repeat2+long23975 cũngchưa đủ. Gate vẫn cần
cảhairepeat hơnfreshcontrol,meancombo hơnmeancontrol,đủSLA/noerror/no newshort;
planN54 còn đòiSLA95%,ITL19,3ms vàlongPASSED. Đây làquytắc mô tả với sốlượt
hữu hạn,khôngkiểmđịnh ýnghĩathốngkê hoặcaccuracyBTC. Khôngdùngslottrống đểbỏgate.
[Repeat1](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/REPEAT1_RESULT.md).

## Cấu hình tốt nhất có dùng chung hai cluster được không? — 2026-10-16 15:02 UTC

Không mặc định chuyển được hiệu năng: Firmus dùng16H200/Slurm, NSCC dùng16H100/PBS. Cùng modelFP8, topology8prefill+8decode (2×TP4EP1 + TP8EP8), RR/NIXL và protocol4000/200,60/120/30; launcher/container paths và tải tối ưu khác nhau. Dữ liệu hiện tại không đủ để quy nguyên nhân chênh lệch cho một thành phần phần cứng cụ thể.
H200: peak đã review MNNVL N54 job23924=2634.03goodtok/s,SLA98.90%, chưa lặp N54. ComboMNNVL+FlashInfer N52 jobs23904/23973=2631.09/2632.06, tín hiệu lặp tốt hơn nhưng23975+long còn chờ. Freshcontrol23974=2594.03.
H100: MNNVL N42 job220720=2041.97goodtok/s,SLA99.06%, mới một lượt; thiếu runtime8rank proof. Cặp220908control→220909repeat đangQ/H để xác nhận. StandaloneFlashInfer N32/34 thấp hơnbaseline1.79/1.40%; không suy comboFlashInfer+MNNVL trênH100 cũng giảm vì chưa đo combo.
Không xếp2634vs2042 thành gain thuật toán: khácGPU/tải. Chọn riêng config từngcluster, so cùngN vớicontrol cùngcluster, kiểmSLA/error/short/long/runtime và lặp. Accuracy99%BTC chưa xác minh.
Queue kiểm trực tiếp:23975/24009 PENDING(Resources);220908 Q,220909 H dependency. Autopilot giữtắt.

## Cấu hình peak H200 job24190 — 17Oct2026

Peak đãreview2671.109goodtok/s,SLA98.8002%,TTFT847.849ms,ITL16.2875ms;N56singlemeasurement. SGLang,Qwen3-235B-A22B-Instruct-2507-FP8,16H200/2nodes. Node0haiworkerprefill,mỗiworkerTP4/EP1,chunk4096;node1mộtdecodeworkerTP8/EP8. TPchia tensorphép tính giữaGPU;EPchia expertsMoE trênnhómGPU,cùng8GPUdecode chứkhôngcộngthêm8GPU. Routerroundrobinchoprefill,NIXLchuyểnKV,KVBF16. DecodeFlashInferattention+FlashInferAllReduceFusionMNNVL,CUDAGraphdensebatch1..64,memoryfraction0.90,context8192. Benchmarkclosedloop56concurrentrequests,4000input/200output,60warmup/120measure/30grace. WeightsFP8official;KVBF16khácweightprecision. Script/configfrozen: qwen-experiments/runs/24190/submitted/. No99%organiseraccuracyclaim.

## BTC yêu cầu H200 hay H100? — 17Oct2026

Theo Qwen3 AI Task Rules, General Rules→ClusterUsage, được chọn một tronghai nền tảng: Firmus2×HGXH200nodes/16GPU,NDRInfiniBand;hoặcNSCCASPIRE2A+2×HGXH100nodes/16GPU. Khôngbắtbuộcphảitốiưucảhai. PerformanceAssessmentnêu rawthroughputkhôngso trực tiếp giữaGPUgenerations;judgesxemcảmethodology/technicalunderstanding. Cóthểswitchkhiplatformmaintenance;otherclusterworkbổsung. VìvậykhôngkếtluậnH200tốt hơnteamH100chỉtừ2671vs2230. Nguồnlocal:2026-APAC-HPC-AI/1. Qwen3 AI Task Rules.md, GeneralRules.

## So H100/H200 minh bạch — 2026-10-17 09:17 UTC

BestH1002229.83,N50;mean2223.93. Chỉsođịnhlượngkhácplatformkhicùngconfig+cùngN. MatchedcomboN52chok1.1881nhưngchỉmộtanchor;estimateH200N50~2642.24chưakiểmchứng. Khôngnhân1.4băngthôngthànhgoodput. Job24272giữlạikiểmtra,ngưỡng2%quyướctrướckếtquảkhôngphảixácsuất95%. Report/ref/audit:[REPORT.md](../reports/cross-platform-20261017/REPORT.md).
