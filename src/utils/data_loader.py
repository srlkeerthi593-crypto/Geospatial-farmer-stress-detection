# =========================================================
# src/utils/data_loader.py
# Handles synthetic dataset generation and file-based loading.
# =========================================================

import os
import random

import numpy as np
import pandas as pd
import streamlit as st

from src.utils.constants import DISTRICT_COORDS, CROPS, DISTRICT_PROFILES


@st.cache_data
def generate_dataset() -> pd.DataFrame:
    """
    Generate 750 synthetic farm records for Karnataka.

    Each record represents one farm observation with 5 normalised
    parameters (0.0–1.0). Gaussian noise (std=0.12) is added around
    district baselines. Crop-specific adjustments reflect real
    agronomic knowledge.

    Returns
    -------
    pd.DataFrame with columns: Region, Crop, Rainfall, Price,
    Cost, Yield, Irrigation.
    """
    random.seed(42)
    np.random.seed(42)

    districts = list(DISTRICT_COORDS.keys())
    records = []
    samples_per_district = 750 // len(districts)
    extra = 750 - samples_per_district * len(districts)

    for i, district in enumerate(districts):
        p = DISTRICT_PROFILES[district]
        n = samples_per_district + (1 if i < extra else 0)

        for _ in range(n):
            crop  = random.choice(CROPS)
            noise = 0.12

            rain  = float(np.clip(np.random.normal(p["rain"],   noise), 0.05, 0.98))
            price = float(np.clip(np.random.normal(p["price"],  noise), 0.05, 0.98))
            yld   = float(np.clip(np.random.normal(p["yield_"], noise), 0.05, 0.98))
            cost  = float(np.clip(np.random.normal(p["cost"],   noise), 0.05, 0.98))
            irrig = float(np.clip(np.random.normal(p["irrig"],  noise), 0.05, 0.98))

            # Crop-specific adjustments
            if crop in ["Coffee", "Coconut", "Areca Nut"]:
                rain  = min(rain + 0.10, 0.98)
                irrig = min(irrig + 0.08, 0.98)
            elif crop in ["Ragi", "Jowar"]:
                rain = max(rain - 0.05, 0.05)
                cost = max(cost - 0.05, 0.05)
            elif crop == "Cotton":
                cost  = min(cost + 0.08, 0.98)
                price = min(price + 0.05, 0.98)

            records.append({
                "Region":     district,
                "Crop":       crop,
                "Rainfall":   round(rain,  4),
                "Price":      round(price, 4),
                "Cost":       round(cost,  4),
                "Yield":      round(yld,   4),
                "Irrigation": round(irrig, 4),
            })

    return pd.DataFrame(records)


def load_dataset(uploaded_file=None) -> pd.DataFrame:
    """
    Load dataset from uploaded file, local Excel, or generate synthetic data.

    Priority:
      1. Streamlit uploaded file (xlsx / csv)
      2. Local file 'data/karnataka_dataset_750_samples.xlsx'
      3. Synthetic generated dataset

    Parameters
    ----------
    uploaded_file : streamlit UploadedFile or None

    Returns
    -------
    pd.DataFrame
    """
    if uploaded_file is not None:
        if uploaded_file.name.endswith("xlsx"):
            return pd.read_excel(uploaded_file)
        else:
            return pd.read_csv(uploaded_file)

    local_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "data",
        "karnataka_dataset_750_samples.xlsx"
    )
    if os.path.exists(local_path):
        return _load_local_excel(local_path)

    return generate_dataset()


@st.cache_data
def _load_local_excel(path: str) -> pd.DataFrame:
    return pd.read_excel(path)
