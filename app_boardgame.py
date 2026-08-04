"""
MeepleMind - Board Game Suggester Application
Main Entrypoint Script
"""
import sys
from pathlib import Path

# Ensure src directory is on sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.ui.views import render_app

if __name__ == "__main__":
    render_app()
