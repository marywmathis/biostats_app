# tests/survival.py

import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test, multivariate_logrank_test


def run_kaplan_meier(durations, event_observed, groups=None):
    """
    Runs a Kaplan-Meier survival analysis.

    Args:
        durations (list): time to event or censoring e.g. [5, 10, 15, 20]
        event_observed (list): 1 if event occurred, 0 if censored e.g. [1, 0, 1, 1]
        groups (list, optional): group labels for each observation e.g. ['A', 'A', 'B', 'B']

    Returns:
        dict: median_survival_time, timeline, survival_probabilities,
              interpretation, and optionally logrank test results
    """
    kmf = KaplanMeierFitter()

    # ── Single-group KM ───────────────────────────────────────────────────────
    if groups is None:
        kmf.fit(durations=durations, event_observed=event_observed)
        median_survival = kmf.median_survival_time_
        sf = kmf.survival_function_

        return {
            "median_survival_time": median_survival,
            "timeline": sf.index.tolist(),
            "survival_probabilities": sf["KM_estimate"].tolist(),
            "interpretation": (
                f"50% of subjects experienced the event by time {median_survival}."
                if not np.isinf(median_survival)
                else "Median survival time not reached — over 50% of subjects remain event-free."
            ),
            "logrank": None,
        }

    # ── Multi-group KM with log-rank test ─────────────────────────────────────
    durations = np.array(durations)
    event_observed = np.array(event_observed)
    groups = np.array(groups)
    unique_groups = np.unique(groups)

    group_results = {}
    for g in unique_groups:
        mask = groups == g
        kmf.fit(
            durations=durations[mask],
            event_observed=event_observed[mask],
            label=str(g),
        )
        sf = kmf.survival_function_
        median_val = kmf.median_survival_time_
        group_results[str(g)] = {
            "median_survival_time": median_val,
            "timeline": sf.index.tolist(),
            "survival_probabilities": sf[str(g)].tolist(),
        }

    # Log-rank test (2 groups: standard; 3+: multivariate)
    if len(unique_groups) == 2:
        g0, g1 = unique_groups
        lr = logrank_test(
            durations_A=durations[groups == g0],
            durations_B=durations[groups == g1],
            event_observed_A=event_observed[groups == g0],
            event_observed_B=event_observed[groups == g1],
        )
        logrank_result = {
            "test": "log-rank",
            "p_value": round(lr.p_value, 4),
            "test_statistic": round(lr.test_statistic, 4),
            "interpretation": (
                f"Survival curves differ significantly between groups (p = {lr.p_value:.4f})."
                if lr.p_value < 0.05
                else f"No significant difference in survival between groups (p = {lr.p_value:.4f})."
            ),
        }
    else:
        lr = multivariate_logrank_test(durations, groups, event_observed)
        logrank_result = {
            "test": "multivariate log-rank",
            "p_value": round(lr.p_value, 4),
            "test_statistic": round(lr.test_statistic, 4),
            "interpretation": (
                f"At least one group's survival curve differs significantly (p = {lr.p_value:.4f})."
                if lr.p_value < 0.05
                else f"No significant difference in survival across groups (p = {lr.p_value:.4f})."
            ),
        }

    return {
        "groups": group_results,
        "logrank": logrank_result,
        "interpretation": logrank_result["interpretation"],
    }


def run_cox_regression(df, duration_col, event_col):
    """
    Runs a Cox proportional hazards regression.

    Args:
        df (pd.DataFrame): dataframe with duration, event, and covariate columns
        duration_col (str): column name for time-to-event data
        event_col (str): column name for event indicator (1=event, 0=censored)

    Returns:
        dict: hazard_ratios, confidence_intervals, p_values, concordance, interpretation
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")
    if duration_col not in df.columns:
        raise ValueError(f"duration_col '{duration_col}' not found in DataFrame.")
    if event_col not in df.columns:
        raise ValueError(f"event_col '{event_col}' not found in DataFrame.")
    if df[duration_col].isnull().any() or df[event_col].isnull().any():
        raise ValueError("duration_col and event_col must not contain missing values.")

    cph = CoxPHFitter()
    cph.fit(df, duration_col=duration_col, event_col=event_col)

    summary = cph.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%", "p"]].round(4)
    summary.columns = ["hazard_ratio", "ci_lower_95", "ci_upper_95", "p_value"]

    significant = summary[summary["p_value"] < 0.05]

    if len(significant) > 0:
        sig_vars = ", ".join(significant.index.tolist())
        interpretation = (
            f"{len(significant)} covariate(s) significantly associated with survival "
            f"(p < 0.05): {sig_vars}."
        )
    else:
        interpretation = "No covariates significantly associated with survival (p ≥ 0.05)."

    return {
        "hazard_ratios": summary["hazard_ratio"].to_dict(),
        "ci_lower_95": summary["ci_lower_95"].to_dict(),
        "ci_upper_95": summary["ci_upper_95"].to_dict(),
        "p_values": summary["p_value"].to_dict(),
        "concordance_index": round(cph.concordance_index_, 4),
        "summary_df": summary,
        "interpretation": interpretation,
    }
    