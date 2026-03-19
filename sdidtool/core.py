"""
Core SyntheticDiD class: wraps the `synthdid` package with a clean high-level API.

Usage
-----
    from sdidtool import SyntheticDiD

    model = SyntheticDiD(
        df=df,
        unit='state',
        time='year',
        outcome='packspercapita',
        treatment='treated',
    )
    results = model.run()
    print(results.summary())
    results.plot()
"""

from __future__ import annotations

import contextlib
import io
import warnings
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd

from .utils import check_panel_balance, detect_outlier_units

# Lazy import so the package can be imported even if synthdid isn't installed
# (useful for type checking and docs).
def _get_synthdid():
    try:
        from synthdid.synthdid import Synthdid
        return Synthdid
    except ImportError as e:
        raise ImportError(
            "The `synthdid` package is required. Install with: pip install synthdid --no-deps"
        ) from e


InferenceMethod = Literal["placebo", "bootstrap", "jackknife"]
EstimatorType = Literal["sdid", "sc", "did"]


@dataclass
class SyntheticDiDResults:
    """Results from a single SDID (or SC / DiD) run."""

    estimator: EstimatorType
    inference: InferenceMethod | None
    att: float
    se: float | None
    n_reps: int | None
    seed: int | None
    n_failed: int | None
    _model: object = field(repr=False)  # underlying synthdid model

    @property
    def rep_success_pct(self) -> float | None:
        if self.n_reps is None or self.n_failed is None:
            return None
        return round(100 * (self.n_reps - self.n_failed) / self.n_reps, 1)

    @property
    def ci_lower(self) -> float | None:
        if self.se is None:
            return None
        return self.att - 1.96 * self.se

    @property
    def ci_upper(self) -> float | None:
        if self.se is None:
            return None
        return self.att + 1.96 * self.se

    @property
    def pvalue(self) -> float | None:
        if self.se is None:
            return None
        from scipy.stats import norm
        return float(2 * (1 - norm.cdf(abs(self.att / self.se))))

    def summary(self) -> pd.DataFrame:
        """Return a one-row DataFrame with ATT, SE, 95% CI, and p-value."""
        return pd.DataFrame([{
            "estimator": self.estimator,
            "att": round(self.att, 4),
            "se": round(self.se, 4) if self.se is not None else None,
            "ci_lower": round(self.ci_lower, 4) if self.ci_lower is not None else None,
            "ci_upper": round(self.ci_upper, 4) if self.ci_upper is not None else None,
            "pvalue": round(self.pvalue, 4) if self.pvalue is not None else None,
            "inference": self.inference,
            "rep_success_pct": self.rep_success_pct,
        }])

    def plot(self, show: bool = True):
        """Return a dict with 'trends' and 'weights' matplotlib figures."""
        import matplotlib.pyplot as plt
        figs = {}
        try:
            self._model.plot_outcomes()
            figs["trends"] = plt.gcf()
            if show:
                plt.show()
        except Exception:
            pass
        try:
            self._model.plot_weights()
            figs["weights"] = plt.gcf()
            if show:
                plt.show()
        except Exception:
            pass
        return None if show else figs


class SyntheticDiD:
    """
    High-level wrapper for Synthetic Difference-in-Differences analysis.

    Parameters
    ----------
    df : pd.DataFrame
        Panel dataset in long format (one row per unit×time).
    unit : str
        Column name for the unit identifier.
    time : str
        Column name for the time variable.
    outcome : str
        Column name for the outcome variable.
    treatment : str
        Column name for the binary treatment indicator (0/1).
    covariates : list[str] | None
        Optional list of covariate column names.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        unit: str,
        time: str,
        outcome: str,
        treatment: str,
        covariates: list[str] | None = None,
    ):
        self.df = df.copy()
        self.unit = unit
        self.time = time
        self.outcome = outcome
        self.treatment = treatment
        self.covariates = covariates

    def run(
        self,
        estimator: EstimatorType = "sdid",
        inference: InferenceMethod = "placebo",
        n_reps: int = 200,
        seed: int | None = 1213,
        cov_method: Literal["optimized", "projected"] | None = "optimized",
        plot: bool = False,
        df: pd.DataFrame | None = None,
    ) -> SyntheticDiDResults:
        """
        Fit SDID (or SC / DiD) and run inference.

        Parameters
        ----------
        estimator : 'sdid' | 'sc' | 'did'
        inference : 'placebo' | 'bootstrap' | 'jackknife'
        n_reps : Number of bootstrap / placebo repetitions.
        seed : Random seed for reproducibility.
        cov_method : Covariate adjustment method ('optimized' | 'projected' | None).
        plot : If True, display trend and weight plots immediately.
        df : Override the dataset (used internally by sensitivity runner).
        """
        Synthdid = _get_synthdid()
        data = df if df is not None else self.df
        covariates = self.covariates if cov_method else None

        check_panel_balance(data, self.unit, self.time)

        model = Synthdid(
            data=data,
            unit=self.unit,
            time=self.time,
            treatment=self.treatment,
            outcome=self.outcome,
            covariates=covariates,
        )

        fit_kwargs: dict = {}
        if estimator == "sc":
            fit_kwargs["synth"] = True
        elif estimator == "did":
            fit_kwargs["did"] = True
        if covariates and cov_method:
            fit_kwargs["cov_method"] = cov_method

        captured = io.StringIO()
        with warnings.catch_warnings(), \
             contextlib.redirect_stdout(captured), \
             contextlib.redirect_stderr(captured):
            warnings.simplefilter("ignore")
            model.fit(**fit_kwargs)

            if seed is not None:
                np.random.seed(seed)

            if inference == "jackknife":
                model.vcov(method="jackknife", n_reps=n_reps)
            else:
                model.vcov(method=inference, n_reps=n_reps)

        n_failed = captured.getvalue().count("Error")

        att = float(model.att)
        se = float(model.se) if model.se is not None else None

        results = SyntheticDiDResults(
            estimator=estimator,
            inference=inference,
            att=att,
            se=se,
            n_reps=n_reps,
            seed=seed,
            n_failed=n_failed if inference in ("placebo", "bootstrap") else None,
            _model=model,
        )

        if plot:
            results.plot(show=True)

        return results

    def sensitivity(
        self,
        pre_periods: list[int] | None = None,
        drop_units: list | None = None,
        drop_outliers: bool = False,
        outlier_threshold: float = 3.0,
        inference_methods: list[InferenceMethod] | None = None,
        cov_variants: list[str | None] | None = None,
        compare_estimators: bool = True,
        n_reps: int = 200,
        seed: int | None = 1213,
    ) -> "SensitivityResults":
        """
        Run a battery of sensitivity tests and return a comparison table.

        Parameters
        ----------
        pre_periods : list[int]
            List of pre-treatment window lengths to try (e.g. [5, 10, 20]).
            Each value trims the dataset to keep only the last N pre-treatment periods.
        drop_units : list
            Explicit unit IDs to exclude from the analysis.
        drop_outliers : bool
            If True, detect and drop outlier units (IQR/Z-score based).
        outlier_threshold : float
            Z-score threshold for outlier detection (default 3.0).
        inference_methods : list['placebo'|'bootstrap'|'jackknife']
            Inference methods to compare (default: all three).
        cov_variants : list[str|None]
            Covariate adjustment variants to try (default: [None, 'optimized', 'projected']
            only if covariates are provided).
        compare_estimators : bool
            If True, run DiD, SC, and SDID for comparison.
        n_reps : int
            Repetitions for stochastic inference.
        seed : int | None
            Random seed.

        Returns
        -------
        SensitivityResults
        """
        from .sensitivity import SensitivityRunner
        runner = SensitivityRunner(self)
        return runner.run(
            pre_periods=pre_periods,
            drop_units=drop_units,
            drop_outliers=drop_outliers,
            outlier_threshold=outlier_threshold,
            inference_methods=inference_methods,
            cov_variants=cov_variants,
            compare_estimators=compare_estimators,
            n_reps=n_reps,
            seed=seed,
        )

    def _trim_pre_periods(self, df: pd.DataFrame, n_pre: int) -> pd.DataFrame:
        """Keep only the last n_pre pre-treatment periods + all post-treatment periods."""
        # Find treatment start time (minimum time where treatment == 1)
        treat_start = df[df[self.treatment] == 1][self.time].min()
        pre_times = sorted(df[df[self.time] < treat_start][self.time].unique())
        if len(pre_times) <= n_pre:
            return df  # Already short enough
        keep_pre = set(pre_times[-n_pre:])
        keep_post = set(df[df[self.time] >= treat_start][self.time].unique())
        return df[df[self.time].isin(keep_pre | keep_post)].copy()
