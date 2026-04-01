# =========================================================
# src/gui/styles.py
# CSS (neon game UI) and JavaScript (Web Audio Synthesiser)
# injected into the Streamlit app via st.markdown.
# =========================================================

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
.stSuccess { background: rgba(0,255,136,0.08) !important; border: 1px solid rgba(0,255,136,0.3) !important; color: #00ff88 !important; }
.stWarning { background: rgba(255,234,0,0.08) !important; border: 1px solid rgba(255,234,0,0.3) !important; }
[data-testid="stSidebar"] { background: rgba(0,10,3,0.97) !important; border-right: 1px solid rgba(0,255,136,0.2) !important; }
.farmer-box { background: rgba(0,10,3,0.95); border: 1px solid rgba(0,255,136,0.5); border-radius: 12px; padding: 20px; text-align: center; position: relative; overflow: hidden; }
.farmer-box::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, #00ff88, transparent); animation: scanBar 3s linear infinite; }
@keyframes scanBar { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
.farmer-emoji { font-size: 5rem; display: block; animation: farmerBob 2s ease-in-out infinite; filter: drop-shadow(0 0 15px rgba(0,255,136,0.4)); }
@keyframes farmerBob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
.farmer-emoji.happy { animation: farmerDance 0.5s ease-in-out infinite; filter: drop-shadow(0 0 20px rgba(57,255,20,0.7)); }
@keyframes farmerDance { 0%,100% { transform: scale(1) rotate(-4deg); } 50% { transform: scale(1.12) rotate(4deg); } }
.farmer-emoji.stressed { animation: farmerShake 0.4s ease-in-out infinite; filter: drop-shadow(0 0 15px rgba(255,34,68,0.6)); }
@keyframes farmerShake { 0%,100% { transform: rotate(-6deg) scale(0.95); } 50% { transform: rotate(6deg) scale(1.05); } }
.farmer-emoji.crisis { animation: farmerCrisis 0.25s ease-in-out infinite; filter: drop-shadow(0 0 20px rgba(255,34,68,0.9)); }
@keyframes farmerCrisis { 0%,100% { transform: rotate(-8deg) scale(0.9) translateY(4px); } 50% { transform: rotate(8deg) scale(1.1) translateY(-4px); } }
.mood-track { width: 100%; height: 14px; background: rgba(0,255,136,0.1); border-radius: 7px; border: 1px solid rgba(0,255,136,0.2); overflow: hidden; margin: 8px 0; }
.mood-fill-inner { height: 100%; border-radius: 7px; transition: width 0.6s ease, background 0.6s ease; position: relative; overflow: hidden; }
.mood-fill-inner::after { content: ''; position: absolute; inset: 0; background: linear-gradient(90deg, transparent 50%, rgba(255,255,255,0.2)); animation: shineBar 1.5s ease-in-out infinite; }
@keyframes shineBar { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
.fsi-big { font-family: 'Orbitron', monospace; font-size: 2.4rem; font-weight: 900; text-align: center; transition: color 0.5s, text-shadow 0.5s; }
.ach-banner { background: linear-gradient(135deg, rgba(0,40,10,0.95), rgba(0,20,5,0.95)); border: 2px solid #39ff14; border-radius: 10px; padding: 14px 20px; text-align: center; font-family: 'Orbitron', monospace; animation: achGlow 1s ease-in-out 3; }
@keyframes achGlow { 0%,100% { box-shadow: 0 0 20px rgba(57,255,20,0.3); } 50% { box-shadow: 0 0 50px rgba(57,255,20,0.8); } }
.xp-track { height: 8px; background: rgba(0,255,136,0.1); border-radius: 4px; overflow: hidden; }
.xp-fill  { height: 100%; background: linear-gradient(90deg, #006622, #39ff14); border-radius: 4px; transition: width 0.5s; }
hr { border: none !important; border-top: 1px solid rgba(0,255,136,0.15) !important; margin: 16px 0 !important; }
[data-testid="stFileUploader"] { border: 1px dashed rgba(0,255,136,0.3) !important; border-radius: 8px !important; background: rgba(0,20,5,0.5) !important; }
[data-testid="stMultiSelect"] > div { background: rgba(0,20,5,0.9) !important; border: 1px solid rgba(0,255,136,0.3) !important; }
.stCaption, small { color: rgba(0,255,136,0.5) !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.72rem !important; }
.glow-green  { color: #00ff88; text-shadow: 0 0 10px rgba(0,255,136,0.7); }
.glow-red    { color: #ff2244; text-shadow: 0 0 10px rgba(255,34,68,0.7); }
.glow-yellow { color: #ffea00; text-shadow: 0 0 10px rgba(255,234,0,0.7); }
.glow-lime   { color: #39ff14; text-shadow: 0 0 10px rgba(57,255,20,0.7); }
</style>
"""
