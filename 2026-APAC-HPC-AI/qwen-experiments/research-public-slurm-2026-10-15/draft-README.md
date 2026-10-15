---
license: mit
datasets:
- mlabonne/open-perfectblend
---



![meituan_team](https://cdn-uploads.huggingface.co/production/uploads/63993d721fad4d6eb265d999/vCqSrLcr-6Z1XRBnBR0sB.png)

# EAGLE3 For Qwen/Qwen3-235B-A22B-Instruct-2507


## About

**SpecBundle** is an open-source initiative, jointly driven by the community and industry, to democratize speculative decoding by providing high-performance speculative decoding draft weights for mainstream open-source models.

This checkpoint was trained by the [**Meituan**](https://huggingface.co/meituan) Team and released as the **phase 1 of SpecBundle release**. We regenerated the responses in the [mlabonne/open-perfectblend](https://huggingface.co/datasets/mlabonne/open-perfectblend) and trained the model on 1.4M data samples for 2 epochs. This checkpoint was trained using the [**SpecForge**](https://github.com/sgl-project/SpecForge) framework.



## Usage

You can use this checkpoint with the command below.

```bash
export SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1

python3 -m sglang.launch_server \
    --model Qwen/Qwen3-235B-A22B-Instruct-2507 \
    --speculative-algorithm EAGLE3 \
    --speculative-draft-model-path lmsys/SGLang-EAGLE3-Qwen3-235B-A22B-Instruct-2507-perfect-blend-regenerated \
    --speculative-num-steps 3 \
    --speculative-eagle-topk 1 \
    --speculative-num-draft-tokens 4 \
    --tp 8
```

# Performance

This checkpoint exhibits superior performance on various benchmarks.

<table>
  <tr>
    <th>Throughput</th>
    <th>Acceptance Length</th>
  </tr>
  <tr>
    <td><img src="https://cdn-uploads.huggingface.co/production/uploads/63993d721fad4d6eb265d999/VT7KzWJDuS62ETMi5eNba.png" /></td>
    <td><img src="https://cdn-uploads.huggingface.co/production/uploads/63993d721fad4d6eb265d999/x4Rbh7sqBy9iBM-Kyrslw.png" /></td>
  </tr>
</table>


You can reproduce the performance with the command below:

```bash
# clone specforge
git clone https://github.com/sgl-project/SpecForge.git
cd SpecForge/benchmarks

# run benchmarks
python bench_eagle3.py \
        --model Qwen/Qwen3-235B-A22B-Instruct-2507 \
        --speculative-algorithm EAGLE3 \
        --speculative-draft-model-path lmsys/SGLang-EAGLE3-Qwen3-235B-A22B-Instruct-2507-perfect-blend-regenerated \
        --port 30003 \
        --config-list 1,3,1,4 1,5,1,6 1,5,3,6 1,7,1,8 1,7,4,8 \
        --benchmark-list gsm8k math500 mtbench humaneval livecodebench financeqa gpqa  \
        --dtype bfloat16 \
        --tp 8 \
        --name qwen3-235b-a22b-spec-bundle
```

## Acknowledgement

We sincerely appreciate the collective efforts from both the developers in the open-source community and our industrial partners, especially Ant Group AQ Team, Meituan, Nex-AGI (Qiji Zhifeng), EigenAI for their invaluable contributions to the release of SpecBundle Phase 1.
