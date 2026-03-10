# What's Trending in DiD (Roth et al. 2023)

**Full citation**: Roth, J., Sant'Anna, P.H.C., Bilinski, A., & Poe, J. (2023). What's trending in difference-in-differences? A synthesis of the recent econometrics literature. *Journal of Econometrics*, 235(2), 2218–2244.
**Tier**: Standard
**Tags**: DiD, staggered, parallel-trends, TWFE, sensitivity, inference, clustering, review
**Source file**: `references/2023 Journal of Econometrics_Whats trending in difference-in-differences - A synthesis of the recent econometrics literature.pdf`
**Extracted**: 2026-03-10

---

## Summary

This paper synthesizes the recent DiD econometrics literature and provides concrete practitioner recommendations. The authors organize advances around three relaxations of the canonical two-period DiD setup: (i) multiple periods and staggered treatment timing, (ii) potential violations of the parallel trends assumption, and (iii) alternative inference frameworks when sampling assumptions fail. The paper functions as a field guide rather than introducing a single new estimator, and is accompanied by a practitioner checklist (Table 1) and a table of R/Stata software packages (Table 2).

---

## Method / Estimator

The paper reviews and contrasts several families of methods rather than proposing one estimator.

**Canonical baseline.** Two-period, two-group DiD identified via:

τ₂ = E[Yi,2 − Yi,1 | Di=1] − E[Yi,2 − Yi,1 | Di=0]

estimated by OLS on a TWFE specification with individual and time fixed effects. Valid under parallel trends, no anticipation, and independent sampling with many clusters.

**Staggered timing — heterogeneity-robust estimators.** The core problem: TWFE with staggered adoption uses "forbidden comparisons" (already-treated units as controls), producing non-convex — potentially negative — weights on unit-level treatment effects. The paper reviews:

- *Callaway & Sant'Anna (2021)*: estimate group-time ATTs, ATT(g,t) = E[Yi,t(g) − Yi,t(∞) | Gi=g], using only not-yet-treated or never-treated units as controls; aggregate via researcher-specified weights into event-study parameters ATT_l^w = Σ_g w_g · ATT(g, g+l).
- *Borusyak, Jaravel & Spiess (2021) — imputation estimator*: fit TWFE on untreated observations only, impute counterfactual outcomes for treated units, aggregate individual-level estimates. More efficient under homoskedastic serially uncorrelated errors but requires parallel trends for all periods and groups.
- *de Chaisemartin & D'Haultfoeuille (2020)*: handles treatments that turn on and off; reports the share of group-time ATTs receiving negative TWFE weight and the degree of heterogeneity needed to flip the sign.
- *Sun & Abraham (2021)*: interaction-weighted estimator using last-treated or never-treated as comparison group; demonstrates that dynamic TWFE leads/lags are contaminated by treatment effects at other relative times under cohort heterogeneity, making pre-trends tests based on dynamic TWFE misleading.
- *Stacking (Cengiz et al. 2019)*: match each treated cohort to clean (not-yet-treated) controls with separate fixed effects per stacked event; Gardner (2021) shows this estimates a convex weighted average of ATT(g,t).

**Covariates / conditional parallel trends.** Methods reviewed:
- *Regression adjustment* (Heckman et al. 1997/1998): model the conditional expectation of outcome change among controls, average predictions over treated covariate distribution.
- *IPW* (Abadie 2005): re-weight by inverse propensity score.
- *Doubly robust* (Sant'Anna & Zhao 2020): valid if either the outcome model or propensity score model is correctly specified; achieves the semiparametric efficiency bound when both are correct. Recommended default.

Note: augmenting TWFE with time-by-covariate interactions (the naive approach) does not consistently estimate the ATT under treatment effect heterogeneity.

**Inference with few clusters.** Methods reviewed: Donald & Lang (2007) t-distribution with J−2 df (requires Gaussian homoskedastic errors); Conley & Taber (2011) (many controls, few treated, learns error distribution from controls); Ferman & Pinto (2019) extension for observable heteroskedasticity; cluster wild bootstrap (Cameron et al. 2008) with caveats about homogeneity requirements (Canay et al. 2021); permutation and conformal approaches for settings with many time periods (Canay et al. 2017; Chernozhukov et al. 2021). Design-based inference (Rambachan & Roth 2022a) treats treatment assignment — not sampling — as the source of randomness, yielding a clear clustering rule: cluster at the level at which treatment is independently assigned.

---

## Key Assumptions

1. **Parallel trends (unconditional):** E[Yi,2(0)−Yi,1(0)|Di=1] = E[Yi,2(0)−Yi,1(0)|Di=0]. Allows level-selection bias but requires trends in untreated potential outcomes to be identical across groups.
2. **No anticipation:** Yi,1(0) = Yi,1(1) for treated units — pre-treatment outcomes are unaffected by future treatment status.
3. **Staggered parallel trends:** For all adoption cohort pairs g ≠ g′ and all period pairs t ≠ t′, counterfactual trends in Yi,t(∞) are parallel across cohorts. Variants: post-treatment only (Callaway & Sant'Anna); among eventually-treated only (excluding never-treated).
4. **Conditional parallel trends:** Parallel trends holds after conditioning on pre-treatment covariates Xi; requires overlap (propensity score bounded away from 1).
5. **SUTVA:** No spillovers — unit i's outcome does not depend on unit j's treatment status.
6. **Independent sampling / large clusters:** Standard inference requires many independent treated and untreated clusters. Design-based alternative requires only that treatment is independently assigned at the clustering level.

---

## Diagnostics & Tests

- **Event-study plots:** Visual check of pre-treatment trend differences. For staggered settings, use heterogeneity-robust ATT_l^w estimates rather than dynamic TWFE coefficients, which are contaminated under cohort heterogeneity (Sun & Abraham 2021).
- **Goodman-Bacon decomposition:** Decomposes TWFE estimate into 2×2 DiD components to quantify weight placed on forbidden comparisons (implemented in `bacondecomp`/`ddtiming`).
- **de Chaisemartin & D'Haultfoeuille diagnostics:** Report share/fraction of group-time ATTs with negative TWFE weight; compute minimum treatment-effect heterogeneity needed to flip the sign (implemented in `TwoWayFEWeights`).
- **Jakiela (2021):** Tests whether TWFE places negative weights on some treated units and whether the data rejects constant treatment effects.
- **Power analysis for pre-trends (Roth 2022):** Tools to assess whether pre-tests are adequately powered against economically relevant violations; implemented in `pretrends` (R). Key finding: pre-trends tests often have low power — violations detectable only 50% of the time can produce biases as large as the estimated treatment effect.
- **Non-inferiority tests (Bilinski & Hatfield 2018; Dette & Schumann 2020):** Reverse null/alternative so that rejection requires strong evidence that pre-trends are small, addressing the low-power problem of standard pre-tests.

---

## Sensitivity Analysis

- **Rambachan & Roth (2022b) — honestDiD:** Bounds post-treatment parallel-trends violations relative to observed pre-treatment violations. Key restriction: |δ₁| ≤ M̄ · max_{r<0}|δ_r|, where δ₁ is the post-treatment violation and δ_r are pre-treatment differences in trends. Reports the "breakdown" M̄ — how large the post-treatment violation must be relative to the maximum pre-treatment violation to overturn a conclusion. Also supports restrictions bounding deviation from a linear extrapolation of pre-trends. Extends to staggered and conditional parallel trends settings. Implemented in `honestDiD` (R/Stata).
- **Bracketing bounds (Ye et al. 2021):** Uses two control groups assumed to bracket the treated group's counterfactual trend (one more cyclical, one less cyclical) to construct partial-identification bounds on the ATT.
- **Keele et al. (2019):** Sensitivity analysis summarizing the strength of confounding that would be needed to induce a given bias magnitude.
- **Freyaldenhoven et al. (2021):** Visual sensitivity analysis plotting the "smoothest" trend through an event-study plot consistent with a null treatment effect.
- **Freyaldenhoven et al. (2019):** GMM strategy that allows parallel trends violations when a covariate is affected by the same confounders as the outcome but not by the treatment itself.

---

## Limitations & Caveats

- **TWFE under staggered adoption:** The static TWFE coefficient can be negative even when all unit-level treatment effects are positive, due to negative weights from forbidden comparisons with already-treated units. Dynamic TWFE event-study coefficients are also contaminated under cohort-level treatment effect heterogeneity, making pre-trends tests based on dynamic TWFE unreliable.
- **Pre-trends testing:** Pre-tests often have low power (Roth 2022). Conditioning on a passed pre-test introduces pre-test bias — the selected subsample of draws that "pass" will be systematically distorted. A detected pre-trend does not clearly indicate how to proceed.
- **Parallel trends is functional-form sensitive:** If parallel trends holds in levels it typically does not hold in logs or other nonlinear transformations (Roth & Sant'Anna 2023). Researchers must justify their functional form choice.
- **Conditional parallel trends — bad controls:** Covariates must be pre-treatment and unaffected by treatment. Conditioning on post-treatment or treatment-affected variables induces a bad-control bias.
- **Lagged outcome as covariate:** Including a lagged outcome transforms the identifying assumption from parallel trends to conditional unconfoundedness; this is not a free robustness check and can introduce mean-reversion bias (Daw & Hatfield 2018).
- **Few clusters:** All available inference approaches require some homogeneity restrictions. The cluster wild bootstrap requires homogeneity conditions that are commonly violated in TWFE settings with heterogeneous treatment effects.
- **SUTVA:** Most DiD methods rule out spillovers; spatial or network spillovers require bespoke extensions.
- **CS vs. BJS tradeoff:** Callaway & Sant'Anna uses only the last pre-treatment period as baseline (weaker assumption, less efficient); Borusyak et al. uses all pre-treatment periods (stronger assumption, more efficient under homoskedastic non-serially-correlated errors). Neither dominates; choice depends on the plausibility of long-horizon parallel trends and degree of serial correlation.

---

## Data / Code

The paper uses Medicaid expansion as a running empirical illustration (state-level insurance coverage rates). No original dataset is introduced. Software packages catalogued in Table 2:

| Package | Software | Method |
|---|---|---|
| `did`, `csdid` | R, Stata | Callaway & Sant'Anna (2021) |
| `did2s` | R, Stata | Gardner (2021), BJS (2021), Sun & Abraham (2021), CS (2021) |
| `didimputation`, `did_imputation` | R, Stata | Borusyak et al. (2021) |
| `DIDmultiplegt`, `did_multiplegt` | R, Stata | de Chaisemartin & D'Haultfoeuille (2020) |
| `eventstudyinteract` | Stata | Sun & Abraham (2021) |
| `fixest` | R | Sun & Abraham (2021) |
| `stackedev` | Stata | Stacking (Cengiz et al. 2019) |
| `staggered` | R | Roth & Sant'Anna (2021), CS (2021), Sun & Abraham (2021) |
| `xtevent` | Stata | Freyaldenhoven et al. (2019) |
| `DRDID`, `drdid` | R, Stata | Sant'Anna & Zhao (2020) |
| `bacondecomp`, `ddtiming` | R, Stata | Goodman-Bacon (2021) diagnostics |
| `TwoWayFEWeights` | R, Stata | de Chaisemartin & D'Haultfoeuille (2020) diagnostics |
| `honestDiD` | R, Stata | Rambachan & Roth (2022b) |
| `pretrends` | R | Roth (2022) power diagnostics |

---

## Related Papers

**Core staggered DiD estimators:**
- Callaway & Sant'Anna (2021). Difference-in-Differences with multiple time periods. *J. Econometrics* 225(2), 200–230.
- Borusyak, Jaravel & Spiess (2021). Revisiting Event Study Designs: Robust and Efficient Estimation. arXiv:2108.12419.
- Sun & Abraham (2021). Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. *J. Econometrics* 225(2), 175–199.
- de Chaisemartin & D'Haultfoeuille (2020). Two-Way Fixed Effects Estimators with Heterogeneous Treatment Effects. *AER* 110(9), 2964–2996.
- Goodman-Bacon (2021). Difference-in-differences with variation in treatment timing. *J. Econometrics* 225(2), 254–277.
- Gardner (2021). Two-stage differences in differences. Working Paper.

**Covariates / doubly robust:**
- Sant'Anna & Zhao (2020). Doubly robust difference-in-differences estimators. *J. Econometrics* 219(1), 101–122.
- Abadie (2005). Semiparametric Difference-in-Differences Estimators. *Rev. Econom. Stud.* 72(1), 1–19.

**Sensitivity / robust inference for parallel trends violations:**
- Rambachan & Roth (2022b). A more credible approach to parallel trends. *Rev. Econ. Stud.* Forthcoming.
- Roth (2022). Pre-test with Caution: Event-study Estimates After Testing for Parallel Trends. *AER: Insights* 4(3), 305–322.
- Freyaldenhoven, Hansen & Shapiro (2019). Pre-event Trends in the Panel Event-Study Design. *AER* 109(9), 3307–3338.
- Bilinski & Hatfield (2018). Seeking evidence of absence: Reconsidering tests of model assumptions. arXiv:1805.03273.

**Functional form sensitivity:**
- Roth & Sant'Anna (2023). When Is Parallel Trends Sensitive to Functional Form? *Econometrica* 91(2), 737–747.

**Inference / clustering:**
- Conley & Taber (2011). Inference with "Difference in Differences" with a Small Number of Policy Changes. *Rev. Econ. Stat.* 93(1), 113–125.
- Rambachan & Roth (2022a). Design-Based Uncertainty for Quasi-Experiments. arXiv:2008.00602.
- Ferman & Pinto (2019). Inference in Differences-in-Differences with Few Treated Groups and Heteroskedasticity. *Rev. Econ. Stat.* 101(3), 452–467.

**Synthetic control connections:**
- Arkhangelsky et al. (2021). Synthetic Difference-in-Differences. *AER* 111(12), 4088–4118.
- Abadie (2021). Using Synthetic Controls: Feasibility, Data Requirements, and Methodological Aspects. *J. Econ. Lit.* 59(2), 391–425.
