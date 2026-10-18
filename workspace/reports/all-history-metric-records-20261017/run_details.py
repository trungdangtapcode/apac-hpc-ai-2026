"""Render source-linked configuration cards for every record-holding job."""
import json
import re
from pathlib import Path

ROOT = Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
OUT = Path(__file__).resolve().parent
EXPLANATIONS = {
    '24544': 'DeepGEMM prefill, auto decode, chunk 8192, concurrency 58 reaches 2,786.696 good tokens/s. All local checks pass. It is 2.5244% above historical same-load chunk 4096 control 24352; a new N58 control 24589 and independent repeat 24588 are submitted. One historical comparison cannot isolate chunk gain from node/time drift. Official full-set accuracy is unverified.',
    '221315.pbs111': 'HPC-Ops prefill+decode at concurrency 50 reaches 2,371.961 good tokens/s, +2.7277% versus immediately preceding decode-only HPC-Ops control 221314 at 2,308.979. Only the prefill MoE runner changes. Mean TTFT falls 669.245 to 486.401 ms; mean ITL rises 17.831 to 18.221 ms. Full local payload, protocol, runtime and output gates pass. Independent repeat and fresh reversed-order control are submitted; official full-set accuracy is unverified.',

    '24528': 'DeepGEMM prefill, chunk 6144, concurrency 56 reaches 2,737.011 good tokens/s, +0.7798% versus fresh chunk 4096 control 24526. All local payload, protocol, runtime and output checks pass. A single sub-percent gain requires the submitted independent repeat and fresh control; no official accuracy claim.',
    '221276.pbs111': 'HPC-Ops decode at concurrency 52 reaches 2,314.735 good tokens/s, only 0.2384% above the fresh N50 observation 221284 at 2,309.229. Mean TTFT rises from 664.620 to 824.582 ms. Full local gates pass. This is a load comparison, not an isolated runner effect. An independent N52 repeat and fresh N50 control are submitted; official full-set accuracy remains unverified.',

    '24425': 'DeepGEMM prefill with chunk 8192 and concurrency 56 reaches 2,722.281 good tokens/s, about 0.20% above control 24327. Frozen payload, runtime, full protocol, short nonregression and 12 long checks pass. This is a provisional peak; an independent repeat and fresh control have been submitted.',
    '221263.pbs111': 'HPC-Ops decode at concurrency 50 reaches 2,308.308 good tokens/s versus fresh prefetch control 221262 at 2,245.534, a 2.7955% increase. Mean ITL falls from 19.448 to 17.804 ms while mean TTFT rises from 457.898 to 678.908 ms. Joint SLA success is 98.753%. Local payload, runtime and output gates pass. This changes the decode MoE runner only; prefill and prefetch are matched. Independent confirmation is pending; organiser full-set accuracy remains unverified.',

    '24352': 'This DeepGEMM prefill N58 trial passed full protocol, runtime and research output checks. It is the highest observed H200 point at 2,718.080 good tokens/s. It is only about 0.048% above the N56 repeat 24327 while TTFT rises by about 123 ms. The repeated N56 mean is 2,716.315; prefer that replicated operating point rather than claim N58 is a confirmed improvement.',
    '221153.pbs111': 'This prefill weight-prefetch N50 trial passed full protocol, runtime and research quality checks. It reached 2,241.336 good tokens/s, +0.444% versus control 221151, and completed its allocation in 15:45 versus 24:51. Prefill loading times were about 306 seconds versus 921 seconds. Cache, node and order remain confounded, so this is not yet a causal startup or throughput improvement. Reversed-order repeat 221194 and control 221195 are submitted.',

    '221151.pbs111': 'This fresh H100 combo control used the same topology, backends and N50 load as the established frontier. It reached 2,231.429 good tokens/s, only about 0.072% above the earlier 2,229.827 peak. Full protocol, payload, runtime, short output and 12 long checks passed. This is a new observed peak within repeat variation, not a new configuration improvement. Review: nscc-pbs/inspection/manual-20261017-continue-1655/review-221151.json.',
    '24291': 'This trial changed only the prefill MoE runner to DeepGEMM relative to fresh control 24263 at N56. It retained the existing decode configuration. Reviewed good throughput increased by 1.8136%, from 2,667.465 to 2,715.842 good tokens/s; mean TTFT fell by 107.569 ms, while mean ITL rose by 0.189 ms. Prefill kernel profiles motivated the experiment. This is measured evidence for this trial, not proof that DeepGEMM wins at every load or on H100. Independent confirmation is required.',
    '23773': 'This was an independent repeat of the earlier round-robin serving configuration at N53. It used 4,096-token prefill chunks and dense decode CUDA graph sizes 1–64. Round-robin sends prompts across the two prefill workers; CUDA graphs aim to reduce launch overhead. Runtime logs show FA3 attention and auto MoE/all-reduce settings, rather than the later MNNVL plus FlashInfer decode combination. The minimum recorded TTFT is an observation of this complete setup; this report does not isolate how much each optimisation contributed.',
    '22517': 'This early topology trial allocated more GPUs to decode: three independent TP4/EP4 decode workers, with only two TP2 prefill workers. At N16, relatively few requests compete for those workers. That is a plausible explanation for the low ITL, but it is not an isolated causal test. This run did not use the later explicit DeepGEMM, MNNVL, FlashInfer decode or 4,096-token prefill tuning. Its latency record does not make it the best aggregate-throughput configuration.',
    '22416': 'This topology allocated 12 GPUs to three TP4 prefill workers and four GPUs to one TP4/EP4 decode worker. N16 is a light load compared with the current goodput frontier. Every evaluated request in the selected full run met both latency limits. This demonstrates a 100% observed pass rate at that load, not a uniquely superior backend or capacity limit.',
    '22532': 'This tied SLA record used six TP2 prefill workers on 12 GPUs and one TP4/EP4 decode worker on four GPUs, at N16. It is a different topology from job 22416 even though both achieved 100% SLA. The observation does not establish which topology is better at higher concurrency.',
    '221058.pbs111': 'This was an independent H100 repeat of the combo load sweep at N48, N50 and N52. It combined round-robin prefill, 4,096-token prefill chunks, dense decode CUDA graphs, MNNVL all-reduce and FlashInfer decode attention. N50 had the highest goodput in that sweep; increasing to N52 did not improve it. The preceding independent N50 run 221052 produced 2,218.032 good tokens/s; the two-run mean is 2,223.930. This validates an observed operating point, not an isolated speedup attributable to every flag.',
    '220720.pbs111': 'This first H100 MNNVL trial added the decode all-reduce fusion backend mnnvl to the earlier round-robin/chunk4096/dense-graph baseline. Its N32 export contains the historical TTFT minimum. However, role logs were empty, so runtime activation was not fully proved for this allocation. Do not attribute the 303.288 ms TTFT causally to MNNVL or present it as a fully validated deployment. Later jobs repeated the setting with improved logging.',
    '220909.pbs111': 'This was the MNNVL repeat with compute-task logging, paired with fresh control 220908. The reviewed goodput improvement was about 7.52% at N32 and 8.24% at N34 versus that control. Runtime proof was recovered from task-side logs. The job also holds the observed H100 mean ITL record at N32. The matched comparison supports a throughput benefit in those tests; it does not separately establish that MNNVL caused the minimum ITL.',
    '220562.pbs111': 'This early full H100 baseline used the transferred round-robin/chunk4096/dense-graph configuration at N32. Longer readiness allowances addressed slow checkpoint loading; they are startup reliability settings, not inference throughput optimisations. The 100% observed SLA rate at N32 is a low-load baseline result. Old metadata saying a benchmark was not yet run is preparation history, not the terminal result.',
    '220575.pbs111': 'This H100 baseline established full-protocol performance before MNNVL tuning, including N32 and N34 observations with 100% joint SLA. It retains the earlier round-robin, chunk4096 and dense-graph setup. Its role here is a baseline and an SLA tie, not the final throughput winner.',
    '220721.pbs111': 'This standalone H100 attention trial selected FlashInfer for decode without the later explicit MNNVL combination. It achieved 100% SLA at the listed lower loads, but historical matched throughput was about 1–2% below the baseline. A 100% pass-rate tie therefore does not imply that this optimisation improved goodput.',
    '220722.pbs111': 'This H100 trial added checkpoint weight prefetch to reduce loading time. Prefetch is a startup and allocation-cost hypothesis, not inherently a faster per-token inference method. The historical short allocation is confounded by load, node and cache differences, and old role logs were incomplete; no causal loading speedup is established. It ties on SLA at the listed lower loads.',
    '220908.pbs111': 'This fresh H100 control used the same task-side logging as MNNVL candidate 220909. It retained round-robin prefill, chunk4096 and dense decode graphs without explicitly selecting MNNVL. It supplies a fairer same-load reference and ties at 100% SLA at N32 and N34. Logging is an evidence fix, not a model optimisation.',
}


def link(label, path):
    return '[{}]({})'.format(label, path)


def render(records):
    grouped = {}
    for platform, metrics in records.items():
        for metric, record in metrics.items():
            for row in record['ties']:
                entry = grouped.setdefault((platform, row['job']), {})
                key = (row['phase'], row['concurrency'])
                entry.setdefault(key, dict(row=row, metrics=[]))['metrics'].append(metric)
    details = []
    navigation = ['Jump to a job: ' + ' · '.join('[{} {}](#{}-job-{})'.format(platform, job, platform.lower(), job.lower().replace('.', '')) for platform, job in grouped), '']
    lines = ['## Configuration and optimisation history of each record job', '',
             'The cards include every tied SLA job, not only the example shown in the summary table. Configuration files describe intended settings; runtime fields below are separately extracted from saved role logs when available. An `auto` setting is a policy, not proof of one fixed kernel backend. Missing fields and old preparation metadata must not be silently treated as verified runtime.', '',
             'All listed layouts allocate 16 GPUs across two nodes and use SGLang to serve Qwen3-235B-A22B-Instruct-2507-FP8. The scored client is AIPerf with the protocol above. FP8 here describes the supplied model checkpoint, not a new quantisation performed by these trials. Common intended settings include context length 8,192 and static memory fraction 0.9; `kv_dtype=auto` is the requested KV setting, and BF16 runtime claims require log/review evidence. A GPU memory fraction is not model accuracy or GPU utilisation.', '',
             '**What the optimisations do:** chunked prefill divides prompt processing into bounded pieces; round-robin distributes prompts across prefill workers; CUDA graphs reduce repeated GPU launch overhead for supported shapes; DeepGEMM provides a selected MoE computation backend; FlashInfer supplies decode attention kernels; MNNVL selects an all-reduce fusion backend; NIXL transfers KV data between separate prefill and decode workers. The heterogeneous-TP descriptor patch repairs transfer compatibility and is not a demonstrated standalone throughput optimisation. Weight prefetch targets checkpoint loading before serving.', '']
    lines.extend(navigation)
    labels = {'good_output_tokens_s': 'goodput', 'ttft_avg_ms': 'mean TTFT', 'itl_avg_ms': 'mean ITL', 'good_request_fraction': 'joint SLA'}
    for (platform, job), observations in grouped.items():
        row = next(iter(observations.values()))['row']
        export = Path(row['export'])
        run = next(p for p in export.parents if p.name == job)
        config = run/'config.json'
        cfg = json.loads(config.read_text())
        submitted = run/'submitted'
        worker = submitted/'worker.sh'
        runtime = {}
        for role in ['prefill-0', 'decode-0']:
            log = run/(role+'.log')
            if log.exists():
                match = re.search(r'server_args=ServerArgs\((.*)', log.read_text())
                if match:
                    runtime[role] = {}
                    for key in ['tp_size', 'ep_size', 'attention_backend', 'decode_attention_backend', 'moe_runner_backend', 'chunked_prefill_size', 'kv_cache_dtype', 'flashinfer_allreduce_fusion_backend']:
                        value = re.search(r'\b'+key+r'=([^,)]*)', match[1])
                        if value:
                            runtime[role][key] = value[1]
        prefill_flags = cfg.get('prefill_extra_flags', [])
        decode_flags = cfg.get('decode_extra_flags', [])
        if worker.exists():
            # Submitted scripts can contain inherited flags missing from config metadata.
            extras = re.findall(r'^\s*extra=\(([^\n]*)\)', worker.read_text(), re.M)
            extras = [x for x in extras if x.strip()]
        else:
            extras = []
        lines += ['### {} job {}'.format(platform, job), '',
                  '**Record held:** '+ '; '.join('{} at N{}'.format(', '.join(labels[m] for m in v['metrics']), k[1]) for k,v in observations.items())+'.', '',
                  '**Layout:** {} GPUs for prefill: {} worker(s), each TP{}/EP{}. {} GPUs for decode: {} worker(s), each TP{}/EP{}.'.format(cfg['prefill_gpus'], cfg['prefill_workers'], cfg['prefill_tp'], cfg.get('prefill_ep', 1), cfg['decode_gpus'], cfg['decode_workers'], cfg['decode_tp'], cfg['decode_ep']), '',
                  '**Experiment:** `{}`. Scheduler: {}.'.format(cfg.get('experiment', cfg['id']), 'Slurm' if platform == 'H200' else 'PBS'), '',
                  '| Recorded point | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) |',
                  '|---|---:|---:|---:|---:|']
        for (phase,n), obs in observations.items():
            p = obs['row']
            lines.append('| N{} ({}) | {:.3f} | {:.3f} | {:.3f} | {:.4f} |'.format(n, phase, p['good_output_tokens_s'], p['ttft_avg_ms'], p['itl_avg_ms'], 100*p['good_request_fraction']))
        lines += ['', '**Configured additions:**', '',
                  '- Prefill: '+ ('`'+' '.join(prefill_flags)+'`' if prefill_flags else 'No additional prefill flags recorded in config.json; inspect runtime below.')+'.',
                  '- Decode: '+ ('`'+' '.join(decode_flags)+'`' if decode_flags else 'No additional decode flags recorded in config.json; inspect runtime below.')+'.',
                  '- Router: '+ ('`'+' '.join(cfg.get('router_extra_flags', []))+'`' if cfg.get('router_extra_flags') else 'No additional router flags recorded in config.json.')+'.',
                  '- KV transfer: `{}`; descriptor patch: `{}`.'.format(cfg.get('transfer', 'unspecified'), cfg.get('transport_patch') or 'not selected'), '']
        if extras:
            lines += ['**Submitted worker additions:** these preserve inherited launch settings that may be absent from the config metadata.', '']
            for extra in extras:
                lines += ['```text', extra, '```', '']
        if runtime:
            lines += ['**Available runtime fields** (one representative log per role; this extraction is not an all-rank audit):', '', '| Setting | Prefill worker 0 | Decode worker 0 |', '|---|---|---|']
            keys = sorted(set().union(*(r.keys() for r in runtime.values())))
            for key in keys:
                lines.append('| `{}` | {} | {} |'.format(key, runtime.get('prefill-0',{}).get(key,'not available'), runtime.get('decode-0',{}).get(key,'not available')))
            lines.append('')
        else:
            lines += ['**Runtime extraction:** representative role logs do not contain parseable ServerArgs here. Review task-side logs and the linked review before treating requested flags as verified activation.', '']
        lines += ['**How this result was obtained and what it proves:** '+EXPLANATIONS.get(job, 'This job ties the listed observed record. Its settings and metrics are reported here, but no isolated causal improvement is established by the record scan.'), '', '**Evidence:** '+link('saved configuration', config)+'; '+link('run artifacts',run)+'; '+link('AIPerf export for the first listed point',export)+(' ; '+link('submitted worker script',worker) if worker.exists() else '')+'.', '']
        details.append(dict(platform=platform, job=job, config_path=str(config), configuration=cfg, representative_runtime=runtime, submitted_worker_additions=extras, records=[v for v in observations.values()], interpretation=EXPLANATIONS.get(job)))
    lines += ['### Matched comparisons and review sources', '', '- '+link('DeepGEMM 24291 runtime, quality and control comparison', ROOT/'serving-tuning-10/prefill-pilot-reviews/24291-v2.json'), '- '+link('H100 221058 sealed sweep review', ROOT/'nscc-pbs/inspection/manual-20261017-0858/review-221058.pbs111.json'), '- '+link('H100 220909 versus 220908 matched review and runtime proof', ROOT/'nscc-pbs/inspection/manual-20261017/pair-review.json'), '', 'Some inherited metadata names earlier controls or an old concurrency. The per-point AIPerf export and terminal reviews determine the measured load and comparison; an old config comment is not a new measurement.']
    (OUT/'job-details.json').write_text(json.dumps(details,indent=2)+'\n')
    return '\n'.join(lines)
