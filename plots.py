def plot_residuals(x, y, slope, intercept):
    y_pred = intercept + slope * x
    residuals = y - y_pred

    fig, ax = plt.subplots()
    ax.scatter(x, residuals)
    ax.axhline(0, linestyle="--")
    ax.set_title("Residual Plot")
    return fig