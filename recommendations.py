def recommend_test(meta):
    """
    Recommends a statistical test based on study design metadata.
    Args:
        meta (dict): keys are design, y_type, x_type, and optionally groups_k
    Returns:
        str: name of recommended test
    """
    if meta["y_type"] == "continuous" and meta["x_type"] == "binary":
        if meta["design"] == "paired":
            return "Paired t-test"
        return "Two-sample t-test (Welch)"

    if meta["y_type"] == "continuous" and meta.get("groups_k", 0) >= 3:
        return "ANOVA"

    if meta["y_type"] == "continuous" and meta.get("groups_k", 0) == 2:
        return "Two-sample t-test (Welch)"

    if meta["y_type"] == "binary" and meta["x_type"] == "binary":
        return "2×2 Chi-square"

    if meta["y_type"] == "continuous" and meta["x_type"] == "continuous":
        return "Linear regression"

    if meta["y_type"] == "binary" and meta["x_type"] == "continuous":
        return "Logistic regression"

    if meta["y_type"] == "time-to-event":
        return "Cox proportional hazards"

    if meta["y_type"] == "binary" and meta["x_type"] == "categorical":
        return "Chi-square test"

    return "Manual selection recommended"
    