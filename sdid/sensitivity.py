"""
SensitivityRunner: orchestrates sensitivity analyses over multiple variants
and returns a SensitivityResults object with a comparison table.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from .core import SyntheticDiD


@dataclass
class SensitivityResults:
    """Results from a sensitivity analysis run."""

    table: pd.DataFrame  # columns: variant, att, se, ci_lower, ci_upper, pvalue

    def __repr__(self) -> str:
        return f"SensitivityResults with {len(self.table)} variants\n{self.table.to_string(index=False)}"

    def plot(self, show: bool = True):
        """Forest plot of ATT estimates with 95% CIs across variants."""
        import matplotlib.pyplot as plt
        import numpy as np

        df = self.table.dropna(subset=["att"])
        fig, ax = plt.subplots(figsize=(9, max(4, len(df) * 0.45)))

        y = np.arange(len(df))
        ax.scatter(df["att"], y, zorder=3, color="steelblue", s=50)

        has_ci = df["ci_lower"].notna() & df["ci_upper"].notna()
        for i, (_, row) in enumerate(df.iterrows()):
            if has_ci.iloc[i]:
                ax.hlines(y[i], row["ci_lower"], row["ci_upper"],
                          color="steelblue", linewidth=1.5)

        ax.axvline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
        ax.set_yticks(y)
        ax.set_yticklabels(df["variant"], fontsize=9)
        ax.set_xlabel("ATT estimate (with 95% CI)")
        ax.set_title("Sensitivity Analysis: ATT across variants")
        ax.grid(axis="x", alpha=0.3)
        fig.tight_layout()

        if show:
            plt.show()
        return fig


class SensitivityRunner:
    def __init__(self, model: "SyntheticDiD"):
        self.model = model

    def run(
        self,
        pre_periods=None,
        drop_units=None,
        drop_outliers=False,
        outlier_threshold=3.0,
        inference_methods=None,
        cov_variants=None,
        compare_estimators=True,
        n_reps=200,
        seed=1213,
    ) -> SensitivityResults:
        from .utils import detect_outlier_units

        model = self.model
        base_df = model.df.copy()
        rows = []

        # Default inference methods
        if inference_methods is None:
            inference_methods = ["placebo", "bootstrap", "jackknife"]

        # Default covariate variants (only if covariates provided)
        if cov_variants is None:
            if model.covariates:
                cov_variants = [None, "optimized", "projected"]
            else:
                cov_variants = [None]

        # Default estimators
        estimators = ["sdid", "sc", "did"] if compare_estimators else ["sdid"]

        # --- Baseline ---
        rows.append(self._run_variant(
            label="baseline",
            df=base_df,
            estimator="sdid",
            inference=inference_methods[0],
            cov_method=None,
            n_reps=n_reps,
            seed=seed,
        ))

        # --- Estimator comparison ---
        if compare_estimators:
            for est in ["sc", "did"]:
                rows.append(self._run_variant(
                    label=f"estimator={est}",
                    df=base_df,
                    estimator=est,
                    inference=inference_methods[0],
                    cov_method=None,
                    n_reps=n_reps,
                    seed=seed,
                ))

        # --- Inference method comparison ---
        for inf in inference_methods:
            if inf == inference_methods[0]:
                continue  # already in baseline
            rows.append(self._run_variant(
                label=f"inference={inf}",
                df=base_df,
                estimator="sdid",
                inference=inf,
                cov_method=None,
                n_reps=n_reps,
                seed=seed,
            ))

        # --- Covariate variants ---
        if model.covariates:
            for cov_m in cov_variants:
                if cov_m is None:
                    continue  # no covariates = baseline
                rows.append(self._run_variant(
                    label=f"covariates={cov_m}",
                    df=base_df,
                    estimator="sdid",
                    inference=inference_methods[0],
                    cov_method=cov_m,
                    n_reps=n_reps,
                    seed=seed,
                ))

        # --- Pre-treatment period length ---
        if pre_periods:
            for n_pre in pre_periods:
                df_trimmed = model._trim_pre_periods(base_df, n_pre)
                rows.append(self._run_variant(
                    label=f"pre_periods={n_pre}",
                    df=df_trimmed,
                    estimator="sdid",
                    inference=inference_methods[0],
                    cov_method=None,
                    n_reps=n_reps,
                    seed=seed,
                ))

        # --- Outlier exclusion ---
        if drop_outliers:
            outliers = detect_outlier_units(
                base_df, model.unit, model.outcome, outlier_threshold
            )
            if outliers:
                df_no_outliers = base_df[~base_df[model.unit].isin(outliers)].copy()
                rows.append(self._run_variant(
                    label=f"drop_outliers ({len(outliers)} units)",
                    df=df_no_outliers,
                    estimator="sdid",
                    inference=inference_methods[0],
                    cov_method=None,
                    n_reps=n_reps,
                    seed=seed,
                ))
            else:
                rows.append({
                    "variant": "drop_outliers (none detected)",
                    "att": None, "se": None, "ci_lower": None, "ci_upper": None, "pvalue": None,
                })

        # --- Explicit unit drop ---
        if drop_units:
            df_dropped = base_df[~base_df[model.unit].isin(drop_units)].copy()
            rows.append(self._run_variant(
                label=f"drop_units={drop_units}",
                df=df_dropped,
                estimator="sdid",
                inference=inference_methods[0],
                cov_method=None,
                n_reps=n_reps,
                seed=seed,
            ))

        table = pd.DataFrame(rows)
        return SensitivityResults(table=table)

    def _run_variant(
        self,
        label: str,
        df: pd.DataFrame,
        estimator: str,
        inference: str,
        cov_method,
        n_reps: int,
        seed,
    ) -> dict:
        try:
            result = self.model.run(
                estimator=estimator,
                inference=inference,
                n_reps=n_reps,
                seed=seed,
                cov_method=cov_method,
                plot=False,
                df=df,
            )
            return {
                "variant": label,
                "att": round(result.att, 4),
                "se": round(result.se, 4) if result.se is not None else None,
                "ci_lower": round(result.ci_lower, 4) if result.ci_lower is not None else None,
                "ci_upper": round(result.ci_upper, 4) if result.ci_upper is not None else None,
                "pvalue": round(result.pvalue, 4) if result.pvalue is not None else None,
            }
        except Exception as e:
            return {
                "variant": label,
                "att": None, "se": None, "ci_lower": None, "ci_upper": None, "pvalue": None,
                "error": str(e),
            }
