# Rebuttal 模板（Information Sciences，审稿意见后使用）

> 用途：收到 IS 审稿意见（一般 2–3 位审稿人，首轮 ~3.1 月）后逐条回应。IS 单盲评审，回应给 Editors + Reviewers，建议 ~4–8 周内提交 revision。
> 原则：证据驱动、逐条编号、诚实（不夸大）、对可复现性/统计批评用 `results/raw/*.json` 实测数据回击。

## 0. 通用结构
```
Response to reviewers — "Exact Bayesian Inference for Spike-and-Slab Priors in
Takagi–Sugeno–Kang Fuzzy Systems with Approximately Calibrated Model-Averaged
Prediction Intervals" (Information Sciences, manuscript ID XXX)

We thank the reviewers for their constructive comments. All changes are
marked in the revised manuscript (tracked at ...). Point-by-point responses:
```

## 1. 逐条回应格式
```
Reviewer 1, Comment R1.1: [原文引用]
Response: We thank the reviewer. [澄清/接受/不同意] ...
- 修改：manuscript.tex:XX / supplementary.tex:XX — [具体改动]
- 证据：results/raw/xxx.json — [实测数字]
```

## 2. 高频问题→现成弹药（来自本轮准备）
| 审稿人可能问 | 现成回应 |
|---|---|
| 「为何不用 conjugate（闭式）？」 | 本稿是**精确贝叶斯推断 + 稀疏选择**的方法贡献；d=81 上 Gibbs/BMA 保持近名义校准（PICP 0.940）而共轭欠覆盖（0.921）（supp Table 7）；§5.3 |
| 「BIC/Laplace 为何塌缩？」 | 消融隔离：阈值化塌缩精度（R² 0.60）；as-implemented ridge 拟合病态矩阵塌缩覆盖；忠实版覆盖近名义但精度低/区间宽（supp Table 5） |
| 「γ 更新式是否正确？」 | 合成验证：穷举 2^R 精确边际对拍，max |Gibbs−Exact| = 8×10⁻⁴（supp Section 9） |
| 「稀疏为何不赢？」 | 低维 + 高维全 τ² 网格：无任何 τ² 优于稠密（低维 0.92 vs 0.94；高维 0.794 vs 0.792）；正确 FCM 已鲁棒 |
| 「缺 ANFIS/ENNreg/IT2 基线？」 | Setup 有 scope 论证（机制不同非后验模型选择）；GP 为外部概率基线；如需可补 ENNreg（R 包） |
| 「Cooling 覆盖欠 1.5pp？」 | 已诚实披露：near-nominal 而非 perfectly calibrated；标题/摘要/图注全链一致；Wilson CI 公开 |
| 「0.48→0.94 before 值哪来的？」 | `results/raw/buggy_baselines.json` + `src/buggy_membership_repro.py` 可复现 |
| 「引用真实性？」 | 39 条 CrossRef 验真（含修复 fragoso/lei DOI） |

## 3. 回应语气
- 接受 → 简短致谢 + 具体改动 + 证据。
- 澄清 → 用稿件原文 + 实测数字说明，不争辩。
- 不同意 → 有证据时礼貌坚持（"we respectfully note that…"），并补一句软化。
- 一律：每处改动给 file:line；新数字必须来自重跑 `results/raw/*.json`。

## 4. 提交 revision 前自检
- [ ] 四件套重编译 0 errors / 0 undefined
- [ ] 新回应中的每个数字都能从 results/raw/ 复现
- [ ] 改动未引入新的夸大声明（保持 near-nominal / approximately calibrated 口径）
- [ ] 高亮改动清单（response letter 首段列出主要修改）
