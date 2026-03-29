# =========================================================
# ⚡ AGRISTRESS AVENGERS — ULTIMATE GAME EDITION
# SELF-CONTAINED VERSION (no external file needed)
# Features: Heatmap | Farmer Game | Music | Animations
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import random

# ─────────────────────────────────────────────────────────
# PAGE CONFIG — Must be the VERY FIRST Streamlit command
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚡ AgriStress Avengers",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────
# MUSIC — Base64 encoded tiny 8-bit loops via HTML audio
# We embed a Web Audio API synthesizer so no file needed
# ─────────────────────────────────────────────────────────
MUSIC_JS = """
<script>
// ── WEB AUDIO SYNTH (no external files needed) ──────────
let audioCtx = null;
let musicNodes = [];
let musicPlaying = false;
let musicInterval = null;

// Chiptune note frequencies (Hz)
const NOTES = {
  C4:261.63, D4:293.66, E4:329.63, F4:349.23,
  G4:392.00, A4:440.00, B4:493.88, C5:523.25,
  D5:587.33, E5:659.25, G5:783.99
};

// Two melodies: peaceful (low stress) and tense (high stress)
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
  // Bass every 4 notes
  if (noteIdx % 4 === 0) {
    playNote(NOTES['C4'] / 2, 0.4, 'sine', 0.06);
  }
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

// Play a reward sound effect
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

// Expose to global so Streamlit buttons can call them
window.AgriMusic = { startMusic, stopMusic, switchMelody, playSFX };
</script>
"""

# ─────────────────────────────────────────────────────────
# FULL CSS — Neon game UI (matches original screenshot)
# ─────────────────────────────────────────────────────────
GAME_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');

/* ── Global ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: radial-gradient(ellipse at 10% 0%, #001a08 0%, #000d02 55%, #000000 100%) !important;
    color: #00ff88 !important;
}

/* Scanline overlay */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background: repeating-linear-gradient(0deg, transparent, transparent 2px,
        rgba(0,255,136,0.012) 2px, rgba(0,255,136,0.012) 4px);
}

/* Grid bg */
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image:
        linear-gradient(rgba(0,255,136,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,136,0.03) 1px, transparent 1px);
    background-size: 60px 60px;
}

/* ── Title ── */
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

/* ── Cards / Containers ── */
[data-testid="stVerticalBlock"] > div > div {
    position: relative; z-index: 1;
}

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

/* ── Metric boxes ── */
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

/* ── Sliders ── */
[data-testid="stSlider"] > div > div > div {
    color: #00ff88 !important;
}

[data-testid="stSlider"] > div > div > div > div {
    background: rgba(0,255,136,0.15) !important;
}

[data-testid="stSlider"] > div > div > div > div > div {
    background: #00ff88 !important;
    box-shadow: 0 0 10px #00ff88 !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: rgba(0,20,5,0.9) !important;
    border: 1px solid rgba(0,255,136,0.4) !important;
    color: #00ff88 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* ── Buttons ── */
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

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 6px !important;
}

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

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background: transparent !important;
}

[data-testid="stTabs"] [data-baseweb="tab-border"] {
    background: rgba(0,255,136,0.15) !important;
}

/* ── Expander ── */
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

/* ── Labels / Text ── */
label, .stMarkdown p, .stMarkdown li {
    color: rgba(0,255,136,0.85) !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* ── Alerts ── */
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

/* ── Success ── */
.stSuccess {
    background: rgba(0,255,136,0.08) !important;
    border: 1px solid rgba(0,255,136,0.3) !important;
    color: #00ff88 !important;
}

/* ── Warning ── */
.stWarning {
    background: rgba(255,234,0,0.08) !important;
    border: 1px solid rgba(255,234,0,0.3) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(0,10,3,0.97) !important;
    border-right: 1px solid rgba(0,255,136,0.2) !important;
}

/* ── Custom game components ── */
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

@keyframes scanBar {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.farmer-emoji {
    font-size: 5rem;
    display: block;
    animation: farmerBob 2s ease-in-out infinite;
    filter: drop-shadow(0 0 15px rgba(0,255,136,0.4));
}

@keyframes farmerBob {
    0%,100% { transform: translateY(0); }
    50%      { transform: translateY(-8px); }
}

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

@keyframes shineBar {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.fsi-big {
    font-family: 'Orbitron', monospace;
    font-size: 2.4rem;
    font-weight: 900;
    text-align: center;
    transition: color 0.5s, text-shadow 0.5s;
}

.hotspot-pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    margin: 2px;
    border: 1px solid;
}

/* ── Floating particles ── */
.particles-container {
    position: fixed; inset: 0; pointer-events: none; z-index: 9999;
    overflow: hidden;
}

.particle {
    position: absolute;
    font-size: 1.3rem;
    animation: floatUp 1.4s ease-out forwards;
    pointer-events: none;
}

@keyframes floatUp {
    0%   { opacity: 1; transform: translateY(0) scale(1) rotate(0deg); }
    100% { opacity: 0; transform: translateY(-130px) scale(0.4) rotate(180deg); }
}

/* ── Achievement banner ── */
.ach-banner {
    background: linear-gradient(135deg, rgba(0,40,10,0.95), rgba(0,20,5,0.95));
    border: 2px solid #39ff14;
    border-radius: 10px;
    padding: 14px 20px;
    text-align: center;
    font-family: 'Orbitron', monospace;
    animation: achGlow 1s ease-in-out 3;
}

@keyframes achGlow {
    0%,100% { box-shadow: 0 0 20px rgba(57,255,20,0.3); }
    50%      { box-shadow: 0 0 50px rgba(57,255,20,0.8); }
}

/* ── Progress / XP bar ── */
.xp-track { height: 8px; background: rgba(0,255,136,0.1); border-radius: 4px; overflow: hidden; }
.xp-fill  { height: 100%; background: linear-gradient(90deg, #006622, #39ff14); border-radius: 4px; transition: width 0.5s; }

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(0,255,136,0.15) !important;
    margin: 16px 0 !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border: 1px dashed rgba(0,255,136,0.3) !important;
    border-radius: 8px !important;
    background: rgba(0,20,5,0.5) !important;
}

/* ── Number input ── */
[data-testid="stNumberInput"] input {
    background: rgba(0,20,5,0.9) !important;
    color: #00ff88 !important;
    border: 1px solid rgba(0,255,136,0.3) !important;
}

/* ── Multiselect ── */
[data-testid="stMultiSelect"] > div {
    background: rgba(0,20,5,0.9) !important;
    border: 1px solid rgba(0,255,136,0.3) !important;
}

/* ── Caption / small text ── */
.stCaption, small {
    color: rgba(0,255,136,0.5) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.72rem !important;
}

/* ── Blink animation for alerts ── */
@keyframes blink {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.4; }
}
.blink { animation: blink 1.2s ease-in-out infinite; }

/* ── Glow text ── */
.glow-green  { color: #00ff88; text-shadow: 0 0 10px rgba(0,255,136,0.7); }
.glow-red    { color: #ff2244; text-shadow: 0 0 10px rgba(255,34,68,0.7); }
.glow-yellow { color: #ffea00; text-shadow: 0 0 10px rgba(255,234,0,0.7); }
.glow-lime   { color: #39ff14; text-shadow: 0 0 10px rgba(57,255,20,0.7); }

</style>
"""

# ─────────────────────────────────────────────────────────
# INJECT CSS + MUSIC JS
# ─────────────────────────────────────────────────────────
st.markdown(GAME_CSS, unsafe_allow_html=True)
st.markdown(MUSIC_JS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# KARNATAKA DISTRICT COORDINATES (lat, lon)
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
# EMBEDDED DATASET — 750 synthetic samples matching the
# original Karnataka dataset structure exactly.
# Columns: Region, Crop, Rainfall, Price, Cost, Yield, Irrigation
# All numeric values are between 0.0 and 1.0
# ─────────────────────────────────────────────────────────

# Seed for reproducibility
random.seed(42)
np.random.seed(42)

DISTRICTS = list(DISTRICT_COORDS.keys())  # 30 districts

CROPS = [
    "Rice", "Wheat", "Maize", "Ragi", "Jowar",
    "Sugarcane", "Cotton", "Groundnut", "Sunflower", "Areca Nut",
    "Coffee", "Coconut", "Banana", "Tomato", "Onion"
]

# Per-district baseline stress profiles (realistic regional variation)
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
def generate_dataset():
    """Generate 750 synthetic farm records matching the original dataset structure."""
    records = []
    samples_per_district = 750 // len(DISTRICTS)  # 25 per district
    extra = 750 - samples_per_district * len(DISTRICTS)

    for i, district in enumerate(DISTRICTS):
        p = DISTRICT_PROFILES[district]
        n = samples_per_district + (1 if i < extra else 0)

        for _ in range(n):
            crop = random.choice(CROPS)
            # Add realistic noise around district baseline
            noise = 0.12
            rain  = float(np.clip(np.random.normal(p["rain"],  noise), 0.05, 0.98))
            price = float(np.clip(np.random.normal(p["price"], noise), 0.05, 0.98))
            yld   = float(np.clip(np.random.normal(p["yield_"],noise), 0.05, 0.98))
            cost  = float(np.clip(np.random.normal(p["cost"],  noise), 0.05, 0.98))
            irrig = float(np.clip(np.random.normal(p["irrig"], noise), 0.05, 0.98))

            # Crop-specific adjustments
            if crop in ["Coffee", "Coconut", "Areca Nut"]:
                rain  = min(rain + 0.10, 0.98)
                irrig = min(irrig + 0.08, 0.98)
            elif crop in ["Ragi", "Jowar"]:
                rain  = max(rain - 0.05, 0.05)
                cost  = max(cost - 0.05, 0.05)
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

    df = pd.DataFrame(records)
    return df


# ─────────────────────────────────────────────────────────
# SESSION STATE INIT (persists across reruns)
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
if "music_on"     not in st.session_state: st.session_state.music_on = False
if "last_fsi"     not in st.session_state: st.session_state.last_fsi = 0.5

# ─────────────────────────────────────────────────────────
# FSI CALCULATION
# ─────────────────────────────────────────────────────────
def compute_fsi(df):
    """
    FSI = Farm Stress Index (0 = No stress, 1 = Maximum stress)

    Formula (weighted average of 5 factors):
      • Low Rainfall → more stress  (weight: 25%)
      • Low Crop Price → more stress (weight: 25%)
      • Low Crop Yield → more stress (weight: 20%)
      • High Input Cost → more stress (weight: 20%)
      • Poor Irrigation → more stress (weight: 10%)
    """
    df = df.copy()
    df["FSI"] = (
        (1 - df["Rainfall"])  * 0.25 +
        (1 - df["Price"])     * 0.25 +
        (1 - df["Yield"])     * 0.20 +
        df["Cost"]            * 0.20 +
        (1 - df["Irrigation"])* 0.10
    )
    return df

def add_stress_labels(df):
    """Classify each farm as HIGH / MEDIUM / LOW stress using 33rd & 66th percentiles."""
    p33 = df["FSI"].quantile(0.33)
    p66 = df["FSI"].quantile(0.66)
    def classify(x):
        if x >= p66: return "HIGH"
        elif x >= p33: return "MEDIUM"
        else: return "LOW"
    df["Stress"] = df["FSI"].apply(classify)
    return df, p33, p66

def get_reason(row):
    """Returns human-readable reasons why a farm is stressed."""
    r = []
    if row["Rainfall"]  < 0.4: r.append("Low Rainfall")
    if row["Yield"]     < 0.4: r.append("Low Yield")
    if row["Price"]     < 0.4: r.append("Low Price")
    if row["Cost"]      > 0.6: r.append("High Cost")
    if row["Irrigation"]< 0.4: r.append("Poor Irrigation")
    return ", ".join(r) if r else "Balanced"

def add_coords(df):
    """Attach latitude/longitude to each row based on district."""
    df = df.copy()
    df["lat"] = df["Region"].map(lambda r: DISTRICT_COORDS.get(r, (14.5, 76.5))[0])
    df["lon"] = df["Region"].map(lambda r: DISTRICT_COORDS.get(r, (14.5, 76.5))[1])
    return df

# ─────────────────────────────────────────────────────────
# AGGREGATE BY DISTRICT (mean FSI per district per crop)
# ─────────────────────────────────────────────────────────
def aggregate(df):
    agg = df.groupby("Region", as_index=False).agg(
        Rainfall=("Rainfall", "mean"),
        Price=("Price", "mean"),
        Yield=("Yield", "mean"),
        Cost=("Cost", "mean"),
        Irrigation=("Irrigation", "mean"),
        Samples=("Rainfall", "count")
    )
    agg = compute_fsi(agg)
    agg, p33, p66 = add_stress_labels(agg)
    agg["Reason"] = agg.apply(get_reason, axis=1)
    agg = add_coords(agg)
    return agg, p33, p66

# ─────────────────────────────────────────────────────────
# HEATMAP BUILDER
# ─────────────────────────────────────────────────────────
def build_map(hex_df, zoom=6.2):
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
            reversescale=True,
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
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=14.5, lon=76.5),
            zoom=zoom
        ),
        height=560,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Rajdhani", color="#00ff88"),
    )
    return fig

# ─────────────────────────────────────────────────────────
# FARMER GAME HELPERS
# ─────────────────────────────────────────────────────────
def compute_game_fsi(rain, price, yld, cost, irrig):
    """Same FSI formula, but with game slider inputs (0–100 scaled to 0–1)."""
    r, p, y, c, i = rain/100, price/100, yld/100, cost/100, irrig/100
    return (1-r)*0.25 + (1-p)*0.25 + (1-y)*0.20 + c*0.20 + (1-i)*0.10

def farmer_state(fsi):
    """Returns (emoji, animation_class, status_text, message, color) based on FSI."""
    if fsi < 0.12:
        return ("🌟", "happy",
                "🌟 THRIVING — FARM CHAMPION!",
                "Wah! Nanna farm super aagide! My family is celebrating! You are a true Avenger! 🎉",
                "#39ff14")
    elif fsi < 0.25:
        return ("👨‍🌾", "happy",
                "😊 VERY HAPPY",
                "Thumba khushi aagide! Great conditions! Keep it up, Avenger! 🌾",
                "#39ff14")
    elif fsi < 0.38:
        return ("🧑‍🌾", "",
                "🙂 CONTENT",
                "Things are okay. A little more improvement and I'll be really happy! 😊",
                "#00ff88")
    elif fsi < 0.50:
        return ("😐", "",
                "😐 NEUTRAL",
                "Hmm... conditions are average. Can you help improve rainfall or crop price?",
                "#ffea00")
    elif fsi < 0.62:
        return ("😟", "stressed",
                "😟 WORRIED",
                "Aiyo! Things are not looking good. My yield is low or costs too high. Please help! 😰",
                "#ffea00")
    elif fsi < 0.75:
        return ("😢", "stressed",
                "😢 VERY STRESSED",
                "Devare! I'm suffering. Rainfall is gone, prices are crashed. My family is hungry! 😭",
                "#ff6600")
    else:
        return ("🆘", "crisis",
                "🆘 FARM CRISIS! HELP!",
                "SAVE ME! Everything has failed! No rain, no yield, high costs! My family needs help! 🚨",
                "#ff2244")

def mood_color(mood_pct):
    if mood_pct > 65: return "linear-gradient(90deg,#005522,#39ff14)"
    elif mood_pct > 40: return "linear-gradient(90deg,#665500,#ffea00)"
    else: return "linear-gradient(90deg,#660011,#ff2244)"

def check_achievements(rain, price, yld, cost, irrig, fsi):
    unlocked = []
    achs = st.session_state.achievements
    checks = {
        "Rain Master":   (not achs["Rain Master"]   and rain  > 80),
        "Profit King":   (not achs["Profit King"]   and price > 80),
        "Harvest Hero":  (not achs["Harvest Hero"]  and yld   > 80),
        "Cost Cutter":   (not achs["Cost Cutter"]   and cost  < 20),
        "Water Wizard":  (not achs["Water Wizard"]  and irrig > 80),
        "Farm Zen":      (not achs["Farm Zen"]       and fsi  < 0.12),
        "Avenger Elite": (not achs["Avenger Elite"] and all(achs[k] for k in list(achs.keys())[:-1])),
    }
    for name, cond in checks.items():
        if cond:
            st.session_state.achievements[name] = True
            unlocked.append(name)
    return unlocked

ACH_META = {
    "Rain Master":   ("💧", "#00ccff", "Rainfall above 80%"),
    "Profit King":   ("💰", "#ffea00", "Crop price above 80%"),
    "Harvest Hero":  ("🌿", "#39ff14", "Yield above 80%"),
    "Cost Cutter":   ("💡", "#ff9900", "Input cost below 20%"),
    "Water Wizard":  ("💦", "#00eeff", "Irrigation above 80%"),
    "Farm Zen":      ("☮",  "#00ff88", "FSI below 12%"),
    "Avenger Elite": ("⚡", "#ff44ff", "All other achievements unlocked"),
}

# ─────────────────────────────────────────────────────────
# ░░░░░░░░░░░░  MAIN APP  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ─────────────────────────────────────────────────────────

# ── HEADER ──────────────────────────────────────────────
st.markdown("<h1>⚡ AGRISTRESS AVENGERS ⚡</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;font-family:Share Tech Mono,monospace;"
    "color:rgba(0,255,136,0.5);font-size:0.82rem;letter-spacing:0.3em;margin-bottom:6px'>"
    "// KARNATAKA FARM STRESS INTELLIGENCE & GAME SYSTEM //</p>",
    unsafe_allow_html=True
)

# ── MUSIC CONTROLS ──────────────────────────────────────
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

# ── DATASET LOADING ─────────────────────────────────────
with st.expander("📂 DATA UPLOAD — Click to load your own dataset (optional)", expanded=False):
    st.markdown("""
    **What is this?**
    By default, the app uses a **built-in dataset** of 750 Karnataka farm samples (auto-generated with realistic regional profiles).
    You can upload your own Excel file (.xlsx) if you have real/updated data.

    **Your file must have these columns:**
    `Region, Crop, Rainfall, Price, Cost, Yield, Irrigation`
    *(All numeric values between 0 and 1)*
    """)
    uploaded = st.file_uploader("Upload your Excel file", type=["xlsx", "csv"])

# Load dataset — use uploaded file OR the built-in generated dataset
if uploaded:
    try:
        df_raw = pd.read_excel(uploaded) if uploaded.name.endswith("xlsx") else pd.read_csv(uploaded)
        st.success(f"✅ Loaded {len(df_raw)} rows from your file!")
    except Exception as e:
        st.error(f"❌ Could not read file: {e}")
        df_raw = None
elif os.path.exists("karnataka_dataset_750_samples.xlsx"):
    # Still support the original file if it exists alongside the script
    @st.cache_data
    def load_excel():
        return pd.read_excel("karnataka_dataset_750_samples.xlsx")
    df_raw = load_excel()
else:
    # ✅ Use the built-in generated dataset — no file needed!
    df_raw = generate_dataset()

if df_raw is None:
    st.stop()

# ── SIDEBAR FILTERS ─────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='font-size:0.9rem'>🎛 FILTERS</h2>", unsafe_allow_html=True)

    # Crop filter
    crops_available = sorted(df_raw["Crop"].unique())
    selected_crops = st.multiselect(
        "🌾 Filter by Crop",
        options=crops_available,
        default=crops_available,
        help="Select which crops to include in the analysis"
    )
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
    +(1-Irrig)×0.10<br>
    <br>
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

# ── FILTER DATA ─────────────────────────────────────────
df_filtered = df_raw[df_raw["Crop"].isin(selected_crops)].copy()
df_filtered = compute_fsi(df_filtered)

# Aggregate by district
hex_df, p33, p66 = aggregate(df_filtered)

# ── TOP METRICS ROW ─────────────────────────────────────
total_districts = len(hex_df)
high_count  = (hex_df["Stress"] == "HIGH").sum()
med_count   = (hex_df["Stress"] == "MEDIUM").sum()
low_count   = (hex_df["Stress"] == "LOW").sum()
avg_fsi     = hex_df["FSI"].mean()
worst_dist  = hex_df.loc[hex_df["FSI"].idxmax(), "Region"]

mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
mc1.metric("📍 Districts", total_districts)
mc2.metric("🔴 HIGH Stress", high_count, delta=f"{high_count/total_districts*100:.0f}% of total", delta_color="inverse")
mc3.metric("🟡 MEDIUM Stress", med_count)
mc4.metric("🟢 LOW Stress", low_count, delta=f"{low_count/total_districts*100:.0f}% of total")
mc5.metric("⚡ Avg FSI", f"{avg_fsi:.3f}")
mc6.metric("🔥 Worst Region", worst_dist)

st.divider()

# ─────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📡 STRESS HEATMAP",
    "🎮 FARMER SIMULATOR",
    "📊 ANALYTICS",
    "🚨 ALERT SYSTEM"
])

# ════════════════════════════════════════════════════════
# TAB 1 — HEATMAP
# ════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 🗺 FSI HEATMAP — KARNATAKA DISTRICTS")

    with st.expander("❓ What is this map? (Click to learn)", expanded=False):
        st.markdown("""
        **This map shows Farm Stress across all 30 Karnataka districts.**

        🟢 **GREEN dots** = LOW stress farms — good conditions, farmer is happy!
        🟡 **YELLOW dots** = MEDIUM stress — some problems, needs attention
        🔴 **RED dots** = HIGH stress — serious problems! Immediate help needed

        **Bigger dot = Higher stress level**

        👆 **Hover over any dot** to see full details: FSI score, stress reason,
        rainfall level, crop price, yield, cost, and irrigation data.

        The **colorbar on the right** shows FSI from 0 (best) to 1 (worst).
        """)

    # Map options row
    mapcol1, mapcol2 = st.columns([3, 1])
    with mapcol2:
        zoom_level = st.slider(
            "🔍 Map Zoom",
            min_value=5, max_value=9, value=6,
            help="Zoom in/out on the Karnataka map"
        )

    # Render map
    map_fig = build_map(hex_df, zoom=zoom_level)
    st.plotly_chart(map_fig, use_container_width=True)

    # Mission Control row
    st.markdown("### 🎯 MISSION CONTROL — DISTRICT DEEP DIVE")

    d_col1, d_col2 = st.columns([2, 1])

    with d_col1:
        st.markdown("""
        <small>Select a district to see its detailed farm stress profile</small>
        """, unsafe_allow_html=True)

        selected_district = st.selectbox(
            "🔍 Select District to Inspect",
            options=sorted(hex_df["Region"].unique()),
            help="Pick any Karnataka district to see its complete stress breakdown"
        )
        sel = hex_df[hex_df["Region"] == selected_district].iloc[0]
        stress_cls = {"HIGH": "glow-red", "MEDIUM": "glow-yellow", "LOW": "glow-lime"}[sel["Stress"]]
        stress_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[sel["Stress"]]

        st.markdown(f"""
        <div class='game-card'>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px'>
                <div><span style='color:rgba(0,255,136,0.5);font-size:0.75rem'>📍 REGION</span>
                     <div style='font-family:Orbitron,monospace;font-weight:700'>{sel['Region']}</div></div>
                <div><span style='color:rgba(0,255,136,0.5);font-size:0.75rem'>⚡ FSI SCORE</span>
                     <div class='fsi-big' style='font-size:1.8rem'>{sel['FSI']:.4f}</div></div>
                <div><span style='color:rgba(0,255,136,0.5);font-size:0.75rem'>🚨 STRESS LEVEL</span>
                     <div class='{stress_cls}' style='font-family:Orbitron,monospace;font-weight:700;font-size:1.1rem'>{stress_icon} {sel['Stress']}</div></div>
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

    with st.expander("🕹️ HOW TO PLAY (Click to learn the game!)", expanded=True):
        st.markdown("""
        **Welcome to Ramu's Farm!** 🌾

        **Your Mission:** Help farmer Ramu achieve a HAPPY farm by adjusting the 5 parameters below.

        | Parameter | What it means | Good value | Bad value |
        |-----------|---------------|------------|-----------|
        | 🌧 **Rainfall** | How much rain the farm receives | HIGH (80+) | LOW (below 40) |
        | 💰 **Crop Price** | Market price for crops | HIGH (80+) | LOW (below 40) |
        | 🌿 **Crop Yield** | How much crop is produced | HIGH (80+) | LOW (below 40) |
        | 📦 **Input Cost** | Cost of seeds, fertilizers etc. | LOW (below 20) | HIGH (above 60) |
        | 💧 **Irrigation** | Water supply for farming | HIGH (80+) | LOW (below 40) |

        **Watch Ramu:** He will **dance happily** when FSI is low, and **shake & cry** when FSI is high!

        **Earn Points:** Keep FSI below 0.30 to earn XP and unlock achievements!

        **🏅 7 Achievements** to unlock — can you get them all?
        """)

    # ── Game layout: Controls | Farmer | Score ──────────────
    gc1, gc2, gc3 = st.columns([2.2, 1.8, 2])

    # ── LEFT: Environment sliders ────────────────────────────
    with gc1:
        st.markdown("**⚙️ ENVIRONMENT CONTROLS**")
        st.markdown("<small>Drag the sliders to change farm conditions</small>", unsafe_allow_html=True)

        rain  = st.slider("🌧 Rainfall Level",  0, 100, 50, key="g_rain",
                          help="How much rainfall the farm gets. Higher = better for crops!")
        price = st.slider("💰 Crop Market Price",  0, 100, 50, key="g_price",
                          help="Price farmers receive for their crops in the market. Higher = more income!")
        yld   = st.slider("🌿 Crop Yield",  0, 100, 50, key="g_yield",
                          help="How much crop the farm produces per acre. Higher = more harvest!")
        cost  = st.slider("📦 Input Cost",  0, 100, 50, key="g_cost",
                          help="Cost of seeds, fertilizers, pesticides. LOWER is better for farmers!")
        irrig = st.slider("💧 Irrigation Access",  0, 100, 50, key="g_irrig",
                          help="How well the farm is irrigated with water supply. Higher = better!")

        st.divider()

        # Season presets
        st.markdown("**🌦 QUICK SEASON PRESETS**")
        st.markdown("<small>Load real-world seasonal conditions instantly</small>", unsafe_allow_html=True)
        ps1, ps2, ps3, ps4 = st.columns(4)

        if "preset" not in st.session_state:
            st.session_state.preset = None

        with ps1:
            if st.button("🌧\nMonsoon", help="Heavy rains, good irrigation but sometimes low prices"):
                st.session_state.preset = "monsoon"
                st.rerun()
        with ps2:
            if st.button("☀️\nDry", help="Drought conditions — very hard for farmers!"):
                st.session_state.preset = "dry"
                st.rerun()
        with ps3:
            if st.button("🌾\nKharif", help="Main crop season — moderate conditions"):
                st.session_state.preset = "kharif"
                st.rerun()
        with ps4:
            if st.button("🏆\nIdeal", help="Perfect farm conditions! Achieve Farm Zen!"):
                st.session_state.preset = "ideal"
                st.rerun()

    # Apply preset if selected
    if st.session_state.preset == "monsoon":
        rain, price, yld, cost, irrig = 85, 55, 72, 42, 80
    elif st.session_state.preset == "dry":
        rain, price, yld, cost, irrig = 15, 45, 28, 58, 22
    elif st.session_state.preset == "kharif":
        rain, price, yld, cost, irrig = 68, 62, 65, 48, 60
    elif st.session_state.preset == "ideal":
        rain, price, yld, cost, irrig = 92, 88, 90, 12, 88

    # Compute game FSI
    g_fsi = compute_game_fsi(rain, price, yld, cost, irrig)
    g_fsi = round(g_fsi, 4)

    # Update score
    if g_fsi < 0.30:
        st.session_state.score = min(9999, st.session_state.score + (15 if g_fsi < 0.15 else 5))
        st.session_state.xp = min(100, st.session_state.xp + 3)

    if st.session_state.xp >= 100:
        st.session_state.xp = 0
        st.session_state.level += 1
        st.markdown(f"""
        <div class='ach-banner'>
            🎊 LEVEL UP! YOU ARE NOW LEVEL {st.session_state.level}! 🎊
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<script>AgriMusic.playSFX('win');</script>", unsafe_allow_html=True)

    # Check achievements
    new_achs = check_achievements(rain, price, yld, cost, irrig, g_fsi)
    for ach in new_achs:
        icon, color, desc = ACH_META[ach]
        st.markdown(f"""
        <div class='ach-banner' style='border-color:{color}'>
            <div style='font-size:2rem'>{icon}</div>
            <div style='color:{color};font-size:1rem'>ACHIEVEMENT UNLOCKED: {ach}</div>
            <div style='color:rgba(0,255,136,0.5);font-size:0.8rem'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<script>AgriMusic.playSFX('win');</script>", unsafe_allow_html=True)

    # ── CENTRE: Farmer character ─────────────────────────────
    with gc2:
        emoji, anim_cls, status_txt, message, st_color = farmer_state(g_fsi)
        mood_pct = max(0, min(100, int((1 - g_fsi) * 100)))
        m_color = mood_color(mood_pct)

        fsi_color = "#ff2244" if g_fsi > 0.66 else "#ffea00" if g_fsi > 0.33 else "#39ff14"
        fsi_glow  = f"0 0 25px {fsi_color}"

        # Play stress SFX if FSI spikes
        if g_fsi > 0.70 and st.session_state.last_fsi <= 0.70:
            st.markdown("<script>AgriMusic.playSFX('alert');</script>", unsafe_allow_html=True)
        elif g_fsi < 0.20 and st.session_state.last_fsi >= 0.20:
            st.markdown("<script>AgriMusic.playSFX('win');</script>", unsafe_allow_html=True)
        st.session_state.last_fsi = g_fsi

        st.markdown(f"""
        <div class='farmer-box'>
            <!-- Score & XP -->
            <div style='font-family:Orbitron,monospace;font-size:0.62rem;
                 color:rgba(0,255,136,0.5);letter-spacing:0.2em'>FARMER XP</div>
            <div style='font-family:Orbitron,monospace;font-size:2rem;
                 font-weight:900;color:#39ff14;
                 filter:drop-shadow(0 0 12px rgba(57,255,20,0.6))'>
                 {str(st.session_state.score).zfill(4)}</div>
            <div style='font-family:Share Tech Mono,monospace;font-size:0.7rem;
                 color:rgba(0,255,136,0.4)'>LEVEL {st.session_state.level}</div>
            <div class='xp-track' style='margin:6px 0'>
                <div class='xp-fill' style='width:{st.session_state.xp}%'></div>
            </div>
            <div style='font-size:0.62rem;color:rgba(0,255,136,0.3);
                 font-family:Share Tech Mono,monospace;margin-bottom:12px'>
                 XP {st.session_state.xp}/100</div>

            <!-- Farmer character -->
            <span class='farmer-emoji {anim_cls}'>{emoji}</span>

            <div style='font-family:Orbitron,monospace;font-size:0.72rem;
                 font-weight:700;color:#00ff88;letter-spacing:0.1em;margin:8px 0 4px'>
                 RAMU — KARNATAKA FARMER</div>

            <!-- Mood bar -->
            <div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;
                 color:rgba(0,255,136,0.4);text-align:left;margin-bottom:3px'>
                 HAPPINESS METER {mood_pct}%</div>
            <div class='mood-track'>
                <div class='mood-fill-inner' style='width:{mood_pct}%;background:{m_color}'></div>
            </div>

            <!-- Status text -->
            <div style='font-family:Orbitron,monospace;font-size:0.8rem;font-weight:700;
                 color:{st_color};margin:10px 0 4px;text-shadow:0 0 10px {st_color}'>
                 {status_txt}</div>
            <div style='font-size:0.78rem;color:rgba(0,255,136,0.55);
                 font-style:italic;line-height:1.4;min-height:44px'>
                 {message}</div>

            <!-- FSI display -->
            <div style='background:rgba(0,0,0,0.4);border:1px solid rgba(0,255,136,0.2);
                 border-radius:6px;padding:10px;margin-top:12px'>
                <div class='fsi-big' style='color:{fsi_color};text-shadow:{fsi_glow}'>
                    {g_fsi:.3f}</div>
                <div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;
                     color:rgba(0,255,136,0.4);letter-spacing:0.2em'>FARM STRESS INDEX</div>
                <div style='font-size:0.72rem;margin-top:4px;color:{fsi_color}'>
                    {'🔴 HIGH STRESS' if g_fsi >= 0.62 else '🟡 MEDIUM STRESS' if g_fsi >= 0.38 else '🟢 LOW STRESS'}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── RIGHT: Achievements + Stress Drivers ─────────────────
    with gc3:
        st.markdown("**🏅 ACHIEVEMENTS**")
        st.markdown("<small>Unlock all 7 to become a Farm Avenger!</small>", unsafe_allow_html=True)

        for ach_name, (icon, color, desc) in ACH_META.items():
            unlocked = st.session_state.achievements[ach_name]
            opacity = "1" if unlocked else "0.3"
            border_style = f"2px solid {color}" if unlocked else f"1px solid {color}55"
            glow = f"box-shadow:0 0 12px {color}66;" if unlocked else ""
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;padding:7px 10px;
                 border-radius:6px;border:{border_style};
                 background:rgba(0,20,5,0.6);margin-bottom:5px;
                 opacity:{opacity};{glow}transition:all 0.3s'>
                <span style='font-size:1.2rem'>{icon}</span>
                <div>
                    <div style='font-weight:700;font-size:0.85rem;color:{color}'>{ach_name}</div>
                    <div style='font-size:0.68rem;color:rgba(0,255,136,0.4)'>{desc}</div>
                </div>
                <span style='margin-left:auto;font-size:0.7rem'>{'✅' if unlocked else '🔒'}</span>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Stress drivers panel
        st.markdown("**💡 WHAT'S STRESSING RAMU?**")
        drivers = []
        if rain  < 40: drivers.append(("🌧", "Increase Rainfall", "#00ccff"))
        if price < 40: drivers.append(("💰", "Raise Crop Price",  "#ffea00"))
        if yld   < 40: drivers.append(("🌿", "Improve Yield",     "#39ff14"))
        if cost  > 60: drivers.append(("📦", "Reduce Input Cost", "#ff6600"))
        if irrig < 40: drivers.append(("💧", "Improve Irrigation","#00eeff"))

        if drivers:
            for icon, tip, color in drivers:
                st.markdown(f"""
                <div style='padding:5px 10px;border:1px solid {color}44;
                     border-left:3px solid {color};border-radius:4px;
                     margin-bottom:4px;font-size:0.82rem;color:{color}'>
                     {icon} Fix: {tip}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='padding:10px;border:1px solid #39ff1444;border-radius:6px;
                 text-align:center;color:#39ff14;font-weight:700'>
                ✅ ALL PARAMETERS HEALTHY!<br>
                <span style='font-size:0.75rem;opacity:0.6'>Ramu is thriving!</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Reset button ─────────────────────────────────────────
    st.divider()
    rcol1, rcol2, rcol3 = st.columns([1,1,4])
    with rcol1:
        if st.button("🔄 RESET SCORE", help="Reset your score and achievements to start fresh"):
            st.session_state.score = 0
            st.session_state.xp = 0
            st.session_state.level = 1
            st.session_state.achievements = {k: False for k in st.session_state.achievements}
            st.session_state.preset = None
            st.rerun()
    with rcol2:
        if st.button("🗑 CLEAR PRESET"):
            st.session_state.preset = None
            st.rerun()

# ════════════════════════════════════════════════════════
# TAB 3 — ANALYTICS
# ════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📊 STRESS ANALYTICS DASHBOARD")

    with st.expander("❓ Understanding the charts", expanded=False):
        st.markdown("""
        **What do these charts tell us?**

        📊 **Stress Distribution Bar**: Shows how many districts are in HIGH / MEDIUM / LOW stress.
        A healthy state has most districts in the LOW category.

        🌾 **Crop-wise FSI**: Compare which crops face more stress. Crops with high FSI need policy intervention.

        🔥 **Full District Ranking**: Sorted from most stressed to least — use this to prioritize aid.

        📈 **Parameter Correlation**: See which factor (rainfall, price, etc.) most influences stress.
        """)

    # Charts row
    ac1, ac2 = st.columns(2)

    with ac1:
        # Stress distribution bar chart
        stress_counts = hex_df["Stress"].value_counts().reindex(["HIGH","MEDIUM","LOW"]).fillna(0)
        bar_colors = ["#ff2244","#ffea00","#39ff14"]
        fig_bar = go.Figure(go.Bar(
            x=stress_counts.index,
            y=stress_counts.values,
            marker_color=bar_colors,
            marker_line_color=["#ff000088","#ffff0088","#00ff0088"],
            marker_line_width=1,
            text=stress_counts.values.astype(int),
            textposition="outside",
            textfont=dict(color="#00ff88", family="Share Tech Mono"),
        ))
        fig_bar.update_layout(
            title=dict(text="📊 Districts by Stress Category", font=dict(color="#39ff14", family="Orbitron", size=13)),
            xaxis=dict(tickfont=dict(color="#00ff88", family="Share Tech Mono")),
            yaxis=dict(tickfont=dict(color="#00ff88", family="Share Tech Mono"), gridcolor="rgba(0,255,136,0.08)"),
            paper_bgcolor="rgba(0,13,2,0.0)", plot_bgcolor="rgba(0,13,2,0.6)",
            font=dict(color="#00ff88"), height=320, margin=dict(t=40,b=20,l=30,r=20),
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with ac2:
        # Crop-wise average FSI
        crop_fsi = df_filtered.groupby("Crop")["FSI"].mean().sort_values(ascending=False)
        fig_crop = go.Figure(go.Bar(
            y=crop_fsi.index,
            x=crop_fsi.values,
            orientation="h",
            marker_color=crop_fsi.values,
            marker_colorscale="RdYlGn",
            marker_reversescale=True,
            text=[f"{v:.3f}" for v in crop_fsi.values],
            textposition="outside",
            textfont=dict(color="#00ff88", family="Share Tech Mono"),
        ))
        fig_crop.update_layout(
            title=dict(text="🌾 Average FSI by Crop Type", font=dict(color="#39ff14", family="Orbitron", size=13)),
            xaxis=dict(tickfont=dict(color="#00ff88", family="Share Tech Mono"), gridcolor="rgba(0,255,136,0.08)"),
            yaxis=dict(tickfont=dict(color="#00ff88", family="Share Tech Mono")),
            paper_bgcolor="rgba(0,13,2,0.0)", plot_bgcolor="rgba(0,13,2,0.6)",
            font=dict(color="#00ff88"), height=320, margin=dict(t=40,b=20,l=30,r=20),
            showlegend=False
        )
        st.plotly_chart(fig_crop, use_container_width=True)

    # Full district ranking table
    st.markdown("### 🔥 FULL DISTRICT STRESS RANKING")
    st.markdown("<small>Sorted from most stressed to least stressed district</small>", unsafe_allow_html=True)

    sorted_df = hex_df.sort_values("FSI", ascending=False)

    for i, (_, row) in enumerate(sorted_df.iterrows()):
        s = row["Stress"]
        icon  = {"HIGH":"🔴","MEDIUM":"🟡","LOW":"🟢"}[s]
        color = {"HIGH":"#ff2244","MEDIUM":"#ffea00","LOW":"#39ff14"}[s]
        rank_bg = "rgba(255,34,68,0.05)" if s=="HIGH" else "rgba(255,234,0,0.03)" if s=="MEDIUM" else "rgba(57,255,20,0.03)"

        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:12px;padding:7px 12px;
             margin-bottom:3px;border:1px solid {color}22;
             border-left:3px solid {color};border-radius:4px;
             background:{rank_bg}'>
            <span style='font-family:Orbitron,monospace;font-size:0.65rem;
                  color:rgba(255,136,0,0.6);width:22px'>#{i+1}</span>
            <span style='font-weight:700;font-size:0.88rem;flex:1'>{row['Region']}</span>
            <span style='font-size:0.75rem;color:rgba(0,255,136,0.5);flex:1'>{row['Reason']}</span>
            <span style='font-family:Share Tech Mono,monospace;font-size:0.8rem;color:{color}'>FSI {row['FSI']:.3f}</span>
            <span style='width:70px;text-align:right;font-size:0.75rem;color:{color}'>{icon} {s}</span>
        </div>
        """, unsafe_allow_html=True)

    # Parameter averages radar-style
    st.markdown("### 📡 DISTRICT PARAMETER AVERAGES")
    params = ["Rainfall","Price","Yield","Irrigation"]
    fig_radar = go.Figure()
    for stress_lvl, color in [("HIGH","#ff2244"),("MEDIUM","#ffea00"),("LOW","#39ff14")]:
        subset = hex_df[hex_df["Stress"]==stress_lvl]
        if len(subset) > 0:
            means = [subset[p].mean() for p in params]
            fig_radar.add_trace(go.Scatterpolar(
                r=means + [means[0]],
                theta=params + [params[0]],
                fill="toself",
                name=stress_lvl,
                line_color=color,
                fillcolor=color.replace(")", ",0.1)").replace("#", "rgba(").replace(
                    "rgba(ff2244,0.1)","rgba(255,34,68,0.1)").replace(
                    "rgba(ffea00,0.1)","rgba(255,234,0,0.1)").replace(
                    "rgba(39ff14,0.1)","rgba(57,255,20,0.1)"),
            ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,1], gridcolor="rgba(0,255,136,0.15)",
                           tickfont=dict(color="rgba(0,255,136,0.5)", size=9)),
            angularaxis=dict(tickfont=dict(color="#00ff88", family="Rajdhani", size=11)),
            bgcolor="rgba(0,13,2,0.6)"
        ),
        showlegend=True, height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#00ff88"),
        legend=dict(font=dict(color="#00ff88"), bgcolor="rgba(0,13,2,0.8)",
                   bordercolor="rgba(0,255,136,0.3)", borderwidth=1),
        title=dict(text="Average Parameters by Stress Level", font=dict(color="#39ff14", family="Orbitron", size=12))
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 4 — ALERT SYSTEM
# ════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🚨 HIGH STRESS ALERT SYSTEM")

    with st.expander("❓ What is this alert system?", expanded=False):
        st.markdown("""
        **This panel shows districts that need IMMEDIATE attention.**

        🔴 **HIGH stress** districts are shown here — these are areas where farmers are suffering
        due to poor rainfall, low crop prices, high costs, or poor irrigation.

        **How to use this:**
        - Government officials can use this to prioritize aid and subsidies
        - NGOs can identify which regions need immediate intervention
        - Researchers can study patterns in farm distress

        **Action Items listed** tell you EXACTLY what needs to be fixed in each district.
        """)

    high_districts = hex_df[hex_df["Stress"]=="HIGH"].sort_values("FSI", ascending=False)
    med_districts  = hex_df[hex_df["Stress"]=="MEDIUM"].sort_values("FSI", ascending=False)

    if len(high_districts) > 0:
        st.markdown(f"#### 🔴 {len(high_districts)} DISTRICTS IN CRITICAL STRESS")
        st.markdown("<small>These districts need immediate government intervention!</small>", unsafe_allow_html=True)

        for _, row in high_districts.iterrows():
            # Build action items
            actions = []
            if row["Rainfall"]  < 0.4: actions.append("Provide drought relief & water tankers")
            if row["Price"]     < 0.4: actions.append("Implement Minimum Support Price (MSP)")
            if row["Yield"]     < 0.4: actions.append("Distribute improved seeds & fertilizer")
            if row["Cost"]      > 0.6: actions.append("Provide input subsidies to reduce cost")
            if row["Irrigation"]< 0.4: actions.append("Build irrigation canals / bore wells")

            st.error(f"""
🔴 **{row['Region']}** | FSI = {row['FSI']:.3f} | Root Cause: {row['Reason']}

📋 **Required Actions:**
{chr(10).join(f'  → {a}' for a in actions) if actions else '  → Monitor closely'}
            """)
    else:
        st.success("✅ No districts in CRITICAL stress zone. Great job, Avengers!")

    if len(med_districts) > 0:
        st.markdown(f"#### 🟡 {len(med_districts)} DISTRICTS IN MODERATE STRESS")
        st.markdown("<small>Watch these districts — they could worsen!</small>", unsafe_allow_html=True)

        for _, row in med_districts.iterrows():
            st.warning(f"🟡 **{row['Region']}** | FSI = {row['FSI']:.3f} | {row['Reason']}")

    st.divider()

    # Summary stats
    st.markdown("### 📋 EXECUTIVE SUMMARY")
    total_farms = len(df_filtered)
    high_farms = len(df_filtered[df_filtered["FSI"] > p66])
    st.markdown(f"""
    <div class='game-card'>
        <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:16px;text-align:center'>
            <div>
                <div style='font-size:2rem;font-weight:900;font-family:Orbitron,monospace;
                     color:#ff2244;text-shadow:0 0 12px rgba(255,34,68,0.5)'>
                     {len(high_districts)}</div>
                <div style='color:rgba(0,255,136,0.5);font-size:0.78rem'>CRITICAL DISTRICTS</div>
            </div>
            <div>
                <div style='font-size:2rem;font-weight:900;font-family:Orbitron,monospace;
                     color:#ffea00;text-shadow:0 0 12px rgba(255,234,0,0.5)'>
                     {high_farms}</div>
                <div style='color:rgba(0,255,136,0.5);font-size:0.78rem'>FARM RECORDS AT HIGH RISK</div>
            </div>
            <div>
                <div style='font-size:2rem;font-weight:900;font-family:Orbitron,monospace;
                     color:#39ff14;text-shadow:0 0 12px rgba(57,255,20,0.5)'>
                     {avg_fsi:.3f}</div>
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
    ⚡ AGRISTRESS AVENGERS v2.0 | KARNATAKA GEOSPATIAL STRESS DETECTION SYSTEM |
    DATA: 750 FARM SAMPLES ACROSS 30 DISTRICTS | BUILT FOR AVENGER FARMERS 🌾
</div>
""", unsafe_allow_html=True)
