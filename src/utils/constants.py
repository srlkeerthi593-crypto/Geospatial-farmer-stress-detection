# =========================================================
# src/utils/constants.py
# Shared constants: district coordinates, crop list,
# and district agronomic baseline profiles.
# =========================================================

DISTRICT_COORDS = {
    "BAGALKOT":         (16.18, 75.69),
    "BALLARI":          (15.14, 76.92),
    "BELAGAVI":         (15.86, 74.50),
    "BENGALURU RURAL":  (13.16, 77.51),
    "BENGALURU URBAN":  (12.97, 77.57),
    "BIDAR":            (17.91, 76.82),
    "CHAMARAJANAGAR":   (11.94, 77.17),
    "CHIKKABALLAPUR":   (13.43, 77.73),
    "CHIKKAMAGALURU":   (13.31, 75.77),
    "CHITRADURGA":      (14.23, 76.40),
    "DAKSHINA KANNADA": (12.85, 74.88),
    "DAVANAGERE":       (14.46, 75.92),
    "DHARWAD":          (15.45, 75.01),
    "GADAG":            (15.42, 75.62),
    "HASSAN":           (13.00, 76.10),
    "HAVERI":           (14.79, 75.40),
    "KALABURAGI":       (17.33, 76.82),
    "KODAGU":           (12.41, 75.74),
    "KOLAR":            (13.13, 78.13),
    "KOPPAL":           (15.35, 76.15),
    "MANDYA":           (12.52, 76.90),
    "MYSURU":           (12.30, 76.65),
    "RAICHUR":          (16.21, 77.36),
    "RAMANAGARA":       (12.72, 77.28),
    "SHIVAMOGGA":       (13.93, 75.56),
    "TUMAKURU":         (13.34, 77.10),
    "UDUPI":            (13.34, 74.74),
    "UTTARA KANNADA":   (14.80, 74.73),
    "VIJAYAPURA":       (16.83, 75.72),
    "YADGIR":           (16.76, 77.60),
}

CROPS = [
    "Rice", "Wheat", "Maize", "Ragi", "Jowar",
    "Sugarcane", "Cotton", "Groundnut", "Sunflower", "Areca Nut",
    "Coffee", "Coconut", "Banana", "Tomato", "Onion",
]

DISTRICT_PROFILES = {
    "BAGALKOT":         dict(rain=0.38, price=0.52, yield_=0.46, cost=0.58, irrig=0.42),
    "BALLARI":          dict(rain=0.32, price=0.48, yield_=0.40, cost=0.62, irrig=0.35),
    "BELAGAVI":         dict(rain=0.55, price=0.58, yield_=0.60, cost=0.45, irrig=0.55),
    "BENGALURU RURAL":  dict(rain=0.60, price=0.65, yield_=0.62, cost=0.40, irrig=0.58),
    "BENGALURU URBAN":  dict(rain=0.58, price=0.70, yield_=0.65, cost=0.38, irrig=0.60),
    "BIDAR":            dict(rain=0.35, price=0.45, yield_=0.38, cost=0.65, irrig=0.32),
    "CHAMARAJANAGAR":   dict(rain=0.50, price=0.50, yield_=0.52, cost=0.50, irrig=0.48),
    "CHIKKABALLAPUR":   dict(rain=0.45, price=0.55, yield_=0.50, cost=0.48, irrig=0.45),
    "CHIKKAMAGALURU":   dict(rain=0.70, price=0.65, yield_=0.68, cost=0.35, irrig=0.65),
    "CHITRADURGA":      dict(rain=0.30, price=0.42, yield_=0.35, cost=0.65, irrig=0.28),
    "DAKSHINA KANNADA": dict(rain=0.78, price=0.68, yield_=0.72, cost=0.32, irrig=0.72),
    "DAVANAGERE":       dict(rain=0.48, price=0.52, yield_=0.50, cost=0.50, irrig=0.46),
    "DHARWAD":          dict(rain=0.52, price=0.55, yield_=0.55, cost=0.46, irrig=0.50),
    "GADAG":            dict(rain=0.36, price=0.46, yield_=0.40, cost=0.60, irrig=0.35),
    "HASSAN":           dict(rain=0.62, price=0.60, yield_=0.62, cost=0.40, irrig=0.60),
    "HAVERI":           dict(rain=0.46, price=0.50, yield_=0.48, cost=0.52, irrig=0.44),
    "KALABURAGI":       dict(rain=0.28, price=0.40, yield_=0.32, cost=0.68, irrig=0.25),
    "KODAGU":           dict(rain=0.82, price=0.72, yield_=0.78, cost=0.28, irrig=0.75),
    "KOLAR":            dict(rain=0.40, price=0.55, yield_=0.44, cost=0.55, irrig=0.38),
    "KOPPAL":           dict(rain=0.30, price=0.42, yield_=0.35, cost=0.66, irrig=0.28),
    "MANDYA":           dict(rain=0.58, price=0.60, yield_=0.62, cost=0.42, irrig=0.65),
    "MYSURU":           dict(rain=0.60, price=0.62, yield_=0.63, cost=0.40, irrig=0.60),
    "RAICHUR":          dict(rain=0.28, price=0.38, yield_=0.30, cost=0.70, irrig=0.22),
    "RAMANAGARA":       dict(rain=0.52, price=0.55, yield_=0.54, cost=0.46, irrig=0.50),
    "SHIVAMOGGA":       dict(rain=0.72, price=0.65, yield_=0.70, cost=0.33, irrig=0.68),
    "TUMAKURU":         dict(rain=0.42, price=0.52, yield_=0.46, cost=0.54, irrig=0.40),
    "UDUPI":            dict(rain=0.80, price=0.68, yield_=0.74, cost=0.30, irrig=0.72),
    "UTTARA KANNADA":   dict(rain=0.75, price=0.62, yield_=0.68, cost=0.35, irrig=0.65),
    "VIJAYAPURA":       dict(rain=0.32, price=0.44, yield_=0.36, cost=0.64, irrig=0.30),
    "YADGIR":           dict(rain=0.25, price=0.38, yield_=0.28, cost=0.72, irrig=0.20),
}

# FSI formula weights
FSI_WEIGHTS = {
    "rainfall":   0.25,
    "price":      0.25,
    "yield":      0.20,
    "cost":       0.20,
    "irrigation": 0.10,
}

# Stress classification thresholds (percentile-based, v4)
STRESS_LOW_PERCENTILE  = 0.33
STRESS_HIGH_PERCENTILE = 0.66

# Achievement metadata
ACH_META = {
    "Rain Master":   ("💧", "#00ccff", "Rainfall above 80%"),
    "Profit King":   ("💰", "#ffea00", "Crop price above 80%"),
    "Harvest Hero":  ("🌿", "#39ff14", "Yield above 80%"),
    "Cost Cutter":   ("💡", "#ff9900", "Input cost below 20%"),
    "Water Wizard":  ("💦", "#00eeff", "Irrigation above 80%"),
    "Farm Zen":      ("☮",  "#00ff88", "FSI below 12%"),
    "Avenger Elite": ("⚡", "#ff44ff", "All other achievements unlocked"),
}
