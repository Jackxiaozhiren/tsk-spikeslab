# Phase 1 + Phase 3 修复日志（Critical + High + 部分 Medium/Low）

生成时间：2026-08-14
范围：Phase 1（期刊合规）+ Phase 3（科学性）审计发现的 Critical/High 确定性修复 + 叙事重构 + 1 项核心校验。所有改动经 `latexmk` 编译验证（manuscript / supplementary 均 exit 0）。

---

## 一、叙事重构（Scope，Seed K5 —— 由「修 bug」转向「方法」）

| # | 改动 | 位置 |
|---|------|------|
| 标题 | 新标题 **「Exact Bayesian Spike-and-Slab Inference for Takagi--Sugeno--Kang Fuzzy Systems with Calibrated Model-Averaged Prediction Intervals」**（去掉 "Reproducibility Fix"） | manuscript.tex、highlights.tex、cover_letter.tex、supplementary.tex 同步 |
| 摘要 | 重排为方法优先：先 Gibbs/BMA 方法与校准保证，bug fix 与稀疏边界降为验证句；结尾改为「generalizes to any rule-based regression with linear consequents」 | manuscript.tex |
| 贡献列表 | #1 改为 "Exact spike-and-slab inference for TSK consequents"，#2 "Calibrated model-averaged prediction intervals"，#3 "A verified dense baseline and a sparsity boundary" | manuscript.tex |
| 引言 | 两问题顺序对调：方法论问题（BIC+Laplace）先，可复现性 bug 后（作支撑） | manuscript.tex |
| 结论 | 以方法开头、以可迁移原则收尾 | manuscript.tex |
| Keywords | 改为 6 个 INS 高频词（含 Bayesian model averaging / prediction intervals），删 "reproducibility" | manuscript.tex |

## 二、格式合规（Elsevier 红线）

| # | 改动 | 位置 |
|---|------|------|
| 文档类 | `\documentclass[11pt]{article}` → `\documentclass[review,1p,times]{elsarticle}` + `\journal{Information Sciences}` + `frontmatter` 包裹 | manuscript.tex |
| 参考文献编号 | `\bibliographystyle{plain}` → `elsarticle-num` | manuscript.tex |
| Highlights | 重写为 5 条、每条 ≤85 字符、方法优先 | highlights.tex |
| 标题 | 投稿信 References 19→20、新增「Suggested Reviewers」段（3 位，邮箱待补） | cover_letter.tex |
| 声明标题 | "Conflict of Interest"→"Declaration of Competing Interest"；"CRediT Author Statement"→"CRediT authorship contribution statement" | manuscript.tex |

## 三、方法严谨性（科学性）

| # | 改动 | 位置 |
|---|------|------|
| 超参陈述 | 补「$\pi=0.5$；rule-level Gibbs/conjugate $\tau^2=10^3$；SSVS $\tau^2=1.0$」+ 种子 SEED=42 | manuscript.tex §Setup |
| 声明修正 | 「PIP concentrate at 1.0」→「close to 1.0（Energy 上偶尔剪至 4 条）」——与 tier1_v2.json ActiveRules={4,5} 对齐 | manuscript.tex §Sparsity |
| 图注澄清 | Fig.1 caption 明说 "reported by the prior buggy pipeline"（buggy R² 是硬编码常量，非重跑） | manuscript.tex §Repro |
| **conjugate 校验** | **实际执行并通过**：block-Gibbs 强制 $\gamma_j=1$ 时，后验均值/协方差恢复闭合形式（相对均值误差 5e-3、协方差误差 9e-2）。已写入 §3.3 | manuscript.tex §Conjugate |

## 四、可复现性（repro）

| # | 改动 |
|---|------|
| requirements.txt | 新建：numpy/scipy/scikit-learn/matplotlib/ucimlrepo |
| README.md | 新建：入口命令、SEED=42、方法名↔代码类映射表 |

## 五、遗留（明确记录，待后续 Phase）

1. **`gibbs_verify.py` / `smoke_test.py` 用 `KMeans` 冒充 FCM**（历史 desk-reject 事故重演），且 `gibbs_verify.py` 名不副实（并不校验 Gibbs）。这两个文件**未纳入本次提交**，需在 Phase 8 删除或重写为 FCM + 闭合形式校验。
2. **新实验（需重跑，暂缓）**：
   - A1 隔离 BIC 硬阈值 vs Laplace 协方差 vs BMA（当前 Gibbs vs BIC 对比混杂）；
   - A2 规则数 R=3–10 敏感性；
   - Z2 外部基线 `bian2025mhtsk`/`xue2023dgaletsk`（或删未引条目 + 说明不适用）；
   - S5 高维数据集 d>30。
3. **buggy 数字可复现性**：`figures_v2.py` 硬编码的 "buggy" R² 无法从当前（已修正）代码重跑——要么提交 buggy 版本，要么维持 caption 澄清（已做）。
4. **旧文件清理**：旧图族 14 个文件、旧 results（tier1_results.json 等）、`facebook.npz`、`src/figures.py` 仍留在仓库，Phase 8 删除/rename。
5. **git push** 未执行（仅本地 commit）。
