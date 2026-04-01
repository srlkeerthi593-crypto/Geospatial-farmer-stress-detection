# =========================================================
# src/logic/fsi.py
# Farm Stress Index (FSI) computation, stress classification,
# district aggregation, and coordinate attachment.
# =========================================================

import pandas as pd

from src.utils.constants import (
    DISTRICT_COORDS,
    FSI_WEIGHTS,
    STRESS_LOW_PERCENTILE,
    STRESS_HIGH_PERCENTILE,
)


def compute_fsi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the Farm Stress Index (FSI) for each row.

    FSI is a weighted composite score in the range [0, 1]:
      0 = No stress (ideal farm conditions)
      1 = Maximum stress (complete crop failure scenario)

    Formula:
      FSI = (1 - Rainfall)  × 0.25   ← drought risk
          + (1 - Price)     × 0.25   ← market risk
          + (1 - Yield)     × 0.20   ← production risk
          + Cost            × 0.20   ← input burden
          + (1 - Irrigation)× 0.10   ← water access risk

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns: Rainfall, Price, Yield, Cost, Irrigation.

    Returns
    -------
    pd.DataFrame with added 'FSI' column.
    """
    w = FSI_WEIGHTS
    df = df.copy()
    df["FSI"] = (
        (1 - df["Rainfall"])   * w["rainfall"] +
        (1 - df["Price"])      * w["price"] +
        (1 - df["Yield"])      * w["yield"] +
        df["Cost"]             * w["cost"] +
        (1 - df["Irrigation"]) * w["irrigation"]
    )
    return df


def add_stress_labels(df: pd.DataFrame):
    """
    Classify each row as HIGH / MEDIUM / LOW stress using
    data-driven percentile thresholds (v4 fix).

    Previous versions used forced equal splits (10-10-10 districts)
    which were statistically biased. This version uses the 33rd and
    66th percentiles of the actual FSI distribution, producing
    unequal, genuinely data-driven class sizes.

    Parameters
    ----------
    df : pd.DataFrame with 'FSI' column.

    Returns
    -------
    tuple : (DataFrame with 'Stress' column, low_thresh, high_thresh)
    """
    low_thresh  = df["FSI"].quantile(STRESS_LOW_PERCENTILE)
    high_thresh = df["FSI"].quantile(STRESS_HIGH_PERCENTILE)

    def classify(x):
        if x >= high_thresh:  return "HIGH"
        elif x >= low_thresh: return "MEDIUM"
        else:                 return "LOW"

    df = df.copy()
    df["Stress"] = df["FSI"].apply(classify)
    return df, low_thresh, high_thresh


def get_reason(row: pd.Series) -> str:
    """
    Generate a human-readable explanation for a district's stress level
    based on which parameters are outside healthy thresholds.
    """
    reasons = []
    if row["Rainfall"]   < 0.4: reasons.append("Low Rainfall")
    if row["Yield"]      < 0.4: reasons.append("Low Yield")
    if row["Price"]      < 0.4: reasons.append("Low Price")
    if row["Cost"]       > 0.6: reasons.append("High Cost")
    if row["Irrigation"] < 0.4: reasons.append("Poor Irrigation")
    return ", ".join(reasons) if reasons else "Balanced"


def add_coords(df: pd.DataFrame) -> pd.DataFrame:
    """Attach latitude and longitude to each district row."""
    df = df.copy()
    df["lat"] = df["Region"].map(
        lambda r: DISTRICT_COORDS.get(r, (14.5, 76.5))[0]
    )
    df["lon"] = df["Region"].map(
        lambda r: DISTRICT_COORDS.get(r, (14.5, 76.5))[1]
    )
    return df


def aggregate(df: pd.DataFrame):
    """
    Aggregate raw farm records to one row per district.

    Steps:
      1. Group by Region, compute mean of all numeric features.
      2. Compute FSI on district-level means.
      3. Apply stress labels.
      4. Attach human-readable stress reasons.
      5. Attach lat/lon coordinates.

    Parameters
    ----------
    df : pd.DataFrame — raw farm records with FSI already computed.

    Returns
    -------
    tuple : (aggregated DataFrame, low_threshold, high_threshold)
    """
    agg = df.groupby("Region", as_index=False).agg(
        Rainfall   = ("Rainfall",   "mean"),
        Price      = ("Price",      "mean"),
        Yield      = ("Yield",      "mean"),
        Cost       = ("Cost",       "mean"),
        Irrigation = ("Irrigation", "mean"),
        Samples    = ("Rainfall",   "count"),
    )
    agg = compute_fsi(agg)
    agg, p_low, p_high = add_stress_labels(agg)
    agg["Reason"] = agg.apply(get_reason, axis=1)
    agg = add_coords(agg)
    return agg, p_low, p_high


def compute_game_fsi(rain: int, price: int, yld: int, cost: int, irrig: int) -> float:
    """
    Compute FSI from integer slider values (0–100 scale → normalised 0–1).

    Used exclusively by the Farmer Simulator game tab.
    """
    r, p, y, c, i = rain / 100, price / 100, yld / 100, cost / 100, irrig / 100
    w = FSI_WEIGHTS
    return (1 - r) * w["rainfall"] + (1 - p) * w["price"] + \
           (1 - y) * w["yield"]    + c * w["cost"] + \
           (1 - i) * w["irrigation"]
