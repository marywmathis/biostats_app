# tests/registry.py

REGISTRY = [
    {"name": "Two-sample t-test (Welch)", "y_type": "continuous", "x_type": "binary", "design": "independent"},
    {"name": "Paired t-test", "y_type": "continuous", "x_type": "binary", "design": "paired"},
    {"name": "ANOVA", "y_type": "continuous", "x_type": "categorical"},
    {"name": "Linear regression", "y_type": "continuous", "x_type": "continuous"},
    {"name": "2×2 Chi-square", "y_type": "binary", "x_type": "binary"},
    {"name": "Chi-square test", "y_type": "binary", "x_type": "categorical"},
    {"name": "Logistic regression", "y_type": "binary", "x_type": "continuous"},
    {"name": "Cox proportional hazards", "y_type": "time-to-event"},
]

def get_allowed_tests(meta):
    """
    Filters the registry to return only tests matching the given metadata.
    Args:
        meta (dict): keys are design, y_type, x_type, and optionally groups_k
    Returns:
        list: matching test dictionaries
    """
    allowed = []
    for test in REGISTRY:
        if test["y_type"] != meta.get("y_type"):
            continue
        if "x_type" in test and test["x_type"] != meta.get("x_type"):
            continue
        if "design" in test and test["design"] != meta.get("design"):
            continue
        allowed.append(test)
    return allowed
