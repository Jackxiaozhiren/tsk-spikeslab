# Phase 0 · 环境与基线快照（INS 转投稿审查）

生成时间：2026-08-13 · 执行方式：主循环 Read/Grep/Bash + workflow 多智能体复核
状态：`INS_review/` 目录新建，本文为首份产物。

---

## 1. 文件清单与修改时间

| 文件 | 类型 | 修改时间 | git 状态 | 说明 |
|------|------|----------|----------|------|
| `manuscript.tex` | 正文（288 行） | 2026-08-13 19:26 | M（已改） | 最新重写稿，`\documentclass[11pt]{article}` |
| `supplementary.tex` | 补充材料（104 行） | **2026-07-27 13:59** | ??（未跟踪） | **旧版残留**，`elsarticle` + `\journal{Applied Soft Computing}` |
| `highlights.tex` | 亮点（26 行） | 2026-08-13 18:24 | M | 已更新，但 PICP 数字与正文矛盾 |
| `cover_letter.tex` | 投稿信（51 行） | 2026-08-13 19:49 | ?? | 面向 Information Sciences（已更新） |
| `references.bib` | 参考文献（40 条，431 行） | **2026-07-27 13:52** | M | **未随正文更新**，含约 20 条未引用条目 |
| `manuscript.pdf` | 正文 PDF | 2026-08-13 19:27 | ?? | 最新编译 |
| `supplementary.pdf` | 补充 PDF | **2026-07-27 13:59** | ?? | 旧版 |
| `cover_letter.md` | 旧投稿信 | — | **D（已删除）** | git 显示删除 |

**关键观察**：`supplementary.tex` 与 `references.bib` 的修改时间停留在 7-27，均早于 8-13 的正文重写，二者未随正文同步更新 → 与正文存在系统性脱节（详见 Phase 2）。

---

## 2. 五件套一致性矩阵

| 维度 | manuscript.tex | supplementary.tex | highlights.tex | cover_letter.tex | references.bib |
|------|----------------|-------------------|----------------|------------------|----------------|
| 目标期刊 | 无 `\journal`（裸 `article`） | **Applied Soft Computing** | — | **Information Sciences** | —（通用） |
| 论文标题 | Correct and Calibrated Bayesian Inference for **Takagi--Sugeno--Kang** Fuzzy Systems… | **Sparse Bayesian TSK … for Building Energy Prediction** | Correct and Calibrated Bayesian Inference for **TSK** Fuzzy Systems… | Correct and Calibrated Bayesian Inference for **Takagi--Sugeno--Kang**… | 注释仍写 "Sparse Bayesian TSK … Spike-and-Slab" |
| 数据集 | Energy（2 目标）+ Concrete（2 个） | Energy + Concrete + **Facebook Metrics + Air Quality**（4 个） | — | — | 含 Facebook/Air Quality 的 bib |
| 方法名 | TSK-LS / Bayesian-TSK / TSK-SpikeSlab-**BIC** / TSK-SpikeSlab-Gibbs / TSK-SSVS | TSK-LS / **TSK-LASSO** / TSK-SpikeSlab / Bayesian-TSK | — | — | — |
| PICP | 0.94–0.95 | 0.000–0.227（旧 τ² 表） | **0.92–0.95** | 0.94–0.95 | — |
| 文档类 | `article`（11pt） | `elsarticle`（review,1p,times） | `article` | `letter` | — |

**结论**：五件套在「期刊 / 标题 / 数据集 / 方法名 / 关键数字」五个维度上均未对齐，`supplementary.tex` 是唯一一个面向 Applied Soft Computing 的旧文件。

---

## 3. 图件：已引用 vs 孤儿

### 3.1 `results/figures/` 磁盘清单（22 个文件）

**新图族（8-13 生成，正文引用）**：
- `fig1_repro_fix.{pdf,png}` ✅ 被 `manuscript.tex` 引用（`fig:repro`）
- `fig2_main_comparison.{pdf,png}` ✅ 被引用（`fig:main`）
- `fig3_calibration.{pdf,png}` ✅ 被引用（`fig:cal`）
- `fig4_sparsity_boundary.{pdf,png}` ✅ 被引用（`fig:sparse`）

**旧图族（7-26 生成，正文未引用 → 孤儿）**：
- `fig1_main_comparison.{pdf,png}` ❌ 孤儿
- `fig2_uncertainty.{pdf,png}` ❌ 孤儿
- `fig3_mechanism.{pdf,png}` ❌ 孤儿
- `fig4_fcm_sensitivity.{pdf,png}` ❌ 孤儿
- `fig5_cd_diagram.{pdf,png}` ❌ 孤儿（**CD 图 = Nemenyi 显著性检验图，正文却无任何统计检验**）
- `fig6_rules.{pdf,png}` ❌ 孤儿
- `fig7_pareto.{pdf,png}` ❌ 孤儿

### 3.2 图件命名冲突
新图 `fig2_main_comparison` 与旧图 `fig1_main_comparison` 语义重叠；`fig2_uncertainty`（旧）与 `fig3_calibration`（新）语义重叠。git 状态中旧图族为 `M`（已修改但仍被跟踪），新图族为 `??`（未跟踪）——两套图并存于仓库，投稿时易误传旧图。

### 3.3 图名 ↔ `\includegraphics` 对应
正文 4 处 `\includegraphics` 均指向新图族，无断链。但存在一个**编号-文件不匹配**：正文 Figure 3 标题是 "Calibration"（`fig3_calibration.pdf`），而旧图族里也有一张 `fig3_mechanism.pdf`——两套 numbering 并存。

---

## 4. 原始数据与代码清单

`results/raw/` 下新旧两套结果并存：

| 文件 | 生成时间 | 状态 |
|------|----------|------|
| `tier1_v2.json` / `tier2_tau2_v2.json` / `tier3_noise_v2.json` | 8-13 | ✅ 与正文 Table 1 数字一致（已核验，见 Phase 2） |
| `energy.npz` / `concrete.npz` | 8-13 | ✅ 正文数据集 |
| `facebook.npz` | 8-13 | ⚠️ Facebook 已从正文删除，但数据仍在 |
| `tier1_results.json` / `tier1_highdim.json` / `tier2_ablation.json` / `tier3_fcm.json` / `tier4_*.json`（7 个） | 7-26 | ❌ 旧实验残留（旧方法/旧图） |

`src/` 下代码：
- 新：`tsk_core.py`（修正后核心）、`experiment_v2.py`、`figures_v2.py`、`gibbs_verify.py`、`smoke_test.py`
- 旧：`figures.py`（git 显示 M，旧图生成脚本）

---

## 5. Phase 0 结论（一句话）

仓库处于「正文已重写、supplementary/bib/旧图/旧数据未清理」的半迁移状态，投稿前必须完成旧版残留清理（详细逐条问题见 Phase 2 报告）。
