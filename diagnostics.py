def check_normality(x):
    stat, p = stats.shapiro(x)
    return p > 0.05, p

def check_equal_variance(g1, g2):
    stat, p = stats.levene(g1, g2)
    return p > 0.05, p
    