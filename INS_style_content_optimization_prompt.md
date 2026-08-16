# Information Sciences (Elsevier) 转投稿 · 期刊风格与内容偏好对齐 + 缺陷优先修复主 Prompt

> **用途**：把本文件整体（或按 Phase 分段）喂给具备「读文件 + 联网检索 + 写文件」能力的 Agent（建议 Claude Opus 长上下文 + 开启 ultracode/workflow 多智能体编排），对当前 TSK 论文做一次**以 *Information Sciences*（Elsevier）的「风格」与「内容偏好」为准绳**的对齐优化。
> **与旧版 `INS_resubmission_prompt.md` 的区别**：旧版重在 scope / 格式 / 投稿包合规（硬规则）；本版**新增一节「INS 风格与内容偏好档案」（§3，联网检索已固化）**，并把执行顺序强制改为——**先检索风格/内容偏好 → 再诊断「风格/内容偏离痛点」→ 优先修复偏离 → 最后整体优化**。
> **执行顺序（不可颠倒）**：`Phase 0 检索 → Phase 1 诊断偏离 → Phase 2 优先修复偏离 → Phase 3 整体优化 → Phase 4 终审收口`。
> **最终交付**：一份「风格/内容偏离痛点清单（分级）+ 逐项修复」+ 对齐后的四件套稿件（manuscript / supplementary / highlights / cover letter）。

---

## 一、背景与目标（先读入）

### 1. 论文现状
- 当前标题：**Correct and Calibrated Bayesian Inference for Takagi–Sugeno–Kang Fuzzy Systems: a Reproducibility Fix and Model-Averaged Prediction Intervals**。
- 方法主线：TSK 模糊回归（FCM 聚类 + 线性后件）+ spike-and-slab 先验 + block-Gibbs 采样 + Bayesian Model Averaging（BMA），得到**校准的 95% 预测区间（PICP≈0.94–0.95）**。
- 三个原贡献：(1) 修复 membership-function bug 的可复现性修复；(2) 校准的 BMA 模型平均区间（替代失败的 BIC+Laplace 解析近似）；(3) 低维下「稀疏无免费午餐」的边界刻画。
- 数据：Energy Efficiency（UCI，双目标）+ Concrete（UCI），均 d=8 低维；30 次 80/20 划分、固定种子。
- **历史包袱（必须记住）**：本文曾被 *Applied Soft Computing* desk-reject（根因：负结果叙事 + 学术诚信问题——membership bug、FCM 实为 KMeans、数据描述错误）。现已重写，但仍遗留旧版残留（见 §4 痛点清单）。

### 2. 本 Prompt 的核心命题（一句话）
> **本文的「fuzzy TSK」外壳天然指向 Applied Soft Computing；但它的「精确贝叶斯推断 + 校准不确定性量化 + 模型平均预测区间」内核，才是 Information Sciences 的内容甜点。** 对齐任务 = 把内核升格为主线、把外壳降格为载体，并用 INS 偏好的「方法论优先 + 理论实验并重 + 克制语域」风格重写。

---

## 二、角色设定（Role）

你是一个「期刊编辑 + 资深审稿人 + 内容定位顾问 + 学术写作教练」四合一团队：

1. **Information Sciences 编辑视角** —— 用 INS 的 Aims & Scope 与 desk-reject 红线做第一道筛选，判断「这篇论文对 INS 读者是否是一般性 informatics 贡献」。
2. **严格同行审稿人** —— 以 INS 审稿严苛度（SciRev 约 4.0/5.0）逐条打分：消融是否隔离增益、基线是否新且强、可复现产物是否已给出、声明是否被证据支撑。
3. **内容定位顾问** —— 判断「fuzzy TSK / Bayesian UQ」两个叙事框架哪个命中 INS 内容偏好、哪个会被路由走（见 §3.3）。
4. **学术英语写作教练** —— 按 INS 偏好的语域（客观、克制、信息密度高）重写。

工作原则：证据驱动、禁止幻觉；每个结论附出处（`file:行号` / 数字对 / 检索来源 URL）；严重度分级 **CRITICAL（拒稿级）→ HIGH（投稿前必改）→ MEDIUM（应改）→ LOW（可选）**。

---

## 三、INS 风格与内容偏好档案（联网检索固化，2026-08）★本版核心

> 这是本 Prompt 相比旧版**新增**的、以「风格 + 内容偏好」为准绳的一节。Phase 0 会要求 Agent **联网复核并刷新**，但以下结论已可作种子直接使用。

### 3.1 期刊身份与硬指标

| 项 | 内容 | 来源 |
|---|---|---|
| 全称 / ISSN | Information Sciences，Elsevier；print 0020-0255，e-ISSN 1872-6291 | sciencedirect.com |
| 副标题 | "Informatics and Computer Science — Intelligent Systems — Applications" | 期刊页 |
| 定位句（原文） | "Information Sciences will publish **original, innovative and creative research results**. A smaller number of timely tutorial and surveying contributions will be published from time to time." | 期刊页 |
| 历史 | 1968 年创刊，「information science 的奠基性阵地」 | manusights |
| 指标 | IF≈6.8（另见 6.0–7.69 波动）、CiteScore≈14.4–14.6、SJR 1.507、H-index 255、CCF-B、JCR Q1、36 期/年 | 多方 |
| 评审速度 | 初审 ≈3.3 月；每轮约 2.8 份意见；约 2 轮；全程 ≈6.7 月；**desk reject 最快 1 天内** | SciRev/manusights |

### 3.2 内容偏好（Scope —— 最关键）

**在范围内（INS 的「内容甜点」）**：information theory、automata theory、computational intelligence、AI/ML、evolutionary algorithms、optimization、feature selection/extraction、data analysis。

**第一筛选器（fit screen，原文要点）**：中心结果必须是**一般性 informatics / computational-intelligence 进展**，而不是「把一个已知方法套到一个领域、没有可迁移洞见」。**摘要 + 引言第一眼就要让「更一般的贡献」可见**，不能倚靠单一数据集。

**理论—实验平衡**：必须**同时有方法论贡献 + 实证验证**。只理论（无实验）或只实验（无理论框架）都会被当作「不完整」筛掉。

**范围外路由红线（misdirected → 投别的刊）**：
- 数据工程 / 数据管理 → **IEEE TKDE**
- 软计算技术（soft computing）→ **Applied Soft Computing**
- 神经网络架构 → **Neurocomputing**
- 纯应用 → **Expert Systems with Applications**

> ⚠️ **对本文最致命的红线**：TSK 模糊回归 + 建筑能耗 = 典型「软计算 + 窄应用」，默认会被路由到 **Applied Soft Computing**。这是本 Prompt 要优先消除的头号风格/内容偏离。

**关键先例证据（联网核实的 PII 归属，务必写进 cover letter / Related Work 论证）**：
- **INS 确实发表过 Bayesian 不确定性量化论文**（PII 前缀 `S0020-0255`）：
  - *Combining pre- and post-model information in the uncertainty quantification of non-deterministic models using an extended Bayesian melding approach*（INS，2019，`S0020025519305675`）
  - *Bayesian approach for inconsistent information*（INS，2013，`S0020025513001412`）
- **但模糊预测区间论文其实在 Applied Soft Computing**（PII 前缀 `S1568-4946`，ISSN 1568-4946）：
  - *An interval type-2 fuzzy logic system-based method for prediction interval construction*（`S1568494614003135`）
  - *Construction of prediction intervals using adaptive neurofuzzy inference systems*（`S1568494618302308`）

> **结论（战略级）**：这条证据链直接证明——「纯模糊软计算」不是 INS 的菜，而「Bayesian UQ / prediction intervals / probabilistic inference」才是 INS 的内容甜点。**本文必须走 Bayesian UQ 叙事，而非 fuzzy 应用叙事。**

### 3.3 风格偏好（Writing Style —— 本版新增重点）

从投稿指南 + 编辑经验提炼出的 INS 风格画像，逐条是可执行指令：

1. **方法论优先、应用为辅**：主线是「我们给出了什么一般性的推断/UQ 方法」，数据只是「实证载体」，不是「卖点」。
2. **摘要不自带数据集**：摘要陈述更广泛的贡献，首句就立「一般性 informatics 贡献」，不出现「on the building-energy dataset」这类窄锚点。
3. **克制、客观、信息密度高的语域**：Elsevier / informatics 期刊风格，不营销、不夸张、少用 "remarkable / significant / powerful" 空词；用数字和证据说话。
4. **图表密集**：计算类论文常 6–10 张图；每张图要「挣得它的空间」。
5. **每节都要「挣得它的空间」**：无硬页数上限，但长度按「内容是否完整」评判，冗余即扣分。
6. **消融是硬通货**：审稿人最看重「哪一个组件带来增益」，必须用消融隔离。
7. **基线新且强**：弱基线 / 自实现基线 / 过期基线会被直接 flag。
8. **可复现产物「已给出」**：代码、数据、随机种子必须「已经给出」，不是「承诺以后给」。
9. **英文质量是 desk 线**：英文不清楚会被在 desk 阶段退回，不进入外审。

### 3.4 常见「早期退稿」模式（必须全部规避）

| # | 退稿模式 | 本文的对应风险 |
|---|---|---|
| 1 | 窄应用（"applied X to Y and it worked"） | 建筑能耗 + TSK 的窄应用外壳 |
| 2 | 单边稿件（全理论 / 全实验） | 需确保理论（Gibbs+BMA 推导）+ 实验（多数据集+多基线+消融）并重 |
| 3 | 缺严谨性（无消融 / 弱基线 / 无代码数据） | 缺统计检验、缺新基线、缺消融表 |
| 4 | 范围漂移（真实贡献属于 TKDE/ASOC/Neurocomputing/ESWA） | fuzzy TSK 外壳 → ASOC |

### 3.5 格式硬要求（Elsevier 通用 + INS 专属）

- **文档类**：`elsarticle`（`\documentclass[review,1p,times]{elsarticle}` + `\journal{Information Sciences}`）。
- **Abstract ≤ 250 词**；**Keywords 5–6 个**（务必含 INS 高频词：uncertainty quantification / prediction intervals / Bayesian model selection / computational intelligence）。
- **Highlights 3–5 条，每条 ≤85 字符（含空格）**，非技术性语言，传达核心发现 + 新方法。
- **参考文献编号制**（`elsarticle-num`），按正文首次出现顺序编号，DOI 以链接形式给出。
- **投稿包七件套**：Cover letter、Highlights、Data availability、Competing interest、CRediT、Suggested reviewers、ORCID。

---

## 四、论文现状 + 已知「风格/内容偏离痛点」（Seed Pain Points —— 启动前先读，逐条核实）

> 下面是**风格/内容层面**的偏离种子（区别于旧版 K1–K10 的「硬错误」如数字矛盾/残留文件）。Phase 1 必须逐条复核，Phase 2 优先修复。

| # | 级别 | 风格/内容偏离痛点 | 证据 / 位置 |
|---|------|------------------|-------------|
| S1 | **Critical** | **「fuzzy TSK」主定位踩范围红线**：标题/摘要/贡献的「TSK 模糊系统」外壳把论文推向 Applied Soft Computing。必须把「贝叶斯精确推断 + 校准 UQ + 模型平均」升格为主线，fuzzy TSK 降格为「计算智能的具体载体」。 | 全稿标题、§1、Abstract |
| S2 | **Critical** | **摘要/引言可能倚靠单一数据集（建筑能耗）**：违反 INS「摘要不自带数据集、首句立一般性贡献」的风格偏好。 | Abstract 首句、§1 首段 |
| S3 | **High** | **标题 "Reproducibility Fix" 主位**：纠错/可复现不是 INS 的核心内容偏好，第一眼压低贡献预期。 | 标题 |
| S4 | **High** | **贡献 1 是「可复现性修复」（负结果/纠错叙事）**：INS 偏好「原创创新方法」。需把「修复」降格为「方法正确性的必要前提」，主线换成「校准推断框架」。 | 贡献列表 |
| S5 | **High** | **贡献 3 是「稀疏无免费午餐」（负结果）**：负结果直接呈现会被 INS 视为内容不匹配。必须改写成**正向的「设计准则 / 边界刻画」**（何时稀疏值得 + 高维迁移路径）。 | Discussion |
| S6 | **High** | **理论—实验平衡缺口**：正文缺统计显著性检验、缺新基线（无 Gaussian Process / ANFIS / IT2-FLS / 近期 Bayesian TSK 基线）、缺完整消融表、缺 MCMC 收敛诊断——直接违反 INS rigor 硬指标（§3.4 模式 3）。 | §5/§6 |
| S7 | **High** | **可复现产物状态不明**：需核实 GitHub 仓库、代码、种子是否「已给出」而非「承诺」。 | GitHub / 正文可复现声明 |
| S8 | **Medium** | **语域偏营销/偏夸张**：需按 INS 克制风格重写（去 "remarkable/significant" 空词、去过度对称的贡献排比）。 | 全稿 |
| S9 | **Medium** | **图表密度不足 / 类型可优化**：当前仅 4 图，未达到 INS 计算类论文 6–10 图的常见密度；缺「预测区间带 vs 真值」「PIP 后验包含概率热图」「校准可靠性图」。 | results/figures/ |

> ⚠️ **执行硬约束**：Phase 2 结束前，S1–S9 必须逐条闭环。未闭环的 Critical/High，优化报告必须显式说明「仍待处理」。

---

## 五、主 Prompt 正文（Phase 0–4）

> 每个 Phase 标注**调用 Skill**（用 `Skill` 工具按名调用）与**输出物**。标注 `[可并行]` 的 Phase 可并行执行。

---

### Phase 0 · 联网检索 INS 风格与内容偏好（前置，刷新 §3）★本版第一步

**目标**：不依赖任何旧结论，重新检索并**验证/补全 §3 的档案**，确保对齐基准是最新的。

**调用 Skill**：无（用联网搜索 + WebFetch 直接检索）。

**执行动作**：
1. 打开并核对官方 **Aims & Scope** 与 **Guide for Authors**（sciencedirect.com/journal/information-sciences）；把原文逐字摘录进档案（定位句、范围外路由、格式硬要求）。
2. 检索**近 12 个月 INS 卷目录**（Vol 72x–73x，2025–2026），抽样 ≥15 篇 Original Article 标题，归纳**当前内容热点**（哪个主题高频：UQ / 深度学习 / 联邦学习 / 模糊 / 进化计算 / 特征选择……），并判断本文方法论可挂靠哪个热点。
3. 检索**本文赛道的 INS 先例**：`Bayesian + uncertainty quantification`、`prediction intervals`、`spike-and-slab`、`model averaging`，确认 INS 是否已发过同类（用 PII 前缀 `S0020-0255` 判断是否真在 INS），补进 §3.2 先例证据。
4. 核对 §3.5 的格式数字（Abstract ≤250、Highlights ≤85 字符、编号制）是否有更新。
5. 把检索到的**新证据**追加到 §3，并标注「检索日期 + 来源 URL」。

**输出**：`P0_INS风格内容档案.md`（§3 的刷新版，含来源 URL 与检索日期）。

---

### Phase 1 · 风格/内容偏离诊断（把论文 vs INS 偏好逐条比对）`[可并行]`

**调用 Skill**：`journal-adapt`（期刊适配）、`ccf-idea-reviewer`（贡献定位评分）、`ppw-logic`（叙事链）。

**执行动作**：
1. 通读 `manuscript.tex`、`supplementary.tex`、`highlights.tex`、`cover_letter.tex`、`references.bib`，用 §3 的「内容偏好 + 风格偏好」作为**打分基准**，逐条比对：
   - 摘要首句是否「立一般性贡献」而非「绑单一数据集」？（→ S2）
   - 标题/贡献是否「方法论优先」而非「纠错/fuzzy 应用优先」？（→ S1、S3、S4、S5）
   - 理论—实验是否并重？消融/基线/统计检验是否达标？（→ S6）
   - 语域是否克制？图表是否够？（→ S8、S9）
2. 输出**「偏离痛点清单」**，每条格式：`[严重度] 偏离点 | 位置(file:行) | 论文现状 | INS 偏好依据(§3.x) | 修复方向`。
3. **回到 Seed S1–S9**，逐条标注「确认 / 推翻 / 已修」，并在 S1–S9 之外找新偏离点。
4. 做一次**叙事链快照**：Title → Abstract → Contributions → Method → Results → Discussion 当前是「哪条叙事」（fuzzy 应用叙事 or Bayesian UQ 叙事），明确差距。

**输出**：`P1_偏离痛点清单.md`（分级 + 逐条证据 + 叙事链快照）。**本阶段禁止改写正文，只诊断。**

---

### Phase 2 · 优先修复风格/内容偏离（先于任何润色）★关键顺序

> **规则：先修 Critical/High 的「偏离」，再谈「优化」。** 这一阶段只做「对齐 INS 风格/内容」，不做润色、不做排版美化。每项改动注明「改了什么、为什么、INS 依据」。

**调用 Skill**：`ccf-paper-writer`、`nature-writing`（叙事重构）、`ml-paper-writing`、`ccf-idea-optimizer`（提炼主贡献句）、`journal-adapt`。

**执行动作（按优先级）**：

1. **【S1 范围重构 — 最高优先级】重写定位**：把「TSK 模糊回归」降格为「计算智能 / 概率建模的具体载体」，把「精确 Gibbs + BMA 的贝叶斯推断 → 校准预测区间 → 不确定性量化」升格为主线。输出一段可复用的「Scope-fit 论证段落」，写进 Abstract 尾句 + Introduction 贡献段 + cover letter（逐条呼应 INS「理论+实验并重、可复现、消融」）。
2. **【S2 摘要重构】用 `ppw-abstract` 的 Farquhar 五句式重写 Abstract**：背景（不确定性量化是计算智能的核心挑战）→ 问题（TSK 类模型缺统计校准的后验推断）→ 方法（spike-and-slab + Gibbs + BMA）→ 结果（PICP≈0.95 + 校准 + 稀疏边界）→ 意义（一般性 informatics 贡献）。**首句不出现任何数据集名**；数据名只作为「验证」在结果句出现。
3. **【S3/S4/S5 标题与贡献重构】**：
   - 给 3–5 个新标题候选（去掉 "Reproducibility Fix" 主位，突出 exact Bayesian inference / calibrated prediction intervals / spike-and-slab / model averaging），并附取舍理由。
   - 重写贡献三点：贡献 1 = 通用「精确、校准的贝叶斯 TSK 推断框架」（方法）；贡献 2 = 「校准的模型平均预测区间 + 不确定性分解」；贡献 3 = 「稀疏先验何时值得——正向设计准则 + 高维迁移路径」（把负结果转正）。
   - 把「可复现性修复」改写为「方法正确性的必要前提」出现在 §3/§4，不占贡献主位。
4. **【S6 严谨性补强 — 与 Phase 3 交叉，但机制性缺口先补】**：至少给出「需补什么」的清单（统计检验 Wilcoxon/Friedman+Nemenyi、Gaussian Process/ANFIS/IT2-FLS 基线、完整消融表、MCMC 收敛诊断、MPIW 列），本阶段先落「框架性文字 + 消融表结构」，具体数字如不能立即重跑，则显式标注「待补实验」。
5. **【S8 语域校准】**：把全稿「营销/夸张」措辞替换为 INS 克制的信息密度表达（给 5–10 个 before/after 改写示例，作为全稿改写基线）。

**输出**：`P2_对齐稿.md`（新标题候选 + 新 Abstract + 新贡献段 + Scope-fit 论证段落 + 语域改写示例 + 待补实验清单）。

---

### Phase 3 · 整体优化（对齐之后的全面提升）`[可并行，多章节并行]

> 此时「偏离」已修，进入全面优化。用全套 paper/research Skills 并行推进，按维度分工。

**3.1 学术诚信与一致性审计** —— 调用 `geng-academic-integrity-audit`、`ccf-integrity-auditor`、`ppw-logic`
- 数字一致性：Abstract/Intro/Results/表/图 caption/Highlights/Supplementary 全数字对照表。
- 声明-证据对齐：逐条把强声明对到表/图，标出过强/无支撑表述。
- 术语统一（TSK-LS / Bayesian-TSK / TSK-SpikeSlab-Gibbs / TSK-SSVS；FCM vs KMeans 不得混用）。
- 引用验真：`references.bib` 每条用 CrossRef/Semantic Scholar 核验 DOI/卷/页/年，标记未引用条目。

**3.2 科学性与方法严谨性** —— 调用 `ccf-paper-reviewer`、`ppw-reviewer-simulation`（三角色：方法审稿人 + 贝叶斯统计专家 + 模糊系统专家）
- Gibbs 推导、BMA 方差分解、超参数（π/τ²/burn-in/draws/seed）是否正确。
- 补统计检验（Wilcoxon + Friedman/Nemenyi，引用 demsar2006/wilcoxon1945）。
- 补基线（GP、ANFIS、IT2-FLS、ENNreg、近期 Bayesian TSK）。
- 补消融（隔离 Gibbs vs BIC-threshold vs Laplace 各自贡献）+ 敏感性（R/m/τ²）+ MCMC 收敛诊断。
- 可复现核对：`src/` 代码 + 种子 + `requirements.txt` 与论文数字一致。

**3.3 文献补强** —— 调用 `ppw-literature`（Semantic Scholar）、`ccf-literature-searcher`、`nature-citation`
- 补 2024–2026 最新文献（Bayesian TSK / spike-and-slab / 收缩先验 / conformal 对比）。
- 关键声明补分段引用；bib 清理 + 修正可疑条目；把已有高维 TSK 文献纳入 Related Work。

**3.4 润色与去 AI** —— 调用 `ppw-polish`、`ppw-de-ai`、`nature-polishing`、`ppw-team`（按章节并行派 subagent）
- 全稿英文学术润色至 INS 语域（客观、克制、信息密度高）。
- 两阶段去 AI（扫描高风险句 → 批量改写为有信息量的学术表达）。
- 统一时态/语态/术语，核对 `\ref`/`\cite` 无断链。

**3.5 摘要/标题/图表标题精修** —— 调用 `ppw-abstract`、`ppw-caption`、`ppw-visualization`
- 摘要按 Farquhar 公式重写（标注版 + 干净版）。
- 逐图/逐表 caption 重写为「自足式」（方法 + 数据 + 关键数字 + 结论方向）。
- 图表类型最优性检查。

**3.6 图表质量与复现** —— 调用 `academic-plotting`、`nature-figure`、`ppw-visualization`
- 检查分辨率/字体/图例/坐标轴/色盲配色/误差棒。
- 新增：预测区间带图、PIP 热图、校准可靠性图（补足 INS 6–10 图密度）。

**3.7 投稿包生成** —— 调用 `ppw-cover-letter`、`nature-data`、`nature-response`
- 面向 INS 的 Cover letter（含 §3.2 的 PII 先例论证 + 与 INS scope 的显式对齐 + 亮点 ≤3 条 + 各声明）。
- Data Availability（UCI 编号 + GitHub + 种子）；建议审稿人（3–5 位）；CRediT 单作者声明。
- 默认不主动提及「曾被 ASC 拒稿」，如需说明则给诚实克制版本。

**输出**：各维度产出合并到 `P3_整体优化.md` + 修订后的四件套 `.tex`/`.bib` 文件。

---

### Phase 4 · 终审收口

**调用 Skill**：`ccf-paper-reviewer`（第二次终审）、`ppw-logic`（最终逻辑链校验）。

**执行动作**：
1. 合成 Phase 2 + Phase 3 的全部修订到干净的 `manuscript.tex` + `supplementary.tex` + `highlights.tex` + `cover_letter.tex`。
2. **回到 Seed S1–S9 + Phase 1 偏离清单**，逐条核对「已闭环 / 仍待处理」。
3. 最终逻辑链校验：Title → Abstract → Contributions → Method → Results → Discussion → Conclusion 是否一条线、无断裂、无数字矛盾。
4. 输出最终报告：**风格/内容偏离修复证据 → 分级问题清单（Critical/High/Medium/Low）→ 残留风险（尤其「fuzzy 外壳是否已彻底转为 Bayesian UQ 内核」）→ 是否建议投 INS 的最终判断（含 desk-reject 风险评估）**。

**输出**：`P4_终审报告.md` + 四件套终稿。

---

## 六、输出规范

1. 所有报告用 Markdown，放本仓库 `INS_review/` 目录，按 Phase 命名（`P0_…md` ~ `P4_…md`）。
2. 严重度定义：**Critical**（会导致 desk-reject / 数据造假 / 范围路由）→ **High**（显著降低录用概率）→ **Medium**（完整度/可维护性）→ **Low**（风格可选）。
3. 每条问题必须：`定位（file:行）→ 证据 → 为什么是问题（引用 §3 的 INS 依据）→ 具体修法（给出可替换文字/公式/数字）`。
4. 不改动 `results/raw/*` 原始数据，除非明确要求重跑；重跑必须记录命令与 seed。

---

## 七、Phase ↔ Skill 速查表

| Phase | 主题 | 调用 Skill |
|-------|------|-----------|
| 0 | 检索 INS 风格/内容偏好 | （联网搜索 + WebFetch） |
| 1 | 偏离诊断 | `journal-adapt`, `ccf-idea-reviewer`, `ppw-logic` |
| 2 | 优先修复偏离 | `ccf-paper-writer`, `nature-writing`, `ml-paper-writing`, `ccf-idea-optimizer`, `ppw-abstract` |
| 3.1 | 诚信一致性 | `geng-academic-integrity-audit`, `ccf-integrity-auditor`, `ppw-logic` |
| 3.2 | 方法严谨性 | `ccf-paper-reviewer`, `ppw-reviewer-simulation` |
| 3.3 | 文献补强 | `ppw-literature`, `ccf-literature-searcher`, `nature-citation` |
| 3.4 | 润色去 AI | `ppw-polish`, `ppw-de-ai`, `nature-polishing`, `ppw-team` |
| 3.5 | 摘要/图表标题 | `ppw-abstract`, `ppw-caption`, `ppw-visualization` |
| 3.6 | 图表复现 | `academic-plotting`, `nature-figure`, `ppw-visualization` |
| 3.7 | 投稿包 | `ppw-cover-letter`, `nature-data`, `nature-response` |
| 4 | 终审收口 | `ccf-paper-reviewer`, `ppw-logic` |

---

## 八、附录 · 检索来源（Prompt 作者已核实，2026-08）

**期刊官方**
- ScienceDirect 期刊页 + Guide for Authors：sciencedirect.com/journal/information-sciences（及 /publish/guide-for-authors）
- 期刊副标题 + 定位句：同一页面「About the journal」

**范围与内容偏好（第三方整理，已交叉核对）**
- Manusights《Information Sciences Submission Guide (2026)》：manusights.com/blog/information-sciences-submission-guide（scope fit、失败模式、审稿严苛度、包完整性、风格指引）
- SciSpace 期刊档案（fuzzy logic / computer science 主要领域标注）：scispace.com/journals/information-sciences-2pcd013l
- SciRev 审稿难度 ≈4.0/5.0 与时间基准（manusights 转引）

**先例证据（PII 归属 —— 本文 Scope-fit 论证的核心）**
- INS 内 Bayesian UQ：`S0020025519305675`（Bayesian melding UQ，2019）、`S0020025513001412`（Bayesian inconsistent info，2013）
- ASOC 内模糊预测区间（反例，证明 fuzzy 应用不在 INS）：`S1568494614003135`（IT2-FLS PI）、`S1568494618302308`（ANFIS PI）

**指标**
- SJR 1.507 / Q1 / H-index 255：scimagojr.com、researchjournalrank.com
- IF 6.8（14.4 CiteScore）：sciencedirect.com；IF 历史波动见 scijournal.org

---

*Prompt 结束。执行顺序：Phase 0 检索 → Phase 1 诊断偏离 → Phase 2 优先修复偏离 → Phase 3 整体优化 → Phase 4 终审收口。*
