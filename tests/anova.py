# tests/anova.py

from scipy import stats

def run_anova(groups):
    """
    Runs a one-way ANOVA test to compare means across 3 or more groups.
    Args:
        groups (list of lists): each inner list contains the values for one group
                                e.g. [[1,2,3], [4,5,6], [7,8,9]]
    Returns:
        dict: containing f_statistic, p_value, and interpretation
    """
    if len(groups) < 3:
        return {"error": "ANOVA requires at least 3 groups."}

    f_statistic, p_value = stats.f_oneway(*groups)

    if p_value < 0.05:
        interpretation = "Statistically significant difference between group means (p < 0.05)."
    else:
        interpretation = "No statistically significant difference between group means (p ≥ 0.05)."

    return {
        "f_statistic": round(f_statistic, 4),
        "p_value": round(p_value, 4),
        "interpretation": interpretation
    }