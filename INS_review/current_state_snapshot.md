# 论文当前状态快照（2026-08-15，供综合 Prompt 引用）

> 说明：本文件由本次会话确定性核验生成，作为综合 Prompt 的「已知状态」依据，避免执行 Agent 重复已完成的修复。

## 1. 投稿包五件套状态（已核验）

| 文件 | 状态 | 关键合规点 |
|---|---|---|
| `manuscript.tex` | ✅ elsarticle，`\journal{Information Sciences}` | `\documentclass[review,1p,times]{elsarticle}`；elsarticle-num 引用；含 Data Availability / Declaration of Competing Interest / Declaration of Generative AI / CRediT 四段声明 |
| `supplementary.tex` | ✅ elsarticle，IS 期刊 | 8 个节：MAE、SSVS τ² 消融、噪声消融、R 扫描、BIC 失败机制消融、MCMC 诊断、高维边界（Superconductivity d=81）、MPIW |
| `highlights.tex` | ✅ 5 条 | 字符数 75/80/73/61/64（均 ≤85）|
| `cover_letter.tex` | ✅ 致 Pedrycz | 含贡献/Journal Fit（6 条 S0020-0255 先例）/Metadata/Suggested Reviewers（3 位）/原创声明 |
| `references.bib` | ✅ 25 条 | 25 条全部被正文引用；CrossRef 已验真（P4）|

## 2. 已确认合规项（本会话复核，勿再改动）

- 摘要词数：**154 词**（≤200 达标；P3 记录为 158，以当前 154 为准）
- Keywords：6 个，`uncertainty quantification` 领跑
- Highlights：5 条 ≤85 字符
- 图：6 张（fig1_repro_fix / fig2_main_comparison / fig3_calibration / fig4_sparsity_boundary / fig5_reliability / fig6_pi_band），全部被正文引用，`results/figures/` 无孤儿图（_legacy/ 已隔离）
- 语域：catastrophically / no free lunch / covers almost nothing / widely-copied / first exact / generalizes to any 全部清零；"severely" 保留 3 处（事实性）
- 术语：spread 统一为「per-cluster standard deviation × s」；方法名 TSK-LS / Bayesian-TSK / TSK-SpikeSlab-BIC / TSK-SpikeSlab-Gibbs / TSK-SSVS 与代码类名映射在 README 声明
- 统计：paired Wilcoxon signed-rank 已入正文（Energy p≥0.07；Concrete p<0.01 但 ΔR²<0.01）；GP 基线已入 Table 1；MCMC 诊断（R-hat≤1.01，ESS>1700）已入正文 + supplementary
- 数字一致性：P4 终审确认 PICP 0.94–0.95 / BIC 0.00–0.18 / 0.41→0.94 / 摘要-引言-结果-结论-cover letter 一致
- 可复现：GitHub remote 已同步（main），Zenodo DOI 10.5281/zenodo.21929319 可解析，SEED=42，requirements.txt 齐全

## 3. 残留风险 / 已知可优化项（P4 + 本会话补充）

| # | 项 | 级别 | 说明 |
|---|---|---|---|
| R-A | 缺 ANFIS / IT2-FLS / 近期稀疏模糊基线实测 | Medium | 已用 GP 补外部概率基线 + Related Work 一句论证为何不适用；审稿人仍可能追问 |
| R-B | 稀疏机制在 d=8 与 d=81 都不赢 | Medium | 靠「sparsity design criterion + 诚实边界」回答 |
| R-C | generality 只 hedge（"applies to"）未演示 | Low | 第二模型族实例化可消除，性价比低 |
| R-D | **作者 Biography ≤100 词 + 证件照（Elsevier author vitae）缺失** | 待确认 | P0 标记为终稿阶段待补；需联网确认 IS 是否硬性要求 |
| R-E | 图 5/6 为 supplementary 风格，非投稿必需 | Low | 已入正文 §5.3 |
| R-F | 「Exact」术语（标题/摘要/贡献 1）：MCMC 采样严格说是有限样本 MC 近似，审稿人可能挑战 | Medium | 本会话新发现；已有 R-hat/ESS 诊断支撑，但建议在方法节显式定义「exact」=「targets the exact posterior, not an analytical approximation」或加一句限定 |
| R-G | 缺行号（review 模式）：manuscript 未 `\usepackage{lineno}`，若 IS 审稿要求行号则不符 | 待确认 | 需联网确认 elsarticle review 模式默认行号策略 |
| R-H | Graphical abstract 是否必需 | 待确认 | 需联网确认 IS 是否强制要求 |
| R-I | `references.bib` 条目 `ieeeaccess2024interpretable` 的 key 名误导（实际是 IEEE TFS 2025，非 IEEE Access 2024） | Low | 元数据正确，仅 key 名不匹配，可顺手改 key |
| R-J | highlights 第 3 条 "worthwhile---and when it is not" 的 `---`（em-dash）在严格「≤85 字符含空格」计数下边界 | Low | 若按 em-dash 计 1 字符仍 ≤85；无需改但可优化措辞 |

## 4. 四件套标题（一致）

> Exact Bayesian Inference for Spike-and-Slab Priors in Takagi--Sugeno--Kang Fuzzy Systems with Calibrated Model-Averaged Prediction Intervals

（manuscript / supplementary / highlights / cover letter 四处一致，P4 已核验）
