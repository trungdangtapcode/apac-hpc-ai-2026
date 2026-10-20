---
pipeline_tag: text-generation
library_name: transformers
tags:
- speculative-decoding
- draft-model
- eagle3
- qwen
- inference-acceleration
base_model: Qwen/Qwen3-235B-A22B-Instruct-2507
license: cc-by-4.0
model-index:
- name: nebius/EAGLE3-Qwen3-235B-A22B-Instruct-2507
  results:
  - task:
      type: text-generation
    dataset:
      name: MT-Bench
      type: MT-Bench
    metrics:
    - name: Acceptance Length
      type: Acceptance Length
      value: 3.18
  - task:
      type: text-generation
    dataset:
      name: GSM8K
      type: GSM8K
    metrics:
    - name: Acceptance Length
      type: Acceptance Length
      value: 4.65
  - task:
      type: text-generation
    dataset:
      name: HumanEval
      type: HumanEval
    metrics:
    - name: Acceptance Length
      type: Acceptance Length
      value: 4.42
datasets:
- nebius/Qwen3-235B-Instruct-Infinity-Instruct-0625
---

## Model Description

This is an EAGLE-3 draft model for **Qwen3-235B-A22B-Instruct-2507**, trained from scratch using **LK losses** — training objectives that directly target acceptance rate rather than using KL divergence as a proxy.

## Training Details

- **Base model**: Qwen/Qwen3-235B-A22B-Instruct-2507
- **Draft architecture**: EAGLE-3
- **Training data**: [Infinity-Instruct-0625 with Qwen3-235B-A22B-Instruct-2507 generated responses](https://huggingface.co/datasets/nebius/Qwen3-235B-Instruct-Infinity-Instruct-0625)
- **Training objective**: Hybrid LK loss with adaptive λ scheduling (η=3)
- **Training**: 10 epochs from random initialization
- **Draft length**: K = 6 speculative tokens

## Performance

Average acceptance length (τ) measured across MT-bench, HumanEval, and GSM8K with K = 7:

| Configuration | Temperature = 0 | Temperature = 1 |
|---------------|-----------------|-----------------|
| EAGLE-3 + KL | 4.25 | 3.77 |
| **EAGLE-3 + LK (ours)** | **4.32** | **4.08** |


### Comparison with Public Checkpoints

| Model | MT-bench (τ) | HumanEval (τ) | GSM8K (τ) |
|-------|--------------|---------------|-----------|
| zhuyksir/EAGLE3-Qwen3-235B-A22B-Instruct-2507-FP8 | 2.64 | 4.03 | 4.43 |
| RedHatAI/Qwen3-235B-A22B-Instruct-2507-speculator.eagle3 | 2.56 | 3.52 | 3.78 |
| **Ours** | **3.18** | **4.42** | **4.65** |

*Measured at temperature = 1 with K = 7*

> **Note:** Earlier vLLM versions sampled draft tokens greedily regardless of temperature, which underestimated acceptance rates at temperature > 0. Stochastic draft sampling was introduced in **v0.18.0**, and from **v0.21.0** it can be enabled via `speculative_config` using `rejection_sample_method` and `draft_sample_method`. The acceptance metrics reported above were measured under standard rejection sampling and are reproducible with the configuration below.

## Usage with vLLM
```python
from vllm import LLM, SamplingParams

llm = LLM(
    model="Qwen/Qwen3-235B-A22B-Instruct-2507",
    speculative_config={
        "method": "eagle3",
        "model": "nebius/EAGLE3-Qwen3-235B-A22B-Instruct-2507",
        "num_speculative_tokens": 6,
        "rejection_sample_method": "standard",
        "draft_sample_method": "gumbel",
    },
)

sampling_params = SamplingParams(temperature=0.7)
outputs = llm.generate(["Explain speculative decoding in simple terms."], sampling_params)
```


## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

## Citation

```
@misc{samarin2026lklosses,
  title     = {LK Losses: Direct Acceptance Rate Optimization for Speculative Decoding},
  author    = {Alexander Samarin and Sergei Krutikov and Anton Shevtsov and Sergei Skvortsov and Filipp Fisin and Alexander Golubev},
  year      = {2026},
  eprint    = {2602.23881},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG},
  url       = {https://arxiv.org/abs/2602.23881}
}
```