def recommend_test(meta):
    if meta["y_type"] == "continuous" and meta["x_type"] == "binary":
        if meta["design"] == "paired":
            return "Paired t test"
        return "Two-sample t test (Welch)"
    if meta["y_type"] == "continuous" and meta["groups_k"] >= 3:
        return "ANOVA"
    if meta["y_type"] == "binary" and meta["x_type"] == "binary":
        return "2×2 Chi-square"
    if meta["y_type"] == "continuous" and meta["x_type"] == "continuous":
        return "Linear regression"
    return "Manual selection recommended"
    