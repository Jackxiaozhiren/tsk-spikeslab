# P5 · 语言润色 + 降 AI 检测报告（Phase A，只检测未改写）

生成时间：2026-08-16 · 依据：`INS_language_polish_deai_prompt.md` 的 Phase A 检测协议 + 四件套全文通读 + 词表机械扫描 + 句长/突发度统计脚本
范围：`manuscript.tex` / `supplementary.tex` / `cover_letter.tex` / `highlights.tex`（`references.bib` 仅引用完整性，不在语言层）
**状态：本报告只检测，未对任何 .tex 做改写。** 检测结果可直接喂给新对话（连同 `INS_language_polish_deai_prompt.md`）执行 Phase B 改写。

---

## 0. 汇总

| 类别 | 计数 |
|---|---|
| **HIGH（结构级）** | **1 项系统性 + 2 项点状**（见 §1–§3） |
| **MEDIUM（词级重复）** | 3 项（§4–§6） |
| **OPTIONAL（可选打磨）** | 3 项（§7–§9） |
| 词表硬命中（词汇膨胀/句式过度声明/过渡词） | **0 项**（既有清理已闭环，§10） |
| 跳过（领域术语保护） | `robust`（统计/技术语境）、`nominally`、`marginally` 等 |
| 已合规、勿动 | 见 §11 |

**一句话结论**：**词汇层的 AI 味已被前几轮清理干净**（无 Moreover/Furthermore/Notably/leverage/delve/paves the way 等）；**现存最大、最可检测的 AI 特征是「句长结构性」——全文句子普遍比 IS 近作长 1.5–2 倍、且缺少短句对比（低 burstiness）**。这恰是检测器与 IS 语料都最敏感的信号。降 AI 的优先级＝**先拆长句、调节奏**，其次处理 3 个词级重复，其余按 Optional 微调。

---

## 1. 【HIGH · 结构级】全文句长系统性偏长、节奏均匀（burstiness 不足）★头号发现

**证据（句长统计脚本，IS 近作语料中位句长 ≈21 词，见 §2 提示）：**

| 文件 | 句数(≥4词) | 均长(词) | 短句≤10词 | 长句≥30词 | ≥40词句子数 | 连续3+长句段数 |
|---|---|---|---|---|---|---|
| manuscript.tex | 139 | **35.9** | 11% | **60%** | 60+ | **42** |
| supplementary.tex | 38 | **40.6** | **0%** | **63%** | 25+ | 13 |
| cover_letter.tex | 24 | 28.2 | 8% | 38% | — | 1 |

**对照 IS 语料**：40 篇 IS 近作摘要中位句长 21 词、句长区间 4–40 词（4 词短句与 40 词长句并存）。本稿 **均长 36–41 词 ≈ IS 的 2 倍**，且 **几乎无短句对照**（supplementary 短句 0%）。

**最长的真实长句（≥80 词，多数可拆）：**

| 位置 | 词数 | 句首（节选） |
|---|---|---|
| manuscript.tex:79（Related Work/可复现） | ≈163 | "We quantify them on a reproduction of this pattern and release the corrected code and baselines…" |
| manuscript.tex:104（§3.2 bug 修复） | ≈143 | "The correct procedure stores the training-time centers and spreads and reuses them verbatim at inference, as in Algorithm…" |
| manuscript.tex:263（§5.4 稀疏边界） | ≈140 | "Correct fuzzy $c$-means already provides robustness to irrelevant features, so sparsity does not improve on the dense baseline in this low-dimensional regime." |
| manuscript.tex:193（§5.2 GP 基线） | ≈96 | "The Gaussian-process reference \cite{rasmussen2006gaussian} attains the accuracy of the non-interpretable Random Forest…" |
| manuscript.tex:243（fig5 图注） | ≈81 | "The Bayesian methods over-cover at the lowest nominal levels (empirical coverage 0.57 at nominal 0.5)…" |
| manuscript.tex:160（§3.5 BMA） | ≈79 | "Over posterior draws the second term spans both between-model (rule-configuration) variation and within-model parameter variation…" |
| supplementary.tex:101（R 扫描） | ≈185 | "The BIC-based approximation (TSK-SpikeSlab-BIC) collapses to negative $R^2$ at every rule count. …"（整段一个长复合句） |
| supplementary.tex:180（高维边界） | ≈125 | "The pattern of the low-dimensional benchmarks reproduces almost exactly: rule-level sparsity (TSK-SpikeSlab-Gibbs) matches the dense baselines…" |
| supplementary.tex:230（合成验证） | ≈100 | "This confirms the arithmetic of the inclusion full conditional and the BMA construction against exact computation…" |
| supplementary.tex:204（MPIW） | ≈99 | "The compact widths support the calibration claim of the main text (Section~5.3, MPIW $\approx6.7$--$32.9$)." |

> 说明：上表词数含分号/破折号连接的多个子句。**部分长句确实靠分号与破折号合法连接**，不应全拆；但 40–185 词的单句密度已远超 IS 惯例，且缺短句对照。**改写策略（Phase B）**：在分号/破折号处把 ≥40 词句子拆成 2–3 句；长句后补一句 6–15 词的短句作强调；目标均长压到 21–28 词。**不要动公式与数字。**

**风险机制（§3.3 对照表）**：检测器判据之一即「burstiness（句长波动）」，人类长短句交错、AI 均匀长句。本稿 60% 长句 + 42 段连续长句 = 低 burstiness 特征。此发现同时对应 Desaire et al. 2023 的「句长多样性」判别特征。

---

## 2. 【HIGH · 结构级】摘要句数过少、句中句子过长

- 现状：摘要 **5 句，句长 25/30/52/59/22（均 ≈38 词）**；词数 ≈188（≤200 ✅）。
- IS 语料对照：摘要中位 **9 句、中位句长 21 词**（4 词短句与 40 词长句并存）。
- 位置：manuscript.tex:33（句 3 "We introduce exact inference (up to finite Monte Carlo error)…" 52 词；句 4 "On two UCI benchmarks (three targets)…" 59 词）。
- **改写策略**：把句 3、句 4 各拆成 2 句（在分号/破折号处），使摘要约 7–8 句、句长分布更有起伏；**保持词数 ≤200、五句式叙事与全部数字不变**。

---

## 3. 【HIGH · 点状】"our method fills this gap"（cover letter）

- 位置：cover_letter.tex:20 — "To our knowledge, no prior work provides exact spike-and-slab posterior sampling with model-averaged prediction intervals for linear-consequent rule models; **our method fills this gap**. Three results structure the contribution."
- 模式：`fills (the) gap` 是典型 AI 惯用语（§4.2 句式过度声明 + §2.3 对照）。
- **改写方向**："…for linear-consequent rule models; **we develop such a sampler and prediction rule**." 或 "…; **this paper provides it**." 保留前文 "To our knowledge" hedged novelty（与 IS 语料 2/40 的用法一致，勿删）。

---

## 4. 【MEDIUM】"severely" 重复 4 处（3 正文 + 1 图注）

- 位置：manuscript.tex:54（"undercovers severely as implemented"）、:229（同）、:294（"the thresholded BIC baseline undercovers severely"）、:234（图注 "undercovers severely as implemented"）。
- 背景：P3 曾明确「severely 保留 3 处（事实性）」。鉴于每处紧跟数字（PICP $=0.00$–$0.18$），"severely" 属冗余强调。
- **改写方向（可选，不强制）**：删 "severely"，直接靠数字说话（"undercovers as implemented: PICP $=0.00$--$0.18$"）。若保留，至少把 4 处减到 ≤2 处，避免重复。
- **若新对话判定这些属「论据充分的事实性强化」，可 SKIPPED。**

---

## 5. 【MEDIUM】"essentially" 重复 3 处

- 位置：manuscript.tex:166（"dense accuracy is essentially flat from $R=4$ upward"）、:193（"the two are essentially tied"）、:229（"essentially all test points on the Energy targets"）。
- 模式：同一个填充副词 3 次（§4.3 Optional 级「累计 ≥3 次才标记」）。
- **改写方向**：至少一处换具体化（"essentially flat"→"nearly unchanged"; "essentially tied"→"differ by 0.01"（已有数字）；"essentially all test points"→"all but a small fraction" 或直接删）。保留 ≤2 处即可。

---

## 6. 【MEDIUM · 合规提示】Generative-AI 声明未用 Elsevier 官方模板句

- 位置：manuscript.tex:312–314。现文："During the preparation of this work the author used Claude (Anthropic) for code development assistance and language editing. All scientific content, methodology design, experimental results, and interpretation were performed and verified by the author."
- 2026-06 政策模板要求（§0.1）："During the preparation of this work, the author(s) used [TOOL] in order to [REASON]. **After using this tool/service, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content of the published article.**"
- **改写方向**：在现文基础上补一句模板收尾（"After using this tool, the author reviewed and edited the content as needed and takes full responsibility for the content of the published article."）。此为合规微调，非语言润色；不改动声明事实。

---

## 7. 【OPTIONAL】句首词分布略单一

- manuscript.tex：句首 "the" 27 次、"we" 12、"a" 6、"on" 5、"this" 5、"our" 5（the/we/this/our 合计 ≈37%）。
- 与 IS 语料比（句首高频为 "in this/we propose/our approach"），本稿 "the" 起句偏多，原因主要是长句把主语后置。
- **改写方向**：随 §1 拆长句自然改善；不必专项处理。

---

## 8. 【OPTIONAL】"significantly worse than every other method"（manuscript.tex:191）

- 有统计支撑（all $p<0.001$），可保留。若要更克制："markedly worse than all other methods（all $p<0.001$）" 或 "worse than every other method（all $p<0.001$）"。**不强求。**

---

## 9. 【OPTIONAL】"robust" 2 处技术语境用法

- manuscript.tex:263 / supplementary.tex:101：`robustness to irrelevant features`（有具体机制与实验支撑）与 `boundary is robust to the rule count`（有 R 扫描证据）。
- 判定：**技术断言、有证据，判 SKIPPED（领域术语保护）**，除非想更精确（"does not depend on the rule count"）。
- 另 supplementary.tex:136 "clearly underperforms" 可改为 "underperforms（$R^2=0.60$）"（数字已给）。

---

## 10. 已闭环、确认干净（新对话勿重复处理）

- **词表硬命中 0**：无 leverage / delve / underscore / showcase / unveil / intricate / pivotal / seamless / groundbreaking / revolutionary / transformative / unprecedented / notably / moreover / furthermore / harness / foster / paves the way / holds great promise / state-of-the-art / cutting-edge。
- **句式过度声明 0**：无 "This proves / There is no doubt / It is undeniable / It can be clearly seen / It is worth noting / It is important to note / This demonstrates the superiority"。
- **过渡词 0**：无 Moreover / Furthermore / Notably / In conclusion, it is clear / On the other hand / Taken as a whole。
- **开场套话 0**：无 "In recent years / With the rapid development of / In today's era"；引言首句 "Predictive models in engineering increasingly need more than point estimates…" 为具体对象优先 ✅（IS 78% 近作风格）。
- **hedge 无叠罗汉**："may behave differently"（1×）、"would strengthen"（1×）单层使用 ✅；断言式语域 ✅（"We show/confirm/attain/recovers"）。
- **被动/名词化**：无 "it is/there is/the implementation of/the use of" 堆砌 ✅（仅声明段必要被动）。
- **第一人称主动** ✅：we introduce/validate/show/implement/evaluate/compare 各 1–2 次，符合 IS 偏好。
- **Highlights 5 条 77/80/71/68/64 字符，全部 ≤85、无缩写、无 TSK** ✅（勿动）。
- **封面称谓已更新** ✅：cover_letter.tex:12 已是 "Professor Sabrina Senatore and Professor Zheng Yan"（与 ScienceDirect 现行 EiC 一致；此前档案里的 Pedrycz 已过时，**不再需要核实动作**）。
- **"as implemented" 7 处**：为全文关键对照术语，属承重词，保持（勿当填充删）。

---

## 11. 勿动清单（硬边界）

- 所有数字（PICP 0.93–0.95 / 0.00–0.18 / R² 0.41→0.94 / 0.48→0.94 / R-hat≤1.001 / ESS>1700 / d=81 / n=3000 / 30 splits 等）。
- 所有公式、`\cite`/`\ref`/`\label`、算法、表格、变量名、方法名（TSK-SpikeSlab-Gibbs / SSVS / BIC 等）。
- 限定语与诚实话术：`near-nominal`、`to our knowledge`、`applies to`、`as implemented`、`not a low-dimensional artifact`、`remains open`。
- 四段声明：Data Availability / Competing Interests / Generative-AI / CRediT（§6 只建议在 Generative-AI 段补模板收尾句，不改事实）。
- Highlights 5 条内容与字符数。

---

## 12. 给新对话的 Phase B 执行建议（优先级排序）

1. **§1 长句拆解 + 节奏调整**（全文，逐节：Abstract→Intro→Related Work→Methodology→Experiments→Discussion→Conclusion→图注→Supplementary）——**这是降 AI 的主战场**。
2. **§2 摘要拆句**（句 3/4 各拆 1 处，保持 ≤200 词）。
3. **§3 cover letter "fills this gap" 改写**。
4. **§4–§5 去重**（severely / essentially 各减到 ≤2 处）。
5. **§6 Generative-AI 声明补模板收尾句**。
6. **§7–§9 Optional 按「宁缺毋滥」原则处理**（改前自问：是否真的更自然/信息密度更高？）。

**执行时**：逐节改写 → `% [De-AI] Original:` 注释 → 双语对照 → `latexmk` 编译 0 errors → 数字/限定语回验（对照 §11）。
