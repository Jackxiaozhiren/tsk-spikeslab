# Information Sciences (Elsevier) 转投稿 · 论文缺陷审查与整体优化主 Prompt

> **用途**：把本文件整体（或分阶段）喂给 Claude Code（建议开启 ultracode / workflow 多智能体编排），对当前 TSK 论文做一次面向 *Information Sciences*（Elsevier）的「缺陷审查 + 整体优化」。
> **使用方式**：可直接粘贴全文，或按 `Phase 0 → Phase 10` 逐段执行；每个 Phase 都标注了应调用的本地 Skill 名。
> **最终交付**：一份分级问题清单（Critical/High/Medium/Low）+ 逐项修订方案 + 修订后的稿件产物。

---

## 一、背景与目标（Context，请先读入）

### 1. 论文现状
- 当前论文标题：**Correct and Calibrated Bayesian Inference for Takagi–Sugeno–Kang Fuzzy Systems: a Reproducibility Fix and Model-Averaged Prediction Intervals**。
- 核心主张（三贡献）：
  1. **可复现性修复**：发现并修复 membership-function bug（训练/推理时模糊隶属度 spread 不一致），把稠密 TSK-LS 的 $R^2$ 从 0.41 拉到 0.94。
  2. **校准的模型平均区间**：用 block-Gibbs 采样 spike-and-slab 先验 + Bayesian Model Averaging（BMA）替代失败的 BIC+Laplace 解析近似，恢复校准（PICP 0.94–0.95 vs 近似法的 0.00–0.18）。
  3. **稀疏性边界刻画**：在低维 building-energy（$d=8$）上，规则级/系数级稀疏都不优于稠密基线（稀疏无免费午餐），把贡献从"稀疏选择"重定位为"正确推理"。
- 历史包袱（必须记住）：本文曾被 **Applied Soft Computing 直接拒稿（desk reject）**，根因是负结果叙事 + 学术诚信问题（membership bug、FCM 实为 KMeans、Facebook 数据描述错误）。现已重写，但**遗留了大量旧版本残留**（见下方"已知问题清单"）。

### 2. 目标期刊 Information Sciences（Elsevier）硬性要求（来自联网检索）
- **范围（Scope，最关键）**：必须是一般性 informatics / computational intelligence 贡献，**不是**"把已知方法套用到单一数据集"的窄应用。
- **理论+实验平衡**：只讲理论或只讲实验都会被拒，必须方法论贡献 + 实证验证并重。
- **范围路由红线**：纯数据工程 → IEEE TKDE；软计算 → Applied Soft Computing / IEEE Trans. Fuzzy Systems；神经网络架构 → Neurocomputing；纯应用 → Expert Systems with Applications。**TSK 模糊回归天然偏"软计算"，这是转投 INS 的头号 desk-reject 风险，必须显式论证为什么属于"一般性 informatics"贡献。**
- **审稿人最看重的硬指标**：
  1. 抽象+引言**第一眼**就要让"更一般的贡献"可见，不能只靠一个数据集。
  2. **消融实验**必须隔离出"哪一部分带来增益"。
  3. 基线必须**新且具竞争力**。
  4. **可复现产物**（代码、数据、随机种子）必须"已经给出"，不能"承诺以后给"。
  5. 英文质量差 → 直接 desk 退回。
- **投稿包完整性**（缺一项即可能被退回）：Cover letter、Highlights、Data availability 声明、Competing interest 声明、CRediT 作者贡献、ORCID、建议审稿人、Editorial Manager 排版终校。
- **Elsevier 通用格式红线**：Highlights 每条 **≤85 字符（含空格）**，3–5 条；Abstract 一般 ≤250 词；参考文献编号制（elsarticle-num）；作者用 elsarticle 文档类。
- **指标参考**（以期刊官网实时为准）：IF≈6.8、CiteScore≈14.4，JCR Q1。

---

## 二、已知问题清单（Seed Issues —— 启动审查前先读，逐条核实，勿漏）

以下是我在初读稿件时**已经发现**的问题，作为审查的"种子"，每个 Phase 都要回来核对是否已闭环：

| # | 级别 | 问题 | 证据位置 |
|---|------|------|----------|
| K1 | **Critical** | **`supplementary.tex` 完全是旧版本残留**：标题仍是 "Sparse Bayesian TSK … for Building Energy Prediction"，仍含 TSK-LASSO、Facebook Metrics、Air Quality 等已从新正文删除的内容，数字与正文严重矛盾。 | [supplementary.tex](supplementary.tex) |
| K2 | **Critical** | **正文只有 2 个数据集**（Energy 双目标 + Concrete）。Facebook、Air Quality 被删除后，验证规模对 INS 偏薄，且 Supplementary 里还留着旧 Facebook/Air Quality 表未清理。 | [manuscript.tex](manuscript.tex) §5 |
| K3 | **High** | **Highlights 每条远超 85 字符**（Elsevier 红线），且与 Abstract 数字不一致：Highlights 写 PICP "0.92–0.95"，Abstract 写 "0.94–0.95"。 | [highlights.tex](highlights.tex) |
| K4 | **High** | **无统计显著性检验**：正文多次写 "within sampling noise" / "statistically indistinguishable"，但从未报 Wilcoxon/p 值/置信区间，而 [references.bib](references.bib) 里却有 `demsar2006`、`wilcoxon1945` 未用。INS 要求严谨消融。 | [manuscript.tex](manuscript.tex) §6 |
| K5 | **High** | **范围定位风险**：标题/贡献用 "Reproducibility Fix + 负结果（稀疏无免费午餐）" 作为卖点，是典型的"软计算/单领域"叙事，直接踩 INS 的 scope 红线。需把"精确 Gibbs+BMA 贝叶斯 TSK 推断"作为方法论主贡献。 | 全稿 |
| K6 | **High** | **"widely-copied bug" 无归属**：正文说"一种被广泛复制的实现错误"，但未引用任何具体来源（论文/代码库）。要么给出确凿出处，要么软化为"我们在复现中发现的实现陷阱"。 | §1、§3.2 |
| K7 | **Medium** | **`references.bib` 有约 20 条未在正文引用的残留条目**（deveaud、moro、moayedi、mdpi、fabunmi、asoc2024/2025×3、cui、amasyali、rockova、raftery、gelman、blei、bian、xue、pan、gong、carvalho、demsar、wilcoxon）。需删除或补引。 | [references.bib](references.bib) |
| K8 | **Medium** | **疑似可疑引用**：`gong2026beliefrule` 标 year 2026、vol 199、Applied Soft Computing；`ieeeaccess2024interpretable` 的 key 是 ieeeaccess 但 journal 写 IEEE Trans. Fuzzy Systems、year 2025。必须用 CrossRef/Semantic Scholar 逐条验真（DOI、卷、页、年、作者）。 | [references.bib](references.bib) |
| K9 | **Medium** | **Cover letter 缺失/过期**：`cover_letter.md` 已被删（git 显示 D），现有 `cover_letter.tex/pdf` 是旧版。需重写面向 INS 的 cover letter。 | git status |
| K10 | **Low** | 标题含 "Reproducibility Fix" 词，第一眼压低贡献预期；单作者 + 无基金 + 单一机构，需在 cover letter 中正面处理。 | 全稿 |

> ⚠️ **执行硬约束**：任何 Phase 的结论都必须"回到 Seed Issues 表逐条打钩闭环"。未闭环的 Critical/High 项，优化报告必须显式说明"仍待处理"。

---

## 三、主 Prompt 正文（Phase 0–10）

> 每个 Phase 标注 **调用 Skill**（用 `Skill` 工具按名调用）与 **输出物**。可并行执行的 Phase 已在括号内标注 `[可并行]`。

---

### Phase 0 · 环境与基线快照（前置，10 分钟）

**目标**：先摸清全部文件，建立"当前真实状态"快照，避免在旧文件上做无用功。

**调用 Skill**：无（用 Read/Grep/Glob 直接扫）。

**执行动作**：
1. 列出仓库所有 `.tex` / `.bib` / `results/` / `src/` 文件及修改时间。
2. 用 `git status` + `git log --oneline -5` 确认哪些文件是旧版残留、哪些已更新。
3. 通读 `manuscript.tex`、`supplementary.tex`、`highlights.tex`、`cover_letter.tex`、`references.bib` 五件套，**交叉比对**：标题、方法名、数据集、数字是否一致。
4. 确认所有 Figure（`results/figures/fig*.pdf`）是否被正文实际引用、文件名与 `\includegraphics` 是否对应（当前 fig1_repro_fix / fig2_main_comparison / fig3_calibration / fig4_sparsity_boundary 是否与旧 fig1_main_comparison 等冲突）。

**输出**：`状态快照.md`（文件清单 + 五件套一致性矩阵 + 已引用/未引用图表清单）。

---

### Phase 1 · 期刊合规审查（Scope + 格式 + 投稿包）`[可并行]`

**调用 Skill**：`ccf-submission-checker`、`ppw-cover-letter`（后期）、`nature-data`（数据可用性）。

**执行动作**：
1. **Scope fit 论证（最高优先级）**：写一段"为什么本文属于 Information Sciences 而非 Applied Soft Computing / IEEE TFS"的定位论证，要求：
   - 强调**方法论贡献是通用的**：精确 Gibbs + BMA 的贝叶斯推断框架不限于 TSK / 建筑能耗，可迁移到任何"线性 consequent + 后件先验选择"的模型族；
   - 把"可复现性修复"降格为**支撑性实证案例**，把"校准的不确定性量化 + 模型选择后验推断"升格为**主线**；
   - 明确本文提供的是一般性 informatics 贡献（不确定性量化方法论），而非单一领域软计算应用。
2. **格式合规**：
   - 改用 `elsarticle` 文档类（`\documentclass[review,1p,times]{elsarticle}` + `\journal{Information Sciences}`）；
   - Highlights 重写为 **3–5 条、每条 ≤85 字符**；
   - Abstract ≤250 词；Keywords 5–6 个（增加 "uncertainty quantification / prediction intervals / Bayesian model selection" 等 INS 高频词）；
   - 参考文献编号制、作者 ORCID、CRediT 单作者声明。
3. **投稿包核对**：Cover letter / Highlights / Data availability / Competing interest / CRediT / ORCID / 建议审稿人 七项，逐项列出"已具备/缺失"。

**输出**：`合规清单.md` + Scope 定位论证段落 + 修订后的 highlights 草稿。

---

### Phase 2 · 学术诚信与一致性审计 `[可并行]`

**调用 Skill**：`ccf-integrity-auditor`、`ppw-logic`。

**执行动作**：
1. **数字一致性**：把 Abstract / Introduction / Results 表 / 图 caption / Highlights / Supplementary 里**每一个数字**（$R^2$、PICP、MPIW、RMSE、$n$、$d$、$R$、$\tau^2$、30 splits）抽出来建表，逐一核对是否自洽。重点核对 Seed K1/K3。
2. **声明-证据对齐**：逐条把正文的"强声明"（如"every TSK baseline depressed"、"PICP≈0"、"no free lunch"）对到对应的表/图，标出**过强、无支撑、或与数据不符**的表述。
3. **术语一致性**：TSK-LS / Bayesian-TSK / TSK-SpikeSlab-BIC / TSK-SpikeSlab-Gibbs / TSK-SSVS 全稿命名统一；"fuzzy c-means" vs "KMeans" 不得再混用（历史事故）。
4. **引用验真**：对 `references.bib` **每一条**（尤其 Seed K8 的可疑项）用 CrossRef / Semantic Scholar 核验 DOI、作者、卷、页、年；列出"DOI 不存在/信息不符/查无此文"的条目。标记"未在正文引用的 bib 条目"（Seed K7）。
5. **图片-文字一致性**：每张图的 caption 是否准确反映图内容与正文引用处的数字。

**输出**：`一致性审计.md`（含：数字对照表、声明-证据矩阵、术语表、引用验真表、未引用条目清单）。

---

### Phase 3 · 科学性与方法严谨性审查 `[可并行]`

**调用 Skill**：`ccf-paper-reviewer`、`ppw-reviewer-simulation`（多角色：方法审稿人 + 贝叶斯统计专家 + 模糊系统专家）。

**执行动作**（三角色分头审，再合并）：
1. **方法审稿人**：Gibbs 采样器推导（Eq. gamma、Woodbury/matrix-determinant 复杂度 $\mathcal{O}(n(d+1)^2)$）是否正确？BMA 方差分解（Eq. bma 的总方差定律）是否正确？超参数（$\pi$、$\tau^2$、burn-in、retained draws、seed）是否交代清楚？
2. **贝叶斯统计专家**：spike-and-slab 先验设置、conjugate 基线作为 sampler 正确性校验（"all rules active must recover closed form"）是否严谨？是否该报收敛诊断（trace/R-hat）？PICP 是否该给置信区间而非点估计？
3. **模糊系统专家**：FCM（$m=2$、$s=1.5$、$R=5$）选择依据？"spread factor $s=1.5$" 与正文"per-cluster standard deviation"是否矛盾？是否遗漏了更近期的高维 TSK 基线（如 bian2025mhtsk、xue2023dgaletsk 已在 bib 里却未用作基线）？
4. **统计显著性（补 K4）**：为"within sampling noise / indistinguishable"补上 **Wilcoxon signed-rank / paired t-test + 多重比较校正（Nemenyi/CD 图，用 demsar2006）**，或明确改为"无显著差异（$p>\cdots$）"。
5. **消融完整性（INS 硬要求）**：补消融表，隔离"Gibbs vs BIC-threshold vs Laplace"每一步的独立贡献；$\tau^2$ 敏感性（已在旧 supplementary，需迁移并更新为新方法版本）；规则数 $R$ 敏感性；burn-in/draws 敏感性。
6. **可复现性**：核对 `src/` 里 `tsk_core.py`（修正后核心）、`experiment_v2.py`、`figures_v2.py` 是否与论文数字一致；seed 是否写死；是否附 `requirements.txt`/环境说明。

**输出**：`科学性审查.md`（三角色意见合并 + 严重度分级 + 逐项可执行修订建议 + 补充实验清单）。

---

### Phase 4 · 定位与叙事重构（针对 INS 的 Story 重写）`[可并行]`

**调用 Skill**：`ccf-paper-writer`、`ml-paper-writing`、`ccf-idea-optimizer`（用于提炼主贡献句）。

**执行动作**：
1. 重写 **Abstract**（用 `ppw-abstract` 的 Farquhar 五句式：背景→问题→方法→结果→意义），把主线从"我们修了个 bug + 稀疏没用"改为"**我们给出精确、校准的贝叶斯 TSK 推断框架，并以一个可复现性案例和一组稀疏性边界实验来实证它**"。
2. 重写 **Introduction 的贡献三点**：贡献 1 降级为"实证案例"，新增/强化"通用 Gibbs+BMA 推断方法论"为贡献 1。
3. 重写 **标题**候选（3–5 个），去掉/弱化 "Reproducibility Fix"，突出 "exact Bayesian inference / calibrated prediction intervals / spike-and-slab / model averaging"。给出每个标题的取舍理由。
4. 重写 **Discussion 的 "Implications"**：把"稀疏无免费午餐"从"结论"改写成"边界条件 + 何时稀疏值得"（正向、建设性），并明确"本文框架在 $d>30$ 高维场景的迁移路径"作为 future work 亮点。
5. 处理 Seed K6：为 bug 声明补上**具体出处**（若能找到源码/论文），否则改写为"我们在复现某已发表基线时发现"的诚实措辞，并说明该 bug 的可迁移警示价值。

**输出**：`重写稿`（新标题候选 + 新 Abstract + 新贡献段 + 新 Discussion 段落，可直接替换）。

---

### Phase 5 · 文献补强与引用核验 `[可并行]`

**调用 Skill**：`ppw-literature`（Semantic Scholar）、`ccf-literature-searcher`、`nature-citation`。

**执行动作**：
1. 补检索 **2024–2026** 的最新相关文献，方向：
   - Bayesian TSK / fuzzy 不确定性量化；
   - spike-and-slab / 连续收缩先验（horseshoe、SSVS）在神经网络/高维回归的最新应用；
   - 预测区间校准（conformal prediction 与贝叶斯的对比，是否需回应）。
2. 为正文关键声明补**分段引用**（每 2–3 句一个可引观点），消除"整段无引用"。
3. 把 bib 里**已有的**高维 TSK 文献（`bian2025mhtsk`、`xue2023dgaletsk`）纳入 Related Work 并在 Discussion 中作为高维基线对比，增强"一般性贡献"观感。
4. 清理未引用条目（Seed K7）+ 修正/删除可疑条目（Seed K8）。

**输出**：`文献补强.md`（新增候选文献 BibTeX + 建议插入位置 + 已清理/修正的条目清单）。

---

### Phase 6 · 写作润色与去 AI 化 `[可并行]`

**调用 Skill**：`ppw-polish`（快速修复或多轮 guided）、`ppw-de-ai`（降 AI 痕迹）、`nature-polishing`（可选，Nature 级句法）、`ppw-team`（若想按章节并行：introduction / method / results / discussion 分别派 subagent）。

**执行动作**：
1. 全稿英文学术润色，目标期刊语域（Elsevier / informatics，客观、克制、不夸张）。
2. 跑 `ppw-de-ai` 两阶段：扫描 AI 高风险句（如过度对称的排比、套路化转折、模板化"we make three contributions"），批量改写为有信息量的学术表达。
3. 统一时态/语态/术语；消除"we"滥用；检查公式编号、交叉引用 `\ref`/`\cite` 无断链。

**输出**：润色后的 `manuscript.tex`（含改动 diff / 变更追踪说明）。

---

### Phase 7 · 摘要 / 标题 / Highlights / 图表标题精修 `[可并行]`

**调用 Skill**：`ppw-abstract`、`ppw-caption`、`ppw-visualization`。

**执行动作**：
1. `ppw-abstract`：按 Farquhar 公式重写摘要，标注五句各自功能，给出"带标注版 + 干净投稿版"。
2. `ppw-caption`：逐图/逐表重写 caption，要求"自足"（读者不看正文也能懂：实验设置 + 关键数字 + 结论方向），并核对与正文数字一致（Seed K3 类问题清零）。
3. `ppw-visualization`：检查每张图的图表类型选择是否最优（$R^2$ 对比→分组柱状/点图；$\tau^2$ 敏感性→折线；PICP→点+95%参考线；稀疏边界→双面板）。给改进建议。

**输出**：新 Abstract（双版）+ 新 caption 集 + 图表类型建议。

---

### Phase 8 · 图表质量与复现 `[可并行]`

**调用 Skill**：`academic-plotting` / `nature-figure`（若需重绘）、`ppw-visualization`。

**执行动作**：
1. 打开 `results/figures/fig*.pdf` 逐一检查：分辨率、字体大小、图例、坐标轴标签、色盲友好配色、误差棒。
2. 核对图内数字与正文表完全一致（尤其 fig1_repro_fix 的 0.41→0.94、fig3_calibration 的 PICP）。
3. 若 Supplementary 重做（清理 K1），同步重绘/删除对应的旧图，确保 `results/figures/` 目录里没有孤儿图。

**输出**：图表问题清单 + 需重绘图清单 + 修订版图（如执行重绘）。

---

### Phase 9 · 投稿包生成（Cover letter + 数据/伦理声明 + 审稿人建议）

**调用 Skill**：`ppw-cover-letter`、`nature-data`、`nature-response`（应对"此前被 ASC 拒稿"的说明策略）。

**执行动作**：
1. 生成面向 INS 的 **Cover letter**，必须包含：
   - 一句话定位本文为"一般性 informatics 贡献（校准的贝叶斯推断 + 不确定性量化），以 TSK 模糊系统为载体"；
   - 与 INS scope 的显式对齐（逐条呼应"理论+实验并重、可复现、消融"）；
   - 亮点（≤3 条，呼应 Highlights）；
   - Data availability / Code availability / Competing interest / 原创性声明；
   - 是否提及"此前被 Applied Soft Computing 拒稿"——**默认不主动提及**（Elsevier 跨刊通常不需要），若用户要求说明，则给一段诚实、克制的改写。
2. 生成 **Data Availability** 声明（UCI 数据集编号 + GitHub 链接 + 种子）。
3. 生成 **建议审稿人**（3–5 位：来自 bib 中 Bayesian TSK / fuzzy 不确定性量化的作者，附理由）。
4. 生成 **CRediT** 单作者声明。

**输出**：`cover_letter.tex` + 声明文件 + 建议审稿人清单。

---

### Phase 10 · 终审与 Checklist 输出（收口）

**调用 Skill**：`ccf-paper-reviewer`（第二次终审）、`ppw-logic`（最终逻辑链校验）。

**执行动作**：
1. 把 Phase 1–9 的所有修订**合成**到一份干净的 `manuscript.tex` + `supplementary.tex` + `highlights.tex` + `cover_letter.tex`。
2. **回到 Seed Issues 表 K1–K10**，逐条核对是否闭环，输出"已闭环 / 仍待处理"状态。
3. 做最终**逻辑链校验**：Title → Abstract → Contributions → Method → Results → Discussion → Conclusion 是否一条线、无断裂、无数字矛盾。
4. 输出最终报告：**分级问题清单（Critical/High/Medium/Low）→ 逐项修复证据 → 残留风险（如 scope fit 无法 100% 消除）→ 是否建议投 INS 的最终判断**。

**输出**：`最终审查报告.md` + 四件套终稿。

---

## 四、输出规范

1. **所有报告**用 Markdown，放在本仓库根目录下，命名 `INS_review/`（新建目录），文件按 Phase 命名（`P1_合规清单.md` …）。
2. **严重度定义**：
   - **Critical**：会导致 desk-reject / 数据造假 / 致命矛盾（对应 K1、K2 级别）；
   - **High**：显著降低录用概率（K3–K6 级别）；
   - **Medium**：可维护性 / 完整性（K7–K9）；
   - **Low**：风格 / 可选（K10）。
3. **每条问题必须**：`定位（文件:行）→ 证据 → 为什么是问题 → 具体修法（给出可替换的文字/公式/数字）`。
4. **不改动** `results/raw/*.npz` 与 `results/raw/*.json` 的原始数据，除非明确要求重跑实验；重跑必须记录命令与 seed。

---

## 五、附：Phase ↔ Skill 调用速查表

| Phase | 主题 | 调用 Skill |
|-------|------|-----------|
| 0 | 环境快照 | （Read/Grep/Glob） |
| 1 | 期刊合规 | `ccf-submission-checker`, `nature-data` |
| 2 | 诚信与一致性 | `ccf-integrity-auditor`, `ppw-logic` |
| 3 | 科学严谨性 | `ccf-paper-reviewer`, `ppw-reviewer-simulation` |
| 4 | 定位与叙事 | `ccf-paper-writer`, `ml-paper-writing`, `ccf-idea-optimizer`, `ppw-abstract` |
| 5 | 文献补强 | `ppw-literature`, `ccf-literature-searcher`, `nature-citation` |
| 6 | 润色去 AI | `ppw-polish`, `ppw-de-ai`, `nature-polishing`, `ppw-team` |
| 7 | 摘要/标题/图表 | `ppw-abstract`, `ppw-caption`, `ppw-visualization` |
| 8 | 图表复现 | `academic-plotting`/`nature-figure`, `ppw-visualization` |
| 9 | 投稿包 | `ppw-cover-letter`, `nature-data`, `nature-response` |
| 10 | 终审收口 | `ccf-paper-reviewer`, `ppw-logic` |
