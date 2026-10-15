---
library_name: transformers
license: mit
---
# sglang-EAGLE3-Qwen3-235B-A22B

## Model Introduction
The Eagle3 draft model was trained using the [SpecForge](https://github.com/sgl-project/SpecForge) framework for the Qwen3-235B-A22B model, leveraging a combination of UltraChat and ShareGPT datasets.


## Benchmark Results
- gsm8k (200 questions)

Output throughput: 224.168 token/s

<b>Accept length: 3.538</b>

- mtbench (80 questions)

Output throughput: 241.5 token/s

<b>Accept length: 3.019</b>


## Usage
You can use this Eagle3 draft model in [SGLang](https://github.com/sgl-project/sglang) with the following command:

```bash
python3 -m sglang.launch_server \
    --model <Qwen3-235B-A22B> \
    --speculative-algorithm EAGLE3 \
    --speculative-draft-model-path <EAGLE3-Qwen3-235B-A22B> \
    --speculative-num-steps 5 \
    --speculative-eagle-topk 8 \
    --speculative-num-draft-tokens 32 \
    --mem-fraction-static 0.75 \
    --tp 8 \
    --enable-ep-moe \
    --context-length 8192 \
    --trust-remote-code \
    --host 0.0.0.0 \
    --port 30000 \
    --dtype bfloat16
```
