# Phase 2 · 立即修复报告

生成时间：2026-08-16
依据：`P1_偏离清单.md`（HIGH + 无争议 MEDIUM）+ 用户决策（①保留基线+强化论证 ②H1 重跑可复现 before 值 ③合成验证留 Phase 3 ④标题软化）。
范围：只做「消除偏离」，不做「提升优化」；未重做 §4 已闭环项；所有新数字来自实测运行（`results/raw/*.json`）或 CrossRef 活页。
验证：四件套 `latexmk` 全部 **0 errors / 0 undefined**；摘要 178 词（≤200）；Highlights 77/80/71/68/64（≤85）；38 引用全被引；标题五文件一致；无旧数字残留。

---

## 1. HIGH 修复

### H1 · Figure 1 buggy 基线值可复现化 + 出处据实（决策②：重跑路径）
- **新脚本** `src/buggy_membership_repro.py`：按正文所述 bug 行为（预测时用占位全零标签从查询数据重估高斯 spreads）在**同一 30 splits（SEED=42）**上复现，产出 `results/raw/buggy_baselines.json`。
- **before 值实测（现全部可追溯）**：TSK-LS 0.78 / **0.48** / **-2.86**（Heating/Cooling/Concrete）；Bayesian-TSK 0.84 / 0.78 / -0.56。
  - ⚠️ 旧硬编码值（0.5671/0.4084/0.4376…，代码注释标注「REJECTED manuscript」）**不可从任何数据复原**，已整体替换为本次实测值；正文/图/封面信全部同步。
- **`src/figures_v2.py:77-84`**：`REPORTED_R2` 改为从 `buggy_baselines.json` 读取；删除「REJECTED manuscript」自指注释；图例「Reported (buggy)」→「Reproduced (buggy)」；y 轴扩展以容纳 Concrete 负值；`fig1_repro_fix` 重新生成。
- **正文/封面信出处改写**（去掉不可验证的「published TSK baselines」外部声明与自指残留）：
  - `manuscript.tex:51,103,293` + 摘要：改为「We reproduce this pattern, quantify its effect」；数字 0.41→0.48（Energy-Cooling）。
  - `cover_letter.tex:24`：0.41→0.48 + 同出处改写。

### H2 · BIC/Laplace 失效机制与自身消融对齐（文本，数字不变）
- **定位**：摘要(:32)、引言(:49)、贡献 2(:58)、校准(:228)、Discussion(:279)、结论(:293)、封面信(:22)。
- **改后机制**：① hard thresholding 塌缩**精度**；② as-implemented 基线的 **ridge-regularized 拟合病态设计矩阵**塌缩**覆盖**（PICP 0.00–0.18）；③ 忠实的 threshold+Laplace（LS 拟合）覆盖近名义（PICP 0.93）但精度低（R² 0.60）、区间宽（MPIW 26.1）。
- 摘要/引言/校准/讨论/结论/封面信全部与该口径一致；PICP 0.00–0.18 数字保留（仍为 as-implemented 基线实测）。

### H3 · 采样器正确性声明收敛 + 可追溯
- **运行** `src/gibbs_verify.py` → 存档 `results/raw/gibbs_verify_output.txt`：R=5 → ΔR²=0.0010、median 相对方差差 5.6%（与正文 10⁻³/6% 一致）；R=10 → 0.0055/14.1%。
- `manuscript.tex:126`：「confirming the sampler's correctness」→「confirming the correctness of the β 与 σ² updates」；补实测值 + 明确 **Eq.(eq:gamma) 不被该固定激活检查覆盖**。
- `manuscript.tex:167` + `supplementary.tex:159`：γ 链在这些基准上**饱和于全激活**（ESS=链长是构造性结果，非活跃探索）；β/σ² 链 R̂≤1.001、ESS(σ²)>1700 正常混合；删除「R̂≤1.01 for the inclusion indicators」「well-mixed chains」的过度表述；收敛验证仅声明于 rule-level 采样器。

### H4 · 投稿信 EiC 抬头
- `cover_letter.tex:12,14`：致 **Sabrina Senatore + Zheng Yan（Editors-in-Chief）**（P0 三源：EiC 已自 Pedrycz 变更为 Senatore；Zheng Yan 仍 Co-EiC）。

### H5 · 作者 Biography
- IS 硬性要求（≤100 词 + 证件照，Word 可编辑）。**非稿件编辑项**，列为 Phase 4 投稿包待办。

---

## 2. MEDIUM 修复

| # | 定位 | 改动 |
|---|---|---|
| M1 | manuscript.tex:228 | Cooling 校准口径一致：池化 PICP **0.935**（表 1 显 0.93）；偏差 **1.5pp**（在一个 per-split 标准误 ~0.026 内，池化后可检测）；Gibbs 与共轭值差 ≤**0.004**；保留「near-nominal 而非 perfectly calibrated」 |
| M2 | manuscript.tex:192 | 「closer than GP」限定逐目标：Heating/Concrete 成立，Cooling 基本打平（TSK 0.93 vs GP 0.94） |
| M3 | 标题 + Highlights + 图注 | 标题 → **"Approximately Calibrated"**（四件套 + Highlights.txt 五文件一致）；Highlights #1「calibrated intervals」→「near-nominal intervals」；Fig3 图注「are calibrated」→「attain near-nominal coverage」；Fig5 图注补 Cooling 名义 0.95 欠覆盖 + 「well-calibrated」→「calibrated」 |
| M4 | manuscript.tex:74 | conformal 句限定为 **split conformal**（Vovk 全量式不需校准集），并据此措辞 |
| M5 | manuscript.tex:122 + §3.4 末尾 | 显式写出 **σ²~InvGamma(0.01,0.01)**；披露三项数值正则化（精度矩阵 +1e-10 jitter、Ridge(0.01) 初始化、σ² floor 1e-4） |
| M6 | manuscript.tex:188 | Wilcoxon 改为「finds no significant difference」+ 逐目标 p 值（Heating 0.11/0.32、Cooling 0.07/0.87）+ 明示「test ≠ 等价、splits 为同一批行的重采样」；Concrete：采样器略优于稠密（mean ΔR²=0.006/0.004） |
| M7 | manuscript.tex:295-316 | backmatter 重排：**CRediT → Acknowledgments → Data Availability → Declaration of Competing Interests → Declaration of Generative AI and AI-assisted technologies in the writing process（紧贴参考文献）**；节标题对齐官方全名（CRediT 位于致谢上方，GenAI 位于参考文献正上方，均按 P0 活页政策） |
| M8 | cover_letter.tex:44-47 | 替换同实验室审稿人：删 Destercke（与 Denoeux 同属 Heudiasyc），补 **Tufan Kumbasar**（Istanbul Technical University，`kumbasart@itu.edu.tr`，Type-2 模糊 + 不确定性量化）——Denoeux / Kumbasar / Pal 三地分散。**投稿前核 3 人非 IS 编委/近 3 年合作者** |
| M10 | supplementary.tex:180 | 高维 τ² 网格透明注：明确只测紧/扩散两极端（括号低维 Table 2 网格），非全集 |

## 3. LOW 修复

| # | 定位 | 改动 |
|---|---|---|
| L1 | 摘要 + :53 | 「at comparable interval width on the Energy targets」悬垂指代 → 明确为「comparable to the closed-form conjugate baseline's」 |
| L2 | 全文 + supplementary | 命名统一 **Energy-Heating / Energy-Cooling**（表 1、校准、补充表 1/4/8、MCMC 行） |
| L3 | manuscript.tex:228 | 「within 0.002」→「within 0.004」（Concrete Δ=0.0038 实测） |
| L4 | references.bib | **fragoso DOI 10.1111/insr.12229→10.1111/insr.12243**（原 DOI 解析到 McElreath《Statistical Rethinking》书评，严重错配）；**lei DOI →10.1080/01621459.2017.1307116**（原 DOI 404）；**chipman pages 65--134→65--116**（CrossRef 实测）；**kasprzak 标题补副标题**「...for a variety of useful divergences」 |
| L5 | manuscript.tex:167 | 收敛声明仅限 rule-level 采样器；SSVS 未声明正式收敛验证 |

## 4. 决策落地
- **① 基线**：不新增 ANFIS/ENNreg/IT2 实验；Setup 加 scope 句（此类方法走 evidential/interval-network 机制而非后验模型选择，非直接基线；GP 为标准概率参考）。
- **④ 标题**：软化（Approximately Calibrated）。

## 5. 新增可追溯产物
- `src/buggy_membership_repro.py`（bug 复现脚本）
- `results/raw/buggy_baselines.json`（before 值实测）
- `results/raw/gibbs_verify_output.txt`（采样器正确性实测）
- `INS_review/P0_standards_refresh.md`、`INS_review/P1_偏离清单.md`

## 6. 编译与一致性验证
- 四件套 `latexmk`：manuscript / supplementary / highlights / cover_letter 全部 exit 0、0 errors、0 undefined。
- 摘要 **178 词**（≤200）；Highlights 5 条 77/80/71/68/64（≤85）；38 引用全被引、无孤儿；标题五文件一致。
- 残留扫描：0.41 / 0.5671 / Energy Heating / Energy Cooling / published TSK baselines / Laplace covariance collapses / well-mixed / 0.002 全部清零。

## 7. 留待 Phase 3（优化/实验，非阻塞）
- **M9**：把 d=81 高维校准结果（Gibbs PICP 0.940 vs conjugate 0.921）提入正文 §5.3 + 摘要末句（desk「为何不用 conjugate」）。
- **H3④**：合成稀疏真值 + 穷举 2^R 对拍 Eq.(eq:gamma) 验证实验（用户已批准）。
- **M10 强化**：高维全 τ² 网格（如需）。
- **投稿时复核项**：EiC 名单、Biography 100 vs 200 词口径、EM 门户、审稿人编委身份、Wilson 区间用精确 n_test。

*本报告所有数字均来自 `results/raw/*.json` 实测或 CrossRef 活页核证，未编造。*
