"""Summarize retained node-wide counters; do not attribute them to solver ranks."""
from pathlib import Path
import json,statistics
E=Path(__file__).resolve().parent
rows=[]
for p in sorted((E/'collected/runs/2294997/arms').iterdir()):
 xs=[json.loads(l) for l in (p/'telemetry-samples.jsonl').read_text().splitlines()]
 a,b=xs[0],xs[-1];dt=b['timestamp_monotonic_seconds']-a['timestamp_monotonic_seconds'];assert dt>0
 freq=[x['cpuinfo_frequency']['median_mhz'] for x in xs]
 counters=['numa_pages_migrated','numa_hint_faults','numa_miss','pgmajfault','pgscan_direct','pswpin','pswpout']
 rows.append({'arm':p.name,'sample_count':len(xs),'sample_span_seconds':dt,'median_of_sample_CPU_frequency_medians_MHz':statistics.median(freq),'minimum_MemAvailable_GiB':min(x['meminfo_kb']['MemAvailable'] for x in xs)/1048576,'node_counter_delta_per_second':{k:(b['vmstat_pages_or_events'][k]-a['vmstat_pages_or_events'][k])/dt for k in counters}})
out={'job_id':'2294997','scope':'Whole-node procfs counter deltas over each sampled solver window, not per-process attribution','arms':rows,'limits':['numa_miss is an allocation-placement counter, not a remote-memory-access rate.','CPU MHz is a sampled median across CPUs, not task-weighted frequency or effective CPU cycles.','pswpin/pswpout deltas are observed zero here; unavailable PSI is not zero.','Counters include node activity and cannot establish the cause of timing drift.']}
(E/'TELEMETRY-INSPECTION.json').write_text(json.dumps(out,indent=2)+'\n')
(E/'TELEMETRY-INSPECTION.md').write_text('''# Retained node telemetry: drift remains unresolved

The six-arm result has large timing drift. Inspecting retained five-second whole-node samples finds median-of-sample CPU-frequency medians near 3,300 MHz in all arms, while sampled minimum available node memory is 37.60–42.42 GiB. These frequency summaries do not prove equal effective solver clocks.

D1, O1 and T2 have observed nonzero direct-reclaim scan rates (about 137.79, 92.74 and 37.70 pages/s); D2, O2 and T1 show zero delta in that counter over their sampled windows. D1 versus D2 also differs in node-wide NUMA page migrations (561.03 versus 0.87 pages/s). Swap input/output deltas are zero in every retained window. PSI data were unavailable. These observations motivate checking allocation placement and memory pressure if a later distinct diagnostic is justified; they do not establish an I/O or NUMA bottleneck. In particular, the slow T1 arm has zero direct-reclaim scan delta, and T2 has the largest migration rate while improving over T1, so no single counter explains all timings.

NUMA miss counts describe allocation placement, not remote memory reads. Sampling covers whole-node activity, not individual solver ranks. The existing next native 40/48 measurement should proceed independently of optional profiling and retain every interval, rather than deleting early slow steps. No scoring rule or frozen payload is changed by this retrospective analysis. Exact deltas, samples and units are in TELEMETRY-INSPECTION.json; inspect_telemetry.py reproduces them.
''')
print(json.dumps({'arms':len(rows),'scope':out['scope']}))
