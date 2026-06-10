# Model Card -- <build_id>

## Base
- Model: microsoft/Phi-3-mini-4k-instruct
- Quantisation: bf16

## Adapter
- Method: LoRA
- r: 16, alpha: 32, dropout: 0.05
- Target modules: q_proj, k_proj, v_proj, o_proj

## Training
- Epochs: 2
- Effective batch size: 16
- Learning rate: 2e-4
- Optimizer: AdamW, cosine schedule, warmup 3%
- Hardware: shared GPU (Nvidia A10G)
- Walltime: 24 minutes

## Eval
- Task metric:
- LLM-as-judge win-rate:
- Human review acceptable rate:
- Latency p50 / p95:
- Cost $/1k tokens:

## Ship gate
- Quality: PASS / FAIL
- Cost: PASS / FAIL
- Latency: PASS / FAIL

## Intended use
Local serving via SLMForge. Not for production-grade output without internal-team re-training on real data.

## Limitations
Trained on synthetic + public data; real-data distribution may differ.
