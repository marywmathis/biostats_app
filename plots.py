# plots.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from lifelines import KaplanMeierFitter


# ── Shared style ──────────────────────────────────────────────────────────────
PALETTE = ["#2ecc71", "#3498db", "#e74c3c", "#f39c12", "#9b59b6", "#1abc9c"]

def _apply_style(ax, title, xlabel, ylabel):
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=9)


# ── 1. Residual plot (linear regression) ─────────────────────────────────────
def plot_residuals(x, y, slope, intercept):
    """
    Residual plot for linear regression.

    Args:
        x (array-like): predictor values
        y (array-like): observed outcome values
        slope (float): regression slope
        intercept (float): regression intercept

    Returns:
        matplotlib.figure.Figure
    """
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    y_pred = intercept + slope * x
    residuals = y - y_pred

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(x, residuals, color=PALETTE[0], alpha=0.7, edgecolors="white", s=60)
    ax.axhline(0, linestyle="--", color="#888", linewidth=1)
    _apply_style(ax, "Residual Plot", "Fitted Values", "Residuals")
    fig.tight_layout()
    return fig


# ── 2. Scatter plot with regression line ─────────────────────────────────────
def plot_regression(x, y, slope, intercept, xlabel="X", ylabel="Y"):
    """
    Scatter plot with overlaid regression line.

    Args:
        x, y (array-like): data points
        slope (float): regression slope
        intercept (float): regression intercept
        xlabel, ylabel (str): axis labels

    Returns:
        matplotlib.figure.Figure
    """
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    x_line = np.linspace(x.min(), x.max(), 200)
    y_line = intercept + slope * x_line

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(x, y, color=PALETTE[1], alpha=0.7, edgecolors="white", s=60, label="Observed")
    ax.plot(x_line, y_line, color=PALETTE[2], linewidth=2, label=f"ŷ = {intercept:.2f} + {slope:.2f}x")
    ax.legend(fontsize=9)
    _apply_style(ax, "Linear Regression", xlabel, ylabel)
    fig.tight_layout()
    return fig


# ── 3. Kaplan-Meier survival curve ───────────────────────────────────────────
def plot_kaplan_meier(durations, event_observed, groups=None, group_labels=None):
    """
    Plots Kaplan-Meier survival curve(s).

    Args:
        durations (list): time to event or censoring
        event_observed (list): 1=event, 0=censored
        groups (list, optional): group label per observation
        group_labels (list, optional): display names for groups

    Returns:
        matplotlib.figure.Figure
    """
    kmf = KaplanMeierFitter()
    fig, ax = plt.subplots(figsize=(8, 5))

    durations = np.array(durations)
    event_observed = np.array(event_observed)

    if groups is None:
        kmf.fit(durations, event_observed=event_observed, label="All subjects")
        kmf.plot_survival_function(ax=ax, color=PALETTE[0], ci_show=True)
    else:
        groups = np.array(groups)
        unique_groups = np.unique(groups)
        for i, g in enumerate(unique_groups):
            mask = groups == g
            label = group_labels[i] if group_labels and i < len(group_labels) else str(g)
            kmf.fit(durations[mask], event_observed=event_observed[mask], label=label)
            kmf.plot_survival_function(ax=ax, color=PALETTE[i % len(PALETTE)], ci_show=True)

    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    _apply_style(ax, "Kaplan-Meier Survival Curve", "Time", "Survival Probability")
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig


# ── 4. KM log-log plot (proportional hazards check) ──────────────────────────
def plot_km_loglog(durations, event_observed, groups, group_labels=None):
    """
    Log(-log(S(t))) vs log(t) plot to visually check proportional hazards assumption.
    Parallel lines = assumption holds.

    Returns:
        matplotlib.figure.Figure
    """
    kmf = KaplanMeierFitter()
    fig, ax = plt.subplots(figsize=(8, 5))

    durations = np.array(durations)
    event_observed = np.array(event_observed)
    groups = np.array(groups)

    for i, g in enumerate(np.unique(groups)):
        mask = groups == g
        label = group_labels[i] if group_labels and i < len(group_labels) else str(g)
        kmf.fit(durations[mask], event_observed=event_observed[mask])
        sf = kmf.survival_function_["KM_estimate"]
        sf = sf[sf > 0]
        t = sf.index
        log_log = np.log(-np.log(sf.values))
        ax.plot(np.log(t), log_log, color=PALETTE[i % len(PALETTE)], label=label, linewidth=2)

    _apply_style(ax, "Log-Log Plot (Proportional Hazards Check)", "log(t)", "log(-log(S(t)))")
    ax.legend(fontsize=9)
    ax.axhline(0, linestyle="--", color="#ccc", linewidth=1)
    fig.tight_layout()
    return fig


# ── 5. Box plot (group comparisons) ──────────────────────────────────────────
def plot_boxplot(groups, labels=None, title="Group Comparison", ylabel="Value"):
    """
    Box plot comparing distributions across groups.

    Args:
        groups (list of lists): one list per group
        labels (list): group labels
        title, ylabel (str): chart labels

    Returns:
        matplotlib.figure.Figure
    """
    if labels is None:
        labels = [f"Group {i+1}" for i in range(len(groups))]

    fig, ax = plt.subplots(figsize=(7, 4))
    bp = ax.boxplot(groups, patch_artist=True, notch=False, vert=True,
                    medianprops=dict(color="white", linewidth=2))

    for patch, color in zip(bp["boxes"], PALETTE):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)

    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels)
    _apply_style(ax, title, "Group", ylabel)
    fig.tight_layout()
    return fig


# ── 6. Bar chart (categorical frequencies / proportions) ─────────────────────
def plot_bar(categories, values, title="Frequencies", xlabel="Category", ylabel="Count"):
    """
    Bar chart for categorical data.

    Args:
        categories (list): category labels
        values (list): heights of bars
        title, xlabel, ylabel (str): chart labels

    Returns:
        matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(categories, values,
                  color=PALETTE[:len(categories)], edgecolor="white", linewidth=0.8)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(values) * 0.01,
                str(val), ha="center", va="bottom", fontsize=9)

    _apply_style(ax, title, xlabel, ylabel)
    fig.tight_layout()
    return fig


# ── 7. Histogram with normality overlay ──────────────────────────────────────
def plot_histogram(x, label="Values", bins=20):
    """
    Histogram with optional normal distribution overlay.

    Args:
        x (array-like): numeric data
        label (str): variable name
        bins (int): number of histogram bins

    Returns:
        matplotlib.figure.Figure
    """
    x = np.array(x, dtype=float)
    x = x[~np.isnan(x)]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(x, bins=bins, color=PALETTE[1], edgecolor="white",
            alpha=0.8, density=True, label="Observed")

    # Normal overlay
    mu, sigma = x.mean(), x.std()
    x_norm = np.linspace(x.min(), x.max(), 200)
    ax.plot(x_norm, (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_norm - mu) / sigma) ** 2),
            color=PALETTE[2], linewidth=2, label=f"Normal (μ={mu:.2f}, σ={sigma:.2f})")

    ax.legend(fontsize=9)
    _apply_style(ax, f"Distribution of {label}", label, "Density")
    fig.tight_layout()
    return fig


# ── 8. Forest plot (Cox / logistic hazard or odds ratios) ────────────────────
def plot_forest(labels, estimates, ci_lower, ci_upper, title="Forest Plot", xlabel="Hazard / Odds Ratio"):
    """
    Forest plot for hazard ratios or odds ratios with confidence intervals.

    Args:
        labels (list): covariate names
        estimates (list): point estimates (HR or OR)
        ci_lower, ci_upper (list): 95% CI bounds
        title, xlabel (str): chart labels

    Returns:
        matplotlib.figure.Figure
    """
    n = len(labels)
    y_pos = np.arange(n)

    fig, ax = plt.subplots(figsize=(8, max(4, n * 0.6)))
    ax.scatter(estimates, y_pos, color=PALETTE[0], s=80, zorder=3)

    for i in range(n):
        ax.plot([ci_lower[i], ci_upper[i]], [y_pos[i], y_pos[i]],
                color=PALETTE[0], linewidth=2, alpha=0.7)

    ax.axvline(1.0, linestyle="--", color="#888", linewidth=1, label="No effect (1.0)")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.legend(fontsize=9)
    _apply_style(ax, title, xlabel, "")
    fig.tight_layout()
    return fig


# ── 9. Q-Q plot (normality check) ────────────────────────────────────────────
def plot_qq(x, label="Values"):
    """
    Q-Q plot to visually assess normality.

    Args:
        x (array-like): numeric data
        label (str): variable name

    Returns:
        matplotlib.figure.Figure
    """
    from scipy import stats as scipy_stats

    x = np.array(x, dtype=float)
    x = x[~np.isnan(x)]

    fig, ax = plt.subplots(figsize=(6, 5))
    (osm, osr), (slope, intercept, r) = scipy_stats.probplot(x, dist="norm")
    ax.scatter(osm, osr, color=PALETTE[1], alpha=0.7, edgecolors="white", s=50)
    ax.plot(osm, slope * np.array(osm) + intercept, color=PALETTE[2], linewidth=2, label=f"R² = {r**2:.3f}")
    ax.legend(fontsize=9)
    _apply_style(ax, f"Q-Q Plot: {label}", "Theoretical Quantiles", "Sample Quantiles")
    fig.tight_layout()
    return fig