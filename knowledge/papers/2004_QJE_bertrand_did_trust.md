# How Much Should We Trust Differences-in-Differences Estimates?

**Full citation**: Bertrand, Marianne, Esther Duflo, and Sendhil Mullainathan (2004). How Much Should We Trust Differences-in-Differences Estimates? *Quarterly Journal of Economics*, 119(1), 249–275.
**Tier**: Deep
**Tags**: DiD, serial-correlation, inference, clustering, placebo, block-bootstrap, standard-errors, panel-data, pre-post-aggregation
**Source file**: `references/2004 QJE_How much should we trust Differences-in-Differences Estimates.pdf`
**Extracted**: 2026-03-10

---

## Summary

This paper demonstrates that the standard errors in published DiD studies are systematically understated because researchers use long panels with serially correlated outcomes but treat errors as if they were serially independent. The paper quantifies the severity of overrejection using placebo laws in CPS data (up to 45–67% false rejection at nominal 5% level), then conducts Monte Carlo simulations to compare how well a range of inference corrections solve the problem. Four practical solutions are ranked by performance and scope of applicability: (1) pre/post time-series aggregation (works for small N, low power); (2) block bootstrap (works for large N, requires programming); (3) empirical variance-covariance matrix (good for large N, requires homoskedasticity assumption); and (4) arbitrary (clustered) variance-covariance matrix (good for large N, requires no distributional assumptions about the error process). Naive parametric AR(k) corrections perform poorly because of small-sample downward bias in autocorrelation estimates and sensitivity to process misspecification.

---

## Method / Estimator

The standard DiD estimator is OLS on the two-way fixed effects model:

```
Y_ist = A_s + B_t + c * X_ist + β * I_st + ε_ist
```

where:
- `Y_ist` is the outcome for individual `i` in group (state) `s` at time `t`
- `A_s`, `B_t` are state and year fixed effects
- `X_ist` are individual-level controls
- `I_st` is a dummy = 1 if group `s` is treated at time `t`
- `β` is the treatment effect of interest (DiD estimand)

The core concern is that OLS standard errors for `β` are inconsistent in the presence of serial correlation in `ε_ist`, because:
1. Panels are typically long (median 11 years in surveyed literature, mean 16.5)
2. Common DiD outcomes (wages, employment) are highly positively serially correlated (first-order AC ≈ 0.51 in CPS female wages, declining slowly)
3. The treatment variable `I_st` is itself highly serially correlated (it switches on once and stays on), amplifying the variance understatement

The four proposed corrections are:
1. **Pre/post aggregation** ("collapsing"): Average the data within pre- and post-intervention periods; run the DiD on a two-period panel; adjust t-statistics for small effective sample size (following Donald and Lang 2001). A variant — "residual aggregation" — first regresses out state/year FE, then averages treatment-state residuals into pre/post. Handles staggered laws.
2. **Block bootstrap**: Bootstrap entire state time-series vectors (preserving within-state autocorrelation structure); construct sampling distribution of the t-statistic; reject if original t exceeds 95th percentile of bootstrapped distribution.
3. **Empirical variance-covariance matrix**: Assumes homoskedasticity across states, uses cross-state variation to estimate the full T×T block of the error covariance; consistent as N → ∞ (Kiefer 1980).
4. **Arbitrary (clustered) variance-covariance matrix**: White/Huber-style sandwich estimator allowing unrestricted within-state correlation across time (Arellano 1987; White 1984); implemented via STATA `cluster` command with states as clusters.

---

## Key Assumptions

1. **Parallel trends (identifying)**: In the absence of the intervention, the change in outcomes over time would have been the same for treated and control groups. This is taken as given throughout the paper — the focus is entirely on *inference* validity, not identification validity.
2. **Treatment as good as random (conditional on fixed effects)**: Interventions are uncorrelated with state- and time-specific shocks after conditioning on state and year FEs.
3. **Correct clustering level**: The inference problem arises from serial correlation of outcomes *within* states over time. It is separate from (though compounded with) the Moulton problem of correlated shocks within state-year cells.
4. **For clustered SE to be valid**: Number of clusters (states/groups) must be large enough for asymptotic approximation to hold. Performance degrades substantially below ~20 groups.
5. **For empirical VCV**: Cross-sectional homoskedasticity across states is required. This is likely violated in practice.
6. **For block bootstrap**: Number of groups must be large enough (≥ ~20–50) for bootstrap distribution to approximate sampling distribution.

---

## Diagnostics & Tests

**Placebo law test (primary diagnostic)**:
- Randomly assign treatment to states and years using real data; compute t-statistic for "effect"; repeat 200–400 times
- Under a correctly-sized test, rejection rate should equal 5%
- Actual OLS rejection rates: 67.5% (micro CPS, no clustering), 44% (aggregated CPS, no SE correction), 49% (Monte Carlo using empirical state distribution)
- This is the key diagnostic the paper introduces for checking whether a DiD inference procedure is properly sized

**Correlogram of residuals**:
- After regressing log wages on state and year dummies, compute AC coefficients of state-year cell means
- First-order AC: 0.51; second-order: 0.44; third-order: 0.33
- Decay is much slower than an AR(1) would predict, indicating more complex process

**Varying N and T** (Table III):
- Overrejection does not decrease much as N falls (from 50 to 6 states, rejection rates stay roughly 38–49%)
- Overrejection does decrease as T falls, but slowly: 15% at T=7, 8% at T=3

**AR(1) Monte Carlo sensitivity** (Table II, Panel B):
- Rejection rates rise monotonically with autocorrelation parameter ρ
- At ρ=0: ~5% (correctly sized); at ρ=0.8: ~37%; at ρ=-0.4: underrejection (~0.8%)

**Power assessment** (2% true effect):
- Assessed by adding `I_st × 0.02` to outcome data before running simulations
- Power is low for aggregation methods (16% with 50 states) and higher for clustering/bootstrap (26–27% with 50 states)

---

## Sensitivity Analysis

1. **Different outcome variables** (Table II, rows 6–8): Overrejection scales with the serial correlation of the dependent variable. Employment (AC≈0.47): 46% rejection. Hours worked (AC≈0.15): 27% rejection. First-differenced log wages (negative AC): <5% rejection.

2. **Serially uncorrelated placebo laws** (Table II, row 5): When the treatment variable itself is not serially correlated (randomly switched on/off each year), OLS rejection rate drops to 5% — confirming the mechanism.

3. **Staggered law timing** (Table VI, rows 4, 8, 12, 16, 19): Residual aggregation method handles staggered laws and continues to perform well (5–9% rejection at N=50), though power is somewhat lower than for simultaneous laws.

4. **AR(2) and AR(1)+white noise processes** (Table IV, rows 7–8): Parametric AR(1) corrections fail catastrophically under process misspecification. AR(2) true process → 30.5% rejection when corrected assuming AR(1). AR(1)+white noise → 38.5% rejection under AR(1) correction.

5. **Imposing known AR(1) parameter** (Table IV, rows 3, 6): Even if the true ρ=0.8 is imposed (rather than estimated), the rejection rate falls only to 16–18% in CPS data, confirming that process misspecification (not just downward bias in ρ estimation) is a core problem with parametric corrections.

---

## Limitations & Caveats

1. **Focus on inference only**: The paper entirely sets aside questions of identification/endogeneity of treatment. It assumes the DiD design is valid and the treatment effect is unbiased; the concern is solely about standard errors.

2. **Uniform treatment effects assumed**: The power simulations generate a uniform 2% effect across all treated states. Heterogeneous treatment effects are noted but not analyzed.

3. **State-level data only**: The Monte Carlo uses U.S. state-level panel data. Generalization to other panel structures (firms, countries, individuals) requires verifying similar autocorrelation properties.

4. **Low power of aggregation methods**: Pre/post collapsing solves the size problem but dramatically reduces power, especially with few states (16% power at N=50; 6.5% at N=10 for 2% effect).

5. **Clustering breaks down with few clusters**: Both clustered SE and empirical VCV methods show notable over-rejection when N < 20 (8% at N=10, 11–15% at N=6 for 5% nominal level).

6. **Block bootstrap impractical without code**: The paper notes that this method, while effective, requires limited programming and was not standard in econometric packages at the time.

7. **No GLS or GMM estimation**: The paper does not evaluate efficiency-improving estimators (GLS on a parametric AR(k) model, GMM for dynamic panels), only variance-correction approaches for OLS. The authors call this out as future work.

8. **Moulton problem treated as separate**: The within-state-year group correlation (Moulton problem) is addressed by aggregating to state-year cells before the main analysis; the paper's focus is the across-year serial correlation problem.

9. **CPS sampling error may attenuate AC**: Small cell sizes in CPS state-year cells introduce sampling noise that lowers observed autocorrelation relative to administrative data, potentially understating the problem's severity in administrative datasets.

---

## Data / Code

**Primary dataset**: CPS Merged Outgoing Rotation Group (MORG), 4th interview month, 1979–1999
- Women aged 25–50
- ~900,000 observations total; ~540,000 with positive weekly earnings
- Outcome: log(weekly earnings)
- Data aggregated to 50 states × 21 years = 1,050 state-year cells (~500 obs per cell)
- Controls: 4 education dummies, quartic in age

**Simulation design (placebo)**:
- Treatment year drawn uniform from [1985, 1995]
- 25 states randomly selected as treated
- Placebo I_st = 1 for treated states after treatment year
- Repeated ≥200 times per cell (typically 400)

**Monte Carlo studies**:
1. State-level empirical distribution: resample states with replacement from CPS, preserving within-state autocorrelation
2. AR(1) with normal disturbances: parameterized to match CPS state-level female wage variances; ρ varied from -0.4 to 0.8

**Software**: STATA
- Clustering: `cluster` command (state as cluster unit)
- GLS parametric correction: `xtgls`
- Block bootstrap: custom code, available upon request from authors

---

## Replication Notes

**Step 1 — Establish overrejection baseline**:
Run OLS on CPS micro data with state/year FE and demographic controls (eq. 1). Randomly assign placebo laws (25 treated states, treatment year in [1985–1995]). Repeat 400 times. Count fraction with |t| > 1.96. Expected: ~67.5% without clustering, ~44% after clustering at state-year level or aggregating to state-year cells.

**Step 2 — Characterize autocorrelation**:
Regress log wage on state and year dummies. Compute mean state-year residuals. Regress residuals on lags 1–3 using OLS (pooling states). Report: AC1=0.51, AC2=0.44, AC3=0.33.

**Step 3 — Parametric corrections** (Table IV):
Use STATA `xtgls` to fit AR(1) to state-year residuals; compute corrected SEs. Run placebo exercise. Key result: rejection rate falls only from 49% to 24% with estimated ρ, to 18% even when imposing ρ=0.8. Conclusion: parametric corrections are insufficient.

**Step 4 — Block bootstrap** (Table V):
For each placebo draw, bootstrap 200 samples by drawing state vectors with replacement. Compute t-statistic distribution. Reject if original t > 95th percentile of bootstrap distribution. Key result: 6.5% rejection at N=50; degrades to 44% at N=6.

**Step 5 — Time-series aggregation** (Table VI):
Average Y_st into pre/post periods (relative to law passage date); run 2-period DiD; use t(N-2) distribution. Also: residual aggregation variant. Key result: 5.3% rejection at N=50; 5.3% at N=10; power ~16% at N=50 for 2% effect.

**Step 6 — Empirical VCV** (Table VII):
Pool residuals across states to estimate T×T covariance block; use this in GLS-style SE computation (Kiefer 1980). Key result: 5.5% rejection at N=50; 10.5% at N=10.

**Step 7 — Clustered SE** (Table VIII):
STATA `cluster(state)` on aggregated state-year data. Key result: 6.3% rejection at N=50; 8% at N=10; 11.5% at N=6. Power: 26.8% at N=50 for 2% effect.

**Main numerical results**:
- Baseline (OLS, CPS micro): 67.5% false rejection
- After state-year clustering only: 44%
- After pre/post aggregation: 5.3% (N=50), 5.3% (N=10)
- After block bootstrap: 6.5% (N=50), 22.5% (N=10), 43.5% (N=6)
- After clustering at state level: 6.3% (N=50), 8% (N=10), 11.5% (N=6)

---

## Key Quotes

> "Most papers that employ Differences-in-Differences estimation (DD) use many years of data and focus on serially correlated outcomes but ignore that the resulting standard errors are inconsistent."

> "These conventional DD standard errors severely understate the standard deviation of the estimators: we find an 'effect' significant at the 5 percent level for up to 45 percent of the placebo interventions."

> "Econometric corrections that place a specific parametric form on the time-series process do not perform well. Bootstrap (taking into account the autocorrelation of the data) works well when the number of states is large enough."

> "One correction that collapses the time series information into a 'pre'- and 'post'-period and explicitly takes into account the effective sample size works well even for small numbers of states."

> "Because computing standard errors that are robust to serial correlation appears relatively easy to implement in most cases, it should become standard practice in applied work."

> "Since a large fraction of the published DD papers we surveyed report t-statistics around 2, our results suggest that some of these findings may not be as significant as previously thought if the outcome variables under study are serially correlated."

---

## Related Papers

- **Donald and Lang (2001)** — Inference with DiD and other panel data; small-sample aggregation theory; cited as basis for t(N-2) adjustment.
- **Moulton (1990)** — Within-state-year cluster correlation problem in micro data; distinct from but compounded with the serial correlation problem.
- **White (1984); Arellano (1987); Kezdi (2002)** — Foundations of the arbitrary/clustered VCV estimator used in the main correction.
- **Kiefer (1980)** — Asymptotic theory for empirical (homoskedastic) VCV estimator with fixed T.
- **Nickell (1981); Solon (1984)** — Downward bias in OLS estimation of autoregression parameters in short panels; explains why parametric AR corrections underperform.
- **MacKinnon and White (1985); Bell and McCaffrey (2002)** — Small-sample bias of White standard errors; especially severe when treatment variable is nearly constant within cluster.
- **Efron and Tibshirani (1994)** — Bootstrap methodology including block bootstrap.
- **Besley and Case (2000)** — Endogeneity of policy interventions in DiD; the identification concern this paper deliberately sets aside.
- **Athey and Imbens (2002)** — Nonlinear DiD; critiques linearity assumptions in standard DD.
- **Meyer (1995)** — Overview of natural and quasi-natural experiments; foundational DiD motivation.
- **Blanchard and Katz (1992)** — Empirical evidence for strong persistence in state-level employment, wages, and unemployment shocks.
