# Preserve completed-job query errors without hiding accounting

On 3 November 2026 at 01:44 Vietnam, a structured read-only query confirmed job 2294670 COMPLETED 0:0 via sacct, while squeue returned status 1 and `Invalid job id specified`. The earlier check_output-based status body raised before the bridge could emit a JSON frame, producing a misleading framed-reply timeout. It was not evidence of VPN or Iris authentication failure.

The new tools/iris_job_status.py captures separate return codes, stdout, stderr and bounded command timeouts for both live squeue and retained accounting, and returns a framed reply even when a command fails. It does not authenticate VPN, mutate scheduler state, retry, cancel or submit jobs. The exact observed command outputs are retained in latest-owner-status.json; no synthetic result is presented as a live query.
