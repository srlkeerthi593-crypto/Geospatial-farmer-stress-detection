# =========================================================
# src/gui/game.py
# Helper functions for the Farmer Simulator game tab:
#   - Farmer character states by FSI level
#   - Mood bar colour logic
#   - Achievement checking
# =========================================================

import streamlit as st
from src.utils.constants import ACH_META


def farmer_state(fsi: float):
    """
    Return farmer character display state based on current FSI.

    Parameters
    ----------
    fsi : float — current Farm Stress Index (0.0–1.0).

    Returns
    -------
    tuple : (emoji, animation_class, status_text, message, colour_hex)
    """
    if fsi < 0.12:
        return ("🌟", "happy", "🌟 THRIVING — FARM CHAMPION!",
                "Wah! Nanna farm super aagide! My family is celebrating! You are a true Avenger! 🎉", "#39ff14")
    elif fsi < 0.25:
        return ("👨‍🌾", "happy", "😊 VERY HAPPY",
                "Thumba khushi aagide! Great conditions! Keep it up, Avenger! 🌾", "#39ff14")
    elif fsi < 0.38:
        return ("🧑‍🌾", "", "🙂 CONTENT",
                "Things are okay. A little more improvement and I'll be really happy! 😊", "#00ff88")
    elif fsi < 0.50:
        return ("😐", "", "😐 NEUTRAL",
                "Hmm... conditions are average. Can you help improve rainfall or crop price?", "#ffea00")
    elif fsi < 0.62:
        return ("😟", "stressed", "😟 WORRIED",
                "Aiyo! Things are not looking good. My yield is low or costs too high. Please help! 😰", "#ffea00")
    elif fsi < 0.75:
        return ("😢", "stressed", "😢 VERY STRESSED",
                "Devare! I'm suffering. Rainfall is gone, prices are crashed. My family is hungry! 😭", "#ff6600")
    else:
        return ("🆘", "crisis", "🆘 FARM CRISIS! HELP!",
                "SAVE ME! Everything has failed! No rain, no yield, high costs! My family needs help! 🚨", "#ff2244")


def mood_color(mood_pct: int) -> str:
    """Return CSS gradient string for the happiness progress bar."""
    if mood_pct > 65:
        return "linear-gradient(90deg,#005522,#39ff14)"
    elif mood_pct > 40:
        return "linear-gradient(90deg,#665500,#ffea00)"
    else:
        return "linear-gradient(90deg,#660011,#ff2244)"


def check_achievements(rain: int, price: int, yld: int, cost: int, irrig: int, fsi: float) -> list:
    """
    Check slider values against achievement unlock conditions.
    Updates st.session_state.achievements in place.

    Parameters
    ----------
    rain, price, yld, cost, irrig : int — slider values (0–100)
    fsi : float — current FSI

    Returns
    -------
    list of str — names of newly unlocked achievements
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


def init_session_state():
    """Initialise all Streamlit session state keys if not already set."""
    if "score"        not in st.session_state: st.session_state.score = 0
    if "xp"           not in st.session_state: st.session_state.xp = 0
    if "level"        not in st.session_state: st.session_state.level = 1
    if "achievements" not in st.session_state:
        st.session_state.achievements = {k: False for k in ACH_META}
    if "music_on"  not in st.session_state: st.session_state.music_on = False
    if "last_fsi"  not in st.session_state: st.session_state.last_fsi = 0.5
    if "preset"    not in st.session_state: st.session_state.preset = None
