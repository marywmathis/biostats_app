# validators.py

import numpy as np
import pandas as pd


def validate_numeric_list(x, name="input", min_length=2):
    """
    Validates that input is a non-empty list of finite numeric values.

    Args:
        x: input to validate
        name (str): variable name for error messages
        min_length (int): minimum number of valid observations required

    Returns:
        dict: valid (bool), cleaned (np.array or None), error (str or None)
    """
    try:
        arr = np.array(x, dtype=float)
    except (TypeError, ValueError):
        return {"valid": False, "cleaned": None,
                "error": f"'{name}' must contain numeric values only."}

    if arr.ndim != 1:
        return {"valid": False, "cleaned": None,
                "error": f"'{name}' must be a 1-dimensional list or array."}

    cleaned = arr[~np.isnan(arr) & np.isfinite(arr)]

    if len(cleaned) < min_length:
        return {"valid": False, "cleaned": None,
                "error": f"'{name}' must have at least {min_length} finite numeric values (got {len(cleaned)})."}

    return {"valid": True, "cleaned": cleaned, "error": None}


def validate_groups(*groups, names=None, min_length=2):
    """
    Validates two or more numeric groups for group-comparison tests.

    Args:
        *groups: two or more lists of numeric values
        names (list, optional): group names for error messages
        min_length (int): minimum observations per group

    Returns:
        dict: valid (bool), cleaned_groups (list or None), errors (list)
    """
    if len(groups) < 2:
        return {"valid": False, "cleaned_groups": None,
                "errors": ["At least two groups are required."]}

    if names is None:
        names = [f"Group {i+1}" for i in range(len(groups))]

    errors = []
    cleaned_groups = []

    for g, name in zip(groups, names):
        result = validate_numeric_list(g, name=name, min_length=min_length)
        if not result["valid"]:
            errors.append(result["error"])
        else:
            cleaned_groups.append(result["cleaned"])

    if errors:
        return {"valid": False, "cleaned_groups": None, "errors": errors}

    return {"valid": True, "cleaned_groups": cleaned_groups, "errors": []}


def validate_survival_inputs(durations, event_observed, groups=None):
    """
    Validates inputs for Kaplan-Meier or Cox regression.

    Args:
        durations (list): time-to-event values
        event_observed (list): 1=event, 0=censored
        groups (list, optional): group labels

    Returns:
        dict: valid (bool), errors (list)
    """
    errors = []

    dur = validate_numeric_list(durations, name="durations", min_length=2)
    if not dur["valid"]:
        errors.append(dur["error"])
    elif np.any(dur["cleaned"] < 0):
        errors.append("'durations' must not contain negative values.")

    try:
        ev = np.array(event_observed, dtype=float)
        if not np.all(np.isin(ev, [0, 1])):
            errors.append("'event_observed' must contain only 0 (censored) or 1 (event).")
    except (TypeError, ValueError):
        errors.append("'event_observed' must be a list of 0s and 1s.")
        ev = None

    if dur["valid"] and ev is not None and len(dur["cleaned"]) != len(ev):
        errors.append("'durations' and 'event_observed' must have the same length.")

    if groups is not None:
        if len(groups) != len(durations):
            errors.append("'groups' must have the same length as 'durations'.")

    if errors:
        return {"valid": False, "errors": errors}

    return {"valid": True, "errors": []}


def validate_dataframe(df, required_cols=None, min_rows=5):
    """
    Validates a pandas DataFrame for analysis.

    Args:
        df: input to check
        required_cols (list, optional): column names that must be present
        min_rows (int): minimum number of rows required

    Returns:
        dict: valid (bool), errors (list)
    """
    errors = []

    if not isinstance(df, pd.DataFrame):
        return {"valid": False, "errors": ["Input must be a pandas DataFrame."]}

    if len(df) < min_rows:
        errors.append(f"DataFrame must have at least {min_rows} rows (got {len(df)}).")

    if required_cols:
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            errors.append(f"Missing required column(s): {', '.join(missing)}.")

    if errors:
        return {"valid": False, "errors": errors}

    return {"valid": True, "errors": []}


def validate_binary_outcome(y, name="outcome"):
    """
    Validates that a variable is binary (0/1 only).

    Args:
        y (list or array): outcome variable
        name (str): variable name for error messages

    Returns:
        dict: valid (bool), error (str or None)
    """
    try:
        arr = np.array(y, dtype=float)
        unique_vals = np.unique(arr[~np.isnan(arr)])
        if not np.all(np.isin(unique_vals, [0, 1])):
            return {"valid": False,
                    "error": f"'{name}' must be binary (0/1 only). Found values: {unique_vals.tolist()}."}
        if len(arr) < 10:
            return {"valid": False,
                    "error": f"'{name}' has fewer than 10 observations — results may be unreliable."}
    except (TypeError, ValueError):
        return {"valid": False, "error": f"'{name}' must contain numeric values only."}

    return {"valid": True, "error": None}


def validate_meta(meta):
    """
    Validates the study configuration dict passed to recommend_test().

    Args:
        meta (dict): keys — design, y_type, x_type, optionally groups_k

    Returns:
        dict: valid (bool), errors (list)
    """
    errors = []

    valid_designs = {"independent", "paired"}
    valid_y_types = {"binary", "continuous", "time-to-event"}
    valid_x_types = {"binary", "categorical", "continuous"}

    if not isinstance(meta, dict):
        return {"valid": False, "errors": ["meta must be a dictionary."]}

    if meta.get("design") not in valid_designs:
        errors.append(f"'design' must be one of {valid_designs}.")

    if meta.get("y_type") not in valid_y_types:
        errors.append(f"'y_type' must be one of {valid_y_types}.")

    if meta.get("x_type") not in valid_x_types:
        errors.append(f"'x_type' must be one of {valid_x_types}.")

    if meta.get("x_type") == "categorical":
        k = meta.get("groups_k")
        if k is None:
            errors.append("'groups_k' is required when x_type is 'categorical'.")
        elif not isinstance(k, (int, float)) or int(k) < 2:
            errors.append("'groups_k' must be an integer >= 2.")

    if errors:
        return {"valid": False, "errors": errors}

    return {"valid": True, "errors": []}