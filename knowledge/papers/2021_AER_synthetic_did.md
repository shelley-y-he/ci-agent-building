# Synthetic Difference-in-Differences

**Full citation**: Arkhangelsky, D., Athey, S., Hirshberg, D. A., Imbens, G. W., & Wager, S. (2021). Synthetic Difference-in-Differences. *American Economic Review*, 111(12), 4088–4118.
**Tier**: Standard
**Tags**: DiD, synthetic-control, panel-data, two-way-fixed-effects, weighting, staggered
**Source file**: `references/2021 AER_Synthetic Difference-in-Differences.pdf`
**Extracted**: 2026-03-10

---

## Summary

This paper proposes Synthetic Difference-in-Differences (SDID), a new panel data estimator that combines the unit reweighting of synthetic control (SC) with the two-way fixed effects structure of difference-in-differences (DID). SDID finds unit weights that make pre-treatment trends parallel (as in SC) and time weights that balance pre- and post-treatment periods, then runs a weighted two-way fixed effects regression. Theoretically and empirically, SDID is shown to be competitive with or dominant over both DID and SC across the settings where each is conventionally used, with lower bias and smaller standard errors in simulations calibrated to real data.

## Method / Estimator

SDID solves a weighted two-way fixed effects regression:

    (tau_sdid, mu, alpha, beta) = argmin sum_i sum_t (Y_it - mu - alpha_i - beta_t - W_it * tau)^2 * omega_i * lambda_t

**Unit weights** (omega_sdid) are chosen to make the weighted average of control pre-trends parallel (not necessarily identical) to the treated pre-trends, with an intercept term and L2 regularization. This relaxes the SC constraint that pre-trends must match exactly.

**Time weights** (lambda_sdid) are chosen so that a weighted average of pre-treatment periods predicts the post-treatment period (for control units), up to a constant.

The estimator can also be written as a weighted double-difference: post-minus-pre for treated units, minus post-minus-pre for weighted control units, where pre-periods are themselves reweighted. The target estimand is the average treatment effect for treated units in treated periods (ATT).

**Inference** is supported via three variance estimators: (1) clustered bootstrap (resample units), (2) jackknife (fix weights, leave one unit out), and (3) placebo method (assign placebo treatments to control units — valid when N_tr = 1, requires homoskedasticity). The bootstrap performs best in large panels; the placebo method is the only option when there is a single treated unit.

**Staggered adoption** extension: apply SDID separately for each adoption cohort, then take a weighted average of cohort-specific estimates.

## Key Assumptions

1. **No unmeasured confounding in the systematic component**: Treatment assignment may depend on the latent factor structure L = Gamma * Upsilon' but not on the idiosyncratic error E. Formally, E[E | W, L] = 0.

2. **Factor structure on outcomes**: Y_it = gamma_i * upsilon_t' + tau * W_it + epsilon_it. The standard DID additive fixed effects model is a special case.

3. **Balancability**: Oracle unit weights must approximately align treated and control latent unit factors (Gamma); oracle time weights must approximately align latent time factors (Upsilon). This is the key identifying assumption — not directly testable, though pre-treatment fit provides indirect evidence.

4. **No contemporaneous confounding shocks**: No unexplained shocks disproportionately affect treated units at the time of treatment.

5. **Error regularity**: Errors are independent across units (may be serially correlated within units), homoskedastic across units. Panel must be large (N, T -> infinity; N_tr * T_post -> infinity, N_co and T_pre -> infinity).

6. **Low effective rank of L**: Singular values of L_{co,pre} must decay sufficiently fast (effective rank roughly below sqrt(min(T_pre, N_co))). No exact low-rank assumption required.

## Diagnostics & Tests

Examine pre-treatment trend balance: whether the weighted control average tracks the treated pre-trend. Good pre-trend fit is necessary (but not sufficient) for identification. SDID makes trend-balancing automatic and data-driven, addressing pre-testing concerns (Roth 2018).

## Sensitivity Analysis

Simulations decompose performance across settings where the interactive component (M) versus additive fixed effects (F) dominate the outcome model. SDID is robust across both regimes. No formal sensitivity analysis for violations of the no-confounding-shock assumption is developed; the authors note this requires historical context to justify.

## Limitations & Caveats

- **Single treated unit**: Bootstrap and jackknife variance estimators are unavailable when N_tr = 1; only the placebo method applies, requiring homoskedasticity across units.
- **Homoskedasticity for placebo inference**: A strong assumption that cannot be tested with one treated unit.
- **Staggered adoption**: The basic algorithm does not directly handle staggered timing; the cohort-by-cohort extension is sketched but lacks full formal guarantees.
- **Precision loss possible**: If there is little systematic heterogeneity across units or time, unequal SDID weights can reduce precision relative to DID.
- **Asymptotics require large N and T**: Results do not apply to small panels; both N and T must grow.
- **Identification assumption is untestable**: The balancability assumption (oracle weights generalize to treated units) has no direct testable implication.
- **Block assignment focus**: Main theoretical results assume all treated units adopt simultaneously.

## Data / Code

- California smoking example: Proposition 99 cigarette tax data (Orzechowski & Walker 2005), 39 states 1970–2000.
- CPS placebo study: Women's log wages, Current Population Survey (NBER MORG), 1979–2019, 50 states.
- Penn World Table placebo study: Log real GDP, 111 countries, 1959–2007 (Feenstra, Inklaar, and Timmer 2015).
- R package `synthdid`: https://github.com/synth-inference/synthdid
- Replication data: https://doi.org/10.3886/E146381V1

## Related Papers

- Abadie, Diamond, and Hainmueller (2010, 2015) — foundational SC papers; California and German reunification applications
- Doudchenko and Imbens (2016) — SC with intercept (DIFP); key precursor
- Ferman and Pinto (2019) — SC with imperfect pre-treatment fit; shows SC is asymptotically biased without regularization
- Ben-Michael, Feller, and Rothstein (2018) — augmented synthetic control; closely related to SDID with linear outcome model
- Athey et al. (2021) — matrix completion estimator; used as benchmark
- Bertrand, Duflo, and Mullainathan (2004) — serial correlation in DID; motivates cluster/bootstrap inference
- Callaway and Sant'Anna (2020) — DiD with multiple time periods
- Athey and Imbens (2021) — design-based analysis with staggered adoption
- Xu (2017) — generalized synthetic control / interactive fixed effects
- Bai (2009); Moon and Weidner (2015, 2017) — interactive fixed effects panels; SDID requires weaker assumptions
- Roth (2018); Rambachan and Roth (2019) — pre-testing and honest inference for parallel trends
