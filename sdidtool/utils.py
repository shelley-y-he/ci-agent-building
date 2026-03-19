"""Utility helpers for the sdidtool wrapper: data validation, outlier detection, loading."""

import pandas as pd
import numpy as np
from pathlib import Path


def check_panel_balance(df: pd.DataFrame, unit: str, time: str) -> None:
    """Raise ValueError if the panel has missing unit×time cells."""
    units = df[unit].unique()
    times = df[time].unique()
    n_expected = len(units) * len(times)
    n_actual = len(df)
    if n_actual != n_expected:
        # Find the gaps
        full_index = pd.MultiIndex.from_product([units, times], names=[unit, time])
        actual_index = pd.MultiIndex.from_frame(df[[unit, time]])
        missing = full_index.difference(actual_index)
        raise ValueError(
            f"Unbalanced panel: expected {n_expected} rows, got {n_actual}. "
            f"{len(missing)} missing unit×time cells.\n"
            f"First 10 missing: {list(missing[:10])}"
        )


def detect_outlier_units(
    df: pd.DataFrame, unit: str, outcome: str, threshold: float = 3.0
) -> list:
    """
    Return list of unit IDs whose mean outcome is an outlier (Z-score > threshold).
    Uses the distribution of unit-level means across all units.
    """
    unit_means = df.groupby(unit)[outcome].mean()
    z = (unit_means - unit_means.mean()) / unit_means.std()
    outliers = unit_means[z.abs() > threshold].index.tolist()
    return outliers


def load_dataset(path: str) -> pd.DataFrame:
    """Load a dataset from .dta, .csv, or .parquet by file extension."""
    p = Path(path)
    if p.suffix == ".dta":
        return pd.read_stata(path)
    elif p.suffix == ".csv":
        return pd.read_csv(path)
    elif p.suffix in (".parquet", ".pq"):
        return pd.read_parquet(path)
    else:
        raise ValueError(f"Unsupported file format: {p.suffix}. Use .dta, .csv, or .parquet.")
