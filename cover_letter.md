The Editor-in-Chief
Professor Mario Koppen
Applied Soft Computing
Elsevier

Dear Professor Koppen,

We submit our manuscript entitled "Sparse Bayesian TSK Fuzzy System with
Spike-and-Slab Priors for Building Energy Prediction" for consideration in
Applied Soft Computing.

CONTRIBUTION AND NOVELTY

This paper introduces Bayesian spike-and-slab priors for Takagi-Sugeno-Kang (TSK)
fuzzy rule consequent selection. While Bayesian TSK fuzzy systems exist (Gu &
Chung, 2017, IEEE TFS; 2018, IEEE TII) and sparse TSK systems have been pursued
through frequentist regularization (KBS, 2024), no prior work combines Bayesian
sparsity-inducing priors with fuzzy system design. We present an analytical
BIC-based approximation that performs rule selection, parameter estimation, and
approximate uncertainty quantification in a single computational pass---avoiding
the cross-validated tuning required by LASSO-based sparse TSK and the MCMC cost
of full posterior sampling. The approach is validated on three regression
benchmarks (two building energy targets plus concrete compressive strength) from
the UCI Machine Learning Repository.

Three findings structure the contribution. First, rule sparsity is data-dependent:
38% of rules are pruned on the Energy benchmarks (1.9 of 5 pruned; 3.1 retained) while no rules
are pruned on Concrete, establishing when sparsity succeeds and when it fails.
The retained sparse models incur a substantial accuracy penalty (RMSE degrades
3.4--3.8$\times$ relative to dense TSK-LS), and we characterize this
sparsity-accuracy-calibration trade-off through extensive ablation. Second, the
non-sparse conjugate Bayesian TSK baseline achieves well-calibrated 95%
prediction intervals (PICP = 0.90--0.96), while the spike-and-slab variant's
analytical approximation systematically undercovers (PICP = 0.06--0.32),
revealing a fundamental trade-off that we trace to the hard-thresholding step
inherent in BIC-based model selection. Third, diagnostic analysis
identifies severe multicollinearity in the TSK design matrix (condition number
exceeding $10^{16}$) as a structural challenge for L$_1$-regularized TSK---a finding
with broad implications for sparse fuzzy system methods.

JOURNAL FIT

We believe this work is well-suited to Applied Soft Computing for three reasons.
First, the paper's core methodology---a fuzzy inference system---falls squarely
within ASC's soft computing scope. Second, the Bayesian-fuzzy hybridization
exemplifies the hybrid intelligent systems that ASC champions as a preferred
publication category. Third, the empirical characterization of the
sparsity-accuracy-calibration trade-off on building energy and materials
benchmarks provides the application-driven validation that distinguishes ASC
from purely theoretical fuzzy systems journals. The paper's emphasis on when
a method works and when it fails---rather than selective reporting of favorable
results---aligns with ASC's standards for applied rigor.

MANUSCRIPT METADATA

- Figures: 7 (main text)
- Tables: 5 (main text)
- Word count: approximately 6,400 words (main text excluding references)
- References: 33
- Supplementary material: ablation result tables (tau^2, alpha sensitivity),
  TSK-LASSO diagnostic code, extended-grid results, and Facebook Metrics (d=19)
  high-dimensional validation

DATA AND CODE AVAILABILITY

The datasets are publicly available from the UCI Machine Learning Repository
(Energy Efficiency: https://archive.ics.uci.edu/dataset/242; Concrete Compressive
Strength: https://archive.ics.uci.edu/dataset/165). The Python code implementing
all experiments, figures, and ablations is provided as supplementary material and
will be made available in a public GitHub repository upon acceptance.

CONFLICT OF INTEREST

The authors declare that they have no known competing financial interests or
personal relationships that could have appeared to influence the work reported
in this paper.

SUGGESTED REVIEWERS

We suggest the following researchers as potential reviewers, based on their
expertise in Bayesian fuzzy systems, sparse learning, and soft computing for
engineering applications:

1. Professor Xiaojing Gu — School of Information Science and Engineering,
   Changzhou University, China. Expertise: Bayesian TSK fuzzy systems.

2. Professor Thierry Denoeux — Universite de Technologie de Compiegne, France.
   Expertise: Belief functions, uncertainty quantification in fuzzy regression.

3. Professor Witold Pedrycz — University of Alberta, Canada. Expertise: Granular
   computing, fuzzy rule-based systems, interpretable fuzzy modeling.

4. Professor Kaibo Liu — University of Wisconsin-Madison, USA. Expertise:
   Bayesian spike-and-slab methods for engineering prognostics.

5. Professor Hossein Moayedi — Department of Civil Engineering, University of
   Technology Sydney, Australia. Expertise: Metaheuristic-optimized fuzzy
   inference for building energy prediction.

CORRESPONDING AUTHOR

Zhiren Xiao
Guangdong University of Finance, Guangzhou, China
Email: 241734106@m.gduf.edu.cn

Sincerely,

Zhiren Xiao
Guangdong University of Finance, Guangzhou, China
