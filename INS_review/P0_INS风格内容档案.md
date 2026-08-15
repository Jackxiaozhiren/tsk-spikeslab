# P0 · Information Sciences 风格与内容偏好档案（联网复核刷新版）

生成时间：2026-08-14 · 执行方式：workflow 五维并行联网检索（metrics / scope-format / style-reject 三agent完成；precedents / toc-content 两agent因计费失败由主循环 WebSearch 补齐）
状态：**对 Prompt §3 种子档案的刷新版**，含 2 处关键更正（Abstract 词数、fuzzy 范围判断）与若干新增先例/格式项。

---

## 0. 本版对种子档案的 3 个关键更正（先说结论）

| # | 种子 §3 说法 | 联网核实结果 | 影响 |
|---|---|---|---|
| **C1** | Abstract ≤ 250 词 | **官方 Guide for Authors：≤ 200 词**（web.archive 2024 存档原文 "Abstract (of up to 200 words)"） | 本稿 190 词，两种口径都达标；但投稿包核对必须以 200 为准 |
| **C2** | 「fuzzy TSK → 必被路由到 Applied Soft Computing」是头号红线 | **过强**。INS 官方 Aims & Scope **明确列出 "Fuzzy Logic and Approximate Reasoning / Soft Computing / Computing with Words"**；期刊参考文献范例正是 Zadeh《Toward a generalized theory of uncertainty (GTU)》(INS 2005) 与 Pedrycz《Introduction to Fuzzy Sets》；主编 **Witold Pedrycz** 本人是模糊系统泰斗 | 战略转向：**fuzzy 外壳不是致命伤**；致命伤是「窄应用无迁移洞见 + 纠错/负结果叙事」。修复重心应从「去模糊化」转为「把一般性 Bayesian-UQ 方法论升格为主线」 |
| **C3** | 种子未提 | INS 在 S0020-0255 前缀下**大量发表不确定性理论/证据推理/belief-function 论文**（见 §5） | 本稿「Bayesian UQ + 预测区间 + 模型平均」内核直接命中 INS 的 uncertainty-theory 血统，scope-fit 论据比种子更强 |

---

## 1. 期刊身份与硬指标（§3.1 刷新）

| 项 | 值 | 来源 | 判定 |
|---|---|---|---|
| 全称 / ISSN | Information Sciences，Elsevier；print 0020-0255，e-ISSN 1872-6291 | Wikipedia / Elsevier Shop / SciJournal | ✅ 确认 |
| 副标题 | "Informatics and Computer Science — Intelligent Systems — Applications" | Elsevier Shop / ScienceDirect | ✅ 确认 |
| 创刊 | 1968 | Wikipedia（"History: 1968–present"） | ✅ 确认 |
| 主编 | **Witold Pedrycz**（种子未提） | Wikipedia infobox | 🆕 新增 |
| 影响因子 | **ScienceDirect 首页 6.8**；SciJournal 7.690（2025）；myhuiban/S-Logix 6.0；Wikipedia 8.233（2021 旧值） | ScienceDirect / SciJournal | ✅ 确认（种子 6.0–7.69 区间成立） |
| CiteScore | 14.4（ScienceDirect）/ 14.6（S-Logix） | ScienceDirect | ✅ 确认 |
| SJR | 1.507（2025）；1.803 为 2024 旧值 | SciJournal | ✅ 确认 |
| H-index | 255 | SciJournal / journalsearches | ✅ 确认 |
| CCF 分级 | **CCF-B（数据库/数据挖掘/内容检索）**，CCF 第 7 版目录（2026-03 通过） | ccf.atom.im / myhuiban | ✅ 确认 |
| JCR 分区 | Q1 | SciJournal / S-Logix | ✅ 确认 |
| 期数 | ~36 期/年（"36 volumes, 36 issues"） | Elsevier Shop | ✅ 确认 |
| 开放获取 | 混合制（hybrid，支持 OA，收 APC） | ScienceDirect | 🆕 新增 |
| 审稿速度 | 首轮 ≈3.1–3.3 月；总 ≈6.5–6.7 月；~1.8–2 轮；~2.6–2.8 意见/轮 | SciRev / manusights | ✅ 确认 |
| 即时拒稿 | **最快 1 天内**（"Decision time immediate rejection 1 days"） | SciRev | ✅ 确认 |
| 审稿严苛度 | 审稿意见难度 **4.0/5.0（difficult）**；manuscript-handling 2.8/5.0；报告质量 3.2/5.0 | SciRev（n=6） | 🆕 新增 |
| 录用竞争 | LetPub 众包接受率 ~22.5%；平均审稿 ~10.8 月；Peeref 周转 16.8 周 | LetPub / Peeref | 🆕 新增 |

---

## 2. Aims & Scope 原文与范围红线（§3.2 刷新）

### 2.1 定位句（原文，已核实）

> "Information Sciences will publish **original, innovative and creative research results**. A smaller number of timely tutorial and surveying contributions will be published from time to time."
> —— ScienceDirect 期刊页 / web.archive 2024 存档

补充原文（存档）：
> "The journal publishes high-quality, refereed articles. It **emphasizes a balanced coverage of both theory and practice**."

### 2.2 在范围内主题（存档原文逐字摘录，★为本稿直接命中的）

**★ Fuzzy Logic and Approximate Reasoning** · **★ Soft Computing** · **★ Computing with Words** · Information Theory · Mathematical Optimization · Artificial Intelligence · Computational Intelligence · Learning and Evolutionary Computing · Artificial Neural Networks · Pattern Recognition · Data Fusion · Genetic Algorithms and Modelling · Finance/Economics Modelling · Data Engineering · Feature Selection/Extraction。

> ⚠️ **种子修正**：fuzzy logic / soft computing / computing with words **是 INS 官方列明的在范围主题**，不是范围外。种子里「fuzzy → ASOC」的判断忽略了这一条。

### 2.3 第一筛选器（fit screen）

中心结果必须是**一般性 informatics / computational-intelligence 进展**，不是「把已知方法套到一个领域、无可迁移洞见」。「摘要 + 引言第一眼就要让更一般的贡献可见」。**必须同时有方法论贡献 + 实证验证**（纯理论或纯实验都算「半篇」）。

### 2.4 范围外路由红线（misdirected，第三方整理 + 存档确认）

数据工程 → IEEE TKDE；软计算技术应用 → Applied Soft Computing；神经网络架构 → Neurocomputing；纯应用 → Expert Systems with Applications。

> **本稿的精确风险点（比种子更准）**：不是「用了 TSK 模糊系统」，而是「读起来像『把 spike-and-slab/Gibbs 套到建筑能耗，还附带一个 bug 修复和一个负结果』」——即 *competent one-domain demonstration*。这是 desk-reject 的第一现场。

---

## 3. 内容偏好（§3.2 刷新，面向本稿的可执行判据）

1. **理论—实验并重是硬门槛**：官方原文 "emphasizes a balanced coverage of both theory and practice"。本稿有 Gibbs/BMA 推导（理论）+ 2 数据集×30 划分（实验），结构达标，但**实验深度被 2 个低维数据集 + 缺新基线 + 缺 MCMC 收敛诊断拖累**。
2. **方法论前置、应用为载体**：方法（exact inference + calibrated UQ）是中心，TSK/建筑能耗是实例。
3. **贡献首句可读性**："The abstract and introduction have to make the **broader contribution visible on the first read**"（manusights，直引 INS 语境）。
4. **消融是硬通货**：审稿人必问「哪个组件带来增益」——本稿已有 Supplementary §5 的 BIC 机制消融，是加分项。
5. **基线新且强**：弱/自实现/过期基线会被 flag。本稿现有 RF/SVR/Bayesian-TSK，**缺 GP / ANFIS / IT2-FLS / ENNreg 实测基线**。
6. **可复现产物「已给出」**：代码/数据/种子须在投稿时存在，不能「承诺以后给」。本稿有 GitHub + Zenodo DOI + SEED=42 + requirements.txt，达标但需核实已 push。
7. **英文质量是 desk 线**："unclear because of English-language quality can be **returned for rewrite before review**"。

---

## 4. 风格偏好（§3.3 刷新，逐条可执行）

1. **克制、客观、信息密度高**：第三方指南从不鼓励夸张形容词；用数字与证据说话。→ 本稿 "catastrophically"（摘要+cover letter 各 1）、"no free lunch" 习语、cover letter "first" 声明需校准。
2. **图表密集**：计算类论文**常见 6–10 图**（manusights 直引）；长度按「完整性」评判，冗余即扣分。→ 本稿仅 4 图，偏少。
3. **每节都要挣得空间**：无硬页数上限，但官方另有长度建议（见 §5）。
4. **语态/拼写**：American spelling 全文统一（含 keywords）；单盲评审（single-anonymized）。
5. **编号章节**：1 / 1.1 / 1.2…；Abstract 不编号。→ 本稿 elsarticle 默认编号，达标。

---

## 5. 格式硬要求（§3.5 刷新，含 2 处更正）

| 项 | 官方要求 | 本稿现状 | 判定 |
|---|---|---|---|
| 文档类 | `elsarticle`（`\documentclass[review,1p,times]{elsarticle}` + `\journal{Information Sciences}`） | ✅ 已改 | 达标 |
| **Abstract** | **≤ 200 词**（种子误写 250） | 190 词 | ✅ 达标 |
| Keywords | **≤ 6 个**，American spelling，避免泛化/复数/多概念 | 6 个（TSK fuzzy system / Bayesian inference / spike-and-slab prior / Gibbs sampling / Bayesian model averaging / prediction intervals） | ✅ 数量达标，但**缺 "uncertainty quantification"** 这一 INS 高频词 |
| Highlights | 3–5 条，每条 ≤85 字符（含空格），非技术性，单独可编辑文件 | 5 条，全部 ≤85 | ✅ 达标 |
| 参考文献 | 提交时任意一致风格；`elsarticle-num`（按出现顺序编号）为最终出版格式 | ✅ 已用 elsarticle-num | 达标 |
| 建议审稿人 | ≥3 位（不得是编委/同事/近期合著者，鼓励地域多样） | ✅ 3 位（Denoeux/Destercke/Pal） | 达标 |
| 必需声明 | Competing interest + CRediT + Data availability | ✅ 三项齐全 | 达标 |
| **长度建议** | 实验类 ≤40 双倍行距页 + 8 图/表；理论类 ≤45 页 + 10 图/表 | 本稿远低于上限 | ✅ 达标 |
| **作者简介** | **Biography ≤100 词 + 证件照（author vitae）**（种子未提） | ❌ 无 Biography 段 | 🆕 待补（终稿阶段） |
| **结论节** | 必需；理论结果要翻译成多数读者可懂的表述 | ✅ 有 Conclusion | 达标 |
| 投稿门户 | Editorial Manager（editorialmanager.com/ins） | — | — |

---

## 6. 先例证据（PII 归属核实，本稿 Scope-fit 论证核心）★

### 6.1 已核实：INS 确实发表 Bayesian UQ / uncertainty 论文（PII 前缀 S0020-0255）

| 论文 | 年 | PII / DOI | 归属 |
|---|---|---|---|
| Combining pre- and post-model information in the uncertainty quantification of non-deterministic models using an extended Bayesian melding approach | 2019 | `S0020025519305675` | ✅ **Information Sciences** |
| Bayesian approach for inconsistent information | 2013 | `S0020025513001412` | ✅ **Information Sciences** |
| Combining uncertain information of differing modalities | 2015 | `S0020025515004417` | ✅ Information Sciences（🆕 新增） |
| Non-parametric Bayesian annotator combination | 2018 | `S0020025518300264` | ✅ Information Sciences（🆕 新增） |
| A belief function theory based approach to combining different representation of uncertainty in prognostics | 2015 | `S0020025515000031` | ✅ Information Sciences（🆕 新增） |
| Toward a generalized theory of uncertainty (GTU) — an outline（Zadeh） | 2005 | INS 172:1–40 | ✅ **期刊参考文献范例**（🆕 新增） |

### 6.2 已核实：模糊预测区间论文确实在 Applied Soft Computing（反例，PII 前缀 S1568-4946）

| 论文 | 年 | PII | 归属 |
|---|---|---|---|
| An interval type-2 fuzzy logic system-based method for prediction interval construction | 2014 | `S1568494614003135` | ✅ **Applied Soft Computing** |
| Construction of prediction intervals using adaptive neurofuzzy inference systems | 2018 | `S1568494618302308` | ✅ **Applied Soft Computing** |

### 6.3 战略结论（比种子更精确）

INS 的 uncertainty 血统是 **Zadeh 的 GTU / Pedrycz 的模糊集 / belief-function（证据理论）** 这条「**信息处理中的不确定性**」主线，而不是「把模糊系统套到某个工程数据做预测」。因此：
- **本稿的「exact Bayesian inference + calibrated prediction intervals + model averaging」内核，就是 INS 的菜**（对应 Zadeh GTU 的不确定性理论 + belief-function 血统）。
- **「TSK 模糊系统」外壳本身不致命**（fuzzy logic 在范围），致命的是**把它写成一个「建筑能耗窄应用 + bug 修复 + 负结果」的单域演示**。
- **投稿信与引言的论证应从「fuzzy → ASOC」改为「本稿是 Zadeh/Pedrycz uncertainty-theory 血统下的一般性 Bayesian-UQ 方法，TSK 是其具体载体」**，并用 §6.1 的 S0020-0255 先例做锚点。

---

## 7. 常见早期退稿模式（§3.4 刷新）

| # | 退稿模式 | 本稿对应风险 |
|---|---|---|
| 1 | 窄应用（"applied X to Y and it worked"） | 建筑能耗 + bug 修复 + 负结果 = 单域演示观感（**头号风险**） |
| 2 | 单边稿件（全理论/全实验） | 结构达标，但实验深度不足（缺新基线/MCMC 诊断） |
| 3 | 缺严谨性（无消融/弱基线/无代码数据） | 消融✅、代码✅；缺 GP/ANFIS/IT2-FLS 基线、缺 R-hat/ESS |
| 4 | 范围漂移（真实贡献属 TKDE/ASOC/Neurocomputing/ESWA） | fuzzy 应用外壳 → ASOC（**已被 §6.3 修正为次要风险**） |
| 5 | 调查类无综合贡献 | 不适用 |
| 6 | 英文不清（desk 退回） | 语域基本克制，仅个别夸张词 |

---

## 8. 检索来源（检索日期 2026-08-14）

**官方**
- ScienceDirect 期刊页 + 存档 Guide for Authors：sciencedirect.com/journal/information-sciences；web.archive.org/web/20240304043814/https://www.sciencedirect.com/...（官方 Aims&Scope 与格式要求原文）
- Elsevier Shop：shop.elsevier.com/journals/information-sciences/0020-0255（期数/ISSN）
- 投稿门户：editorialmanager.com/ins

**第三方**
- Manusights《Information Sciences Submission Guide (2026)》：manusights.com/blog/information-sciences-submission-guide（scope fit、失败模式、审稿严苛度、风格指引、6-10 图、ablation）
- SciRev：scirev.org/journal/information-sciences/（审稿难度 4.0/5、首轮 3.1 月、即时拒稿 1 天）
- SciJournal：scijournal.org/inform-sciences（IF/SJR/H-index/CiteScore）
- CCF 第 7 版目录：ccf.atom.im（CCF-B）
- LetPub / Peeref：接受率与周转补充

**先例证据（PII 归属）**
- INS Bayesian-UQ：`S0020025519305675`、`S0020025513001412`、`S0020025515004417`、`S0020025518300264`、`S0020025515000031`；Zadeh GTU（INS 2005）
- ASOC 模糊预测区间（反例）：`S1568494614003135`、`S1568494618302308`

---

*Phase 0 结束。核心产出：① Abstract ≤200 词更正；②「fuzzy 外壳不致命、窄应用+纠错+负结果叙事才致命」的战略转向；③ S0020-0255 先例证据链（6 条）可用于投稿信 Scope-fit 论证。*
