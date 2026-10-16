## Codex autopilot đã tắt — 2026-10-16 13:42:29 UTC

Theo yêu cầu người dùng: dừng tự gọi Codex để giảm tiêu hao quota.
Đã gỡ cron `ap42-qwen-autopilot`, tạo `PAUSED`, xóa trigger `FORCE` nếu có.
Không tự bật lại, tạo lịch thay thế hoặc gọi Codex nền nếu chưa được yêu cầu rõ ràng.
Giữ nguyên VPN, job GPU đã gửi và watcher Slurm không gọi AI.
Các hướng dẫn tự chạy bên dưới chỉ là lịch sử; không phải quyền tiếp tục autopilot.

# Qwen research autopilot on the VPS

Local cron checks every5minutes and invokes an authenticated `codex exec` run
when queue/transfer state changes, or at least once every6hours. Each model run
is limited to20minutes and protected by a lock. No root required.

Read [LATEST.md](LATEST.md) for progress and [HISTORY.md](HISTORY.md) for history.
This does not send messages into the original chat. It uses Codex account quota,
separately from NSCC GPU SU. The VPS, cron daemon and Codex login must remain
available. Runs stop after2026-11-15. Exact scope: [POLICY.md](POLICY.md).

Pause: `touch /home/apacsc42/workspace/research-autopilot/PAUSED`.
Resume: remove that file. Request next check: create `FORCE` in this directory.
Inspect schedule: `crontab -l`. Logs: `wake.log`, `cron.log`, `runs/`.

Official guidance: [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode),
[Scheduled tasks](https://learn.chatgpt.com/docs/automations).
This is a custom VPS cron workflow, not a task registered in the Scheduled UI.

Usage fix16Oct: [USAGE_AUDIT.md](USAGE_AUDIT.md). Triggersignorependingreasons/elapsed; compactcurrentcontext,historyarchived;PythonbackoffworksundercronPATH.
