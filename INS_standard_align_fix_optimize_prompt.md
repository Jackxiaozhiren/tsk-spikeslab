# Information Sciences (Elsevier) 转投递 · 标准检索 → 偏离修复 → 整体优化 综合主 Prompt（v3.0）

> **用途**：把本文件整体（或按 Phase 分段）喂给具备「读文件 + 联网检索 + 写文件」能力的 Agent（建议 Claude Opus/Sonnet 长上下文 + 开启 ultracode/workflow 多智能体编排），对当前 TSK 论文做一次以 **Information Sciences（Elsevier）投稿标准**为准绳的「**先检索标准 → 再诊断偏离 → 先立即修复偏离 → 后整体优化**」全流程。
> **与旧版 Prompt 的区别**：旧版 `INS_resubmission_prompt.md`（P0–P10）与 `INS_style_content_optimization_prompt.md` 写于论文 P2/P3 修复**之前**，其种子问题清单已大多闭环。本版 v3 是**针对当前（P4 后）稿件状态**的重写：§3 标准档案为 **2026-08 六路联网检索固化版**（含 2024 On Hold 事件、新颖性确认、scope-fit 先例链）；§5 种子清单为**本次会话核验出的当前真实偏离/风险**；§6 执行顺序强制「先修复、后优化」。
> **执行顺序（不可颠倒）**：`Phase 0 检索刷新 → Phase 1 诊断偏离 → Phase 2 立即修复偏离 → Phase 3 整体优化 → Phase 4 终审收口`。
> **最终交付**：一份分级「偏离/风险清单（已闭环/待处理）」，一份与 IS 标准完全对齐的四件套稿件（manuscript / supplementary / highlights / cover letter）+ 可上传 Editorial Manager 的投稿包。

---

## 一、背景与目标（先读入）

### 1.1 论文现状（2026-08-15 确定性核验）

- **当前标题**：*Exact Bayesian Inference for Spike-and-Slab Priors in Takagi–Sugeno–Kang Fuzzy Systems with Calibrated Model-Averaged Prediction Intervals*
- **方法主线**：TSK 模糊回归（FCM 聚类 + 线性后件）+ spike-and-slab 先验 + **block-Gibbs 采样（精确推断，替代 BIC+Laplace 解析近似）** + **Bayesian Model Averaging（BMA）**，得到**校准的 95% 预测区间（PICP 0.94–0.95）**。单规则包含全条件用 matrix-determinant + Woodbury 恒等式在 O(n(d+1)²) 内算出。
- **三贡献（已正向化）**：(1) 对 linear-consequent 规则模型的精确 spike-and-slab 推断；(2) 校准的模型平均预测区间 + 解析近似失效诊断（含消融）；(3) 稀疏设计准则（何时稀疏值得——低维稠密即可，高维/无关特征 regime 才需要）。
- **数据**：Energy Efficiency（UCI，双目标）+ Concrete（UCI），均 d=8；30 次 80/20 划分、SEED=42；另补 Superconductivity d=81 高维边界检验（supplementary）。
- **已具备的严谨性**：paired Wilcoxon（p 值入文）、GP 外部概率基线（PICP 0.93–0.94 vs 本文 0.94–0.95）、多链 MCMC 诊断（R-hat≤1.01、ESS>1700）、消融表（BIC 失效机制逐环节隔离）、R 扫描、τ² 消融、噪声消融、6 张图、25 条被引文献（CrossRef 验真）、GitHub + Zenodo DOI。
- **历史包袱（必须记住）**：本文曾被 *Applied Soft Computing* desk-reject（根因：负结果叙事 + 学术诚信问题）。已彻底重写为「精确校准的贝叶斯 UQ 方法」叙事。**审稿人/编辑不知道这段历史，但稿件里任何与「自指基线」「夸大声明」「不可验证出处」有关的残留都会触发诚信红线。**

### 1.2 核心命题（一句话）

> **「TSK 模糊系统」外壳天然指向 Applied Soft Computing；但「精确贝叶斯推断 + 校准不确定性量化 + 模型平均预测区间」内核，是 Information Sciences 的明确在范围主题（Fuzzy Logic / Soft Computing / Uncertainty 血统）。** 对齐任务 = 把内核升格为主线、把外壳降格为载体，并用 IS 偏好的「方法论优先 + 理论实验并重 + 克制语域 + 可复现」标准重写。

### 1.3 目标期刊硬性要求（一句话速记）

单盲评审、原创研究文章、Abstract≤200 词（个别出处 300，需活页确认）、必须含 Conclusion、Highlights 3–5 条每条 ≤85 字符单独文件、elsarticle + 编号引用、声明四件套（Competing interest / CRediT / Data availability / Generative-AI）、≥3 建议审稿人、ORCID；desk 层四筛：**窄应用 / 单边稿件 / 缺严谨性 / 范围漂移**，外加英文质量。

---

## 二、角色设定（Role）

你是「期刊编辑 + 资深审稿人 + 内容定位顾问 + 学术英语写作教练」四合一团队：

1. **Information Sciences 编辑视角** —— 用 IS 的 Aims & Scope 与 desk 四筛做第一道筛选，判断「这篇论文对 IS 读者是否是一般性 informatics / computational-intelligence 贡献」。
2. **严格同行审稿人** —— 以 IS 审稿严苛度（SciRev ≈4.0/5.0）逐条打分：消融是否隔离增益、基线是否新且强、可复现产物是否「已给出」（present, not promised）、声明是否被证据支撑、引用是否真实无幻觉。
3. **内容定位顾问** —— 判断「fuzzy TSK / Bayesian-UQ」两个叙事框架哪个命中 IS 内容偏好（§3.3）、哪个会被路由走（§3.2 范围外红线）。
4. **学术英语写作教练** —— 按 IS 语域（客观、克制、信息密度高、American spelling）重写。

**工作原则**：证据驱动、禁止幻觉；每个结论附出处（`file:行号` / 数字对 / 检索来源 URL）；严重度分级 **CRITICAL（拒稿级/诚信红线）→ HIGH（投稿前必改）→ MEDIUM（应改）→ LOW（可选）**；**不编造任何实验数字**——所有数字只能来自 `results/raw/*.json` 或已入文的实测值。

---

## 三、IS 投稿标准档案（2026-08 六路联网检索固化版）★ 本版核心

> 说明：本档案由 6 路并行联网检索（官方 Guide for Authors / Aims & Scope / 格式模板 / 投稿流程政策 / 近期先例与新颖性 / 审稿统计）固化。**Phase 0 会要求 Agent 在活页上复核刷新**；以下已可作为种子直接使用。检索日期 2026-08-15。

### 3.1 期刊身份与硬指标

| 项 | 值 | 来源 |
|---|---|---|
| 全称 / ISSN | Information Sciences，Elsevier；print 0020-0255，e-ISSN 1872-6291 | ScienceDirect |
| 主编 | **Witold Pedrycz**（University of Alberta）；**Zheng Yan（西安电子科大）为 Co-EiC** | Xidian 官网 / Wikipedia |
| 定位句（原文） | "Information Sciences will publish **original, innovative and creative research results**. A smaller number of timely tutorial and surveying contributions will be published from time to time."；"**emphasizes a balanced coverage of both theory and practice**" | 官方 Aims & Scope |
| 文章类型 | 主类型「**Original research work**」；另有 Short Communications；综述/教程选择性录用 | Guide for Authors + 2026 期目次 |
| 影响因子 | ScienceDirect 页面（2026-08）显示 **6.8**；但 **2025 JCR（2026-06 发布）实为 6.0**，Elsevier 页面滞后 | JustScience / wos-journal.info |
| **⚠️ 2024 诚信事件** | **2024-06 Clarivate 将 INS 列入 Web of Science On Hold**（12 篇 2023 论文被指异常引用），2023 年度 JIF 被压制，2024-08-26 解除，JIF 于 2025-06 恢复为 6.8；自引率 17.3%→~5%，年发文 1400→894 | Retraction Watch |
| CiteScore / SJR / H-index | 14.4–14.6 / ≈1.5–1.8 / 255 | ScienceDirect / scijournal |
| 分区 | JCR Q1（CS, Information Systems）；**CCF-B**；中科院 1 区 TOP | LetPub / CCF |
| 审稿速度 | 首轮 ≈3.1–3.3 月；全程 ≈6.5–6.7 月；~1.8–2 轮；每轮 2–3 人；**desk reject 最快 ~1 天** | SciRev / manusights |
| 审稿严苛度 | 意见难度 **4.0/5.0**；报告质量 3.2/5.0；处理体验 2.8/5.0 | SciRev（n=6） |
| 接受率 | 众包 ~22.5% | LetPub |
| 评审模型 | **单盲（single-anonymized）**，作者身份可见，≥2 位审稿人 | Guide for Authors |
| 投稿门户 | **Editorial Manager：editorialmanager.com/ins**（submit.elsevier.com/INS） | — |
| 开放获取 | 混合制（hybrid），订阅路线无版面费；OA 需 APC | ScienceDirect |
| 近期限流 | 2025-2026 特刊方向：Graph-based AI、6G/AI-native、Privacy-risk evaluation | myhuiban |

### 3.2 Aims & Scope 与范围红线（原文逐字）

**在范围内（官方 Aims & Scope 逐字，★=本稿直接命中）**：
- Foundations of Information Science：computational intelligence、**★ SOFT COMPUTING**、knowledge engineering …
- Implementations and Information Technology：intelligent systems、genetic algorithms and modelling、**★ FUZZY LOGIC AND APPROXIMATE REASONING**、artificial neural networks、**★ SYMBOLIC/NUMERIC AND STATISTICAL TECHNIQUES**、perceptions and pattern recognition、data engineering、data fusion、…、**★ MODELLING AND COMPUTING WITH WORDS**。
- Applications：image processing、data compression、finance/economics modelling …

> **结论（两次检索一致确认）**：**Fuzzy Logic / Soft Computing / Computing with Words 均明确在 IS 官方范围内**。「fuzzy 外壳 → 必被路由到 ASOC」是误判。真正的 desk 触发点是**「窄应用、无可迁移洞见、纠错/负结果叙事、单边稿件、缺严谨性」**。

**第一筛选器（fit screen）**：中心结果必须是**一般性 informatics / computational-intelligence 进展**，不是「把已知方法套到一个领域、无可迁移洞见」。「摘要 + 引言第一眼就要让更一般的贡献可见」，不能倚靠单一数据集。

**理论—实验平衡（硬门槛）**：官方原文 "emphasizes a balanced coverage of both theory and practice"。只理论或只实验都算「半篇」。

**范围外路由红线（misdirected）**：数据工程 → IEEE TKDE；软计算技术本身 → Applied Soft Computing；神经网络架构 → Neurocomputing；纯应用 → Expert Systems with Applications；纯统计（无 informatics 角度）→ 统计期刊。

### 3.3 内容偏好（面向本稿的可执行判据）

1. **方法论优先、应用为载体**：方法（exact block-Gibbs + BMA → 校准 UQ）是中心，TSK/建筑能耗是实例。
2. **贡献首句可读**："The abstract and introduction have to make the **broader contribution visible on the first read**"。
3. **消融是硬通货**：审稿人必问「哪个组件带来增益」——本稿 BIC 失效机制消融已具备，是加分项。
4. **基线新且强**：本稿已有 GP/RF/SVR + 自建 conjugate/BIC/Gibbs；**缺 ANFIS / IT2-FLS / 近期稀疏模糊基线实测**（残留 Medium，见 §5）。
5. **可复现「已给出」**：代码/数据/种子必须投稿时已存在——本稿 GitHub + Zenodo DOI + SEED=42 达标。
6. **新颖性必须显式**：无 separate novelty statement 字段，新颖性靠**引言 + 投稿信显式呈现**（"stressing the motivation for, and the novel aspects of, the work"）。
7. **英文质量是 desk 线**："unclear because of English-language quality can be **returned for rewrite before review**"。

### 3.4 风格偏好

1. **克制、客观、信息密度高**：用数字与证据说话，不堆夸张形容词。
2. **图表密集**：计算类论文常见 **6–10 图**；本稿 6 图达标（实验类图+表合计上限 8）。
3. **American spelling** 全文统一（含 keywords）；**单盲评审，不要匿名化**（保留作者名/单位）。
4. **编号章节** 1 / 1.1 / 1.2；Abstract 不编号；**必须含 Conclusion 节**，理论结果要翻译成多数读者可懂。
5. **审稿体验**：review 模式下建议**加行号**（当前稿缺失，见 §5-A1）。

### 3.5 格式硬要求（含 2 处待活页复核的矛盾点）

| 项 | 官方要求 | 本稿现状 | 判定 |
|---|---|---|---|
| 文档类 | `elsarticle`；官方模板建议 `\documentclass[preprint,review,12pt]{elsarticle}`（review 得 1.5 倍行距）；Times 用 `times` 选项 | `\documentclass[review,1p,times]{elsarticle}` + `\journal{Information Sciences}` | ✅ 达标（class 组合可复核） |
| **行号** | elsarticle **不自动加行号**，需 `\usepackage{lineno}` + `\linenumbers`（审稿友好，官方模板注释推荐） | **无 lineno** | ⚠️ **待补（§5-A1）** |
| **Abstract** | 「of up to **200 words**」（一处出处读作 300——**两读数矛盾，活页复核**） | **154 词** | ✅ 两种口径均达标 |
| Keywords | 4–6 个，紧接摘要，避免与标题重复 | 6 个（uncertainty quantification 领跑） | ✅ |
| Highlights | 3–5 条，**每条 ≤85 字符含空格**，**单独文件**，**禁用缩写/术语** | 5 条 75/80/73/61/64 ✓；**但第 4 条含缩写 "TSK"** | ⚠️ **待修（§5-A2）** |
| Graphical abstract | **非必需**（官方 Writing-and-formatting 目录无此项） | 无 | ✅ 无需准备 |
| 参考文献 | 编号制方括号 [1]、[1,2]；elsarticle-num | elsarticle-num ✓；25 条全部被引 ✓ | ✅ |
| 长度 | 实验类 ≤**40 双倍行距页 + 8 图/表**；理论类 ≤45 页 + 10 或 20 图/表（两出处不一）；**指导值非硬上限** | 远低于上限 | ✅ |
| 必备结构 | Abstract + **Conclusions** | 有 Conclusion ✓ | ✅ |
| 图规格 | EPS/PDF/TIFF/JPEG 单文件；线稿 ≥1000 dpi、彩图 ≥300 dpi、组合图 ≥500 dpi；字高 ≥6–7 pt | 6 张 PDF 图 | ✅（投稿前核 dpi） |
| 声明 | Competing interest + CRediT + Data availability + **Declaration of generative AI use**（Elsevier 政策 2026-06 更新，置于参考文献前） | 四段齐全，Generative AI 声明已含 | ✅ |
| 作者简介 Biography | **检索未确认 IS 硬性要求**（P0 曾标记「终稿阶段待补」）；活页复核，若要求则补 ≤100 词 + 证件照 | 无 | ⚠️ 活页确认后决定 |

### 3.6 投稿包与政策要求（Editorial Manager）

| 项 | 要求 | 本稿状态 |
|---|---|---|
| 投稿门户 | editorialmanager.com/ins | — |
| 上传项 | Manuscript（PDF）+ LaTeX 源码包（.tex/.cls/.bib/.bst/.sty，**不得子文件夹**）；Highlights 单独文件；Figures 单独；Supplementary 单独 | 需整理 |
| Cover letter | 投稿信（可选但强烈建议），显式呈现新颖性 + scope fit，引用 IS 官方主题 | ✅ 已有（可强化 novelty 句） |
| 建议审稿人 | **≥3 位**；不得为编委/近期合著者；鼓励地域多样 | ✅ 3 位（Denoeux/Destercke/Pal，均非 IS 编委） |
| ORCID | 投稿时收集 | ✅ 已有 |
| 声明 | Competing interest / CRediT / Data availability / Generative-AI（均须在投稿时提供） | ✅ 正文已含 |
| SSRN 预印本 | 投稿时可免费挂 SSRN，稿件经 desk 后公开（可选） | 可选 |
| **引用诚信** | **On Hold 事件后审查趋严**：AI 可能幻觉参考文献；「fabricated references may lead to rejection」；避免过度自引 | ✅ CrossRef 已验真；**投稿前再跑一遍验真** |

### 3.7 早期退稿模式（desk screen 四筛 + 语言线）

| # | 退稿模式 | 本稿对应状态 |
|---|---|---|
| 1 | **窄应用**（"applied X to Y and it worked"、无可迁移洞见） | 已通过方法优先叙事消除（P3/P4 闭环） |
| 2 | **单边稿件**（全理论或全实验） | 已闭环（推导 + 2 数据集 + 统计检验 + GP + MCMC 诊断 + 高维检验） |
| 3 | **缺严谨性**（无消融/弱基线/无代码数据） | 已闭环（消融 ✓ 代码 ✓ DOI ✓）；残留：缺 ANFIS/IT2 基线（Medium） |
| 4 | **范围漂移**（真实贡献属 TKDE/ASOC/Neurocomputing/ESWA/统计期刊） | 已通过 S0020-0255 先例 + 方法定位消除 |
| 5 | 英文不清 | 语域已克制，仅个别点可再润 |
| 6 | 引用幻觉 / 诚信问题 | CrossRef 已验真；保持不夸大 novelty |

### 3.8 本稿 scope-fit 证据链与新颖性确认（2026-08 检索）★ 新增价值

**新颖性确认（关键利好）**：跨 arXiv API + 多轮 web 检索，**未发现任何已发表工作**做「TSK 后件 spike-and-slab 先验的精确 block-Gibbs 推断 + BMA 校准预测区间」。最接近的先例（必须显式引用并区分）：
- Gu, Chung, Wang — *Bayesian TSK Fuzzy Classifier*（IEEE TFS 2017，`10.1109/TFUZZ.2016.2617377`）→ 已引 `gu2017bayesian`
- Liu, Chung, Wang — *Bayesian zero-order TSK fuzzy system modeling*（Applied Soft Computing 2017，`10.1016/j.asoc.2017.01.040`）→ **未引，建议补引**
- Gu, Wang — *BTSK-JL joint structure/parameter learning*（IEEE TII 2018，`10.1109/TII.2018.2813977`）→ 已引 `gu2018bayesian`
- Miskony & Wang — *Construction of PIs using ANFIS*（Applied Soft Computing 2018，`10.1016/j.asoc.2018.04.039`）→ **未引，建议补引**
- Pan & Bester — *Marginal likelihood based model comparison in Fuzzy Bayesian Learning*（arXiv 2017）→ 可选补引（BMA/marginal-likelihood 谱系）

**IS 发表 Bayesian / prediction-interval / TSK 论文的硬证据（scope-fit 先例链，投稿信与引言可引用）**：
- *Regression trees for fast and adaptive prediction intervals*（IS 2025，Vol 686, `10.1016/j.ins.2024.121369`）
- *Multi-objective prediction intervals for wind power forecast based on deep neural networks*（IS 2021，`10.1016/j.ins.2020.10.034`）
- *Generalized collaborative relevance vector regression*（IS 2025，`10.1016/j.ins.2024.121311`，稀疏贝叶斯 RVM）
- *Learning, inference, prediction on probability density functions with constrained Gaussian processes*（IS 2023，`10.1016/j.ins.2023.119068`）
- *Active learning Bayesian support vector regression*（IS 2021，`10.1016/j.ins.2020.08.090`）
- *Construction of PIs based on deep stochastic configuration networks*（IS 2019/2020，PII `S0020025519301513`）
- 多篇 TSK 论文（Hierarchical fuzzy regression tree IS 2024、two-view deep interpretable TSK classifier IS 2024 等）→ **TSK 回归论文在 IS 很常见**

**「解析近似替代后验采样会失效」的相关理论谱系（Related Work 补强用）**：
- Gelfand & Dey — *Bayesian Model Choice: Asymptotics and Exact Calculations*（JRSS-B 1994，`10.1111/j.2517-6161.1994.tb01996.x`）
- Chipman, George, McCulloch — *The Practical Implementation of Bayesian Model Selection*（IMS Lecture Notes 38, 2001）
- Kasprzak, Giordano, Broderick — *How good is your Laplace approximation of the Bayesian posterior?*（JMLR 26, 2025）——**最贴合本稿「Laplace 协方差塌缩」诊断的当代参考文献**

**⚠️ 防御性提示**：IS 审稿人熟悉 conformal prediction / quantile regression 的 PI 文献（IS 2025 预测区间论文即是）。本稿 Discussion/Related Work **需至少一句**回应「为何不用 conformal/分位数回归」，否则审稿人会问。

---

## 四、当前论文状态快照（已核验 2026-08-15，执行时先复核再动笔）

> 本节目的是让执行 Agent **不要重复已完成的修复**。以下各项均已核验为「已闭环」，除非 Phase 1 复核推翻，否则不重做。

| 维度 | 已闭环项（勿重做） |
|---|---|
| 叙事 | 标题/摘要/贡献已方法优先；"Reproducibility Fix"/"no free lunch"/"catastrophically"/"widely-copied"/"first exact"/"generalizes to any" 全清零；"severely" 保留 3 处（事实性） |
| 摘要 | 154 词（≤200 ✓）；Farquhar 五句式；首句立一般性 UQ 贡献 |
| Keywords | 6 个，uncertainty quantification 领跑 |
| Highlights | 5 条 75/80/73/61/64 字符（≤85 ✓） |
| 数字一致性 | PICP 0.94–0.95 / BIC 0.00–0.18 / 0.41→0.94（energy-cooling）/ 摘要-引言-结果-结论-cover letter 一致（P4 终审核验） |
| 统计 | paired Wilcoxon 入文（Energy p≥0.07；Concrete p<0.01 但 ΔR²<0.01）；GP 入 Table 1；MCMC 诊断入文 + supplementary |
| 术语 | spread = per-cluster std × s 统一；方法名与代码类名映射入 README |
| 引用 | 25 条全部被引；CrossRef 验真（P4）；`jantre2025spike`/`neuralnet2024sparsetsk` DOI 已修 |
| 图 | 6 张全部被引，无孤儿图（_legacy/ 已隔离） |
| 可复现 | GitHub 已 push（main）；Zenodo DOI 可解析；SEED=42；requirements.txt |
| 声明 | Data availability / Competing interest / Generative-AI / CRediT 四段齐全 |
| 投稿信 | 致 Pedrycz；含 6 条 S0020-0255 先例 + 3 位建议审稿人 + 元数据 |

---

## 五、已知偏离痛点 / 残留风险清单（种子，Phase 2 必须先逐条闭环）★

> 严重度定义：**CRITICAL**（desk-reject / 诚信红线）→ **HIGH**（投稿前必改）→ **MEDIUM**（应改）→ **LOW**（可选）。

### A. 格式 / 投稿包层（本轮核验新发现，均可立即修复，无科学风险）

| # | 级别 | 偏离 | 证据 | 修法 |
|---|---|---|---|---|
| A1 | MEDIUM | **review 模式缺行号**：`\documentclass[review,1p,times]{elsarticle}` 未 `\usepackage{lineno}`，elsarticle review 选项不自动加行号 | manuscript.tex:1；elsdoc v3.5 | 加 `\usepackage{lineno}` + `\linenumbers`（或按官方模板改 `\documentclass[preprint,review,12pt]{elsarticle}`），重编译验证 |
| A2 | MEDIUM | **Highlights 第 4 条含缩写 "TSK"**：Elsevier Highlights 规范「No jargon/acronyms/abbreviations」；编辑第一眼看到的是 highlights | highlights.tex:22 | 改为无缩写表达，如 "Corrected a membership bug that had understated the accuracy of fuzzy models."（≤85 字符），并复核其余 4 条是否含缩写 |
| A3 | LOW | Highlights 第 3 条 `---`（em-dash）排版在「≤85 字符」计数下虽达标，但含连字符写法欠优 | highlights.tex:21 | 改为 "Clarifies when sparse model selection pays off—and when it does not."（或其他更简洁写法） |
| A4 | LOW | `references.bib` 条目 `ieeeaccess2024interpretable` 的 **key 名误导**（实际是 IEEE Trans. Fuzzy Systems 2025，非 IEEE Access 2024） | references.bib:39 | 改 key 为 `li2025gaussiancentralized` 或类似，全文同步 `\cite` |
| A5 | MEDIUM | **Highlights 需为 Editorial Manager 可上传文件**（当前仅 `.tex` 编译的 PDF）：EM 要求 Highlights 单独上传，Elsevier 建议 Word/文本 | — | 生成一份纯文本/Word 版 `Highlights.txt` 或 `.docx`（5 条内容），投稿时以 item type「Highlights」上传 |
| A6 | LOW | **Abstract 词数出处矛盾（200 vs 300）** | §3.5 | 活页复核 Guide for Authors；当前 154 词两种口径都达标，不改内容，仅记录 |

### B. 内容 / 科学层（立即修复或随 Phase 3 优化）

| # | 级别 | 偏离 | 证据 | 修法 |
|---|---|---|---|---|
| B1 | MEDIUM | **「Exact」术语未定义**：MCMC 严格说是有限样本 MC 近似（有 MC error），标题/摘要/贡献 1 用 "Exact" 可能被审稿人挑战「exact 何解？」 | 标题、manuscript.tex:29/54/137 | 在方法节（§3.4 或引言）加一句显式定义：「exact」在此指「target the exact posterior by posterior sampling, as opposed to the BIC/Laplace analytical approximation」，并指出收敛诊断（R-hat/ESS）是该声明的证据 |
| B2 | HIGH | **Related Work 缺「最近似先例」与「解析近似失效理论谱系」引用**：Liu ASC 2017 零阶贝叶斯 TSK、Miskony ASC 2018 ANFIS 预测区间、Gelfand-Dey 1994、Chipman 2001、Kasprzak JMLR 2025 均未引 | 检索 §3.8 | 补引 3–5 条，显式区分「本稿 vs 先例」：本稿是首个 spike-and-slab 精确 Gibbs + BMA 区间 |
| B3 | MEDIUM | **未回应 conformal prediction / 分位数回归**：IS 审稿人熟悉该 PI 谱系，缺一句会被追问 | 检索 §3.8 防御性提示 | Discussion 或 Related Work 加 1 句：为何选贝叶斯 BMA 区间而非 conformal/分位数（如：需模型内不确定性分解、conformal 需 hold-out 校准集、本文目标是模型选择不确定性传播） |
| B4 | MEDIUM | **新颖性未显式陈述**：检索确认无先例，但引言/投稿信未把「to our knowledge, this is the first exact spike-and-slab block-Gibbs inference for TSK consequents」写出（注意：按诚信教训，用 hedged "to our knowledge"，不用裸 "first"） | 检索 §3.8 | 引言 Related Work 末段 + 投稿信 Contribution 段各加一句 hedged novelty 陈述 |
| B5 | LOW | 引言第 2 句 "designers require calibrated uncertainty to support decisions under limited data" 的读者锚点仍偏工程应用 | manuscript.tex:44 | 可微调为「statistical/machine-learning models」语境（可选，若 Phase 1 判定已够一般化则不动） |

### C. 残留风险（P4 已判定可接受，Phase 2 只记录、不重做，除非用户决策）

| # | 风险 | 级别 | 说明 / 决策 |
|---|---|---|---|
| C-A | 缺 ANFIS / IT2-FLS / 近期稀疏模糊基线实测（已用 GP 补外部概率基线） | Medium | Related Work 已有一句「为何不适用」；若审稿人要求可补 |
| C-B | 稀疏机制在 d=8 与 d=81 都不赢（负结果转边界刻画） | Medium | 靠「sparsity design criterion + 诚实边界」回答 |
| C-C | generality 只 hedge（"applies to"）未演示第二模型族 | Low | 性价比低，不建议重做 |
| C-D | 作者 Biography ≤100 词 + 证件照：**检索未确认 IS 硬性要求** | 待活页 | 活页 Guide for Authors 若要求，补入终稿；不要求则跳过 |

---

## 六、主执行流程（强制顺序：检索 → 诊断 → 修复 → 优化 → 终审）

### Phase 0 · 联网检索刷新 IS 标准（复核归档，~20 分钟）

**目标**：在活页上复核 §3 档案，标记已变化/矛盾点；产出**本 Prompt 的官方来源复核表**。

**调用 Skill**：`ccf-submission-checker`（投稿包合规模板）、`deep-research` / `research-ops`（可选编排）。

**执行动作**：
1. 依次检索并核对（每次标注「复核一致 / 有出入 / 无法访问」）：
   - 官方 Guide for Authors：`sciencedirect.com/journal/information-sciences/publish/guide-for-authors`（ScienceDirect 常 403，用 `web.archive.org` + 检索快照 + 第三方转述）→ **重点复核：Abstract 词数 200 vs 300、长度页数/图数上限、是否有 Graphical abstract/Biography 要求**
   - Aims & Scope 原文：`shop.elsevier.com/journals/information-sciences/0020-0255`
   - Editorial Manager 门户：`editorialmanager.com/ins`（确认所需文件清单）
   - 第三方指南：`manusights.com/blog/information-sciences-submission-guide`、`scirev.org/journal/information-sciences`
2. 复核 §3.1 指标（IF/CiteScore/CCF/分区）是否有 2026 下半年更新。
3. 把「复核结果 vs §3 档案」差异写入 `P0_standards_refresh.md`，并在档案中标注最新日期。
4. **硬约束**：若发现 §3 与活页冲突，**以活页为准**，并在报告中记录冲突。

**输出**：`P0_standards_refresh.md`（复核差异表 + 最终标准清单，作为后续所有 Phase 的唯一标准来源）。

### Phase 1 · 诊断「论文 vs IS 标准」偏离（只诊断，不改写，~40 分钟）

**目标**：以 P0 最终标准为准绳，把论文五件套（manuscript / supplementary / highlights / cover letter / references）逐项对照，**产出完整偏离清单**（含 §5 种子的复核）。

**调用 Skill**（三视角并行 + 确定性核验）：
- `journal-adapt`（期刊适配视角）、`ccf-idea-reviewer`（贡献定位/新颖性评分）、`ppw-logic`（叙事链与数字一致性）
- `ccf-integrity-auditor`（数字/声明/引用/术语诚信）、`ccf-paper-reviewer`（整体科学审）、`ppw-reviewer-simulation`（模拟同行评审，多角色）
- `ccf-literature-searcher`（文献缺口）、`ccf-experiment-designer`（实验充分性/消融/基线核对）

**执行动作**：
1. 对 §5 种子清单（A1–A6 / B1–B5 / C-A…C-D）**逐条复核：确认 / 推翻 / 更新**。
2. **确定性核验**（不得靠模型记忆）：
   - 摘要词数、每行 highlights 字符数（含空格）、图数、表数、图+表合计 vs ≤8；
   - 全文数字与 `results/raw/*.json` 交叉比对（PICP / R² / RMSE / MPIW / n / d / R / τ² / 30 splits）；
   - 每个 `\cite` key 在 references.bib 存在、每条 bib 被引用、每条 DOI 用 CrossRef 验真；
   - 扫描残留语域词（§四 已清零清单 + "Exact" 定义缺失 B1）；
   - 检查 `\linenumbers` 是否存在（A1）、highlights 是否含缩写（A2）；
   - 编译四件套（latexmk），确认 0 errors / 0 undefined refs。
3. 三视角合并出**分级偏离清单**（沿用 §5 严重度定义），每条：`定位（文件:行）→ 证据 → 为什么是偏离 → 具体修法（可替换文字/公式）`。
4. **向用户汇报并取得确认后进入 Phase 2**（审计原则：先诊断不改写；若用户授权「直接修」，则跳过确认步骤）。

**输出**：`P1_偏离清单.md`（分级、证据到行号、含 §5 种子逐条复核状态）。

### Phase 2 · 立即修复偏离（先修，~1–2 小时）

**目标**：把 Phase 1 确认的 **CRITICAL + HIGH + 无争议 MEDIUM** 偏离**立即修复**（优先于任何「提升优化」动作）。「修复」= 消除不符合 IS 标准的问题；「优化」留给 Phase 3。

**调用 Skill**：`ccf-paper-writer`（定点改写）、`ppw-caption`（图注）、`ppw-literature` + `nature-citation`（补引）、`ppw-abstract`（若需动摘要）、`nature-data`（数据声明）。

**执行动作**（按下表顺序，每项修完即编译验证）：
1. **A1 行号**：manuscript.tex 加 `\usepackage{lineno}` + `\linenumbers`；编译验证行号出现在 PDF。
2. **A2/A3 Highlights**：改第 4 条去缩写、第 3 条去 em-dash 写法；逐条重计字符数（≤85）。
3. **B1 Exact 定义**：方法节加一句显式定义（见 §5-B1 修法）；同步检查 cover letter 是否需对齐。
4. **B2 补引**：把 §3.8 的 4–5 条关键文献补入 `references.bib`（Liu ASC 2017、Miskony ASC 2018、Gelfand-Dey 1994、Chipman 2001、Kasprzak JMLR 2025），在 Related Work 对应位置引用，并**显式区分本稿贡献**；更新 cover letter References 计数。
5. **B3 一句 conformal 回应**：Discussion 或 Related Work 补一句。
6. **B4 hedged novelty**：引言 Related Work 末段 + 投稿信各加 "to our knowledge …" 一句。
7. **A4 bib key 更名**、**A5 Highlights 文本版生成**、**A6 记录 Abstract 词数出处**。
8. **C 类残留**：只记录、不重做（除非用户已决策）。
9. 每步后 `latexmk` 编译；最后统一重编译四件套，核对摘要/字符/图数/引用无回归。

**硬约束**：**不重做** §四 已闭环项；**不编造数字**；改动以「最小必要」为原则（修复 ≠ 重写）。

**输出**：`P2_fixes_applied.md`（逐项：改动内容 / 文件:行 / 编译结果）+ 修订后四件套。

### Phase 3 · 整体提升优化（后优，可分模块并行）

**目标**：在「已合规」基础上，把论文从 solid 提升到 excellent——深化方法论呈现、实证深度、写作质量、文献完整性、图表表现力。**不得破坏 Phase 2 已闭环项。**

**调用 Skill**（按模块分配）：
- **叙事模块**：`ccf-paper-writer`、`research-paper-writing` / `ml-paper-writing`、`nature-writing`、`ccf-paper-to-exemplar`（若需按 IS 已发表论文范例重写某段）
- **摘要/标题/图表标题**：`ppw-abstract`、`ppw-caption`、`ppw-visualization`
- **图表**：`academic-plotting` / `nature-figure`（重绘/检查 dpi、字体、色盲友好、误差棒）
- **实验分析**：`ccf-experiment-designer`、`ppw-experiment`（讨论段落、可测发现提炼）
- **文献**：`ppw-literature`、`ccf-literature-searcher`、`nature-citation`、`get-paper`
- **语言**：`ppw-polish`（quick-fix 或 guided multi-pass）、`ppw-de-ai`（两阶段降 AI）、`nature-polishing`、`ppw-team`（按章节并行 polish/translation/de-ai）
- **科研构思**（可选，若需补强方向）：`brainstorming-research-ideas`、`creative-thinking-for-research`

**执行动作**（分模块，可并行）：
1. **叙事精修**：重读全文，验证 Title → Abstract → Contributions → Method → Results → Discussion → Conclusion 论证链无断裂、无过度声明；贡献 1–3 与结果逐一对应；Discussion 的「解析近似失效」与「稀疏设计准则」正向且克制。
2. **写作润色 + 降 AI**：全稿按 IS 语域（客观、信息密度高、American spelling）润色；跑 `ppw-de-ai` 两阶段（扫描 AI 高风险句 → 批量改写为有信息量学术表达）；统一时态/语态/术语；检查 `\ref`/`\cite` 无断链。
3. **图表**：检查 6 图 dpi/字体/配色/误差棒；图注自足性（读者不看正文能懂：设置 + 关键数字 + 结论方向）；`ppw-visualization` 复核图表类型选择。
4. **摘要/标题**：`ppw-abstract` 复核 Farquhar 五句式与 IS 风格（可给出「带标注版 + 干净投稿版」）；确认词数 ≤200。
5. **文献完整性**：补强 2024–2026 最新相关文献（Bayesian fuzzy UQ / spike-and-slab / 预测区间校准），尤其 §3.8 先例；每 2–3 句一个可引观点；清理未引条目。
6. **实验分析深化**：检查是否可提炼新的可测量发现（如「解析近似在条件数 ~1e18 病态设计矩阵上失效」作为可迁移诊断的普适性讨论）；讨论模块对照 §3.3 内容偏好补强。
7. **可选增强（不强制，用户决策）**：
   - 若补 **ANFIS / IT2-FLS 基线**（C-A）→ 用 `ccf-experiment-designer` 设计 + 跑实验 + `ppw-experiment` 写结果；
   - 若补 **conformal 对照**（B3 升级为实验）→ 同法；
   - 若制作 **Graphical abstract**（§3.5 非必需）→ 用 `academic-plotting` 生成。

**硬约束**：优化 ≠ 引入未实测的数字；凡新增数字必须来自真实运行的结果 JSON；凡新增实验记录命令与 seed。

**输出**：`P3_优化报告.md`（模块 × 改动 × 理由）+ 修订后四件套终稿。

### Phase 4 · 终审收口 + Editorial Manager 投稿 checklist（~30 分钟）

**目标**：把 P2/P3 所有修订合成到干净四件套，回验 §5 种子逐条闭环，输出**最终投稿包**与**可执行投稿 checklist**。

**调用 Skill**：`ccf-paper-reviewer`（终审）、`ppw-logic`（逻辑链终验）、`ccf-integrity-auditor`（诚信终验）、`ccf-submission-checker`（投稿就绪）、`ppw-cover-letter`（投稿信终版）、`nature-response`（如需）。

**执行动作**：
1. 合成干净四件套 + `Highlights.txt`（或 .docx）+ 建议审稿人清单，重编译（latexmk exit 0）。
2. **回验 §5 种子表**：A1–A6 / B1–B5 / C-A…C-D 逐条标注「已闭环 / 仍需处理」。
3. 最终数字一致性 + 逻辑链校验（Title→Abstract→…→Conclusion 一条线；无数字矛盾）。
4. 输出 **Editorial Manager 上传清单**：
   - Manuscript（PDF）+ LaTeX 源码包（.tex/.cls/.bib/.bst/.sty 打包，无子文件夹）
   - Highlights（单独文件）
   - Figures（6 张单独文件，核 dpi）
   - Supplementary（单独）
   - Cover letter
   - Data availability / Competing interest / CRediT / Generative-AI（已在正文）
   - 3 位建议审稿人 + ORCID + 通讯作者
5. 输出**最终报告**：分级偏离/风险清单（已闭环/仍待处理）+ 是否建议投 IS 的最终判断 + 残留风险（若有）。
6. 若用户需要，生成**投稿后跟进**材料（rebuttal 模板留给收到意见后）。

**输出**：`P4_终审报告.md` + 最终投稿包 + Editorial Manager 上传清单。

---

## 七、输出规范

1. **报告**用 Markdown，置于 `INS_review/`，按 Phase 命名（`P0_standards_refresh.md`、`P1_偏离清单.md`、`P2_fixes_applied.md`、`P3_优化报告.md`、`P4_终审报告.md`）。
2. **严重度**：CRITICAL（desk-reject/诚信）→ HIGH（投稿前必改）→ MEDIUM（应改）→ LOW（可选）。
3. **每条问题必须**：`定位（文件:行）→ 证据 → 为什么是偏离 → 具体修法（可替换文字/公式/数字）`。
4. **不改动** `results/raw/*.npz` 与 `results/raw/*.json`；重跑实验必须记录命令与 seed。
5. **不编造**：所有数字来自 `results/raw/*.json` 或已入文实测值；引用必须真实（CrossRef 验真）。
6. **活页为准**：任何 §3 与 ScienceDirect 活页冲突处，以活页为准并记录。
7. 编译验证：每次改动后 `latexmk -pdf`，最终 0 errors / 0 undefined refs。

---

## 八、Phase ↔ Skill 速查表

| Phase | 主题 | 调用 Skill |
|---|---|---|
| 0 | 标准复核 | `ccf-submission-checker`、`deep-research`、`research-ops` |
| 1 | 偏离诊断 | `journal-adapt`、`ccf-idea-reviewer`、`ppw-logic`、`ccf-integrity-auditor`、`ccf-paper-reviewer`、`ppw-reviewer-simulation`、`ccf-literature-searcher`、`ccf-experiment-designer` |
| 2 | 立即修复 | `ccf-paper-writer`、`ppw-caption`、`ppw-literature`、`nature-citation`、`ppw-abstract`、`nature-data` |
| 3 | 整体优化 | `ccf-paper-writer`、`research-paper-writing`、`ml-paper-writing`、`nature-writing`、`ccf-paper-to-exemplar`、`ppw-abstract`、`ppw-caption`、`ppw-visualization`、`academic-plotting`、`nature-figure`、`ccf-experiment-designer`、`ppw-experiment`、`ppw-literature`、`ccf-literature-searcher`、`nature-citation`、`get-paper`、`ppw-polish`、`ppw-de-ai`、`nature-polishing`、`ppw-team`、`brainstorming-research-ideas`、`creative-thinking-for-research` |
| 4 | 终审收口 | `ccf-paper-reviewer`、`ppw-logic`、`ccf-integrity-auditor`、`ccf-submission-checker`、`ppw-cover-letter`、`nature-response` |
| 全程编排 | （可选） | `0-autoresearch-skill`、`ccf-pipeline-orchestrator`、`ppw-team` |

---

## 九、附：关键数字对照表（Phase 1/4 必核）

| 项 | 基准值（当前已入文） | 出处 |
|---|---|---|
| PICP headline | 0.94–0.95（Energy 与 Concrete） | 摘要/引言/结果/结论/cover letter 一致 |
| BIC 近似法欠覆盖 | 0.00–0.18 | 摘要/结果 |
| 修正后稠密基线 | R² 0.41→0.94（energy-cooling）；0.57→0.97（heating）；0.44→0.74（Concrete） | §Repro / Fig.1 |
| Wilcoxon | Energy p≥0.07；Concrete p<0.01（ΔR²<0.01） | §Main |
| GP 基线 | R² 0.998/0.98/0.89；PICP 0.93–0.94 | Table 1 |
| MCMC 诊断 | R-hat≤1.01；ESS(σ²)>1700 | §Setup + Supplementary Table 6 |
| 高维边界 | Superconductivity d=81，R²≈0.79，PICP 0.940 | Supplementary Table 7 |
| 摘要词数 | 154（≤200 或 ≤300 均达标） | 实测 |
| Highlights | 5 条 75/80/73/61/64 字符 | 实测 |
| 图 / 表 / 引用 | 6 图 + 1 表（合计 7 ≤ 8）；25 条引用全部被引 | 实测 |
| 数据/代码 | GitHub + Zenodo `10.5281/zenodo.21929319` + SEED=42 | Data Availability |

---

*本 Prompt 由六路联网检索（2026-08-15）+ 当前稿件确定性核验生成。核心执行顺序：先检索标准 → 再诊断偏离 → 立即修复偏离 → 后整体优化 → 终审收口。*
