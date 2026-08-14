# Phase 2 修复日志（Critical + High 逐项闭环）

生成时间：2026-08-14
范围：仅 Critical + High（Medium/Low 留待后续 Phase）。所有改动已通过 `latexmk` 编译验证（manuscript 与 supplementary 均 exit 0、无错误）。

> 注：仓库目录在会话中被重命名 `ASC论文` → `IS论文`（与转投 Information Sciences 一致），本日志路径以新目录 `IS论文/` 为准。

---

## 🔴 Critical

### C1 · spread 描述统一为「逐簇标准差 × s」
- **改动**（manuscript.tex 三处）：
  - §3.1 eq:membership（L89）：`spreads $s_{ji}$ set to the standard deviation of the training points assigned to each cluster, scaled by a factor $s$`
  - Algorithm 1（L102）：`per-cluster standard deviations from training points, scaled by $s$`
  - §Setup（L156）：`per-cluster standard deviation of training points, scaled by $s=1.5$`
- **依据**：`src/tsk_core.py:140-148` 实际实现 `spreads[j] = per_cluster_std * s + 0.01`（默认 s=1.5）。原两处描述（常数 1.5 / 纯逐簇标准差）各自只对一半，现已统一。

### C2 · supplementary 期刊 + 标题 + 全部旧内容重写
- `\journal{Applied Soft Computing}` → `\journal{Information Sciences}`
- 标题改为正文标题的「Supplementary Material for …」
- references.bib 头注释同步改为新标题
- 整份 supplementary 按新正文（2 数据集 / 4 方法 + SSVS）重写（见 H10）

---

## 🟠 High

| # | 问题 | 改动 | 文件:行 |
|---|------|------|---------|
| H1 | 零统计检验 | 新增 paired Wilcoxon signed-rank 结果（p 值），引用 `wilcoxon1945individual`；表 caption 与正文措辞改为定量 | manuscript.tex §Results/L179、caption/L183 |
| H2 | Highlights PICP 0.92 | 改 0.94–0.95 | highlights.tex L20 |
| H3 | 贡献#1 "+0.30 to +0.53" | 改 "+0.10 to +0.53 across three targets" | manuscript.tex L48 |
| H4 | "three benchmarks" | 改 "two UCI benchmarks (three regression targets)"；L48/L230 同步 "three targets" | manuscript.tex L48/L156/L230 |
| H5 | "six orders" | 改 "three orders of magnitude" | manuscript.tex L232 |
| H6 | "widely-copied"/"common implementation" | 软化/删除，改为 "an implementation we encountered while reproducing published TSK baselines" | manuscript.tex L40/L94、cover_letter.tex L24 |
| H7 | jantre2025spike DOI 失效 | DOI 改 `10.1109/TNNLS.2024.3485529` | references.bib |
| H8 | neuralnet2024sparsetsk DOI 指向错误论文 | 作者改 Ji/Fan/Dong/Liu，pages 106599，DOI `10.1016/j.neunet.2024.106599`，标题补全 | references.bib |
| H9 | BIC 法名与代码名脱节 | 方法定义处加 "(labeled `SpikeSlab-Fast` in the released code)"，Gibbs/SSVS 同步 | manuscript.tex L158 |
| H10 | supplementary 5 处旧内容 | 整份重写：删 TSK-LASSO/Facebook/Air Quality/旧 τ² 表；MAE 表、SSVS τ² 表（0.1–100）、噪声消融表均从 `tier1_v2/tier2_tau2_v2/tier3_noise_v2.json` 重新计算 | supplementary.tex |
| H11 | "depressed every TSK baseline" | 改 "depressed the dense TSK baselines to varying degrees" | manuscript.tex L48 |

---

## 关键科学发现（H1 的诚实处理）

对 30 splits 跑 paired Wilcoxon signed-rank（R² 与 RMSE）后，结果比原文的「statistically indistinguishable」更微妙：

- **BIC 近似法**显著劣于所有方法（全部 target 上 p<0.001）——这是干净的正结果，已写入正文。
- **TSK-LS vs Bayesian-TSK / Gibbs**：Energy 两目标不显著（p≥0.07）；**Concrete 上名义显著（p<0.01）但效应量可忽略（ΔR²<0.01）**。

正文已按此诚实表述：「not significantly worse on the Energy targets (p≥0.07); on Concrete the residual difference is nominally significant (p<0.01) but negligible in magnitude (ΔR²<0.01)」，而非继续写"indistinguishable"。

## 遗留事项（非 Critical/High，记录备查）

1. **`demsar2006statistical` 仍未引用**：现有 `fig5_cd_diagram`（Nemenyi CD 图）是旧版（7 方法 × 5 数据集，含 Facebook/Air Quality），**不能复用**。跨数据集 CD 图属 Phase 8 重绘任务，届时再引 demsar2006。
2. **20 条未引用 bib 条目**（K7）仍在 references.bib，属 Phase 5 清理/补引。
3. **孤儿图 14 个文件**（旧图族）仍在 `results/figures/`，属 Phase 8 清理。
4. **Medium/Low 项**（如 "dense baselines are strong" 过强、single-target 推广、cover letter "first exact" 声明等）留待 Phase 3/4 处理。
5. **PDF 需重新编译**：manuscript.pdf / supplementary.pdf / highlights.pdf / cover_letter.pdf 当前仍是改动前的旧版本，需 `latexmk -pdf` 重新生成。
