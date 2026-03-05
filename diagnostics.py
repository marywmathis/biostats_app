# diagnostics.py

import numpy as np
import pandas as pd
from scipy import stats


def check_normality(x, label=None):
    """
    Runs a Shapiro-Wilk test (n <= 50) or D'Agostino-Pearson K² test (n > 50).

    Args:
        x (list or array): numeric values
        label (str, optional): group label for display purposes

    Returns:
        dict: test_used, statistic, p_value, is_normal, interpretation
    """
    x = np.array(x, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)

    if n < 3:
        return {
            "label": label,
            "test_used": "none",
            "statistic": None,
            "p_value": None,
            "is_normal": None,
            "interpretation": "Too few observations to test normality (n < 3).",
        }

    if n <= 50:
        stat, p = stats.shapiro(x)
        test_used = "Shapiro-Wilk"
    else:
        stat, p = stats.normaltest(x)
        test_used = "D'Agostino-Pearson K²"

    return {
        "label": label,
        "test_used": test_used,
        "statistic": round(float(stat), 4),
        "p_value": round(float(p), 4),
        "is_normal": p > 0.05,
        "interpretation": (
            f"Data appears normally distributed ({test_used}, p = {p:.4f})."
            if p > 0.05
            else f"Data does not appear normally distributed ({test_used}, p = {p:.4f})."
        ),
    }


def check_equal_variance(*groups, labels=None):
    """
    Runs Levene's test to check for equal variances across groups.

    Args:
        *groups: two or more lists of numeric values
        labels (list, optional): group labels for display

    Returns:
        dict: statistic, p_value, equal_variance, interpretation
    """
    cleaned = [np.array(g, dtype=float) for g in groups]
    cleaned = [g[~np.isnan(g)] for g in cleaned]

    if any(len(g) < 2 for g in cleaned):
        return {
            "statistic": None,
            "p_value": None,
            "equal_variance": None,
            "interpretation": "Each group must have at least 2 observations for Levene's test.",
        }

    stat, p = stats.levene(*cleaned)

    return {
        "statistic": round(float(stat), 4),
        "p_value": round(float(p), 4),
        "equal_variance": p > 0.05,
        "interpretation": (
            f"Groups have equal variances — Levene's test not significant (p = {p:.4f})."
            if p > 0.05
            else f"Groups do not have equal variances — Levene's test significant (p = {p:.4f}). Consider Welch's correction."
        ),
    }


def check_sphericity(data):
    """
    Approximates sphericity check for repeated measures using Mauchly's concept.
    In practice, runs pairwise Levene tests across repeated columns as a proxy.

    Args:
        data (pd.DataFrame): rows = subjects, columns = time points / conditions

    Returns:
        dict: warning, recommendation, interpretation
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame with repeated measures as columns.")

    if data.shape[1] < 3:
        return {
            "warning": False,
            "recommendation": "Sphericity only relevant for 3+ time points.",
            "interpretation": "Sphericity check not applicable for fewer than 3 conditions.",
        }

    # Compute pairwise difference variances
    cols = data.columns.tolist()
    diff_vars = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            diff = data[cols[i]] - data[cols[j]]
            diff_vars.append(diff.var(ddof=1))

    var_ratio = max(diff_vars) / min(diff_vars) if min(diff_vars) > 0 else float("inf")
    violated = var_ratio > 2.0  # rough heuristic

    return {
        "warning": violated,
        "variance_ratio": round(var_ratio, 4),
        "recommendation": (
            "Apply Greenhouse-Geisser or Huynh-Feldt correction in your repeated measures ANOVA."
            if violated
            else "Sphericity assumption appears reasonable."
        ),
        "interpretation": (
            f"Pairwise difference variance ratio = {var_ratio:.2f}. "
            + ("Sphericity may be violated — use a corrected F-test." if violated
               else "No strong evidence of sphericity violation.")
        ),
    }


def check_proportional_hazards(df, duration_col, event_col, covariate_col):
    """
    Checks the proportional hazards assumption using log-log survival plot data.
    A formal Schoenfeld residual test requires a fitted Cox model (see survival.py).
    This function returns a warning and guidance for the teaching UI.

    Args:
        df (pd.DataFrame): dataframe with survival data
        duration_col (str): time column
        event_col (str): event column
        covariate_col (str): binary grouping covariate to check

    Returns:
        dict: guidance and interpretation
    """
    if covariate_col not in df.columns:
        raise ValueError(f"Column '{covariate_col}' not found in DataFrame.")

    unique_vals = df[covariate_col].dropna().unique()
    if len(unique_vals) != 2:
        return {
            "checkable": False,
            "interpretation": "Proportional hazards log-log check requires a binary covariate.",
        }

    return {
        "checkable": True,
        "covariate": covariate_col,
        "groups": list(unique_vals),
        "interpretation": (
            f"To verify proportional hazards for '{covariate_col}': plot log(-log(S(t))) vs log(t) "
            "for each group. Parallel lines indicate the assumption holds. "
            "For a formal test, use Schoenfeld residuals after fitting the Cox model."
        ),
        "recommendation": "Use plots.py KM log-log plot or run Schoenfeld residuals via lifelines.",
    }


def run_all_diagnostics(groups, labels=None, repeated_measures_df=None):
    """
    Convenience function: runs normality + equal variance checks on a list of groups.

    Args:
        groups (list of lists): each sublist is one group's data
        labels (list, optional): group labels
        repeated_measures_df (pd.DataFrame, optional): for sphericity check

    Returns:
        dict: normality results per group, variance result, optional sphericity result
    """
    if labels is None:
        labels = [f"Group {i+1}" for i in range(len(groups))]

    normality_results = [
        check_normality(g, label=labels[i]) for i, g in enumerate(groups)
    ]

    variance_result = check_equal_variance(*groups, labels=labels)

    all_normal = all(
        r["is_normal"] for r in normality_results if r["is_normal"] is not None
    )

    result = {
        "normality": normality_results,
        "equal_variance": variance_result,
        "all_normal": all_normal,
        "recommendation": (
            "Parametric tests are appropriate."
            if all_normal and variance_result.get("equal_variance")
            else "Consider non-parametric alternatives or Welch's correction."
        ),
    }

    if repeated_measures_df is not None:
        result["sphericity"] = check_sphericity(repeated_measures_df)

    return result