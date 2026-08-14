# Phase 2 · 学术诚信与一致性审计（INS 转投稿审查）

生成时间：2026-08-13
方法：主循环（数字/CrossRef/原始数据确定性核验）+ workflow 五维并行审计（figures / numbers / claims / terminology / crossdoc）
合并结果：**34 条问题** = 2 Critical + 11 High + 10 Medium + 11 Low（workflow 结果）∪ 主循环确定性核验（CrossRef 逐条验真 + Table 1 与 `tier1_v2.json` 交叉比对）

> 说明：workflow 的 `numbers` 维度因结构化输出重试超限未返回，本报告的「数字一致性」由主循环确定性核验补齐（已覆盖 Table 1 全表 + 稀疏边界全部数字）。

---

## 0. 已核验「一致」的部分（避免误伤，先给出干净项）

以下数字经与 `results/raw/tier1_v2.json`、`tier2_tau2_v2.json`、`tier3_noise_v2.json` 逐项比对，**正文与数据一致，无需改动**：

- **Table 1（主对比表）全部 18 个 cell**（RMSE / R² / PICP，6 方法 × 3 目标）与 `tier1_v2.json` 均值一致（正文取 2 位小数舍入）。例：TSK-LS Cooling R²=0.94（raw 0.937）；TSK-SpikeSlab-BIC Concrete R²=-6.0（raw -6.003）；Gibbs PICP=0.95（raw 0.954）。
- **稀疏边界全部数字**：τ²=0.1 → R²≈-5.4（raw -5.30）；τ²=100 → 0.92 vs 0.94（raw 0.92 vs 0.937）；噪声 0→30 → 0.93→0.88（raw 0.932→0.875）。
- **MPIW "≈6.7–32.9"**（§Calibration）：与 raw 的 Heating 6.6–6.8 → Concrete 32.0–32.9 一致（但该数字只出现在正文、未进任何表，见 Low 类）。
- **cover letter "References: 19"**：与 manuscript.tex 中 19 个唯一 `\cite` key 一致（正确，非错误）。

---

## 1. 分级问题清单（定位 → 证据 → 为什么 → 修法）

### 🔴 Critical（2 条，会导致 desk-reject / 致命矛盾）

#### C1 · 核心方法细节自相矛盾：`spread factor s=1.5` vs `per-cluster standard deviation`
- **定位**：manuscript.tex §Setup(156) vs §Method eq:membership(89)、Algorithm 1(102)、§Bug(94)
- **证据**：L156 写「Gaussian membership **spread factor $s=1.5$**」；L89 写「spreads $s_{ji}$ **estimated from the training points assigned to each cluster**」；L102 写「per-cluster **standard deviations** from training points」。常数 `s=1.5` 与「逐簇标准差」在数学上互斥。
- **为什么**：这是论文**最核心的模型规格**。审稿人无法判断 $s_{ji}$ 到底是常数 1.5 还是逐簇标准差 → 头条结果按描述无法复现，属致命矛盾。
- **修法**：统一为一条规则，例如「$s_{ji} = 1.5 \times \sigma_{\text{cluster},i}$（逐簇标准差 × 尺度因子 1.5）」，并同步改 eq:membership / Algorithm 1 / §Bug；或删掉因子、只保留「逐簇标准差」。（需回到源码 `src/tsk_core.py` 确认真实实现是哪一种，再改文字。）

#### C2 · supplementary 声明错误期刊 + 过期标题（= Seed K1）
- **定位**：supplementary.tex L10（`\journal{Applied Soft Computing}`）、L15（标题「Sparse Bayesian TSK … for Building Energy Prediction」）；references.bib L1 注释同旧题
- **证据**：正文标题（manuscript L19）是「Correct and Calibrated Bayesian Inference for **Takagi--Sugeno--Kang** Fuzzy Systems…」，投稿信（cover_letter L12）面向 Information Sciences。supplementary 却声明 Applied Soft Computing + 旧标题。
- **为什么**：supplementary 署名错误的期刊与完全不相关的旧标题，是 desk-reject / 学术诚信红线——等于告诉编辑「转投稿包没更新」。
- **修法**：`\journal{Information Sciences}`（或删期刊行用期刊模板）+ 改 supplementary 标题为正文标题的「Supplementary Material for …」+ 改 references.bib 头注释。

### 🟠 High（11 条，显著降低录用概率）

#### H1 · 统计等价性声明，全文零统计检验（= Seed K4）
- **定位**：manuscript.tex L179「statistically indistinguishable」「within sampling noise」、L183 表 caption「within sampling noise」、L214「within sampling error」
- **证据**：全文 grep `wilcoxon|p-value|p<|significan|demsar|t-test|paired` 为空；bib 里 `demsar2006statistical`、`wilcoxon1945individual` 存在但**从未被引用**；仓库里还躺着一张 `fig5_cd_diagram`（Nemenyi CD 图）却未用于正文。
- **为什么**：INS 方法论期刊对「不可区分/噪声内」这类形式化等价声明，审稿人必要求 Wilcoxon/t 检验 + p 值。
- **修法**：在 30 splits 上跑 paired Wilcoxon signed-rank 报 p 值并引 `wilcoxon1945individual`/`demsar2006statistical`；或把措辞降级为纯描述性（「均值差 < 一个标准差」）。

#### H2 · Highlights PICP "0.92–0.95" 与正文 "0.94–0.95" 矛盾（= Seed K3 主项）
- **定位**：highlights.tex L20 vs manuscript.tex L27/44/214/263、cover_letter.tex L22
- **证据**：Highlights 写「PICP $=0.92$–$0.95$」，正文/投稿信一律 0.94–0.95（raw 数据 0.935–0.954）。
- **为什么**：Elsevier Highlights 是编辑第一眼看到的页面，数字与摘要不一致 = 硬伤。
- **修法**：Highlights 改「0.94–0.95」；同时每条 Highlights 需 ≤85 字符（当前每条均超，见 P1 格式项）。

#### H3 · 贡献 #1 的改进幅度 "+0.30 to +0.53" 数字错误（应为 +0.10 to +0.53）
- **定位**：manuscript.tex L48
- **证据**：L48 写「$R^2$ improvements of $+0.30$ to $+0.53$」；但 §Repro(L167) 给出的 6 个改进是 +0.53 / +0.40 / +0.30 / **+0.14** / **+0.10** / **+0.24**。真实下界是 **+0.10**（0.87→0.97），不是 +0.30。
- **为什么**：摘要/贡献段与 Results 表数字直接矛盾，且是「三贡献」之一的关键数字。
- **修法**：改「$+0.10$ to $+0.53$」，并核实「on three benchmarks」措辞（见 H4）。

#### H4 · "three UCI regression benchmarks" 实为 2 个数据集
- **定位**：manuscript.tex L156（§Setup）、L48（「on three benchmarks」）
- **证据**：L156 写「three UCI regression benchmarks」，但只列出 Energy Efficiency（2 目标）与 Concrete（1 目标）= **2 个数据集、3 个 target**。L48 的「on three benchmarks」同源。
- **为什么**：「3 个 benchmark」的模糊表述掩盖了验证规模单薄（正文仅 2 数据集，Facebook/Air Quality 已被删），INS 审稿人会追问验证规模。
- **修法**：改为「two UCI datasets (three regression targets)」，全稿统一，贡献 #1 的「three benchmarks」改为「three targets」。

#### H5 · "six orders of magnitude" 与实际 τ² 网格矛盾（实为 3 个数量级）
- **定位**：manuscript.tex L232（§Sparsity Boundary）
- **证据**：L232 写「over **six** orders of magnitude」；但 `tier2_tau2_v2.json` 的 key 是 {0.1, 0.3, 1, 3, 10, 100}（$10^{-1}\sim10^2$ = **3 个数量级**，6 个取值），`src/experiment_v2.py` 硬编码该列表。「six」是旧 supplementary τ² 表（$10^0\sim10^6$）的残留。
- **为什么**：文字与图 x 轴（0.1–100）直接冲突，审稿人对图一眼即穿。
- **修法**：改「three orders of magnitude」或「six settings（$0.1\sim100$）」。

#### H6 · "widely-copied bug" 无任何出处（= Seed K6）
- **定位**：manuscript.tex L40、L94；cover_letter.tex L24
- **证据**：L40「a **common** implementation」「a **widely-copied** TSK code pattern」；L94「A common implementation」；cover letter「this code pattern is **widely copied**」。全文无任何引用指向具体论文/代码库。
- **为什么**：可复现性论文的贡献 #1 全建立在这个 bug 的存在上，「widely-copied」无出处 = 不可验证的强声明。
- **修法**：给出具体源码/论文出处；否则软化为「an implementation pattern we encountered in our reproduction」并删「widely-copied」。

#### H7 · 被引文献 `jantre2025spike` DOI 失效（CrossRef 404）
- **定位**：references.bib（`jantre2025spike`，正文 L65 已引）
- **证据**：bib DOI `10.1109/TNNLS.2024.3488592` → CrossRef **404**；正确 DOI 为 `10.1109/TNNLS.2024.3485529`（作者 Jantre, IEEE TNNLS, 2025, vol 36, iss 6, pp 11176–11188，元数据一致，仅 DOI 串错位）。
- **为什么**：**被引**参考文献带失效 DOI，审稿人点链接即失败。
- **修法**：DOI 改为 `10.1109/TNNLS.2024.3485529`。

#### H8 · 被引文献 `neuralnet2024sparsetsk` DOI 指向错误论文（作者/卷号不符）
- **定位**：references.bib（`neuralnet2024sparsetsk`，正文 L65 已引）
- **证据**：bib 写「Chen, Xiaogang … vol **179**」；CrossRef 返回该 DOI `10.1016/j.neunet.2024.106600` 的论文作者为 **Liu**、卷号 **180**——DOI 指向了另一篇不相关的论文。
- **为什么**：**被引**文献元数据错误（作者+卷号），是学术诚信/引用验真红线。
- **修法**：用 CrossRef 按标题「Convergence Analysis of Sparse TSK Fuzzy Systems…」重新查正确 DOI/卷/页，或核对该论文真实出处。

#### H9 · 方法名 `TSK-SpikeSlab-BIC` 与代码名 `SpikeSlab-Fast` 未对应
- **定位**：manuscript.tex L158/194 vs `tier1_v2.json`（key `SpikeSlab-Fast`）
- **证据**：正文方法名是 TSK-SpikeSlab-BIC，但发布的结果 JSON 用 `SpikeSlab-Fast`，全稿无任何映射说明。
- **为什么**：可复现产物无法与论文方法表对应，「Fast」一词全文无定义。
- **修法**：统一命名（JSON key 改为 TSK-SpikeSlab-BIC，或 README/Data Availability 给出映射）。

#### H10 · supplementary 残留 5 处与正文冲突的旧内容（TSK-LASSO / TSK-SpikeSlab 歧义 / Facebook / Air Quality / τ² 表）
- **定位**：supplementary.tex L33/44-46/90/99（TSK-LASSO）、L34/91（TSK-SpikeSlab 歧义）、L30/76-99（Facebook Metrics + Air Quality）、L52-72（τ² 表 $10^0\sim10^6$）
- **证据**：正文方法表（L158）只有 4 方法 + SSVS，无 TSK-LASSO；正文只评估 2 数据集；正文稀疏边界是 coefficient-level SSVS（τ²=0.1→R²=-5.4），supplementary τ² 表却是 rule-level、RMSE 恒 20.55、PICP 0.000–0.227——两套数字不可调和。
- **为什么**：supplementary 呈现的是正文从未介绍的第 5 个方法 + 4 个数据集 + 一套与正文矛盾的消融，属「旧版残留」的系统性表现（Seed K1 的展开）。
- **修法**：删 TSK-LASSO 行与「Extended TSK-LASSO Diagnostic」节；`TSK-SpikeSlab` 改精确名（BIC 或 Gibbs）；删 Facebook/Air Quality 列与 Air Quality 节；τ² 表换成正文实际使用的 coefficient-level SSVS（0.1–100，报 R²/PICP/MPIW）。

#### H11 · 贡献 #1 "every TSK baseline" / "depressed every baseline" 仅对 TSK-LS 验证
- **定位**：manuscript.tex L48「depressed **every** TSK baseline」、L40
- **证据**：改进幅度（+0.10～+0.53）里 Bayesian-TSK 的改进（+0.10～+0.24）远小于 TSK-LS（+0.30～+0.53），且「every」语气过强；H3 的数字错误叠加放大此问题。
- **为什么**：强断言「every baseline depressed」与数据里 Bayesian-TSK 仅 +0.10 的温和改进不完全匹配。
- **修法**：与 H3 合并修——精确数字 + 弱化「every」为「all dense TSK baselines, to varying degrees」。

---

## 2. 数字对照表（正文 vs 原始数据）

| 来源位置 | 正文数字 | raw 数据 | 判定 |
|----------|----------|----------|------|
| Table 1 · TSK-LS Heating R² | 0.97 | 0.971 | ✅ |
| Table 1 · TSK-LS Cooling R² | 0.94 | 0.937 | ✅（舍入） |
| Table 1 · TSK-LS Concrete R² | 0.74 | 0.738 | ✅（舍入） |
| Table 1 · BIC R²（3 目标） | -1.8/-3.1/-6.0 | -1.810/-3.075/-6.003 | ✅ |
| Table 1 · Gibbs PICP | 0.95/0.94/0.95 | 0.952/0.936/0.954 | ✅ |
| Table 1 · RF R² Concrete | 0.90 | 0.903 | ✅ |
| §Sparsity τ²=0.1→R² | -5.4 | -5.30 | ✅ |
| §Sparsity τ²=100→R² | 0.92 vs 0.94 | 0.92 vs 0.937 | ✅ |
| §Sparsity 噪声 0→30 | 0.93→0.88 | 0.932→0.875 | ✅ |
| §Calibration MPIW | 6.7–32.9 | 6.6–32.9 | ✅（但未进表） |
| **Abstract/结论 PICP** | 0.94–0.95 | 0.935–0.954 | ✅ |
| **Highlights PICP** | **0.92–0.95** | — | ❌ **H2** |
| **贡献#1 改进幅度** | **+0.30 to +0.53** | +0.10～+0.53 | ❌ **H3** |
| **§Sparsity τ² 范围** | **six orders** | 3 orders | ❌ **H5** |

---

## 3. 声明-证据矩阵（节选，High 及以上已在上表列出）

| 声明 | 位置 | 支撑 | 判定 |
|------|------|------|------|
| "dense baselines are strong" | L179 | RF 全面碾压 TSK（Concrete 0.90 vs 0.74） | ⚠️ Medium：过强，未承认 RF/SVR 占优 |
| "no free lunch"（系数级） | L232/50 | 仅 Energy-Cooling 单目标验证 | ⚠️ Medium：单目标推广到「domain」 |
| "first exact Bayesian inference … in TSK" | cover_letter L20 | 正文未作此「first」声明 | ⚠️ Medium：投稿信 priority claim 无正文支撑 |
| "at comparable interval width" | L44 | Concrete 上近似法区间约 2× 宽 | ⚠️ Low：不准确 |

---

## 4. 术语一致性表

| 概念 | 正文 | supplementary | 代码/数据 | 判定 |
|------|------|---------------|-----------|------|
| BIC 近似法 | TSK-SpikeSlab-BIC | TSK-SpikeSlab | `SpikeSlab-Fast` | ❌ 三处不同名（H9） |
| 系数级稀疏 | TSK-SSVS | — | `SSVS-Gibbs` | ⚠️ Medium |
| Gibbs 法 | TSK-SpikeSlab-Gibbs | — | `SpikeSlab-Gibbs` | ⚠️ Medium |
| LASSO 法 | 无（仅相关文献） | TSK-LASSO | — | ❌ H10 |
| Concrete 数据集 | Concrete Compressive Strength | Concrete CS | `Concrete` | ⚠️ Medium |
| Energy 目标 | Energy Heating/Cooling | Energy (Heating)/Energy-Cooling | `Energy-Heating`/`Energy-Cooling` | ⚠️ Low（标点/连字符） |
| fuzzy c-means | `fuzzy c-means` 与 `fuzzy $c$-means` 混用 | — | — | ⚠️ Low（$c$ 排版） |
| 高斯 spread | **spread factor s=1.5** vs **per-cluster std** | — | 待查 `tsk_core.py` | ❌ **C1 Critical** |

---

## 5. 引用验真表（CrossRef，40 条）

- **被引但 DOI 错误（High，须立即修）**：`jantre2025spike`（DOI 失效，见 H7）、`neuralnet2024sparsetsk`（DOI 指向错误论文，见 H8）。
- **supplementary 引用但 DOI 错误（Medium）**：`deveaud2014accurate`（DOI 指向一篇无关的 "Kim" 论文，pages 421-428；应改回 De Vito 等人 Air Quality 正确出处，且该条目随 Air Quality 节删除）。
- **未引条目中的小瑕疵（Low，随删除消解）**：`xue2023dgaletsk` pages 3852-3866→实 3866-3880；`raftery1995bayesian`/`wilcoxon1945individual` pages 末页缺；`demsar2006statistical` 的 DBLP DOI `10.5555/...` 无法解析（JMLR 2006 本无 DOI，应改 URL 或删）。
- **验真为正确（含 Seed K8 的两条「可疑」项）**：
  - `gong2026beliefrule`：DOI 真实存在（Applied Soft Computing, 2026, vol 199, pp 115383）→ **Seed K8 的怀疑可撤销**，该条元数据正确（但未被引用，见 K7 删除）。
  - `ieeeaccess2024interpretable`：DOI `10.1109/tfuzz.2025.3600911` 真实（IEEE Trans. Fuzzy Systems, 2025）→ key 名 `ieeeaccess2024` 有误导性，但元数据正确，仅需改 key 名。
- **仅 LaTeX 编码差异（非错误，无需改）**：`denoeux`（\oe）、`rockova`（\v{c}）、`bezdek`（\&）——CrossRef 对比时出现的差异均为重音/转义字符，非真实错误。

---

## 6. 未引用 bib 条目清单（= Seed K7，20 条，随正文引用策略决定删除/补引）

`amasyali2018review`、`rockova2018spikeslab`、`cui2021curse`、`moayedi2022feasibility`、`mdpi2022buildings`、`fabunmi2024anfis`、`asoc2024deepfuzzy`、`asoc2025fuzzycognitive`、`asoc2025fuzzybigdata`、`moro2016predicting`、`raftery1995bayesian`、`gelman2013bayesian`、`blei2017variational`、`bian2025mhtsk`、`xue2023dgaletsk`、`pan2024threetsk`、`gong2026beliefrule`、`carvalho2010horseshoe`、`demsar2006statistical`、`wilcoxon1945individual`。

> 注意：`bian2025mhtsk`、`xue2023dgaletsk` 是高维 TSK 基线文献（Seed K2/K5 建议在 Discussion 补引）；`demsar2006`/`wilcoxon1945` 应随 H1 补检验后转为引用。

---

## 7. 图片-文字一致性

- 正文 4 图（fig1_repro_fix / fig2_main_comparison / fig3_calibration / fig4_sparsity_boundary）均被 `\includegraphics` 正确引用，caption 与正文数字一致。
- **孤儿图 14 个文件**（旧图族 7 名 × pdf/png）：`fig1_main_comparison`、`fig2_uncertainty`、`fig3_mechanism`、`fig4_fcm_sensitivity`、`fig5_cd_diagram`、`fig6_rules`、`fig7_pareto`——均未被任何 tex 引用，属旧版残留（Medium，投稿前须删，否则混入 artifact 包）。
- **fig5_cd_diagram 尤其关键**：CD 图（Nemenyi 显著性检验）已生成却未用于正文 → 印证 H1「显著性检验做了却未报」。

---

## 8. 结论

Phase 2 审计确认：**正文 Table 1 与全部稀疏边界数字与原始数据一致**（可信），但存在 **2 个 Critical**（核心方法规格自相矛盾 + supplementary 旧版残留）与 **11 个 High**（统计检验缺失、Highlights/贡献段数字矛盾、2 条被引文献 DOI 错误、widely-copied 无出处、代码-正文命名脱节、supplementary 5 处旧内容）。Critical/High 清单见下方待确认列表。
