# tests/survival.py

import numpy as np
from lifelines import KaplanMeierFitter, CoxPHFitter
import pandas as pd

def run_kaplan_meier(durations, event_observed, groups=None):
    """
    Runs a Kaplan-Meier survival analysis.
    Args:
        durations (list): time to event or censoring e.g. [5, 10, 15, 20]
        event_observed (list): 1 if event occurred, 0 if censored e.g. [1, 0, 1, 1]
        groups (list, optional): group labels for each observation e.g. ['A', 'A', 'B', 'B']
    Returns:
        dict: containing median_survival_time and interpretation
    """
    kmf = KaplanMeierFitter()
    kmf.fit(durations=durations, event_observed=event_observed)

    median_survival = kmf.median_survival_time_

    return {
        "median_survival_time": median_survival,
        "interpretation": f"50% of subjects experienced the event by time {median_survival}."
    }

def run_cox_regression(df, duration_col, event_col):
    """
    Runs a Cox proportional hazards regression.
    Args:
        df (pd.DataFrame): dataframe containing duration, event, and covariate columns
        duration_col (str): name of the column with time-to-event data
        event_col (str): name of the column with event occurrence (1=event, 0=censored)
    Returns:
        dict: containing hazard_ratios, p_values, and interpretation
    """
    cph = CoxPHFitter()
    cph.fit(df, duration_col=duration_col, event_col=event_col)

    summary = cph.summary[["exp(coef)", "p"]].round(4)
    summary.columns = ["hazard_ratio", "p_value"]

    significant = summary[summary["p_value"] < 0.05]

    if len(significant) > 0:
        interpretation = f"{len(significant)} covariate(s) significantly associated with survival (p < 0.05)."
    else:
        interpretation = "No covariates significantly associated with survival (p ≥ 0.05)."

    return {
        "hazard_ratios": summary.to_dict(),
        "interpretation": interpretation
    }