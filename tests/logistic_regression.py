# tests/logistic_regression.py

import numpy as np
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

def run_logistic_regression(X, y):
    """
    Runs a logistic regression to predict a binary outcome from a continuous exposure.
    Args:
        X (list): list of continuous exposure values e.g. [1.2, 3.4, 5.6]
        y (list): list of binary outcome values e.g. [0, 1, 0, 1]
    Returns:
        dict: containing odds_ratio, p_value, confidence_interval, and interpretation
    """
    X = np.array(X).reshape(-1, 1)
    y = np.array(y)

    if len(np.unique(y)) != 2:
        return {"error": "Outcome variable must be binary (0 and 1 only)."}

    if len(X) != len(y):
        return {"error": "X and y must have the same number of observations."}

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression()
    model.fit(X_scaled, y)

    coef = model.coef_[0][0]
    odds_ratio = round(np.exp(coef), 4)

    n = len(y)
    se = 1 / np.sqrt(n)
    z = coef / se
    p_value = round(2 * (1 - stats.norm.cdf(abs(z))), 4)

    ci_lower = round(np.exp(coef - 1.96 * se), 4)
    ci_upper = round(np.exp(coef + 1.96 * se), 4)

    if p_value < 0.05:
        interpretation = f"Statistically significant association (OR={odds_ratio}, p < 0.05)."
    else:
        interpretation = f"No statistically significant association (OR={odds_ratio}, p ≥ 0.05)."

    return {
        "odds_ratio": odds_ratio,
        "p_value": p_value,
        "confidence_interval": [ci_lower, ci_upper],
        "interpretation": interpretation
    }