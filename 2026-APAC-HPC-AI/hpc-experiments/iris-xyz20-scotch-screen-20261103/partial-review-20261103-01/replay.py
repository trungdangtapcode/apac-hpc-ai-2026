"""Replay an individually hashed partial capture; no completed comparison claim."""
from pathlib import Path
import hashlib,json,re,statistics
P=Path(__file__).resolve().parent;C=P/'collected';metadata=json.loads((P/'collection.json').read_text())
for n,m in metadata['files'].items():
 raw=(C/n).read_bytes();assert len(raw)==m['bytes'] and hashlib.sha256(raw).hexdigest()==m['sha256']
rows=[]
for a in sorted((C/'arms').iterdir()):
 samplepath=a/'telemetry-samples.jsonl'
 if not samplepath.is_file():continue
 data=samplepath.read_bytes();lines=data.splitlines();dropped=0
 if data and not data.endswith(b'\n'):lines=lines[:-1];dropped=1
 samples=[json.loads(x) for x in lines if x.strip()];assert samples
 start,end=samples[0],samples[-1];duration=end['timestamp_monotonic_seconds']-start['timestamp_monotonic_seconds'];assert duration>0
 mem=lambda key:[s['meminfo_kb'][key]/1024**2 for s in samples if key in s.get('meminfo_kb',{})]
 deltas={k:end['vmstat_pages_or_events'][k]-start['vmstat_pages_or_events'][k] for k in start['vmstat_pages_or_events'] if k in end['vmstat_pages_or_events']}
 log=(a/'simpleFoam.log').read_text();times=[float(v) for v in re.findall(r'Wall-clock time elapsed during the current time step = ([\deE.+-]+)',log)]
 metrics={k:{'minimum_GiB':min(mem(k)),'maximum_GiB':max(mem(k))} for k in ['MemAvailable','Active(anon)','Cached'] if mem(k)}
 rows.append({'arm':a.name,'samples':len(samples),'trailing_incomplete_lines_ignored':dropped,'sample_duration_s':duration,'memory':metrics,'counter_deltas':deltas,'counter_rates_per_second':{k:v/duration for k,v in deltas.items()},'observed_intervals':len(times),'partial_interval_mean_s':statistics.mean(times) if times else None,'maximum_interval_s':max(times) if times else None,'native_End_observed':bool(re.search(r'^End\s*$',log,re.M)),'cpu_median_MHz_min':min(s['cpuinfo_frequency']['median_mhz'] for s in samples),'cpu_median_MHz_max':max(s['cpuinfo_frequency']['median_mhz'] for s in samples),'pressure_availability':{k:sum(s['pressure'][k]['available'] for s in samples) for k in ['cpu','io','memory']},'collector_ms_max':max(s['collection_ms'] for s in samples)})
report={'capture_utc':metadata['utc'],'scope':'Partial individual-file snapshot of running 2294671. S1 is internally reviewed by the frozen runtime; X1 incomplete. No independent full output replay, four-arm result, stage cost or speedup claim. Step-to-sample alignment has uncertain native clock origin; no exact spike attribution.','all_retained_hashes_pass':True,'arms':rows}
(P/'ANALYSIS.json').write_text(json.dumps(report,indent=2)+'\n')
for r in rows:print(json.dumps({k:v for k,v in r.items() if k not in ['counter_rates_per_second']}))
