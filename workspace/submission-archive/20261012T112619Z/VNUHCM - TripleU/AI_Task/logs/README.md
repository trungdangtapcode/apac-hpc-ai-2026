# Evidence included

`RESULTS.md`, `results.json` and `results.csv` point to original canonical AIPerf exports. `runs/<job>/` preserves completed/failed worker logs, Slurm output, canonical metrics, per-request JSONL, client logs, configuration and provenance. `snapshots/` is a frozen view of the queue and recovery registry at packaging time. Its pending states do not update automatically after packaging.

Per-request JSONL contains warmup and profiling records; filter `metadata.benchmark_phase == "profiling"` for scored-window request statistics. Read canonical `profile_export_aiperf.json` for AIPerf goodput; multiply by 200. Short sweep measurements are labelled separately from long confirmation runs. Per-request SLA is not inferred from aggregate TTFT/ITL averages.

The selected input dataset is included once in `dataset/`, unmodified. Repeated `inputs.json`, duplicate phase exports, writable container homes, checkpoints and container binaries are omitted from the archive. Originals remain in the workspace. `artifact-manifest.json` files copied from source enumerate those original run trees and may refer to files omitted here; root `FILE_MANIFEST.json` and `SHA256SUMS` describe the delivered package.

Quality benchmark results and full generated response texts are not claimed to be archived. No official organiser score has been received.
