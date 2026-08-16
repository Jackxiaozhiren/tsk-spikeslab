# P0 · IS 投稿标准检索刷新报告（2026-08-16 六路联网复核）

> **依据**：`INS_standard_align_fix_optimize_prompt.md` §3 标准档案（2026-08-15 冻结）。
> **方法**：6 路并行联网检索 Agent（①官方 Guide for Authors ②Aims & Scope ③Editorial Manager 门户与投稿包 ④第三方指南与审稿体验 ⑤期刊指标 ⑥新颖性复核 + 范围先例链），合计 239 次工具调用，全部返回结构化结果（6/6，0 失败）。
> **定位**：本报告是**后续 Phase 1–4 的唯一标准来源**；任何与本报告冲突的旧档案条目，以本报告为准。

---

## 0. 检索可靠性声明（重要，先读）

| 源 | 可访问性 | 影响 |
|---|---|---|
| ScienceDirect 官方 Guide for Authors / Aims & Scope / Editorial Board 活页 | **HTTP 403**（WebFetch / curl 全浏览器头 / r.jina.ai / allorigins / /pdf / /print / elsevier.com 均失败） | 官方 Guide 唯一可用副本为 **web.archive.org 2024-03-04 快照**；IS 专有细则以其 + 活页 Elsevier 通用政策（2026-08-16 实抓）+ 第三方 2026 指南交叉验证。**2026 年内若有细则变更无法 100% 排除**，建议投稿前用浏览器（登录/JS 环境）在期刊官网复核一次 |
| editorialmanager.com/ins | HTTP 200，但长期横幅「**Site under development. Do not use for live manuscript submission.**」（2025-08 / 2026-02 快照亦同，非临时维护） | 投稿门户需从期刊官网「Submit your article」按钮确认实际入口 |
| submit.elsevier.com/INS | HTTP 200，但返回**与任意期刊代码一致的通用 SPA 壳**（用假代码验证） | INS 映射无法由此确认 |
| SciRev / manusights（2026-06-18 更新）/ LetPub / justscience / xueshu / myhuiban / journalmetrics / arXiv API / DOI 落地页 | 全部可直访 | 审稿体验、指标、先例链的主要实证来源 |

---

## 1. 复核差异表（vs §3 档案）

判定说明：**✅确认**（与档案一致）｜**🔄更新**（档案过时，以活页为准）｜**⚠️警示**（影响投稿动作）｜**❓无法核实**（登录墙/403，投稿前人工复核）。

### 1.1 期刊身份与硬指标

| 档案值（§3.1） | 活页实测（2026-08） | 判定 |
|---|---|---|
| 定位句 "publish original, innovative and creative research results" + "balanced coverage of both theory and practice" | Elsevier Shop 逐字一致（含 "fully acknowledges ... breadth of the discipline"） | ✅ 确认 |
| 文章类型：Original research work 为主；Short Communications；综述/教程选择性 | 主类型确认（manusights 2026）；Short Communications 见 2026 期目次（Vol 728/731/754）；综述/教程 "selective ... higher bar" | ✅ 确认 |
| **EiC：Witold Pedrycz（Alberta）+ Zheng Yan（西电）Co-EiC** | **EiC 已变更为 Sabrina Senatore（Università degli Studi di Salerno, Italy）；Zheng Yan 仍为 Co-EiC**。Elsevier Shop 活页、Senatore LinkedIn、Yan 西电主页三源一致；where2submit 仍列 Pedrycz（数据滞后）。ScienceDirect 编委页 403，未能直接读官方编委名单 | 🔄 **更新（高风险项，见 §2-1）** |
| 影响因子：ScienceDirect 显 6.8，2025 JCR 实为 6.0 | **当前 JIF = 6.0（2025 数据，JCR 2026 于 2026-06-17 发布）**；ScienceDirect 主页仍显 6.8（滞后，已确认）。5 年 IF ≈ 6.0 | ✅ 确认（6.8 为上一度量年值，**不得引用为当前值**） |
| CiteScore 14.4–14.6 | **14.6（CiteScore 2025，2026-06-05 发布）**；SD 主页仍显 14.4（滞后） | ✅ 确认 |
| SJR ≈1.5–1.8；H-index 255 | **SJR 1.507（2025，低于 2024 的 1.803）**；H-index 255（稳定） | ✅ 确认 |
| JCR Q1（CS, IS）；CCF-B；中科院 1 区 TOP | Q1 确认（CS/IS 百分位 81.6%）；CCF-B 确认 | ✅ 确认 |
| 中科院分区 | **两源矛盾**：unionpub/kejianyi 称仍 1区TOP；另一路检索见「2024 事件后降为 2 区」；且中科院分区表据称已停止更新（ablesci 2026-03）。**仅影响投稿决策，不写入稿件** | ⚠️ 警示 |
| 2024 On Hold 事件 | 确认 2024-06-17 置入、**2024-08-26 解除**；2024 数据 JIF 恢复 6.7996（2025-06 发布）；自引率 17.3%（2022）→14.7%（2024）→**5.0%（2025）**；年发文 1400→894（2025）；**截至 2026-08 无新 On Hold / 预警，WoS 状态 Active** | ✅ 确认 |
| 审稿速度：首轮 3.1–3.3 月；全程 6.5–6.7 月；1.8–2 轮；desk reject ~1 天 | SciRev 实值：首轮 3.1 月、全程 6.5 月、轮数 1.8、报告数 2.6、即时拒稿 1 天——全部一致 | ✅ 确认 |
| 审稿严苛度 4.0/3.2/2.8 | SciRev 实值 4.0/3.2/2.8 全部一致 | ✅ 确认 |
| 接受率 ~22.5% | LetPub 实值 22.5%（**注意：LetPub 页 URL 已从 journalid=1753 变更为 3567**） | ✅ 确认 |
| 近期限流：Graph-based AI / 6G-AI-native / Privacy-risk | **Graph-based AI 特刊确认**（投稿截止 2026-06-30）；**Privacy-risk evaluation 特刊确认**（ScienceDirect 官方页）；**6G/AI-native 特刊不属 IS**——属于《Digital Communications and Networks》（另一本 KeAi/Elsevier 期刊），**档案系误植** | 🔄 更新 |

### 1.2 Aims & Scope 与范围红线

| 档案值 | 活页实测 | 判定 |
|---|---|---|
| 范围内主题：Soft Computing / Fuzzy Logic and Approximate Reasoning / Symbolic-Numeric and Statistical Techniques / Modelling and Computing with Words / Computational Intelligence | 全部仍逐字在列（Elsevier Shop 活页） | ✅ 确认 |
| 「fuzzy 外壳 → 必被路由 ASOC」系误判 | 确认；desk 触发点仍是**窄应用、单边稿件、缺严谨性、范围漂移、英文质量** | ✅ 确认 |
| 第一筛选器：fit screen（一般性贡献首眼可见） | manusights 2026 明确 "narrow application with no general informatics or computational-intelligence contribution" 为拒稿模式 #1 | ✅ 确认 |

### 1.3 格式硬要求

| 档案值（§3.5） | 活页实测 | 判定 |
|---|---|---|
| Abstract 词数 200 vs 300 矛盾 | **官方 Guide 定论：200 词**（"Abstract (of up to 200 words)"）；300 词在 IS 任何来源均查无实据 | ✅ 确认（200；当前 154/175 均达标） |
| 长度：实验类 ≤40 双倍行距页 + 8 图/表；理论类 ≤45 页 + 10 或 20 图/表 | 官方：实验 40 页 + 8 图/表；理论 45 页 + 10 图/表。「20 图/表」替代值查无实据 | ✅ 确认（当前 22 页、6 图+1 表=7，达标） |
| Graphical abstract 非必需 | 确认：Guide 无该项；清单仅 "Graphical Abstracts / Highlights files (**where applicable**)" | ✅ 确认 |
| **作者 Biography：待确认** | **IS 硬性要求「Vitae」：每位作者 ≤100 词传记 + 证件照，可编辑格式（Word），非 PDF**（2024 官方快照）。Elsevier 通用支持（2026-05）对参考著作给 ≤200 词，IS 专属为 100 词——投稿时再核一次 | 🔄 **更新（缺失项，见 §2-2）** |
| Highlights：3–5 条 ≤85 字符、单独文件、禁缩写 | 活页 Elsevier（2026-08-16 实抓）确认：3–5 条、≤85 字符含空格、禁 jargon/缩写、**以 Word 文件按「Highlights」item type 上传**；「**final files 阶段才必需**」，Guide 措辞为「optional yet highly encouraged」 | ✅ 确认（**+2 细则**） |
| **行号**：review 模式应加 lineno | IS/Elsevier 作者指南**无行号要求**（仅 troubleshooting 支持页提及）；「single anonymized + 至少 2 审稿人」确认。当前稿已加 `\lineno`——保留即可，非硬性 | ✅ 确认（非必需） |
| 四声明 | Competing interests（共享声明，Attach Files 上传，**无需签名**）✅；CRediT（要求，14 角色，位于致谢上方）✅；Data availability（「where appropriate」软性要求，但 Elsevier 新版面日益要求，**建议保留正文现有声明**）✅；**Generative AI 声明（要求，官方节标题为「Declaration of Generative AI and AI-assisted technologies in the writing process」，置于参考文献正上方）** | ✅ 确认（⚠️ 当前正文节标题为「Declaration of Generative AI」，未与官方全名一致，见 §2-4） |

### 1.4 投稿包与政策（Editorial Manager）

| 档案值（§3.6） | 活页实测 | 判定 |
|---|---|---|
| 门户 editorialmanager.com/ins | **活页长期横幅「Site under development. Do not use for live manuscript submission」** | ⚠️ 警示（见 §2-5） |
| 上传项：Manuscript PDF + LaTeX 源包（.tex/.cls/.bib/.bst/.sty 无子文件夹） | 可编辑源文件必需（官方确认）；`.tex/.cls/.bib/.bst/.sty` 扩展清单与「无子文件夹」为 EM Attach Files 登录后配置，活页不可见 | ✅ 部分确认 |
| Highlights 单独文件 | 确认（独立 item type） | ✅ 确认 |
| Cover letter 可选但强烈建议 | Elsevier/EM 标准项；IS 是否必需为期刊配置，活页不可见 | ✅ 部分确认 |
| 建议审稿人 ≥3；不得为编委/近期合著者；地域多样 | **排除规则逐字确认**（"should not suggest reviewers who are colleagues, or who have co-authored or collaborated with you during the last three years"）；「≥3」「地域多样」未见于任何可访问来源（应为 EM 登录后步骤） | ✅ 部分确认 |
| ORCID 投稿时收集 | 2024 Guide 快照无 ORCID 条款；manusights 2026 列 ORCID 为必填项之一；Elsevier EM 可设 optional/required——**无 IS 专属「强制」明文**，但为 Elsevier 通行做法 | ✅ 部分确认 |
| SSRN 预印本 | 确认：投稿时可附免费 SSRN 预印本，**通过 desk 后才公开** | ✅ 确认 |
| 引用诚信 | On Hold 后审查趋严；Crossref 验真建议保留（现 38 条，P4 已验） | ✅ 确认 |

### 1.5 早期退稿模式（desk 四筛 + 语言线）

manusights 2026-06-18 实抓，五条全部确认，与档案 §3.7 逐条对应：①窄应用 ②单边稿件（"all theory with no validation, or all validation with no theory"）③缺严谨性（"no ablation, weak or outdated baselines, no reproducibility"）④范围漂移（data-engineering / soft-computing / pure-application）⑤英文不清（"can be returned for rewrite before review"）。

### 1.6 新颖性与范围先例链（2026-08 复核）

| 档案值（§3.8） | 2026-08 复核 | 判定 |
|---|---|---|
| **新颖性：无已发表工作做「TSK 后件 spike-and-slab 精确 block-Gibbs + BMA 校准区间」** | **仍成立**。arXiv API 组合检索：`Takagi-Sugeno × spike-and-slab` = 0；`fuzzy × spike and slab` = 0；`Takagi-Sugeno × Gibbs` = 0；`Takagi-Sugeno × Bayesian` 唯一命中为 arXiv 2009.00822（2020，聚类式贝叶斯 T-S 辨识，Type-2 Student-t 隶属度，非 spike-and-slab block-Gibbs） | ✅ 确认（novelty 声明安全） |
| 近邻先例（Gu 2017 / Liu 2017 / Gu 2018 / Miskony 2018） | 四条全部以 DOI/落地页精确确认 | ✅ 确认 |
| 近邻新工作（2024–2026 模糊预测区间） | 均为**非贝叶斯或非 TSK**：Guven/Koklu/Kumbasar Type-2 FLS 区间（FUZZ-IEEE 2024）、Cartagena 等 Evolving Fuzzy PIs（IEEE TETCI 2024）、Alves 等金融模糊区间（Comput Econ 2025）等——**不推翻新颖性**，Phase 3 可考虑补 1–2 条作为最近邻（LOW） | ✅ 确认 |
| spike-and-slab Gibbs / BMA 区间 2025–2026 活跃于线性/频率派（COLT 2025、arXiv 2601.07864、arXiv 2510.16224、CBMA ICLR 2025 等） | 均不涉 TSK，**反而强化「TSK 缺口」新颖性** | ✅ 确认 |
| IS 范围先例链（回归树 PI / 风功率 DNN PI / 协同 RVM / 约束 GP / 主动学习 B-SVR / 随机配置网络 PI） | 全部精确确认（DOI 落地）。**一处措辞修正**：Qiu et al. 题为 "Generalized collaborative **relevance vector regression**"（非 "RVM"） | ✅ 确认 |
| 理论谱系：Gelfand-Dey 1994 / Chipman 2001 / Kasprzak 2025 | 三条全部确认。**两处元数据待修**：①Chipman 页码：references.bib 记 65–134，Project Euclid/Wharton 实为 **65–116**；②Kasprzak 标题应含完整副标题 "Finite-sample computable error bounds **for a variety of useful divergences**" | ⚠️ 需修（Phase 1 复核，见 §2-6） |

---

## 2. 对本稿的可执行影响（供 Phase 1/2 闭环）

| # | 影响 | 级别 | 处理建议 |
|---|---|---|---|
| 2-1 | **投稿信致 Pedrycz 已过时**：EiC 现为 **Sabrina Senatore**（Zheng Yan 为 Co-EiC） | HIGH | Phase 2 更新 cover_letter 抬头/称谓至 Senatore（或改中性称谓如 "Dear Editor-in-Chief"）；投稿前从期刊官网编委页再确认一次 |
| 2-2 | **作者 Biography 为 IS 硬性要求且当前缺失**：≤100 词 + 证件照，Word 可编辑格式 | HIGH（终稿阶段） | Phase 4 投稿包准备时补 1 段 ≤100 词 Biography + 照片（可编辑格式）；投稿时再核 100 vs 200 词口径 |
| 2-3 | Highlights 需「单独 Word/文本文件、按 Highlights item type 上传」；「final files 阶段才必需」 | MEDIUM | 现有 `Highlights.txt` 已达标（5 条 ≤85 字符）；投稿时按 item type 上传，可补 `.docx` 版 |
| 2-4 | Generative AI 声明节标题与官方全名不一致 | LOW | 可对齐为官方标题 "Declaration of Generative AI and AI-assisted technologies in the writing process" |
| 2-5 | editorialmanager.com/ins 横幅警示「Do not use for live manuscript submission」 | 警示 | 投稿前从期刊官网「Submit your article」按钮确认实际门户（可能为 submit.elsevier.com 或迁移后的 EM） |
| 2-6 | 引用元数据两处：Chipman 页码 65–134 vs 65–116；Kasprzak 标题副标题 | LOW | Phase 1 用 CrossRef/Project Euclid 复核后修正 references.bib |
| 2-7 | IF 现值 6.0（2025 数据）；SD 主页 6.8 为滞后 | 记录 | 任何正文/封面信/材料不得引用 6.8 作为当前值（现稿件未引用 IF，无此风险，仅记录） |
| 2-8 | 6G/AI-native 特刊不属 IS（档案误植） | 记录 | 修正档案；不影响本稿 |
| 2-9 | CAS 分区 1区TOP vs 2区 矛盾 + 分区表停止更新 | 记录 | 仅投稿决策用，不写入稿件 |

---

## 3. 最终标准清单（Phase 1–4 唯一标准来源）

### 3.1 投稿类型与评审
- 主类型 **Original research work**；单盲评审，**≥2 位独立审稿人**；desk reject 最快 ~1 天。

### 3.2 硬性格式
| 项 | 标准 |
|---|---|
| 模板 | `elsarticle`（review 得 1.5 倍行距，Times）|
| Abstract | **≤200 词**（当前 154/175 达标）|
| Keywords | 4–6 个，紧接摘要，避免与标题重复 |
| Highlights | 3–5 条、**每条 ≤85 字符含空格**、禁缩写/术语、**单独 Word 文件**（final-files 阶段必需）|
| 长度 | 实验类 **≤40 双倍行距页 + 8 图/表**；理论类 45 页 + 10（当前 22 页、6 图+1 表=7 达标）|
| 图规格 | PDF 单文件；线稿 ≥1000 dpi、彩图 ≥300 dpi、组合 ≥500 dpi；字高 ≥6–7 pt |
| 必备节 | Abstract + **Conclusions**；编号章节；American spelling |
| **Vitae（新增确认）** | **每位作者 ≤100 词传记 + 证件照（Word 可编辑）** |
| 行号 | 非必需（已加，保留即可）|
| Graphical abstract | 非必需 |

### 3.3 必备声明（置于参考文献前）
1. **Declaration of competing interests**（共享声明，EM Attach Files 上传，无需签名）
2. **CRediT**（14 角色）
3. **Data availability**（软性要求，建议保留）
4. **Declaration of Generative AI and AI-assisted technologies in the writing process**（置于参考文献正上方）

### 3.4 投稿包（Editorial Manager）
- Manuscript PDF + LaTeX 源包（.tex/.cls/.bib/.bst/.sty，无子文件夹）；Highlights 单独文件；Figures 单独；Supplementary 单独；Cover letter（可选但强烈建议）；Data/Competing/CRediT/GenAI（正文已含）；建议审稿人（排除近 3 年合著者/同事，≥3）；ORCID；SSRN 预印本（可选，desk 后才公开）。
- **⚠️ 门户：editorialmanager.com/ins 现显示「Site under development」横幅——投稿前从期刊官网「Submit your article」进入确认。**

### 3.5 审稿预期
首轮 ~3.1–3.3 月；全程 ~6.5–6.7 月；~1.8 轮 / ~2.6 报告；desk reject ~1 天；难度 4.0/5.0；报告质量 3.2/5.0；处理体验 2.8/5.0；接受率 ~22.5%。

### 3.6 desk 四筛 + 语言线（五条）
窄应用 / 单边稿件 / 缺严谨性（无消融、弱基线、不可复现）/ 范围漂移 / 英文不清可退稿重写。

### 3.7 引用诚信
引用必须真实（CrossRef/落地页验真）；On Hold 事件后审查趋严；避免过度自引。本稿 38 条引用须在 Phase 1 逐条验真。

---

## 4. 来源清单（主要）

- 官方 Guide for Authors（**2024-03-04 存档副本**）：https://web.archive.org/web/20240304043814/https://www.sciencedirect.com/journal/information-sciences/publish/guide-for-authors （活页 403）
- Aims & Scope（Elsevier Shop 活页）：https://shop.elsevier.com/journals/information-sciences/0020-0255
- Highlights 规范（Elsevier 活页，2026-08-16 实抓）：https://www.elsevier.com/researcher/author/tools-and-resources/highlights
- CRediT 政策（Elsevier 活页）：https://www.elsevier.com/researcher/author/policies-and-guidelines/credit-author-statement
- Generative AI 声明政策（Elsevier 活页）：https://www.elsevier.com/about/policies-and-standards/the-use-of-generative-ai-and-ai-assisted-technologies-in-writing-for-elsevier
- Editorial Manager：https://www.editorialmanager.com/ins （⚠️「Site under development」横幅）
- SciRev：https://scirev.org/journal/information-sciences/
- manusights 2026 投稿指南：https://manusights.com/blog/information-sciences-submission-guide
- LetPub（journalid=3567）：https://www.letpub.com/index.php?journalid=3567&page=journalapp&view=detail
- 指标：journalmetrics.org / wos-journal.info/journalid/19574 / sci.justscience.cn/details.html?id=1633 / scijournal.org/inform-sciences / myhuiban.com/journal/115 / xueshu.com/sci/41535/01.html
- On Hold 历史：ea-iset.org/h-nd-1294.html / unionpub.cn/keyan/20240828.html
- 先例链与理论谱系 DOI 落地页：见 §1.6 所列各 DOI（10.1109/TFUZZ.2016.2617377 等）

---

*本报告由 6 路并行检索 Agent 生成（2026-08-16），作为后续 Phase 的唯一标准来源。标注「⚠️ 投稿前人工复核」项：EiC 名单、Biography 100/200 词口径、EM 门户、中科院分区。*
