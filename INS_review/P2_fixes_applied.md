# Phase 2 · 修复日志（IS 标准偏离项 A/B 类立即修复）

生成时间：2026-08-15
依据：`INS_standard_align_fix_optimize_prompt.md` §5 种子清单（A1–A6 / B1–B5），本次会话确定性核验 + 六路联网检索结论。
范围：仅「修复偏离」，不做整体优化（Phase 3 待用户指令）。所有改动已 `latexmk -pdf` 编译验证（四件套均 exit 0、0 errors、0 undefined）。

---

## A. 格式 / 投稿包层

### A1 · review 模式补行号 ✅
- **改动**：`manuscript.tex` preamble 加 `\usepackage{lineno}` + `\linenumbers`（elsarticle review 选项不自动加行号，elsdoc v3.5 已确认）。
- **验证**：lineno.sty 加载成功；PDF 首页 margin 行号（3、4…）可见；稿件 19 页。
- **影响**：审稿友好，符合官方模板对 review 模式的建议。

### A2 · Highlights 第 4 条去缩写 "TSK" ✅
- **改动**：`highlights.tex` 第 4 条 `understated TSK accuracy` → `depressed fuzzy-system accuracy`（Elsevier Highlights 规范禁缩写/术语）。
- **字符数**：68（≤85 ✓）。

### A3 · Highlights 第 3 条去 em-dash 写法 ✅
- **改动**：`worthwhile---and when it is not` → `worthwhile and when it is not`（避免 `---` 排版冗余）。
- **字符数**：71（≤85 ✓）。
- **新 highlights 字符集**：75 / 80 / 71 / 68 / 64。

### A4 · bib key 更名（误导性 key）✅
- **改动**：`references.bib` `ieeeaccess2024interpretable` → `li2025gaussiancentralized`（元数据正确但 key 误标 IEEE Access 2024，实为 IEEE Trans. Fuzzy Systems 2025）；`manuscript.tex` `\cite` 同步。
- **验证**：全文无旧 key 残留。

### A5 · Highlights 纯文本版（Editorial Manager 上传用）✅
- **新增**：`Highlights.txt`（5 条内容与 highlights.tex 同步），EM 上传时以 item type「Highlights」提交。

### A6 · Abstract 词数出处矛盾（200 vs 300）✅ 已记录
- **记录**：官方 Guide for Authors 两出处分别读「≤200 词」与「≤300 词」，同份 Scribd 存档（2025-08-10 抓取）。当前摘要 **154 词，两种口径均达标**，不改内容；投稿前在 ScienceDirect 活页复核一次即可。

---

## B. 内容 / 科学层

### B1 · 「Exact」术语显式定义 ✅
- **改动**：`manuscript.tex` §3.4（L140）在「we sample it exactly with a block-Gibbs sampler」后加一句：
  > Here ``exact'' means that we target the posterior by sampling rather than replacing it with a BIC-plus-Laplace analytical surrogate; as with any MCMC procedure the estimates carry finite Monte Carlo error, which we quantify with the convergence diagnostics of Section~\ref{sec:setup}.
- **目的**：预判审稿人挑战「MCMC 何来 exact」；用已入文的 R-hat/ESS 诊断支撑该声明。

### B2 · Related Work 补引最贴近先例 + 解析近似失效理论谱系 ✅
- **新增 6 条 bib**（`references.bib`，总数 25 → **31**）：
  1. `liu2017bayesianzero` — Bayesian zero-order TSK（Applied Soft Computing 2017）
  2. `miskony2018predictionintervals` — PI via ANFIS（Applied Soft Computing 2018）
  3. `gelfand1994bayesian` — Bayesian model choice exact vs asymptotic（JRSS-B 1994）
  4. `chipman2001practical` — Practical implementation of Bayesian model selection（IMS 2001）
  5. `kasprzak2025laplace` — Laplace 近似误差界（JMLR 2025）
  6. `vovk2005algorithmic` — Conformal prediction（Springer 2005）
- **正文引用**（`manuscript.tex`）：
  - §2.1：零阶贝叶斯 TSK 与 ANFIS 预测区间先例 + 一句「均未做稀疏高阶后件模型平均」区分；
  - §2.2：「解析近似失效」理论谱系（gelfand/chipman/kasprzak）；
  - §2.2 末：conformal 回应 + hedged 新颖性（见 B3/B4）。
- **验证**：31 条 bib 全部被正文引用（0 未引条目）；bbl 含全部新 key；编译 0 undefined。

### B3 · 回应 conformal prediction（防御性一句）✅
- **改动**：§2.2 末加一句——conformal 需单独校准集、且不把预测方差分解为噪声 + 模型选择分量，本文 BMA 显式传播后者。

### B4 · hedged 新颖性陈述（"to our knowledge"）✅
- **改动**：
  - `manuscript.tex` §2.2 末：`...BMA-calibrated prediction intervals, which to our knowledge has not been developed for linear-consequent rule models...`；
  - `cover_letter.tex` Contribution 段：`To our knowledge, no prior work provides exact spike-and-slab posterior sampling with BMA-calibrated prediction intervals for linear-consequent rule models; our method fills this gap.`
- **依据**：六路检索确认无先例（arXiv API 双查询 0 命中 + 多轮 web 检索），但仍用 hedged 措辞（遵守「first 裸声明」诚信教训）。
- **同步**：cover letter `References: 25` → `References: 31`。

---

## C. 残留风险（仅记录，不重做）

| # | 风险 | 级别 | 状态 |
|---|---|---|---|
| C-A | 缺 ANFIS / IT2-FLS / 近期稀疏模糊基线实测 | Medium | 已用 GP 外部概率基线 + Related Work 一句「为何不适用」缓解；本次未补实测 |
| C-B | 稀疏机制 d=8 / d=81 均不赢 | Medium | 靠「sparsity design criterion + 诚实边界」回答 |
| C-C | generality 只 hedge 未演示 | Low | 不重做 |
| C-D | 作者 Biography ≤100 词 + 证件照：**检索未确认 IS 硬性要求** | 待活页 | 活页若要求，终稿阶段补 |

---

## 验证汇总

| 项 | 结果 |
|---|---|
| 四件套编译 | manuscript / supplementary / highlights / cover_letter 全部 exit 0、0 errors、0 undefined |
| 摘要词数 | 154（未改动） |
| Highlights 字符 | 75 / 80 / 71 / 68 / 64（≤85 ✓） |
| 引用 | 31 条全部被引；bbl 含全部新 key |
| 行号 | PDF margin 行号渲染 ✓ |
| 页数 | manuscript 19 页（远低于 40 页上限） |

## 未做（待 Phase 3 或用户决策）
- 整体叙事/语言/图表优化（Phase 3）
- 补 ANFIS/IT2-FLS 实测基线（C-A）
- conformal 对照实验升级（B3 目前为文本回应）
- git commit（等用户确认）
