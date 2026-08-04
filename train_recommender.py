"""
Data Preprocessing Script Launcher Shim.
Redirects to scripts/train_recommender.py.
"""
from scripts.train_recommender import preprocess_bgg_data

if __name__ == "__main__":
    preprocess_bgg_data()
