# =========================================================
# ⚡ AGRISTRESS AVENGERS — v4.0
# main.py — Entry point to launch the Streamlit application
#
# Usage:
#   streamlit run main.py
# =========================================================

import subprocess
import sys
import os

if __name__ == "__main__":
    app_path = os.path.join(os.path.dirname(__file__), "src", "gui", "app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
