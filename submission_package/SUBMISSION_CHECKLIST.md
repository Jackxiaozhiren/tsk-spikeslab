# Editorial Manager — Information Sciences 投稿 checklist

> 依据：`INS_review/P0_standards_refresh.md`（P0 标准档案）+ `INS_review/P4_终审报告.md`。
> 生成：2026-08-16。**P5 语言润色后刷新：2026-08-16 16:20**（manuscript/supplementary/cover_letter PDF 与 `ins_latex_source.zip` 均已重建；**采用 `final` 期刊版式：无行号、标题单次、ORCID 显示完整数字 0009-0008-2164-4557**；zip 已实测自含可编译，四件套 0 errors/undefined，manuscript 17 页、supplementary 5 页）。门户：`editorialmanager.com/ins`（⚠️ 当前显示「Site under development」横幅，**投稿前从期刊官网「Submit your article」按钮进入确认实际门户**）。

## 0. 投稿前必核（人工，无法自动化）
- [x] **EiC 名单**：现为 Sabrina Senatore + Zheng Yan（投稿信已致此二人）；投稿时从期刊官网编委页最终确认
- [ ] **Biography**：≤100 词 + 证件照（Word 可编辑）——见 `biography.txt` 草稿，补全后上传
- [x] **建议审稿人编委身份**：已联网检索，**无证据表明 Denoeux / Kumbasar / Pal 任一为 IS 编委**（Denoeux 关联 IJAR 等刊、Kumbasar/Pal 仅曾在 IS 发文）；三人异地（法国/土耳其/印度）、与作者无合著；投稿时仍建议从编委页最终扫一遍
- [x] **EM 门户**：Elsevier 当前机制为「期刊主页 → Submit your article」进入（submit.elsevier.com 为新式 EM）；`editorialmanager.com/ins` 仍显示「Site under development」横幅——投稿时从官网按钮进入，勿直接用 EM 旧地址
- [ ] Abstract 词数口径（200 vs 300）以投稿时官网为准（当前 **178 词**，两种口径均达标）

## 1. 上传文件清单（Editorial Manager）

| 项 | 文件 | 状态 |
|---|---|---|
| Manuscript（PDF） | `submission_package/manuscript.pdf`（17 页 A4，final 版式，0 errors/undefined） | ✅ |
| LaTeX 源码包（.zip，无子文件夹） | `submission_package/ins_latex_source.zip`（manuscript.tex / references.bib / supplementary.tex / highlights.tex / cover_letter.tex + 6 图，顶层平铺；已测自含可编译） | ✅ |
| Highlights（单独文件，final-files 阶段必需） | `submission_package/Highlights.txt` + `Highlights.docx`（5 条 ≤85 字符） | ✅ |
| Figures（6 张单独） | `submission_package/figures/fig1..fig6.pdf`（纯矢量 PDF，dpi 达标） | ✅ |
| Supplementary（单独） | `submission_package/supplementary.pdf`（9 节，0 errors） | ✅ |
| Cover letter | `submission_package/cover_letter.pdf`（致 Senatore + Yan；含贡献/novelty/journal fit/3 审稿人/原创声明） | ✅ |
| 声明四件套（正文已含） | Data availability / Competing interests / CRediT / Generative AI（均在 manuscript 尾部，顺序合规） | ✅ |

## 2. 元数据
- 通讯作者：Zhiren Xiao，Guangdong University of Finance, Guangzhou, China
- Email：`241734106@m.gduf.edu.cn`
- ORCID：`0009-0008-2164-4557`（已含于 manuscript/cover letter）
- Title：Exact Bayesian Inference for Spike-and-Slab Priors in Takagi–Sugeno–Kang Fuzzy Systems with Approximately Calibrated Model-Averaged Prediction Intervals
- Keywords：uncertainty quantification; prediction intervals; Bayesian inference; spike-and-slab prior; Bayesian model averaging; Takagi–Sugeno–Kang fuzzy system

## 3. 建议审稿人（3 位，异地）
1. Prof. Thierry Denœux — Heudiasyc, Université de Technologie de Compiègne, France（evidential/uncertainty-aware regression）
2. Prof. Tufan Kumbasar — Istanbul Technical University, Turkey（type-2 fuzzy logic, uncertainty quantification）`kumbasart@itu.edu.tr`
3. Prof. Nikhil R. Pal — Indian Statistical Institute, Kolkata, India（fuzzy systems, high-dimensional TSK）

## 4. 声明与政策
- 单盲评审（作者身份保留）；≥2 审稿人；SSRN 预印本可选（desk 通过后公开）。
- 引用诚信：**37 条引用 CrossRef + 联网全部验真通过（2026-08-16 复核）**；修正 7 处引用元数据错误（xue2023dgaletsk 作者/页码、lei2018distributionfree 缺 2 作者、zhang2023sparse 作者顺序、bian2025mhtsk 作者/标题、liu2017bayesianzero 作者/页码、khosravi 页码、pineau 标题）；删 2 条低贡献引用（heliyon2024early、khosravi2011comprehensive）；无杜撰引用。新颖性 2026-08 arXiv 复核仍成立。
- Generative AI 声明已含（Claude 用于代码辅助与语言编辑）。

## 5. 提交后预期
首轮 ~3.1–3.3 月；全程 ~6.5–6.7 月；desk reject 最快 ~1 天；接受率 ~22.5%。
