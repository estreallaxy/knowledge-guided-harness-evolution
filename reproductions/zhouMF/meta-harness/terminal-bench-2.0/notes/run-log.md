# 运行记录（周梦凡 / zhouMF）

`jobs/`、`runs/`、`logs/` 都在 `.gitignore` 里，原始产物不入库，所以每个 job 的关键指标
都在这里留档。字段与 `configs/meta-harness.yaml` 的 `records.fields` 对齐。

生成方式（job 结束后执行，可多次追加）：

```bash
cd /data1/users/zhouMF/knowledge-guided-harness-evolution/reproductions/zhouMF/meta-harness/terminal-bench-2.0
python3 code-adaptation/scripts/summarize_run.py \
  ../code/reference_examples/terminal_bench_2/jobs/<job_dir> \
  --append-to notes/run-log.md
```

公共条件（所有记录共用）：environment=`docker`、执行模型 `deepseek/deepseek-v4-flash`、
H0=`agents.baseline_kira:AgentHarness`、任务来自 `-p /data1/users/zhouMF/benchmarks/tb2-split-v1/<split>`、
`--ak temperature=0.7`。与参考实现的偏差见 `notes/adaptations.md`。

## R1 oracle 链路验证（不调模型）

目的：先用 harbor 内置 `oracle` agent 验证 docker 后端、任务镜像、`-p`+`-i` 过滤与判分器，
把"与模型无关"的部分先排除掉。


### 2026-10-10__08-59-09

- 实验条件：agent=`oracle`，model=`None`，environment=`docker`，n_concurrent=1，trials/任务=1，任务数=1
- 任务来源：`/data1/users/zhouMF/benchmarks/tb2-split-v1/train/bn-fit-modify`（source=train）
- 时间：2026-10-10T08:59:09.924157 → 2026-10-10T09:00:22.490916
- 汇总：trials=1，完成=1，异常=0，重试=0

| # | task | trial | reward | in_tok | out_tok | cost_usd | wall_s | exception |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | bn-fit-modify | bn-fit-modify__VarKzZ6 | 1.0 | None | None | — | 72.5 | 无 |

- 平均 reward：1.0000（1/1 满分）

## R2 P2 执行模型 smoke

目的：确认 `deepseek-v4-flash` 能经 litellm 驱动 H0，并接受 `temperature=0.7` 与原生 tool calling。


### 2026-10-10__09-05-35

- 实验条件：agent=`agents.baseline_kira:AgentHarness`，model=`deepseek/deepseek-v4-flash`，environment=`docker`，n_concurrent=1，trials/任务=1，任务数=1
- 任务来源：`/data1/users/zhouMF/benchmarks/tb2-split-v1/train/bn-fit-modify`（source=train）
- 时间：2026-10-10T09:05:35.522934 → 2026-10-10T09:10:58.403393
- 汇总：trials=1，完成=1，异常=0，重试=0
- 合计用量：input_tokens=499575，cache_tokens=0，output_tokens=46507，cost_usd=0.070168

| # | task | trial | reward | in_tok | out_tok | cost_usd | wall_s | exception |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | bn-fit-modify | bn-fit-modify__XeMwwWC | 1.0 | 499575 | 46507 | 0.070168 | 320.2 | 无 |

- 平均 reward：1.0000（1/1 满分）

## R3 P3 H0 基线（train 全集）

目的：H0 在同条件下跑 train 30 题的基线分数、token、费用与时延；dev/test 不参与。

启动命令（2026-10-10 09:16，后台运行，日志 `runs/h0-baseline.log`）：

```bash
HARBOR_TASK_PATH=/data1/users/zhouMF/benchmarks/tb2-split-v1/train \
  bash code-adaptation/scripts/run_local_docker.sh \
  agents.baseline_kira:AgentHarness full 2 4 --job-name h0-baseline
```

状态：**进行中**，job 目录 `../code/reference_examples/terminal_bench_2/jobs/h0-baseline/`。
完成后用上面的 `summarize_run.py` 命令把逐题表追加到本节。

### R3 逐题结果（job 结束后自动追加）


### h0-baseline

- 实验条件：agent=`agents.baseline_kira:AgentHarness`，model=`deepseek/deepseek-v4-flash`，environment=`docker`，n_concurrent=未记录，trials/任务=2，任务数=30
- 任务来源：`/data1/users/zhouMF/benchmarks/tb2-split-v1/train/bn-fit-modify`（source=train）
- 时间：2026-10-10T09:11:18.693205 → 2026-10-10T09:54:22.620810
- 汇总：trials=60，完成=60，异常=56，重试=0
- 合计用量：input_tokens=55317166，cache_tokens=0，output_tokens=725524，cost_usd=1.379713

| # | task | trial | reward | in_tok | out_tok | cost_usd | wall_s | exception |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | bn-fit-modify | bn-fit-modify__CVqE72j | — | 0 | 0 | — | 31.5 | error |
| 2 | bn-fit-modify | bn-fit-modify__TmHUugR | 1.0 | 234674 | 63197 | 0.084071 | 395.2 | 无 |
| 3 | caffe-cifar-10 | caffe-cifar-10__RwG8aAx | — | 0 | 0 | — | 33.0 | error |
| 4 | caffe-cifar-10 | caffe-cifar-10__VXpsXFL | — | 501685 | 12263 | 0.031402 | 2451.0 | error |
| 5 | compile-compcert | compile-compcert__KoP74xa | — | 0 | 0 | — | 37.7 | error |
| 6 | compile-compcert | compile-compcert__bdTsGbU | 1.0 | 35820920 | 95057 | 0.379908 | 1762.9 | 无 |
| 7 | custom-memory-heap-crash | custom-memory-heap-crash__NxTbTqD | 1.0 | 880285 | 36006 | 0.061368 | 318.0 | 无 |
| 8 | custom-memory-heap-crash | custom-memory-heap-crash__yDYfCHm | — | 0 | 0 | — | 17.1 | error |
| 9 | dna-assembly | dna-assembly__BjYBRAX | — | 3159816 | 338066 | 0.457343 | 1806.1 | error |
| 10 | dna-assembly | dna-assembly__upbSgbs | — | 0 | 0 | — | 40.5 | error |
| 11 | extract-moves-from-video | extract-moves-from-video__RKXNBcg | — | 0 | 0 | — | 37.9 | error |
| 12 | extract-moves-from-video | extract-moves-from-video__Uii9GU7 | — | 13260440 | 138108 | 0.283756 | 1700.0 | error |
| 13 | fix-code-vulnerability | fix-code-vulnerability__qr4Cs8V | 1.0 | 215479 | 11094 | 0.023127 | 98.9 | 无 |
| 14 | fix-code-vulnerability | fix-code-vulnerability__vJjMdCZ | — | 0 | 0 | — | 17.4 | error |
| 15 | fix-ocaml-gc | fix-ocaml-gc__6Snnp3B | — | 1241309 | 25424 | 0.051042 | 232.8 | error |
| 16 | fix-ocaml-gc | fix-ocaml-gc__8QzX2DS | — | 0 | 0 | — | 32.8 | error |
| 17 | gcode-to-text | gcode-to-text__Yvq7HfX | — | 1243 | 265 | 0.000390 | 28.8 | error |
| 18 | gcode-to-text | gcode-to-text__n7eL4ez | — | 0 | 0 | — | 25.7 | error |
| 19 | git-multibranch | git-multibranch__fV5Y2E9 | — | 0 | 0 | — | 31.1 | error |
| 20 | git-multibranch | git-multibranch__id4HW43 | — | 0 | 0 | — | 32.8 | error |
| 21 | headless-terminal | headless-terminal__5LUZgwU | — | 0 | 0 | — | 25.0 | error |
| 22 | headless-terminal | headless-terminal__98PRLBq | — | 0 | 0 | — | 24.2 | error |
| 23 | hf-model-inference | hf-model-inference__EUD25fh | — | 0 | 0 | — | 24.8 | error |
| 24 | hf-model-inference | hf-model-inference__hFi2ANE | — | 0 | 0 | — | 24.7 | error |
| 25 | llm-inference-batching-scheduler | llm-inference-batching-scheduler__uvEShTH | — | 0 | 0 | — | 25.7 | error |
| 26 | llm-inference-batching-scheduler | llm-inference-batching-scheduler__vA6EZeN | — | 0 | 0 | — | 25.2 | error |
| 27 | mailman | mailman__JjNaWSq | — | 0 | 0 | — | 35.1 | error |
| 28 | mailman | mailman__fwwD3AR | — | 0 | 0 | — | 38.6 | error |
| 29 | make-mips-interpreter | make-mips-interpreter__8FzxTXn | — | 0 | 0 | — | 21.7 | error |
| 30 | make-mips-interpreter | make-mips-interpreter__rKzh9LG | — | 0 | 0 | — | 22.8 | error |
| 31 | mcmc-sampling-stan | mcmc-sampling-stan__EaYX9hK | — | 0 | 0 | — | 80.1 | error |
| 32 | mcmc-sampling-stan | mcmc-sampling-stan__Ez8FqiU | — | 0 | 0 | — | 32.6 | error |
| 33 | mteb-retrieve | mteb-retrieve__WoMXDTy | — | 0 | 0 | — | 18.4 | error |
| 34 | mteb-retrieve | mteb-retrieve__r7hc4Ep | — | 0 | 0 | — | 17.7 | error |
| 35 | polyglot-c-py | polyglot-c-py__48KD8ep | — | 1315 | 6044 | 0.007309 | 68.8 | error |
| 36 | polyglot-c-py | polyglot-c-py__oMsgzf7 | — | 0 | 0 | — | 33.7 | error |
| 37 | portfolio-optimization | portfolio-optimization__MC6w6VN | — | 0 | 0 | — | 24.8 | error |
| 38 | portfolio-optimization | portfolio-optimization__tvBDyq5 | — | 0 | 0 | — | 25.0 | error |
| 39 | pypi-server | pypi-server__G4gBZFn | — | 0 | 0 | — | 24.9 | error |
| 40 | pypi-server | pypi-server__s7mHbTK | — | 0 | 0 | — | 26.5 | error |
| 41 | pytorch-model-cli | pytorch-model-cli__dLTpsdg | — | 0 | 0 | — | 24.9 | error |
| 42 | pytorch-model-cli | pytorch-model-cli__p6mPREA | — | 0 | 0 | — | 26.1 | error |
| 43 | qemu-alpine-ssh | qemu-alpine-ssh__CoySiAM | — | 0 | 0 | — | 17.6 | error |
| 44 | qemu-alpine-ssh | qemu-alpine-ssh__xXbqaYi | — | 0 | 0 | — | 17.4 | error |
| 45 | query-optimize | query-optimize__Fu8ykiL | — | 0 | 0 | — | 31.4 | error |
| 46 | query-optimize | query-optimize__srhYknP | — | 0 | 0 | — | 30.7 | error |
| 47 | raman-fitting | raman-fitting__RhDh36p | — | 0 | 0 | — | 24.4 | error |
| 48 | raman-fitting | raman-fitting__b2MfrdP | — | 0 | 0 | — | 25.8 | error |
| 49 | regex-log | regex-log__2qtkQpj | — | 0 | 0 | — | 37.5 | error |
| 50 | regex-log | regex-log__bkTjckn | — | 0 | 0 | — | 38.3 | error |
| 51 | sam-cell-seg | sam-cell-seg__Qfsy7JM | — | 0 | 0 | — | 17.1 | error |
| 52 | sam-cell-seg | sam-cell-seg__tn3QkVR | — | 0 | 0 | — | 17.3 | error |
| 53 | sanitize-git-repo | sanitize-git-repo__iJi9A46 | — | 0 | 0 | — | 24.8 | error |
| 54 | sanitize-git-repo | sanitize-git-repo__zmUaiqy | — | 0 | 0 | — | 24.0 | error |
| 55 | schemelike-metacircular-eval | schemelike-metacircular-eval__3WzF6rs | — | 0 | 0 | — | 24.8 | error |
| 56 | schemelike-metacircular-eval | schemelike-metacircular-eval__JbiGW7d | — | 0 | 0 | — | 25.2 | error |
| 57 | torch-pipeline-parallelism | torch-pipeline-parallelism__2Qbqoiu | — | 0 | 0 | — | 38.5 | error |
| 58 | torch-pipeline-parallelism | torch-pipeline-parallelism__sXUv7io | — | 0 | 0 | — | 37.2 | error |
| 59 | winning-avg-corewars | winning-avg-corewars__CwsaQvd | — | 0 | 0 | — | 16.8 | error |
| 60 | winning-avg-corewars | winning-avg-corewars__rTArbvj | — | 0 | 0 | — | 17.9 | error |

- 平均 reward：1.0000（4/4 满分）

### h0-baseline-r2

- 实验条件：agent=`agents.baseline_kira:AgentHarness`，model=`deepseek/deepseek-v4-flash`，environment=`docker`，n_concurrent=8，trials/任务=2，任务数=30
- 任务来源：`/data1/users/zhouMF/benchmarks/tb2-split-v1/train/bn-fit-modify`（source=train）
- 时间：2026-10-10T23:23:28.008242 → 2026-10-11T01:42:47.898190
- 汇总：trials=60，完成=60，异常=16，重试=0
- 合计用量：input_tokens=312152301，cache_tokens=0，output_tokens=5290540，cost_usd=9.287389

| # | task | trial | reward | in_tok | out_tok | cost_usd | wall_s | exception |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | bn-fit-modify | bn-fit-modify__t4cHsrM | 1.0 | 201654 | 31891 | 0.045968 | 254.7 | 无 |
| 2 | bn-fit-modify | bn-fit-modify__wkfyXBQ | 1.0 | 111970 | 27130 | 0.038751 | 215.2 | 无 |
| 3 | caffe-cifar-10 | caffe-cifar-10__La8jRYe | 0.0 | 3320760 | 23745 | 0.075831 | 1381.1 | error |
| 4 | caffe-cifar-10 | caffe-cifar-10__XECyDCi | — | 6047824 | 44929 | 0.127180 | 2639.9 | error |
| 5 | compile-compcert | compile-compcert__Q4gBKcU | — | — | — | — | 220.8 | error |
| 6 | compile-compcert | compile-compcert__nYmBVKU | 0.0 | 85470919 | 114898 | 0.739949 | 2451.8 | error |
| 7 | custom-memory-heap-crash | custom-memory-heap-crash__DyoLtzQ | 1.0 | 1037647 | 41598 | 0.071069 | 381.5 | 无 |
| 8 | custom-memory-heap-crash | custom-memory-heap-crash__nZSUrSU | 1.0 | 1290795 | 59259 | 0.094373 | 475.9 | 无 |
| 9 | dna-assembly | dna-assembly__prVwFyc | 1.0 | 4789870 | 304867 | 0.425771 | 1870.0 | error |
| 10 | dna-assembly | dna-assembly__vkpUsax | 0.0 | 657249 | 174359 | 0.224681 | 990.2 | 无 |
| 11 | extract-moves-from-video | extract-moves-from-video__SvzKHRL | 0.0 | 8323483 | 80671 | 0.176343 | 2221.4 | error |
| 12 | extract-moves-from-video | extract-moves-from-video__pfx6VfP | 0.0 | 10126860 | 100939 | 0.212112 | 1893.5 | error |
| 13 | fix-code-vulnerability | fix-code-vulnerability__5oSddnp | 1.0 | 109558 | 5431 | 0.012252 | 79.6 | 无 |
| 14 | fix-code-vulnerability | fix-code-vulnerability__Ntfpwje | 1.0 | 311049 | 7790 | 0.021716 | 95.0 | 无 |
| 15 | fix-ocaml-gc | fix-ocaml-gc__4NokCqc | 1.0 | 24048310 | 73447 | 0.269133 | 2510.5 | 无 |
| 16 | fix-ocaml-gc | fix-ocaml-gc__76BqM69 | 1.0 | 14870134 | 59629 | 0.189975 | 3457.7 | 无 |
| 17 | gcode-to-text | gcode-to-text__geHGXW7 | 0.0 | 1878377 | 157804 | 0.190228 | 939.7 | error |
| 18 | gcode-to-text | gcode-to-text__us5LDkT | 0.0 | 2936841 | 148054 | 0.218304 | 939.8 | error |
| 19 | git-multibranch | git-multibranch__DpDdhCz | — | 48884 | 17257 | 0.024009 | 177.3 | error |
| 20 | git-multibranch | git-multibranch__hxStcbb | 1.0 | 716291 | 109255 | 0.146130 | 694.8 | 无 |
| 21 | headless-terminal | headless-terminal__A274rRn | 1.0 | 129408 | 50647 | 0.065542 | 343.5 | 无 |
| 22 | headless-terminal | headless-terminal__XbNrukt | 1.0 | 213989 | 57566 | 0.075097 | 382.3 | 无 |
| 23 | hf-model-inference | hf-model-inference__jGDyHPA | 1.0 | 226434 | 18822 | 0.028424 | 351.6 | 无 |
| 24 | hf-model-inference | hf-model-inference__mNTPSUr | 1.0 | 172537 | 18872 | 0.027781 | 361.8 | 无 |
| 25 | llm-inference-batching-scheduler | llm-inference-batching-scheduler__7JVaG3C | 1.0 | 720080 | 49953 | 0.078964 | 340.9 | 无 |
| 26 | llm-inference-batching-scheduler | llm-inference-batching-scheduler__xdPzdww | 1.0 | 6267695 | 129215 | 0.230197 | 853.7 | 无 |
| 27 | mailman | mailman__FMNtZ4G | 1.0 | 6848896 | 228056 | 0.346748 | 1562.9 | 无 |
| 28 | mailman | mailman__RfQmVCj | 1.0 | 3739897 | 90008 | 0.152913 | 809.1 | 无 |
| 29 | make-mips-interpreter | make-mips-interpreter__J76nzsb | 0.0 | 28311958 | 194934 | 0.461847 | 1828.9 | 无 |
| 30 | make-mips-interpreter | make-mips-interpreter__cd2XyqE | 1.0 | 12778918 | 288111 | 0.464102 | 1836.4 | error |
| 31 | mcmc-sampling-stan | mcmc-sampling-stan__3QvVG2g | 1.0 | 20923843 | 78065 | 0.262367 | 1534.3 | 无 |
| 32 | mcmc-sampling-stan | mcmc-sampling-stan__gu2ecEw | 1.0 | 4997660 | 94188 | 0.166803 | 1121.3 | 无 |
| 33 | mteb-retrieve | mteb-retrieve__W7YdBod | 1.0 | 321348 | 15829 | 0.026926 | 326.1 | 无 |
| 34 | mteb-retrieve | mteb-retrieve__ukgLTGi | 1.0 | 2834596 | 54989 | 0.104004 | 631.7 | 无 |
| 35 | polyglot-c-py | polyglot-c-py__PSvzVK5 | 1.0 | 79018 | 47694 | 0.060880 | 315.0 | 无 |
| 36 | polyglot-c-py | polyglot-c-py__bm93vty | 1.0 | 247525 | 94658 | 0.121690 | 579.2 | 无 |
| 37 | portfolio-optimization | portfolio-optimization__BeNdkXy | 0.0 | 612193 | 30556 | 0.046352 | 303.2 | 无 |
| 38 | portfolio-optimization | portfolio-optimization__jp2Tn7e | 0.0 | 342393 | 18793 | 0.029308 | 187.5 | 无 |
| 39 | pypi-server | pypi-server__dnLb4iN | 1.0 | 124578 | 19288 | 0.027403 | 161.9 | 无 |
| 40 | pypi-server | pypi-server__nHRCLDC | 1.0 | 88794 | 21374 | 0.029520 | 188.8 | 无 |
| 41 | pytorch-model-cli | pytorch-model-cli__BdbPWLn | 1.0 | 1493943 | 55297 | 0.089147 | 570.8 | 无 |
| 42 | pytorch-model-cli | pytorch-model-cli__gMuJEUg | 1.0 | 538084 | 72225 | 0.099425 | 549.2 | 无 |
| 43 | qemu-alpine-ssh | qemu-alpine-ssh__4kWpw4C | 0.0 | 882517 | 47595 | 0.074363 | 421.2 | 无 |
| 44 | qemu-alpine-ssh | qemu-alpine-ssh__hLd2ngd | 0.0 | 3016461 | 92575 | 0.152713 | 666.2 | 无 |
| 45 | query-optimize | query-optimize__FwbViEd | — | 305676 | 36987 | 0.052507 | 1182.7 | error |
| 46 | query-optimize | query-optimize__f9y7whz | 1.0 | 481426 | 45088 | 0.064112 | 1214.0 | 无 |
| 47 | raman-fitting | raman-fitting__CETrsEz | 0.0 | 961359 | 156347 | 0.210079 | 934.0 | error |
| 48 | raman-fitting | raman-fitting__VFUDKEq | 0.0 | 1449670 | 147436 | 0.201067 | 938.1 | error |
| 49 | regex-log | regex-log__d64bWHh | 1.0 | 268458 | 130331 | 0.164719 | 708.7 | 无 |
| 50 | regex-log | regex-log__gxBZFZo | 1.0 | 97085 | 99268 | 0.124464 | 546.2 | 无 |
| 51 | sam-cell-seg | sam-cell-seg__h8wQ7wv | 0.0 | 7071021 | 126476 | 0.219557 | 1015.8 | 无 |
| 52 | sam-cell-seg | sam-cell-seg__jQ4Gxmj | 0.0 | 8420813 | 128069 | 0.231099 | 2427.4 | 无 |
| 53 | sanitize-git-repo | sanitize-git-repo__8VcRKKZ | 1.0 | 902730 | 37421 | 0.067616 | 296.4 | 无 |
| 54 | sanitize-git-repo | sanitize-git-repo__MTkut6K | 1.0 | 845185 | 34554 | 0.066519 | 246.3 | 无 |
| 55 | schemelike-metacircular-eval | schemelike-metacircular-eval__bxZDx7u | 1.0 | 19239929 | 275171 | 0.482409 | 2092.8 | 无 |
| 56 | schemelike-metacircular-eval | schemelike-metacircular-eval__zD2nzg7 | 1.0 | 3537365 | 171735 | 0.245282 | 1291.5 | 无 |
| 57 | torch-pipeline-parallelism | torch-pipeline-parallelism__6isqENG | — | 1162327 | 160674 | 0.214372 | 1872.6 | error |
| 58 | torch-pipeline-parallelism | torch-pipeline-parallelism__yJaxcLC | 0.0 | 153670 | 162609 | 0.203148 | 1475.3 | error |
| 59 | winning-avg-corewars | winning-avg-corewars__HwxoNHj | 1.0 | 915124 | 38010 | 0.061053 | 561.2 | 无 |
| 60 | winning-avg-corewars | winning-avg-corewars__REPQRQT | 1.0 | 4129223 | 88101 | 0.153097 | 727.7 | 无 |

- 平均 reward：0.6909（38/55 满分）

## R4 P5 优化循环冒烟（验证"提议 → 校验 → 评测 → 记录"四段）

目的：证明 Meta-Harness 的优化闭环在本地 docker + deepseek 下能完整跑通一轮，
并把提议器（Claude Code CLI → 本地网关 → deepseek）从"探针可用"提升到"循环内可用"。

启动命令（2026-10-11 01:50，前台受控运行，日志 `runs/p5-smoke.log`）：

```bash
HARBOR_TASK_PATH=/data1/users/zhouMF/benchmarks/tb2-smoke-v1 \
  bash code-adaptation/scripts/run_meta_harness.sh p5-smoke \
    --iterations 1 --trials 1 --skip-baseline --concurrent 4
```

`tb2-smoke-v1` 是从 train 划分挑出的 4 道便宜题（`bn-fit-modify`、`custom-memory-heap-crash`、
`fix-code-vulnerability`、`sanitize-git-repo`）的本地副本，只用于验证机制，不用于报告分数。
用 `--skip-baseline` 避免重复 Phase 0（基线已在 R3 单独跑过）。

### 四段证据

| 阶段 | 产物 | 证据 |
| --- | --- | --- |
| 提议 | `agents/deadline_aware_delivery.py`(253 行)、`prompt-templates/deadline-aware-delivery.txt`、`logs/p5-smoke/pending_eval.json` | 提议器实际调用 184+ 次工具：读基线 trajectory、派 1 个 `Agent` 子代理做诊断、复制 H0 后逐处 Edit；耗时 **13m14s** |
| 校验 | `jobs/p5-smoke/smoke-deadline_aware_delivery/` | `--validate-agent` import 通过 + `bn-fit-modify` 冒烟 **smoke OK（3m48s）**，1/1 候选有效 |
| 评测 | `jobs/p5-smoke/evolve-deadline_aware_delivery-t1/` | 4 题 × 1 trial，**avg=100%**，cost=$0.19，耗时 **6m14s** |
| 记录 | `logs/p5-smoke/evolution_summary.jsonl`、`frontier_val.json` | 逐题 pass rate、hypothesis、rollout 指标、frontier 均落盘 |

- 总耗时：23m21s（propose 13m14s + bench 6m14s）
- 真实花费：DeepSeek 余额 ¥67.09 → ¥65.39，即 **¥1.70**
- 提议器产出（模型自述的假设与证据）：
  基线 `h0-baseline-r2` 中 **14/59 trial 因 `AgentTimeoutError` 结束**，17 个 0 分 trial 里有 9 个是超时；
  另有 6 个"从未写出输出"的 0 分 trial 合计烧掉 470 个 turn 仍在探索；
  消耗 ≥90% 预算的 trial 通过率仅 2/11(18%)，而 <50% 的为 28/36(78%)。
  改动只做一件事：每轮把剩余墙钟预算暴露给模型，并临近截止时升级紧迫度。

### 结论与保留意见

- 闭环机制**已跑通**，验收二的前半条件（H0 出发跑通初始化与至少一轮 trace 优化）在本工作区成立。
- 4 道冒烟题对 H0 本身也偏易，100% 不能当作改进证据；真实增益必须在 train 30 题上按 `h0-baseline-r2` 对比。
- 提议器用的是 `deepseek-v4-flash` 而非论文的 Opus `effort=max`，提议质量不可与论文直接比；
  机制（skill 先验、工具集、stream-json、只改单文件候选）一致。
- `claude_wrapper` 记录的 `total_cost_usd` 是 Anthropic 列表价，对 deepseek 无意义；
  上表的真实花费取自 DeepSeek 余额差。

## R5 P6 正式搜索（train 30 题 × 1 trial × 2 轮）

启动命令（2026-10-11 02:23，后台运行，日志 `runs/p6-main.log`）：

```bash
HARBOR_TASK_PATH=/data1/users/zhouMF/benchmarks/tb2-split-v1/train \
HARBOR_TIMEOUT_SECONDS=10800 \
  bash code-adaptation/scripts/run_meta_harness.sh p6-main \
    --iterations 2 --trials 1 --skip-baseline --concurrent 8
```

`--skip-baseline` 的原因：Phase 0 会对 2 个基线各跑 30 题，约多花 ¥26；基线已在 R3 单独跑过，
逐题对比在 `notes/reproduction-summary.md` 第三节手工完成。

### 轮次结果

| 轮 | 候选 | 逐题均分（30 题为分母） | 评测耗时 | 提议耗时 |
| --- | --- | --- | --- | --- |
| 1 | `enforced_final_state_audit` | **0.667** NEW BEST | 72m31s | 9m00s |
| 2 | `deadline_audited_delivery` | 0.633（delta −3.3%） | 69m03s | 7m05s |
| 2 | `deadline_aware_delivery` | 0.600（delta −6.7%） | 66m56s | 同上 |

- 最终 frontier：`enforced_final_state_audit` @ 66.7%
- 第 2 轮的两个候选都是"墙钟预算可见性 + 完成审计门禁"方向的变体/消融，均未超过第 1 轮
- 总耗时：02:23:07 → 06:24:00（**5h05m**）
- 真实花费：DeepSeek 余额 ¥47.26 → ¥16.87，即 **¥30.39**

### 产物

| 路径 | 内容 |
| --- | --- |
| `logs/p6-main/evolution_summary.jsonl` | 3 条记录：候选、hypothesis、逐题 pass rate、rollout 指标（turns/cost/tokens） |
| `logs/p6-main/frontier_val.json` | 逐题 best_agent 与 pass_rate，`_best` = `enforced_final_state_audit` @ 66.7% |
| `logs/p6-main/pending_eval.json` | 每轮提议器写出的候选清单 |
| `logs/p6-main/claude_sessions/` | 提议器会话：`events.jsonl`、`response.md`、`meta.json`、逐次工具调用 |
| `jobs/p6-main/smoke-*` | 3 次候选冒烟（均 OK） |
| `jobs/p6-main/evolve-*-t1/` | 3 次 30 题评测的逐题 trace |
| `agents/enforced_final_state_audit.py` 等 | 3 个候选（单文件，继承 `Terminus2`） |

### 与基线的对比（摘要）

| 口径 | H0 基线 R3 | iter1 候选 | iter2 候选 A | iter2 候选 B |
| --- | --- | --- | --- | --- |
| 计分题数 | 30（2 trials） | 28（1 trial） | 28（1 trial） | 27（1 trial） |
| 均分 | 0.6667 | 0.7143 | 0.6786 | 0.6667 |

候选在三条上都不构成稳定改进：iter1 的 +4.8pt 来自 `compile-compcert`、`portfolio-optimization`
0→1 与 `dna-assembly` 0.5→1，同时 `pytorch-model-cli`、`make-mips-interpreter` 由 1 掉到 0。
逐题表见 `notes/reproduction-summary.md` 第三节。

## R6 环境重检（2026-10-12，不调执行模型）

目的：在续跑前确认链路仍可用、H0 仍与共享参考一致，并核对余额，判断能否继续 P6 扩轮。

| 检查 | 命令 | 结果 |
| --- | --- | --- |
| 免 provider 单测 | `uv run --with pytest --no-sync pytest tests/ -q` | ✅ 12 passed in 5.13s |
| H0 一致性 | `md5sum harness/h0/terminus-kira/agents/baseline_kira.py` 与个人副本 | ✅ 同为 `2a6d57f5782037da70ffb279adab024e` |
| H0 无本地改动 | `git diff --stat HEAD -- .../agents/baseline_kira.py` | ✅ 无 diff |
| harbor / uv / docker | `.venv/bin/python -c "import harbor"`、`uv --version`、`docker version` | ✅ harbor 0.18.0、uv 0.13.0、docker 24.0.2 |
| 提议器网关 | `curl 127.0.0.1:4000/health/liveliness` | ✅ 200 |
| 本地任务集 | `ls /data1/users/zhouMF/benchmarks/tb2-split-v1` | ✅ train 30 / dev 19 / test 40 |
| DeepSeek 余额 | `curl https://api.deepseek.com/user/balance` | ⚠️ `total_balance ¥2.26`（granted 0） |

结论：环境与链路完好，H0 仍满足"与参考实现一致"。**余额不足**，单候选 30 题 1 trial 约 ¥10，
因此本轮无法继续 P6 扩轮或做候选 2 trials 的严格对比；该项转入待办（见 `notes/reproduction-steps.md` 第五节）。
