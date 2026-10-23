# Why a PBS node marked free may not fit the four-node job

The read-only snapshot at **23 October 18:54:23 UTC** reports 758 standard 128-CPU nodes in the `ex` pool. It classifies 182 as `free`, but **zero** of those nodes have all 128 CPUs unassigned. The largest advertised free CPU count among these partially occupied nodes is 124, on two nodes. This supports the observed shortage for a job requesting four whole 128-core chunks with exclusive placement. It does not establish an exact dispatch time or a scheduler fault.

`state=free` must not be read as “the server is empty.” On this observed system it includes nodes with partial CPU allocations. The snapshot retains the full histogram of unassigned CPU counts. Only one pool node has zero assigned CPUs, and no zero-assigned node is marked free. The aggregate counts do not establish which non-free state that node has. Memory, reservations, sharing policy and scheduling priority are not fully evaluated by this small report, so even four apparently idle nodes would not guarantee immediate eligibility.

The existing jobs remain 25940700 Q/q5 (node_pool), 25943865 H/qdev and 25947168 H/q5 under their recorded prerequisites. No qsub, cancellation, hold, qalter, budget or payload edit was made. Direct submission to the route-only q5 queue is not a remedy. The current native leader uses 128 ranks per node; reducing rank density to fit fragments would be a different experiment with known older losing observations, not an equivalent confirmation.

The inspector reads scheduler metadata and stores only aggregate counts plus whitelisted metadata for our three jobs. No other user's job IDs or environment/authentication data are retained. GPU labels in the count keys refer to the advertised scheduler CPU pool, not a measured physical GPU inventory. Hardware utilization, memory traffic and node health were not measured. Sources and exact UTC are in [the JSON snapshot](snapshot-20261023T1854.json).

Run from the experiment directory with a fresh destination:

```sh
python3 inspect_scheduler.py --output snapshot-NEW.json
```

The helper is read-only and refuses to replace an earlier snapshot. A later queue decision requires a fresh snapshot; this is a dated explanation, not live cluster state.

Interpretation correction: an earlier prose draft equated the single zero-assigned node with the single down node. Those two aggregate counts do not prove that identity; the raw snapshot is unchanged.
