import os
import requests
from typing import Tuple, List, Dict, Any, Optional
from src.recommender.engine import recommend_games

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def is_backend_online() -> bool:
    """Check if FastAPI backend server is online at http://localhost:8000/health."""
    try:
        res = requests.get(f"{API_BASE_URL}/health", timeout=3)
        return res.status_code == 200
    except Exception:
        return False

def get_catalog_metadata() -> Tuple[Dict[str, Any], List[str], List[str], List[str], List[str]]:
    """Fetch metadata, categories, mechanics, themes, and game names from backend API."""
    res = requests.get(f"{API_BASE_URL}/api/v1/metadata", timeout=10)
    res.raise_for_status()
    data = res.json()
    
    metadata_dict = {
        'total_games': data['total_games'],
        'total_mechanics': data['total_mechanics'],
        'total_themes': data['total_themes']
    }
    return (
        metadata_dict,
        data['categories'],
        data['mechanics'],
        data['themes'],
        data['all_names']
    )

def fetch_recommendations_api(
    selected_names: List[str],
    player_count_range: Optional[Tuple[int, int]] = None,
    playtime_option: Optional[str] = None,
    complexity_range: Optional[Tuple[float, float]] = None,
    selected_cats: Optional[List[str]] = None,
    selected_mechs: Optional[List[str]] = None,
    selected_themes: Optional[List[str]] = None,
    exclude_names: Optional[List[str]] = None,
    use_profile_similarity: bool = False,
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """Send recommendation request payload to POST /api/v1/recommend with fallback."""
    payload = {
        "selected_names": selected_names,
        "player_count_range": list(player_count_range) if player_count_range else None,
        "playtime_option": playtime_option,
        "complexity_range": list(complexity_range) if complexity_range else None,
        "selected_cats": selected_cats,
        "selected_mechs": selected_mechs,
        "selected_themes": selected_themes,
        "exclude_names": exclude_names,
        "use_profile_similarity": use_profile_similarity,
        "top_n": top_n
    }
    try:
        res = requests.post(f"{API_BASE_URL}/api/v1/recommend", json=payload, timeout=15)
        if res.status_code == 200:
            return res.json()
        else:
            # Fallback to local computation if backend returns unexpected status
            return recommend_games(
                selected_names=selected_names,
                player_count_range=player_count_range,
                playtime_option=playtime_option,
                complexity_range=complexity_range,
                selected_cats=selected_cats,
                selected_mechs=selected_mechs,
                selected_themes=selected_themes,
                exclude_names=exclude_names,
                use_profile_similarity=use_profile_similarity,
                top_n=top_n
            )
    except Exception:
        # Fallback to local computation if HTTP connection fails
        return recommend_games(
            selected_names=selected_names,
            player_count_range=player_count_range,
            playtime_option=playtime_option,
            complexity_range=complexity_range,
            selected_cats=selected_cats,
            selected_mechs=selected_mechs,
            selected_themes=selected_themes,
            exclude_names=exclude_names,
            use_profile_similarity=use_profile_similarity,
            top_n=top_n
        )

def sync_bgg_collection_api(username: str) -> Tuple[bool, str, List[str]]:
    """Send username payload to POST /api/v1/bgg-collection."""
    payload = {"username": username}
    res = requests.post(f"{API_BASE_URL}/api/v1/bgg-collection", json=payload, timeout=20)
    res.raise_for_status()
    data = res.json()
    return data['success'], data['error_msg'], data['matched_games']

def request_ai_explanation_api(rec: Dict[str, Any], liked_games: List[str], model: str = "phi3") -> str:
    """Send recommendation item and liked games payload to POST /api/v1/explain."""
    payload = {
        "rec": rec,
        "liked_games": liked_games,
        "model": model
    }
    res = requests.post(f"{API_BASE_URL}/api/v1/explain", json=payload, timeout=120)
    res.raise_for_status()
    return res.json()['explanation']
