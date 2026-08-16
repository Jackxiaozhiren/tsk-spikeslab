# Information Sciences (Elsevier) 投稿 · 语言润色 + 降 AI 专项 Prompt（v1.0）

> **用途**：把本文件整体喂给具备「读文件 + 写文件 + 联网检索 + 调用 Skill」能力的 Agent（建议 Claude Opus 长上下文 + 开启 workflow 多智能体编排），对当前 TSK 论文做一次**以 *Information Sciences*（Elsevier）语域为准绳的「英文润色 + 自然化降 AI 痕迹」专项处理**。
> **与既有 Prompt 的分工**（勿混淆）：
> - `INS_standard_align_fix_optimize_prompt.md`（v3.0）＝**标准检索 → 偏离修复 → 整体优化**的主战略 prompt（scope/内容/科学层）。
> - `INS_style_content_optimization_prompt.md`（v2.0）＝**风格/内容偏离修复**。
> - **本文件（v1.0）＝语言层专项执行 prompt**：只做两件事——① 把英文润色到 IS 语域；② 消除 AI 味、让文本读起来像自然的人类学术写作。**不改变任何科学内容、数字、公式、引用**；不对文本做 scope/叙事层重构（那是 v3.0 的职责）。
> - **与旧版的关系**：v3.0 的 Phase 3.4 把 `ppw-polish` + `ppw-de-ai` 各一句话带过；本文件把这两者**展开为可执行的全部规则**（模式库全文、分节协议、检测→改写两阶段工作流、验证清单），并叠加 **2026-08 联网获得的检测器机制与 IS 语料证据**。
> **执行前提**：以下四件套已存在且可编译——`manuscript.tex`、`supplementary.tex`、`highlights.tex`、`cover_letter.tex`（另有 `references.bib`）。Agent 第一步必须先读这四个文件 + `INS_review/` 下最近的 `P3_优化报告.md`（避免重复处理已闭环项）。
> **最终交付**：`P5_语言润色降AI报告.md` + 四件套的润色版 `.tex`（含 `% [De-AI]` / `% [Polish]` 注释供作者逐条确认）+ 双语对照（供作者审阅）+ 一份可上编辑器/AI 检测器的对照前后文本。

---

## 〇、诚信框架与目标定位（先读，硬规则）

### 0.1 为什么「降 AI」是合法的、以及它的正确边界

- **Elsevier 官方政策（2026-06 更新，本 prompt 联网核实）**：作者可以使用 AI 工具「improve language and readability（改进语言与可读性）」、整理结构、辅助文献整理，**前提是人工审阅把关**；AI 工具「must never be used as a substitute for human critical thinking, expertise and evaluation」。**禁止**：无作者实质智力贡献地生成稿件章节、捏造/篡改数据与参考文献、把 AI 列为作者。
- **披露是硬义务**：AI 用于稿件准备，必须在**正文内、参考文献前**单独一节声明（不是 cover letter、不是致谢）。模板句（原文）：*"During the preparation of this work, the author(s) used [NAME OF TOOL / SERVICE] in order to [REASON]. After using this tool/service, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content of the published article."* 基本语法/拼写/标点检查**免声明**；但**对句式结构或组织做了实质性改动就需要声明**。
- **隐瞒才是撤稿事由**：COPE 2025 修订的撤稿指南把「undisclosed use of artificial intelligence」列为撤稿事由——触发点是**隐瞒**，不是「用了 AI」。Elsevier 是 COPE 成员。因此**本稿的正确做法是：声明 + 把文本打磨到作者真正负责的自然水准**，而不是「不声明 + 偷偷降分规避检测」。
- **检测工具不可靠，不要把它当圣旨**：Turnitin 自报文档级误报 <1%（限 AI>20% 的文档）、句级误报约 4%；斯坦福 2023 研究显示 7 种检测器把 **61.2% 的人类 TOEFL（非母语）作文误判为 AI**；COPE/ICMJE 均不背书任何商用检测产品。**作者是中文母语者**——检测分数偏高完全可能是假阳性，**绝不为了追低分而牺牲学术质量或真实性**。

### 0.2 本 prompt 的目标（一句话）

> 把「AI 助写后的英文」改写成「**自然、地道、有作者声音、符合 IS 语域**的人类学术写作」，从而**在合规披露的前提下**降低被检测器标记的概率。**降分是结果，不是目标；目标是自然度与质量。**

### 0.3 硬规则（任何时候不得违反）

1. **绝不改变科学内容**：所有公式、LaTeX 命令、`\cite{}`/`\ref{}`、变量名、模型记号、**数字结果**（PICP / R² / RMSE / MPIW / n / d / R / τ² / seed / 30 splits）、命题表述、脚注、表格/图内文字**逐字保留**。
2. **绝不新增事实/数据/引用**：不引入稿件里没有的实证声明、数据或参考文献。
3. **绝不因「润色」改变论证强度**：不把负结果改成正结果、不删减必要的限定语（`near-nominal`、`to our knowledge`、`applies to`）。
4. **声明不动**：`Declaration of Generative AI`、Data availability、Competing interest、CRediT 四段必须原样保留（若发现缺 Generative-AI 声明，报告提示补，不改写）。
5. **宁缺毋滥**：文本已经很自然地道时**保留原文**，不要为改而改；每次改写都要能解释「为什么更像人类学术写作」。
6. **不引入夸张/营销词**：不把普通表达升级成 `novel/first/state-of-the-art/powerful`；如原文已过度，按 §四 降级。

---

## 一、目标期刊语言硬指标（2026-08 联网固化）

| 项 | 要求 | 对本 prompt 的含义 | 来源 |
|---|---|---|---|
| 语言 | 英文；**「unclear because of English-language quality can be returned for rewrite before review」**（desk 语言线） | 润色不是可选加分，是 desk 存活线；目标＝让句子无需第二遍就能读懂 | Elsevier 政策 / manusights |
| 拼写 | American **或** British 可，**不可混用** | 全文统一 American spelling（含 keywords），逐个抽查 color/behaviour/utilize 等 | Elsevier 标准模板 |
| Abstract | 「concise and factual」，须能独立成篇；Editorial Manager 表单**强制 ≤200 词**（第三方实证） | 保持当前 185 词并复核；不自带数据集、首句立一般性贡献 | Elsevier 模板 + CSDN 投稿实证 |
| Keywords | **≤6 个**；避免泛化/复数/多概念（avoid *and, of* 等连接） | 现有 6 个达标；润色不增删 | Elsevier 模板 |
| Highlights | **3–5 条**，每条 **≤85 字符含空格**，单独文件（Word/文本，非 PDF），**no jargon/acronyms/abbreviations** | 全文扫描缩写（TSK、PICP、BMA 等不得出现在 Highlights）；逐条数长度 | Elsevier 官方 support 页 |
| 参考文献 | 编号制（非上标）、按正文出现顺序 | `elsarticle-num` 已达标；润色不碰 `\cite` | EndNote 样式记录 |
| 结构 | 需 Conclusion 节；摘要 1 段式（IS 不用 structured abstract） | 摘要保持单段、8–10 句 | OpenAlex 语料（见 §二） |
| 长度 | 无硬页数上限；实验类常见 6–10 图；「每节挣得空间」 | 润色可适度收紧冗余，但不过度压缩 | manusights |

> ⚠️ **投稿前人工核实项**：本 prompt 联网检索发现 ScienceDirect 显示主编信息为 **Sabrina S. Senatore 与 Zheng Z. Yan**（既有档案与 cover letter 写的是 Pedrycz）。两者可能因换届时间差并存。**改写 cover letter 称谓前，请到 editorialmanager.com/ins 或期刊页核实现任 EiC 名单**；本 prompt 不改写称谓，仅在报告中提示。

---

## 二、IS 写作风格画像（40 篇 2024–2026 近作语料分析，2026-08 联网）

> 基于 OpenAlex API 按 ISSN `0020-0255` 拉取的 40 篇 IS 论文摘要 + Crossref 抽查 10 篇 + 1 篇 OA 全文。这是**本 prompt 的语域基准**，也是「降 AI」的标靶：**不是把文本改得更像「通用好英文」，而是更像「IS 里真实发表的那类论文」。**

### 2.1 摘要结构模板（对照你自己的摘要逐条检查）

| 序号 | 动作 | IS 近作实际做法 | 本稿现状 |
|---|---|---|---|
| 1 | **开头** | **78%（31/40）以「具体对象优先」的实义句开场**，直接命名研究对象（"Random Forests (RFs) are powerful ensemble learning algorithms…"），**极少**用 "In recent years / With the rapid development of" 这类套话 | 首句 "Calibrated prediction intervals are essential…" ✅ 已符合 |
| 2 | 转方法 | 用 hinge 句："In this paper, we propose…" / "To address this issue/limitation, we propose…" | 现为 "We introduce exact inference…" ✅ |
| 3 | 结尾 | **落在带具体数字的实证结论**上（"…outperforming the state-of-the-art alternatives"、"99.6%, 99.8%, and 98.2%"），**仅 3/40 提未来工作**，无一用 "paves the way for" 收尾 | 尾句 "The approach applies to any rule-based regression…" ✅ |
| 4 | 词数 | 中位 **9 句 / 199 词 / 句均 21 词**；单段 | 当前 185 词 ✅ |

### 2.2 语域特征（重要：与直觉相反，IS 是「断言式、轻 hedge」）

- **第一人称主动**是标配："we propose" 13/40、"we introduce" 6/40、"we present" 4/40、"we show" 3/40；"this paper/study proposes" 亦常见（约 10/40）。**该用 we 的地方别改成被动**。
- **hedge 极少**："suggest" **0/40**、"might" 0/40、"may" 仅 2/40、"to the best of our knowledge" 2/40。论据扎实就直接断言。
- **"novel" 出现 17/40**，但**几乎总是具体的**（"a novel fuzzy attention mechanism"），不是空夸。**`state-of-the-art` 仅 5/40、`competitive` 5/40**——克制。
- **数字与统计检验写进摘要**：Wilcoxon signed-rank、PIT（probability integral transform）、coverage-nominal 分析等直接点名；"across more than 30,000 evaluated configurations"。
- **方法缩写（acronym）密集**：标题 9/40 嵌入缩写（FE-RNN、IGEA、SPAFIS…）；首现定义、后文复用甚至当主语。
- **可复现链接进摘要**："The code is available at github.com/…"。
- **容忍直接、简洁、偶发非母语化的表达**（"Traditional methods are not able to cop up with computing and time requirements"）。**把这种直接利落的句子过度打磨成平滑的 LLM 腔，反而是 mismatch。**

### 2.3 IS 近作「有」vs LLM 文本「有」的对比（降 AI 的精确靶子）

| IS 近作**有**（要保留/强化） | IS 近作**没有**（＝典型 AI 味，要清除） |
|---|---|
| 具体对象优先的开场 | "In today's data-driven era"、"recent years have witnessed…" 套话开场 |
| 第一人称主动 + 实义动词（propose/introduce/present/show） | 一律被动或名词化堆砌 |
| 数字、统计检验、方法缩写、可复现链接 | "comprehensive/extensive/robust" 无数字支撑的膨胀形容词 |
| 直接、信息密度高的短句与长句交错 | 句长均匀平滑、句句等长 |
| 以实证结论收尾 | 以 "paves the way for / holds great promise" 式空泛意义收尾 |
| 轻 hedge、断言式 | "may/could/potentially/pave the way" hedge 叠罗汉 |
| 逻辑递进连接 | "Moreover / Furthermore / Additionally / Notably / It is worth noting" 填充式过渡 |

---

## 三、降 AI 检测机制与证据化策略（联网证据）

### 3.1 检测器在测量什么

- **perplexity（困惑度）**：词的「可预测性」。AI 倾向低困惑度（用词可预测）；人类写作困惑度高。
- **burstiness（突发度/句长波动）**：一段文本里困惑度的变化。人类长短句交错，AI 均匀单调。
- 自 2023 秋起 GPTZero 等已迁移到**深度学习句级分类**，但上述特征仍解释其决策的大部分。Turnitin 句级误报 ~4%，且 54% 的误报句紧挨着真 AI 句（**过渡点风险最高**）。
- **结论**：与其逐字躲一个黑箱分数，不如**把文本写成「特征上像人类」**——长短句交错、标点丰富、有具体数字/人名、有作者判断、无填充过渡、无 AI 高频词。

### 3.2 实证 AI 高频词（Kobak et al., *Science Advances* 2025，15M 摘要语料）

> 词表开源：`github.com/berenslab/llm-excess-vocab`（MIT 协议）。以下为放大倍数最高者，与 §四 本地词表合并使用。

| 词 | 频率比 | 处理 |
|---|---|---|
| delves / delving | ~28× | 全删或改 investigate/examines |
| underscores | ~13.8× | 改 shows/highlights（或直接陈述） |
| showcasing | ~10.7× | 删或改 presenting/which shows |
| potential | delta 0.052 | 只在真有潜在性时用，避免每段一次 |
| findings | delta 0.041 | 改 results/observations 换用 |
| crucial | delta 0.037 | 改 important/central 或删 |

> 另据 Warwick 2025（4,820 份报告）：ChatGPT 关联标记词（delve, intricate, pivotal, comprehensive, crucial）2024 年暴增（underscore +690%），**2025 年又回落 17%（delve −78.6%）**——因为作者们在主动清除可见标记。这证明「清除可见标记」是普遍、正当的写作实践，与「未披露的 AI 代写」是两回事。

### 3.3 检测特征 ↔ 可操作改写策略（执行改写时的对照表）

| # | 人类写作特征（检测器据此区分） | 可操作改写动作 |
|---|---|---|
| 1 | **句长变化（burstiness）** | 目标句均 15–20 词；把连续 3 个长句拆/缩；长句后接短句制造强调；20+ 词才算长句 |
| 2 | **标点丰富度** | 人类多用破折号、分号、括号、问号；AI 多用单引号。**适度**引入破折号/分号/括号（但不要每段都用） |
| 3 | **具体性** | 加具体数字、变量名、数据集名、人名、算法步骤；**优先于** "researchers"/"the model"/"it" 这类泛指 |
| 4 | **作者判断（ownership）** | 写「我们为何这么选 / 这个现象意味着什么」的解释性判断句，而非中性复述 |
| 5 | **填充过渡** | 删 "Moreover/Furthermore/Notably/It is worth noting"；用**基于推理的连接词**（therefore/because/although/by contrast/this follows from…）或直接顺接 |
| 6 | **动词优先** | 名词化还原为动词："the implementation of"→"we implement"；被动→必要时主动 |
| 7 | **引用引入多样化** | 不要每句都是 "X et al. [n] proposed"；轮换 "in [ref], / [ref] showed / following [ref], we…" |
| 8 | **非均匀段落** | 段落开头用具体观察/数据而非统一模板；每段有「一句功能性主题句」 |
| 9 | **不over-polish** | 保留 IS 式直接表达，不把每句都「润得丝滑」；**过度圆滑本身就是 AI 味** |

### 3.4 非母语假阳性警告（对本文尤其重要）

- 斯坦福 2023：**61.2% 的人类 TOEFL（非母语）作文被检测器标为 AI**（97% 至少被一家标注）。驱动因素是非母语文本 perplexity 偏低（词汇复杂度低、句式规整）。
- 2026 EACL 复测：新检测器的非母语偏置可能已减弱，但仍无定论。
- **推论**：中文母语作者的英文本身就可能被误标。**本 prompt 的降 AI 目标 = 让文本「信息密度高、长短句自然、有判断」**，而不是把英文改成母语级花哨；**若检测分数仍偏高但文本自然准确，这属于检测器假阳性，不要为追分牺牲内容**。

---

## 四、反 AI 模式库（本地 Skill `ppw-de-ai` / `references` 固化，三级风险）

> 加载参考文件：`~/.claude/skills/references/anti-ai-patterns.md`（及其 `vocabulary.md` / `sentence-patterns.md` / `transitions-and-tone.md`）；改写阶段加载 `references/expression-patterns/*.md`（按章节）。

### 4.1 词汇膨胀（Vocabulary Inflation）

| 风险 | 问题词 | 替换方向 |
|---|---|---|
| **High** | groundbreaking | useful in practice |
| High | revolutionary | substantial |
| High | transformative | meaningful |
| High | unprecedented | not previously reported in this dataset/context（要有证据） |
| High | crucially | importantly / directly |
| **Medium** | robust | stable / consistent / reliable under [condition]（给出条件） |
| Medium | comprehensive | broad / multi-part / dataset-wide（说明覆盖了什么） |
| Medium | insightful | informative |
| Medium | seamless | coherent / smooth |
| Medium | leverage | use / draw on |
| **Optional** | notably | 删掉或直接写具体点 |
| Optional | significantly | materially / by X% / statistically significant（给证据） |
| Optional | effective | effective at [task]（绑定任务） |
| Optional | advanced | 具体技术描述词 |

**全量禁用清单（本地 ppw 固化）**：Accentuate, Amass, Ameliorate, Amplify, Alleviate, Ascertain, Advocate, Articulate, Bolster, Conceptualize, Conjecture, Consolidate, Culminate, Decipher, Delineate, Delve (Into), Diverge, Disseminate, Elucidate, Endeavor, Enumerate, Envision, Exacerbate, Expedite, Foster, Galvanize, Harmonize, Hone, Innovate, Integrate, Interpolate, Intricate, Leverage, Manifest, Mediate, Nurture, Nuanced, Obscure, Perpetuate, Permeate, Pivotal, Ponder, Prescribe, Prevailing, Profound, Recapitulate, Reconcile, Rectify, Reimagine, Scrutinize, Substantiate, Tailor, Transcend, Traverse, Underscore, Unveil, Vibrant, Testament, Showcasing, Intricate, Pivotal。

> ⚠️ **领域术语保护**：`landscape`（如 spatial landscape）、`robust`（统计语境）、`conjugate`、`Bayesian` 等若是**该领域标准术语且在语境中恰当**，标记为 SKIPPED，不替换。**只处理膨胀用法，不处理专业术语。**

### 4.2 句式过度声明（Sentence Overclaim）

| 风险 | 问题句 | 替换方向 |
|---|---|---|
| **High** | This proves that [claim]. | This suggests that [claim]. / The results show that [claim]. |
| High | It is undeniable that [claim]. | The evidence indicates that [claim]. |
| High | This paper completely solves [problem]. | This paper addresses [problem] by [approach]. |
| High | There is no doubt that [claim]. | The findings consistently point to [claim]. |
| **Medium** | It can be clearly seen that [claim]. | The results show that [claim]. |
| Medium | This highlights the importance of [point]. | This indicates the relevance of [point]. / 直接陈述 point |
| Medium | It should be emphasized that [point]. | [Point]. |
| Medium | This demonstrates the superiority of [method]. | [Method] performs better than [baseline] on [metric].（写实际比较） |
| **Optional** | It is worth noting that [point]. | [Point]. |
| Optional | It is important to note that [point]. | [Point]. |
| Optional | In this context, [claim]. | [Claim]. |

> ⚠️ **IS 语域校准（重要，覆盖通用规则）**：IS 摘要语料中 "suggest/may" 极少（见 §2.2），是**断言式**期刊。因此本模式库的 hedge 化改造**只用于「论据不足或因果不明」的声明**；论据充分的声明保持断言（show/demonstrate/confirm）。**不要全篇机械降级成 suggest。**

### 4.3 过渡词与语气（Transition & Tone）

| 风险 | 问题 | 替换方向 |
|---|---|---|
| **High** | Moreover, it is worth noting that [point]. | Moreover, [point].（去掉双层填充） |
| High | In conclusion, it is clear that [claim]. | In conclusion, these findings suggest that [claim].（若证据允许） |
| High | Taken as a whole, this underscores the critical importance of [point]. | Taken together, these findings indicate that [point]. |
| **Medium** | Furthermore, [generic reinforcement]. | 仅当逻辑确有递进才保留；堆叠过渡是 AI 签名 |
| Medium | On the other hand, [point]. | In contrast, [point]. / 删（无真正对立时） |
| Medium | This aligns with the broader trend that [claim]. | This pattern is consistent with prior findings on [topic]. |
| Medium | From a broader perspective, [claim]. | 换成具体尺度（methodologically / empirically / in this setting） |
| **Optional** | Overall, [claim]. | 删或移到结论 |
| Optional | In essence, [claim]. | [Claim]. |
| Optional | Importantly, [claim]. | [Claim]. / 具体说明为什么重要 |

---

## 五、分节润色 × 降 AI 协议（逐节执行基准）

> 执行顺序：先 Abstract → Introduction → Related Work → Methodology → Experiments → Discussion → Conclusion → 图注 → Highlights → Cover letter。**逐节输出、逐节确认（作者审阅双语对照后再进下一节）。**
> 每节改写时加载对应 `references/expression-patterns/<section>.md` 的推荐/避免表达，同时应用 §四 模式库 + §3.3 策略。

| 节 | IS 语域要点（做什么） | 高发 AI 痕迹（查什么/改什么） |
|---|---|---|
| **Abstract** | 首句立一般性 UQ 贡献、不自带数据集（本稿已达标）；assertive、轻 hedge；以带数字的实证结论收尾；≤200 词、单段 | "In recent years" 套话开场、句句等长、"paves the way" 式收尾、无数字的 "significant/robust"、堆叠过渡词 |
| **Introduction** | 以具体问题开场（规则回归 + 校准不确定性）；"we" 表述贡献；论证链：背景→两问题（方法性 + 可复现性）→方法→三点贡献→路线图 | "With the rapid development of" 开场、"Moreover/Furthermore" 填充过渡、"It is widely accepted that" 借来的模板句、贡献段排比过度对称 |
| **Related Work** | 按研究流组织（Bayesian TSK / sparse selection / reproducibility）而非文献列表；显式区分本稿 vs 先例；补一句为何不用 conformal/分位数回归 | 引用引入句式单一（连续 "X et al. proposed"）、"recent studies have shown" 泛泛综述、"a gap exists" 空泛 gap |
| **Methodology** | 精确、可复现、主动态；"we" 描述步骤；设计 rationale（"This design enables [benefit] while preserving [constraint]"）；不要 "we simply use" | "we leverage/harness"、"the implementation of" 名词化、被动句堆叠、每步都用 "Then the model can better learn" 式模糊能力描述 |
| **Experiments/Results** | "The results show that [finding]"；量化比较 "[Method] outperforms [baseline] by [value] on [metric]"；点名统计检验（Wilcoxon、PIT、coverage-nominal）；MCMC 诊断（R-hat/ESS）作为 "exact" 的证据 | "It can be clearly seen that"、"Obviously,"、"The results are very good."、无数字的 superiority 声明 |
| **Discussion** | 解释机制、连回研究问题；"This pattern suggests that…"（此处允许 suggest）；边界意识（"This result should be interpreted in light of [constraint]"）；回应 conformal/分位数 | "This highlights the importance of"、"Taken as a whole"、重复结果不解释、过度推广 |
| **Conclusion** | "Taken together, these findings suggest that…"；贡献陈述具体（"contributes to [field] by [specific contribution]"）；future work 具体 | "In conclusion, it is clear that"、"paves the way for"、"This paper completely solves"、新引入正文没有的内容 |
| **图注 Captions** | 自足式：方法 + 数据 + 关键数字 + 结论方向（读者不看正文能懂） | 泛泛描述、无数字、AI 腔的 "illustrates the superiority" |
| **Highlights** | 3–5 条、每条 ≤85 字符含空格、非技术性、**无缩写**、单独文件、不营销 | TSK/PICP/BMA 等缩写、em-dash 用法、营销性 "first/novel" |
| **Cover letter** | 克制、方法优先；"to our knowledge" 式 hedged novelty；scope-fit 论证（§0 之外不展开）；数字与事实 | 裸 "first"、"sits squarely within" 等过度断言、无证据的 "landmark/groundbreaking" |

---

## 六、两阶段执行工作流（Phase A 检测 → Phase B 改写）

> 对齐 `ppw-de-ai` 的两阶段设计，但按 IS 语域做两处定制：① 检测维度加入 §二 IS 语料对比 + §3.2 Kobak 词表；② 改写基准是「IS 断言式语域」而非通用「更 hedging」。

### Phase A · 检测（只扫描，不改写）

1. **读入**：四件套 + `INS_review/P3_优化报告.md`（标记已闭环项：beats→improves on、pays off→is beneficial、catastrophically 已清等，**不得回归**）。
2. **三维扫描**（单遍，全文）：
   - 词汇膨胀（§4.1 + 3.2 Kobak 词表 + 全量禁用清单）；
   - 句式过度声明（§4.2）；
   - 过渡词/语气（§4.3）；
   - **IS 语料对比**（§2.3）：套话开场、填充过渡、空泛意义收尾、hedge 叠罗汉、无数字膨胀词、句长均匀区段。
3. **分级**：High / Medium / Optional；领域术语命中标 SKIPPED（§4.1 保护规则）；Optional 级**累计 ≥3 次**才标记（单次不标，降噪）。
4. **产出检测报告**：`[#N] [级别] 类别 · 原文 → 建议 · 位置(file:行)`，汇总行 "Found N patterns (X High / Y Medium / Z Optional)" + 跳过数。
5. **非母语提示**：对 Medium 级中「语法无误但句式规整」的句子，标注「可能非母语规整，非真 AI；按 §3.4 处理」——**不强行改写，除非同时提升信息密度**。
6. 若检测报告需人工勾选（fix all High / High+Medium / 指定条目），按用户选择进入 Phase B。

### Phase B · 改写（逐节，先确认后写）

1. **按段分组改写**：同一段内多处命中**一次过**，保持段落连贯。**重组表达而非换同义词**（restructure, not synonym-swap）。
2. **加载章节表达模式**：`references/expression-patterns/<section>.md` 的推荐表达，保证改写后的句子是「该章节语境下的地道学术表达」，而非通用替换词。
3. **应用 §3.3 策略**：长短句交错（句均 15–20，长句后接短句）、适度标点、加具体数字/变量、写作者判断句、去填充过渡、动词优先、引用引入多样化、段落开头用具体观察。
4. **IS 语域守则**：该断言就断言（show/demonstrate），该 hedge 才 hedge（suggest only 当证据弱）；保留方法缩写/枚举/可复现链接/统计检验名；**不把直接利落的句子过度圆滑**。
5. **LaTeX 处理**：
   - 只改周围自然语言；`\cite{}`/`\ref{}`/`\label{}`/公式/表格/图内文字逐字保留；
   - 用 Edit 就地改；每处改写前加注释行 `% [De-AI] Original: <原文>`（多行则每行前缀）；润色类改动加 `% [Polish] Original:`；
   - 不引入加粗/斜体等原文没有的强调格式；不把段落改写成 item 列表；
   - 已有旧注释先清理再添加。
6. **双语对照**：每个被改写的段落，在会话里给出 `> **[Chinese]** …` 中文对照，供作者逐条审阅；**.tex 文件保持纯英文、投稿可用**。
7. **改写报告**：总改写数 / 按类别计数 / 跳过项 / **词数 delta（+/- N words）** / 是否建议进一步 polish。

---

## 七、验证与收口

1. **编译验证**：改写后 `latexmk -pdf` 四件套，**0 errors / 0 undefined refs**；确认 `% [De-AI]`/`% [Polish]` 注释不破坏编译（LaTeX 注释天然安全）。
2. **数字一致性回验**：改写不得触碰任何数字；用 `P3_优化报告.md` 的数字对照表抽查 Abstract/Intro/Results/结论/图注 5 处关键数字（PICP 0.94–0.95、BIC 0.00–0.18、R² 0.41→0.94、R-hat≤1.01、d=81）逐字一致。
3. **术语一致性**：`spread`（per-cluster std × s）、方法名映射、`near-nominal` 等全稿统一。
4. **IS 特质保留检查**：方法缩写仍在、可复现链接仍在、统计检验名仍在、摘要仍单段 ≤200 词、Highlights 仍无缩写且 ≤85 字符。
5. **自然度自检（每个改写句）**：
   - 读出来顺不顺（拟人度）？
   - 是否真的提升了可读性/信息密度？**若只是换词，撤销并判「检测通过」**；
   - 有没有把信息改丢、把强度改弱、把断言改糊？
6. **诚实边界自检**：无新增事实、无删减必要限定、声明段原样、无营销升级。
7. **可选降分度量（仅作信号，不作圣旨）**：若用户提供某检测器的原文分数，可在改写后对**改写段落**复测并报告 delta；同时报告「该分数受非母语偏置影响，仅供参考」。**绝不为了追分牺牲质量**。
8. **产出报告**：`P5_语言润色降AI报告.md`（检测→改写→验证三段，含 before/after 对照表、词数 delta、遗留 Optional 项）+ 四件套润色版 + 双语对照。

---

## 八、Skills 调用速查表

| 阶段 | 调用 Skill | 作用 |
|---|---|---|
| A 检测 | `ppw-de-ai` | 两阶段检测核心（三级风险、领域词保护、检测报告） |
| A 检测 | `ppw-logic` | 论证链与数字一致性基线（改前快照） |
| A 检测 | `ccf-integrity-auditor` | 声明-证据对齐、术语一致性扫描 |
| B 改写 | `ppw-polish` | 逐节润色（quick-fix 或 guided），`% [Polish]` 注释 |
| B 改写 | `nature-polishing` | 高语域润色备选（句法打磨、formal register） |
| B 改写 | `journal-adapt` | 用 IS 已发表论文语料做章节级适配（若需更强对齐） |
| B 改写 | `ppw-team` | 多章节并行派 subagent（polish + de-ai + translation 并行） |
| B 改写 | `ppw-abstract` | Abstract Farquhar 五句式复核 + 词数 |
| B 改写 | `ppw-caption` | 图注自足式重写 |
| B 改写 | `ppw-cover-letter` | Cover letter 语域收口 |
| C 验证 | `ppw-reviewer-simulation` | 以「语言审稿人」角色模拟审阅润色后文本 |
| C 验证 | `geng-academic-integrity-audit` | 最终诚信自查（无新增事实/无营销升级/声明完整） |

---

## 九、来源与证据（2026-08 联网核实）

**Elsevier 官方**
- Generative AI policies for journals（Policy updated June 2026）：elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals
- The use of Generative AI and AI-assisted technologies in writing for Elsevier：elsevier.com/about/policies-and-standards/the-use-of-generative-ai-and-ai-assisted-technologies-in-writing-for-elsevier
- AI in the review process 政策：elsevier.com/about/policies-and-standards/the-use-of-generative-ai-and-ai-assisted-technologies-in-the-review-process
- Aims & Scope / 期刊页 / Guide for Authors 目录（ScienceDirect 反爬 403，以存档+标准模板为准）：sciencedirect.com/journal/information-sciences；shop.elsevier.com/journals/information-sciences/0020-0255
- Highlights 规范（≤85 字符、独立文件）：elsevier.support/publishing/answer/how-do-i-include-highlights-with-my-manuscript
- 语言要求：elsevier.support/publishing/answer/in-which-languages-can-i-submit-my-manuscript
- Language Editing Service：webshop.elsevier.com/language-editing

**降 AI 机制与证据**
- Kobak et al., "Delving into ChatGPT usage in academic writing through excess vocabulary"（Science Advances 2025）：arxiv.org/html/2406.07016v3；science.org/doi/10.1126/sciadv.adt3813；词表 github.com/berenslab/llm-excess-vocab
- Mak & Walasek, ChatGPT marker words 2016–2025（Warwick）：wrap.warwick.ac.uk/id/eprint/195006/
- Desaire et al., 20 stylistic features human vs ChatGPT（Cell Reports Physical Science 2023）：pmc.ncbi.nlm.nih.gov/articles/PMC10328544/
- 非母语假阳性：Liang et al.（Stanford, Patterns 2023）arxiv.org/abs/2304.02819；EACL 2026 SRW 复测 aclanthology.org/2026.eacl-srw.20
- Turnitin 误报自述：turnitin.com/blog/understanding-the-false-positive-rate-for-sentences-of-our-ai-writing-detection-capability
- GPTZero 原理：gptzero.me/news/how-ai-detectors-work
- COPE 撤稿指南 2025（undisclosed AI 事由）：casrai.org/news/cope-retraction-guidelines-ai-third-party-authorship
- Editors' Statement on Responsible Use of Generative AI（Am J Bioeth 2023）：pmc.ncbi.nlm.nih.gov/articles/PMC11218843/
- CASRAI 2026 检测器采纳指南（误报、非母语、不背书）：casrai.org/guides/ai-detection-tools-adoption-academic-publishing-2026-trends

**IS 语料风格**
- 40 篇 IS 2024–2026 摘要语料（OpenAlex API，ISSN 0020-0255）：api.openalex.org/works?filter=primary_location.source.issn:0020-0255,from_publication_date:2024-01-01
- 抽查 DOI（Crossref 验证归属）：10.1016/j.ins.2024.120276、10.1016/j.ins.2025.122184 等
- 全文样例 VAR-VAE（IS 713:122184, 2025）：research.rug.nl/en/publications/probabilistic-forecasting-with-var-vae-advancing-time-series-fore/

**第三方投稿指南 / 指标**
- Manusights《Information Sciences Submission Guide (2026)》：manusights.com/blog/information-sciences-submission-guide
- SciRev：scirev.org/journal/information-sciences/
- LetPub：letpub.com/index.php?journalid=3567&page=journalapp&view=detail
- EndNote 引用样式：endnote.com/downloads/styles/information-sciences/

---

*Prompt 结束。执行顺序：读现状 → Phase A 检测 → 用户勾选 → Phase B 逐节改写（先确认后写）→ 验证收口。核心原则：不改科学内容；合规披露；把文本写成「IS 里真实发表的那类论文」，而非「通用好英文」。*
