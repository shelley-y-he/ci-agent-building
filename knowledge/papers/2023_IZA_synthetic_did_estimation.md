# Synthetic Difference-in-Differences Estimation (Clarke, Pailañir, Athey, Imbens 2023)

**Full citation**: Clarke, D., Pailañir, D., Athey, S., & Imbens, G. (2023). Synthetic Difference-in-Differences Estimation. *IZA Discussion Paper*, No. 15907.
**Tier**: Deep
**Tags**: DiD, synthetic-control, SDiD, staggered, inference, Stata, implementation
**Source file**: `references/2023 IZA_Synthetic Difference-in-Differences Estimation.pdf`
**Extracted**: 2026-03-10

---

## Summary

This paper describes the Stata implementation (`sdid`) of the Synthetic Difference-in-Differences (SDID) estimator originally developed by Arkhangelsky et al. (2021). It provides a detailed exposition of the SDID theory for both block (single adoption date) and staggered adoption designs, covers all three inference procedures (bootstrap, jackknife, placebo), explains covariate adjustment options, and demonstrates the estimator through two empirical applications — California's Proposition 99 tobacco law and parliamentary gender quotas. The paper is primarily a methods/software documentation paper rather than a theoretical contribution, but it extends the original Arkhangelsky et al. framework by detailing the staggered adoption algorithms and covariate handling more explicitly.

---

## Method / Estimator

**Core estimator.** SDID estimates the ATT from a two-way fixed effects regression with optimally chosen unit weights (omega) and time weights (lambda):

```
(tau_hat, mu_hat, alpha_hat, beta_hat) = argmin over (tau, mu, alpha, beta):
    sum_{i=1}^{N} sum_{t=1}^{T} (Y_it - mu - alpha_i - beta_t - W_it * tau)^2
    * omega_hat_i * lambda_hat_t
```

This nests DID (omega_i = 1/N, lambda_t = 1/T for all units/periods) and SC (optimal omega, no unit FE, no time weights).

**Unit weights (omega).** Found by solving a regularized least squares problem that minimizes the discrepancy between the weighted control pre-trends and the treated pre-trends:

```
(omega_0_hat, omega_hat) = argmin over (omega_0, omega in Omega):
    sum_{t=1}^{T_pre} (omega_0 + sum_{i=1}^{N_co} omega_i * Y_it
        - (1/N_tr) * sum_{i=N_co+1}^{N} Y_it)^2
    + zeta^2 * T_pre * ||omega||_2^2
```

The constraint set Omega requires omega_i >= 0 and sum(omega_i) = 1 for control units; treated units receive weight 1/N_tr. The intercept omega_0 allows a constant level difference between treatment and controls (unlike SC, which requires approximate level matching). The regularization parameter is `zeta = (N_tr * T_post)^(1/4) * sigma_hat`, where sigma_hat^2 is estimated from first differences of the pre-treatment control outcomes.

**Time weights (lambda).** Found by minimizing discrepancy between weighted pre-treatment period averages and the post-treatment average for each control unit:

```
(lambda_0_hat, lambda_hat) = argmin over (lambda_0, lambda in Lambda):
    sum_{i=1}^{N_co} (lambda_0 + sum_{t=1}^{T_pre} lambda_t * Y_it
        - (1/T_post) * sum_{t=T_pre+1}^{T} Y_it)^2
    + zeta^2 * N_co * ||lambda||^2
```

Lambda constraints: lambda_t >= 0, sum of pre-treatment lambda_t = 1; post-treatment periods receive equal weight 1/T_post. The regularization for time weights uses a very small constant (zeta = 1e-6 * sigma_hat) to ensure uniqueness.

**Staggered adoption.** For A distinct adoption dates, the staggered ATT is a weighted average of adoption-specific SDID estimates:

```
ATT_hat = sum_{a in A} (T_post^a / T_post) * tau_hat_sdid_a
```

where each tau_hat_sdid_a is estimated on the subsample of pure controls and units that first adopt in period a. Weights are proportional to the number of post-treatment periods contributed by each adoption cohort.

**Covariate adjustment.** Two approaches:
1. *Optimized* (default, Arkhangelsky et al. 2021): SDID is applied to residuals Y_it^res = Y_it - X_it * beta_hat, where beta is estimated jointly within the Frank-Wolfe optimization. Can be numerically sensitive if covariates have high variance; standardizing as Z-scores is recommended.
2. *Projected* (Kranz 2022): beta is estimated by OLS of Y_it on X_it + unit FE + time FE using only untreated observations (W_it = 0), then residuals are passed to SDID. More stable and substantially faster.

---

## Key Assumptions

1. **Balanced panel**: Strongly balanced panel required — every unit observed in every time period. No missing outcomes or covariates permitted.
2. **No always-treated units**: Units treated from period 1 cannot be included because no pre-treatment period exists for weight construction.
3. **At least two pre-treatment periods**: Needed to compute regularization parameter (sigma_hat requires computing first differences).
4. **Pure control units exist**: At least some units must never be treated to serve as donor pool.
5. **No parallel trends required in aggregate**: SDID is consistent without parallel trends because it optimally constructs a synthetic control that matches pre-trends by design; the unit FE additionally allows constant level differences (unlike SC).
6. **Treatment irreversibility**: Once treated, units remain treated. The framework assumes absorbing treatment.
7. **Homoskedasticity across units** (for placebo inference only): Placebo variance estimation requires that untreated units have the same variance as treated units, since placebo assignments are made only within the control group.
8. **Number of treated units grows** (for bootstrap and jackknife): Asymptotic normality proofs require the number of treated units to grow with N. With only one treated unit, only placebo inference is appropriate.

---

## Diagnostics & Tests

1. **Pre-trend visual inspection**: The `graph` option in `sdid` produces (a) a unit-specific weights scatter plot showing the difference-in-difference estimate for each control unit vs. its assigned weight, and (b) an outcome trends plot showing treated vs. synthetic control trajectories over time with time weights displayed as a bar chart at the bottom. Visual convergence of pre-treatment trends between treated and synthetic control is the primary diagnostic.

2. **Event study style plot**: Section 4.4 describes how to compute and plot the quantity (Y_bar_tr_t - Y_bar_co_t) - (Y_bar_tr_baseline - Y_bar_co_baseline) for each t, where the baseline is the SDID-weighted pre-treatment average. This is the analogue of a panel event study. Pre-treatment estimates should cluster around zero if SDID matching is successful.

3. **Comparison across methods**: The `method()` option allows running SDID, DID, and SC on the same data and comparing graphical outputs and estimates. Divergence of DID trends in pre-treatment periods (observable in method(did) graphs) motivates SDID.

4. **Adoption-specific estimates**: In staggered designs, `e(tau)` returns the ATT for each adoption cohort. Examining heterogeneity across cohorts can reveal whether treatment effects vary by timing.

5. **Bootstrap convergence check**: Default 50 repetitions is explicitly noted as too few for reliable inference; larger reps are recommended and scalable with the `reps(#)` option.

---

## Sensitivity Analysis

1. **Inference method comparison**: Bootstrap, jackknife, and placebo procedures can all be run and compared. Jackknife tends to be conservative (wider CIs); this is documented both theoretically and empirically in the gender quota example (jackknife SE = 6.01, bootstrap SE = 4.73, placebo SE = 5.15 for the same estimate of 10.33).

2. **Covariate inclusion**: The gender quota example shows that including log GDP per capita (via either optimized or projected method) produces ATT = 8.05, nearly identical to the no-covariate ATT = 8.03. This confirms the covariate does not substantially confound the estimate in this application.

3. **Covariate method comparison**: Optimized vs. projected covariate adjustment can be compared directly. In the gender quota example, both give ATT ≈ 8.05, but projected is 5x faster (61 vs. 324 seconds with 50 bootstrap reps).

4. **Method (SDID vs. DID vs. SC)**: The `method()` option enables direct comparison. In the Proposition 99 example, the three estimators produce different estimates and match quality, illustrating the sensitivity of standard DID/SC to their respective assumptions.

5. **Unstandardized covariates**: The `unstandardized` option bypasses automatic Z-score normalization and should be used cautiously. Sensitivity of results to covariate scaling is a documented risk.

---

## Limitations & Caveats

1. **Requires balanced panel**: Missing observations must be imputed or those units dropped. This can be restrictive in practice and may introduce selection bias if missingness is non-random.

2. **No always-treated units**: Applications where all pre-period data is post-treatment for some units cannot use SDID without additional data.

3. **Requires pure controls**: If all units eventually receive treatment, the method fails entirely.

4. **Small number of treated units**: With one treated unit (as in Proposition 99), only placebo inference is valid. Bootstrap and jackknife CIs are unreliable. This is a common constraint in comparative case studies.

5. **Jackknife undefined with one treated unit per cohort**: In staggered designs, any cohort with only one treated unit makes the jackknife undefined for that cohort.

6. **Placebo requires more controls than treated units**: Permutation-based inference cannot be constructed when the number of treated units meets or exceeds the number of control units.

7. **Staggered design with few pure controls**: The staggered extension may be ineffective when the pool of pure control units is small, since each adoption-specific subsample needs sufficient controls to construct a good synthetic counterfactual.

8. **Covariate optimization instability**: The Frank-Wolfe solver for the optimized covariate method can be numerically sensitive when covariates have high variance, potentially yielding non-globally-optimal solutions. Standardization mitigates but does not eliminate this risk.

9. **Homoskedasticity for placebo**: Placebo inference is only valid under homoskedasticity across units — an assumption that may fail in practice (e.g., larger countries vs. smaller ones in the gender quota panel).

10. **Event study CIs require manual coding**: Constructing event study plots with proper CIs is not automated by `sdid` and requires non-trivial Stata programming (detailed in Section 4.4).

---

## Data / Code

**Datasets:**
- `prop99_example.dta`: 39 US states, 1970–2000, cigarette packs per capita (Orzechowski & Walker 2005 via Abadie et al. 2010). Available at `www.damianclarke.net/stata/`.
- `quota_example.dta`: 115 countries, 1990–2015, women in parliament (%), maternal mortality, log GDP per capita. Based on Bhalotra et al. (2022) but subset to countries with complete observations. Available at `www.damianclarke.net/stata/`.

**Software:**
- Primary: Stata `sdid` command by Pailañir & Clarke (2022), written in Mata. Available via SSC: `ssc install sdid` (or `https://ideas.repec.org/c/boc/bocode/s459058.html`).
- R equivalent: `synthdid` package by Hirshberg (undated), available at `https://synth-inference.github.io/synthdid/`. Results are identical to `sdid` (abstracting from pseudo-random number generation differences) where procedures overlap.
- Covariate alternative: `xsynth` package in R (Kranz 2022), implements the projected covariate method.

**Key command syntax:**
```stata
sdid depvar groupvar timevar treatment [if] [in], vce(type) [covariates(varlist, type) seed(#) reps(#) method(type) graph g1on g1_opt(string) g2_opt(string) graph_export(string, type) msize() unstandardized mattitles]
```

---

## Replication Notes

### Example 1: Proposition 99 (Block Design)

**Data**: `prop99_example.dta` from `www.damianclarke.net/stata/`. 39 US states (1 treated: California, 38 controls), years 1970–2000. Outcome: cigarette packs sold per capita (`packspercapita`). Treatment: `treated` = 1 for California from 1989 onward. Panel dimensions: N = 39, T = 31, T_pre = 19 (1970–1988), T_post = 12 (1989–2000), N_co = 38, N_tr = 1.

**Exact replication steps:**
```stata
webuse set www.damianclarke.net/stata/
webuse prop99_example.dta, clear
sdid packspercapita state year treated, vce(placebo) seed(1213)
```

**Key implementation choices:**
- `vce(placebo)` is the only appropriate inference method because N_tr = 1 (bootstrap and jackknife require multiple treated units).
- `seed(1213)` must be set to replicate the reported standard error (the point estimate is deterministic; the SE is not).
- Default 50 placebo replications used (authors note more reps are preferable).

**Reported results:**
- ATT = -15.604 (identical to Table 1 of Arkhangelsky et al. 2021)
- SE = 9.532 (placebo-based; slightly differs from Arkhangelsky et al. due to pseudo-random draws)
- 95% CI: [-34.286, 3.078]; p = 0.102 (not significant at 5%)

**Graph replication:**
```stata
sdid packspercapita state year treated, vce(placebo) seed(1213) graph g1on ///
    g2_opt(ylabel(0(25)150) ytitle("Packs per capita") scheme(sj)) ///
    g1_opt(xtitle("") scheme(sj)) g1on graph_export(sdid_, .eps)
```
This produces Figure 1: (a) unit-specific weights scatter, (b) outcome trends with time weights.

**Manual graph replication** (to replicate Figure 1b from stored matrices):
```stata
preserve
clear
matrix series=e(series)
matrix lambda=e(lambda)
qui svmat series, names(col)
qui svmat lambda
tw line Yco1989 year, yaxis(1) || line Ytr1989 year, yaxis(1) || ///
    bar lambda1 year if year<=1988, yaxis(2) ylabel(0(1)5, axis(2)) ///
    yscale(off axis(2)) xline(1989, lc(red)) ///
    legend(order(1 "Control" 2 "Treated") pos(12) col(2)) scheme(sj)
graph export sdid_replicate.eps, replace
restore
```

**Comparison with DID and SC** (Figure 2):
```stata
sdid packspercapita state year treated, method(sdid) vce(noinference) graph g1on ...
sdid packspercapita state year treated, method(did)  vce(noinference) graph g1on ...
sdid packspercapita state year treated, method(sc)   vce(noinference) graph g1on ...
```

### Example 2: Parliamentary Gender Quotas (Staggered Adoption)

**Data**: `quota_example.dta` from `www.damianclarke.net/stata/`. 115 countries, 1990–2015 (but restricted to complete observations). 9 treated countries adopted parliamentary gender quotas across 7 distinct adoption years between 2000 and 2013. Outcome: `womparl` (% women in parliament). Treatment: `quota`. Covariate available: `lngdp` (log GDP per capita).

**Exact replication steps (no covariates):**
```stata
webuse quota_example.dta, clear
sdid womparl country year quota, vce(bootstrap) seed(1213)
```

**Reported results (no covariates):**
- ATT = 8.034, SE = 3.740, p = 0.032, 95% CI: [0.703, 15.365]
- Adoption-specific estimates from `matlist e(tau)`:
  - 2000: 8.389, 2002: 6.968, 2003: 13.952, 2005: -3.451, 2010: 2.749, 2012: 21.763, 2013: -0.820

**With covariates (optimized method):**
```stata
drop if lngdp==.   // drops some control countries with missing GDP
sdid womparl country year quota, vce(bootstrap) seed(1213) covariates(lngdp)
```
- ATT = 8.052, SE = 3.093, p = 0.009, 95% CI: [1.990, 14.113]
- Computational time: ~324 seconds (50 bootstrap reps)

**With covariates (projected method, Kranz 2022):**
```stata
sdid womparl country year quota, vce(bootstrap) seed(1213) covariates(lngdp, projected)
```
- ATT = 8.059, SE = 3.119, p = 0.010, 95% CI: [1.946, 14.173]
- Computational time: ~61 seconds (vs. 324 for optimized) — 5x faster

**Table 1 replication** (three models with estout):
```stata
webuse quota_example.dta, clear
lab var quota "Parliamentary Gender Quota"
eststo sdid_1: sdid womparl country year quota, vce(bootstrap) seed(2022)
drop if lngdp==.
eststo sdid_2: sdid womparl country year quota, vce(bootstrap) seed(2022) covariates(lngdp, optimized)
eststo sdid_3: sdid womparl country year quota, vce(bootstrap) seed(2022) covariates(lngdp, projected)
esttab sdid_1 sdid_2 sdid_3 using "example1.tex", nonotes nomtitles ...
```
Note: seed changes to 2022 here vs. 1213 above, so SEs will differ slightly from the single-model runs.

### Example 3: Inference comparison (reduced staggered sample)

For jackknife to be feasible, the sample is restricted to countries adopting quotas only in 2002 and 2003 (dropping Algeria, Kenya, Samoa, Swaziland, Tanzania):
```stata
webuse quota_example.dta, clear
drop if country=="Algeria" | country=="Kenya" | country=="Samoa" | ///
        country=="Swaziland" | country=="Tanzania"
sdid womparl country year quota, vce(bootstrap) seed(1213)  // ATT=10.331, SE=4.729
sdid womparl country year quota, vce(placebo) seed(1213)    // ATT=10.331, SE=5.147
sdid womparl country year quota, vce(jackknife)              // ATT=10.331, SE=6.006
```
Execution times on a standard PC with Stata SE 15.1: bootstrap 18.2s, placebo 10.1s, jackknife 0.7s (50 reps for bootstrap/placebo).

### Example 4: Event study plot (Section 4.4)

For 2002 adoption cohort only, with projected covariates and 100 bootstrap reps. Key steps:
1. Keep 2002 adopters and pure controls; drop if lngdp missing.
2. Run `sdid womparl country year quota, vce(noinference) graph covariates(lngdp, projected)`.
3. Extract `e(lambda)` (pre-treatment time weights, 12 periods), `e(series)` (Yco and Ytr trajectories), and `e(difference)` (Ytr - Yco by year, 26 periods).
4. Compute baseline: `meanpre_o = lambda' * (Ytr - Yco)` using only pre-treatment periods.
5. Compute event study gap: `d = (Ytr_t - Yco_t) - meanpre_o` for all t.
6. Bootstrap B=100 times using `bsample, cluster(country)`, recomputing `d` in each resample.
7. Compute `rowsd()` across bootstrap replicates to get SE for each year; construct 95% CI as `d ± 1.96*SE`.
8. Plot scatter of `d` with `rarea` CIs.

---

## Key Quotes

- "SDID avoids common pitfalls in standard DID and SC methods — namely an inability to estimate causal relationships if parallel trends are not met in aggregate data in the case of DID, and a requirement that the treated unit be housed within a 'convex hull' of control units in the case of SC." (p. 3)

- "The presence of unit-fixed effects implies that SDID will simply seek to match treated and control units on pre-treatment trends, and not necessarily on both pre-treatment trends and levels, allowing for a constant difference between treatment and control units." (p. 4)

- "Given limits to these inference options when the number of treated units is small, an alternative placebo, or permutation-based, inference procedure is proposed." (p. 7)

- "In the case of this placebo-based variance, homoskedasticity across units is required, given that the variance is based off placebo assignments of treatment made only within the control group." (p. 7)

---

## Related Papers

- **Arkhangelsky, Athey, Hirshberg, Imbens, Wager (2021)** — *AER* 111(12): 4088–4118. The foundational SDID paper. This IZA paper is its Stata implementation companion. Must read alongside.
- **Abadie, Diamond, Hainmueller (2010)** — *JASA* 105(490): 493–505. Synthetic control methods; Proposition 99 original application.
- **Kranz (2022)** — Technical report on SDID with time-varying covariates; introduces the "projected" covariate method (`xsynth` in R).
- **Hirshberg (undated)** — `synthdid` R package; original R code from Arkhangelsky et al. (2021).
- **Athey & Imbens (2022)** — *Journal of Econometrics* 226(1): 62–79. Design-based analysis in DiD with staggered adoption.
- **Ben-Michael, Feller, Rothstein (2021)** — *JASA* 116(536): 1789–1803. Augmented synthetic control; alternative to SDID for staggered settings.
- **de Chaisemartin & D'Haultfoeuille (2022)** — *Econometrics Journal*. Survey of two-way FE and DiD with heterogeneous effects.
- **Roth, Sant'Anna, Bilinski, Poe (2022)** — Survey of recent DiD econometrics literature.
- **Sun & Abraham (2021)** — *Journal of Econometrics* 225(2): 175–199. Dynamic treatment effects in event studies with heterogeneous treatment; proposed as one way to aggregate staggered SDID event studies.
- **Conley & Taber (2011)** — *REStat* 93(1): 113–125. Inference with few policy changes; theoretical grounding for placebo-based inference.
- **Bhalotra, Clarke, Gomes, Venkataramani (2022)** — NBER WP 30103. Source of gender quota data used in the staggered adoption example.
- **Freyaldenhoven, Hansen, Shapiro (2019)** — *AER* 109(9): 3307–38. Pre-event trends and panel event study design.
- **Clarke & Tapia-Schythe (2021)** — *Stata Journal* 21(4): 853–884. Panel event study implementation in Stata (`eventdd`).
