# 🌾 AgriStress Avengers — Farmer Stress Index Dashboard

**Spatial Hotspot Detection of Farmer Stress using Geospatial Farmer Stress Index**

> Group: AGRISTRESS AVENGERS  
> Members: Badiya Sunil Kumar | Yashaswini H V | SRL Keerthi | Sibbala Yoshitha

---

## 📌 About

This Streamlit dashboard computes a **Farmer Stress Index (FSI)** by combining 5 agricultural indicators:

| Indicator | Stress Direction |
|-----------|-----------------|
| 🌧️ Rainfall | Less = More stress |
| 💰 Market Price | Lower = More stress |
| 🌾 Crop Yield | Lower = More stress |
| 🧾 Cultivation Cost | Higher = More stress |
| 💧 Irrigation | Less = More stress |

Districts are classified into **High / Medium / Low** stress zones and visualized as hotspot maps.

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/srlkeerthi593-crypto/Geospatial-farmer-stress-detection.git
cd Geospatial-farmer-stress-detection
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
📦 Geospatial-farmer-stress-detection
 ┣ 📂 data/
 ┃ ┗ 📄 agri_dataset_500_samples.xlsx      ← Main dataset (AP & Karnataka)
 ┣ 📂 src/
 ┃ ┗ 📄 fsi_utils.py                       ← FSI computation utilities
 ┣ 📂 docs/
 ┃ ┗ 📄 Farmer_Stress_Proposal.pdf         ← Project proposal
 ┣ 📄 app.py                               ← Main Streamlit application
 ┣ 📄 requirements.txt                     ← Python dependencies
 ┗ 📄 README.md
```

---

## 🖥️ Dashboard Features

| Tab | Description |
|-----|-------------|
| 🗺️ Hotspot Map | District-wise FSI bar map + pie chart + top hotspots |
| 📊 FSI Analysis | Distribution histogram, crop-wise boxplot, radar chart |
| 📈 Indicator Deep Dive | Per-indicator analysis + correlation heatmap |
| 🏆 District Rankings | High/Medium/Low stress district tables |
| 📋 Raw Data | Full dataset with FSI scores + download as CSV |

---

## ⚙️ How FSI is Computed

```
FSI = w1×(1-norm_Rainfall) + w2×(1-norm_Price) + w3×(1-norm_Yield) 
    + w4×norm_Cost + w5×(1-norm_Irrigation)
```

Default weights: Rainfall=0.25, Price=0.25, Yield=0.20, Cost=0.20, Irrigation=0.10

All weights are **adjustable via the sidebar sliders** in real time.

---

## 📊 Dataset

- **Regions:** 25 districts across Andhra Pradesh and Karnataka
- **Crops:** Cotton, Maize, Millets, Rice, Sugarcane, Wheat
- **Records:** 500 samples
- **Period:** 2015–2023

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Visualization:** Plotly
- **Data Processing:** Pandas, NumPy
- **ML/Stats:** Scikit-learn, SciPy
- **GIS (next phase):** GeoPandas, Folium, PySAL, QGIS

---

## 📜 License
MIT License — Free to use for academic and research purposes.
