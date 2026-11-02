# Read-only quality measurement snapshots

Run `python3 monitoring/snapshot.py --out-dir monitoring/snapshots/NEW_UNIQUE_NAME` from the study root. Each invocation performs one scheduler query and one accounting query, reads available client/callback artifacts, and writes an immutable JSON/Markdown snapshot. It does not poll in a loop, start a model, admit/retry/cancel jobs, change budget, authenticate or send messages.

Read the timestamp before using a snapshot. The scheduler row is live at capture time; `workflow/STATE.json` is only the last callback state and can still say `RECORDED_NO_DISPATCH` after root has submitted later wrapped jobs. The admission ledger and scheduler receipts establish whether a job was submitted. A client summary alone does not establish native job completion. A callback VALID event establishes the existing raw-response checks; native COMPLETED 0:0 is checked independently, and a human technical review remains separate.

The point ratio uses only shards completed and callback-validated on both roles. Incomplete or unmatched shards are visible but excluded from this paired progress statistic. This statistic is explicitly partial until all 12032 fixed IDs are covered. The monitor does not rerun response validation and cannot certify official Q1 quality. A failed scheduler query is unknown, never an empty queue.

## JSON Lines handling finding

An exploratory prompt-length check initially used `read_text().splitlines()` and failed on a legal Unicode line-separator character inside a JSON string. Iterating the file by newline-delimited records fixes that diagnostic. The frozen quality client and aggregator already use file-record iteration and were unaffected; no question or response was dropped. The retained `check_prompt_lengths.py` uses file-record iteration and its real-data outputs are kept in `reviews/`.
