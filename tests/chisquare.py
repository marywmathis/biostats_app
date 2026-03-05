# tests/chisquare.py

from scipy import stats
import numpy as np

def run_chisquare(contingency_table):
    """
    Runs a Chi-square test of independence on a contingency table.
    Args:
        contingency_table (list of lists): 2D table of observed frequencies
                                           e.g. [[10, 20], [30, 40]]
    Returns:
        dict: containing chi2_statistic, p_value, degrees_of_freedom,
              expected frequencies, and interpretation
    """
    table = np.array(contingency_table)

    if table.shape[0] < 2 or table.shape[1] < 2:
        return {"error": "Contingency table must have at least 2 rows and 2 columns."}

    chi2, p_value, dof, expected = stats.chi2_contingency(table)

    if p_value < 0.05:
        interpretation = "Statistically significant association between variables (p < 0.05)."
    else:
        interpretation = "No statistically significant association between variables (p ≥ 0.05)."

    return {
        "chi2_statistic": round(chi2, 4),
        "p_value": round(p_value, 4),
        "degrees_of_freedom": dof,
        "expected": expected.tolist(),
        "interpretation": interpretation
    }