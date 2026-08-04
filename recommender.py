"""
Recommender Engine Compatibility Shim.
Redirects imports to src.recommender.
"""
from src.recommender.engine import load_data, recommend_games
from src.recommender.bgg_api import fetch_bgg_collection

__all__ = ["load_data", "recommend_games", "fetch_bgg_collection"]
