"""
recommendations.py
Recommends statistical tests and provides teaching content for each.
"""

TEST_CONTENT = {
    "Paired t-test": {
        "description": "Compares means of two related groups (e.g., before/after measurements on the same subjects).",
        "assumptions": [
            "Differences between pairs are approximately normally distributed",
            "Observations are paired (matched or repeated measures)",
            "Continuous outcome variable",
        ],
        "when_to_use": "Use when the same subjects are measured twice, or subjects are matched by a relevant characteristic.",
        "effect_size": "Cohen's d (paired)",
        "common_mistake": "Using an independent t-test when data is actually paired — this loses statistical power.",
        "epi_example": "Comparing blood pressure before and after a hypertension intervention in the same patients.",
    },
    "Two-sample t-test (Welch)": {
        "description": "Compares means of two independent groups without assuming equal variances.",
        "assumptions": [
            "Outcome is approximately normally distributed within each group (or n > 30 per group)",
            "Observations are independent between groups",
            "Continuous outcome variable",
        ],
        "when_to_use": "Use when comparing a continuous outcome between two unrelated groups.",
        "effect_size": "Cohen's d",
        "common_mistake": "Using Student's t-test (equal variance assumed) by default — Welch's is safer and preferred.",
        "epi_example": "Comparing mean BMI between exposed and unexposed workers in an occupational cohort.",
    },
    "Mann-Whitney U test": {
        "description": "Non-parametric alternative to the two-sample t-test based on rank ordering.",
        "assumptions": [
            "Ordinal or continuous outcome",
            "Independent groups",
            "No assumption of normality",
        ],
        "when_to_use": "Use when normality is violated and sample size is small, or outcome is ordinal.",
        "effect_size": "Rank-biserial correlation",
        "common_mistake": "Interpreting as comparing medians — it technically compares rank distributions.",
        "epi_example": "Comparing pain scores (ordinal scale) between treatment and control groups.",
    },
    "Wilcoxon signed-rank test": {
        "description": "Non-parametric alternative to the paired t-test.",
        "assumptions": [
            "Paired or matched observations",
            "Ordinal or continuous outcome",
            "Symmetric distribution of differences (less strict than normality)",
        ],
        "when_to_use": "Use instead of paired t-test when differences are not normally distributed.",
        "effect_size": "Rank-biserial correlation",
        "common_mistake": "Forgetting to check symmetry of differences — the test is not assumption-free.",
        "epi_example": "Comparing self-reported stress levels before and after a workplace wellness program.",
    },
    "ANOVA": {
        "description": "Tests whether means differ across three or more independent groups.",
        "assumptions": [
            "Continuous outcome",
            "Approximately normal distribution within groups (or large n)",
            "Homogeneity of variances (Levene's test)",
            "Independent observations",
        ],
        "when_to_use": "Use when comparing a continuous outcome across 3+ groups simultaneously to avoid inflating Type I error.",
        "effect_size": "Eta-squared (η²) or omega-squared",
        "common_mistake": "Running multiple t-tests instead — this inflates the false positive rate. Always use ANOVA first, then post-hoc tests.",
        "epi_example": "Comparing mean cholesterol across four dietary intervention groups.",
    },
    "Kruskal-Wallis test": {
        "description": "Non-parametric alternative to one-way ANOVA using ranks.",
        "assumptions": [
            "Ordinal or continuous outcome",
            "3+ independent groups",
            "No normality required",
        ],
        "when_to_use": "Use when ANOVA assumptions (normality or equal variance) are violated.",
        "effect_size": "Eta-squared based on H statistic",
        "common_mistake": "Not following up with post-hoc tests (e.g., Dunn's test) after a significant result.",
        "epi_example": "Comparing physical activity levels across three socioeconomic groups.",
    },
    "Repeated measures ANOVA": {
        "description": "Tests differences across 3+ time points or conditions within the same subjects.",
        "assumptions": [
            "Continuous outcome",
            "Sphericity (Mauchly's test) — use Greenhouse-Geisser correction if violated",
            "Normally distributed residuals",
        ],
        "when_to_use": "Use when the same subjects are measured at 3+ time points.",
        "effect_size": "Partial eta-squared",
        "common_mistake": "Ignoring sphericity — always report the corrected p-value if Mauchly's test is significant.",
        "epi_example": "Tracking mean blood glucose at baseline, 3 months, and 6 months in a diabetes trial.",
    },
    "2×2 Chi-square": {
        "description": "Tests association between two binary variables using observed vs. expected cell counts.",
        "assumptions": [
            "Expected cell count ≥ 5 in all cells (use Fisher's exact if not met)",
            "Observations are independent",
            "Binary exposure and outcome",
        ],
        "when_to_use": "Use to test whether two binary variables are statistically associated.",
        "effect_size": "Odds Ratio (OR), Risk Ratio (RR), or Phi coefficient",
        "common_mistake": "Using chi-square when expected counts < 5 — switch to Fisher's exact test.",
        "epi_example": "Testing association between smoking (yes/no) and lung cancer (yes/no) in a case-control study.",
    },
    "Fisher's exact test": {
        "description": "Exact test for association in 2×2 tables with small expected cell counts.",
        "assumptions": [
            "Fixed row and column marginals",
            "Independent observations",
            "Small sample or sparse cells",
        ],
        "when_to_use": "Use instead of chi-square when any expected cell count < 5.",
        "effect_size": "Odds Ratio",
        "common_mistake": "Only applying when n is very small — Fisher's is valid at any sample size when cells are sparse.",
        "epi_example": "Testing a rare exposure-disease association in a small case-control study.",
    },
    "Chi-square test": {
        "description": "Tests association between a categorical exposure and a binary outcome across multiple groups.",
        "assumptions": [
            "Expected cell count ≥ 5 in most cells",
            "Independent observations",
        ],
        "when_to_use": "Use when exposure has 3+ unordered categories and outcome is binary.",
        "effect_size": "Cramér's V",
        "common_mistake": "Not checking expected cell counts — use Fisher's or collapse categories if cells are too sparse.",
        "epi_example": "Testing whether disease prevalence differs across racial/ethnic groups.",
    },
    "McNemar's test": {
        "description": "Tests change in a binary outcome for paired/matched data.",
        "assumptions": [
            "Binary outcome",
            "Paired or matched design",
            "Focus is on discordant pairs",
        ],
        "when_to_use": "Use when comparing binary outcomes before/after in the same subjects, or in matched case-control studies.",
        "effect_size": "Odds Ratio from discordant pairs",
        "common_mistake": "Using a regular chi-square on paired data — this violates independence and is incorrect.",
        "epi_example": "Comparing seropositive status before and after vaccination in the same cohort.",
    },
    "Linear regression": {
        "description": "Models the linear relationship between a continuous outcome and one or more predictors.",
        "assumptions": [
            "Linearity between predictors and outcome",
            "Normally distributed residuals",
            "Homoscedasticity (constant variance of residuals)",
            "Independent observations",
            "No severe multicollinearity (for multiple predictors)",
        ],
        "when_to_use": "Use to quantify the effect of a continuous or binary exposure on a continuous outcome, while adjusting for confounders.",
        "effect_size": "β coefficient (unstandardized or standardized)",
        "common_mistake": "Not checking residual plots — violations of linearity or homoscedasticity can invalidate results.",
        "epi_example": "Estimating the effect of years of education on systolic blood pressure, adjusted for age and sex.",
    },
    "Logistic regression": {
        "description": "Models the log-odds of a binary outcome as a function of predictors.",
        "assumptions": [
            "Binary outcome",
            "Independence of observations",
            "No extreme multicollinearity",
            "Linearity of continuous predictors with the log-odds",
            "Adequate sample size (≥10 events per predictor)",
        ],
        "when_to_use": "Use to estimate odds ratios and adjust for multiple confounders with a binary outcome.",
        "effect_size": "Odds Ratio (OR) = exp(β)",
        "common_mistake": "Interpreting OR as RR when outcome prevalence > 10% — use Poisson regression for common outcomes.",
        "epi_example": "Estimating the odds of hypertension associated with obesity, adjusted for age, sex, and diet.",
    },
    "Cox proportional hazards": {
        "description": "Models the hazard of an event over time as a function of covariates.",
        "assumptions": [
            "Proportional hazards assumption (log-log plot or Schoenfeld residuals)",
            "Non-informative censoring",
            "Linear relationship between continuous predictors and log-hazard",
            "Independent observations",
        ],
        "when_to_use": "Use for time-to-event outcomes where subjects may be censored (e.g., didn't experience the event by end of study).",
        "effect_size": "Hazard Ratio (HR) = exp(β)",
        "common_mistake": "Not testing the proportional hazards assumption — violation requires time-varying coefficients or stratification.",
        "epi_example": "Estimating the effect of smoking on time to cardiovascular disease in a prospective cohort study.",
    },
    "Poisson regression": {
        "description": "Models count outcomes or estimates risk ratios for common binary outcomes.",
        "assumptions": [
            "Outcome is a count or rate",
            "Mean ≈ variance (if overdispersed, use negative binomial)",
            "Independent observations",
            "Log-linear relationship",
        ],
        "when_to_use": "Use for count data (e.g., number of hospitalizations) or as an alternative to logistic regression when outcome prevalence > 10%.",
        "effect_size": "Rate Ratio or Risk Ratio = exp(β)",
        "common_mistake": "Ignoring overdispersion — always check mean vs. variance and use robust standard errors or negative binomial if needed.",
        "epi_example": "Modeling number of asthma attacks per year as a function of air pollution exposure.",
    },
    "Manual selection recommended": {
        "description": "Your combination of study design, outcome type, and exposure type didn't match a standard pattern.",
        "assumptions": [],
        "when_to_use": "Review your study design choices above — some combinations may need a specialist test or a different framing.",
        "effect_size": "Depends on the selected test",
        "common_mistake": "Forcing data into an ill-fitting test — consult a biostatistician when in doubt.",
        "epi_example": "Complex designs (multilevel data, multiple outcomes, competing risks) often require custom modeling.",
    },
}


def recommend_test(meta: dict) -> str:
    """
    Recommends a statistical test based on study design metadata.

    Args:
        meta (dict): keys — design, y_type, x_type, optionally groups_k, normal (bool)

    Returns:
        str: name of recommended test
    """
    design = meta.get("design", "independent")
    y_type = meta.get("y_type")
    x_type = meta.get("x_type")
    groups_k = meta.get("groups_k", 2)
    normal = meta.get("normal", True)  # assumed normal unless user flags otherwise

    # ── Time-to-event ────────────────────────────────────────────────────────
    if y_type == "time-to-event":
        return "Cox proportional hazards"

    # ── Continuous outcome ────────────────────────────────────────────────────
    if y_type == "continuous":
        if x_type == "binary":
            if design == "paired":
                return "Wilcoxon signed-rank test" if not normal else "Paired t-test"
            return "Mann-Whitney U test" if not normal else "Two-sample t-test (Welch)"

        if x_type == "categorical":
            k = int(groups_k)
            if design == "paired":
                return "Repeated measures ANOVA"
            return "Kruskal-Wallis test" if not normal else ("ANOVA" if k >= 3 else "Two-sample t-test (Welch)")

        if x_type == "continuous":
            return "Linear regression"

    # ── Binary outcome ────────────────────────────────────────────────────────
    if y_type == "binary":
        if x_type == "binary":
            if design == "paired":
                return "McNemar's test"
            return "2×2 Chi-square"

        if x_type == "categorical":
            return "Chi-square test"

        if x_type == "continuous":
            return "Logistic regression"

    return "Manual selection recommended"


def get_teaching_content(test_name: str) -> dict:
    """Returns teaching content dict for a given test name."""
    return TEST_CONTENT.get(test_name, TEST_CONTENT["Manual selection recommended"])
