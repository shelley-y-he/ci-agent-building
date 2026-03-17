"""sdid — Synthetic Difference-in-Differences analysis toolkit."""

from .core import SyntheticDiD, SyntheticDiDResults
from .sensitivity import SensitivityResults

__all__ = ["SyntheticDiD", "SyntheticDiDResults", "SensitivityResults"]
