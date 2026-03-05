def when_anova(meta):
    return (
        meta["design"] == "independent"
        and meta["y_type"] == "continuous"
        and meta["x_type"] == "categorical"
        and meta["groups_k"] >= 3
    )

def validate_anova(payload):
    groups = payload.get("groups")

    if not groups or len(groups) < 3:
        return False, "Need at least 3 groups."

    if any(len(g) < 2 for g in groups):
        return False, "Each group must have ≥2 observations."

    return True, ""

def run_anova(payload):
    groups = payload["groups"]
    F, p = stats.f_oneway(*groups)

    return {"F": F, "p": p}
    def run_kruskal(payload):
    groups = payload["groups"]
    H, p = stats.kruskal(*groups)
    return {"H": H, "p": p}
    def run_mcnemar(payload):
    table = payload["table"]  # [[a,b],[c,d]]

    b = table[0,1]
    c = table[1,0]

    chi2 = (abs(b - c) - 1)**2 / (b + c) if (b + c) > 0 else 0
    p = 1 - stats.chi2.cdf(chi2, 1)

    return {"chi2": chi2, "p": p}
    import statsmodels.api as sm

def run_poisson(payload):
    y = payload["y"]
    X = sm.add_constant(payload["x"])

    model = sm.GLM(y, X, family=sm.families.Poisson())
    results = model.fit()

    return {
        "coef": results.params.tolist(),
        "pvalues": results.pvalues.tolist(),
        "summary": str(results.summary())
    }
    