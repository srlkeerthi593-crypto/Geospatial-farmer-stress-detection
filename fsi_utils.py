import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


def compute_fsi(df: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """
    Compute Farmer Stress Index for each record.
    FSI range: 0 (no stress) to 1 (maximum stress)
    """
    scaler = MinMaxScaler()
    result = df.copy()

    result['norm_rainfall']   = 1 - scaler.fit_transform(df[['Rainfall']])
    result['norm_price']      = 1 - scaler.fit_transform(df[['Price']])
    result['norm_yield']      = 1 - scaler.fit_transform(df[['Yield']])
    result['norm_cost']       = scaler.fit_transform(df[['Cost']])
    result['norm_irrigation'] = 1 - scaler.fit_transform(df[['Irrigation']])

    result['FSI'] = (
        weights['Rainfall']   * result['norm_rainfall']   +
        weights['Price']      * result['norm_price']       +
        weights['Yield']      * result['norm_yield']       +
        weights['Cost']       * result['norm_cost']        +
        weights['Irrigation'] * result['norm_irrigation']
    ).round(4)

    result['Stress_Category'] = pd.cut(
        result['FSI'],
        bins=[0, 0.4, 0.65, 1.0],
        labels=['Low', 'Medium', 'High'],
        include_lowest=True
    )
    return result


def district_summary(df_fsi: pd.DataFrame) -> pd.DataFrame:
    """Aggregate FSI and indicators at district level."""
    grp = df_fsi.groupby('Region').agg(
        FSI=('FSI', 'mean'),
        Rainfall=('Rainfall', 'mean'),
        Price=('Price', 'mean'),
        Cost=('Cost', 'mean'),
        Yield=('Yield', 'mean'),
        Irrigation=('Irrigation', 'mean'),
        Sample_Count=('FSI', 'count')
    ).reset_index()
    grp['FSI'] = grp['FSI'].round(4)
    grp['Stress_Category'] = pd.cut(
        grp['FSI'], bins=[0, 0.4, 0.65, 1.0],
        labels=['Low', 'Medium', 'High'], include_lowest=True
    )
    return grp.sort_values('FSI', ascending=False).reset_index(drop=True)


def normalize_weights(weights: dict) -> dict:
    """Normalize weights to sum to 1.0."""
    total = sum(weights.values())
    if total == 0:
        return {k: 1/len(weights) for k in weights}
    return {k: v/total for k, v in weights.items()}


DEFAULT_WEIGHTS = {
    'Rainfall':   0.25,
    'Price':      0.25,
    'Yield':      0.20,
    'Cost':       0.20,
    'Irrigation': 0.10,
}
