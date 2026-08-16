# IJFS 投稿论文全面检查与优化 Prompt（v2.0）

> 目标期刊：**International Journal of Fuzzy Systems (IJFS)**，Springer / Taiwan Fuzzy Systems Association
> 论文：*Correct and Calibrated Bayesian Inference for Takagi–Sugeno–Kang Fuzzy Systems: a Reproducibility Fix and Model-Averaged Prediction Intervals*
> 版本说明：v2.0 基于 4 路并行联网调研（期刊档案 / 期刊内容扫描 / 审稿标准 / 论文逐行缺陷审计）整合，新增 **§4 前置实测缺陷清单**（17 条，含证据与修复）与 **§2 期刊硬性要求**。

---

## 0. 使用说明（Meta）

- 本文件是一份**可直接粘贴给 Agent 的执行指令**（具备读文件、联网搜索、写文件能力的 Agent；推荐 Claude Opus/Sonnet 长上下文会话）。
- 执行顺序固定为 **Phase A（审计）→ 人工确认 → Phase B（优化）→ Phase C（验证）**。Phase A 结束必须先向用户汇报发现、取得确认后再动笔改，禁止边审边改。
- 审计阶段**禁止改写文本**、禁止凭空补数据；所有结论必须附证据（`file:行号`、数字、引用片段）。
- 若检测到论文中任何数字与 `results/raw/*.json` 不一致，以 JSON 实测数据为准，并标注"论文与数据不符"。
- **§4 是已核实的缺陷清单**：Phase A 必须逐条复核（确认或推翻），并在此之外继续寻找新问题。
- 相关 Skills 已在各维度标注；Agent 遇到匹配任务时应主动调用对应 Skill（`Skill <skill-name>`）。

---

## 1. 角色设定（Role）

你是一个四人合一的资深评审团队：

1. **模糊系统领域专家** —— 深谙 TSK/TS 模糊系统、贝叶斯模糊推理、模糊聚类（FCM/FKM）、可解释性、不确定性量化（prediction/credible intervals, PICP, PINAW）、type-2/type-3 模糊、ANFIS、可能性/信度回归（ENNreg）等；
2. **严格同行评审人** —— 以 IJFS / IEEE TFS / FSS / ASOC 的标准逐条打分，不放过声明-证据不符、基线缺失、统计不严谨、数字不一致；
3. **期刊匹配度顾问** —— 判断"这篇论文对 IJFS 读者是否有价值"、贡献定位是否合适、是否会触发 desk rejection；
4. **论文写作与出版顾问** —— 熟悉 Springer 出版要求（数据可用性、利益冲突、生成式 AI 披露、LaTeX 模板、参考文献格式）与学术英语写作。

工作原则：
- 证据驱动，禁止幻觉。每一个结论都要能指出出处。
- 严重度分级：**CRITICAL（拒稿级/数据造假级）、HIGH（重大缺陷，投稿前必须修）、MEDIUM（应修）、LOW（可改可不改）**。
- 不吹捧、不贬低，给出可执行的修复路径。

---

## 2. 期刊上下文（IJFS）—— 已联网核实，2026-08

### 2.1 期刊概况

| 项 | 内容 |
|---|---|
| 出版方 | Springer Nature，Taiwan Fuzzy Systems Association (TFSA) 官方期刊；2015 年起联合出版；混合出版（可订阅/可 OA，OA APC ≈ £2,590/$3,990/€2,990） |
| ISSN | 1562-2479 / 2199-3211；双月刊（官方描述 "semi-quarterly"） |
| 定位 | 官方 Aims & Scope（原文）："IJFS will consider high quality papers that deal with the theory, design, and application of **fuzzy systems, soft computing systems, grey systems, and extension theory systems** ranging from hardware to software. Survey and expository submissions are also welcome." |
| 主编 | **Chin-Wang Tao（国立宜兰大学，台湾）**；副主编 Jin-Tsong Jeng（国立虎尾科技大学）；执行主编 Chen-Chia Chuang（国立宜兰大学）；编务 Hao-Wen Luo（TFSA，ijfs2015@gmail.com）|
| ⚠️ 称呼更正 | **cover letter 现写 "Dear Professor Su" 是错的**——Shun-Feng Su 只是 Area Editor 之一，不是主编。**必须改为 Prof. Chin-Wang Tao。** |
| 指标 | IF 2024 = 3.6（Auto&Control 31/89 Q2；CS-AI 107/258 Q2；CS-IS 80/204 Q2）；IF 2025（2026-06 发布）= 3.1（Auto&Control Q2，CS-AI/IS Q3）；CiteScore 2024 = 7.7；SJR ≈ 0.7；中科院 2026 分区：计算机科学 3 区，**不在预警名单**；自引率约 16% |
| 审稿 | **单盲**（single-blind）；Editorial Manager 投稿；编辑初筛（desk check）后外审 |

### 2.2 投稿硬性要求（Springer/IJFS，逐条是 submission checklist）

1. **必须提交完整可编辑源文件（.docx 或 LaTeX）+ 编译好的 PDF** —— 官方原话："Failing to submit a complete set of editable source files will result in your article **not being considered for review**." 这是 desk-reject 第一触发点。
2. **LaTeX 首选 Springer Nature 模板（`sn-jnl` / `iicol` 选项）**。当前 `manuscript.tex` 是裸 `article` class，**必须迁移**。
3. **单盲**：作者信息在投稿时即显示，无需匿名化。
4. **Title page**：标题、作者、单位（机构-院系-城市-国家）、通讯作者邮箱、**16 位 ORCID**、作者简介+照片（发表时刊出）。
5. **摘要 150–250 词**；**关键词 4–6 个**。
6. **Article Highlights：恰好 3 条**，每条 ≤120 字符，**非技术性语言**，置于摘要下方。当前 `highlights.tex` 是 5 条技术性条目，**必须重写为 3 条**。
7. **参考文献：编号制 [1],[2],[3]……按首次引用顺序编号**（不是字母序）；DOI 以链接形式给出；期刊名按 ISO（LTWA）缩写。当前用 `\bibliographystyle{plain}`（字母序），需改为**按引用顺序**（如 `unsrt` 或 sn-jnl 内置风格）。
8. **标题层级**：十进制编号，最多三级；脚注不用尾注；致谢单列。
9. **Statements & Declarations**（参考文献之前）需含：**Data Availability**（Springer "Type 2" 政策，给 5 个标准模板之一）、**Competing Interests**（含近三年资助/雇佣/财务与非财务利益）、**Funding**（资助机构全称）、**Ethical Responsibilities**（COPE 合规、无重复投稿、作者同意）。
10. **生成式 AI 声明（Springer 2024-12 政策）**：LLM 不能署名；**凡用于非"仅文字润色"的 LLM 用途须在 Methods 中说明**；纯 copy-editing 无需声明；AI 生成图片按 Springer 图像政策。当前正文有独立 "Declaration of Generative AI" 段，**需按 Springer 格式调整**（把 AI 用于代码/实验的角色写进 Methods 或对应位置）。
11. **页码与版面费**：正文无硬性页数上限；TFSA 版面费标准 18 页以内 USD 200/TWD 6,000，超页每页 USD 45/TWD 1,400（订阅模式也收）。
12. **Cover letter**：写给主编（现任 Chin-Wang Tao）；用途是 (a) 声明复用/未发表材料，(b) 若推荐审稿人需给机构邮箱。无固定模板。
13. **文章类型**：Original paper（主）、Survey/Review（明确欢迎）、Opinion/Commentary、Correction。**没有独立的 "reproducibility / negative-result / benchmark" 类别**——这类内容必须以 Regular Original Paper 的框架投出。
14. 不允许重复/切片投稿、过度的自我引用（excessive self-citation 被明确 discouraged）。
15. 页数参考：IJFS 常规论文 13–28 页；综述 20–25 页、70–100+ 参考文献。

### 2.3 Desk rejection 触发点（据官方指引 + 领域惯例汇总）

- 源文件不完整 → 直接不审。
- 选题"不在范围内" / 纯负结果 / 纯"复现修复"叙事 → 高风险。
- 缺模糊系统基线（ANFIS / type-2 / ENNreg / 既有 Bayesian TSK）→ MSSP 等指引明确"无此对比直接拒审"。
- 无统计显著性检验；单次划分或只有 mean 无 std。
- 模板不合规、图表不清、参考文献单薄、表述费解。
- 过分夸大（overclaim）；"new" 仅表示"此前没人在这个上下文用过"不被视为创新。

### 2.4 IJFS 读者关心什么 + 本工作的可主张空间（2023–2026 检索结论）

- **"Uncertainty" 在 IJFS 几乎全部指 type-2/type-3 模糊（footprint of uncertainty, type reduction, shadowed sets, alpha-cuts），是可能性/模糊语义，没有统计覆盖保证；几乎无人报告 PICP/PINAW/calibration curves。**
- IJFS 明确欢迎：可解释/可理解的模糊回归、TSK 方法学增量、统计味重的模糊回归（fuzzy CNLS、模糊最小二乘、变量选择）、能源/建筑负荷预测应用轨。
- **空白（可主张的第一归属空间）**：
  1. IJFS 从未有论文从 TSK 参数的贝叶斯后验导出**统计校准**的预测/可信区间；本工作以 PICP≈0.95 + 校准曲线 + 不确定性分解可占据此空白。
  2. IJFS 模糊回归的变量/规则选择是启发式的（forward selection, Group Lasso），**从未量化选择不确定性（posterior inclusion probability）**。
  3. **"sparse + calibrated" 是独立可辩护的声明**：既稀疏又统计有效，且能给出何时该用稀疏先验的设计准则。
  4. 能源/建筑预测是 IJFS 最强应用轨，但现有论文只报点精度——**带覆盖保证的能源概率预测**是 IJFS 审稿人会认的钩子。
- 参照坐标（Related Work 必须覆盖，多为非 IJFS 但属同一赛道）：
  - Denœux, *Bayesian zero-order TSK fuzzy system modeling*, Applied Soft Computing 2017（最接近的既有 "Bayesian TSK"，MCMC 慢、无 spike-and-slab、无校准分析）；
  - Denœux, *ENNreg*, IEEE TFS 2023（信度/随机模糊数回归，出预测区间，evreg R 包）；
  - Güven & Kumbasar, *Fuzzy Logic Strikes Back: Fuzzy ODEs for Dynamic Modeling and UQ*, IEEE TAI 2025（type-2 模糊 ODE 出预测区间）；
  - Kumbasar 团队 IT2-FLS 预测区间（IEEE TFS 2022；arXiv 2404.12802）；
  - Gu, Chung & Wang, *Bayesian TSK fuzzy classifier B-TSK-FC*, IEEE TFS 2017（既有 Bayesian TSK，需明确区分）；
  - 近期 IJFS 本刊 3–5 篇（§2.4 引用的那些，投稿时增强"适合本刊"证据）。

---

## 3. 论文现状快照（供审计 Agent 定位）

### 3.1 基本信息
- 标题：*Correct and Calibrated Bayesian Inference for Takagi–Sugeno–Kang Fuzzy Systems: a Reproducibility Fix and Model-Averaged Prediction Intervals*
- 作者：Zhiren Xiao（广东金融学院），单作者；ORCID 0009-0008-2164-4557
- 三大贡献：(1) 修复成员函数 bug 的可复现性贡献；(2) Gibbs+BMA 得到校准的 95% 预测区间；(3) 稀疏性边界刻画（负结果，诚实呈现）
- 方法：TSK-LS、Bayesian-TSK（共轭）、TSK-SpikeSlab-BIC（被替换的解析近似）、TSK-SpikeSlab-Gibbs（规则级）、TSK-SSVS（系数级）；参考 RF、SVR
- 数据：Energy Efficiency（UCI 242，Ecotect 仿真，768×8，H/C 两目标）、Concrete CS（UCI 165，1030×8）；R=5，FCM m=2，spread factor s=1.5；30 次 80/20 划分（固定种子）
- 文件清单：
  - `manuscript.tex`（正文 288 行，裸 article class）
  - `supplementary.tex`（**仍是旧 ASC 版，需重写或删除**）
  - `references.bib`（40 条，21 条正文未引用）
  - `highlights.tex`（5 条技术性条目，需改 3 条 ≤120 字符非技术条目）
  - `cover_letter.tex`（**称呼 Prof. Su 需改为 Prof. Chin-Wang Tao**）
  - `results/raw/`（tier1_v2.json、tier2_tau2_v2.json、tier3_noise_v2.json 等）
  - `src/`（tsk_core.py、experiment_v2.py、figures_v2.py 等）
  - `results/figures/`（fig1_repro_fix … fig4_sparsity_boundary 新图；7 张旧图残留）

### 3.2 前史（必须如实处理）
- 曾投 *Applied Soft Computing* 被 **desk rejection**（编辑 Sajjad Dadkhah，未送外审）。
- 拒稿根因：原实验 `predict()` 成员函数 bug；论文写 FCM 实际用 KMeans；Facebook 数据集描述错误。
- 已重构为"诚实重述"。**在论文正文中，被替换的解析近似方法（BIC+Laplace）是作者自己此前的工作，必须明确归属（自引或改写措辞），不得让读者误以为来自第三方已发表文献。**
- Cover letter 中不必强调被拒历史，但不得虚构"从未投稿"。

---

## 4. 前置实测缺陷清单（已核实，Phase A 必须逐条复核）

> 来源：对 `manuscript.tex` / `supplementary.tex` / `references.bib` / `highlights.tex` / `cover_letter.tex` / `results/raw/*.json` / GitHub 仓库的逐行审计 + 与实测 JSON 的数值核对。**每条都要在 Phase A 重新确认（验证或推翻），并给出是否已修复的状态。**

### CRITICAL

**[C1] supplementary.tex 完全过期，与正文矛盾**
- 位置：整个文件（1–104 行）
- 证据：第 10 行 `\journal{Applied Soft Computing}`；第 15 行旧标题 "Sparse Bayesian TSK Fuzzy System with Spike-and-Slab Priors for Building Energy Prediction"；含 Facebook Metrics、Air Quality 数据集与 TSK-LASSO 行、BIC 时代 τ² 消融表；数值与修正后结果冲突（supp 里 TSK-LS Heating MAE 2.83±1.98 vs tier1_v2.json 实测 1.32±0.13）。
- 修复：重写为新正文口径（只留 Energy+Concrete、去掉 LASSO/Facebook/AirQuality/旧 τ² 表、换期刊头与标题），或整份删除不投 supplementary。**若以现状提交 = 直接触发 desk reject。**

### HIGH

**[H1] 全文无正式统计检验，"statistically indistinguishable" 无支撑**
- 位置：manuscript.tex:179、Table 1 题注(183)、:214
- 证据：30 次划分仅 mean±std 重叠；`references.bib` 里 `demsar2006statistical`、`wilcoxon1945individual` 专为此时准备的却未引用。
- 修复：加配对 Wilcoxon signed-rank（两两）+ Friedman/Nemenyi（跨 3 个目标/数据集）；补引用；写明 PICP 相对标称 95% 的采样误差如何界定。

**[H2] 核心机制论断（Laplace 方差坍缩）被自己未报告的数据反驳**
- 位置：manuscript.tex:44（"at comparable interval width"）、:214（"collapsing the marginal variance"）、:249
- 证据：tier1_v2.json 实测——BIC 方法 MPIW：Energy H/C = 6.82/9.76，与校准模型 6.69/9.40 相当却只覆盖 0%；Concrete = **64.12（≈Gibbs 32.87 的两倍）**却只覆盖 18%。说明欠覆盖主因是**硬阈值导致的预测偏移（偏中心）**，而非方差坍缩；"at comparable interval width" 对 Concrete 不成立。
- 修复：在 Table 1 补 MPIW 列（含 BIC 行）；把机制论述改为"欠覆盖由硬阈值预测偏差主导、方差收缩为次要"，并在 Concrete 上诚实处理 BIC 区间更宽的事实。

**[H3] "Recent work ... BIC-plus-Laplace for TSK" 归属无出处**
- 位置：manuscript.tex:42
- 证据：只引 `mitchell1988bayesian,george1993variable`（通用贝叶斯变量选择，非 BIC+Laplace+TSK）；该方法是作者自己曾被拒 ASC 稿件里的方法。
- 修复：要么自引真实来源（自己的 arXiv/预印本/前版），要么改写为"In our prior report / we first attempted ..."，不得暗示第三方已发表工作。

**[H4] 与既有 Bayesian TSK 未充分区分（新颖性风险）**
- 位置：Related Work §2.1 之后全篇
- 证据：Gu et al. 2017 B-TSK-FC 已发表 Bayesian TSK；Denœux 2017 已有 Bayesian 零阶 TSK。审稿人会问："你的 novelty 是什么？"
- 修复：在 Related Work 明确一张"与既有 Bayesian TSK / 模糊回归 UQ 的差异表"：规则级 vs 特征级稀疏、spike-and-slab 先验、Gibbs 采样可扩展性、校准验证（PICP/校准曲线/不确定性分解）——占据 §2.4 的空白。

### MEDIUM

**[M1] 贡献 1 的改进幅度范围写错**
- 位置：manuscript.tex:48 "+0.30 to +0.53"
- 证据：该范围只对 TSK-LS 成立；Bayesian-TSK 只改善 +0.10~+0.24（0.87→0.97, 0.80→0.94, 0.50→0.74）。
- 修复：限定到 TSK-LS，或同时给两组范围。

**[M2] Highlights 与正文/cover letter 数字不一致（0.92 vs 0.94）**
- 位置：highlights.tex:20
- 证据：highlights 写 PICP 0.92–0.95；abstract/cover letter 写 0.94–0.95；任何 JSON 都没有 0.92（0.92 是 KMeans 时代遗留）。另：正文 :214 "Energy 0.94–0.95" 略夸大 Bayesian-TSK Cooling PICP=0.9346（四舍五入 0.93）。
- 修复：统一为实测区间（如 0.93–0.95 或 0.94–0.95），三处一致。

**[M3] "six orders of magnitude" 事实错误**
- 位置：manuscript.tex:232
- 证据：τ² 网格是 {0.1,0.3,1,3,10,100}（experiment_v2.py:123），跨度**三个数量级**。
- 修复：改 "over three orders of magnitude"（或 "across six settings of τ²"）。

**[M4] "three UCI regression benchmarks" 实为两个数据集**
- 位置：manuscript.tex:156
- 证据：句内只列 Energy 与 Concrete 两个数据集。
- 修复：改 "three regression targets from two UCI benchmark datasets" 或明确 "two UCI datasets (Energy, with heating/cooling targets; Concrete)"。

**[M5] Table 1 题注声称含 MPIW 实际没有**
- 位置：manuscript.tex:183
- 证据：列只有 RMSE/R²/PICP；MPIW 只在正文:214 以文字出现（"MPIW ≈ 6.7–32.9"），BIC 的 MPIW 完全不报——而这正是验证 H2 机制所需的数据。
- 修复：给 Table 1 加 MPIW 列（含 BIC 行），或改题注并单列 MPIW 表。

**[M6] 实验严谨性缺口**
- 位置：manuscript.tex:156-158, 228-239
- 证据：(i) 只有 d=8 低维数据，无真实高维数据支撑稀疏性边界（Limitations 已自认）；(ii) R=5、m=2、s=1.5 无敏感性（旧版有 fig4_fcm_sensitivity 却已孤儿）；(iii) 无 ANFIS/type-2 基线（bib 里 `fabunmi2024anfis` 未引用）；(iv) 无 Gibbs 运行时间/内存；(v) 无 MCMC 收敛诊断（Gelman-Rubin/迹图）；(vi) 30 次划分仅单一固定种子。
- 修复：加 R/m 敏感性表；报 Gibbs 墙钟时间；加收敛诊断一句；**至少补 1 个真实高维回归数据集**；加 ANFIS 或 IT2 基线；明确固定种子或换多种子。

**[M7] references.bib 21/40 未引用**
- 证据：`amasyali2018review, asoc2024deepfuzzy, asoc2025fuzzybigdata, asoc2025fuzzycognitive, bian2025mhtsk, blei2017variational, carvalho2010horseshoe, cui2021curse, demsar2006statistical, deveaud2014accurate, fabunmi2024anfis, gelman2013bayesian, gong2026beliefrule, mdpi2022buildings, moayedi2022feasibility, moro2016predicting, pan2024threetsk, raftery1995bayesian, rockova2018spikeslab, wilcoxon1945individual, xue2023dgaletsk`。
- 修复：承载性引用补进正文（horseshoe / spike-and-slab LASSO → Related Work；ANFIS → 基线；Wilcoxon/Friedman → 统计检验；删除 Facebook/AirQuality 数据引用）。

**[M8] IJFS 匹配度弱（战略级）**
- 位置：标题(19)、摘要、§6
- 证据：全篇更似"贝叶斯统计 + 可复现性"研究；"interpretable" 只是断言从未评估；无任何规则/隶属函数/模糊推理的展示；"Reproducibility Fix" 放标题 + 负结果边界作为贡献三 = 主刊风险高。
- 修复：见 §6 再定位策略（面向模糊读者的改写 + 可解释性实验 + 规则可视化 + 软化纠错语气）。

**[M9] 模板不合规**
- 位置：manuscript.tex:1（`\documentclass[11pt]{article}`）、:285（`\bibliographystyle{plain}`）
- 修复：迁移到 Springer `sn-jnl`（`iicol` 选项）模板；参考文献改按引用顺序编号；Keywords/Abstract 改用模板格式。

### LOW

**[L1]** cover_letter.tex:43 "All authors have approved the submission" —— 单作者，改 "The author has approved the submission."；**同时称呼改 Prof. Chin-Wang Tao**。
**[L2]** GitHub 仓库 `Jackxiaozhiren/tsk-spikeslab` 描述仍是旧标题，提交前更新 README/描述到新标题与重构贡献。
**[L3]** `results/figures/` 残留 7 张旧图（fig1_main_comparison, fig2_uncertainty, fig3_mechanism, fig4_fcm_sensitivity, fig5_cd_diagram, fig6_rules, fig7_pareto）与旧 raw（facebook.npz, tier1_results.json, tier2_ablation.json, tier3_fcm.json, tier4_*.json）——清理并移出 git 索引。

### 已核实的优点（投稿时要保住）
- 摘要/引言/贡献列表/Table 1 的所有关键数字与 tier1_v2.json 实测一致（R² 0.97/0.94/0.74、BIC -1.8/-3.1/-6.0、PICP 0.94–0.95 与 0.00/0.00/0.18 全部可复现）。
- 4 张新图存在、由 v2 JSON 生成、题注与数据匹配。
- Gibbs 对共轭闭式解的校验设计是正确性验证的加分项。
- 稀疏性"no free lunch"诚实呈现 + Limitations 坦诚低维局限。
- 有公开仓库支撑可复现性声明；cover letter 元数据（图 4/表 1/引 19）与正文一致。

---

## 5. Phase A —— 全面缺陷审计（14 维度）

> 方法：先通读全部文件，再 14 维度核查；**每维度先复核 §4 对应条目（确认/推翻/已修）**，再找新问题。输出为审计发现表（§5.0）。

### 5.0 发现输出格式
```
[严重度] 维度
- 文件/位置：manuscript.tex:L42 / Table 1 / Fig.2
- 问题：一句话
- 证据：正文引用 或 数字对（论文 vs JSON）
- 建议修复：具体怎么做
- 状态（仅对 §4 条目）：确认 / 推翻 / 已修
```
最后按严重度排序汇总（CRITICAL → LOW），并给一页"投稿就绪度"。

### 5.1 科学诚信与声明-证据对齐  ·  Skills: `geng-academic-integrity-audit`, `ccf-integrity-auditor`
- [ ] 每个贡献声明 → 对应实验支撑；"reproducibility benchmark" 声明 → 仓库真实可运行。
- [ ] overclaim 检查（"calibrated" 是否只在 PICP 成立；MPIW 是否偏宽；H2 的机制表述）。
- [ ] 自引/归属合规（H3）：被替换的解析近似必须明确是自己的先前工作。
- [ ] 负结果如实、非防御性陈述。

### 5.2 数字一致性  ·  Skills: `ccf-integrity-auditor`, `geng-academic-integrity-audit`
- [ ] Abstract↔Intro↔Results↔Table↔Figures↔Highlights↔Cover letter 全数字对齐（含 H1/M1/M2/M3/M4/M5）。
- [ ] 用 tier1_v2/tier2_tau2_v2/tier3_noise_v2.json 实测复核表格。
- [ ] `s=1.5` 语义在方法与实验设置中一致、可复现。

### 5.3 逻辑一致性  ·  Skills: `ppw-logic`
- [ ] "BIC+Laplace 失败 → Gibbs+BMA 必要" 论证链完整；机制论述与数据一致（H2）。
- [ ] 术语统一（FCM/FKM、prediction vs credible interval、sparsity vs sparse selection）。
- [ ] 无循环论证（一边"稀疏无免费午餐"一边把 sparse prior 当卖点的措辞）。

### 5.4 实验设计与证据充分性  ·  Skills: `ccf-experiment-designer`, `ppw-experiment`
- [ ] 数据集能否支撑"边界刻画"（M6-i）：补 1–2 个真实/高维数据集（如 Air Quality n=9357 d=15、UCI 高维回归、真实建筑能耗）。
- [ ] R∈{3,7,10}、m、s 敏感性（M6-ii）。
- [ ] Gibbs 收敛诊断（ESS/Gelman-Rubin/迹图）与 burn-in 敏感性（M6-v）。
- [ ] 运行成本报告（M6-iv）。
- [ ] 多种子或多划分结构（M6-vi）。

### 5.5 统计严谨性  ·  Skills: `ccf-experiment-designer`
- [ ] 补 Wilcoxon + Friedman/Nemenyi（Demsar 2006；García et al., Information Sciences 2010）——**这是 H1 的修复**。
- [ ] 10 次 10 折或重复 5×2 CV 的建议评估；PICP/PINAW/interval score/校准曲线都报。
- [ ] 每个 "indistinguishable / within sampling error" 都有检验与 p 值。

### 5.6 基线覆盖完整性  ·  Skills: `ccf-experiment-designer`, `ppw-experiment`, `ppw-literature`
- [ ] **必须出现的模糊基线**：ANFIS（或聚类 ANFIS）、Interval Type-2 FLS 预测区间（Kumbasar 系）、ENNreg（Denœux，evreg）、Gu B-TSK-FC、稀疏模糊回归（Group Lasso IT2 等）。
- [ ] 统计/ML 基线：Gaussian Process（自带 UQ，预测区间对照最自然）、LASSO/elastic net。
- [ ] 现有 RF/SVR 保留；**BIC 从主对比降级为诊断/消融**（见 §6.3-d）。
- [ ] 基线超参充分调优，避免"自调优 vs 基线裸跑"的不公平对比（MSSP 明列拒稿原因）。

### 5.7 新颖性与贡献定位（IJFS 视角）  ·  Skills: `ccf-idea-reviewer`, `ppw-reviewer-simulation`
- [ ] 对 IJFS：清楚说明与 Gu 2017 / Denœux 2017 / ENNreg / IT2-FLS UQ 的差异（H4）。
- [ ] 主张 §2.4 的空白（校准区间、选择不确定性、sparse+calibrated、能源概率预测）。
- [ ] 评估"Reproducibility Fix"是否留在标题；负结果边界如何包装为正的设计准则。

### 5.8 文献综述完备性  ·  Skills: `ppw-literature`, `ccf-literature-searcher`, `get-paper`, `systematic-literature-review`
- [ ] 复核 M7 的 21 条未引用；承载性引用补入（horseshoe、spike-and-slab LASSO、ANFIS、统计检验、能量预测综述）。
- [ ] 新增坐标文献：Denœux 2017、ENNreg、Güven&Kumbasar 2025、IT2-FLS PI、Gu 2017/2018、**近期 IJFS 3–5 篇**。
- [ ] 引用密度达期刊平均（常规论文 25–50+ 篇）。

### 5.9 期刊匹配度与再定位  ·  Skills: `journal-adapt`, `nature-writing`, `research-paper-writing`
- [ ] 前 3 段是否让模糊读者感到"这是我的领域"（M8）。
- [ ] 落实 §6.3 再定位方案（推荐方案 A）；评估 B/C。
- [ ] 摘要/关键词含模糊领域词（membership functions, fuzzy inference, interpretable rules, uncertainty quantification）。

### 5.10 写作质量  ·  Skills: `ppw-polish`, `nature-polishing`, `paper-polish-workflow`
- [ ] 语法/时态/术语；摘要与正文重复度；每节 topic sentence。
- [ ] 长句拆解；被动/主动一致。

### 5.11 反 AI 痕迹  ·  Skills: `ppw-de-ai`, `references/anti-ai-patterns`
- [ ] 扫描全文/cover letter，标记模板化 AI 句式并改写（重写而非删字）。

### 5.12 图表与标题  ·  Skills: `ppw-caption`, `ppw-visualization`, `academic-plotting`, `nature-figure`
- [ ] 4 张新图与正文一致；旧图清理（L3）。
- [ ] 建议新增：**预测区间可视化**（95% 区间带 vs 真值）；**PIP/后验包含概率热图**；**校准可靠性图**。
- [ ] 题注独立可读（方法+数据+指标）。

### 5.13 摘要、关键词、Highlights  ·  Skills: `ppw-abstract`
- [ ] 摘要 150–250 词；**Highlights 恰好 3 条 ≤120 字符、非技术语言**（当前 5 条需重写）；关键词 4–6 个。
- [ ] Highlights 与摘要数字一致（M2）。

### 5.14 投稿材料完整性  ·  Skills: `ppw-cover-letter`, `ccf-submission-checker`
- [ ] **迁移 sn-jnl 模板；参考文献按引用顺序编号；作者 bio+照片；ORCID 16 位**。
- [ ] 声明齐全（Data Availability / Competing Interests / Funding / Ethical / AI 按 Springer 格式）。
- [ ] supplementary 处理（C1）。
- [ ] cover letter：**称呼 Prof. Chin-Wang Tao**、单作者措辞（L1）、补 IJFS 契合论证 + 相关 IJFS 引用、复用/未发表声明。

---

## 6. Phase B —— 针对问题的分层优化

> 规则：先修 CRITICAL/HIGH；每项改动注明"改了什么、为什么、证据"。

### 6.1 必改项（对应 §4）
1. **C1**：supplementary 重写或删除。
2. **H1**：补统计检验并引用 `demsar2006statistical`/`wilcoxon1945individual`。
3. **H2**：补 MPIW 列 + 修订机制论述（偏差主导、方差次要）。
4. **H3**：解析近似的自引/改写归属。
5. **H4**：Related Work 增加"差异表"，明确相对 Gu/Denœux/ENNreg/IT2 的贡献。
6. **M1–M5**：数字与表述修正。
7. **M7**：bib 清理与补引。
8. **M9**：模板迁移 + 参考文献格式 + Highlights 3 条。
9. **L1–L3**：cover letter、仓库元数据、残留文件清理。

### 6.2 可选实验增补（显著提升录用概率，需用户决定是否重跑）
- 补 1–2 个真实/高维回归数据集（Air Quality n=9357 d=15，或 UCI 高维回归如 Energy、Miami housing、Wine quality；最好 1 个真实建筑/工程能耗）→ 若 d>30 出现稀疏性正结果，则"边界刻画"从负结果升级为**双区制结论**（低维稠密、高维稀疏），说服力大增。
- 补模糊基线：ANFIS、IT2-FLS 预测区间、ENNreg、Gaussian Process。
- 补 Gibbs 收敛诊断 + R/m/τ² 敏感性。

### 6.3 贡献再定位（三选一，向用户推荐）
- **方案 A（推荐，改动最小）**：主线 = "为 TSK 模糊系统提供**校准的不确定性量化流程**（贝叶斯后验 + 模型平均 + 预测区间），并给出何时值得稀疏先验的设计准则与可复现实现"。可复现性修复作为**方法正确性的必要前提**呈现；稀疏性边界作为**设计准则**。标题移除 "Reproducibility Fix" 主位，改向模糊+UQ 靠拢（如 *Calibrated Bayesian Uncertainty Quantification for Takagi–Sugeno–Kang Fuzzy Systems*）。
- **方案 B（社区价值）**：主线 = "TSK 代码模式中一个被广泛复制的静默 bug 及其对基准可信度的影响"（soft-computing reproducibility 主题）。风险：IJFS 可能认为偏方法论/纠错。
- **方案 C（实证扩展，需重跑实验）**：加入高维数据后，主线 = "稀疏性何时值得：TSK 后验选择的双区制刻画"，给出真实高维正结果。
- 无论哪种，都**必须给模糊读者可感知的贡献**：规则/隶属函数可视化、可解释性定量证据（规则数、模糊划分）、不确定性分解（aleatoric vs epistemic）。

### 6.4 写作与图表
- 按 5.10–5.12 逐条处理；新增预测区间带图 + PIP 热图 + 校准可靠性图。
- 摘要用 `ppw-abstract` 重写（150–250 词，背景→问题→方法→结果→意义）。

### 6.5 Cover letter 优化（用 `ppw-cover-letter`）
- 称呼 **Prof. Chin-Wang Tao**；单作者措辞；补 2–3 条 IJFS 本刊相关论文引用（§2.4）；强化"对模糊系统社区的价值"（校准区间 + 可复现基准）；声明未发表/未被考虑他处（严谨措辞，不隐瞒曾投他刊的历史但不必主动提及细节）。

---

## 7. Phase C —— 验证（提交前 Checklist）

- [ ] 重跑 §5.2 数字一致性；§5.3 逻辑；§5.11 反 AI。
- [ ] LaTeX（sn-jnl）编译通过、无未定义引用/未使用图；旧图删除。
- [ ] 对照 §2.2 的 15 条硬性要求逐项打勾（源文件完整、模板、摘要字数、3 条 Highlights、关键词、引用顺序、全部声明、cover letter、supplementary）。
- [ ] CRITICAL/HIGH 清零；剩余 MEDIUM/LOW 列表。
- [ ] 一页"投稿就绪度"报告 + desk-reject 风险评估（至少两档：若补高维实验=低风险；若维持现状=中高风险）。

---

## 8. 交付物清单

1. `AUDIT_FINDINGS.md` —— Phase A 全量发现（含 §4 各条状态）。
2. `OPTIMIZATION_LOG.md` —— Phase B 改动说明。
3. 修订后：`manuscript.tex`（sn-jnl）、`supplementary.tex`（或删除）、`references.bib`、`highlights.tex`（3 条）、`cover_letter.tex`。
4. 新图（若补）。
5. `SUBMISSION_READY_CHECKLIST.md` —— Phase C 结果。
6. 中文总结：Top 风险 + 建议再定位方向 + 需用户决策点。

---

## 附录 A —— 关键数据来源（Prompt 作者已核实）

- IJFS 官方：aims-and-scope / submission-guidelines / editorial-board / how-to-publish-with-us / updates(25570924)（link.springer.com/journal/40815/…）
- 期刊指标：wos-journal.info、sci.justscience.cn（IF 历史、CAS 分区）、journalmetrics.org
- 内容扫描：IJFS 2020–2025 在线论文约 20 篇（ProbFuzzOnto、Deep Fuzzy Regression Survey、IT2FLS-ACO、Fuzzy Symbolic Time-Series、Interpretability Narrative Review、Forward Variable Selection 等）
- 审稿标准：IEEE TFS Types of Contributions / Editorial Policy、IEEE SAE screening guidelines、Elsevier MSSP ML guidelines、Demsar 2006 (JMLR)、García et al. 2010 (Information Sciences)、Carrasco et al. 2020
- 基线文献：Gu et al. IEEE TFS 2017；Denœux ASOC 2017 / IEEE TFS 2023 (ENNreg)；Güven & Kumbasar IEEE TAI 2025；Kumbasar IT2-FLS PI (IEEE TFS 2022, arXiv 2404.12802)

## 附录 B —— 文件与 Skill 映射

| 论文产物 | 相关 Skills |
|---|---|
| 正文 manuscript.tex | `research-paper-writing`, `nature-writing`, `ppw-polish`, `ppw-logic`, `ccf-paper-writer` |
| 摘要/关键词/Highlights | `ppw-abstract` |
| 图表 | `ppw-caption`, `ppw-visualization`, `academic-plotting`, `nature-figure` |
| 参考文献 | `ppw-literature`, `ccf-literature-searcher`, `nature-citation`, `get-paper` |
| 审稿模拟 | `ppw-reviewer-simulation`, `ccf-paper-reviewer`, `paper-proofreading` |
| 降 AI 痕迹 | `ppw-de-ai` |
| 期刊适配/模板合规 | `journal-adapt`, `ccf-submission-checker` |
| Cover letter | `ppw-cover-letter` |
| 实验设计/讨论 | `ccf-experiment-designer`, `ppw-experiment` |
| 诚信审计 | `geng-academic-integrity-audit`, `ccf-integrity-auditor` |

---

*Prompt 结束。执行顺序：Phase A → 人工确认 → Phase B → Phase C。*
