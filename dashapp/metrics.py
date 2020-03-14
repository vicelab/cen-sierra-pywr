import numpy as np
from scipy import stats


def root_mean_square_error(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())


def nash_sutcliffe_efficiency(predictions, targets):
    if not predictions.any() or not targets.any():
        return -1
    slope, intercept, r_value, p_value, std_err = stats.linregress(predictions, targets)
    return r_value ** 2


def percent_bias(predictions, targets):
    return predictions.mean() / targets.mean() - 1
