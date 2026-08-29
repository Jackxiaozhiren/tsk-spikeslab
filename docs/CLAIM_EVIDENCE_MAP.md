# Phase 6 主张—证据映射

日期：2026-08-29  
工作树：`<WORK_ROOT>`  
用途：把旧稿中的科学主张与 Phase 4 从零重建的权威输出逐项对齐。旧 Prompt、旧 QA、旧 PDF、旧 JSON 和旧“终审通过”报告不作为证据。

## 决策摘要

本轮不新增研究方法。稿件改写为一篇以可复现实现审计、正确性修复和预测性不确定性比较为中心的应用型软件/软计算论文候选稿。所有结果数字仅从 `rebuild_results_2026-08-29_v1/` 的 JSON 或由其自动生成的表图进入稿件。

## 主张映射

| 旧稿主张或数字 | 当前权威证据 | Phase 6 处理 |
| --- | --- | --- |
| “membership bug 将 Energy-Cooling 的 TSK-LS 从 0.48 提升到 0.94” | `buggy_baselines.json` 的新管线复现得到 Energy-Cooling TSK-LS 的极端负 (R^2)，并非旧的 0.48；新主结果中的修复后 TSK-LS 为 (R^2=0.9229)。 | 删除固定的 0.48→0.94 叙事；只保留“训练时冻结、推理时复用 membership 参数”的实现原则，并把缺陷复现限定为敏感性诊断。 |
| BIC-plus-Laplace “崩溃到负 (R^2)，PICP=0–0.18” | `main_rebuilt.json` 中修复后主管线的 TSK-SpikeSlab-BIC 为 (R^2=0.9563/0.9220/0.7859)，PICP (=0.9403/0.9344/0.9383)；`ablation_isolate_v2.json` 的四个配置均为正 (R^2)。 | 删除负 (R^2) 和机制确定性归因；改为说明在修复后管线下 BIC、threshold、Gibbs threshold 与 BMA 的差异较小，旧崩溃不能作为当前结论。 |
| “Gibbs/BMA 恢复并优于/校准 dense baseline” | `main_rebuilt.json`：Gibbs (R^2=0.9567/0.9224/0.7840)，Bayesian (R^2=0.9569/0.9227/0.7858)，PICP 分别约 0.940/0.934/0.938；TSK-LS 为 0.9570/0.9229/0.7859。 | 改为“Gibbs/BMA 与 dense/conjugate TSK 接近；不声称优势或完美校准”。同时报告 GP 的点预测与区间结果，避免把 TSK 结果置于脱离基线的叙事中。 |
| “exact Bayesian inference / exact MCMC” | 代码是 MCMC；`synthetic_gamma_verify.json` 只支持在有限合成配置上与枚举结果比较，且当前最大 PIP 差约 0.0261、BMA 均值最大差约 0.0224。 | 将 “exact” 全部改为 “block-Gibbs posterior sampling” 或 “finite-sample numerical verification”；仅在“枚举对照”语境中使用 exact enumeration。 |
| “所有 MCMC \\hat R≤1.001” | `mcmc_diagnostics.json`：raw (eta) (hat R_max=1.061)（Energy-Cooling）、1.030（Concrete）；predictive (hat R_max=1.004)、1.027；(sigma^2) ESS 均值约 1639.5/1740.3。 | 删除旧门槛式结论；报告 raw 参数与 predictive quantity 的分开诊断，并明确混合仍有风险。 |
| “低维和高维都证明 sparsity 不值得” | 低维主结果 rule-level Gibbs 与 dense 接近；高维探针为 dense 0.8197、Bayesian 0.8221、Gibbs 0.7643、SSVS (	au^2=1) 0.8130、(	au^2=10) 0.8182；grid 最大 SSVS 约 0.8195，低于对应 dense。 | 保留为“本实验设置下未观察到稳定收益”，不外推为普遍 sparsity boundary；明确高维探针的实验范围和限制。 |
| “rule-level inclusion probabilities saturate near 1.0 / Gibbs recovers true sparse rules to (10^{-3})” | 主结果 active-rule ratio 与诊断支持真实 benchmark 上的高激活；合成枚举差异约 0.0261，不是 (10^{-3}) 级的普遍证据。 | 限定为“在这些 benchmark 中常接近全激活”；删除 (10^{-3}) 泛化表述，保留合成对照的实际误差。 |
| “PICP near-nominal / calibrated” | Bayesian/Gibbs PICP 为约 0.932–0.940；Conformal 为约 0.9566–0.9712；GP 为约 0.9312–0.9395。 | 使用“接近 nominal 95%”并同时给出 width/WIS/CRPS；不使用 “calibrated” 作为已证实的绝对标签。 |
| “方法适用于任何线性后件 rule-based regression” | 当前实验覆盖 3 个低维目标和 1 个高维探针，固定 Gaussian antecedent/FCM/TSK 结构。 | 改为“可作为具有线性后件的 TSK 实现的一个可复现实例”；把广泛适用性列为待验证范围。 |
| “首个/据我们所知没有先例” | Phase 5 最近邻包括 Bayesian TSK、sparse TSK、uncertainty-aware TSK、conformal fuzzy regression 和 high-dimensional TSK。 | 删除优先权式 novelty claim；将贡献聚焦于实现审计、修复后比较和可复现证据链。 |
| 旧稿中的旧表格、旧图、旧 supplementary 数字 | 与新 JSON 的 schema、结果和诊断不一致。 | 表格和图全部由新 JSON 自动生成；旧图不复制，旧补充结果不直接保留。 |

## 可保留的技术事实

- TSK 输出可写成带规则块的线性设计模型。
- 训练阶段计算的 Gaussian membership centers/spreads 应被冻结并在推理时复用。
- 共轭 Bayesian TSK 可作为 dense reference；rule-level spike-and-slab 使用 block-Gibbs sampling，BMA 通过 posterior predictive draws 传播模型不确定性。
- 所有主结果来自 30 个固定种子的 80/20 splits；conformal 使用 outer-train 内再划分 calibration set，不能与普通 TSK 结果作完全同 protocol 的等价解释。
- 当前结果只支持“在本数据和本实现协议下”的比较结论。

## 不得重新引入的表述

`exact inference`、`exact MCMC`、`perfectly calibrated`、`correct and calibrated Bayesian TSK`、`first`、`no prior work`、`applies to any rule-based regression`、旧的 `0.48\rightarrow0.94`、旧的负 (R^2) 崩溃数字，以及“所有 \\hat R≤1.001”。

