# =========================================================
# ⚡ AGRISTRESS AVENGERS — FINAL SUBMISSION EDITION
# MSC (AA) & PGD (SDS) Python Project Work 2026
#
# PURPOSE:
#   A GUI-based geospatial Python application that detects,
#   visualises, and predicts farm stress across all 30
#   Karnataka districts using real agricultural parameters.
#
# TECHNICAL TRACK: Machine Learning (ML Track)
#   Libraries used:
#     • scikit-learn : KMeans clustering + Linear Regression
#     • pandas / numpy : data wrangling and computation
#     • plotly : interactive geospatial visualisations
#     • streamlit : GUI framework
#
# AUTHOR  : [Your Name]
# DATE    : 2026
# VERSION : 3.0 (Final)
# =========================================================

# ── Standard library ──────────────────────────────────────
import os
import random

# ── Third-party: data & ML ────────────────────────────────
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans                    # Unsupervised spatial clustering
from sklearn.linear_model import LinearRegression     # Supervised FSI prediction
from sklearn.metrics import mean_squared_error, r2_score  # Model evaluation
from sklearn.model_selection import train_test_split  # Train/test split
from sklearn.preprocessing import StandardScaler      # Feature normalisation

# ── Third-party: visualisation & GUI ─────────────────────
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# Must be the very first Streamlit call in the script.
# Sets browser tab title, wide layout, and collapsed sidebar.
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚡ AgriStress Avengers",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────
# WEB AUDIO SYNTHESISER (JavaScript)
#
# Generates 8-bit chiptune music entirely in the browser
# using the Web Audio API — no external audio files needed.
# Two melodies are defined:
#   MELODY_PEACE : plays when farm stress is low
#   MELODY_TENSE : plays when farm stress is high
# Sound effects (SFX) fire on achievements and stress spikes.
# ─────────────────────────────────────────────────────────
MUSIC_JS = """
<script>
let audioCtx = null;
let musicPlaying = false;
let musicInterval = null;

const NOTES = {
  C4:261.63, D4:293.66, E4:329.63, F4:349.23,
  G4:392.00, A4:440.00, B4:493.88, C5:523.25,
  D5:587.33, E5:659.25, G5:783.99
};

const MELODY_PEACE = ['C4','E4','G4','E4','C4','G4','A4','G4','E4','C5','B4','G4'];
const MELODY_TENSE = ['A4','A4','G5','A4','G4','A4','G5','E5','D5','E5','D4','E4'];

let currentMelody = MELODY_PEACE;
let noteIdx = 0;

function initAudio() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
}

function playNote(freq, duration, type='square', volume=0.08) {
  if (!audioCtx) return;
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.connect(gain);
  gain.connect(audioCtx.destination);
  osc.type = type;
  osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
  gain.gain.setValueAtTime(volume, audioCtx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
  osc.start(audioCtx.currentTime);
  osc.stop(audioCtx.currentTime + duration);
}

function playNextNote() {
  if (!musicPlaying) return;
  const noteKey = currentMelody[noteIdx % currentMelody.length];
  playNote(NOTES[noteKey], 0.3, 'square', 0.07);
  if (noteIdx % 4 === 0) playNote(NOTES['C4'] / 2, 0.4, 'sine', 0.06);
  noteIdx++;
}

function startMusic(melody) {
  initAudio();
  currentMelody = melody === 'peace' ? MELODY_PEACE : MELODY_TENSE;
  musicPlaying = true;
  noteIdx = 0;
  clearInterval(musicInterval);
  musicInterval = setInterval(playNextNote, 380);
}

function stopMusic() {
  musicPlaying = false;
  clearInterval(musicInterval);
}

function switchMelody(melody) {
  currentMelody = melody === 'peace' ? MELODY_PEACE : MELODY_TENSE;
  noteIdx = 0;
}

function playSFX(type) {
  initAudio();
  if (type === 'win') {
    [523.25, 659.25, 783.99, 1046.5].forEach((f, i) => {
      setTimeout(() => playNote(f, 0.25, 'square', 0.1), i * 120);
    });
  } else if (type === 'alert') {
    [220, 185, 220, 185].forEach((f, i) => {
      setTimeout(() => playNote(f, 0.15, 'sawtooth', 0.08), i * 150);
    });
  } else if (type === 'click') {
    playNote(440, 0.05, 'sine', 0.06);
  }
}

window.AgriMusic = { startMusic, stopMusic, switchMelody, playSFX };
</script>
"""

# ─────────────────────────────────────────────────────────
# CSS — NEON GAME UI
#
# Custom stylesheet injected via st.markdown.
# Uses Google Fonts: Orbitron (headings), Rajdhani (body),
# Share Tech Mono (monospace data displays).
# Key visual effects:
#   • Scanline + grid overlays for retro CRT feel
#   • CSS keyframe animations for farmer character states
#   • Glowing borders and pulsing metric cards
# ─────────────────────────────────────────────────────────
GAME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: radial-gradient(ellipse at 10% 0%, #001a08 0%, #000d02 55%, #000000 100%) !important;
    color: #00ff88 !important;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background: repeating-linear-gradient(0deg, transparent, transparent 2px,
        rgba(0,255,136,0.012) 2px, rgba(0,255,136,0.012) 4px);
}

[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image:
        linear-gradient(rgba(0,255,136,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,136,0.03) 1px, transparent 1px);
    background-size: 60px 60px;
}

h1 {
    font-family: 'Orbitron', monospace !important;
    text-align: center !important;
    font-size: 2.6rem !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, #00ff88, #39ff14, #00ffcc) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    filter: drop-shadow(0 0 24px rgba(0,255,136,0.7)) !important;
    animation: titlePulse 3s ease-in-out infinite !important;
    letter-spacing: 0.1em !important;
    margin-bottom: 4px !important;
}

@keyframes titlePulse {
    0%,100% { filter: drop-shadow(0 0 18px rgba(0,255,136,0.6)); }
    50%      { filter: drop-shadow(0 0 40px rgba(0,255,136,1)); }
}

h2, h3 {
    font-family: 'Orbitron', monospace !important;
    color: #39ff14 !important;
    letter-spacing: 0.1em !important;
    text-shadow: 0 0 10px rgba(57,255,20,0.4) !important;
}

[data-testid="stVerticalBlock"] > div > div { position: relative; z-index: 1; }

.game-card {
    background: rgba(0,20,5,0.88) !important;
    border: 1px solid rgba(0,255,136,0.4) !important;
    border-radius: 10px !important;
    padding: 18px 20px !important;
    position: relative !important;
    backdrop-filter: blur(8px) !important;
    box-shadow: 0 0 30px rgba(0,255,136,0.05), inset 0 0 40px rgba(0,0,0,0.4) !important;
}

.game-card::before {
    content: '';
    position: absolute; top: 0; left: 15%; right: 15%; height: 1px;
    background: linear-gradient(90deg, transparent, #00ff88, transparent);
}

[data-testid="stMetric"] {
    background: rgba(0,20,5,0.9) !important;
    border: 1px solid rgba(0,255,136,0.3) !important;
    border-radius: 8px !important;
    padding: 12px !important;
    animation: metricGlow 3s ease-in-out infinite !important;
}

@keyframes metricGlow {
    0%,100% { box-shadow: 0 0 8px rgba(0,255,136,0.1); }
    50%      { box-shadow: 0 0 20px rgba(0,255,136,0.3); }
}

[data-testid="stMetricLabel"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.72rem !important;
    color: rgba(0,255,136,0.6) !important;
    letter-spacing: 0.15em !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    color: #00ff88 !important;
    text-shadow: 0 0 10px rgba(0,255,136,0.5) !important;
}

[data-testid="stSlider"] > div > div > div { color: #00ff88 !important; }
[data-testid="stSlider"] > div > div > div > div { background: rgba(0,255,136,0.15) !important; }
[data-testid="stSlider"] > div > div > div > div > div {
    background: #00ff88 !important;
    box-shadow: 0 0 10px #00ff88 !important;
}

[data-testid="stSelectbox"] > div > div {
    background: rgba(0,20,5,0.9) !important;
    border: 1px solid rgba(0,255,136,0.4) !important;
    color: #00ff88 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

.stButton > button {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    background: rgba(0,20,5,0.9) !important;
    color: #00ff88 !important;
    border: 1px solid rgba(0,255,136,0.5) !important;
    border-radius: 4px !important;
    padding: 8px 16px !important;
    transition: all 0.25s !important;
    clip-path: polygon(6px 0%, 100% 0%, calc(100% - 6px) 100%, 0% 100%) !important;
}

.stButton > button:hover {
    background: rgba(0,255,136,0.15) !important;
    box-shadow: 0 0 20px rgba(0,255,136,0.4) !important;
    transform: translateY(-2px) !important;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] { background: transparent !important; gap: 6px !important; }
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    color: rgba(0,255,136,0.5) !important;
    background: rgba(0,20,5,0.8) !important;
    border: 1px solid rgba(0,255,136,0.25) !important;
    border-radius: 4px !important;
    padding: 8px 18px !important;
    transition: all 0.25s !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: #00ff88 !important;
    background: rgba(0,255,136,0.12) !important;
    border-color: #00ff88 !important;
    box-shadow: 0 0 14px rgba(0,255,136,0.3) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: transparent !important; }
[data-testid="stTabs"] [data-baseweb="tab-border"] { background: rgba(0,255,136,0.15) !important; }

[data-testid="stExpander"] {
    background: rgba(0,20,5,0.7) !important;
    border: 1px solid rgba(0,255,136,0.2) !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
    color: #39ff14 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
}

label, .stMarkdown p, .stMarkdown li {
    color: rgba(0,255,136,0.85) !important;
    font-family: 'Rajdhani', sans-serif !important;
}

.element-container .stAlert {
    background: rgba(255,34,68,0.08) !important;
    border: 1px solid rgba(255,34,68,0.4) !important;
    border-left: 3px solid #ff2244 !important;
    border-radius: 6px !important;
    animation: alertPulse 2.5s ease-in-out infinite !important;
}
@keyframes alertPulse {
    0%,100% { background: rgba(255,34,68,0.05); }
    50%      { background: rgba(255,34,68,0.12); }
}

.stSuccess {
    background: rgba(0,255,136,0.08) !important;
    border: 1px solid rgba(0,255,136,0.3) !important;
    color: #00ff88 !important;
}
.stWarning {
    background: rgba(255,234,0,0.08) !important;
    border: 1px solid rgba(255,234,0,0.3) !important;
}

[data-testid="stSidebar"] {
    background: rgba(0,10,3,0.97) !important;
    border-right: 1px solid rgba(0,255,136,0.2) !important;
}

/* ── Farmer character animations ── */
.farmer-box {
    background: rgba(0,10,3,0.95);
    border: 1px solid rgba(0,255,136,0.5);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.farmer-box::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #00ff88, transparent);
    animation: scanBar 3s linear infinite;
}
@keyframes scanBar { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }

.farmer-emoji {
    font-size: 5rem; display: block;
    animation: farmerBob 2s ease-in-out infinite;
    filter: drop-shadow(0 0 15px rgba(0,255,136,0.4));
}
@keyframes farmerBob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }

.farmer-emoji.happy {
    animation: farmerDance 0.5s ease-in-out infinite;
    filter: drop-shadow(0 0 20px rgba(57,255,20,0.7));
}
@keyframes farmerDance {
    0%,100% { transform: scale(1) rotate(-4deg); }
    50%      { transform: scale(1.12) rotate(4deg); }
}

.farmer-emoji.stressed {
    animation: farmerShake 0.4s ease-in-out infinite;
    filter: drop-shadow(0 0 15px rgba(255,34,68,0.6));
}
@keyframes farmerShake {
    0%,100% { transform: rotate(-6deg) scale(0.95); }
    50%      { transform: rotate(6deg) scale(1.05); }
}

.farmer-emoji.crisis {
    animation: farmerCrisis 0.25s ease-in-out infinite;
    filter: drop-shadow(0 0 20px rgba(255,34,68,0.9));
}
@keyframes farmerCrisis {
    0%,100% { transform: rotate(-8deg) scale(0.9) translateY(4px); }
    50%      { transform: rotate(8deg) scale(1.1) translateY(-4px); }
}

.mood-track {
    width: 100%; height: 14px;
    background: rgba(0,255,136,0.1);
    border-radius: 7px;
    border: 1px solid rgba(0,255,136,0.2);
    overflow: hidden; margin: 8px 0;
}
.mood-fill-inner {
    height: 100%; border-radius: 7px;
    transition: width 0.6s ease, background 0.6s ease;
    position: relative; overflow: hidden;
}
.mood-fill-inner::after {
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(90deg, transparent 50%, rgba(255,255,255,0.2));
    animation: shineBar 1.5s ease-in-out infinite;
}
@keyframes shineBar { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }

.fsi-big {
    font-family: 'Orbitron', monospace;
    font-size: 2.4rem; font-weight: 900; text-align: center;
    transition: color 0.5s, text-shadow 0.5s;
}

.ach-banner {
    background: linear-gradient(135deg, rgba(0,40,10,0.95), rgba(0,20,5,0.95));
    border: 2px solid #39ff14; border-radius: 10px;
    padding: 14px 20px; text-align: center;
    font-family: 'Orbitron', monospace;
    animation: achGlow 1s ease-in-out 3;
}
@keyframes achGlow {
    0%,100% { box-shadow: 0 0 20px rgba(57,255,20,0.3); }
    50%      { box-shadow: 0 0 50px rgba(57,255,20,0.8); }
}

.xp-track { height: 8px; background: rgba(0,255,136,0.1); border-radius: 4px; overflow: hidden; }
.xp-fill  { height: 100%; background: linear-gradient(90deg, #006622, #39ff14); border-radius: 4px; transition: width 0.5s; }

hr { border: none !important; border-top: 1px solid rgba(0,255,136,0.15) !important; margin: 16px 0 !important; }

[data-testid="stFileUploader"] {
    border: 1px dashed rgba(0,255,136,0.3) !important;
    border-radius: 8px !important;
    background: rgba(0,20,5,0.5) !important;
}

[data-testid="stMultiSelect"] > div {
    background: rgba(0,20,5,0.9) !important;
    border: 1px solid rgba(0,255,136,0.3) !important;
}

.stCaption, small {
    color: rgba(0,255,136,0.5) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.72rem !important;
}

.glow-green  { color: #00ff88; text-shadow: 0 0 10px rgba(0,255,136,0.7); }
.glow-red    { color: #ff2244; text-shadow: 0 0 10px rgba(255,34,68,0.7); }
.glow-yellow { color: #ffea00; text-shadow: 0 0 10px rgba(255,234,0,0.7); }
.glow-lime   { color: #39ff14; text-shadow: 0 0 10px rgba(57,255,20,0.7); }
</style>
"""

# Inject CSS and JS into the Streamlit page
st.markdown(GAME_CSS, unsafe_allow_html=True)
st.markdown(MUSIC_JS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# KARNATAKA DISTRICT COORDINATES
#
# Real-world latitude/longitude centroids for all 30
# Karnataka districts. Used to place markers on the map.
# Source: approximate geographic centroids.
# ─────────────────────────────────────────────────────────
DISTRICT_COORDS = {
    "BAGALKOT":        (16.18, 75.69),
    "BALLARI":         (15.14, 76.92),
    "BELAGAVI":        (15.86, 74.50),
    "BENGALURU RURAL": (13.16, 77.51),
    "BENGALURU URBAN": (12.97, 77.57),
    "BIDAR":           (17.91, 76.82),
    "CHAMARAJANAGAR":  (11.94, 77.17),
    "CHIKKABALLAPUR":  (13.43, 77.73),
    "CHIKKAMAGALURU":  (13.31, 75.77),
    "CHITRADURGA":     (14.23, 76.40),
    "DAKSHINA KANNADA":(12.85, 74.88),
    "DAVANAGERE":      (14.46, 75.92),
    "DHARWAD":         (15.45, 75.01),
    "GADAG":           (15.42, 75.62),
    "HASSAN":          (13.00, 76.10),
    "HAVERI":          (14.79, 75.40),
    "KALABURAGI":      (17.33, 76.82),
    "KODAGU":          (12.41, 75.74),
    "KOLAR":           (13.13, 78.13),
    "KOPPAL":          (15.35, 76.15),
    "MANDYA":          (12.52, 76.90),
    "MYSURU":          (12.30, 76.65),
    "RAICHUR":         (16.21, 77.36),
    "RAMANAGARA":      (12.72, 77.28),
    "SHIVAMOGGA":      (13.93, 75.56),
    "TUMAKURU":        (13.34, 77.10),
    "UDUPI":           (13.34, 74.74),
    "UTTARA KANNADA":  (14.80, 74.73),
    "VIJAYAPURA":      (16.83, 75.72),
    "YADGIR":          (16.76, 77.60),
}

# ─────────────────────────────────────────────────────────
# SYNTHETIC DATASET CONFIGURATION
#
# Each district has a hand-crafted baseline profile derived
# from real Karnataka agricultural knowledge:
#   - Coastal/Western Ghats districts (Kodagu, Udupi) → high rain
#   - Northern dry-land districts (Raichur, Yadgir) → low rain, high cost
#   - Bangalore region → higher prices, better infrastructure
#
# Gaussian noise is added per sample to simulate natural
# variation around these baselines.
# ─────────────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

DISTRICTS = list(DISTRICT_COORDS.keys())

CROPS = [
    "Rice", "Wheat", "Maize", "Ragi", "Jowar",
    "Sugarcane", "Cotton", "Groundnut", "Sunflower", "Areca Nut",
    "Coffee", "Coconut", "Banana", "Tomato", "Onion"
]

# District baseline profiles: all values normalised 0.0–1.0
DISTRICT_PROFILES = {
    "BAGALKOT":        dict(rain=0.38, price=0.52, yield_=0.46, cost=0.58, irrig=0.42),
    "BALLARI":         dict(rain=0.32, price=0.48, yield_=0.40, cost=0.62, irrig=0.35),
    "BELAGAVI":        dict(rain=0.55, price=0.58, yield_=0.60, cost=0.45, irrig=0.55),
    "BENGALURU RURAL": dict(rain=0.60, price=0.65, yield_=0.62, cost=0.40, irrig=0.58),
    "BENGALURU URBAN": dict(rain=0.58, price=0.70, yield_=0.65, cost=0.38, irrig=0.60),
    "BIDAR":           dict(rain=0.35, price=0.45, yield_=0.38, cost=0.65, irrig=0.32),
    "CHAMARAJANAGAR":  dict(rain=0.50, price=0.50, yield_=0.52, cost=0.50, irrig=0.48),
    "CHIKKABALLAPUR":  dict(rain=0.45, price=0.55, yield_=0.50, cost=0.48, irrig=0.45),
    "CHIKKAMAGALURU":  dict(rain=0.70, price=0.65, yield_=0.68, cost=0.35, irrig=0.65),
    "CHITRADURGA":     dict(rain=0.30, price=0.42, yield_=0.35, cost=0.65, irrig=0.28),
    "DAKSHINA KANNADA":dict(rain=0.78, price=0.68, yield_=0.72, cost=0.32, irrig=0.72),
    "DAVANAGERE":      dict(rain=0.48, price=0.52, yield_=0.50, cost=0.50, irrig=0.46),
    "DHARWAD":         dict(rain=0.52, price=0.55, yield_=0.55, cost=0.46, irrig=0.50),
    "GADAG":           dict(rain=0.36, price=0.46, yield_=0.40, cost=0.60, irrig=0.35),
    "HASSAN":          dict(rain=0.62, price=0.60, yield_=0.62, cost=0.40, irrig=0.60),
    "HAVERI":          dict(rain=0.46, price=0.50, yield_=0.48, cost=0.52, irrig=0.44),
    "KALABURAGI":      dict(rain=0.28, price=0.40, yield_=0.32, cost=0.68, irrig=0.25),
    "KODAGU":          dict(rain=0.82, price=0.72, yield_=0.78, cost=0.28, irrig=0.75),
    "KOLAR":           dict(rain=0.40, price=0.55, yield_=0.44, cost=0.55, irrig=0.38),
    "KOPPAL":          dict(rain=0.30, price=0.42, yield_=0.35, cost=0.66, irrig=0.28),
    "MANDYA":          dict(rain=0.58, price=0.60, yield_=0.62, cost=0.42, irrig=0.65),
    "MYSURU":          dict(rain=0.60, price=0.62, yield_=0.63, cost=0.40, irrig=0.60),
    "RAICHUR":         dict(rain=0.28, price=0.38, yield_=0.30, cost=0.70, irrig=0.22),
    "RAMANAGARA":      dict(rain=0.52, price=0.55, yield_=0.54, cost=0.46, irrig=0.50),
    "SHIVAMOGGA":      dict(rain=0.72, price=0.65, yield_=0.70, cost=0.33, irrig=0.68),
    "TUMAKURU":        dict(rain=0.42, price=0.52, yield_=0.46, cost=0.54, irrig=0.40),
    "UDUPI":           dict(rain=0.80, price=0.68, yield_=0.74, cost=0.30, irrig=0.72),
    "UTTARA KANNADA":  dict(rain=0.75, price=0.62, yield_=0.68, cost=0.35, irrig=0.65),
    "VIJAYAPURA":      dict(rain=0.32, price=0.44, yield_=0.36, cost=0.64, irrig=0.30),
    "YADGIR":          dict(rain=0.25, price=0.38, yield_=0.28, cost=0.72, irrig=0.20),
}


@st.cache_data
def generate_dataset() -> pd.DataFrame:
    """
    Generate 750 synthetic farm records for Karnataka.

    Each record represents one farm observation with 5 normalised
    parameters (0.0–1.0). Gaussian noise (std=0.12) is added around
    district baselines to simulate natural variation. Crop-specific
    adjustments reflect real agronomic knowledge (e.g., Coffee needs
    more rainfall, Cotton has higher input costs).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: Region, Crop, Rainfall, Price,
        Cost, Yield, Irrigation.
    """
    records = []
    samples_per_district = 750 // len(DISTRICTS)   # 25 per district
    extra = 750 - samples_per_district * len(DISTRICTS)

    for i, district in enumerate(DISTRICTS):
        p = DISTRICT_PROFILES[district]
        n = samples_per_district + (1 if i < extra else 0)

        for _ in range(n):
            crop = random.choice(CROPS)
            noise = 0.12  # Standard deviation for Gaussian noise

            # Sample each parameter from a normal distribution,
            # clipped to valid range [0.05, 0.98]
            rain  = float(np.clip(np.random.normal(p["rain"],   noise), 0.05, 0.98))
            price = float(np.clip(np.random.normal(p["price"],  noise), 0.05, 0.98))
            yld   = float(np.clip(np.random.normal(p["yield_"], noise), 0.05, 0.98))
            cost  = float(np.clip(np.random.normal(p["cost"],   noise), 0.05, 0.98))
            irrig = float(np.clip(np.random.normal(p["irrig"],  noise), 0.05, 0.98))

            # Apply crop-specific agronomic adjustments
            if crop in ["Coffee", "Coconut", "Areca Nut"]:
                # High-rainfall plantation crops
                rain  = min(rain + 0.10, 0.98)
                irrig = min(irrig + 0.08, 0.98)
            elif crop in ["Ragi", "Jowar"]:
                # Drought-resistant millets — lower rain, lower cost
                rain = max(rain - 0.05, 0.05)
                cost = max(cost - 0.05, 0.05)
            elif crop == "Cotton":
                # Cash crop — higher input cost, better price
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


# ─────────────────────────────────────────────────────────
# SESSION STATE INITIALISATION
#
# Streamlit reruns the entire script on every widget
# interaction. Session state persists values across reruns.
# ─────────────────────────────────────────────────────────
if "score"        not in st.session_state: st.session_state.score = 0
if "xp"           not in st.session_state: st.session_state.xp = 0
if "level"        not in st.session_state: st.session_state.level = 1
if "achievements" not in st.session_state:
    st.session_state.achievements = {
        "Rain Master": False, "Profit King": False,
        "Harvest Hero": False, "Cost Cutter": False,
        "Water Wizard": False, "Farm Zen": False,
        "Avenger Elite": False
    }
if "music_on"  not in st.session_state: st.session_state.music_on = False
if "last_fsi"  not in st.session_state: st.session_state.last_fsi = 0.5
if "preset"    not in st.session_state: st.session_state.preset = None


# ─────────────────────────────────────────────────────────
# FSI (FARM STRESS INDEX) FUNCTIONS
# ─────────────────────────────────────────────────────────

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

    Weights reflect relative importance from agronomic literature.
    Rainfall and Price carry the highest weight (25% each) as they
    are the primary drivers of farmer income and survival.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns Rainfall, Price, Yield, Cost, Irrigation.

    Returns
    -------
    pd.DataFrame
        Same DataFrame with an additional 'FSI' column.
    """
    df = df.copy()
    df["FSI"] = (
        (1 - df["Rainfall"])   * 0.25 +
        (1 - df["Price"])      * 0.25 +
        (1 - df["Yield"])      * 0.20 +
        df["Cost"]             * 0.20 +
        (1 - df["Irrigation"]) * 0.10
    )
    return df


def add_stress_labels(df: pd.DataFrame):
    """
    Classify each district as HIGH / MEDIUM / LOW stress.

    Uses percentile-based thresholds (33rd and 66th) so that
    exactly one-third of districts fall into each category.
    This relative classification is more robust than fixed
    thresholds, especially when dataset composition changes.

    Parameters
    ----------
    df : pd.DataFrame  DataFrame with 'FSI' column.

    Returns
    -------
    tuple : (DataFrame with 'Stress' column, p33 float, p66 float)
    """
    p33 = df["FSI"].quantile(0.33)
    p66 = df["FSI"].quantile(0.66)

    def classify(x):
        if x >= p66:   return "HIGH"
        elif x >= p33: return "MEDIUM"
        else:          return "LOW"

    df["Stress"] = df["FSI"].apply(classify)
    return df, p33, p66


def get_reason(row: pd.Series) -> str:
    """
    Generate a human-readable explanation for a district's stress.

    Checks each parameter against fixed threshold values to identify
    which factors are contributing to farm stress. Used in tooltips
    and alert panels.

    Parameters
    ----------
    row : pd.Series  A row from the aggregated district DataFrame.

    Returns
    -------
    str  Comma-separated list of stress reasons, or 'Balanced'.
    """
    reasons = []
    if row["Rainfall"]   < 0.4: reasons.append("Low Rainfall")
    if row["Yield"]      < 0.4: reasons.append("Low Yield")
    if row["Price"]      < 0.4: reasons.append("Low Price")
    if row["Cost"]       > 0.6: reasons.append("High Cost")
    if row["Irrigation"] < 0.4: reasons.append("Poor Irrigation")
    return ", ".join(reasons) if reasons else "Balanced"


def add_coords(df: pd.DataFrame) -> pd.DataFrame:
    """
    Attach latitude and longitude to each district row.

    Looks up coordinates from DISTRICT_COORDS dictionary.
    Falls back to Karnataka's geographic centre (14.5, 76.5)
    for any unrecognised district name.

    Parameters
    ----------
    df : pd.DataFrame  DataFrame with a 'Region' column.

    Returns
    -------
    pd.DataFrame  Same DataFrame with 'lat' and 'lon' columns added.
    """
    df = df.copy()
    df["lat"] = df["Region"].map(lambda r: DISTRICT_COORDS.get(r, (14.5, 76.5))[0])
    df["lon"] = df["Region"].map(lambda r: DISTRICT_COORDS.get(r, (14.5, 76.5))[1])
    return df


def aggregate(df: pd.DataFrame):
    """
    Aggregate raw farm records to one row per district.

    Groups by Region and computes mean values for all 5 parameters.
    Then computes FSI, stress labels, reasons, and coordinates.

    Parameters
    ----------
    df : pd.DataFrame  Filtered farm-level DataFrame.

    Returns
    -------
    tuple : (aggregated DataFrame, p33 float, p66 float)
    """
    agg = df.groupby("Region", as_index=False).agg(
        Rainfall=("Rainfall",   "mean"),
        Price=("Price",         "mean"),
        Yield=("Yield",         "mean"),
        Cost=("Cost",           "mean"),
        Irrigation=("Irrigation","mean"),
        Samples=("Rainfall",    "count")
    )
    agg = compute_fsi(agg)
    agg, p33, p66 = add_stress_labels(agg)
    agg["Reason"] = agg.apply(get_reason, axis=1)
    agg = add_coords(agg)
    return agg, p33, p66


# ─────────────────────────────────────────────────────────
# ML MODULE 1 — KMeans CLUSTERING
#
# Unsupervised machine learning to group districts by
# agricultural similarity. Unlike the FSI rule-based
# classification, KMeans discovers natural groupings
# from the data itself without using any predefined labels.
#
# Steps:
#   1. Extract 5-feature matrix per district
#   2. Standardise features (zero mean, unit variance)
#   3. Fit KMeans with k=3 (mirrors LOW/MEDIUM/HIGH)
#   4. Map numeric cluster IDs → stress labels by FSI rank
# ─────────────────────────────────────────────────────────
@st.cache_data
def run_kmeans_clustering(agg_df: pd.DataFrame):
    """
    Run KMeans clustering on district-level farm features.

    Uses StandardScaler to normalise features before clustering
    so that no single parameter dominates due to scale differences.
    Cluster labels are mapped to LOW/MEDIUM/HIGH by ranking
    cluster centroids on mean FSI.

    Parameters
    ----------
    agg_df : pd.DataFrame  Aggregated district DataFrame with FSI.

    Returns
    -------
    tuple : (DataFrame with ML_Stress column, KMeans model, scaler)
    """
    features = ["Rainfall", "Price", "Yield", "Cost", "Irrigation"]
    X = agg_df[features].values

    # Step 1: Standardise — zero mean, unit variance per feature
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Step 2: Fit KMeans with 3 clusters, fixed seed for reproducibility
    # n_init=10 runs the algorithm 10 times and picks the best result
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    agg_df = agg_df.copy()
    agg_df["KMeans_Cluster"] = labels

    # Step 3: Map cluster IDs to stress labels by average FSI
    # Cluster with lowest mean FSI → "LOW", highest → "HIGH"
    cluster_fsi_mean = agg_df.groupby("KMeans_Cluster")["FSI"].mean().sort_values()
    cluster_to_label = {
        cluster_fsi_mean.index[0]: "LOW",
        cluster_fsi_mean.index[1]: "MEDIUM",
        cluster_fsi_mean.index[2]: "HIGH",
    }
    agg_df["ML_Stress"] = agg_df["KMeans_Cluster"].map(cluster_to_label)

    return agg_df, kmeans, scaler


# ─────────────────────────────────────────────────────────
# ML MODULE 2 — LINEAR REGRESSION (FSI PREDICTION)
#
# Supervised machine learning to predict FSI from the 5
# farm parameters. This validates the FSI formula and
# shows which parameters most strongly influence stress.
#
# Steps:
#   1. Use farm-level data (750 rows) as training set
#   2. 80/20 train-test split
#   3. Fit LinearRegression on training set
#   4. Evaluate on test set using R² and RMSE
#   5. Extract feature coefficients as "importance" scores
# ─────────────────────────────────────────────────────────
@st.cache_data
def run_regression(df: pd.DataFrame):
    """
    Train a Linear Regression model to predict FSI.

    Uses the 5 raw farm parameters as features and FSI as
    the target variable. The model coefficients reveal which
    parameters most strongly drive farm stress.

    A high R² score (close to 1.0) indicates that the FSI
    formula is well-explained by a linear combination of
    the input parameters — as expected from its design.

    Parameters
    ----------
    df : pd.DataFrame  Farm-level DataFrame with FSI computed.

    Returns
    -------
    dict containing:
        model       : fitted LinearRegression object
        r2          : R² score on test set
        rmse        : Root Mean Squared Error on test set
        coef_df     : DataFrame of feature coefficients
        y_test      : actual FSI values (test set)
        y_pred      : predicted FSI values (test set)
        feature_names: list of feature names
    """
    features = ["Rainfall", "Price", "Yield", "Cost", "Irrigation"]
    X = df[features].values
    y = df["FSI"].values

    # 80/20 train-test split, stratification not needed for regression
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Fit model on training data only
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Evaluate on unseen test data
    y_pred = model.predict(X_test)
    r2   = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # Build coefficient table — positive = increases FSI (more stress)
    coef_df = pd.DataFrame({
        "Feature":     features,
        "Coefficient": model.coef_,
        "Abs_Coef":    np.abs(model.coef_)
    }).sort_values("Abs_Coef", ascending=False)

    return {
        "model":        model,
        "r2":           r2,
        "rmse":         rmse,
        "coef_df":      coef_df,
        "y_test":       y_test,
        "y_pred":       y_pred,
        "feature_names": features,
    }


# ─────────────────────────────────────────────────────────
# HEATMAP BUILDER
#
# Creates a Plotly Scattermapbox figure with dark tiles.
# Each district is a coloured circle where:
#   - Colour encodes FSI (green→yellow→red via RdYlGn scale)
#   - Size encodes FSI (larger = more stressed)
# Custom hover template shows all district stats.
# ─────────────────────────────────────────────────────────
def build_map(hex_df: pd.DataFrame, zoom: int = 6) -> go.Figure:
    """
    Build the interactive Karnataka FSI heatmap.

    Parameters
    ----------
    hex_df : pd.DataFrame  Aggregated district data with lat/lon/FSI.
    zoom   : int           Initial map zoom level (default 6).

    Returns
    -------
    go.Figure  Plotly figure ready for st.plotly_chart().
    """
    # Scale marker size: base 14px + up to 14px extra based on FSI
    marker_sizes = hex_df["FSI"].apply(lambda x: 14 + x * 14)

    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(
        lat=hex_df["lat"],
        lon=hex_df["lon"],
        mode="markers",
        marker=dict(
            size=marker_sizes,
            color=hex_df["FSI"],
            colorscale="RdYlGn",
            reversescale=True,       # Reverse so red = high stress
            opacity=0.90,
            colorbar=dict(
                title=dict(text="FSI", font=dict(color="#00ff88", family="Share Tech Mono")),
                tickfont=dict(color="#00ff88", family="Share Tech Mono"),
                bgcolor="rgba(0,13,2,0.85)",
                bordercolor="rgba(0,255,136,0.3)",
                borderwidth=1,
                thickness=14,
                len=0.75,
            )
        ),
        customdata=hex_df[["Region", "Stress", "Reason", "Samples",
                            "Rainfall", "Price", "Yield", "Cost", "Irrigation"]].values,
        hovertemplate=(
            "<b>🎯 %{customdata[0]}</b><br>"
            "━━━━━━━━━━━━━━━━━━<br>"
            "⚡ FSI Score: <b>%{marker.color:.3f}</b><br>"
            "🚨 Stress: <b>%{customdata[1]}</b><br>"
            "🧠 Reason: %{customdata[2]}<br>"
            "━━━━━━━━━━━━━━━━━━<br>"
            "🌧 Rainfall: %{customdata[4]:.2f} | 💰 Price: %{customdata[5]:.2f}<br>"
            "🌿 Yield: %{customdata[6]:.2f} | 📦 Cost: %{customdata[7]:.2f}<br>"
            "💧 Irrigation: %{customdata[8]:.2f}<br>"
            "📊 Samples: %{customdata[3]}<extra></extra>"
        )
    ))

    fig.update_layout(
        mapbox=dict(style="carto-darkmatter", center=dict(lat=14.5, lon=76.5), zoom=zoom),
        height=560,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Rajdhani", color="#00ff88"),
    )
    return fig


# ─────────────────────────────────────────────────────────
# FARMER GAME HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────

def compute_game_fsi(rain: int, price: int, yld: int,
                     cost: int, irrig: int) -> float:
    """
    Compute FSI from game slider values (0–100 integer scale).

    Converts slider integers to normalised floats [0,1] before
    applying the standard FSI formula.

    Parameters
    ----------
    rain, price, yld, cost, irrig : int  Slider values 0–100.

    Returns
    -------
    float  FSI in range [0.0, 1.0].
    """
    r, p, y, c, i = rain/100, price/100, yld/100, cost/100, irrig/100
    return (1-r)*0.25 + (1-p)*0.25 + (1-y)*0.20 + c*0.20 + (1-i)*0.10


def farmer_state(fsi: float):
    """
    Return the farmer character state based on current FSI.

    Maps FSI ranges to visual and textual feedback:
      [0.00, 0.12) → Thriving (dance animation, green glow)
      [0.12, 0.25) → Very Happy
      [0.25, 0.38) → Content
      [0.38, 0.50) → Neutral
      [0.50, 0.62) → Worried (shake animation)
      [0.62, 0.75) → Very Stressed
      [0.75, 1.00] → Crisis (rapid crisis animation, red glow)

    Parameters
    ----------
    fsi : float  Current Farm Stress Index.

    Returns
    -------
    tuple : (emoji, css_class, status_text, message, hex_color)
    """
    if fsi < 0.12:
        return ("🌟","happy","🌟 THRIVING — FARM CHAMPION!",
                "Wah! Nanna farm super aagide! My family is celebrating! You are a true Avenger! 🎉","#39ff14")
    elif fsi < 0.25:
        return ("👨‍🌾","happy","😊 VERY HAPPY",
                "Thumba khushi aagide! Great conditions! Keep it up, Avenger! 🌾","#39ff14")
    elif fsi < 0.38:
        return ("🧑‍🌾","","🙂 CONTENT",
                "Things are okay. A little more improvement and I'll be really happy! 😊","#00ff88")
    elif fsi < 0.50:
        return ("😐","","😐 NEUTRAL",
                "Hmm... conditions are average. Can you help improve rainfall or crop price?","#ffea00")
    elif fsi < 0.62:
        return ("😟","stressed","😟 WORRIED",
                "Aiyo! Things are not looking good. My yield is low or costs too high. Please help! 😰","#ffea00")
    elif fsi < 0.75:
        return ("😢","stressed","😢 VERY STRESSED",
                "Devare! I'm suffering. Rainfall is gone, prices are crashed. My family is hungry! 😭","#ff6600")
    else:
        return ("🆘","crisis","🆘 FARM CRISIS! HELP!",
                "SAVE ME! Everything has failed! No rain, no yield, high costs! My family needs help! 🚨","#ff2244")


def mood_color(mood_pct: int) -> str:
    """Return a CSS gradient string for the happiness bar based on percentage."""
    if mood_pct > 65:  return "linear-gradient(90deg,#005522,#39ff14)"
    elif mood_pct > 40: return "linear-gradient(90deg,#665500,#ffea00)"
    else:               return "linear-gradient(90deg,#660011,#ff2244)"


def check_achievements(rain, price, yld, cost, irrig, fsi) -> list:
    """
    Check and unlock achievements based on current slider values.

    Each achievement requires a specific parameter threshold to be
    met for the first time. 'Avenger Elite' requires all others
    to already be unlocked.

    Parameters
    ----------
    rain, price, yld, cost, irrig : int  Slider values 0–100.
    fsi : float  Current Farm Stress Index.

    Returns
    -------
    list  Names of newly unlocked achievements (may be empty).
    """
    unlocked = []
    achs = st.session_state.achievements
    checks = {
        "Rain Master":   (not achs["Rain Master"]   and rain  > 80),
        "Profit King":   (not achs["Profit King"]   and price > 80),
        "Harvest Hero":  (not achs["Harvest Hero"]  and yld   > 80),
        "Cost Cutter":   (not achs["Cost Cutter"]   and cost  < 20),
        "Water Wizard":  (not achs["Water Wizard"]  and irrig > 80),
        "Farm Zen":      (not achs["Farm Zen"]       and fsi  < 0.12),
        "Avenger Elite": (not achs["Avenger Elite"] and
                          all(achs[k] for k in list(achs.keys())[:-1])),
    }
    for name, condition in checks.items():
        if condition:
            st.session_state.achievements[name] = True
            unlocked.append(name)
    return unlocked


# Achievement display metadata: (icon, colour, description)
ACH_META = {
    "Rain Master":   ("💧", "#00ccff", "Rainfall above 80%"),
    "Profit King":   ("💰", "#ffea00", "Crop price above 80%"),
    "Harvest Hero":  ("🌿", "#39ff14", "Yield above 80%"),
    "Cost Cutter":   ("💡", "#ff9900", "Input cost below 20%"),
    "Water Wizard":  ("💦", "#00eeff", "Irrigation above 80%"),
    "Farm Zen":      ("☮",  "#00ff88", "FSI below 12%"),
    "Avenger Elite": ("⚡", "#ff44ff", "All other achievements unlocked"),
}


# ═════════════════════════════════════════════════════════
# ░░░░░░░░░░░░░░  MAIN APPLICATION  ░░░░░░░░░░░░░░░░░░░░░
# ═════════════════════════════════════════════════════════

# ── App Header ───────────────────────────────────────────
st.markdown("<h1>⚡ AGRISTRESS AVENGERS ⚡</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;font-family:Share Tech Mono,monospace;"
    "color:rgba(0,255,136,0.5);font-size:0.82rem;letter-spacing:0.3em;margin-bottom:6px'>"
    "// KARNATAKA FARM STRESS INTELLIGENCE & GAME SYSTEM — ML EDITION //</p>",
    unsafe_allow_html=True
)

# ── Music Controls ───────────────────────────────────────
mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns([1,1,1,1,4])
with mcol1:
    if st.button("🎵 PLAY"):
        st.session_state.music_on = True
        st.markdown("<script>AgriMusic.startMusic('peace');</script>", unsafe_allow_html=True)
with mcol2:
    if st.button("⏹ STOP"):
        st.session_state.music_on = False
        st.markdown("<script>AgriMusic.stopMusic();</script>", unsafe_allow_html=True)
with mcol3:
    if st.button("⚡ TENSE"):
        st.markdown("<script>AgriMusic.switchMelody('tense');</script>", unsafe_allow_html=True)
with mcol4:
    if st.button("☮ PEACE"):
        st.markdown("<script>AgriMusic.switchMelody('peace');</script>", unsafe_allow_html=True)
with mcol5:
    st.markdown(
        "<small style='color:rgba(0,255,136,0.4)'>🎮 Press PLAY for 8-bit game music | "
        "TENSE = high stress theme | PEACE = happy farm theme</small>",
        unsafe_allow_html=True
    )

st.divider()

# ── Dataset Loading ──────────────────────────────────────
with st.expander("📂 DATA UPLOAD — Click to load your own dataset (optional)", expanded=False):
    st.markdown("""
    **Default:** Built-in 750-sample Karnataka dataset (synthetic, realistic baselines).
    Upload your own `.xlsx` or `.csv` to override with real data.

    **Required columns:** `Region, Crop, Rainfall, Price, Cost, Yield, Irrigation`
    *(All numeric columns must be normalised between 0.0 and 1.0)*
    """)
    uploaded = st.file_uploader("Upload Excel or CSV file", type=["xlsx", "csv"])

# Priority: uploaded file → local file → generated dataset
if uploaded:
    try:
        df_raw = (pd.read_excel(uploaded)
                  if uploaded.name.endswith("xlsx")
                  else pd.read_csv(uploaded))
        st.success(f"✅ Loaded {len(df_raw)} rows from uploaded file!")
    except Exception as e:
        st.error(f"❌ Could not read file: {e}")
        df_raw = None
elif os.path.exists("karnataka_dataset_750_samples.xlsx"):
    @st.cache_data
    def load_excel():
        return pd.read_excel("karnataka_dataset_750_samples.xlsx")
    df_raw = load_excel()
else:
    df_raw = generate_dataset()

if df_raw is None:
    st.stop()

# ── Sidebar Filters ──────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='font-size:0.9rem'>🎛 FILTERS</h2>", unsafe_allow_html=True)

    crops_available = sorted(df_raw["Crop"].unique())
    selected_crops = st.multiselect(
        "🌾 Filter by Crop",
        options=crops_available,
        default=crops_available,
        help="Select which crops to include in the analysis"
    )
    # Default to all crops if none selected
    if not selected_crops:
        selected_crops = crops_available

    st.divider()
    st.markdown("""
    <div style='font-family:Share Tech Mono,monospace;font-size:0.7rem;
    color:rgba(0,255,136,0.4);line-height:1.8'>
    📐 FSI FORMULA:<br>
    (1-Rain)×0.25<br>
    +(1-Price)×0.25<br>
    +(1-Yield)×0.20<br>
    +Cost×0.20<br>
    +(1-Irrig)×0.10<br><br>
    Range: 0 (best) → 1 (worst)
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown(f"""
    <div style='font-family:Share Tech Mono,monospace;font-size:0.7rem;color:rgba(0,255,136,0.5)'>
    🏆 SCORE: {st.session_state.score}<br>
    ⭐ LEVEL: {st.session_state.level}<br>
    📊 SAMPLES: {len(df_raw)}
    </div>
    """, unsafe_allow_html=True)

# ── Data Processing Pipeline ─────────────────────────────
# Filter → FSI → Aggregate → ML
df_filtered = df_raw[df_raw["Crop"].isin(selected_crops)].copy()
df_filtered = compute_fsi(df_filtered)           # Compute FSI for every farm record
hex_df, p33, p66 = aggregate(df_filtered)        # Aggregate to district level

# Run both ML models on aggregated district data
ml_df, kmeans_model, scaler_model = run_kmeans_clustering(hex_df)
regression_results = run_regression(df_filtered)  # Regression on full farm-level data

# ── Top-Level Metrics ────────────────────────────────────
total_districts = len(hex_df)
high_count  = (hex_df["Stress"] == "HIGH").sum()
med_count   = (hex_df["Stress"] == "MEDIUM").sum()
low_count   = (hex_df["Stress"] == "LOW").sum()
avg_fsi     = hex_df["FSI"].mean()
worst_dist  = hex_df.loc[hex_df["FSI"].idxmax(), "Region"]

mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
mc1.metric("📍 Districts",     total_districts)
mc2.metric("🔴 HIGH Stress",   high_count,
           delta=f"{high_count/total_districts*100:.0f}% of total", delta_color="inverse")
mc3.metric("🟡 MEDIUM Stress", med_count)
mc4.metric("🟢 LOW Stress",    low_count,
           delta=f"{low_count/total_districts*100:.0f}% of total")
mc5.metric("⚡ Avg FSI",       f"{avg_fsi:.3f}")
mc6.metric("🔥 Worst Region",  worst_dist)

st.divider()

# ── Tab Layout ───────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📡 STRESS HEATMAP",
    "🎮 FARMER SIMULATOR",
    "📊 ANALYTICS & ML",
    "🚨 ALERT SYSTEM"
])

# ════════════════════════════════════════════════════════
# TAB 1 — INTERACTIVE STRESS HEATMAP
# ════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 🗺 FSI HEATMAP — KARNATAKA DISTRICTS")

    with st.expander("❓ How to read this map", expanded=False):
        st.markdown("""
        **Each circle represents one Karnataka district.**

        🟢 **GREEN** = LOW stress — good conditions
        🟡 **YELLOW** = MEDIUM stress — needs monitoring
        🔴 **RED** = HIGH stress — immediate intervention needed

        **Larger circle = higher FSI (more stress)**

        Hover over any district to see its full breakdown: FSI score,
        stress classification, root cause, and all 5 parameter values.
        """)

    mapcol1, mapcol2 = st.columns([3, 1])
    with mapcol2:
        zoom_level = st.slider("🔍 Map Zoom", min_value=5, max_value=9, value=6)

    st.plotly_chart(build_map(hex_df, zoom=zoom_level), use_container_width=True)

    # District deep-dive inspector
    st.markdown("### 🎯 DISTRICT INSPECTOR")
    d_col1, d_col2 = st.columns([2, 1])

    with d_col1:
        selected_district = st.selectbox(
            "🔍 Select District",
            options=sorted(hex_df["Region"].unique())
        )
        sel = hex_df[hex_df["Region"] == selected_district].iloc[0]
        stress_cls  = {"HIGH":"glow-red","MEDIUM":"glow-yellow","LOW":"glow-lime"}[sel["Stress"]]
        stress_icon = {"HIGH":"🔴","MEDIUM":"🟡","LOW":"🟢"}[sel["Stress"]]

        # Also show ML cluster label for this district
        ml_row   = ml_df[ml_df["Region"] == selected_district].iloc[0]
        ml_label = ml_row["ML_Stress"]
        ml_match = "✅ Agrees with ML" if sel["Stress"] == ml_label else f"⚠️ ML says: {ml_label}"

        st.markdown(f"""
        <div class='game-card'>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px'>
                <div><span style='color:rgba(0,255,136,0.5);font-size:0.75rem'>📍 REGION</span>
                     <div style='font-family:Orbitron,monospace;font-weight:700'>{sel['Region']}</div></div>
                <div><span style='color:rgba(0,255,136,0.5);font-size:0.75rem'>⚡ FSI SCORE</span>
                     <div class='fsi-big' style='font-size:1.8rem'>{sel['FSI']:.4f}</div></div>
                <div><span style='color:rgba(0,255,136,0.5);font-size:0.75rem'>🚨 STRESS LEVEL</span>
                     <div class='{stress_cls}' style='font-family:Orbitron,monospace;font-weight:700;font-size:1.1rem'>{stress_icon} {sel['Stress']}</div></div>
                <div><span style='color:rgba(0,255,136,0.5);font-size:0.75rem'>🤖 ML VERDICT</span>
                     <div style='font-size:0.82rem;color:#39ff14'>{ml_match}</div></div>
                <div><span style='color:rgba(0,255,136,0.5);font-size:0.75rem'>🧠 ROOT CAUSE</span>
                     <div style='font-size:0.85rem'>{sel['Reason']}</div></div>
            </div>
            <hr/>
            <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;text-align:center'>
                <div><div style='color:rgba(0,255,136,0.5);font-size:0.7rem'>🌧 RAINFALL</div>
                     <div style='font-family:Share Tech Mono,monospace;font-size:1.1rem'>{sel['Rainfall']:.2f}</div>
                     <div style='font-size:0.7rem;color:rgba(0,255,136,0.4)'>{'✅ Good' if sel['Rainfall']>=0.4 else '⚠️ Low'}</div></div>
                <div><div style='color:rgba(0,255,136,0.5);font-size:0.7rem'>💰 PRICE</div>
                     <div style='font-family:Share Tech Mono,monospace;font-size:1.1rem'>{sel['Price']:.2f}</div>
                     <div style='font-size:0.7rem;color:rgba(0,255,136,0.4)'>{'✅ Good' if sel['Price']>=0.4 else '⚠️ Low'}</div></div>
                <div><div style='color:rgba(0,255,136,0.5);font-size:0.7rem'>🌿 YIELD</div>
                     <div style='font-family:Share Tech Mono,monospace;font-size:1.1rem'>{sel['Yield']:.2f}</div>
                     <div style='font-size:0.7rem;color:rgba(0,255,136,0.4)'>{'✅ Good' if sel['Yield']>=0.4 else '⚠️ Low'}</div></div>
                <div><div style='color:rgba(0,255,136,0.5);font-size:0.7rem'>📦 COST</div>
                     <div style='font-family:Share Tech Mono,monospace;font-size:1.1rem'>{sel['Cost']:.2f}</div>
                     <div style='font-size:0.7rem;color:rgba(0,255,136,0.4)'>{'⚠️ High' if sel['Cost']>0.6 else '✅ OK'}</div></div>
                <div><div style='color:rgba(0,255,136,0.5);font-size:0.7rem'>💧 IRRIGATION</div>
                     <div style='font-family:Share Tech Mono,monospace;font-size:1.1rem'>{sel['Irrigation']:.2f}</div>
                     <div style='font-size:0.7rem;color:rgba(0,255,136,0.4)'>{'✅ Good' if sel['Irrigation']>=0.4 else '⚠️ Poor'}</div></div>
                <div><div style='color:rgba(0,255,136,0.5);font-size:0.7rem'>📊 SAMPLES</div>
                     <div style='font-family:Share Tech Mono,monospace;font-size:1.1rem'>{int(sel['Samples'])}</div>
                     <div style='font-size:0.7rem;color:rgba(0,255,136,0.4)'>farm records</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with d_col2:
        st.markdown("### 🏆 TOP 5 HOTSPOTS")
        st.markdown("<small>Districts with highest farm stress</small>", unsafe_allow_html=True)
        top5 = hex_df.nlargest(5, "FSI")
        for i, (_, row) in enumerate(top5.iterrows()):
            rank_colors = ["#ff2244","#ff4400","#ff6600","#ff8800","#ffaa00"]
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:8px;padding:7px 10px;
                 margin-bottom:5px;border:1px solid rgba(255,34,68,0.25);
                 border-left:3px solid {rank_colors[i]};
                 background:rgba(255,34,68,0.04);border-radius:4px'>
                <span style='font-family:Orbitron,monospace;font-size:0.65rem;
                      color:rgba(255,136,0,0.7);width:18px'>#{i+1}</span>
                <span style='flex:1;font-weight:700;font-size:0.85rem'>{row['Region']}</span>
                <span style='font-family:Share Tech Mono,monospace;
                      color:{rank_colors[i]};font-size:0.82rem'>{row['FSI']:.3f}</span>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB 2 — FARMER SIMULATOR GAME
# ════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🎮 RAMU'S FARM SIMULATOR")

    with st.expander("🕹️ HOW TO PLAY", expanded=True):
        st.markdown("""
        **Help farmer Ramu achieve a HAPPY farm!** 🌾

        | Parameter | Good value | Bad value |
        |-----------|------------|-----------|
        | 🌧 **Rainfall** | HIGH (80+) | LOW (below 40) |
        | 💰 **Crop Price** | HIGH (80+) | LOW (below 40) |
        | 🌿 **Crop Yield** | HIGH (80+) | LOW (below 40) |
        | 📦 **Input Cost** | LOW (below 20) | HIGH (above 60) |
        | 💧 **Irrigation** | HIGH (80+) | LOW (below 40) |

        Keep FSI below 0.30 to earn XP. Unlock all 7 achievements to become an Avenger Elite!
        """)

    gc1, gc2, gc3 = st.columns([2.2, 1.8, 2])

    with gc1:
        st.markdown("**⚙️ ENVIRONMENT CONTROLS**")
        rain  = st.slider("🌧 Rainfall Level",     0, 100, 50, key="g_rain")
        price = st.slider("💰 Crop Market Price",  0, 100, 50, key="g_price")
        yld   = st.slider("🌿 Crop Yield",         0, 100, 50, key="g_yield")
        cost  = st.slider("📦 Input Cost",         0, 100, 50, key="g_cost")
        irrig = st.slider("💧 Irrigation Access",  0, 100, 50, key="g_irrig")

        st.divider()
        st.markdown("**🌦 SEASON PRESETS**")
        ps1, ps2, ps3, ps4 = st.columns(4)
        with ps1:
            if st.button("🌧\nMonsoon"): st.session_state.preset = "monsoon"; st.rerun()
        with ps2:
            if st.button("☀️\nDry"):    st.session_state.preset = "dry";     st.rerun()
        with ps3:
            if st.button("🌾\nKharif"): st.session_state.preset = "kharif";  st.rerun()
        with ps4:
            if st.button("🏆\nIdeal"):  st.session_state.preset = "ideal";   st.rerun()

    # Override slider values with preset values if a preset is active
    if   st.session_state.preset == "monsoon": rain,price,yld,cost,irrig = 85,55,72,42,80
    elif st.session_state.preset == "dry":     rain,price,yld,cost,irrig = 15,45,28,58,22
    elif st.session_state.preset == "kharif":  rain,price,yld,cost,irrig = 68,62,65,48,60
    elif st.session_state.preset == "ideal":   rain,price,yld,cost,irrig = 92,88,90,12,88

    # Compute FSI from current slider/preset values
    g_fsi = round(compute_game_fsi(rain, price, yld, cost, irrig), 4)

    # Award XP for maintaining low FSI
    if g_fsi < 0.30:
        st.session_state.score = min(9999, st.session_state.score + (15 if g_fsi < 0.15 else 5))
        st.session_state.xp    = min(100,  st.session_state.xp + 3)

    # Level up when XP bar fills
    if st.session_state.xp >= 100:
        st.session_state.xp = 0
        st.session_state.level += 1
        st.markdown(f"<div class='ach-banner'>🎊 LEVEL UP! YOU ARE NOW LEVEL {st.session_state.level}! 🎊</div>",
                    unsafe_allow_html=True)
        st.markdown("<script>AgriMusic.playSFX('win');</script>", unsafe_allow_html=True)

    # Check and display newly unlocked achievements
    new_achs = check_achievements(rain, price, yld, cost, irrig, g_fsi)
    for ach in new_achs:
        icon, color, desc = ACH_META[ach]
        st.markdown(f"""
        <div class='ach-banner' style='border-color:{color}'>
            <div style='font-size:2rem'>{icon}</div>
            <div style='color:{color};font-size:1rem'>ACHIEVEMENT UNLOCKED: {ach}</div>
            <div style='color:rgba(0,255,136,0.5);font-size:0.8rem'>{desc}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<script>AgriMusic.playSFX('win');</script>", unsafe_allow_html=True)

    with gc2:
        emoji, anim_cls, status_txt, message, st_color = farmer_state(g_fsi)
        mood_pct  = max(0, min(100, int((1 - g_fsi) * 100)))
        m_color   = mood_color(mood_pct)
        fsi_color = "#ff2244" if g_fsi > 0.66 else "#ffea00" if g_fsi > 0.33 else "#39ff14"
        fsi_glow  = f"0 0 25px {fsi_color}"

        # Trigger audio SFX on stress threshold crossings
        if g_fsi > 0.70 and st.session_state.last_fsi <= 0.70:
            st.markdown("<script>AgriMusic.playSFX('alert');</script>", unsafe_allow_html=True)
        elif g_fsi < 0.20 and st.session_state.last_fsi >= 0.20:
            st.markdown("<script>AgriMusic.playSFX('win');</script>", unsafe_allow_html=True)
        st.session_state.last_fsi = g_fsi

        score_str  = str(st.session_state.score).zfill(4)
        xp_val     = st.session_state.xp
        lvl_val    = st.session_state.level
        stress_lbl = ("&#128308; HIGH STRESS" if g_fsi >= 0.62
                      else "&#128993; MEDIUM STRESS" if g_fsi >= 0.38
                      else "&#128994; LOW STRESS")

        farmer_html = (
            "<div class='farmer-box'>"
            f"<div style='font-family:Orbitron,monospace;font-size:0.62rem;color:rgba(0,255,136,0.5);letter-spacing:0.2em'>FARMER XP</div>"
            f"<div style='font-family:Orbitron,monospace;font-size:2rem;font-weight:900;color:#39ff14;filter:drop-shadow(0 0 12px rgba(57,255,20,0.6))'>{score_str}</div>"
            f"<div style='font-family:Share Tech Mono,monospace;font-size:0.7rem;color:rgba(0,255,136,0.4)'>LEVEL {lvl_val}</div>"
            f"<div class='xp-track' style='margin:6px 0'><div class='xp-fill' style='width:{xp_val}%'></div></div>"
            f"<div style='font-size:0.62rem;color:rgba(0,255,136,0.3);font-family:Share Tech Mono,monospace;margin-bottom:12px'>XP {xp_val}/100</div>"
            f"<span class='farmer-emoji {anim_cls}' style='font-size:5rem;display:block;line-height:1.2'>{emoji}</span>"
            f"<div style='font-family:Orbitron,monospace;font-size:0.72rem;font-weight:700;color:#00ff88;letter-spacing:0.1em;margin:8px 0 4px'>RAMU &#8212; KARNATAKA FARMER</div>"
            f"<div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;color:rgba(0,255,136,0.4);text-align:left;margin-bottom:3px'>HAPPINESS METER {mood_pct}%</div>"
            f"<div class='mood-track'><div class='mood-fill-inner' style='width:{mood_pct}%;background:{m_color}'></div></div>"
            f"<div style='font-family:Orbitron,monospace;font-size:0.8rem;font-weight:700;color:{st_color};margin:10px 0 4px;text-shadow:0 0 10px {st_color}'>{status_txt}</div>"
            f"<div style='font-size:0.78rem;color:rgba(0,255,136,0.55);font-style:italic;line-height:1.4;min-height:44px'>{message}</div>"
            f"<div style='background:rgba(0,0,0,0.4);border:1px solid rgba(0,255,136,0.2);border-radius:6px;padding:10px;margin-top:12px'>"
            f"<div class='fsi-big' style='color:{fsi_color};text-shadow:{fsi_glow}'>{g_fsi:.3f}</div>"
            f"<div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;color:rgba(0,255,136,0.4);letter-spacing:0.2em'>FARM STRESS INDEX</div>"
            f"<div style='font-size:0.72rem;margin-top:4px;color:{fsi_color}'>{stress_lbl}</div>"
            f"</div></div>"
        )
        st.markdown(farmer_html, unsafe_allow_html=True)

    with gc3:
        st.markdown("**🏅 ACHIEVEMENTS**")
        for ach_name, (icon, color, desc) in ACH_META.items():
            unlocked     = st.session_state.achievements[ach_name]
            opacity      = "1" if unlocked else "0.3"
            border_style = f"2px solid {color}" if unlocked else f"1px solid {color}55"
            glow         = f"box-shadow:0 0 12px {color}66;" if unlocked else ""
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;padding:7px 10px;
                 border-radius:6px;border:{border_style};background:rgba(0,20,5,0.6);
                 margin-bottom:5px;opacity:{opacity};{glow}transition:all 0.3s'>
                <span style='font-size:1.2rem'>{icon}</span>
                <div>
                    <div style='font-weight:700;font-size:0.85rem;color:{color}'>{ach_name}</div>
                    <div style='font-size:0.68rem;color:rgba(0,255,136,0.4)'>{desc}</div>
                </div>
                <span style='margin-left:auto;font-size:0.7rem'>{'✅' if unlocked else '🔒'}</span>
            </div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown("**💡 WHAT'S STRESSING RAMU?**")
        drivers = []
        if rain  < 40: drivers.append(("🌧","Increase Rainfall","#00ccff"))
        if price < 40: drivers.append(("💰","Raise Crop Price","#ffea00"))
        if yld   < 40: drivers.append(("🌿","Improve Yield","#39ff14"))
        if cost  > 60: drivers.append(("📦","Reduce Input Cost","#ff6600"))
        if irrig < 40: drivers.append(("💧","Improve Irrigation","#00eeff"))
        if drivers:
            for icon, tip, color in drivers:
                st.markdown(f"""
                <div style='padding:5px 10px;border:1px solid {color}44;
                     border-left:3px solid {color};border-radius:4px;
                     margin-bottom:4px;font-size:0.82rem;color:{color}'>{icon} Fix: {tip}</div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='padding:10px;border:1px solid rgba(57,255,20,0.27);border-radius:6px;
                 text-align:center;color:#39ff14;font-weight:700'>
                ✅ ALL PARAMETERS HEALTHY!<br>
                <span style='font-size:0.75rem;opacity:0.6'>Ramu is thriving!</span>
            </div>""", unsafe_allow_html=True)

    st.divider()
    rcol1, rcol2, _ = st.columns([1,1,4])
    with rcol1:
        if st.button("🔄 RESET SCORE"):
            st.session_state.score = 0; st.session_state.xp = 0; st.session_state.level = 1
            st.session_state.achievements = {k: False for k in st.session_state.achievements}
            st.session_state.preset = None; st.rerun()
    with rcol2:
        if st.button("🗑 CLEAR PRESET"):
            st.session_state.preset = None; st.rerun()

# ════════════════════════════════════════════════════════
# TAB 3 — ANALYTICS & ML
# Combines standard analytics charts with two ML sections:
#   Section A: KMeans unsupervised clustering
#   Section B: Linear Regression with feature importance
# ════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📊 STRESS ANALYTICS DASHBOARD")

    # ── Standard charts ──────────────────────────────────
    ac1, ac2 = st.columns(2)

    with ac1:
        # Bar chart: count of districts per stress category
        stress_counts = hex_df["Stress"].value_counts().reindex(["HIGH","MEDIUM","LOW"]).fillna(0)
        fig_bar = go.Figure(go.Bar(
            x=stress_counts.index, y=stress_counts.values,
            marker_color=["#ff2244","#ffea00","#39ff14"],
            text=stress_counts.values.astype(int), textposition="outside",
            textfont=dict(color="#00ff88", family="Share Tech Mono"),
        ))
        fig_bar.update_layout(
            title=dict(text="Districts by Stress Category", font=dict(color="#39ff14",family="Orbitron",size=13)),
            xaxis=dict(tickfont=dict(color="#00ff88",family="Share Tech Mono")),
            yaxis=dict(tickfont=dict(color="#00ff88",family="Share Tech Mono"),gridcolor="rgba(0,255,136,0.08)"),
            paper_bgcolor="rgba(0,13,2,0.0)", plot_bgcolor="rgba(0,13,2,0.6)",
            font=dict(color="#00ff88"), height=300, margin=dict(t=40,b=20,l=30,r=20), showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with ac2:
        # Horizontal bar: average FSI per crop type
        crop_fsi = df_filtered.groupby("Crop")["FSI"].mean().sort_values(ascending=False)
        fig_crop = go.Figure(go.Bar(
            y=crop_fsi.index, x=crop_fsi.values, orientation="h",
            marker_color=crop_fsi.values, marker_colorscale="RdYlGn", marker_reversescale=True,
            text=[f"{v:.3f}" for v in crop_fsi.values], textposition="outside",
            textfont=dict(color="#00ff88", family="Share Tech Mono"),
        ))
        fig_crop.update_layout(
            title=dict(text="Average FSI by Crop Type", font=dict(color="#39ff14",family="Orbitron",size=13)),
            xaxis=dict(tickfont=dict(color="#00ff88",family="Share Tech Mono"),gridcolor="rgba(0,255,136,0.08)"),
            yaxis=dict(tickfont=dict(color="#00ff88",family="Share Tech Mono")),
            paper_bgcolor="rgba(0,13,2,0.0)", plot_bgcolor="rgba(0,13,2,0.6)",
            font=dict(color="#00ff88"), height=300, margin=dict(t=40,b=20,l=30,r=20), showlegend=False
        )
        st.plotly_chart(fig_crop, use_container_width=True)

    # Full ranking table
    st.markdown("### 🔥 DISTRICT STRESS RANKING")
    sorted_df = hex_df.sort_values("FSI", ascending=False)
    for i, (_, row) in enumerate(sorted_df.iterrows()):
        s       = row["Stress"]
        icon    = {"HIGH":"🔴","MEDIUM":"🟡","LOW":"🟢"}[s]
        color   = {"HIGH":"#ff2244","MEDIUM":"#ffea00","LOW":"#39ff14"}[s]
        rank_bg = ("rgba(255,34,68,0.05)" if s=="HIGH" else
                   "rgba(255,234,0,0.03)"  if s=="MEDIUM" else
                   "rgba(57,255,20,0.03)")
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:12px;padding:7px 12px;
             margin-bottom:3px;border:1px solid {color}22;border-left:3px solid {color};
             border-radius:4px;background:{rank_bg}'>
            <span style='font-family:Orbitron,monospace;font-size:0.65rem;color:rgba(255,136,0,0.6);width:22px'>#{i+1}</span>
            <span style='font-weight:700;font-size:0.88rem;flex:1'>{row['Region']}</span>
            <span style='font-size:0.75rem;color:rgba(0,255,136,0.5);flex:1'>{row['Reason']}</span>
            <span style='font-family:Share Tech Mono,monospace;font-size:0.8rem;color:{color}'>FSI {row['FSI']:.3f}</span>
            <span style='width:70px;text-align:right;font-size:0.75rem;color:{color}'>{icon} {s}</span>
        </div>""", unsafe_allow_html=True)

    # Radar chart
    st.markdown("### 📡 PARAMETER AVERAGES BY STRESS LEVEL")
    RADAR_FILL = {
        "HIGH":   ("rgba(255,34,68,1)","rgba(255,34,68,0.12)"),
        "MEDIUM": ("rgba(255,234,0,1)","rgba(255,234,0,0.12)"),
        "LOW":    ("rgba(57,255,20,1)","rgba(57,255,20,0.12)"),
    }
    params    = ["Rainfall","Price","Yield","Irrigation"]
    fig_radar = go.Figure()
    for stress_lvl in ["HIGH","MEDIUM","LOW"]:
        line_c, fill_c = RADAR_FILL[stress_lvl]
        subset = hex_df[hex_df["Stress"] == stress_lvl]
        if len(subset) > 0:
            means = [subset[p].mean() for p in params]
            fig_radar.add_trace(go.Scatterpolar(
                r=means+[means[0]], theta=params+[params[0]],
                fill="toself", name=stress_lvl,
                line_color=line_c, fillcolor=fill_c,
            ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True,range=[0,1],gridcolor="rgba(0,255,136,0.15)",
                           tickfont=dict(color="rgba(0,255,136,0.5)",size=9)),
            angularaxis=dict(tickfont=dict(color="#00ff88",family="Rajdhani",size=11)),
            bgcolor="rgba(0,13,2,0.6)"
        ),
        showlegend=True, height=380, paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#00ff88"),
        legend=dict(font=dict(color="#00ff88"),bgcolor="rgba(0,13,2,0.8)",
                   bordercolor="rgba(0,255,136,0.3)",borderwidth=1),
        title=dict(text="Average Parameters by Stress Level",font=dict(color="#39ff14",family="Orbitron",size=12))
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.divider()

    # ════════════════════════════════════════════════════
    # ML SECTION A — KMeans UNSUPERVISED CLUSTERING
    # ════════════════════════════════════════════════════
    st.markdown("### 🤖 ML MODULE A — KMeans UNSUPERVISED CLUSTERING")
    st.markdown(
        "<small>Scikit-learn KMeans groups districts by farm parameter similarity "
        "without using any predefined stress labels. "
        "Features are standardised before clustering.</small>",
        unsafe_allow_html=True
    )

    mla1, mla2 = st.columns(2)

    with mla1:
        # KMeans cluster distribution bar
        ml_counts  = ml_df["ML_Stress"].value_counts().reindex(["HIGH","MEDIUM","LOW"]).fillna(0)
        fig_ml_bar = go.Figure(go.Bar(
            x=ml_counts.index, y=ml_counts.values,
            marker_color=["#ff2244","#ffea00","#39ff14"],
            text=ml_counts.values.astype(int), textposition="outside",
            textfont=dict(color="#00ff88", family="Share Tech Mono"),
        ))
        fig_ml_bar.update_layout(
            title=dict(text="🤖 KMeans Cluster Distribution", font=dict(color="#39ff14",family="Orbitron",size=13)),
            xaxis=dict(tickfont=dict(color="#00ff88",family="Share Tech Mono")),
            yaxis=dict(tickfont=dict(color="#00ff88",family="Share Tech Mono"),gridcolor="rgba(0,255,136,0.08)"),
            paper_bgcolor="rgba(0,13,2,0.0)", plot_bgcolor="rgba(0,13,2,0.6)",
            font=dict(color="#00ff88"), height=300, margin=dict(t=40,b=20,l=30,r=20), showlegend=False
        )
        st.plotly_chart(fig_ml_bar, use_container_width=True)

    with mla2:
        # Scatter: FSI vs Rainfall coloured by ML cluster
        cl_colors  = {"HIGH":"#ff2244","MEDIUM":"#ffea00","LOW":"#39ff14"}
        fig_scatter = go.Figure()
        for cl in ["HIGH","MEDIUM","LOW"]:
            sub = ml_df[ml_df["ML_Stress"] == cl]
            fig_scatter.add_trace(go.Scatter(
                x=sub["Rainfall"], y=sub["FSI"],
                mode="markers+text",
                marker=dict(size=10, color=cl_colors[cl], opacity=0.85,
                            line=dict(color="rgba(0,255,136,0.3)",width=1)),
                text=sub["Region"], textposition="top center",
                textfont=dict(size=7, color=cl_colors[cl]),
                name=f"Cluster: {cl}",
            ))
        fig_scatter.update_layout(
            title=dict(text="FSI vs Rainfall — ML Clusters", font=dict(color="#39ff14",family="Orbitron",size=13)),
            xaxis=dict(title="Rainfall",tickfont=dict(color="#00ff88"),gridcolor="rgba(0,255,136,0.08)"),
            yaxis=dict(title="FSI",tickfont=dict(color="#00ff88"),gridcolor="rgba(0,255,136,0.08)"),
            paper_bgcolor="rgba(0,13,2,0.0)", plot_bgcolor="rgba(0,13,2,0.6)",
            font=dict(color="#00ff88"), height=300, margin=dict(t=40,b=20,l=40,r=20),
            legend=dict(font=dict(color="#00ff88"),bgcolor="rgba(0,13,2,0.8)")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # FSI vs ML cluster agreement table
    agree_count = (ml_df["Stress"] == ml_df["ML_Stress"]).sum()
    agree_pct   = agree_count / len(ml_df) * 100
    st.markdown(f"""
    <div class='game-card' style='text-align:center;padding:14px;margin-bottom:12px'>
        <span style='font-family:Orbitron,monospace;font-size:1.8rem;font-weight:900;
        color:#39ff14;text-shadow:0 0 15px rgba(57,255,20,0.6)'>{agree_pct:.0f}%</span>
        <div style='color:rgba(0,255,136,0.5);font-size:0.8rem;margin-top:4px'>
        Agreement between rule-based FSI labels and KMeans ML clusters
        ({agree_count} of {len(ml_df)} districts match)</div>
    </div>
    """, unsafe_allow_html=True)

    for _, row in ml_df[["Region","Stress","ML_Stress","FSI"]].sort_values("FSI",ascending=False).iterrows():
        match      = row["Stress"] == row["ML_Stress"]
        match_icon = "✅" if match else "⚠️"
        color      = "#39ff14" if match else "#ffea00"
        lbl_colors = {"HIGH":"#ff2244","MEDIUM":"#ffea00","LOW":"#39ff14"}
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:12px;padding:5px 12px;
             margin-bottom:2px;border:1px solid {color}22;border-radius:4px;background:rgba(0,20,5,0.5)'>
            <span style='flex:1;font-size:0.85rem;font-weight:700'>{row['Region']}</span>
            <span style='font-size:0.75rem;color:rgba(0,255,136,0.5)'>FSI {row['FSI']:.3f}</span>
            <span style='font-size:0.75rem;color:#aaa'>Rule: <b style='color:{lbl_colors[row["Stress"]]}'>{row['Stress']}</b></span>
            <span style='font-size:0.75rem;color:#aaa'>ML: <b style='color:{lbl_colors[row["ML_Stress"]]}'>{row['ML_Stress']}</b></span>
            <span style='font-size:0.85rem'>{match_icon}</span>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ════════════════════════════════════════════════════
    # ML SECTION B — LINEAR REGRESSION (FSI PREDICTION)
    # ════════════════════════════════════════════════════
    st.markdown("### 📈 ML MODULE B — LINEAR REGRESSION (FSI PREDICTION)")
    st.markdown(
        "<small>Supervised learning: predicts FSI from farm parameters. "
        "Trained on 80% of data, evaluated on 20% held-out test set. "
        "Coefficients reveal which parameters most drive farm stress.</small>",
        unsafe_allow_html=True
    )

    r   = regression_results
    mlb1, mlb2, mlb3 = st.columns(3)
    mlb1.metric("📐 R² Score",  f"{r['r2']:.4f}",  help="1.0 = perfect prediction")
    mlb2.metric("📉 RMSE",      f"{r['rmse']:.4f}", help="Lower = better fit")
    mlb3.metric("🧪 Test Size", f"{len(r['y_test'])} samples")

    mlbc1, mlbc2 = st.columns(2)

    with mlbc1:
        # Feature coefficient bar chart
        coef_df     = r["coef_df"]
        coef_colors = ["#ff2244" if c > 0 else "#39ff14" for c in coef_df["Coefficient"]]
        fig_coef    = go.Figure(go.Bar(
            x=coef_df["Feature"], y=coef_df["Coefficient"],
            marker_color=coef_colors,
            text=[f"{v:+.3f}" for v in coef_df["Coefficient"]],
            textposition="outside",
            textfont=dict(color="#00ff88", family="Share Tech Mono"),
        ))
        fig_coef.update_layout(
            title=dict(text="Feature Coefficients (impact on FSI)",
                       font=dict(color="#39ff14",family="Orbitron",size=12)),
            xaxis=dict(tickfont=dict(color="#00ff88",family="Share Tech Mono")),
            yaxis=dict(tickfont=dict(color="#00ff88",family="Share Tech Mono"),
                       gridcolor="rgba(0,255,136,0.08)", zeroline=True,
                       zerolinecolor="rgba(0,255,136,0.3)"),
            paper_bgcolor="rgba(0,13,2,0.0)", plot_bgcolor="rgba(0,13,2,0.6)",
            font=dict(color="#00ff88"), height=320, margin=dict(t=40,b=30,l=40,r=20),
            showlegend=False
        )
        st.plotly_chart(fig_coef, use_container_width=True)
        st.markdown(
            "<small>🔴 Positive coefficient = increases stress &nbsp;|&nbsp; "
            "🟢 Negative coefficient = reduces stress</small>",
            unsafe_allow_html=True
        )

    with mlbc2:
        # Scatter: actual vs predicted FSI
        fig_pred = go.Figure()
        # Perfect prediction line
        min_val, max_val = float(r["y_test"].min()), float(r["y_test"].max())
        fig_pred.add_trace(go.Scatter(
            x=[min_val, max_val], y=[min_val, max_val],
            mode="lines", name="Perfect Fit",
            line=dict(color="rgba(0,255,136,0.4)", dash="dash", width=1)
        ))
        # Actual vs predicted scatter points
        fig_pred.add_trace(go.Scatter(
            x=r["y_test"], y=r["y_pred"],
            mode="markers", name="Predictions",
            marker=dict(size=5, color="#00ff88", opacity=0.6,
                        line=dict(color="rgba(0,255,136,0.2)", width=0.5))
        ))
        fig_pred.update_layout(
            title=dict(text=f"Actual vs Predicted FSI  (R²={r['r2']:.3f})",
                       font=dict(color="#39ff14",family="Orbitron",size=12)),
            xaxis=dict(title="Actual FSI",tickfont=dict(color="#00ff88"),
                       gridcolor="rgba(0,255,136,0.08)"),
            yaxis=dict(title="Predicted FSI",tickfont=dict(color="#00ff88"),
                       gridcolor="rgba(0,255,136,0.08)"),
            paper_bgcolor="rgba(0,13,2,0.0)", plot_bgcolor="rgba(0,13,2,0.6)",
            font=dict(color="#00ff88"), height=320, margin=dict(t=40,b=30,l=50,r=20),
            legend=dict(font=dict(color="#00ff88"),bgcolor="rgba(0,13,2,0.8)")
        )
        st.plotly_chart(fig_pred, use_container_width=True)

    # Interpretation card
    top_feature   = r["coef_df"].iloc[0]["Feature"]
    top_coef      = r["coef_df"].iloc[0]["Coefficient"]
    top_direction = "increases" if top_coef > 0 else "decreases"
    st.markdown(f"""
    <div class='game-card'>
        <div style='font-family:Orbitron,monospace;font-size:0.8rem;color:#39ff14;margin-bottom:8px'>
        🧠 MODEL INTERPRETATION</div>
        <div style='font-size:0.85rem;line-height:1.8;color:rgba(0,255,136,0.8)'>
        • The regression model achieves <b>R² = {r['r2']:.4f}</b> —
          meaning {r['r2']*100:.1f}% of FSI variance is explained by the 5 input features.<br>
        • <b>{top_feature}</b> is the strongest predictor: a unit increase
          {top_direction} FSI by <b>{abs(top_coef):.3f}</b>.<br>
        • The near-perfect R² is expected because FSI is mathematically
          derived from these same parameters — this confirms the formula's integrity.<br>
        • RMSE of <b>{r['rmse']:.4f}</b> indicates very low prediction error on unseen data.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
# TAB 4 — ALERT SYSTEM
# ════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🚨 HIGH STRESS ALERT SYSTEM")

    with st.expander("❓ About this alert system", expanded=False):
        st.markdown("""
        Districts are flagged automatically based on their FSI score.
        **HIGH** stress districts need immediate government intervention.
        Action items are generated per district based on which specific
        parameters are below/above threshold values.
        """)

    high_districts = hex_df[hex_df["Stress"]=="HIGH"].sort_values("FSI", ascending=False)
    med_districts  = hex_df[hex_df["Stress"]=="MEDIUM"].sort_values("FSI", ascending=False)

    if len(high_districts) > 0:
        st.markdown(f"#### 🔴 {len(high_districts)} DISTRICTS IN CRITICAL STRESS")
        for _, row in high_districts.iterrows():
            # Generate targeted action items based on specific parameter failures
            actions = []
            if row["Rainfall"]   < 0.4: actions.append("Provide drought relief & water tankers")
            if row["Price"]      < 0.4: actions.append("Implement Minimum Support Price (MSP)")
            if row["Yield"]      < 0.4: actions.append("Distribute improved seeds & fertilizer")
            if row["Cost"]       > 0.6: actions.append("Provide input subsidies to reduce cost")
            if row["Irrigation"] < 0.4: actions.append("Build irrigation canals / bore wells")

            st.error(f"""
🔴 **{row['Region']}** | FSI = {row['FSI']:.3f} | Root Cause: {row['Reason']}

📋 **Required Actions:**
{chr(10).join(f'  → {a}' for a in actions) if actions else '  → Monitor closely'}
            """)
    else:
        st.success("✅ No districts in CRITICAL stress zone. Great job, Avengers!")

    if len(med_districts) > 0:
        st.markdown(f"#### 🟡 {len(med_districts)} DISTRICTS IN MODERATE STRESS")
        for _, row in med_districts.iterrows():
            st.warning(f"🟡 **{row['Region']}** | FSI = {row['FSI']:.3f} | {row['Reason']}")

    st.divider()

    # Executive Summary
    st.markdown("### 📋 EXECUTIVE SUMMARY")
    high_farms = len(df_filtered[df_filtered["FSI"] > p66])
    st.markdown(f"""
    <div class='game-card'>
        <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:16px;text-align:center'>
            <div>
                <div style='font-size:2rem;font-weight:900;font-family:Orbitron,monospace;
                     color:#ff2244;text-shadow:0 0 12px rgba(255,34,68,0.5)'>{len(high_districts)}</div>
                <div style='color:rgba(0,255,136,0.5);font-size:0.78rem'>CRITICAL DISTRICTS</div>
            </div>
            <div>
                <div style='font-size:2rem;font-weight:900;font-family:Orbitron,monospace;
                     color:#ffea00;text-shadow:0 0 12px rgba(255,234,0,0.5)'>{high_farms}</div>
                <div style='color:rgba(0,255,136,0.5);font-size:0.78rem'>FARM RECORDS AT HIGH RISK</div>
            </div>
            <div>
                <div style='font-size:2rem;font-weight:900;font-family:Orbitron,monospace;
                     color:#39ff14;text-shadow:0 0 12px rgba(57,255,20,0.5)'>{avg_fsi:.3f}</div>
                <div style='color:rgba(0,255,136,0.5);font-size:0.78rem'>STATE AVERAGE FSI</div>
            </div>
        </div>
        <div style='margin-top:14px;font-size:0.82rem;color:rgba(0,255,136,0.5);line-height:1.6'>
            📌 <b>State Stress Level:</b>
            {'🔴 Karnataka farms are facing CRITICAL stress. Immediate policy action required!'
             if avg_fsi > 0.55 else
             '🟡 Karnataka farms face MODERATE stress. Monitor and intervene in red zones.'
             if avg_fsi > 0.40 else
             '🟢 Karnataka farms are in relatively GOOD condition. Continue current practices!'}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center;font-family:Share Tech Mono,monospace;
     font-size:0.7rem;color:rgba(0,255,136,0.25);padding:10px;letter-spacing:0.15em'>
    ⚡ AGRISTRESS AVENGERS v3.0 — ML EDITION |
    KARNATAKA GEOSPATIAL STRESS DETECTION SYSTEM |
    ML: KMeans Clustering + Linear Regression (scikit-learn) |
    750 FARM SAMPLES · 30 DISTRICTS · 15 CROPS 🌾
</div>
""", unsafe_allow_html=True)
